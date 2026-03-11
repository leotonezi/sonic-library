"""Tests for OpenAI circuit breaker integration in recommendations."""

from unittest.mock import patch, MagicMock

import pytest

from app.core.circuit_breaker import CircuitBreaker, CircuitState


class FakeRedisHash:
    """Minimal fake Redis supporting hash operations."""

    def __init__(self):
        self._store: dict = {}

    def hgetall(self, key):
        return dict(self._store.get(key, {}))

    def hset(self, key, mapping=None, **kwargs):
        if key not in self._store:
            self._store[key] = {}
        if mapping:
            self._store[key].update(mapping)


def _make_open_circuit(redis_client=None):
    """Create an OpenAI circuit breaker that is already in OPEN state."""
    if redis_client is None:
        redis_client = FakeRedisHash()
    cb = CircuitBreaker(
        name="openai",
        failure_threshold=1,
        recovery_timeout=300,
        redis_client=redis_client,
    )
    cb.record_failure()
    assert cb.is_call_permitted() is False
    return cb, redis_client


class TestOpenAICircuitBreakerInRecommendations:
    """Test that generate_book_recommendations respects the OpenAI circuit breaker."""

    @patch("app.services.recommendation_service._get_openai_circuit_breaker")
    def test_returns_none_when_circuit_open(self, mock_get_cb):
        """When OpenAI circuit is open, generate_book_recommendations returns None."""
        from app.services.recommendation_service import generate_book_recommendations

        cb, _ = _make_open_circuit()
        mock_get_cb.return_value = cb

        fake_review = MagicMock()
        fake_review.book_id = 1
        fake_review.rate = 5
        fake_review.content = "Great book"

        result = generate_book_recommendations([fake_review])
        assert result is None

    @patch("app.services.recommendation_service._get_openai_circuit_breaker")
    @patch("app.services.recommendation_service.get_cached_recommendations")
    @patch("app.services.recommendation_service.get_google_books_by_genre")
    @patch("app.services.recommendation_service.llm")
    def test_records_success_on_successful_call(
        self, mock_llm, mock_google, mock_cache, mock_get_cb
    ):
        """Successful LLM call records success on the circuit breaker."""
        redis = FakeRedisHash()
        cb = CircuitBreaker(
            name="openai", failure_threshold=5, recovery_timeout=30, redis_client=redis
        )
        mock_get_cb.return_value = cb
        mock_cache.return_value = None
        mock_google.return_value = []

        mock_result = MagicMock()
        mock_result.content = "Recommendation text"
        mock_llm.return_value = mock_result

        fake_review = MagicMock()
        fake_review.book_id = 1
        fake_review.rate = 5
        fake_review.content = "Great book"

        from app.services.recommendation_service import generate_book_recommendations

        result = generate_book_recommendations([fake_review])
        assert result == "Recommendation text"

        # Verify circuit is still closed
        state = redis._store.get("circuit_breaker:openai", {})
        assert state.get("state") == CircuitState.CLOSED

    @patch("app.services.recommendation_service._get_openai_circuit_breaker")
    @patch("app.services.recommendation_service.get_cached_recommendations")
    @patch("app.services.recommendation_service.get_google_books_by_genre")
    @patch("app.services.recommendation_service.llm")
    def test_records_failure_on_llm_error(
        self, mock_llm, mock_google, mock_cache, mock_get_cb
    ):
        """Failed LLM call records failure on the circuit breaker."""
        redis = FakeRedisHash()
        cb = CircuitBreaker(
            name="openai", failure_threshold=5, recovery_timeout=30, redis_client=redis
        )
        mock_get_cb.return_value = cb
        mock_cache.return_value = None
        mock_google.return_value = []

        mock_llm.side_effect = Exception("OpenAI API error")

        fake_review = MagicMock()
        fake_review.book_id = 1
        fake_review.rate = 5
        fake_review.content = "Great book"

        from app.services.recommendation_service import generate_book_recommendations

        with pytest.raises(Exception, match="OpenAI API error"):
            generate_book_recommendations([fake_review])

        # Verify failure was recorded
        state = redis._store.get("circuit_breaker:openai", {})
        assert int(state.get("failure_count", 0)) == 1


class TestRecommendationsEndpointFallback:
    """Test the /recommendations/ endpoint fallback when circuit is open."""

    @patch("app.api.v1.endpoints.recommendations.generate_book_recommendations")
    def test_recommendations_returns_fallback_when_circuit_open(self, mock_gen):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.core.security import get_current_user
        from app.core.database import get_db

        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_review = MagicMock()
        mock_review.id = 1
        mock_review.user_id = 1
        mock_review.book_id = 1
        mock_review.external_book_id = None
        mock_review.content = "Great book"
        mock_review.rate = 5
        mock_review.user_name = "Test User"
        mock_review.user_profile_picture = None
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_review]

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_session

        # generate_book_recommendations returns None when circuit is open
        mock_gen.return_value = None

        try:
            client = TestClient(app)
            response = client.get("/recommendations/")

            assert response.status_code == 200
            body = response.json()
            assert body["data"] is None
            assert body["message"] == "AI recommendations are temporarily unavailable. Please try again shortly."
            assert body["status"] == "ok"
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.endpoints.recommendations.generate_book_recommendations")
    def test_graph_returns_only_user_books_when_circuit_open(self, mock_gen):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.core.security import get_current_user
        from app.core.database import get_db

        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_session

        # generate_book_recommendations returns None when circuit is open
        mock_gen.return_value = None

        try:
            client = TestClient(app)
            response = client.get("/recommendations/graph")

            assert response.status_code == 200
            body = response.json()
            graph = body["data"]
            # No recommendation nodes when circuit is open and no reviews
            assert all(n["type"] != "recommendations" for n in graph["nodes"])
            assert graph["edges"] == []
        finally:
            app.dependency_overrides.clear()
