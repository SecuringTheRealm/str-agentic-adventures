"""
Tests for game engine wiring (issue #416).

Covers:
- Game context flows through the /input endpoint (build_game_context integration)
- Campaign ID is set on conversation threads
- Combat resolution uses character equipment from game context
- State updates include character HP, conditions, and weapon info
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from app.database import Base
from app.models.db_models import ConversationThread
from app.rules_engine import get_weapon_stats
from app.services.game_context_service import (
    build_game_context,
    build_state_updates,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# In-memory DB fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def fighter_character_data() -> dict:
    """Character data dict representing a level-3 Fighter with a longsword."""
    return {
        "id": "char-fighter-1",
        "name": "Thorn Ironforge",
        "race": "human",
        "character_class": "fighter",
        "level": 3,
        "experience": 1000,
        "abilities": {
            "strength": 16,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 8,
        },
        "hit_points": {"current": 28, "maximum": 31},
        "armor_class": 16,
        "proficiency_bonus": 2,
        "conditions": [],
        "structured_inventory": {
            "items": [
                {
                    "id": "item-longsword",
                    "name": "Longsword",
                    "item_type": "weapon",
                    "weight": 3.0,
                    "quantity": 1,
                    "equipped": True,
                },
                {
                    "id": "item-chain-mail",
                    "name": "Chain Mail",
                    "item_type": "armor",
                    "weight": 55.0,
                    "quantity": 1,
                    "equipped": True,
                },
                {
                    "id": "item-shield",
                    "name": "Shield",
                    "item_type": "shield",
                    "weight": 6.0,
                    "quantity": 1,
                    "equipped": True,
                },
            ],
            "equipment": {
                "main_hand": "item-longsword",
                "off_hand": "item-shield",
                "armor": "item-chain-mail",
            },
            "gold": 15,
        },
    }


# ---------------------------------------------------------------------------
# Step 1: Game context flows through the /input endpoint
# ---------------------------------------------------------------------------


class TestBuildGameContext:
    """Tests for build_game_context producing a rich context dict."""

    def test_context_includes_combat_stats_from_character(
        self, db_session, fighter_character_data
    ):
        """build_game_context returns combat-relevant values from character data."""
        # Pre-load character dict (simulating Scribe fetch)
        context = build_game_context(
            character_id="char-fighter-1",
            campaign_id="campaign-1",
            character_data=fighter_character_data,
        )

        assert context["character_id"] == "char-fighter-1"
        assert context["campaign_id"] == "campaign-1"
        assert context["character_name"] == "Thorn Ironforge"
        assert context["character_class"] == "fighter"
        assert context["character_level"] == "3"

        # Combat values
        assert context["current_hp"] == 28
        assert context["max_hp"] == 31
        assert context["proficiency_bonus"] == 2

        # Equipped weapon derived from structured_inventory
        assert context["equipped_weapon_name"] == "Longsword"
        assert context["equipped_weapon_damage"] == "1d8"  # SRD longsword
        assert "versatile" in context["equipped_weapon_properties"]

        # Attack bonus = ability mod + proficiency
        # STR 16 -> mod +3, proficiency +2 -> total +5
        assert context["attack_bonus"] == 5
        assert context["damage_modifier"] == 3  # STR modifier

    def test_context_computes_ac_from_equipment(self, fighter_character_data):
        """AC is calculated from equipped armor and shield."""
        context = build_game_context(
            character_id="char-fighter-1",
            campaign_id="campaign-1",
            character_data=fighter_character_data,
        )
        # Chain mail = 16 AC (no DEX), + 2 shield = 18
        assert context["armor_class"] == 18

    def test_context_fallback_for_missing_character(self):
        """When character data is sparse, context has safe defaults."""
        minimal_char = {
            "id": "char-unknown",
            "name": "Mystery",
            "class": "Wizard",
            "level": 1,
        }
        context = build_game_context(
            character_id="char-unknown",
            campaign_id="campaign-1",
            character_data=minimal_char,
        )
        # Should not crash; provides defaults
        assert context["character_id"] == "char-unknown"
        assert context["character_level"] == "1"
        assert context["attack_bonus"] == 2  # 0 mod + 2 proficiency

    def test_context_finesse_weapon_uses_higher_mod(self):
        """A finesse weapon should use the higher of STR/DEX modifiers."""
        char = {
            "id": "char-rogue",
            "name": "Shadow",
            "character_class": "rogue",
            "level": 5,
            "abilities": {
                "strength": 10,
                "dexterity": 18,
                "constitution": 12,
                "intelligence": 14,
                "wisdom": 10,
                "charisma": 8,
            },
            "hit_points": {"current": 33, "maximum": 33},
            "structured_inventory": {
                "items": [
                    {
                        "id": "item-rapier",
                        "name": "Rapier",
                        "item_type": "weapon",
                        "equipped": True,
                    }
                ],
                "equipment": {"main_hand": "item-rapier"},
            },
        }
        context = build_game_context(
            character_id="char-rogue",
            campaign_id="campaign-1",
            character_data=char,
        )
        # Rapier is finesse; DEX 18 -> +4 mod, proficiency at L5 = +3
        assert context["attack_bonus"] == 7
        assert context["damage_modifier"] == 4


# ---------------------------------------------------------------------------
# Step 2: Campaign ID is set on conversation threads
# ---------------------------------------------------------------------------


class TestConversationThreadCampaignId:
    """Tests that campaign_id is wired into ConversationThread records."""

    def test_new_thread_gets_campaign_id(self, db_session):
        """When a new thread is created it should have the campaign_id set."""
        from app.agents.dungeon_master_agent import DungeonMasterAgent

        # Patch get_session_context to use our in-memory DB
        def _ctx():
            from contextlib import contextmanager

            @contextmanager
            def _session():
                try:
                    yield db_session
                    db_session.flush()
                except Exception:
                    db_session.rollback()
                    raise

            return _session()

        with patch("app.agents.dungeon_master_agent.get_session_context", _ctx):
            dm = DungeonMasterAgent.__new__(DungeonMasterAgent)
            dm._threads = {}
            dm._fallback_mode = True

            dm._get_or_create_thread("session-123", campaign_id="campaign-abc")

            # Verify the DB record
            row = (
                db_session.query(ConversationThread)
                .filter(ConversationThread.session_id == "session-123")
                .first()
            )
            assert row is not None
            assert row.campaign_id == "campaign-abc"
            assert row.agent_name == "DM"

    def test_existing_thread_updated_with_campaign_id(self, db_session):
        """If a thread exists without campaign_id, it gets back-filled."""
        # Pre-create a thread without campaign_id
        thread = ConversationThread(
            id=str(uuid.uuid4()),
            session_id="session-456",
            agent_name="DM",
            messages=[],
            campaign_id=None,
        )
        db_session.add(thread)
        db_session.commit()

        from app.agents.dungeon_master_agent import DungeonMasterAgent

        def _ctx():
            from contextlib import contextmanager

            @contextmanager
            def _session():
                try:
                    yield db_session
                    db_session.flush()
                except Exception:
                    db_session.rollback()
                    raise

            return _session()

        with patch("app.agents.dungeon_master_agent.get_session_context", _ctx):
            dm = DungeonMasterAgent.__new__(DungeonMasterAgent)
            dm._threads = {}
            dm._fallback_mode = True

            dm._get_or_create_thread("session-456", campaign_id="campaign-xyz")

            db_session.refresh(thread)
            assert thread.campaign_id == "campaign-xyz"


# ---------------------------------------------------------------------------
# Step 4: Combat resolution uses character equipment
# ---------------------------------------------------------------------------


class TestCombatUsesEquipment:
    """Tests that combat orchestration passes equipment stats."""

    def test_orchestration_passes_weapon_stats(self):
        """_call_combat_mc should include weapon and attack data from state."""
        from app.agents.orchestration import _call_combat_mc

        state = {
            "character_id": "char-1",
            "attack_bonus": 5,
            "equipped_weapon_damage": "1d8",
            "damage_modifier": 3,
            "equipped_weapon_name": "Longsword",
            "equipped_weapon_properties": ["versatile"],
            "proficiency_bonus": 2,
        }

        # Mock the combat MC agent to capture what action_data it receives
        mock_combat_mc = MagicMock()
        captured = {}

        async def _capture_action(encounter_id, action_data):
            captured.update(action_data)
            return {"success": True}

        mock_combat_mc.process_combat_action = _capture_action

        with patch(
            "app.agents.combat_mc_agent.get_combat_mc",
            return_value=mock_combat_mc,
        ):
            import asyncio

            result = asyncio.run(
                _call_combat_mc("I attack the goblin", state)
            )

        assert result is not None
        key, value = result
        assert key == "combat_update"

        # Verify equipment stats were forwarded
        assert captured["attack_bonus"] == 5
        assert captured["damage_dice"] == "1d8"
        assert captured["damage_modifier"] == 3
        assert captured["weapon_name"] == "Longsword"

    def test_fallback_combat_uses_damage_dice_key(self):
        """Fallback combat should accept damage_dice and damage_modifier."""
        from app.agents.combat_mc_agent import CombatMCAgent

        agent = CombatMCAgent.__new__(CombatMCAgent)
        agent._fallback_mode = True
        agent.rules_engine = None
        agent.active_combats = {}
        agent.fallback_mechanics = {
            "ability_modifiers": {},
            "base_proficiency_bonus": 2,
            "base_armor_class": 10,
            "base_hit_points": 8,
        }

        encounter = {
            "status": "active",
            "enemies": [],
            "round": 1,
            "turn_order": [],
        }

        action = {
            "type": "attack",
            "actor_id": "char-1",
            "target_id": "enemy_1",
            "attack_bonus": 5,
            "target_ac": 10,  # Easy hit
            "damage_dice": "1d8",
            "damage_modifier": 3,
        }

        # Seed random to get a reliable hit
        import random

        random.seed(42)
        result = agent._process_fallback_combat_action(encounter, action)

        # The result should use the damage_dice and modifier
        assert result["action_type"] == "attack"
        # Either hit or miss is fine, but no crash
        assert "message" in result


# ---------------------------------------------------------------------------
# Step 5: State updates enrichment
# ---------------------------------------------------------------------------


class TestBuildStateUpdates:
    """Tests for build_state_updates enriching the response with game state."""

    def test_includes_character_state(self):
        """State updates should contain character_state with HP and conditions."""
        context = {
            "current_hp": 28,
            "max_hp": 31,
            "armor_class": 18,
            "conditions": ["poisoned"],
            "character_level": "3",
            "equipped_weapon_name": "Longsword",
            "equipped_weapon_damage": "1d8",
            "attack_bonus": 5,
            "spell_slots": None,
        }
        dm_response = {
            "state_updates": {"last_action": "attack goblin"},
        }

        result = build_state_updates(context, dm_response)

        assert "character_state" in result
        char_state = result["character_state"]
        assert char_state["current_hp"] == 28
        assert char_state["max_hp"] == 31
        assert char_state["armor_class"] == 18
        assert char_state["conditions"] == ["poisoned"]
        assert char_state["level"] == 3

    def test_includes_equipped_weapon(self):
        """State updates should include the equipped weapon details."""
        context = {
            "current_hp": 20,
            "max_hp": 20,
            "armor_class": 14,
            "conditions": [],
            "character_level": "1",
            "equipped_weapon_name": "Shortsword",
            "equipped_weapon_damage": "1d6",
            "attack_bonus": 5,
            "spell_slots": None,
        }
        dm_response = {"state_updates": {}}

        result = build_state_updates(context, dm_response)

        assert "equipped_weapon" in result
        assert result["equipped_weapon"]["name"] == "Shortsword"
        assert result["equipped_weapon"]["damage_dice"] == "1d6"
        assert result["equipped_weapon"]["attack_bonus"] == 5

    def test_includes_spell_slots_when_present(self):
        """State updates should include spell slots for spellcasters."""
        context = {
            "current_hp": 15,
            "max_hp": 15,
            "armor_class": 12,
            "conditions": [],
            "character_level": "3",
            "equipped_weapon_name": "",
            "spell_slots": [{"level": 1, "total": 4, "used": 1}],
        }
        dm_response = {"state_updates": {}}

        result = build_state_updates(context, dm_response)

        assert "spell_slots" in result
        assert result["spell_slots"][0]["level"] == 1

    def test_preserves_dm_state_updates(self):
        """DM-provided state updates should be preserved in the output."""
        context = {
            "current_hp": 20,
            "max_hp": 20,
            "armor_class": 10,
            "conditions": [],
            "character_level": "1",
            "equipped_weapon_name": "",
            "spell_slots": None,
        }
        dm_response = {
            "state_updates": {"xp_gained": 50, "last_action": "explored cave"},
        }

        result = build_state_updates(context, dm_response)

        assert result["xp_gained"] == 50
        assert result["last_action"] == "explored cave"
        # Character state is still included
        assert "character_state" in result


# ---------------------------------------------------------------------------
# Step 3: Rules engine integration with weapon stats
# ---------------------------------------------------------------------------


class TestRulesEngineWeaponIntegration:
    """Tests that the rules engine weapon lookup works for combat."""

    def test_get_weapon_stats_longsword(self):
        """get_weapon_stats should return correct stats for a longsword."""
        stats = get_weapon_stats("longsword")
        assert stats["damage_dice"] == "1d8"
        assert stats["damage_type"] == "slashing"
        assert "versatile" in stats["properties"]

    def test_get_weapon_stats_rapier(self):
        """get_weapon_stats should return finesse property for rapier."""
        stats = get_weapon_stats("rapier")
        assert stats["damage_dice"] == "1d8"
        assert "finesse" in stats["properties"]

    def test_get_weapon_stats_unknown_falls_back(self):
        """Unknown weapons should get a safe default."""
        stats = get_weapon_stats("enchanted moonblade")
        assert stats["damage_dice"] == "1d4"
        assert stats["damage_type"] == "bludgeoning"

    def test_get_weapon_stats_shortbow_is_ranged(self):
        """Ranged weapons should have ammunition property."""
        stats = get_weapon_stats("shortbow")
        assert "ammunition" in stats["properties"]
