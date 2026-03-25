"""
Tests for dice roll narrative integration with the DM agent.

Covers the narrate_dice_roll method (fallback and Azure modes) and
the handle_dice_roll WebSocket handler's DM narration path.
"""

# ruff: noqa: ANN001, ANN201, ANN202

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dm_agent(fallback: bool = True):
    """Return a DungeonMasterAgent instance with Azure dependencies mocked out."""
    with patch("app.agents.dungeon_master_agent.agent_client_manager"):
        from app.agents.dungeon_master_agent import DungeonMasterAgent

        agent = DungeonMasterAgent.__new__(DungeonMasterAgent)
        agent._threads = {}
        agent._fallback_mode = fallback
        agent._fallback_initialized = False
        agent.chat_client = None
        agent.azure_client = None
        return agent


# ---------------------------------------------------------------------------
# narrate_dice_roll – fallback mode
# ---------------------------------------------------------------------------


class TestNarrateDiceRollFallback:
    """Test _fallback_narrate_dice_roll via narrate_dice_roll in fallback mode."""

    @pytest.fixture
    def agent(self):
        """Provide a DM agent instance in fallback mode."""
        return _make_dm_agent(fallback=True)

    @pytest.mark.anyio("asyncio")
    async def test_natural_20_single_d20(self, agent) -> None:
        """Natural 20 on a single d20 returns a critical success message."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Aria",
                "notation": "1d20",
                "result": {"total": 20, "rolls": [20]},
                "skill": None,
            }
        )
        assert "natural 20" in result.lower() or "critical success" in result.lower()
        assert "20" in result

    @pytest.mark.anyio("asyncio")
    async def test_natural_1_single_d20(self, agent) -> None:
        """Natural 1 on a single d20 returns a critical failure message."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Aria",
                "notation": "1d20",
                "result": {"total": 1, "rolls": [1]},
                "skill": None,
            }
        )
        assert "natural 1" in result.lower() or "critical failure" in result.lower()
        assert "1" in result

    @pytest.mark.anyio("asyncio")
    async def test_high_d20_roll(self, agent) -> None:
        """Roll of 18 on d20 returns a solid/outstanding result."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Brom",
                "notation": "1d20+3",
                "result": {"total": 21, "rolls": [18]},
                "skill": "athletics",
            }
        )
        assert "Brom" in result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.anyio("asyncio")
    async def test_low_d20_roll(self, agent) -> None:
        """Roll of 3 on d20 returns a poor showing message."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Calix",
                "notation": "1d20",
                "result": {"total": 3, "rolls": [3]},
                "skill": "stealth",
            }
        )
        assert "Calix" in result
        assert "poor" in result.lower() or "3" in result

    @pytest.mark.anyio("asyncio")
    async def test_non_d20_roll(self, agent) -> None:
        """Non-d20 roll returns a simple notation/total message."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Dara",
                "notation": "2d6+3",
                "result": {"total": 10, "rolls": [4, 3]},
                "skill": None,
            }
        )
        assert "Dara" in result
        assert "2d6+3" in result
        assert "10" in result

    @pytest.mark.anyio("asyncio")
    async def test_skill_text_included(self, agent) -> None:
        """Skill name is formatted and included in the narration."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Elan",
                "notation": "1d20+5",
                "result": {"total": 15, "rolls": [10]},
                "skill": "sleight_of_hand",
            }
        )
        assert "sleight of hand" in result.lower()

    @pytest.mark.anyio("asyncio")
    async def test_missing_rolls_key(self, agent) -> None:
        """If result contains no rolls list, still returns a valid string."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Faro",
                "notation": "1d20",
                "result": {"total": 12},
                "skill": None,
            }
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# narrate_dice_roll – Azure mode (mocked)
# ---------------------------------------------------------------------------


class TestNarrateDiceRollAzure:
    """Test narrate_dice_roll when Azure OpenAI is available."""

    @pytest.fixture
    def agent(self):
        """Provide a DM agent instance with a mocked Azure client."""
        ag = _make_dm_agent(fallback=False)
        mock_azure = MagicMock()
        mock_azure.chat_completion = AsyncMock(
            return_value="The fates smile upon Aria as the die comes to rest."
        )
        ag.azure_client = mock_azure
        return ag

    @pytest.mark.anyio("asyncio")
    async def test_azure_narration_returned(self, agent) -> None:
        """Azure narration is returned when the client succeeds."""
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Aria",
                "notation": "1d20",
                "result": {"total": 15, "rolls": [15]},
                "skill": None,
            }
        )
        assert result == "The fates smile upon Aria as the die comes to rest."

    @pytest.mark.anyio("asyncio")
    async def test_azure_critical_hit_prompt_includes_special(
        self, agent
    ) -> None:
        """A natural 20 triggers the CRITICAL SUCCESS note in the Azure prompt."""
        await agent.narrate_dice_roll(
            {
                "player_name": "Brom",
                "notation": "1d20",
                "result": {"total": 20, "rolls": [20]},
                "skill": "athletics",
            }
        )
        call_args = agent.azure_client.chat_completion.call_args
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "CRITICAL SUCCESS" in user_message["content"]

    @pytest.mark.anyio("asyncio")
    async def test_azure_fallback_on_exception(self, agent) -> None:
        """Falls back to rule-based narration when Azure raises an exception."""
        agent.azure_client.chat_completion = AsyncMock(
            side_effect=RuntimeError("Azure unavailable")
        )
        result = await agent.narrate_dice_roll(
            {
                "player_name": "Calix",
                "notation": "1d20",
                "result": {"total": 20, "rolls": [20]},
                "skill": None,
            }
        )
        # Should still get a meaningful string from the fallback
        assert "critical success" in result.lower() or "20" in result


# ---------------------------------------------------------------------------
# handle_dice_roll – DM narration wire-up
# ---------------------------------------------------------------------------


class TestHandleDiceRollNarration:
    """Test that handle_dice_roll triggers DM narration and sends dm_narration."""

    @pytest.mark.anyio("asyncio")
    async def test_dm_narration_sent_after_dice_result(self) -> None:
        """After a dice roll, a dm_narration message is sent to the campaign."""
        sent_messages: list[str] = []

        mock_ws = MagicMock()

        mock_manager = MagicMock()
        mock_manager.send_campaign_message = AsyncMock(
            side_effect=lambda msg, _cid: sent_messages.append(msg)
        )
        mock_manager.send_personal_message = AsyncMock()

        mock_dm_agent = MagicMock()
        mock_dm_agent.narrate_dice_roll = AsyncMock(
            return_value="The die lands with a satisfying clatter."
        )

        mock_rules = MagicMock()
        mock_rules.roll_dice.return_value = {
            "total": 15,
            "rolls": [15],
            "modifier": 0,
            "notation": "1d20",
            "timestamp": "2024-01-01T00:00:00",
        }

        with (
            patch("app.api.websocket_routes.manager", mock_manager),
            patch(
                "app.agents.dungeon_master_agent.get_dungeon_master",
                return_value=mock_dm_agent,
            ),
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin",
                return_value=mock_rules,
            ),
        ):
            from app.api.websocket_routes import handle_dice_roll

            await handle_dice_roll(
                {
                    "type": "dice_roll",
                    "notation": "1d20",
                    "player_name": "Aria",
                },
                mock_ws,
                campaign_id="campaign-123",
            )

        assert len(sent_messages) == 2
        types = [json.loads(m)["type"] for m in sent_messages]
        assert "dice_result" in types
        assert "dm_narration" in types

        narration_msg = next(
            json.loads(m)
            for m in sent_messages
            if json.loads(m)["type"] == "dm_narration"
        )
        assert narration_msg["narration"] == "The die lands with a satisfying clatter."
        assert narration_msg["roll_context"]["notation"] == "1d20"

    @pytest.mark.anyio("asyncio")
    async def test_dm_narration_error_does_not_break_dice_result(self) -> None:
        """dice_result is still delivered even when DM narration raises."""
        sent_messages: list[str] = []

        mock_ws = MagicMock()
        mock_manager = MagicMock()
        mock_manager.send_campaign_message = AsyncMock(
            side_effect=lambda msg, _cid: sent_messages.append(msg)
        )

        mock_dm_agent = MagicMock()
        mock_dm_agent.narrate_dice_roll = AsyncMock(
            side_effect=RuntimeError("DM agent exploded")
        )

        mock_rules = MagicMock()
        mock_rules.roll_dice.return_value = {
            "total": 7,
            "rolls": [7],
            "modifier": 0,
            "notation": "1d20",
            "timestamp": "2024-01-01T00:00:00",
        }

        with (
            patch("app.api.websocket_routes.manager", mock_manager),
            patch(
                "app.agents.dungeon_master_agent.get_dungeon_master",
                return_value=mock_dm_agent,
            ),
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin",
                return_value=mock_rules,
            ),
        ):
            from app.api.websocket_routes import handle_dice_roll

            # Should not raise
            await handle_dice_roll(
                {
                    "type": "dice_roll",
                    "notation": "1d20",
                    "player_name": "Brom",
                },
                mock_ws,
                campaign_id="campaign-123",
            )

        # Only the dice_result should have been sent; narration errored silently
        assert len(sent_messages) == 1
        msg = json.loads(sent_messages[0])
        assert msg["type"] == "dice_result"
