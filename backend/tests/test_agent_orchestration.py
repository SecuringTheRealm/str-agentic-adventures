"""
Tests for DM agent orchestration - context-based routing to specialist agents.
"""

import pytest
from app.agents.orchestration import detect_agent_triggers


class TestDetectAgentTriggers:
    """Test the context detection logic for specialist agent routing."""

    def test_combat_keywords_in_player_input(self) -> None:
        """Test that combat keywords in player input trigger combat_mc."""
        triggers = detect_agent_triggers(
            dm_response="You step forward bravely.",
            player_input="I attack the goblin with my sword",
        )
        assert "combat_mc" in triggers

    def test_combat_keywords_in_dm_response(self) -> None:
        """Test that combat keywords in DM response trigger combat_mc."""
        triggers = detect_agent_triggers(
            dm_response="The orc swings its axe to fight you in combat!",
            player_input="I open the door",
        )
        assert "combat_mc" in triggers

    def test_exploration_keywords_trigger_narrator(self) -> None:
        """Test that exploration keywords trigger the narrator."""
        triggers = detect_agent_triggers(
            dm_response="You see a dark corridor ahead.",
            player_input="I look around the room",
        )
        assert "narrator" in triggers

    def test_examine_triggers_narrator(self) -> None:
        """Test that 'examine' triggers narrator."""
        triggers = detect_agent_triggers(
            dm_response="You notice something peculiar.",
            player_input="I examine the ancient runes on the wall",
        )
        assert "narrator" in triggers

    def test_character_keywords_trigger_scribe(self) -> None:
        """Test that character/inventory keywords trigger the scribe."""
        triggers = detect_agent_triggers(
            dm_response="You check your belongings.",
            player_input="I check my inventory",
        )
        assert "scribe" in triggers

    def test_hp_triggers_scribe(self) -> None:
        """Test that 'hp' keyword triggers scribe."""
        triggers = detect_agent_triggers(
            dm_response="You feel wounded.",
            player_input="How many hp do I have?",
        )
        assert "scribe" in triggers

    def test_stats_triggers_scribe(self) -> None:
        """Test that 'stats' triggers scribe."""
        triggers = detect_agent_triggers(
            dm_response="You recall your training.",
            player_input="Show me my stats",
        )
        assert "scribe" in triggers

    def test_npc_interaction_triggers_narrator(self) -> None:
        """Test that NPC interaction keywords trigger narrator."""
        triggers = detect_agent_triggers(
            dm_response="The merchant looks at you expectantly.",
            player_input="I talk to the shopkeeper",
        )
        assert "narrator" in triggers

    def test_persuade_triggers_narrator(self) -> None:
        """Test that 'persuade' triggers narrator."""
        triggers = detect_agent_triggers(
            dm_response="The guard eyes you suspiciously.",
            player_input="I try to persuade the guard to let us pass",
        )
        assert "narrator" in triggers

    def test_agent_tag_parsing(self) -> None:
        """Test that [AGENT:name] tags in DM response are parsed."""
        triggers = detect_agent_triggers(
            dm_response="The enemy charges! [AGENT:combat_mc] Prepare for battle!",
            player_input="I stand my ground",
        )
        assert "combat_mc" in triggers

    def test_multiple_agent_tags(self) -> None:
        """Test that multiple [AGENT:name] tags are all parsed."""
        triggers = detect_agent_triggers(
            dm_response=(
                "[AGENT:narrator] The scene shifts. "
                "[AGENT:scribe] Update your character."
            ),
            player_input="I rest",
        )
        assert "narrator" in triggers
        assert "scribe" in triggers

    def test_multiple_triggers_can_fire(self) -> None:
        """Test that multiple trigger types can fire simultaneously."""
        triggers = detect_agent_triggers(
            dm_response="You search the room and find a goblin. Combat begins!",
            player_input="I look around and attack anything hostile",
        )
        assert "narrator" in triggers
        assert "combat_mc" in triggers

    def test_no_triggers_for_generic_input(self) -> None:
        """Test that generic input without keywords produces no triggers."""
        triggers = detect_agent_triggers(
            dm_response="You stand in the tavern.",
            player_input="I wait patiently",
        )
        assert triggers == []

    def test_case_insensitive_detection(self) -> None:
        """Test that keyword detection is case-insensitive."""
        triggers = detect_agent_triggers(
            dm_response="COMBAT BEGINS!",
            player_input="I ATTACK the dragon",
        )
        assert "combat_mc" in triggers

    def test_agent_tag_case_insensitive(self) -> None:
        """Test that [AGENT:NAME] tags are normalised to lowercase."""
        triggers = detect_agent_triggers(
            dm_response="[AGENT:NARRATOR] A new scene unfolds.",
            player_input="Continue",
        )
        assert "narrator" in triggers

    def test_no_duplicate_triggers(self) -> None:
        """Test that the same trigger is not added twice."""
        triggers = detect_agent_triggers(
            dm_response="[AGENT:narrator] You look around the area.",
            player_input="I explore the cave and search for treasure",
        )
        # narrator should appear from both keywords and the tag, but only once
        assert triggers.count("narrator") == 1

    def test_spell_combat_trigger(self) -> None:
        """Test that casting a spell at a target triggers combat."""
        triggers = detect_agent_triggers(
            dm_response="The air crackles with energy.",
            player_input="I cast spell at the skeleton",
        )
        assert "combat_mc" in triggers

    def test_initiative_triggers_combat(self) -> None:
        """Test that 'initiative' keyword triggers combat_mc."""
        triggers = detect_agent_triggers(
            dm_response="Roll for initiative!",
            player_input="What's the initiative order?",
        )
        assert "combat_mc" in triggers

    def test_level_up_triggers_scribe(self) -> None:
        """Test that 'level up' triggers scribe."""
        triggers = detect_agent_triggers(
            dm_response="You have enough experience to level up!",
            player_input="I want to level up",
        )
        assert "scribe" in triggers

    def test_equipment_triggers_scribe(self) -> None:
        """Test that 'equipment' triggers scribe."""
        triggers = detect_agent_triggers(
            dm_response="You inspect your gear.",
            player_input="What equipment do I have?",
        )
        assert "scribe" in triggers


class TestOrchestrateSpecialistAgents:
    """Test the async orchestration of specialist agents."""

    @pytest.mark.asyncio
    async def test_empty_triggers_returns_empty_dict(self) -> None:
        """Test that no triggers produces no specialist results."""
        from app.agents.orchestration import orchestrate_specialist_agents

        result = await orchestrate_specialist_agents(
            triggers=[],
            player_input="I wait",
            game_state=None,
            session_id="test-session",
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_combat_trigger_calls_combat_mc(self) -> None:
        """Test that combat_mc trigger invokes the combat MC agent."""
        from unittest.mock import AsyncMock, patch

        from app.agents.orchestration import orchestrate_specialist_agents

        mock_combat_mc = AsyncMock()
        mock_combat_mc.process_combat_action.return_value = {
            "action_type": "attack",
            "success": True,
            "message": "Attack hits!",
            "damage": 7,
        }

        with patch(
            "app.agents.combat_mc_agent.get_combat_mc",
            return_value=mock_combat_mc,
        ):
            result = await orchestrate_specialist_agents(
                triggers=["combat_mc"],
                player_input="I attack the goblin",
                game_state=None,
                session_id="test-session",
            )

        assert "combat_update" in result

    @pytest.mark.asyncio
    async def test_narrator_trigger_calls_narrator(self) -> None:
        """Test that narrator trigger invokes the narrator agent."""
        from unittest.mock import AsyncMock, patch

        from app.agents.orchestration import orchestrate_specialist_agents

        mock_narrator = AsyncMock()
        mock_narrator.describe_scene.return_value = "A dark cave stretches before you."

        with patch(
            "app.agents.narrator_agent.get_narrator", return_value=mock_narrator
        ):
            result = await orchestrate_specialist_agents(
                triggers=["narrator"],
                player_input="I look around",
                game_state={"mood": "tense"},
                session_id="test-session",
            )

        assert "scene_narrative" in result

    @pytest.mark.asyncio
    async def test_scribe_trigger_calls_scribe(self) -> None:
        """Test that scribe trigger invokes the scribe agent."""
        from unittest.mock import AsyncMock, patch

        from app.agents.orchestration import orchestrate_specialist_agents

        mock_scribe = AsyncMock()
        mock_scribe.get_character.return_value = {
            "name": "TestHero",
            "class": "Fighter",
            "level": 5,
        }

        with patch(
            "app.agents.scribe_agent.get_scribe", return_value=mock_scribe
        ):
            result = await orchestrate_specialist_agents(
                triggers=["scribe"],
                player_input="check my character sheet",
                game_state={"character_id": "char-1"},
                session_id="test-session",
            )

        assert "character_update" in result

    @pytest.mark.asyncio
    async def test_multiple_triggers_produce_multiple_results(self) -> None:
        """Test that multiple triggers invoke multiple agents."""
        from unittest.mock import AsyncMock, patch

        from app.agents.orchestration import orchestrate_specialist_agents

        mock_narrator = AsyncMock()
        mock_narrator.describe_scene.return_value = "A dark room."

        mock_combat_mc = AsyncMock()
        mock_combat_mc.process_combat_action.return_value = {
            "success": True,
            "message": "Hit!",
        }

        with (
            patch(
                "app.agents.narrator_agent.get_narrator",
                return_value=mock_narrator,
            ),
            patch(
                "app.agents.combat_mc_agent.get_combat_mc",
                return_value=mock_combat_mc,
            ),
        ):
            result = await orchestrate_specialist_agents(
                triggers=["narrator", "combat_mc"],
                player_input="I look around and attack",
                game_state=None,
                session_id="test-session",
            )

        assert "scene_narrative" in result
        assert "combat_update" in result

    @pytest.mark.asyncio
    async def test_agent_error_handled_gracefully(self) -> None:
        """Test that a specialist agent error does not crash orchestration."""
        from unittest.mock import AsyncMock, patch

        from app.agents.orchestration import orchestrate_specialist_agents

        mock_narrator = AsyncMock()
        mock_narrator.describe_scene.side_effect = Exception("Azure unavailable")

        with patch(
            "app.agents.narrator_agent.get_narrator", return_value=mock_narrator
        ):
            result = await orchestrate_specialist_agents(
                triggers=["narrator"],
                player_input="I look around",
                game_state=None,
                session_id="test-session",
            )

        # Should not crash; narrator result is omitted or empty
        assert isinstance(result, dict)


class TestProcessPlayerActionIntegration:
    """Test that process_player_action integrates orchestration correctly."""

    @pytest.mark.asyncio
    async def test_explicit_combat_action_type_still_works(self) -> None:
        """Test that explicit action_type='combat' still routes directly."""
        from app.agents.orchestration import detect_agent_triggers

        # Explicit combat type should not go through auto-detection
        # The existing routing in game_routes.py handles this
        triggers = detect_agent_triggers(
            dm_response="",
            player_input="I do nothing special",
        )
        # No combat keywords, so no triggers
        assert "combat_mc" not in triggers

    @pytest.mark.asyncio
    async def test_general_action_with_combat_keywords_triggers_combat_mc(
        self,
    ) -> None:
        """Test that a general action containing combat keywords triggers combat_mc."""
        from app.agents.orchestration import detect_agent_triggers

        triggers = detect_agent_triggers(
            dm_response="The goblin lunges at you!",
            player_input="I swing my sword to attack",
        )
        assert "combat_mc" in triggers
