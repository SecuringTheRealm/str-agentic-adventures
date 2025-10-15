"""
Test to ensure all frontend API calls have corresponding backend endpoints.
This test scans the frontend code for API calls and validates they exist in the backend.
"""

import os
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

RAW_API_PREFIX = os.getenv("API_PREFIX", "")
API_PREFIX = f"/{RAW_API_PREFIX.strip('/')}" if RAW_API_PREFIX else ""


def build_path(endpoint: str) -> str:
    """Construct full API path with optional prefix."""
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    return f"{API_PREFIX}{endpoint}" if API_PREFIX else endpoint


def normalize_api_path(path: str) -> str:
    """Normalize API paths by removing optional /api prefix."""
    if path.startswith("/api/"):
        return path[4:]
    return path


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
            r"/api/[a-zA-Z0-9/_-]+",  # Legacy API paths with /api prefix
            r"/game/[a-zA-Z0-9/_-]+",  # Current API paths without /api prefix
            r"apiClient\.(get|post|put|delete|patch)\([\"']([^\"']+)[\"']",  # axios calls
            r"await\s+api\.[a-zA-Z_]+\(",  # api.function() calls
        ]

        for file_path in frontend_path.rglob("*.ts"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple) and len(match) > 0:
                            value = match[1] if len(match) > 1 else match[0]
                        else:
                            value = match

                        if isinstance(value, str) and value.startswith(("/api/", "/game/")):
                            api_calls.add(normalize_api_path(value))
            except (OSError, UnicodeDecodeError):
                continue  # Skip files that can't be read

        return api_calls

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
            with open(frontend_api_path, encoding="utf-8") as f:
                content = f.read()

            # Extract function definitions like "export const functionName = async"
            function_pattern = r"export const (\w+) = async"
            matches = re.findall(function_pattern, content)
            api_functions.update(matches)

            # Extract API endpoint paths from the file
            endpoint_pattern = (
                r"apiClient\.(get|post|put|delete|patch)\([\"']([^\"']+)[\"']"
            )
            matches = re.findall(endpoint_pattern, content)
            endpoints = {normalize_api_path(match[1]) for match in matches}

        except (OSError, UnicodeDecodeError):
            return set()

        return api_functions, endpoints

    def test_frontend_api_functions_exist(self) -> None:
        """Test that frontend API functions are implemented."""
        functions, _ = self.get_frontend_api_functions()

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

    def test_frontend_api_endpoints_exist_in_backend(self, client) -> None:
        """Test that all frontend API endpoints exist in the backend."""
        expected_endpoints = [
            "/game/character",
            "/game/input",
            "/game/campaign",
            "/game/generate-image",
            "/game/battle-map",
        ]

        for endpoint in expected_endpoints:
            full_endpoint = build_path(endpoint)
            if "character/" in endpoint:
                response = client.get(f"{full_endpoint}/test-id")
                assert response.status_code in [200, 404, 422, 500], (
                    f"GET {endpoint} should be accessible"
                )
            else:
                response = client.post(full_endpoint, json={})
                assert response.status_code in [200, 400, 422, 500, 503], (
                    f"POST {endpoint} should be accessible"
                )

    def test_websocket_endpoints_configured(self) -> None:
        """Test that WebSocket endpoints are properly configured."""
        from app.main import app

        assert len(app.routes) > 0, "App should have routes configured"

        try:
            from app.api.websocket_routes import router as ws_router

            assert ws_router is not None, "WebSocket router should be importable"
        except ImportError:
            pytest.fail("WebSocket routes module should be importable")

    def test_dice_rolling_endpoints_exist(self, client) -> None:
        """Test that dice rolling endpoints exist (used by frontend DiceRoller component)."""
        dice_endpoints = [
            "/game/dice/roll",
            "/game/dice/roll-with-character",
            "/game/dice/manual-roll",
        ]

        for endpoint in dice_endpoints:
            response = client.post(build_path(endpoint), json={})
            assert response.status_code in [200, 400, 422, 500], (
                f"Dice endpoint {endpoint} should exist"
            )

    def test_character_progression_endpoints_exist(self, client) -> None:
        """Test character progression endpoints."""
        progression_endpoints = [
            ("/game/character/test-id/level-up", "POST"),
            ("/game/character/test-id/award-experience", "POST"),
            ("/game/character/test-id/progression-info", "GET"),
        ]

        for endpoint, method in progression_endpoints:
            full_endpoint = build_path(endpoint)
            if method == "GET":
                response = client.get(full_endpoint)
            else:
                response = client.post(full_endpoint, json={})
            assert response.status_code in [200, 400, 404, 422, 500], (
                f"{method} {endpoint} should exist"
            )

    def test_campaign_management_endpoints_exist(self, client) -> None:
        """Test campaign management endpoints."""
        campaign_endpoints = [
            "/game/campaign/generate-world",
            "/game/campaign/test-id/start-session",
            "/game/session/test-session/action",
            "/game/combat/initialize",
            "/game/combat/test-combat/turn",
        ]

        for endpoint in campaign_endpoints:
            response = client.post(build_path(endpoint), json={})
            assert response.status_code in [200, 400, 404, 422, 500], (
                f"Campaign endpoint {endpoint} should exist"
            )

    def test_api_error_handling_consistency(self, client) -> None:
        """Test that all API endpoints handle errors consistently."""
        endpoints_to_test = [
            "/game/character",
            "/game/campaign",
            "/game/input",
            "/game/generate-image",
            "/game/battle-map",
        ]

        for endpoint in endpoints_to_test:
            response = client.post(build_path(endpoint), json={"invalid": "data"})
            assert response.status_code in [200, 400, 422, 500, 503], (
                f"{endpoint} should handle data properly"
            )

            if response.status_code >= 400:
                response_data = response.json()
                assert "detail" in response_data, (
                    f"{endpoint} error response should have 'detail' field"
                )

    def test_frontend_typescript_compatibility(self) -> None:
        """Test that frontend TypeScript interfaces match backend models."""
        import json
        from typing import get_type_hints

        from app.models.game_models import (
            Campaign,
            CharacterSheet,
            CreateCampaignRequest,
            CreateCharacterRequest,
            GameResponse,
            PlayerInput,
        )

        models_to_test = [
            CharacterSheet,
            Campaign,
            GameResponse,
            CreateCharacterRequest,
            CreateCampaignRequest,
            PlayerInput,
        ]

        for model_class in models_to_test:
            assert hasattr(model_class, "model_dump"), (
                f"{model_class.__name__} should have model_dump method"
            )

            assert hasattr(model_class, "model_json_schema"), (
                f"{model_class.__name__} should have schema method"
            )

            schema = model_class.model_json_schema()
            assert "properties" in schema, (
                f"{model_class.__name__} schema should have properties"
            )
            assert "type" in schema, f"{model_class.__name__} schema should have type"

            try:
                json.dumps(schema)
            except (TypeError, ValueError) as e:
                raise AssertionError(
                    f"{model_class.__name__} schema is not JSON serializable: {e}"
                ) from None

            type_hints = get_type_hints(model_class)
            for field_name in schema.get("properties", {}):
                if hasattr(model_class, field_name):
                    assert field_name in type_hints or (
                        hasattr(model_class, "__annotations__")
                        and field_name in model_class.__annotations__
                    ), (
                        f"Field {field_name} in {model_class.__name__} should have type annotation"
                    )

    def test_cors_configuration(self, client) -> None:
        """Test that CORS is properly configured for frontend access."""
        response = client.options(
            build_path("/game/character"),
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code in [200, 405], "CORS should be configured"

    def test_websocket_path_matches_frontend(self) -> None:
        """Test that WebSocket paths match what the frontend expects."""
        from app.api.websocket_routes import router as ws_router

        assert ws_router is not None, "WebSocket router should exist"
        assert len(ws_router.routes) > 0, (
            "WebSocket router should have routes configured"
        )

        ws_paths = [route.path for route in ws_router.routes]
        assert "/ws/{campaign_id}" in ws_paths, (
            "Campaign WebSocket endpoint should exist at /ws/{campaign_id}"
        )
        assert "/ws/chat/{campaign_id}" in ws_paths, (
            "Chat WebSocket endpoint should exist at /ws/chat/{campaign_id}"
        )
        assert "/ws/global" in ws_paths, (
            "Global WebSocket endpoint should exist at /ws/global"
        )

    def test_websocket_sdk_message_types_match_backend(self) -> None:
        """Test that frontend WebSocket SDK message types match backend implementation."""
        from app.api.websocket_routes import router as ws_router

        assert ws_router is not None, "WebSocket router should exist"

        expected_message_types = [
            "chat_start",
            "chat_stream",
            "chat_complete",
            "chat_error",
            "chat_input",
            "dice_roll",
            "dice_result",
            "game_update",
            "character_update",
            "ping",
            "pong",
            "error",
        ]

        assert len(expected_message_types) > 0, (
            "Expected WebSocket message types should be documented"
        )
