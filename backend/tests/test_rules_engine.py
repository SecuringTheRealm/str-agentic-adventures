"""Tests for backend/app/rules_engine.py — attack resolution and damage calculation."""

from unittest.mock import patch

import pytest
from app.rules_engine import calculate_damage, resolve_attack

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
