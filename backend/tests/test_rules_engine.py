"""Tests for backend/app/rules_engine.py — attack resolution, damage calculation, HP tracking, death saves, initiative."""

from unittest.mock import patch

import pytest
from app.rules_engine import (
    apply_damage,
    apply_healing,
    calculate_damage,
    death_saving_throw,
    resolve_attack,
    roll_initiative,
)

# ---------------------------------------------------------------------------
# resolve_attack
# ---------------------------------------------------------------------------


class TestResolveAttackHitAndMiss:
    """Basic hit/miss logic based on roll + bonus vs AC."""

    def test_hits_when_total_equals_ac(self) -> None:
        # Roll 10, bonus 5 → total 15 vs AC 15 → hit
        with patch("app.rules_engine._roll_d20", return_value=10):
            result = resolve_attack(attack_bonus=5, target_ac=15)
        assert result["hit"] is True
        assert result["roll"] == 10
        assert result["total"] == 15

    def test_hits_when_total_exceeds_ac(self) -> None:
        with patch("app.rules_engine._roll_d20", return_value=15):
            result = resolve_attack(attack_bonus=3, target_ac=14)
        assert result["hit"] is True

    def test_misses_when_total_below_ac(self) -> None:
        # Roll 5, bonus 2 → total 7 vs AC 15 → miss
        with patch("app.rules_engine._roll_d20", return_value=5):
            result = resolve_attack(attack_bonus=2, target_ac=15)
        assert result["hit"] is False
        assert result["critical"] is False

    def test_result_contains_required_keys(self) -> None:
        with patch("app.rules_engine._roll_d20", return_value=10):
            result = resolve_attack(attack_bonus=0, target_ac=10)
        assert set(result.keys()) == {"hit", "critical", "roll", "total"}


class TestResolveAttackCriticals:
    """Natural 20 / natural 1 override normal hit/miss logic."""

    def test_natural_20_always_hits(self) -> None:
        # Even with a high AC, a natural 20 should always hit
        with patch("app.rules_engine._roll_d20", return_value=20):
            result = resolve_attack(attack_bonus=0, target_ac=100)
        assert result["hit"] is True
        assert result["critical"] is True

    def test_natural_1_always_misses(self) -> None:
        # Even with a huge bonus, a natural 1 should always miss
        with patch("app.rules_engine._roll_d20", return_value=1):
            result = resolve_attack(attack_bonus=100, target_ac=2)
        assert result["hit"] is False
        assert result["critical"] is False

    def test_natural_20_is_critical(self) -> None:
        with patch("app.rules_engine._roll_d20", return_value=20):
            result = resolve_attack(attack_bonus=5, target_ac=15)
        assert result["critical"] is True

    def test_non_natural_20_is_not_critical(self) -> None:
        # Roll 19 + bonus exceeds AC but is not a crit
        with patch("app.rules_engine._roll_d20", return_value=19):
            result = resolve_attack(attack_bonus=0, target_ac=10)
        assert result["critical"] is False


class TestResolveAttackAdvantageDisadvantage:
    """Advantage/disadvantage rolling logic."""

    def test_advantage_takes_higher_roll(self) -> None:
        rolls = iter([8, 15])
        with patch("app.rules_engine._roll_d20", side_effect=rolls):
            result = resolve_attack(attack_bonus=0, target_ac=14, advantage=True)
        assert result["roll"] == 15

    def test_disadvantage_takes_lower_roll(self) -> None:
        rolls = iter([8, 15])
        with patch("app.rules_engine._roll_d20", side_effect=rolls):
            result = resolve_attack(attack_bonus=0, target_ac=14, disadvantage=True)
        assert result["roll"] == 8

    def test_advantage_and_disadvantage_cancel(self) -> None:
        # When both are set, only one d20 roll is made (straight roll)
        with patch("app.rules_engine._roll_d20", return_value=12) as mock_roll:
            result = resolve_attack(
                attack_bonus=0, target_ac=14, advantage=True, disadvantage=True
            )
        assert mock_roll.call_count == 1
        assert result["roll"] == 12

    def test_advantage_hit_uses_higher_die(self) -> None:
        # lower=5 (miss), higher=18 (hit) → advantage should hit
        rolls = iter([5, 18])
        with patch("app.rules_engine._roll_d20", side_effect=rolls):
            result = resolve_attack(attack_bonus=0, target_ac=15, advantage=True)
        assert result["hit"] is True

    def test_disadvantage_miss_uses_lower_die(self) -> None:
        # lower=5 (miss), higher=18 (hit) → disadvantage should miss
        rolls = iter([5, 18])
        with patch("app.rules_engine._roll_d20", side_effect=rolls):
            result = resolve_attack(attack_bonus=0, target_ac=15, disadvantage=True)
        assert result["hit"] is False


# ---------------------------------------------------------------------------
# calculate_damage
# ---------------------------------------------------------------------------


class TestCalculateDamageBasic:
    """Basic damage dice rolling."""

    def test_returns_required_keys(self) -> None:
        result = calculate_damage("1d6", modifier=0)
        assert set(result.keys()) == {"rolls", "modifier", "total"}

    def test_single_die_total(self) -> None:
        with patch("app.rules_engine.random.randint", return_value=4):
            result = calculate_damage("1d6", modifier=0)
        assert result["rolls"] == [4]
        assert result["total"] == 4

    def test_modifier_is_added_to_total(self) -> None:
        with patch("app.rules_engine.random.randint", return_value=4):
            result = calculate_damage("1d6", modifier=3)
        assert result["modifier"] == 3
        assert result["total"] == 7

    def test_multiple_dice(self) -> None:
        # Two dice each returning 3 → sum 6 + modifier 0 = 6
        with patch("app.rules_engine.random.randint", return_value=3):
            result = calculate_damage("2d6", modifier=0)
        assert len(result["rolls"]) == 2
        assert result["total"] == 6

    def test_implicit_one_die(self) -> None:
        # "d8" should be treated as "1d8"
        with patch("app.rules_engine.random.randint", return_value=5):
            result = calculate_damage("d8", modifier=0)
        assert len(result["rolls"]) == 1
        assert result["total"] == 5

    def test_invalid_notation_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_damage("invalid", modifier=0)


class TestCalculateDamageCritical:
    """Critical hit doubles dice count, not modifier."""

    def test_critical_doubles_dice_count(self) -> None:
        with patch("app.rules_engine.random.randint", return_value=3):
            result = calculate_damage("2d6", modifier=0, critical=True)
        # 2d6 becomes 4d6 on a crit
        assert len(result["rolls"]) == 4

    def test_critical_modifier_not_doubled(self) -> None:
        with patch("app.rules_engine.random.randint", return_value=3):
            result = calculate_damage("2d6", modifier=5, critical=True)
        # modifier stays at 5, not 10
        assert result["modifier"] == 5
        assert result["total"] == 4 * 3 + 5  # 4 dice × 3 + 5

    def test_critical_increases_total(self) -> None:
        # Non-crit: 1d6 → [4] total 4; crit: 2d6 → more dice
        with patch("app.rules_engine.random.randint", return_value=4):
            normal = calculate_damage("1d6", modifier=0, critical=False)
            crit = calculate_damage("1d6", modifier=0, critical=True)
        assert crit["total"] > normal["total"]

    def test_non_critical_rolls_base_dice_count(self) -> None:
        with patch("app.rules_engine.random.randint", return_value=3):
            result = calculate_damage("2d6", modifier=0, critical=False)
        assert len(result["rolls"]) == 2


# ---------------------------------------------------------------------------
# apply_damage / apply_healing
# ---------------------------------------------------------------------------


class TestApplyDamage:
    """Tests for apply_damage()."""

    def test_damage_reduces_hp(self) -> None:
        """Damage correctly reduces current HP."""
        result = apply_damage(current_hp=20, max_hp=20, damage=5)
        assert result["new_hp"] == 15
        assert result["unconscious"] is False
        assert result["instant_death"] is False

    def test_hp_cannot_go_below_zero(self) -> None:
        """HP is clamped to 0, not negative."""
        result = apply_damage(current_hp=5, max_hp=20, damage=10)
        assert result["new_hp"] == 0

    def test_unconscious_at_zero_hp(self) -> None:
        """Character is unconscious when HP reaches 0."""
        result = apply_damage(current_hp=5, max_hp=20, damage=5)
        assert result["new_hp"] == 0
        assert result["unconscious"] is True
        assert result["instant_death"] is False

    def test_instant_death_when_damage_equals_max_hp(self) -> None:
        """Instant death when remaining damage (overkill) equals max_hp."""
        # current_hp=5, damage=25: overkill = 20 = max_hp → instant death
        result = apply_damage(current_hp=5, max_hp=20, damage=25)
        assert result["new_hp"] == 0
        assert result["instant_death"] is True

    def test_instant_death_when_damage_exceeds_max_hp(self) -> None:
        """Instant death when remaining damage (overkill) exceeds max_hp."""
        # current_hp=1, damage=22: overkill = 21 > 20 → instant death
        result = apply_damage(current_hp=1, max_hp=20, damage=22)
        assert result["new_hp"] == 0
        assert result["instant_death"] is True

    def test_no_instant_death_when_damage_below_max_hp(self) -> None:
        """No instant death when remaining damage < max_hp."""
        result = apply_damage(current_hp=10, max_hp=20, damage=15)
        assert result["new_hp"] == 0
        assert result["unconscious"] is True
        assert result["instant_death"] is False

    def test_zero_damage(self) -> None:
        """Zero damage leaves HP unchanged."""
        result = apply_damage(current_hp=15, max_hp=20, damage=0)
        assert result["new_hp"] == 15
        assert result["unconscious"] is False

    def test_negative_damage_treated_as_zero(self) -> None:
        """Negative damage values are treated as 0."""
        result = apply_damage(current_hp=15, max_hp=20, damage=-5)
        assert result["new_hp"] == 15


class TestApplyHealing:
    """Tests for apply_healing()."""

    def test_healing_increases_hp(self) -> None:
        """Healing correctly increases HP."""
        result = apply_healing(current_hp=5, max_hp=20, healing=10)
        assert result["new_hp"] == 15

    def test_healing_cannot_exceed_max_hp(self) -> None:
        """Healing is capped at max_hp."""
        result = apply_healing(current_hp=18, max_hp=20, healing=10)
        assert result["new_hp"] == 20

    def test_healing_at_full_hp(self) -> None:
        """Healing when already at full HP stays at max."""
        result = apply_healing(current_hp=20, max_hp=20, healing=5)
        assert result["new_hp"] == 20

    def test_negative_healing_treated_as_zero(self) -> None:
        """Negative healing values are treated as 0."""
        result = apply_healing(current_hp=10, max_hp=20, healing=-5)
        assert result["new_hp"] == 10


# ---------------------------------------------------------------------------
# death_saving_throw
# ---------------------------------------------------------------------------


class TestDeathSavingThrow:
    """Tests for death_saving_throw()."""

    def test_success_at_roll_ten_or_higher(self) -> None:
        """Roll >= 10 is a success."""
        with patch("app.rules_engine.random.randint", return_value=10):
            result = death_saving_throw()
        assert result["roll"] == 10
        assert result["success"] is True
        assert result["critical_success"] is False
        assert result["critical_fail"] is False

    def test_failure_below_ten(self) -> None:
        """Roll < 10 is a failure."""
        with patch("app.rules_engine.random.randint", return_value=9):
            result = death_saving_throw()
        assert result["roll"] == 9
        assert result["success"] is False
        assert result["critical_success"] is False
        assert result["critical_fail"] is False

    def test_natural_20_critical_success(self) -> None:
        """Natural 20 is a critical success (regain 1 HP)."""
        with patch("app.rules_engine.random.randint", return_value=20):
            result = death_saving_throw()
        assert result["roll"] == 20
        assert result["success"] is True
        assert result["critical_success"] is True
        assert result["critical_fail"] is False

    def test_natural_1_critical_fail(self) -> None:
        """Natural 1 is a critical failure (counts as 2 failures)."""
        with patch("app.rules_engine.random.randint", return_value=1):
            result = death_saving_throw()
        assert result["roll"] == 1
        assert result["success"] is False
        assert result["critical_success"] is False
        assert result["critical_fail"] is True

    def test_result_contains_required_keys(self) -> None:
        """Result always has the four required keys."""
        result = death_saving_throw()
        assert "roll" in result
        assert "success" in result
        assert "critical_success" in result
        assert "critical_fail" in result

    def test_roll_in_valid_range(self) -> None:
        """Roll is always between 1 and 20."""
        for _ in range(20):
            result = death_saving_throw()
            assert 1 <= result["roll"] <= 20


# ---------------------------------------------------------------------------
# roll_initiative
# ---------------------------------------------------------------------------


class TestRollInitiative:
    """Tests for roll_initiative()."""

    def test_initiative_sorted_descending(self) -> None:
        """Combatants are sorted by initiative highest first."""
        combatants = [
            {"name": "Fighter", "dex_modifier": 2},
            {"name": "Rogue", "dex_modifier": 4},
            {"name": "Wizard", "dex_modifier": 1},
        ]
        with patch(
            "app.rules_engine.random.randint",
            side_effect=[5, 10, 8],  # Fighter=7, Rogue=14, Wizard=9
        ):
            results = roll_initiative(combatants)

        assert results[0]["name"] == "Rogue"   # 14
        assert results[1]["name"] == "Wizard"  # 9
        assert results[2]["name"] == "Fighter" # 7

    def test_dex_modifier_tiebreaker(self) -> None:
        """Ties in initiative are broken by DEX modifier (higher wins)."""
        combatants = [
            {"name": "LowDex", "dex_modifier": 0},
            {"name": "HighDex", "dex_modifier": 3},
        ]
        # Both roll 8 so total initiative is 8 vs 11... let's make raw dice tie
        with patch(
            "app.rules_engine.random.randint",
            side_effect=[10, 7],  # LowDex=10, HighDex=10 (7+3)
        ):
            results = roll_initiative(combatants)

        # Both have initiative 10; HighDex (modifier 3) wins the tiebreak
        assert results[0]["name"] == "HighDex"
        assert results[1]["name"] == "LowDex"

    def test_initiative_includes_roll_and_total(self) -> None:
        """Each result entry contains initiative_roll and initiative."""
        combatants = [{"name": "A", "dex_modifier": 2}]
        with patch("app.rules_engine.random.randint", return_value=12):
            results = roll_initiative(combatants)
        assert results[0]["initiative_roll"] == 12
        assert results[0]["initiative"] == 14  # 12 + 2

    def test_missing_dex_modifier_defaults_to_zero(self) -> None:
        """Combatants without dex_modifier default to 0."""
        combatants = [{"name": "Monster"}]
        with patch("app.rules_engine.random.randint", return_value=15):
            results = roll_initiative(combatants)
        assert results[0]["initiative"] == 15

    def test_empty_combatant_list(self) -> None:
        """Empty list returns empty list."""
        assert roll_initiative([]) == []

    def test_original_combatant_data_preserved(self) -> None:
        """Original combatant data is preserved in the result entries."""
        combatants = [{"name": "Paladin", "dex_modifier": 1, "hp": 45}]
        results = roll_initiative(combatants)
        assert results[0]["name"] == "Paladin"
        assert results[0]["hp"] == 45
