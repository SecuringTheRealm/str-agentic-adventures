"""
Comprehensive test for the campaign endpoint to ensure proper behavior.
"""

from fastapi.testclient import TestClient


def test_campaign_endpoint_with_missing_config() -> bool | None:
    """Test that campaign endpoint works without Azure OpenAI configuration.
    
    Note: Basic campaign creation doesn't require Azure OpenAI. Only character
    creation and AI-powered features require Azure OpenAI configuration.
    """
    from app.main import app
    client = TestClient(app)

    # Test campaign creation - should work without Azure config
    campaign_data = {
        "name": "Test Campaign",
        "setting": "fantasy",
        "tone": "heroic",
    }

    response = client.post("/api/game/campaign", json=campaign_data)

    # Campaign creation should succeed without Azure OpenAI
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    response_data = response.json()
    assert "id" in response_data, "Response should contain campaign ID"
    assert response_data["name"] == "Test Campaign"

    print(
        "✓ Test passed: Campaign endpoint works without Azure OpenAI configuration"
    )
    return True


def test_campaign_endpoint_with_config() -> bool | None:
    """Test that campaign endpoint works with configuration.
    
    Note: Campaign creation doesn't require Azure OpenAI configuration,
    so this test simply verifies the endpoint works correctly.
    """
    from app.main import app

    client = TestClient(app)

    # Test campaign creation
    campaign_data = {
        "name": "Test Campaign",
        "setting": "fantasy",
        "tone": "heroic",
    }

    response = client.post("/api/game/campaign", json=campaign_data)

    # Campaign creation should succeed
    if response.status_code != 200:
        print(
            f"✗ Test failed: Campaign creation failed with status {response.status_code}"
        )
        return False

    print(
        f"✓ Test passed: Campaign creation succeeded with status {response.status_code}"
    )
    return True


if __name__ == "__main__":
    print("Testing campaign endpoint error handling...")

    success1 = test_campaign_endpoint_with_missing_config()
    success2 = test_campaign_endpoint_with_config()

    if success1 and success2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)
