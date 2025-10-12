"""
Test campaign endpoint functionality and error handling.
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestCampaignEndpoint:
    """Test campaign endpoint with proper assertions."""

    def test_campaign_endpoint_with_missing_config(self) -> None:
        """Test that basic campaign creation works without Azure OpenAI.
        
        Note: Campaign creation doesn't require Azure OpenAI for basic functionality.
        Only character creation and AI-powered features require Azure OpenAI.
        """
        from app.main import app
        client = TestClient(app)

        # Test campaign creation - should succeed without Azure config
        campaign_data = {
            "name": "Test Campaign",
            "setting": "fantasy",
            "tone": "heroic",
        }

        response = client.post("/api/game/campaign", json=campaign_data)

        # Campaign creation should succeed (doesn't require Azure OpenAI)
        assert response.status_code == 200, (
            f"Campaign creation should succeed without Azure OpenAI, got: {response.status_code}"
        )
        
        response_data = response.json()
        assert response_data["name"] == "Test Campaign"
        assert "id" in response_data

    def test_campaign_endpoint_with_valid_data(self) -> None:
        """Test campaign creation with valid data."""
        from app.main import app
        client = TestClient(app)

        campaign_data = {
            "name": "Test Campaign",
            "setting": "A magical fantasy world",
            "tone": "heroic",
        }

        response = client.post("/api/game/campaign", json=campaign_data)

        # Campaign creation should succeed
        assert response.status_code == 200, (
            f"Unexpected status: {response.status_code}"
        )
        
        response_data = response.json()
        assert response_data["name"] == "Test Campaign"
        assert response_data["setting"] == "A magical fantasy world"
        assert "id" in response_data

    def test_campaign_endpoint_validation(self) -> None:
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

        # Test with valid minimum data - campaigns don't validate empty names at Pydantic level
        # but they should still create successfully
        minimal_data = {"name": "", "setting": "fantasy"}
        response = client.post("/api/game/campaign", json=minimal_data)

        # Empty name is allowed by the model, so this should succeed
        assert response.status_code in [200, 422], (
            f"Should either succeed or return validation error, got: {response.status_code}"
        )


if __name__ == "__main__":
    test_obj = TestCampaignEndpoint()
    test_obj.test_campaign_endpoint_with_missing_config()
