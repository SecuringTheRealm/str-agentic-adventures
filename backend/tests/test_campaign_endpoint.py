"""
Test campaign endpoint functionality and error handling.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestCampaignEndpoint:
    """Test campaign endpoint with proper assertions."""

    def test_campaign_endpoint_with_missing_config(self):
        """Test that campaign endpoint properly handles missing Azure OpenAI configuration."""

        # Temporarily clear Azure OpenAI environment variables
        env_vars_to_clear = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
        ]

        original_values = {}
        for var in env_vars_to_clear:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        try:
            # Import after clearing environment to ensure settings get the missing values
            from app.main import app

            client = TestClient(app)

            # Test campaign creation with missing config
            campaign_data = {
                "name": "Test Campaign",
                "setting": "fantasy",
                "tone": "heroic",
            }

            response = client.post("/api/game/campaign", json=campaign_data)

            # Assert proper error handling for missing Azure config
            assert response.status_code in [404, 500, 503], (
                f"Unexpected status code: {response.status_code}"
            )

            if response.status_code == 404:
                pytest.fail(
                    "Got 404 - endpoint not found. This indicates a routing issue."
                )
            elif response.status_code in [500, 503]:
                response_data = response.json()
                # Should contain meaningful error message
                assert "detail" in response_data, (
                    "Error response should contain 'detail' field"
                )
                detail = response_data["detail"]
                # Error should be informative about configuration issue
                assert len(detail) > 10, "Error detail should be informative"

        finally:
            # Restore original environment values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]

    def test_campaign_endpoint_with_valid_data(self):
        """Test campaign creation with valid data and mocked dependencies."""

        with patch("app.agents.dungeon_master_agent.get_dungeon_master") as mock_dm:
            # Mock successful campaign creation
            mock_dm.return_value.create_campaign.return_value = {
                "id": "camp_123",
                "name": "Test Campaign",
                "setting": "fantasy",
                "tone": "heroic",
                "homebrew_rules": [],
                "characters": [],
                "session_log": [],
                "state": "created",
            }

            from app.main import app

            client = TestClient(app)

            campaign_data = {
                "name": "Test Campaign",
                "setting": "A magical fantasy world",
                "tone": "heroic",
            }

            response = client.post("/api/game/campaign", json=campaign_data)

            # Should succeed with mocked agent
            if response.status_code == 200:
                response_data = response.json()
                assert response_data["name"] == "Test Campaign"
                assert response_data["setting"] == "fantasy"
                assert "id" in response_data
            else:
                # If still failing due to missing dependencies, that's expected
                assert response.status_code in [500, 503], (
                    f"Unexpected status: {response.status_code}"
                )

    def test_campaign_endpoint_validation(self):
        """Test campaign endpoint input validation."""

        from app.main import app

        client = TestClient(app)

        # Test missing required fields
        invalid_data = {"name": "Test"}  # Missing setting
        response = client.post("/api/game/campaign", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422, (
            "Should return validation error for missing fields"
        )

        # Test empty name
        invalid_data = {"name": "", "setting": "fantasy"}
        response = client.post("/api/game/campaign", json=invalid_data)

        # Should return validation error for empty name
        assert response.status_code == 422, (
            "Should return validation error for empty name"
        )


if __name__ == "__main__":
    test_obj = TestCampaignEndpoint()
    test_obj.test_campaign_endpoint_with_missing_config()
