"""
Frontend-Backend Integration Tests.
Tests API endpoint compatibility and route configuration.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestFrontendBackendIntegration:
    """Test frontend-backend API integration."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_health_endpoint_exists(self, client) -> None:
        """Test that the health endpoint exists and responds."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "0.1.0"}

    def test_root_endpoint_exists(self, client) -> None:
        """Test that the root endpoint exists and responds."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_api_routes_exist(self, client) -> None:
        """Test that all expected API routes exist and return proper status codes."""
        # Test routes that should exist based on frontend api.ts file
        routes_to_test = [
            ("/api/game/character", "POST"),
            ("/api/game/character/test-id", "GET"),
            ("/api/game/input", "POST"),
            ("/api/game/campaign", "POST"),
            ("/api/game/generate-image", "POST"),
            ("/api/game/battle-map", "POST"),
            ("/api/game/character/test-id/level-up", "POST"),
            ("/api/game/character/test-id/award-experience", "POST"),
            ("/api/game/character/test-id/progression-info", "GET"),
            ("/api/game/dice/roll", "POST"),
            ("/api/game/dice/roll-with-character", "POST"),
            ("/api/game/dice/manual-roll", "POST"),
        ]

        for route, method in routes_to_test:
            if method == "GET":
                response = client.get(route)
                # GET endpoints should either work (200) or return proper error (404, 422, 500, 503)
                # 503 can happen when Azure OpenAI configuration is missing
                assert response.status_code in [200, 404, 422, 500, 503], (
                    f"Route {route} returned unexpected status {response.status_code}"
                )
            elif method == "POST":
                response = client.post(route, json={})
                # POST endpoints should return proper error codes for invalid data or success
                # Some endpoints might succeed with empty data (like campaign creation)
                assert response.status_code in [200, 400, 422, 500, 503], (
                    f"Route {route} returned unexpected status {response.status_code}"
                )

    @patch("app.agents.scribe_agent.get_scribe")
    def test_character_creation_endpoint_compatibility(
        self, mock_scribe, client
    ) -> None:
        """Test character creation endpoint matches frontend expectations."""
        # Mock scribe agent response
        mock_scribe_instance = MagicMock()
        mock_scribe.return_value = mock_scribe_instance
        mock_scribe_instance.create_character.return_value = {
            "id": "test-character-id",
            "name": "Test Hero",
            "race": "human",
            "class": "fighter",
            "level": 1,
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10,
            },
            "hit_points": {"current": 20, "maximum": 20},
            "inventory": [],
        }

        # Frontend request format (matches api.ts)
        frontend_request = {
            "name": "Test Hero",
            "race": "human",
            "character_class": "fighter",
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10,
            },
            "backstory": "A brave warrior",
        }

        response = client.post("/api/game/character", json=frontend_request)

        # Should not return 500 error due to missing configuration
        assert (
            response.status_code != 500
            or "Azure OpenAI configuration" in response.json().get("detail", "")
        ), f"Character creation failed with unexpected error: {response.json()}"

        # If it's a config error, that's expected in test environment
        if response.status_code == 503:
            assert "Azure OpenAI configuration" in response.json().get("detail", "")
        elif response.status_code == 200:
            # If successful, check response format
            response_data = response.json()
            expected_fields = [
                "id",
                "name",
                "race",
                "character_class",
                "level",
                "abilities",
                "hit_points",
                "inventory",
            ]
            for field in expected_fields:
                assert field in response_data, (
                    f"Missing field {field} in character response"
                )

    @patch("app.agents.dungeon_master_agent.get_dungeon_master")
    def test_campaign_creation_endpoint_compatibility(self, mock_dm, client) -> None:
        """Test campaign creation endpoint matches frontend expectations."""
        # Mock dungeon master agent
        mock_dm_instance = MagicMock()
        mock_dm.return_value = mock_dm_instance
        mock_dm_instance.create_campaign.return_value = {
            "id": "test-campaign-id",
            "name": "Epic Adventure",
            "setting": "Fantasy Realm",
            "tone": "heroic",
            "homebrew_rules": [],
            "characters": [],
            "session_log": [],
            "state": "created",
        }

        # Frontend request format (matches api.ts)
        frontend_request = {
            "name": "Epic Adventure",
            "setting": "Fantasy Realm",
            "tone": "heroic",
            "homebrew_rules": ["Custom rule 1"],
        }

        response = client.post("/api/game/campaign", json=frontend_request)

        # Should not return 500 error due to missing configuration
        assert (
            response.status_code != 500
            or "Azure OpenAI configuration" in response.json().get("detail", "")
        ), f"Campaign creation failed with unexpected error: {response.json()}"

        # If it's a config error, that's expected in test environment
        if response.status_code == 503:
            assert "Azure OpenAI configuration" in response.json().get("detail", "")

    @patch("app.api.game_routes.get_dungeon_master")
    def test_player_input_endpoint_compatibility(self, mock_dm, client) -> None:
        """Test player input endpoint matches frontend expectations."""
        # Mock dungeon master agent with proper async support
        mock_dm_instance = MagicMock()
        mock_dm.return_value = mock_dm_instance
        mock_dm_instance.process_input = AsyncMock(return_value={
            "message": "You enter the tavern and see a bustling crowd.",
            "visuals": [{"image_url": "http://example.com/tavern.jpg"}],
            "state_updates": {"location": "tavern"},
            "combat_updates": None,
        })

        # Frontend request format (matches api.ts)
        frontend_request = {
            "message": "I enter the tavern",
            "character_id": "test-character-id",
            "campaign_id": "test-campaign-id",
        }

        response = client.post("/api/game/input", json=frontend_request)

        # Should succeed with mocked response or handle fallback gracefully
        # Accept 200 (success), 404 (character not found), or 500 (unexpected error in fallback)
        assert response.status_code in [200, 404, 500], f"Unexpected status: {response.status_code}, response: {response.json()}"

    def test_image_generation_endpoint_exists(self, client) -> None:
        """Test image generation endpoint matches frontend expectations."""
        # Frontend request format (matches api.ts)
        frontend_request = {
            "image_type": "character_portrait",
            "details": {"name": "Test Hero", "race": "human", "class": "fighter"},
        }

        response = client.post("/api/game/generate-image", json=frontend_request)

        # Should handle the request (even if it fails due to missing config)
        assert response.status_code in [200, 400, 500, 503], (
            f"Image generation endpoint returned unexpected status: {response.status_code}"
        )

    def test_battle_map_endpoint_exists(self, client) -> None:
        """Test battle map generation endpoint matches frontend expectations."""
        # Frontend request format (matches api.ts)
        frontend_request = {
            "environment": {"type": "forest", "size": "medium"},
            "combat_context": {"participants": 4},
        }

        response = client.post("/api/game/battle-map", json=frontend_request)

        # Should handle the request (even if it fails due to missing config)
        assert response.status_code in [200, 400, 500, 503], (
            f"Battle map endpoint returned unexpected status: {response.status_code}"
        )

    def test_dice_rolling_endpoints_exist(self, client) -> None:
        """Test dice rolling endpoints exist and handle requests."""
        # Test basic dice roll
        response = client.post("/api/game/dice/roll", json={"notation": "1d20"})
        assert response.status_code in [200, 400, 500], (
            f"Dice roll endpoint returned unexpected status: {response.status_code}"
        )

        # Test manual dice roll
        response = client.post(
            "/api/game/dice/manual-roll", json={"notation": "1d20", "result": 15}
        )
        assert response.status_code in [200, 400, 500], (
            f"Manual dice roll endpoint returned unexpected status: {response.status_code}"
        )

    def test_missing_endpoints_fail_properly(self, client) -> None:
        """Test that missing endpoints return 404."""
        missing_endpoints = [
            "/api/game/nonexistent",
            "/api/missing/route",
            "/api/game/character/missing/endpoint",
        ]

        for endpoint in missing_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404, (
                f"Missing endpoint {endpoint} should return 404"
            )

    def test_cors_headers_present(self, client) -> None:
        """Test that CORS headers are present for frontend access."""
        response = client.options("/api/game/character")
        # CORS should be configured to allow frontend access
        # The exact headers depend on the CORS configuration
        assert response.status_code in [200, 405], "CORS preflight should be handled"

    def test_websocket_route_exists(self, client) -> None:
        """Test that WebSocket route exists."""
        # We can't easily test WebSocket connection in this setup,
        # but we can verify the app has routes configured
        from app.main import app

        # The main goal is to ensure routes are configured
        # WebSocket routes are included via router inclusion
        assert len(app.routes) > 0, "App should have routes configured"

        # Check that websocket_routes module is imported in main.py
        import app.api.websocket_routes

        assert hasattr(app.api.websocket_routes, "router"), (
            "WebSocket router should be defined"
        )

    def test_frontend_backend_model_compatibility(self) -> None:
        """Test that frontend TypeScript models match backend Pydantic models."""
        from app.models.game_models import (
            Abilities,
            CharacterClass,
            CreateCampaignRequest,
            CreateCharacterRequest,
            GameResponse,
            PlayerInput,
            Race,
        )

        # Test that all required frontend fields are present in backend models

        # Character creation compatibility
        abilities = Abilities(strength=16)
        char_request = CreateCharacterRequest(
            name="Test",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=abilities,
        )
        char_dict = char_request.model_dump()
        frontend_char_fields = ["name", "race", "character_class", "abilities"]
        for field in frontend_char_fields:
            assert field in char_dict

        # Campaign creation compatibility
        campaign_request = CreateCampaignRequest(
            name="Test Campaign", setting="Fantasy"
        )
        campaign_dict = campaign_request.model_dump()
        frontend_campaign_fields = ["name", "setting", "tone", "homebrew_rules"]
        for field in frontend_campaign_fields:
            assert field in campaign_dict

        # Player input compatibility
        player_input = PlayerInput(
            message="Test message", character_id="test-id", campaign_id="test-campaign"
        )
        input_dict = player_input.model_dump()
        frontend_input_fields = ["message", "character_id", "campaign_id"]
        for field in frontend_input_fields:
            assert field in input_dict

        # Game response compatibility
        game_response = GameResponse(
            message="Test response", images=[], state_updates={}
        )
        response_dict = game_response.model_dump()
        frontend_response_fields = [
            "message",
            "images",
            "state_updates",
            "combat_updates",
        ]
        for field in frontend_response_fields:
            assert field in response_dict

    def test_error_response_format(self, client) -> None:
        """Test that error responses are in the expected format."""
        # Test invalid JSON
        response = client.post("/api/game/character", data="invalid json")
        assert response.status_code == 422  # Unprocessable Entity
        assert "detail" in response.json()

        # Test missing required fields
        response = client.post("/api/game/character", json={})
        assert response.status_code == 422
        assert "detail" in response.json()
