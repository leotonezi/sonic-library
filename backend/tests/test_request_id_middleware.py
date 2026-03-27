"""Tests for US-002 — RequestIDMiddleware (request_id tracing)."""

import uuid
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import RequestIDMiddleware, request_id_ctx


def _make_app() -> FastAPI:
    """Minimal FastAPI app with the middleware for isolated testing."""
    test_app = FastAPI()
    test_app.add_middleware(RequestIDMiddleware)

    @test_app.get("/ping")
    def ping():
        return {"request_id": request_id_ctx.get()}

    return test_app


client = TestClient(_make_app())


# --- X-Request-ID header on every response ---

def test_response_contains_x_request_id_header():
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers


def test_generated_request_id_is_valid_uuid4():
    resp = client.get("/ping")
    rid = resp.headers["X-Request-ID"]
    # Should be parseable as a UUID
    parsed = uuid.UUID(rid, version=4)
    assert str(parsed) == rid


# --- Reuse incoming X-Request-ID ---

def test_reuses_incoming_x_request_id():
    custom_id = "my-custom-trace-id-123"
    resp = client.get("/ping", headers={"X-Request-ID": custom_id})
    assert resp.headers["X-Request-ID"] == custom_id


def test_incoming_request_id_available_in_contextvar():
    custom_id = "ctx-var-test-456"
    resp = client.get("/ping", headers={"X-Request-ID": custom_id})
    body = resp.json()
    assert body["request_id"] == custom_id


# --- ContextVar populated for generated IDs ---

def test_generated_request_id_matches_contextvar():
    resp = client.get("/ping")
    body = resp.json()
    header_id = resp.headers["X-Request-ID"]
    assert body["request_id"] == header_id


# --- structlog contextvars integration ---

def test_structlog_contextvars_bound():
    """The middleware binds request_id into structlog contextvars."""
    import structlog

    captured = {}

    original_bind = structlog.contextvars.bind_contextvars

    def spy_bind(**kwargs):
        captured.update(kwargs)
        return original_bind(**kwargs)

    with patch("app.core.middleware.structlog.contextvars.bind_contextvars", side_effect=spy_bind):
        resp = client.get("/ping")

    assert resp.status_code == 200
    assert "request_id" in captured


# --- Integration with main app ---

def test_main_app_has_request_id_header(client):
    """The production app (from conftest) returns X-Request-ID."""
    resp = client.get("/books/?page=1&page_size=1")
    assert "X-Request-ID" in resp.headers
    # Should be a valid UUID when no incoming header
    uuid.UUID(resp.headers["X-Request-ID"], version=4)
