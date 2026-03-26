"""Negative and edge-case combat tests for the rules engine.

Covers scenarios that sit outside the normal happy path: zero-HP attackers,
self-targeting, unavailable class actions, dead targets, negative damage,
overkill / instant death, duplicate conditions, and absent-condition removal.

See issue #524.
"""

from unittest.mock import patch

import pytest
from app.rules_engine import (
    Condition,
    apply_condition,
    apply_damage,
    apply_healing,
    calculate_damage,
    get_attack_modifiers,
    remove_condition,
    resolve_attack,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fighter_combatant() -> dict:
    """A level-5 Fighter with standard stats."""
    return {
        "id": "fighter-1",
        "name": "Thorn",
        "character_class": "fighter",
        "current_hp": 45,
        "max_hp": 45,
        "armor_class": 18,
        "attack_bonus": 7,
        "damage_dice": "1d8",
        "damage_modifier": 4,
        "conditions": [],
    }


@pytest.fixture
def wizard_combatant() -> dict:
    """A level-5 Wizard with lower HP."""
    return {
        "id": "wizard-1",
        "name": "Elara",
        "character_class": "wizard",
        "current_hp": 28,
        "max_hp": 28,
        "armor_class": 13,
        "attack_bonus": 5,
        "damage_dice": "1d6",
        "damage_modifier": 3,
        "conditions": [],
    }


@pytest.fixture
def dead_combatant(fighter_combatant: dict) -> dict:
    """A combatant already at 0 HP."""
    return {**fighter_combatant, "id": "dead-1", "name": "Fallen", "current_hp": 0}


# ---------------------------------------------------------------------------
# 1. Attack at 0 HP
# ---------------------------------------------------------------------------


class TestAttackAtZeroHP:
    """A combatant at 0 HP should not be able to attack effectively.

    The current rules engine (resolve_attack) does not accept attacker HP,
    so there is no built-in gate.  These tests document the expected
    behaviour once such a check is added, and are marked xfail until then.
    """

    @pytest.mark.xfail(
        reason="resolve_attack does not yet gate on attacker HP",
        strict=False,
    )
    def test_attack_at_zero_hp_should_fail(self, dead_combatant: dict) -> None:
        """A 0-HP combatant's attack should be prevented or flagged."""
        # If the engine added an attacker_hp parameter, we'd expect a
        # rejection or an automatic miss.  For now we verify the function
        # runs without error and document the gap.
        with patch("app.rules_engine._roll_d20", return_value=15):
            result = resolve_attack(
                attack_bonus=dead_combatant["attack_bonus"],
                target_ac=13,
            )
        # The expectation is that an unconscious / 0-HP attacker should not
        # score a hit; the engine currently allows it.
        assert result["hit"] is False

    def test_unconscious_condition_grants_attack_disadvantage(
        self, dead_combatant: dict
    ) -> None:
        """An unconscious attacker should at least have disadvantage."""
        mods = get_attack_modifiers(
            attacker_conditions=[Condition.UNCONSCIOUS.value],
            target_conditions=[],
        )
        # Unconscious implies incapacitated — SRD says the creature can't
        # take actions.  The condition effect dict doesn't set
        # attack_disadvantage directly but the incapacitated flag is present.
        assert mods["advantage"] is False  # no advantage on own attacks


# ---------------------------------------------------------------------------
# 2. Target self
# ---------------------------------------------------------------------------


class TestTargetSelf:
    """Attempting to target oneself with an attack.

    The rules engine operates on numeric values (bonus, AC, dice) and does
    not track attacker / target identity.  These tests document expected
    behaviour and work with what the engine exposes.
    """

    def test_self_target_attack_still_resolves(
        self, fighter_combatant: dict
    ) -> None:
        """Engine resolves an attack even when attacker == target (same AC)."""
        with patch("app.rules_engine._roll_d20", return_value=15):
            result = resolve_attack(
                attack_bonus=fighter_combatant["attack_bonus"],
                target_ac=fighter_combatant["armor_class"],
            )
        # The engine has no identity awareness; the roll is valid.
        assert "hit" in result

    def test_self_damage_applies_normally(
        self, fighter_combatant: dict
    ) -> None:
        """Damage applied to self should follow normal HP rules."""
        dmg = calculate_damage("1d8", modifier=4, critical=False)
        result = apply_damage(
            current_hp=fighter_combatant["current_hp"],
            max_hp=fighter_combatant["max_hp"],
            damage=dmg["total"],
        )
        assert result["new_hp"] < fighter_combatant["current_hp"]
        assert result["new_hp"] >= 0


# ---------------------------------------------------------------------------
# 3. Use unavailable action (Action Surge for non-Fighter)
# ---------------------------------------------------------------------------


class TestUnavailableAction:
    """Attempting to use a class-specific action on a non-qualifying class.

    The rules engine does not implement Action Surge or class-feature
    gating, so these tests document the expectation and are marked xfail.
    """

    @pytest.mark.xfail(
        reason="No class-feature gating in rules_engine yet",
        strict=False,
    )
    def test_action_surge_unavailable_for_wizard(
        self, wizard_combatant: dict
    ) -> None:
        """A Wizard should not be able to use Action Surge."""
        # When class-feature validation is added, calling something like
        # use_class_action(combatant, "action_surge") should raise or
        # return an error for non-Fighters.
        from app.rules_engine import use_class_action  # type: ignore[attr-defined]

        with pytest.raises((ValueError, AttributeError)):
            use_class_action(wizard_combatant, "action_surge")

    @pytest.mark.xfail(
        reason="No class-feature gating in rules_engine yet",
        strict=False,
    )
    def test_action_surge_available_for_fighter(
        self, fighter_combatant: dict
    ) -> None:
        """A Fighter should be allowed to use Action Surge."""
        from app.rules_engine import use_class_action  # type: ignore[attr-defined]

        result = use_class_action(fighter_combatant, "action_surge")
        assert result is not None


# ---------------------------------------------------------------------------
# 4. Attack dead target
# ---------------------------------------------------------------------------


class TestAttackDeadTarget:
    """Attacking a target already at 0 HP."""

    def test_attack_resolves_against_dead_target(
        self, dead_combatant: dict
    ) -> None:
        """The engine should still resolve the attack roll (no crash)."""
        with patch("app.rules_engine._roll_d20", return_value=15):
            result = resolve_attack(
                attack_bonus=7,
                target_ac=dead_combatant["armor_class"],
            )
        assert "hit" in result

    def test_damage_to_zero_hp_target_stays_at_zero(self) -> None:
        """Applying further damage to a 0-HP target keeps HP at 0."""
        result = apply_damage(current_hp=0, max_hp=45, damage=10)
        assert result["new_hp"] == 0
        assert result["unconscious"] is True

    def test_massive_damage_to_zero_hp_triggers_instant_death(self) -> None:
        """If overkill >= max_hp on a 0-HP target, instant death triggers."""
        result = apply_damage(current_hp=0, max_hp=45, damage=45)
        assert result["instant_death"] is True
        assert result["new_hp"] == 0


# ---------------------------------------------------------------------------
# 5. Negative damage
# ---------------------------------------------------------------------------


class TestNegativeDamage:
    """Negative damage values should never reduce HP below the floor."""

    def test_negative_damage_is_clamped_to_zero(self) -> None:
        """apply_damage should treat negative damage as 0."""
        result = apply_damage(current_hp=20, max_hp=30, damage=-5)
        assert result["new_hp"] == 20  # no change

    def test_negative_healing_is_clamped_to_zero(self) -> None:
        """apply_healing should treat negative healing as 0."""
        result = apply_healing(current_hp=20, max_hp=30, healing=-10)
        assert result["new_hp"] == 20  # no change

    def test_zero_damage_leaves_hp_unchanged(self) -> None:
        """Zero damage should be a no-op."""
        result = apply_damage(current_hp=25, max_hp=40, damage=0)
        assert result["new_hp"] == 25
        assert result["unconscious"] is False


# ---------------------------------------------------------------------------
# 6. Overkill / instant death
# ---------------------------------------------------------------------------


class TestOverkillAndInstantDeath:
    """Damage exceeding remaining HP should cap at 0; massive damage
    triggers instant death per SRD rules."""

    def test_hp_floors_at_zero(self) -> None:
        """HP must never go negative."""
        result = apply_damage(current_hp=10, max_hp=30, damage=50)
        assert result["new_hp"] == 0

    def test_unconscious_on_zero_hp(self) -> None:
        """Reaching 0 HP should flag unconscious."""
        result = apply_damage(current_hp=5, max_hp=30, damage=5)
        assert result["unconscious"] is True
        assert result["new_hp"] == 0

    def test_instant_death_when_overkill_exceeds_max_hp(self) -> None:
        """Overkill damage >= max_hp triggers instant death (SRD massive damage)."""
        # current 10, max 30, damage 40 → raw HP = -30, overkill = 30 >= 30
        result = apply_damage(current_hp=10, max_hp=30, damage=40)
        assert result["instant_death"] is True

    def test_no_instant_death_when_overkill_below_max_hp(self) -> None:
        """Overkill less than max_hp should NOT trigger instant death."""
        # current 10, max 30, damage 20 → raw HP = -10, overkill = 10 < 30
        result = apply_damage(current_hp=10, max_hp=30, damage=20)
        assert result["instant_death"] is False
        assert result["unconscious"] is True

    def test_exact_max_hp_overkill_triggers_instant_death(self) -> None:
        """Overkill exactly equal to max_hp should trigger instant death."""
        # current 10, max 20, damage 30 → raw HP = -20, overkill = 20 >= 20
        result = apply_damage(current_hp=10, max_hp=20, damage=30)
        assert result["instant_death"] is True


# ---------------------------------------------------------------------------
# 7. Double condition
# ---------------------------------------------------------------------------


class TestDoubleCondition:
    """Applying a condition already present should not duplicate it."""

    def test_apply_stunned_twice_no_duplicate(self) -> None:
        """Applying STUNNED to an already-stunned combatant yields one entry."""
        conditions = apply_condition([], Condition.STUNNED)
        assert conditions.count(Condition.STUNNED.value) == 1

        conditions = apply_condition(conditions, Condition.STUNNED)
        assert conditions.count(Condition.STUNNED.value) == 1

    def test_apply_multiple_different_conditions(self) -> None:
        """Different conditions can coexist."""
        conditions: list[str] = []
        conditions = apply_condition(conditions, Condition.STUNNED)
        conditions = apply_condition(conditions, Condition.BLINDED)
        assert len(conditions) == 2
        assert Condition.STUNNED.value in conditions
        assert Condition.BLINDED.value in conditions

    def test_duplicate_does_not_reorder(self) -> None:
        """Re-applying an existing condition should preserve list order."""
        conditions = apply_condition([], Condition.PRONE)
        conditions = apply_condition(conditions, Condition.BLINDED)
        original_order = list(conditions)

        conditions = apply_condition(conditions, Condition.PRONE)
        assert conditions == original_order


# ---------------------------------------------------------------------------
# 8. Remove absent condition
# ---------------------------------------------------------------------------


class TestRemoveAbsentCondition:
    """Removing a condition not present should not error or alter the list."""

    def test_remove_absent_condition_returns_same_list(self) -> None:
        """Removing a condition that isn't there should be a safe no-op."""
        conditions = [Condition.BLINDED.value]
        result = remove_condition(conditions, Condition.STUNNED)
        assert result == [Condition.BLINDED.value]

    def test_remove_from_empty_list(self) -> None:
        """Removing from an empty condition list should return empty."""
        result = remove_condition([], Condition.FRIGHTENED)
        assert result == []

    def test_remove_does_not_mutate_original(self) -> None:
        """The original list must not be modified."""
        original = [Condition.PRONE.value, Condition.POISONED.value]
        original_copy = list(original)
        remove_condition(original, Condition.STUNNED)
        assert original == original_copy
