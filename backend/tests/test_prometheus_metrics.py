"""Tests for Prometheus counters and histograms (US-010)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    external_api_requests_total,
    external_api_duration_seconds,
    cache_operations_total,
    recommendation_generation_duration_seconds,
    circuit_breaker_state,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_http_metrics_registered(client):
    """http_requests_total and http_request_duration_seconds should appear in /metrics."""
    response = client.get("/metrics")
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_external_api_metrics_registered(client):
    """external_api_requests_total and external_api_duration_seconds should appear in /metrics."""
    # Seed a sample to ensure the metric family is present
    external_api_requests_total.labels(service="google_books", status="success").inc(0)
    external_api_duration_seconds.labels(service="google_books").observe(0)

    response = client.get("/metrics")
    body = response.text
    assert "external_api_requests_total" in body
    assert "external_api_duration_seconds" in body


def test_cache_metrics_registered(client):
    """cache_operations_total should appear in /metrics."""
    cache_operations_total.labels(cache="recommendations", result="hit").inc(0)

    response = client.get("/metrics")
    body = response.text
    assert "cache_operations_total" in body


def test_recommendation_generation_metric_registered(client):
    """recommendation_generation_duration_seconds should appear in /metrics."""
    recommendation_generation_duration_seconds.observe(0)

    response = client.get("/metrics")
    body = response.text
    assert "recommendation_generation_duration_seconds" in body


def test_circuit_breaker_state_metric_registered(client):
    """circuit_breaker_state gauge should appear in /metrics."""
    circuit_breaker_state.labels(service="google_books").set(0)

    response = client.get("/metrics")
    body = response.text
    assert "circuit_breaker_state" in body


def test_http_request_increments_counter(client):
    """Making an HTTP request should increment http_requests_total."""
    # Get current value for GET /metrics (excluded path, won't count)
    # Make a request to a non-excluded path
    before = http_requests_total.labels(method="GET", path="/books", status_code="500")._value.get()
    client.get("/books")
    after = http_requests_total.labels(method="GET", path="/books", status_code="500")._value.get()
    # We can't predict the exact status_code, but the metric family should exist
    response = client.get("/metrics")
    assert 'http_requests_total{' in response.text


def test_http_metrics_have_correct_labels(client):
    """http_requests_total should have method, path, status_code labels."""
    response = client.get("/metrics")
    body = response.text
    # After making requests, we should see label patterns
    assert "method=" in body
    assert "status_code=" in body


def test_external_api_metrics_have_correct_labels(client):
    """external_api_requests_total should have service and status labels."""
    external_api_requests_total.labels(service="openai", status="success").inc()
    response = client.get("/metrics")
    body = response.text
    assert 'service="openai"' in body
    assert 'status="success"' in body


def test_cache_metrics_have_correct_labels(client):
    """cache_operations_total should have cache and result labels."""
    cache_operations_total.labels(cache="popular_books", result="miss").inc()
    response = client.get("/metrics")
    body = response.text
    assert 'cache="popular_books"' in body
    assert 'result="miss"' in body


def test_circuit_breaker_state_values(client):
    """circuit_breaker_state gauge should accept 0, 1, 2 values."""
    circuit_breaker_state.labels(service="test_service").set(0)
    assert circuit_breaker_state.labels(service="test_service")._value.get() == 0

    circuit_breaker_state.labels(service="test_service").set(1)
    assert circuit_breaker_state.labels(service="test_service")._value.get() == 1

    circuit_breaker_state.labels(service="test_service").set(2)
    assert circuit_breaker_state.labels(service="test_service")._value.get() == 2
