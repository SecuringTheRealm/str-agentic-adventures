"""
Example test showing migration from os.environ patching to dependency injection.
This demonstrates how to update existing tests that patch os.environ.
"""

import os
from unittest.mock import MagicMock, patch

from app.config import Settings, get_config
from app.main import app
from fastapi.testclient import TestClient

from .factories import create_standard_fighter


class TestMigrationExample:
    """Examples showing how to migrate from os.environ patching to dependency injection."""

    def test_old_pattern_os_environ_patching(self) -> None:
        """
        OLD PATTERN: Direct os.environ manipulation (problematic).

        This is the pattern we're replacing - it's fragile and can cause issues.
        """
        # Save original values
        original_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        original_key = os.environ.get("AZURE_OPENAI_API_KEY")

        # Modify environment
        if "AZURE_OPENAI_ENDPOINT" in os.environ:
            del os.environ["AZURE_OPENAI_ENDPOINT"]
        if "AZURE_OPENAI_API_KEY" in os.environ:
            del os.environ["AZURE_OPENAI_API_KEY"]

        try:
            # Test with modified environment
            client = TestClient(app)

            with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
                mock_scribe = MagicMock()

                async def mock_create_character(*args, **kwargs):
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

                mock_scribe.create_character = mock_create_character
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

                # Should return 503 due to missing configuration
                assert response.status_code == 503

        finally:
            # Restore environment - easy to forget and cause test pollution!
            if original_endpoint:
                os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint
            if original_key:
                os.environ["AZURE_OPENAI_API_KEY"] = original_key

    def test_new_pattern_dependency_injection(self) -> None:
        """
        NEW PATTERN: Use FastAPI dependency override (recommended).

        This is cleaner, more reliable, and doesn't affect global state.
        """
        # Create test configuration
        missing_config = Settings(
            azure_openai_endpoint="",  # Missing configuration
            azure_openai_api_key="",
            azure_openai_chat_deployment="",
            azure_openai_embedding_deployment="",
        )

        # Override the dependency
        app.dependency_overrides[get_config] = lambda: missing_config

        try:
            client = TestClient(app)

            with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
                mock_scribe = MagicMock()

                async def mock_create_character(*args, **kwargs):
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

                mock_scribe.create_character = mock_create_character
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

                # Should return 503 due to missing configuration
                assert response.status_code == 503

        finally:
            # Clean up - simple and reliable
            app.dependency_overrides.clear()

    def test_new_pattern_with_fixtures(self, client_with_missing_config) -> None:
        """
        NEW PATTERN: Use pytest fixtures for even cleaner tests.

        This is the cleanest approach using the fixtures from conftest.py.
        """
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = MagicMock()

            async def mock_create_character(*args, **kwargs):
                return create_standard_fighter()

            mock_scribe.create_character = mock_create_character
            mock_get_scribe.return_value = mock_scribe

            # Use factory for request data too
            character_data = create_standard_fighter()
            response = client_with_missing_config.post(
                "/api/game/character",
                json={
                    "name": character_data["name"],
                    "race": character_data["race"],
                    "character_class": character_data["character_class"],
                    "abilities": character_data["abilities"],
                },
            )

            # Should return 503 due to missing configuration
            assert response.status_code == 503

    def test_migration_benefits_demonstration(self) -> None:
        """
        Demonstrate the benefits of the new pattern.
        """
        # 1. Create different configurations easily
        valid_config = Settings(
            azure_openai_endpoint="https://test.openai.azure.com",
            azure_openai_api_key="test-key",
            azure_openai_chat_deployment="test-chat",
            azure_openai_embedding_deployment="test-embedding",
        )

        invalid_config = Settings(
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_chat_deployment="",
            azure_openai_embedding_deployment="",
        )

        # 2. Test with valid config
        app.dependency_overrides[get_config] = lambda: valid_config
        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = MagicMock()

            async def mock_create_character(*args, **kwargs):
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

            mock_scribe.create_character = mock_create_character
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
            assert response.status_code == 200

        # 3. Switch to invalid config in the same test
        app.dependency_overrides[get_config] = lambda: invalid_config

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
        assert response.status_code == 503

        # 4. Clean up
        app.dependency_overrides.clear()

        # Benefits demonstrated:
        # - No global state pollution
        # - Easy to switch configurations within a test
        # - Clean, readable code
        # - No risk of forgetting to restore environment
        # - Consistent behavior across test runs
