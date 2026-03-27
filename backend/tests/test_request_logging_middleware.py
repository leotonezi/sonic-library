"""Tests for US-008 — RequestLoggingMiddleware (request/response access logging)."""

import time
from unittest.mock import patch, MagicMock

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.middleware import RequestLoggingMiddleware, RequestIDMiddleware


def _make_app() -> FastAPI:
    """Minimal FastAPI app with logging middleware for isolated testing."""
    test_app = FastAPI()
    test_app.add_middleware(RequestIDMiddleware)
    test_app.add_middleware(RequestLoggingMiddleware)

    @test_app.get("/ok")
    def ok():
        return {"status": "ok"}

    @test_app.get("/not-found")
    def not_found():
        return JSONResponse(status_code=404, content={"detail": "not found"})

    @test_app.get("/error")
    def error():
        return JSONResponse(status_code=500, content={"detail": "server error"})

    @test_app.get("/redirect")
    def redirect():
        return JSONResponse(status_code=301, content={"detail": "moved"})

    @test_app.get("/health")
    def health():
        return {"status": "healthy"}

    return test_app


app = _make_app()
client = TestClient(app)


class TestRequestLogging:
    """Verify that request logging middleware logs with correct levels."""

    def test_2xx_logged_at_info(self):
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/ok")
            assert resp.status_code == 200
            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[0][0] == "request completed"
            assert call_kwargs[1]["method"] == "GET"
            assert call_kwargs[1]["path"] == "/ok"
            assert call_kwargs[1]["status_code"] == 200
            assert "duration_ms" in call_kwargs[1]

    def test_3xx_logged_at_info(self):
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/redirect", follow_redirects=False)
            assert resp.status_code == 301
            mock_logger.info.assert_called_once()
            assert mock_logger.info.call_args[1]["status_code"] == 301

    def test_4xx_logged_at_warning(self):
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/not-found")
            assert resp.status_code == 404
            mock_logger.warning.assert_called_once()
            assert mock_logger.warning.call_args[1]["status_code"] == 404

    def test_5xx_logged_at_error(self):
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/error")
            assert resp.status_code == 500
            mock_logger.error.assert_called_once()
            assert mock_logger.error.call_args[1]["status_code"] == 500

    def test_log_includes_duration_ms(self):
        with patch("app.core.middleware.logger") as mock_logger:
            client.get("/ok")
            duration_ms = mock_logger.info.call_args[1]["duration_ms"]
            assert isinstance(duration_ms, float)
            assert duration_ms >= 0

    def test_log_includes_method_and_path(self):
        with patch("app.core.middleware.logger") as mock_logger:
            client.get("/ok")
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["method"] == "GET"
            assert kwargs["path"] == "/ok"

    def test_log_includes_user_id_none_when_unauthenticated(self):
        with patch("app.core.middleware.logger") as mock_logger:
            client.get("/ok")
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["user_id"] is None


class TestHealthCheckExclusion:
    """Health check endpoints should not be logged."""

    def test_health_endpoint_not_logged(self):
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/health")
            assert resp.status_code == 200
            mock_logger.info.assert_not_called()
            mock_logger.warning.assert_not_called()
            mock_logger.error.assert_not_called()


class TestUserIdExtraction:
    """Verify user_id extraction from JWT cookie."""

    def test_valid_jwt_extracts_user_email(self):
        from jose import jwt
        from app.core.config import settings

        token = jwt.encode(
            {"sub": "test@example.com", "exp": str(int(time.time()) + 3600)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        with patch("app.core.middleware.logger") as mock_logger:
            client.get("/ok", cookies={"access_token": token})
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["user_id"] == "test@example.com"

    def test_invalid_jwt_returns_null_user_id(self):
        with patch("app.core.middleware.logger") as mock_logger:
            client.get("/ok", cookies={"access_token": "invalid-token"})
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["user_id"] is None


class TestIntegration:
    """Integration tests with the main application."""

    def test_main_app_logs_requests(self, client):
        """The production app logs requests via the middleware."""
        with patch("app.core.middleware.logger") as mock_logger:
            resp = client.get("/books/?page=1&page_size=1")
            assert resp.status_code == 200
            mock_logger.info.assert_called()
