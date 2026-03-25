"""
Tests for the spell utilities module (concentration tracking and spell save DC).
"""

from unittest.mock import patch

import pytest
from app.utils.spells import (
    SPELLCASTING_ABILITY,
    ConcentrationState,
    break_concentration,
    calculate_spell_attack_modifier,
    calculate_spell_save_dc,
    check_concentration,
    start_concentration,
)


class TestConcentrationState:
    """Tests for the ConcentrationState model."""

    def test_default_state_has_no_active_spell(self) -> None:
        state = ConcentrationState()
        assert state.active_spell is None
        assert state.caster_id is None

    def test_state_with_active_spell(self) -> None:
        state = ConcentrationState(active_spell="Hold Person", caster_id="char1")
        assert state.active_spell == "Hold Person"
        assert state.caster_id == "char1"


class TestStartConcentration:
    """Tests for start_concentration."""

    def test_starts_concentration_on_new_spell(self) -> None:
        state = ConcentrationState()
        new_state = start_concentration(state, "Hold Person", "char1")
        assert new_state.active_spell == "Hold Person"
        assert new_state.caster_id == "char1"

    def test_starting_concentration_breaks_previous(self) -> None:
        state = ConcentrationState(active_spell="Blur", caster_id="char1")
        new_state = start_concentration(state, "Hold Person", "char1")
        assert new_state.active_spell == "Hold Person"
        assert new_state.caster_id == "char1"

    def test_original_state_is_not_mutated(self) -> None:
        state = ConcentrationState(active_spell="Blur", caster_id="char1")
        start_concentration(state, "Hold Person", "char1")
        # Original state should be unchanged
        assert state.active_spell == "Blur"


class TestBreakConcentration:
    """Tests for break_concentration."""

    def test_clears_active_spell(self) -> None:
        state = ConcentrationState(active_spell="Hold Person", caster_id="char1")
        new_state = break_concentration(state)
        assert new_state.active_spell is None

    def test_preserves_caster_id(self) -> None:
        state = ConcentrationState(active_spell="Hold Person", caster_id="char1")
        new_state = break_concentration(state)
        assert new_state.caster_id == "char1"

    def test_break_when_not_concentrating_is_safe(self) -> None:
        state = ConcentrationState()
        new_state = break_concentration(state)
        assert new_state.active_spell is None


class TestCheckConcentration:
    """Tests for check_concentration (CON saving throw)."""

    def test_dc_is_ten_for_low_damage(self) -> None:
        with patch("app.utils.spells.random.randint", return_value=15):
            result = check_concentration(constitution_modifier=0, damage_taken=5)
        assert result["dc"] == 10  # max(10, 5//2=2) => 10

    def test_dc_is_half_damage_for_high_damage(self) -> None:
        with patch("app.utils.spells.random.randint", return_value=15):
            result = check_concentration(constitution_modifier=0, damage_taken=30)
        assert result["dc"] == 15  # max(10, 30//2=15) => 15

    def test_dc_boundary_exactly_twenty(self) -> None:
        with patch("app.utils.spells.random.randint", return_value=20):
            result = check_concentration(constitution_modifier=0, damage_taken=20)
        assert result["dc"] == 10  # max(10, 20//2=10) => 10

    def test_dc_boundary_twenty_two(self) -> None:
        with patch("app.utils.spells.random.randint", return_value=20):
            result = check_concentration(constitution_modifier=0, damage_taken=22)
        assert result["dc"] == 11  # max(10, 22//2=11) => 11

    def test_maintained_when_total_meets_dc(self) -> None:
        # roll=10, modifier=0, total=10 vs dc=10 (damage=5) → maintained
        with patch("app.utils.spells.random.randint", return_value=10):
            result = check_concentration(constitution_modifier=0, damage_taken=5)
        assert result["maintained"] is True

    def test_lost_when_total_below_dc(self) -> None:
        # roll=5, modifier=0, total=5 vs dc=10 → lost
        with patch("app.utils.spells.random.randint", return_value=5):
            result = check_concentration(constitution_modifier=0, damage_taken=5)
        assert result["maintained"] is False

    def test_constitution_modifier_is_applied(self) -> None:
        # roll=7, modifier=3, total=10 vs dc=10 → maintained
        with patch("app.utils.spells.random.randint", return_value=7):
            result = check_concentration(constitution_modifier=3, damage_taken=5)
        assert result["maintained"] is True

    def test_result_contains_required_keys(self) -> None:
        result = check_concentration(constitution_modifier=2, damage_taken=10)
        assert "dc" in result
        assert "roll" in result
        assert "maintained" in result

    def test_roll_is_between_one_and_twenty(self) -> None:
        for _ in range(20):
            result = check_concentration(constitution_modifier=0, damage_taken=10)
            assert 1 <= result["roll"] <= 20


class TestCalculateSpellSaveDc:
    """Tests for calculate_spell_save_dc."""

    def test_standard_formula(self) -> None:
        assert calculate_spell_save_dc(
            proficiency_bonus=2, spellcasting_ability_modifier=3
        ) == 13

    def test_higher_level_caster(self) -> None:
        assert calculate_spell_save_dc(
            proficiency_bonus=3, spellcasting_ability_modifier=4
        ) == 15

    def test_minimum_values(self) -> None:
        assert calculate_spell_save_dc(
            proficiency_bonus=2, spellcasting_ability_modifier=0
        ) == 10

    def test_negative_modifier(self) -> None:
        # Unusual but theoretically possible
        assert calculate_spell_save_dc(
            proficiency_bonus=2, spellcasting_ability_modifier=-1
        ) == 9


class TestCalculateSpellAttackModifier:
    """Tests for calculate_spell_attack_modifier."""

    def test_standard_formula(self) -> None:
        assert calculate_spell_attack_modifier(
            proficiency_bonus=2, spellcasting_ability_modifier=3
        ) == 5

    def test_higher_level_caster(self) -> None:
        assert calculate_spell_attack_modifier(
            proficiency_bonus=6, spellcasting_ability_modifier=5
        ) == 11

    def test_zero_modifier(self) -> None:
        assert calculate_spell_attack_modifier(
            proficiency_bonus=2, spellcasting_ability_modifier=0
        ) == 2


class TestSpellcastingAbility:
    """Tests for the SPELLCASTING_ABILITY mapping."""

    @pytest.mark.parametrize("character_class,expected_ability", [
        ("wizard", "intelligence"),
        ("cleric", "wisdom"),
        ("druid", "wisdom"),
        ("bard", "charisma"),
        ("sorcerer", "charisma"),
        ("warlock", "charisma"),
        ("paladin", "charisma"),
        ("ranger", "wisdom"),
    ])
    def test_each_class_uses_correct_ability(
        self, character_class: str, expected_ability: str
    ) -> None:
        assert SPELLCASTING_ABILITY[character_class] == expected_ability

    def test_all_expected_classes_present(self) -> None:
        expected_classes = {
            "wizard", "cleric", "druid", "bard",
            "sorcerer", "warlock", "paladin", "ranger",
        }
        assert set(SPELLCASTING_ABILITY.keys()) == expected_classes
