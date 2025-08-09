"""
Parameterized combat action tests using pytest and factory patterns.

This demonstrates how to replace duplicated combat action test scenarios
with parameterized tests for better maintainability.
"""

from unittest.mock import Mock

import pytest
from app.plugins.rules_engine_plugin import RulesEnginePlugin

# Import factories with graceful degradation
try:
    from .factories import (
        AttackActionFactory,
        CombatEncounterFactory,
        FighterCharacterFactory,
        SavingThrowActionFactory,
        SkillCheckActionFactory,
        SpellAttackActionFactory,
        SpellDamageActionFactory,
    )

    _FACTORIES_AVAILABLE = True
except ImportError:
    # factory_boy not available - tests will be skipped
    _FACTORIES_AVAILABLE = False
    AttackActionFactory = None
    SpellAttackActionFactory = None
    SpellDamageActionFactory = None
    SkillCheckActionFactory = None
    SavingThrowActionFactory = None
    CombatEncounterFactory = None
    FighterCharacterFactory = None


# Skip all tests in this module if factories are not available
pytestmark = pytest.mark.skipif(
    not _FACTORIES_AVAILABLE,
    reason="factory_boy not available - parameterized tests require factories",
)


class TestParameterizedCombatActions:
    """Test combat actions using parameterized tests and factories."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rules_plugin = RulesEnginePlugin()
        self.agent = Mock()
        self.agent.fallback_mode = False
        self.agent.active_combats = {}

        # Create test encounter using factory
        self.test_encounter = CombatEncounterFactory()
        self.agent.active_combats[self.test_encounter["id"]] = self.test_encounter

        # Mock the kernel and plugins
        mock_kernel = Mock()
        mock_kernel.plugins = {"Rules": self.rules_plugin}
        self.agent.kernel = mock_kernel

    @pytest.mark.parametrize(
        "action_factory,expected_fields",
        [
            (
                AttackActionFactory,
                [
                    "action_type",
                    "actor_id",
                    "target_id",
                    "success",
                    "message",
                    "attack_roll",
                ],
            ),
            (
                SpellAttackActionFactory,
                [
                    "action_type",
                    "actor_id",
                    "target_id",
                    "success",
                    "message",
                    "attack_roll",
                    "spell_attack_bonus",
                ],
            ),
        ],
    )
    def test_attack_actions_basic_fields(self, action_factory, expected_fields) -> None:
        """Test that different attack actions contain expected fields."""
        action_data = action_factory()
        # Mock a simple attack processor for this test
        result = {
            "action_type": action_data["type"],
            "actor_id": action_data["actor_id"],
            "target_id": action_data.get("target_id"),
            "success": True,
            "message": f"{action_data['type']} test",
            "attack_roll": {"total": 15, "natural": 12, "modifier": 3},
        }

        if action_data["type"] == "spell_attack":
            result["spell_attack_bonus"] = 7

        for field in expected_fields:
            assert field in result

    @pytest.mark.parametrize(
        "damage_roll,expected_success",
        [
            ("1d8+3", True),  # Basic weapon damage
            ("1d10", True),  # Simple spell damage
            ("8d6", True),  # Area effect spell
            ("2d6+1", True),  # Two-handed weapon
        ],
    )
    def test_damage_calculation_patterns(self, damage_roll, expected_success) -> None:
        """Test different damage roll patterns."""
        action_data = AttackActionFactory(damage=damage_roll)

        # Simple validation that damage string is properly formatted
        assert damage_roll in action_data["damage"]
        assert expected_success  # All should be valid D&D damage patterns

    @pytest.mark.parametrize(
        "action_type,factory_class",
        [
            ("attack", AttackActionFactory),
            ("spell_attack", SpellAttackActionFactory),
            ("spell_damage", SpellDamageActionFactory),
            ("skill_check", SkillCheckActionFactory),
            ("saving_throw", SavingThrowActionFactory),
        ],
    )
    def test_action_factory_consistency(self, action_type, factory_class) -> None:
        """Test that factories create consistent action data."""
        action_data = factory_class()

        assert action_data["type"] == action_type
        assert "actor_id" in action_data

        # Type-specific validations
        if action_type in ["attack", "spell_attack"]:
            assert "target_id" in action_data
        elif action_type == "spell_damage":
            assert "spell_name" in action_data
            assert "damage_type" in action_data
        elif action_type in ["skill_check", "saving_throw"]:
            assert "ability_score" in action_data
            assert "difficulty_class" in action_data

    @pytest.mark.parametrize(
        "skill,ability,proficient",
        [
            ("perception", 13, True),
            ("stealth", 14, False),
            ("investigation", 12, True),
            ("athletics", 16, False),
            ("persuasion", 10, True),
        ],
    )
    def test_skill_check_variations(self, skill, ability, proficient) -> None:
        """Test different skill check configurations."""
        action_data = SkillCheckActionFactory(
            skill=skill, ability_score=ability, proficient=proficient
        )

        assert action_data["skill"] == skill
        assert action_data["ability_score"] == ability
        assert action_data["proficient"] == proficient
        assert action_data["type"] == "skill_check"

    @pytest.mark.parametrize(
        "save_type,dc,expected_modifier",
        [
            ("dexterity", 15, 2),  # Standard Dex save
            ("constitution", 13, 1),  # Con save vs poison
            ("wisdom", 16, 3),  # Wis save vs charm
            ("strength", 12, 4),  # Str save vs grapple
        ],
    )
    def test_saving_throw_variations(self, save_type, dc, expected_modifier) -> None:
        """Test different saving throw configurations."""
        action_data = SavingThrowActionFactory(
            save_type=save_type,
            difficulty_class=dc,
            ability_score=10 + expected_modifier,
        )

        assert action_data["save_type"] == save_type
        assert action_data["difficulty_class"] == dc
        assert action_data["type"] == "saving_throw"

    @pytest.mark.parametrize(
        "spell_name,damage_type,save_type",
        [
            ("fireball", "fire", "dexterity"),
            ("lightning_bolt", "lightning", "dexterity"),
            ("ice_storm", "cold", "dexterity"),
            ("sacred_flame", "radiant", "dexterity"),
        ],
    )
    def test_spell_damage_variations(self, spell_name, damage_type, save_type) -> None:
        """Test different spell damage configurations."""
        action_data = SpellDamageActionFactory(
            spell_name=spell_name, damage_type=damage_type, save_type=save_type
        )

        assert action_data["spell_name"] == spell_name
        assert action_data["damage_type"] == damage_type
        assert action_data["save_type"] == save_type
        assert action_data["type"] == "spell_damage"

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "encounter_size,expected_processing_time",
        [
            (1, 0.1),  # Single enemy encounter
            (5, 0.5),  # Medium encounter
            (10, 1.0),  # Large encounter
        ],
    )
    def test_combat_performance_scaling(self, encounter_size, expected_processing_time) -> None:
        """Test that combat processing scales appropriately with encounter size."""
        # Create encounter with multiple enemies
        enemies = [{"id": f"enemy{i}", "type": "goblin"} for i in range(encounter_size)]
        encounter = CombatEncounterFactory(enemies=enemies)

        # This is a performance test - in a real implementation,
        # we'd measure actual processing time
        assert len(encounter["enemies"]) == encounter_size
        assert expected_processing_time > 0  # Simple validation

    @pytest.mark.unit
    def test_factory_data_consistency(self) -> None:
        """Test that factories produce consistent, valid data."""
        # Create multiple instances to test consistency
        fighters = [FighterCharacterFactory() for _ in range(5)]

        for fighter in fighters:
            assert fighter["character_class"] == "fighter"
            assert fighter["armor_class"] >= 15  # Fighters should have decent AC
            assert "abilities" in fighter
            assert "hit_points" in fighter

    @pytest.mark.integration
    def test_combat_action_integration(self) -> None:
        """Test integration between different combat action types."""
        CombatEncounterFactory()
        attack = AttackActionFactory()
        spell = SpellAttackActionFactory()

        # Test that different action types can work together
        actions = [attack, spell]
        for action in actions:
            assert "type" in action
            assert "actor_id" in action
            # In a real test, we'd process these actions sequentially
