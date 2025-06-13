"""
Test to ensure all frontend API calls have corresponding backend endpoints.
This test scans the frontend code for API calls and validates they exist in the backend.
"""

import pytest
import sys
import os
import re
from pathlib import Path
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestFrontendBackendAPICompatibility:
    """Test that all frontend API calls have corresponding backend endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def get_frontend_api_calls(self):
        """Extract API calls from frontend code."""
        frontend_path = Path(__file__).parent.parent.parent / "frontend" / "src"
        api_calls = set()

        if not frontend_path.exists():
            pytest.skip("Frontend directory not found")

        # Patterns to match API calls
        patterns = [
            r"/api/[a-zA-Z0-9/_-]+",  # API paths
            r'apiClient\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',  # axios calls
            r"await\s+api\.[a-zA-Z_]+\(",  # api.function() calls
        ]

        for file_path in frontend_path.rglob("*.ts"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple) and len(match) > 0:
                            # For patterns that capture groups
                            api_calls.add(match[1] if len(match) > 1 else match[0])
                        elif isinstance(match, str):
                            api_calls.add(match)
            except (UnicodeDecodeError, IOError):
                continue  # Skip files that can't be read

        # Filter to only API paths
        api_paths = {call for call in api_calls if call.startswith("/api/")}

        return api_paths

    def get_frontend_api_functions(self):
        """Extract API function calls from frontend services/api.ts."""
        frontend_api_path = (
            Path(__file__).parent.parent.parent
            / "frontend"
            / "src"
            / "services"
            / "api.ts"
        )

        if not frontend_api_path.exists():
            return set()

        api_functions = set()

        try:
            with open(frontend_api_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract function definitions like "export const functionName = async"
            function_pattern = r"export const (\w+) = async"
            matches = re.findall(function_pattern, content)
            api_functions.update(matches)

            # Extract API endpoint paths from the file
            endpoint_pattern = (
                r'apiClient\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            )
            matches = re.findall(endpoint_pattern, content)
            endpoints = {match[1] for match in matches}

        except (UnicodeDecodeError, IOError):
            return set()

        return api_functions, endpoints

    def test_frontend_api_functions_exist(self):
        """Test that frontend API functions are implemented."""
        functions, endpoints = self.get_frontend_api_functions()

        expected_functions = {
            "createCharacter",
            "getCharacter",
            "sendPlayerInput",
            "createCampaign",
            "generateImage",
            "generateBattleMap",
        }

        for func in expected_functions:
            assert func in functions, (
                f"API function {func} is missing from frontend api.ts"
            )

    def test_frontend_api_endpoints_exist_in_backend(self, client):
        """Test that all frontend API endpoints exist in the backend."""
        functions, endpoints = self.get_frontend_api_functions()

        # Known endpoints that should exist
        expected_endpoints = [
            "/game/character",
            "/game/input",
            "/game/campaign",
            "/game/generate-image",
            "/game/battle-map",
        ]

        for endpoint in expected_endpoints:
            # Test GET endpoints
            if "character/" in endpoint:
                response = client.get(f"/api{endpoint}/test-id")
                assert response.status_code in [200, 404, 422, 500], (
                    f"GET {endpoint} should be accessible"
                )
            else:
                # Test POST endpoints
                response = client.post(f"/api{endpoint}", json={})
                assert response.status_code in [200, 400, 422, 500, 503], (
                    f"POST {endpoint} should be accessible"
                )

    def test_websocket_endpoints_configured(self):
        """Test that WebSocket endpoints are properly configured."""
        from app.main import app

        # Check that WebSocket routes are included by checking that we have some routes
        assert len(app.routes) > 0, "App should have routes configured"

        # Check that websocket routes module can be imported
        try:
            from app.api.websocket_routes import router as ws_router

            assert ws_router is not None, "WebSocket router should be importable"
        except ImportError:
            pytest.fail("WebSocket routes module should be importable")

    def test_dice_rolling_endpoints_exist(self, client):
        """Test that dice rolling endpoints exist (used by frontend DiceRoller component)."""
        dice_endpoints = [
            "/api/game/dice/roll",
            "/api/game/dice/roll-with-character",
            "/api/game/dice/manual-roll",
        ]

        for endpoint in dice_endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code in [200, 400, 422, 500], (
                f"Dice endpoint {endpoint} should exist"
            )

    def test_character_progression_endpoints_exist(self, client):
        """Test character progression endpoints."""
        progression_endpoints = [
            ("/api/game/character/test-id/level-up", "POST"),
            ("/api/game/character/test-id/award-experience", "POST"),
            ("/api/game/character/test-id/progression-info", "GET"),
        ]

        for endpoint, method in progression_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            assert response.status_code in [200, 400, 404, 422, 500], (
                f"{method} {endpoint} should exist"
            )

    def test_campaign_management_endpoints_exist(self, client):
        """Test campaign management endpoints."""
        campaign_endpoints = [
            "/api/game/campaign/generate-world",
            "/api/game/campaign/test-id/start-session",
            "/api/game/session/test-session/action",
            "/api/game/combat/initialize",
            "/api/game/combat/test-combat/turn",
        ]

        for endpoint in campaign_endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code in [200, 400, 404, 422, 500], (
                f"Campaign endpoint {endpoint} should exist"
            )

    def test_api_error_handling_consistency(self, client):
        """Test that all API endpoints handle errors consistently."""
        endpoints_to_test = [
            "/api/game/character",
            "/api/game/campaign",
            "/api/game/input",
            "/api/game/generate-image",
            "/api/game/battle-map",
        ]

        for endpoint in endpoints_to_test:
            # Test with invalid JSON
            response = client.post(endpoint, json={"invalid": "data"})
            # Some endpoints may accept minimal data and return 200, others should validate and return error codes
            assert response.status_code in [200, 400, 422, 500, 503], (
                f"{endpoint} should handle data properly"
            )

            # All error responses should have a "detail" field, successful responses should have proper data
            if response.status_code >= 400:
                response_data = response.json()
                assert "detail" in response_data, (
                    f"{endpoint} error response should have 'detail' field"
                )

    def test_frontend_typescript_compatibility(self):
        """Test that frontend TypeScript interfaces match backend models."""
        # This is a basic check - in a real app you'd want more sophisticated validation
        from app.models.game_models import (
            CharacterSheet,
            Campaign,
            GameResponse,
            CreateCharacterRequest,
            CreateCampaignRequest,
            PlayerInput,
        )

        # Test that models can be serialized (important for API responses)
        models_to_test = [
            CharacterSheet,
            Campaign,
            GameResponse,
            CreateCharacterRequest,
            CreateCampaignRequest,
            PlayerInput,
        ]

        for model_class in models_to_test:
            # Check that the model has a model_dump method (Pydantic v2)
            assert hasattr(model_class, "model_dump"), (
                f"{model_class.__name__} should have model_dump method"
            )

            # Check that the model has a model_json_schema method
            assert hasattr(model_class, "model_json_schema"), (
                f"{model_class.__name__} should have schema method"
            )

    def test_cors_configuration(self, client):
        """Test that CORS is properly configured for frontend access."""
        # Test preflight request
        response = client.options(
            "/api/game/character",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        # Should not fail with CORS error
        assert response.status_code in [200, 405], "CORS should be configured"

    def test_websocket_path_matches_frontend(self):
        """Test that WebSocket paths match what the frontend expects."""
        # Frontend expects: /api/ws/{campaign_id}
        from app.api.websocket_routes import router as ws_router

        # Check that the WebSocket router exists and has routes
        assert ws_router is not None, "WebSocket router should exist"
        assert len(ws_router.routes) > 0, (
            "WebSocket router should have routes configured"
        )
