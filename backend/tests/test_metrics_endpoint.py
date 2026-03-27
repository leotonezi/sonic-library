"""Tests for the Prometheus /metrics endpoint (US-009)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_metrics_endpoint_returns_200(client):
    """GET /metrics should return 200."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_endpoint_content_type(client):
    """GET /metrics should return Prometheus text format content type."""
    response = client.get("/metrics")
    assert "text/plain" in response.headers["content-type"] or \
           "text/plain" in response.headers.get("content-type", "")


def test_metrics_endpoint_contains_prometheus_data(client):
    """GET /metrics should contain Prometheus-compatible metric lines."""
    response = client.get("/metrics")
    body = response.text
    # Default prometheus-client metrics include process and python info
    assert "process_" in body or "python_" in body or "# HELP" in body


def test_metrics_endpoint_no_auth_required(client):
    """GET /metrics should not require authentication."""
    # No auth headers/cookies provided — should still succeed
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.status_code != 401
    assert response.status_code != 403
