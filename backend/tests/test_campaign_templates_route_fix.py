"""Test campaign templates route ordering fix."""

import pytest
from app.main import app
from fastapi.testclient import TestClient


class TestCampaignTemplatesRouteOrdering:
    """Test that campaign templates route is correctly ordered before parameterized route."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_campaign_templates_route_works(self, client) -> None:
        """Test that /campaign/templates returns templates successfully."""
        response = client.get("/api/game/campaign/templates")

        # Should return 200 OK, not 404
        assert response.status_code == 200

        # Should return templates in expected format
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

        # Templates may be empty in test database - that's OK
        # The important thing is the endpoint works and returns proper structure
        if len(data["templates"]) > 0:
            # Each template should have expected fields
            for template in data["templates"]:
                assert "id" in template
                assert "name" in template
                assert "is_template" in template
                assert template["is_template"] is True

    def test_campaign_id_route_still_works(self, client) -> None:
        """Test that parameterized campaign route still works for actual IDs."""
        # First create a campaign to test with
        campaign_data = {
            "name": "Test Campaign",
            "setting": "Test Setting",
            "tone": "heroic",
        }
        create_response = client.post("/api/game/campaign", json=campaign_data)
        assert create_response.status_code == 200

        campaign_id = create_response.json()["id"]

        # Now try to get this specific campaign
        campaign_response = client.get(f"/api/game/campaign/{campaign_id}")

        # Should return 200 OK (campaign exists)
        assert campaign_response.status_code == 200

        campaign = campaign_response.json()
        assert campaign["id"] == campaign_id
        assert campaign["name"] == "Test Campaign"

    def test_nonexistent_campaign_returns_404(self, client) -> None:
        """Test that non-existent campaign ID returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/game/campaign/{fake_id}")

        # Should return 404 for non-existent campaign
        assert response.status_code == 404

        error = response.json()
        assert "detail" in error
        assert fake_id in error["detail"]

    def test_templates_word_not_treated_as_campaign_id(self, client) -> None:
        """Test that 'templates' is not treated as a campaign ID."""
        # This is the core test - before our fix, this would return 404 with
        # "Campaign templates not found" because 'templates' was treated as campaign_id
        response = client.get("/api/game/campaign/templates")

        # Should NOT return 404 with campaign not found error
        assert response.status_code != 404

        # Should return 200 with templates
        assert response.status_code == 200

        data = response.json()
        assert "templates" in data
        # Should not have an error about "Campaign templates not found"
        assert "detail" not in data
