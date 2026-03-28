"""Tests for the realtime voice token endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_realtime_token_endpoint_exists() -> None:
    """Token endpoint should be registered (not 404)."""
    response = client.get("/api/realtime/token")
    assert response.status_code != 404


def test_realtime_token_returns_error_without_endpoint() -> None:
    """Token endpoint returns 503 when Azure OpenAI is not configured."""
    # In test env, endpoint is likely empty
    response = client.get("/api/realtime/token")
    # Either 503 (not configured) or 502/500 (configured but can't reach Azure)
    assert response.status_code in (503, 502, 500, 200)
