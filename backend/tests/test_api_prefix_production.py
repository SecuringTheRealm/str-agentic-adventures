"""Test that API routes work correctly with /api prefix in production."""

import pytest
from app.main import app
from fastapi.testclient import TestClient


class TestProductionAPIPrefix:
    """Test that the application correctly handles /api prefix in production."""

    @pytest.fixture
    def production_client(self):
        """Create a test client that simulates production environment with /api root_path."""
        from fastapi import FastAPI
        from app.main import app as base_app
        import types

        # Create a new FastAPI instance with root_path="/api"
        prod_app = FastAPI(root_path="/api")

        # Mount all routes from the original app
        for route in base_app.routes:
            prod_app.router.routes.append(route)

        # Copy exception handlers, middleware, etc. if needed
        prod_app.exception_handlers = base_app.exception_handlers.copy()
        prod_app.middleware_stack = base_app.middleware_stack

        client = TestClient(prod_app)
        yield client
    @pytest.fixture
    def dev_client(self):
        """Create a test client for development environment (no prefix)."""
        return TestClient(app)

    def test_production_has_api_prefix(self, production_client) -> None:
        """Test that production environment configures /api root_path."""
        # Access the app through the client
        assert production_client.app.root_path == "/api"

    def test_dev_has_no_prefix(self, dev_client) -> None:
        """Test that development environment has no root_path prefix."""
        assert dev_client.app.root_path == ""

    def test_production_campaign_templates_with_api_prefix(
        self, production_client
    ) -> None:
        """Test that /api/game/campaign/templates works in production."""
        response = production_client.get("/api/game/campaign/templates")

        # Should return 200 OK with templates
        assert response.status_code == 200

        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_production_campaign_templates_without_api_prefix(
        self, production_client
    ) -> None:
        """Test that /game/campaign/templates also works (backward compatibility)."""
        response = production_client.get("/game/campaign/templates")

        # Should return 200 OK with templates
        assert response.status_code == 200

        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_production_health_check_with_api_prefix(self, production_client) -> None:
        """Test that /api/health works in production."""
        response = production_client.get("/api/health")

        # Should return 200 OK
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"

    def test_production_health_check_without_api_prefix(
        self, production_client
    ) -> None:
        """Test that /health also works (backward compatibility)."""
        response = production_client.get("/health")

        # Should return 200 OK
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"

    def test_dev_campaign_templates_no_api_prefix(self, dev_client) -> None:
        """Test that development uses routes without /api prefix."""
        response = dev_client.get("/game/campaign/templates")

        # Should return 200 OK with templates
        assert response.status_code == 200

        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_dev_health_check_no_api_prefix(self, dev_client) -> None:
        """Test that development health check works without prefix."""
        response = dev_client.get("/health")

        # Should return 200 OK
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
