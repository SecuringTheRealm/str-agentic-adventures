"""
Tests for the opening narrative feature:
- NarratorAgent.generate_opening_narrative method
- POST /campaign/{campaign_id}/opening-narrative endpoint
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestNarratorAgentOpeningNarrative:
    """Tests for NarratorAgent.generate_opening_narrative."""

    @pytest.mark.asyncio
    async def test_fallback_mode_returns_narrative(self) -> None:
        """generate_opening_narrative returns a valid structure in fallback mode."""
        from app.agents.narrator_agent import NarratorAgent

        with patch("app.agents.base_agent.agent_client_manager") as mock_manager:
            mock_manager.get_chat_client.return_value = None

            agent = NarratorAgent()
            assert agent._fallback_mode

        campaign_ctx = {
            "id": "camp-1",
            "name": "The Lost Realm",
            "setting": "fantasy",
            "tone": "heroic",
            "world_description": "A mystical land filled with ancient ruins.",
        }
        character_ctx = {
            "name": "Aldric",
            "character_class": "fighter",
            "race": "human",
            "backstory": "",
        }

        result = await agent.generate_opening_narrative(campaign_ctx, character_ctx)

        assert "scene_description" in result
        assert "quest_hook" in result
        assert "suggested_actions" in result
        assert "help_text" in result
        assert isinstance(result["suggested_actions"], list)
        assert 1 <= len(result["suggested_actions"]) <= 3
        assert result["help_text"] == "What can I do?"

    @pytest.mark.asyncio
    async def test_azure_path_returns_narrative(self) -> None:
        """generate_opening_narrative uses Azure OpenAI when available."""
        import json

        from app.agents.narrator_agent import NarratorAgent

        mock_azure_client = AsyncMock()
        # First call: describe_scene, second call: quest_hook + actions
        mock_azure_client.chat_completion.side_effect = [
            "The ancient city stretches before you, its spires piercing storm clouds.",
            json.dumps(
                {
                    "quest_hook": "A dying merchant presses a treasure map into your hand.",
                    "suggested_actions": [
                        "Examine the treasure map",
                        "Ask the merchant for more details",
                        "Look for a safe place to rest",
                    ],
                }
            ),
        ]

        with patch("app.agents.base_agent.agent_client_manager") as mock_manager:
            mock_chat = MagicMock()
            mock_manager.get_chat_client.return_value = mock_chat

            agent = NarratorAgent()
            agent._fallback_mode = False
            agent.azure_client = mock_azure_client

        campaign_ctx = {
            "id": "camp-2",
            "name": "Shadows of the Past",
            "setting": "dark fantasy",
            "tone": "dark",
            "world_description": "A realm shrouded in eternal twilight.",
        }
        character_ctx = {
            "name": "Lyra",
            "character_class": "rogue",
            "race": "elf",
            "backstory": "Exiled from her homeland.",
        }

        result = await agent.generate_opening_narrative(campaign_ctx, character_ctx)

        assert result["scene_description"] == (
            "The ancient city stretches before you, its spires piercing storm clouds."
        )
        assert result["quest_hook"] == "A dying merchant presses a treasure map into your hand."
        assert len(result["suggested_actions"]) == 3
        assert result["help_text"] == "What can I do?"

    @pytest.mark.asyncio
    async def test_azure_failure_falls_back_gracefully(self) -> None:
        """When Azure fails partway, fallback narrative is returned with scene description."""

        from app.agents.narrator_agent import NarratorAgent

        mock_azure_client = AsyncMock()
        # describe_scene succeeds, but the JSON generation fails
        mock_azure_client.chat_completion.side_effect = [
            "A stormy night descends on the village.",
            Exception("Azure quota exceeded"),
        ]

        with patch("app.agents.base_agent.agent_client_manager") as mock_manager:
            mock_chat = MagicMock()
            mock_manager.get_chat_client.return_value = mock_chat

            agent = NarratorAgent()
            agent._fallback_mode = False
            agent.azure_client = mock_azure_client

        campaign_ctx = {
            "id": "camp-3",
            "name": "Test Campaign",
            "setting": "fantasy",
            "tone": "mystery",
            "world_description": "",
        }
        character_ctx = {
            "name": "Gareth",
            "character_class": "wizard",
            "race": "gnome",
            "backstory": "",
        }

        result = await agent.generate_opening_narrative(campaign_ctx, character_ctx)

        # Scene description from the first Azure call should be preserved
        assert result["scene_description"] == "A stormy night descends on the village."
        assert "quest_hook" in result
        assert isinstance(result["suggested_actions"], list)

    @pytest.mark.asyncio
    async def test_fallback_narrative_tone_variations(self) -> None:
        """_fallback_opening_narrative returns different hooks for each tone."""
        from app.agents.narrator_agent import NarratorAgent

        with patch("app.agents.base_agent.agent_client_manager") as mock_manager:
            mock_manager.get_chat_client.return_value = None
            agent = NarratorAgent()

        tones = ["heroic", "dark", "mystery", "comedy"]
        results = {
            tone: agent._fallback_opening_narrative("Hero", "fighter", "fantasy", tone)
            for tone in tones
        }

        # All tones should produce valid structure
        for _tone, result in results.items():
            assert "quest_hook" in result
            assert "suggested_actions" in result
            assert len(result["suggested_actions"]) >= 1

        # Each tone should produce a different hook
        hooks = [results[t]["quest_hook"] for t in tones]
        assert len(set(hooks)) == len(tones), "Each tone should have a unique quest hook"

    @pytest.mark.asyncio
    async def test_suggested_actions_capped_at_three(self) -> None:
        """Azure response with more than 3 actions is capped to 3."""
        import json

        from app.agents.narrator_agent import NarratorAgent

        mock_azure_client = AsyncMock()
        mock_azure_client.chat_completion.side_effect = [
            "You stand at the crossroads.",
            json.dumps(
                {
                    "quest_hook": "The road to glory begins here.",
                    "suggested_actions": [
                        "Action 1",
                        "Action 2",
                        "Action 3",
                        "Action 4",  # Extra action that should be truncated
                    ],
                }
            ),
        ]

        with patch("app.agents.base_agent.agent_client_manager") as mock_manager:
            mock_manager.get_chat_client.return_value = MagicMock()
            agent = NarratorAgent()
            agent._fallback_mode = False
            agent.azure_client = mock_azure_client

        result = await agent.generate_opening_narrative(
            {"id": "c", "setting": "fantasy", "tone": "heroic", "world_description": ""},
            {"name": "Tester", "character_class": "fighter", "race": "", "backstory": ""},
        )

        assert len(result["suggested_actions"]) == 3


class TestOpeningNarrativeEndpoint:
    """Tests for POST /game/campaign/{campaign_id}/opening-narrative."""

    def test_endpoint_success(self) -> None:
        """Endpoint returns opening narrative for a valid campaign."""
        from app.main import app

        client = TestClient(app)

        mock_campaign = MagicMock()
        mock_campaign.name = "The Lost Realm"
        mock_campaign.setting = "fantasy"
        mock_campaign.tone = "heroic"
        mock_campaign.world_description = "A magical world."

        mock_opening = {
            "scene_description": "You stand at the edge of a grand city.",
            "quest_hook": "A cloaked figure beckons you into a dark alley.",
            "suggested_actions": [
                "Follow the figure",
                "Ignore and look around",
                "Ask nearby guards",
            ],
            "help_text": "What can I do?",
        }

        with (
            patch(
                "app.services.campaign_service.campaign_service.get_campaign",
                return_value=mock_campaign,
            ),
            patch(
                "app.api.routes.session_routes.get_narrator"
            ) as mock_get_narrator,
        ):
            mock_narrator = AsyncMock()
            mock_narrator.generate_opening_narrative.return_value = mock_opening
            mock_get_narrator.return_value = mock_narrator

            response = client.post(
                "/game/campaign/camp-1/opening-narrative",
                json={
                    "character": {
                        "name": "Aldric",
                        "character_class": "fighter",
                        "race": "human",
                        "backstory": "",
                    }
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["scene_description"] == "You stand at the edge of a grand city."
        assert data["quest_hook"] == "A cloaked figure beckons you into a dark alley."
        assert len(data["suggested_actions"]) == 3
        assert data["help_text"] == "What can I do?"

    def test_endpoint_campaign_not_found(self) -> None:
        """Endpoint returns 404 when campaign does not exist."""
        from app.main import app

        client = TestClient(app)

        with patch(
            "app.services.campaign_service.campaign_service.get_campaign",
            return_value=None,
        ):
            response = client.post(
                "/game/campaign/nonexistent/opening-narrative",
                json={"character": {"name": "Hero"}},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_endpoint_narrator_error_returns_500(self) -> None:
        """Endpoint returns 500 when narrator agent raises an unexpected error."""
        from app.main import app

        client = TestClient(app)

        mock_campaign = MagicMock()
        mock_campaign.name = "Test Campaign"
        mock_campaign.setting = "fantasy"
        mock_campaign.tone = "heroic"
        mock_campaign.world_description = ""

        with (
            patch(
                "app.services.campaign_service.campaign_service.get_campaign",
                return_value=mock_campaign,
            ),
            patch(
                "app.api.routes.session_routes.get_narrator"
            ) as mock_get_narrator,
        ):
            mock_narrator = AsyncMock()
            mock_narrator.generate_opening_narrative.side_effect = RuntimeError(
                "Unexpected error"
            )
            mock_get_narrator.return_value = mock_narrator

            response = client.post(
                "/game/campaign/camp-1/opening-narrative",
                json={"character": {}},
            )

        assert response.status_code == 500
        assert "Failed to generate opening narrative" in response.json()["detail"]

    def test_endpoint_empty_character_context(self) -> None:
        """Endpoint handles empty character context gracefully."""
        from app.main import app

        client = TestClient(app)

        mock_campaign = MagicMock()
        mock_campaign.name = "Test Campaign"
        mock_campaign.setting = "fantasy"
        mock_campaign.tone = "heroic"
        mock_campaign.world_description = None

        mock_opening = {
            "scene_description": "Your adventure begins.",
            "quest_hook": "Adventure awaits.",
            "suggested_actions": ["Look around", "Ask for directions"],
            "help_text": "What can I do?",
        }

        with (
            patch(
                "app.services.campaign_service.campaign_service.get_campaign",
                return_value=mock_campaign,
            ),
            patch(
                "app.api.routes.session_routes.get_narrator"
            ) as mock_get_narrator,
        ):
            mock_narrator = AsyncMock()
            mock_narrator.generate_opening_narrative.return_value = mock_opening
            mock_get_narrator.return_value = mock_narrator

            response = client.post(
                "/game/campaign/camp-1/opening-narrative",
                json={},  # No character context
            )

        assert response.status_code == 200
