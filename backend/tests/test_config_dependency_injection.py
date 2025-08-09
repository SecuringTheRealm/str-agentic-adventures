"""
Tests for improved configuration handling via dependency injection.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.config import Settings, get_config
from app.main import app


class TestConfigurationDependencyInjection:
    """Test configuration dependency injection."""

    def test_character_creation_with_valid_config(self, client_with_config):
        """Test character creation with valid configuration."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            # Mock the scribe agent to avoid kernel initialization
            mock_scribe = MagicMock()

            # Make create_character return an awaitable with proper format
            async def create_character_async(*args, **kwargs):
                return {
                    "id": "char_123",
                    "name": "Test Character",
                    "race": "human",
                    "character_class": "fighter",
                    "level": 1,
                    "abilities": {
                        "strength": 16,
                        "dexterity": 14,
                        "constitution": 15,
                        "intelligence": 12,
                        "wisdom": 13,
                        "charisma": 10,
                    },
                    "hit_points": {"current": 12, "maximum": 12},
                    "armor_class": 16,
                    "inventory": [],
                    "features": [],
                    "spells": [],
                }

            mock_scribe.create_character = create_character_async
            mock_get_scribe.return_value = mock_scribe

            character_data = {
                "name": "Test Character",
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

            response = client_with_config.post(
                "/api/game/character", json=character_data
            )

            assert response.status_code == 200
            assert mock_get_scribe.called

    def test_character_creation_with_missing_config(self, client_with_missing_config):
        """Test character creation with missing Azure OpenAI configuration."""
        character_data = {
            "name": "Test Character",
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

        response = client_with_missing_config.post(
            "/api/game/character", json=character_data
        )

        # Should return 503 error for missing configuration
        assert response.status_code == 503
        assert "Azure OpenAI configuration" in response.json().get("detail", "")

    def test_campaign_creation_with_valid_config(self, client_with_config):
        """Test campaign creation with valid configuration."""
        with patch(
            "app.services.campaign_service.campaign_service.create_campaign"
        ) as mock_create:
            # Mock successful campaign creation
            mock_create.return_value = {
                "id": "camp_123",
                "name": "Test Campaign",
                "setting": "Fantasy World",
                "tone": "heroic",
                "created_at": "2024-01-01T00:00:00Z",
            }

            campaign_data = {
                "name": "Test Campaign",
                "setting": "Fantasy World",
                "tone": "heroic",
            }

            response = client_with_config.post("/api/game/campaign", json=campaign_data)

            assert response.status_code == 200
            assert mock_create.called

    def test_campaign_creation_with_missing_config(
        self, client_with_missing_config, campaign_factory
    ):
        """Test campaign creation with missing Azure OpenAI configuration."""
        # Use factory instead of hand-crafted dictionary
        campaign_data = campaign_factory()

        response = client_with_missing_config.post(
            "/api/game/campaign", json=campaign_data
        )

        # Should return 503 error for missing configuration
        assert response.status_code == 503
        assert "Azure OpenAI configuration" in response.json().get("detail", "")

    def test_config_dependency_injection_works(self):
        """Test that configuration dependency injection is functioning."""
        test_config = Settings(
            azure_openai_endpoint="https://test.example.com",
            azure_openai_api_key="test-key",
            azure_openai_chat_deployment="test-deployment",
            azure_openai_embedding_deployment="test-embedding",
        )

        # Override the dependency
        app.dependency_overrides[get_config] = lambda: test_config

        try:
            client = TestClient(app)

            # Test any endpoint that uses config dependency
            with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
                mock_scribe = MagicMock()

                # Make create_character return an awaitable with proper format
                async def create_character_async(*args, **kwargs):
                    return {
                        "id": "test",
                        "name": "Test",
                        "race": "human",
                        "character_class": "fighter",
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
                        "armor_class": 15,
                        "inventory": [],
                        "features": [],
                        "spells": [],
                    }

                mock_scribe.create_character = create_character_async
                mock_get_scribe.return_value = mock_scribe

                response = client.post(
                    "/api/game/character",
                    json={
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
                    },
                )

                # Should use the injected config and not fail with missing config
                assert response.status_code == 200

        finally:
            # Clean up
            app.dependency_overrides.clear()

    def test_get_character_with_valid_config(self, client_with_config):
        """Test get character with valid configuration."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = MagicMock()

            # Make get_character return an awaitable
            async def get_character_async(*args, **kwargs):
                return {
                    "id": "char_123",
                    "name": "Existing Character",
                    "race": "elf",
                    "character_class": "wizard",
                }

            mock_scribe.get_character = get_character_async
            mock_get_scribe.return_value = mock_scribe

            response = client_with_config.get("/api/game/character/char_123")

            assert response.status_code == 200
            assert mock_get_scribe.called

    def test_get_character_with_missing_config(self, client_with_missing_config):
        """Test get character with missing Azure OpenAI configuration."""
        response = client_with_missing_config.get("/api/game/character/char_123")

        # Should return 503 error for missing configuration
        assert response.status_code == 503
        assert "Azure OpenAI configuration" in response.json().get("detail", "")
