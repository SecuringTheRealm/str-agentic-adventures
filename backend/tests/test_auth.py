"""Tests for the Easy Auth FastAPI dependency (backend/app/auth.py)."""

from __future__ import annotations

import base64
import json

import pytest
from app.auth import AuthDep, AuthenticatedUser, get_current_user
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Unit tests – get_current_user dependency
# ---------------------------------------------------------------------------


class TestGetCurrentUser:
    """Unit tests for get_current_user."""

    def _make_principal(self, claims: list[dict]) -> str:
        """Encode a claims payload as a base64 Easy-Auth principal header value."""
        payload = json.dumps({"claims": claims}).encode("utf-8")
        return base64.b64encode(payload).decode("utf-8")

    def test_valid_headers_return_authenticated_user(self) -> None:
        """Valid Easy Auth headers produce an AuthenticatedUser instance."""
        principal = self._make_principal([{"typ": "name", "val": "Alice"}])
        user = get_current_user(
            x_ms_client_principal_id="user-123",
            x_ms_client_principal_name="Alice",
            x_ms_client_principal=principal,
        )
        assert isinstance(user, AuthenticatedUser)
        assert user.user_id == "user-123"
        assert user.name == "Alice"
        assert user.claims == {"name": "Alice"}

    def test_missing_principal_id_raises_401(self) -> None:
        """Missing x-ms-client-principal-id must raise HTTP 401."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(
                x_ms_client_principal_id=None,
                x_ms_client_principal_name=None,
                x_ms_client_principal=None,
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_malformed_base64_principal_returns_empty_claims(self) -> None:
        """A malformed x-ms-client-principal value must not crash; claims stay empty."""
        user = get_current_user(
            x_ms_client_principal_id="user-456",
            x_ms_client_principal_name="Bob",
            x_ms_client_principal="!!!not-valid-base64!!!",
        )
        assert user.user_id == "user-456"
        assert user.name == "Bob"
        assert user.claims == {}

    def test_valid_principal_id_without_principal_header(self) -> None:
        """When only the ID header is present, user is authenticated; claims empty."""
        user = get_current_user(
            x_ms_client_principal_id="user-789",
            x_ms_client_principal_name=None,
            x_ms_client_principal=None,
        )
        assert user.user_id == "user-789"
        assert user.name == ""
        assert user.claims == {}

    def test_multiple_claims_are_extracted(self) -> None:
        """All claims in the principal payload are mapped to the claims dict."""
        principal = self._make_principal(
            [
                {"typ": "email", "val": "charlie@example.com"},
                {"typ": "role", "val": "admin"},
            ]
        )
        user = get_current_user(
            x_ms_client_principal_id="user-abc",
            x_ms_client_principal_name="Charlie",
            x_ms_client_principal=principal,
        )
        assert user.claims == {"email": "charlie@example.com", "role": "admin"}


# ---------------------------------------------------------------------------
# Integration tests – AuthDep used in a FastAPI route
# ---------------------------------------------------------------------------


class TestAuthDepRouteIntegration:
    """Tests that verify AuthDep works correctly when injected into routes."""

    def _build_app(self) -> FastAPI:
        """Build a minimal FastAPI app that uses AuthDep."""
        app = FastAPI()

        @app.get("/me")
        def read_me(user: AuthDep) -> dict:
            return {"user_id": user.user_id, "name": user.name, "claims": user.claims}

        return app

    def _make_principal(self, claims: list[dict]) -> str:
        payload = json.dumps({"claims": claims}).encode("utf-8")
        return base64.b64encode(payload).decode("utf-8")

    def test_authdep_with_valid_headers(self) -> None:
        """Route using AuthDep returns user data when valid Easy Auth headers sent."""
        app = self._build_app()
        client = TestClient(app, raise_server_exceptions=True)
        principal = self._make_principal([{"typ": "sub", "val": "abc"}])
        response = client.get(
            "/me",
            headers={
                "x-ms-client-principal-id": "user-001",
                "x-ms-client-principal-name": "Dave",
                "x-ms-client-principal": principal,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-001"
        assert data["name"] == "Dave"
        assert data["claims"] == {"sub": "abc"}

    def test_authdep_missing_headers_returns_401(self) -> None:
        """Route using AuthDep returns 401 when Easy Auth headers are absent."""
        app = self._build_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_authdep_malformed_principal_still_serves_route(self) -> None:
        """Route using AuthDep succeeds with empty claims when principal malformed."""
        app = self._build_app()
        client = TestClient(app, raise_server_exceptions=True)
        response = client.get(
            "/me",
            headers={
                "x-ms-client-principal-id": "user-002",
                "x-ms-client-principal-name": "Eve",
                "x-ms-client-principal": "bad-base64!!!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-002"
        assert data["claims"] == {}
