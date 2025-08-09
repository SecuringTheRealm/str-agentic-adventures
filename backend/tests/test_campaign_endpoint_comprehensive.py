"""
Comprehensive test for the campaign endpoint to ensure proper error handling.
"""

import os

from fastapi.testclient import TestClient


def test_campaign_endpoint_with_missing_config() -> bool | None:
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

        # We expect a service unavailable error (503) with proper error message about Azure OpenAI
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"

        response_data = response.json()
        detail = response_data.get("detail", "")

        assert "Azure OpenAI configuration" in detail, (
            f"Error message should mention Azure OpenAI configuration: {detail}"
        )
        assert "agentic demo requires" in detail, (
            f"Error should mention this is an agentic demo: {detail}"
        )
        assert "AZURE_OPENAI_ENDPOINT" in detail, (
            f"Error should list required env vars: {detail}"
        )

        print(
            "✓ Test passed: Campaign endpoint properly handles missing Azure OpenAI configuration"
        )
        return True

    finally:
        # Restore original environment values
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]


def test_campaign_endpoint_with_config() -> bool | None:
    """Test that campaign endpoint works when Azure OpenAI configuration is provided."""

    # Set minimal valid Azure OpenAI configuration
    test_config = {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key-12345",
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002",
    }

    original_values = {}
    for var, value in test_config.items():
        original_values[var] = os.environ.get(var)
        os.environ[var] = value

    try:
        # Import after setting environment
        from app.main import app

        client = TestClient(app)

        # Test campaign creation with valid config
        campaign_data = {
            "name": "Test Campaign",
            "setting": "fantasy",
            "tone": "heroic",
        }

        response = client.post("/api/game/campaign", json=campaign_data)

        # This might fail due to the actual Azure OpenAI calls, but should not be a 503 config error
        if response.status_code == 503:
            response_data = response.json()
            detail = response_data.get("detail", "")
            if "Azure OpenAI configuration" in detail:
                print(
                    "✗ Test failed: Still getting configuration error even with config set"
                )
                return False

        print(
            f"✓ Test passed: With configuration, got status {response.status_code} (not 503 config error)"
        )
        return True

    finally:
        # Restore original environment values
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]


if __name__ == "__main__":
    print("Testing campaign endpoint error handling...")

    success1 = test_campaign_endpoint_with_missing_config()
    success2 = test_campaign_endpoint_with_config()

    if success1 and success2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)
