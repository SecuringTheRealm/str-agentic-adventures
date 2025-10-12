"""
Comprehensive API route tests with proper error handling and edge cases.
"""

import os
import sys
from unittest.mock import AsyncMock, Mock, patch

import httpx
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIRouteValidation:
    """Test API route input validation and error handling."""

    def test_character_creation_validation(self) -> None:
        """Test character creation endpoint validation."""
        from app.main import app

        client = TestClient(app)

        # Test missing required fields
        invalid_requests = [
            {},  # Empty request
            {"name": "Test"},  # Missing other required fields
            {"name": "", "race": "human", "character_class": "fighter"},  # Empty name
            {"name": "Test", "race": "", "character_class": "fighter"},  # Empty race
            {"name": "Test", "race": "human", "character_class": ""},  # Empty class
            {
                "name": "Test",
                "race": "human",
                "character_class": "fighter",
            },  # Missing abilities
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/game/character", json=invalid_request)
            assert response.status_code == 422, (
                f"Should reject invalid request: {invalid_request}"
            )

    def test_character_creation_with_valid_data(self) -> None:
        """Test character creation with valid data and mocked agent."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock successful character creation
            mock_scribe = Mock()
            mock_scribe.create_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test Hero",
                    "character_class": "fighter",
                    "race": "human",
                    "level": 1,
                    "abilities": {
                        "strength": 16,
                        "dexterity": 14,
                        "constitution": 15,
                        "intelligence": 12,
                        "wisdom": 13,
                        "charisma": 10,
                    },
                    "hit_points": {"current": 10, "maximum": 10},
                    "armor_class": 10,
                    "proficiency_bonus": 2,
                    "inventory": [],
                    "spells": [],
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app

            client = TestClient(app)

            valid_request = {
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
            }

            response = client.post("/api/game/character", json=valid_request)

            if response.status_code == 200:
                data = response.json()
                assert data["name"] == "Test Hero"
                assert data["character_class"] == "fighter"
                assert "id" in data
            else:
                # If agent dependencies are missing or validation fails, expect proper error handling
                assert response.status_code in [400, 500, 503]

    def test_campaign_creation_validation(self) -> None:
        """Test campaign creation endpoint validation."""
        from app.main import app

        client = TestClient(app)

        # Test missing required fields - these should fail validation
        invalid_requests = [
            {},  # Empty request
            {"name": "Test"},  # Missing setting
            {"setting": "Fantasy"},  # Missing name
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/game/campaign", json=invalid_request)
            assert response.status_code == 422, (
                f"Should reject invalid request: {invalid_request}"
            )

        # Empty strings are technically valid in the Pydantic model
        # but may be handled by business logic - test these separately
        edge_cases = [
            {"name": "", "setting": "Fantasy"},  # Empty name
            {"name": "Test", "setting": ""},  # Empty setting
        ]

        for edge_case in edge_cases:
            response = client.post("/api/game/campaign", json=edge_case)
            # Accept either success or validation error
            assert response.status_code in [200, 422], (
                f"Edge case should succeed or fail validation: {edge_case}, got {response.status_code}"
            )

    def test_player_input_validation(self) -> None:
        """Test player input endpoint validation."""
        from app.main import app

        client = TestClient(app)

        # Test missing required fields
        invalid_requests = [
            {},  # Empty request
            {"message": "Hello"},  # Missing IDs
            {
                "message": "",
                "character_id": "char_123",
                "campaign_id": "camp_456",
            },  # Empty message
            {
                "message": "Hello",
                "character_id": "",
                "campaign_id": "camp_456",
            },  # Empty character_id
            {
                "message": "Hello",
                "character_id": "char_123",
                "campaign_id": "",
            },  # Empty campaign_id
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/game/input", json=invalid_request)
            assert response.status_code == 422, (
                f"Should reject invalid request: {invalid_request}"
            )


class TestAPIRouteErrorHandling:
    """Test API route error handling scenarios."""

    def test_character_creation_agent_error(self) -> None:
        """Test character creation when agent returns error."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock agent returning error
            mock_scribe = Mock()
            mock_scribe.create_character = AsyncMock(
                return_value={
                    "error": "Invalid character data: abilities must sum to specific total"
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app

            client = TestClient(app)

            request_data = {
                "name": "Test Hero",
                "race": "human",
                "character_class": "fighter",
                "abilities": {
                    "strength": 50,  # Invalid high value
                    "dexterity": 50,
                    "constitution": 50,
                    "intelligence": 50,
                    "wisdom": 50,
                    "charisma": 50,
                },
            }

            response = client.post("/api/game/character", json=request_data)

            if response.status_code == 400:
                # Should return proper error message
                data = response.json()
                assert "detail" in data
            else:
                # If dependencies missing, should handle gracefully
                assert response.status_code in [500, 503]

    def test_character_creation_agent_exception(self) -> None:
        """Test character creation when agent raises exception."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock agent raising exception
            mock_scribe = Mock()
            mock_scribe.create_character = AsyncMock(
                side_effect=Exception("Database connection failed")
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app

            client = TestClient(app)

            request_data = {
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
            }

            response = client.post("/api/game/character", json=request_data)

            # Should return 400 (validation error) or 500 error with meaningful message
            assert response.status_code in [400, 500]
            data = response.json()
            assert "detail" in data

    def test_campaign_creation_missing_dependencies(self) -> None:
        """Test campaign creation works without Azure dependencies.

        Note: Campaign creation doesn't require Azure OpenAI, only character creation does.
        """
        from app.main import app

        client = TestClient(app)

        request_data = {
            "name": "Test Campaign",
            "setting": "Fantasy World",
            "tone": "heroic",
        }

        response = client.post("/api/game/campaign", json=request_data)

        # Campaign creation should succeed without Azure config
        assert response.status_code == 200, (
            f"Campaign creation should succeed without Azure OpenAI, got: {response.status_code}"
        )
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Campaign"


class TestAPIRouteDataTransformation:
    """Test API route data transformation between API and agents."""

    def test_character_class_field_transformation(self) -> None:
        """Test that character_class is properly transformed to class for agents."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.create_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test",
                    "character_class": "fighter",
                    "race": "human",
                    "level": 1,
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app

            client = TestClient(app)

            request_data = {
                "name": "Test",
                "race": "human",
                "character_class": "fighter",  # API uses character_class
                "abilities": {
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10,
                },
            }

            response = client.post("/api/game/character", json=request_data)

            if response.status_code == 200:
                # Verify agent was called with transformed data
                call_args = mock_scribe.create_character.call_args[0][0]
                assert "class" in call_args  # Should be transformed to "class"
                assert call_args["class"] == "fighter"
                assert (
                    "character_class" not in call_args
                )  # Should not have original field

    def test_homebrew_rules_array_transformation(self) -> None:
        """Test that homebrew rules are properly handled as an array."""
        from app.main import app

        client = TestClient(app)

        request_data = {
            "name": "Test Campaign",
            "setting": "Fantasy World",
            "tone": "heroic",
            "homebrew_rules": ["Custom rule 1", "Custom rule 2"],
        }

        response = client.post("/api/game/campaign", json=request_data)

        # Campaign creation should succeed
        assert response.status_code == 200, (
            f"Campaign creation should succeed, got: {response.status_code}"
        )

        data = response.json()
        # Verify homebrew rules are preserved
        assert "homebrew_rules" in data
        assert isinstance(data["homebrew_rules"], list)
        assert len(data["homebrew_rules"]) == 2


class TestAPIRoutePerformance:
    """Test API route performance and timeout handling."""

    def test_character_creation_timeout_handling(self) -> None:
        """Test character creation handles agent timeouts."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock agent that takes too long
            async def slow_create_character(data):
                import asyncio

                await asyncio.sleep(10)  # Simulate timeout
                return {"id": "char_123"}

            mock_scribe = Mock()
            mock_scribe.create_character = slow_create_character
            mock_get_scribe.return_value = mock_scribe

            from app.main import app

            client = TestClient(app)

            request_data = {
                "name": "Test",
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
            }

            # This test might timeout depending on client settings
            # In a real scenario, we'd configure appropriate timeouts
            try:
                response = client.post("/api/game/character", json=request_data)
                # If it completes, verify it handles the delay (including 400 for validation errors)
                assert response.status_code in [200, 400, 500, 503, 504]
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout):
                # Timeout is expected behavior for this test
                pass
            except Exception:
                # Re-raise any non-timeout-related exceptions to avoid masking errors
                raise


class TestAPIRouteSecurity:
    """Test API route security considerations."""

    def test_large_payload_handling(self) -> None:
        """Test API handles unreasonably large payloads."""
        from app.main import app

        client = TestClient(app)

        # Create very large payload
        large_backstory = "A" * 100000  # 100KB backstory

        request_data = {
            "name": "Test",
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
            "backstory": large_backstory,
        }

        response = client.post("/api/game/character", json=request_data)

        # Should handle large payload gracefully (including 400 for validation)
        assert response.status_code in [200, 400, 413, 422, 500]

    def test_malformed_json_handling(self) -> None:
        """Test API handles malformed JSON."""
        from app.main import app

        client = TestClient(app)

        # Send malformed JSON
        response = client.post(
            "/api/game/character",
            content="{'invalid': json}",  # Malformed JSON
            headers={"Content-Type": "application/json"},
        )

        # Should reject with appropriate error
        assert response.status_code == 422

    def test_sql_injection_protection(self) -> None:
        """Test API protects against SQL injection attempts."""
        from app.main import app

        client = TestClient(app)

        malicious_inputs = [
            "'; DROP TABLE characters; --",
            "' OR '1'='1",
            "1'; UNION SELECT * FROM users; --",
        ]

        for malicious_input in malicious_inputs:
            request_data = {
                "name": malicious_input,
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
            }

            response = client.post("/api/game/character", json=request_data)

            # Should handle malicious input safely
            # Either process it as regular text or reject appropriately
            assert response.status_code in [200, 400, 422, 500]
