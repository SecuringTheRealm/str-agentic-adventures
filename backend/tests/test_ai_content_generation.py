"""
Test AI content generation endpoint functionality.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class TestAIContentGeneration:
    """Test AI content generation endpoint."""

    def test_ai_content_generation_endpoint_exists(self) -> None:
        """Test that the AI content generation endpoint exists and returns proper structure."""
        from app.main import app

        client = TestClient(app)

        # Test with minimal valid request
        request_data = {
            "suggestion": "Expand on character motivations",
            "current_text": "The party enters a tavern.",
            "context_type": "description",
            "campaign_tone": "heroic",
        }

        # This test focuses on endpoint structure, not Azure OpenAI functionality
        with patch("app.azure_openai_client.AzureOpenAIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat_completion = AsyncMock(
                return_value="Generated test content"
            )
            mock_client_class.return_value = mock_client

            response = client.post("/game/campaign/ai-generate", json=request_data)

            # Should return proper response structure
            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "generated_content" in data
            assert "success" in data
            assert isinstance(data["success"], bool)

            if data["success"]:
                assert isinstance(data["generated_content"], str)
                assert len(data["generated_content"]) > 0
            else:
                assert "error" in data

    def test_ai_content_generation_with_empty_text(self) -> None:
        """Test AI content generation with empty current text."""
        from app.main import app

        client = TestClient(app)

        request_data = {
            "suggestion": "Add environmental details",
            "current_text": "",
            "context_type": "setting",
            "campaign_tone": "dark",
        }

        with patch("app.azure_openai_client.AzureOpenAIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat_completion = AsyncMock(
                return_value="A dark forest shrouded in mist"
            )
            mock_client_class.return_value = mock_client

            response = client.post("/game/campaign/ai-generate", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert "generated_content" in data
            assert "success" in data

    def test_ai_content_generation_error_handling(self) -> None:
        """Test error handling when Azure OpenAI fails."""
        from app.main import app

        client = TestClient(app)

        request_data = {
            "suggestion": "Expand on character motivations",
            "current_text": "The party enters a tavern.",
            "context_type": "description",
            "campaign_tone": "heroic",
        }

        # Mock Azure OpenAI to raise an exception
        with patch("app.azure_openai_client.AzureOpenAIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat_completion = AsyncMock(
                side_effect=Exception("Azure OpenAI error")
            )
            mock_client_class.return_value = mock_client

            response = client.post("/game/campaign/ai-generate", json=request_data)
            assert (
                response.status_code == 200
            )  # Should still return 200 with error in response

            data = response.json()
            assert data["success"] is False
            assert "error" in data
            assert "Azure OpenAI error" in data["error"]

    def test_invalid_request_data(self) -> None:
        """Test with invalid request data."""
        from app.main import app

        client = TestClient(app)

        # Missing required fields
        invalid_request = {
            "suggestion": "Expand on character motivations"
            # Missing other required fields
        }

        response = client.post("/game/campaign/ai-generate", json=invalid_request)
        assert response.status_code == 422  # Validation error
