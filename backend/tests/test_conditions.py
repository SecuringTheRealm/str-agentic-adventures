"""
Tests for the conditions system in rules_engine.py.

Covers Condition enum, CONDITION_EFFECTS, apply_condition,
remove_condition, and get_attack_modifiers.
"""

import pytest
from app.rules_engine import (
    CONDITION_EFFECTS,
    Condition,
    apply_condition,
    get_attack_modifiers,
    remove_condition,
)


class TestConditionEnum:
    """Verify all expected SRD conditions are present in the enum."""

    @pytest.mark.unit
    def test_all_conditions_defined(self) -> None:
        """All 14 SRD conditions must be present."""
        expected = {
            "prone",
            "stunned",
            "frightened",
            "unconscious",
            "grappled",
            "blinded",
            "charmed",
            "deafened",
            "incapacitated",
            "invisible",
            "paralyzed",
            "petrified",
            "poisoned",
            "restrained",
        }
        actual = {c.value for c in Condition}
        assert actual == expected

    @pytest.mark.unit
    def test_condition_is_string_enum(self) -> None:
        """Condition values must be plain strings (str subclass)."""
        for cond in Condition:
            assert isinstance(cond.value, str)
            # str(Enum) on a str-Enum returns the value directly
            assert cond == cond.value


class TestConditionEffects:
    """Verify key entries in CONDITION_EFFECTS match SRD rules."""

    @pytest.mark.unit
    def test_prone_effects(self) -> None:
        """Prone: disadvantage on own attacks, melee/ranged modifier for attackers."""
        effects = CONDITION_EFFECTS[Condition.PRONE]
        assert effects.get("attack_disadvantage") is True
        assert effects.get("melee_attacker_advantage") is True
        assert effects.get("ranged_attacker_disadvantage") is True

    @pytest.mark.unit
    def test_stunned_effects(self) -> None:
        """Stunned: incapacitated, auto-fail STR/DEX saves, attackers have advantage."""
        effects = CONDITION_EFFECTS[Condition.STUNNED]
        assert effects.get("incapacitated") is True
        assert effects.get("auto_fail_str_dex_saves") is True
        assert effects.get("attacker_advantage") is True

    @pytest.mark.unit
    def test_unconscious_effects(self) -> None:
        """Unconscious: incapacitated + auto-fail saves + attacker advantage + prone."""
        effects = CONDITION_EFFECTS[Condition.UNCONSCIOUS]
        assert effects.get("incapacitated") is True
        assert effects.get("auto_fail_str_dex_saves") is True
        assert effects.get("attacker_advantage") is True
        assert effects.get("prone") is True

    @pytest.mark.unit
    def test_all_conditions_have_effects(self) -> None:
        """Every condition must have at least one effect entry."""
        for cond in Condition:
            assert cond in CONDITION_EFFECTS, f"{cond} missing from CONDITION_EFFECTS"
            assert len(CONDITION_EFFECTS[cond]) > 0, f"{cond} has empty effects"


class TestApplyCondition:
    """Tests for apply_condition()."""

    @pytest.mark.unit
    def test_apply_condition_adds_to_list(self) -> None:
        """Applying a condition should add it to the list."""
        result = apply_condition([], Condition.PRONE)
        assert "prone" in result

    @pytest.mark.unit
    def test_apply_condition_no_duplicate(self) -> None:
        """Applying the same condition twice must not create duplicates."""
        conditions = apply_condition([], Condition.PRONE)
        conditions = apply_condition(conditions, Condition.PRONE)
        assert conditions.count("prone") == 1

    @pytest.mark.unit
    def test_apply_condition_preserves_existing(self) -> None:
        """Applying a new condition should preserve existing conditions."""
        conditions = ["stunned"]
        result = apply_condition(conditions, Condition.PRONE)
        assert "stunned" in result
        assert "prone" in result

    @pytest.mark.unit
    def test_apply_condition_returns_new_list(self) -> None:
        """apply_condition must return a new list, not mutate the original."""
        original = ["stunned"]
        result = apply_condition(original, Condition.PRONE)
        assert original == ["stunned"]
        assert result != original


class TestRemoveCondition:
    """Tests for remove_condition()."""

    @pytest.mark.unit
    def test_remove_condition_removes_it(self) -> None:
        """Removing a condition should exclude it from the returned list."""
        conditions = ["prone", "stunned"]
        result = remove_condition(conditions, Condition.PRONE)
        assert "prone" not in result
        assert "stunned" in result

    @pytest.mark.unit
    def test_remove_condition_not_present(self) -> None:
        """Removing a condition that isn't present should be a no-op."""
        conditions = ["stunned"]
        result = remove_condition(conditions, Condition.PRONE)
        assert result == ["stunned"]

    @pytest.mark.unit
    def test_remove_condition_empty_list(self) -> None:
        """Removing from an empty list should return an empty list."""
        result = remove_condition([], Condition.PRONE)
        assert result == []

    @pytest.mark.unit
    def test_remove_condition_returns_new_list(self) -> None:
        """remove_condition must return a new list, not mutate the original."""
        original = ["prone", "stunned"]
        result = remove_condition(original, Condition.PRONE)
        assert original == ["prone", "stunned"]
        assert result == ["stunned"]


class TestGetAttackModifiers:
    """Tests for get_attack_modifiers()."""

    @pytest.mark.unit
    def test_no_conditions_no_modifier(self) -> None:
        """No conditions → no advantage or disadvantage."""
        result = get_attack_modifiers([], [])
        assert result == {"advantage": False, "disadvantage": False}

    @pytest.mark.unit
    def test_prone_target_melee_advantage(self) -> None:
        """Attacking a prone target in melee grants advantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["prone"], ranged=False
        )
        assert result["advantage"] is True
        assert result["disadvantage"] is False

    @pytest.mark.unit
    def test_prone_target_ranged_disadvantage(self) -> None:
        """Attacking a prone target at range gives disadvantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["prone"], ranged=True
        )
        assert result["advantage"] is False
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_prone_attacker_disadvantage(self) -> None:
        """A prone attacker has disadvantage on their own attacks."""
        result = get_attack_modifiers(
            attacker_conditions=["prone"], target_conditions=[], ranged=False
        )
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_stunned_target_attacker_advantage(self) -> None:
        """Attacks against a stunned creature have advantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["stunned"]
        )
        assert result["advantage"] is True
        assert result["disadvantage"] is False

    @pytest.mark.unit
    def test_blinded_attacker_disadvantage(self) -> None:
        """A blinded attacker has disadvantage."""
        result = get_attack_modifiers(
            attacker_conditions=["blinded"], target_conditions=[]
        )
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_blinded_target_advantage(self) -> None:
        """Attacks against a blinded target have advantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["blinded"]
        )
        assert result["advantage"] is True

    @pytest.mark.unit
    def test_invisible_attacker_advantage(self) -> None:
        """An invisible attacker has advantage on attacks."""
        result = get_attack_modifiers(
            attacker_conditions=["invisible"], target_conditions=[]
        )
        assert result["advantage"] is True

    @pytest.mark.unit
    def test_invisible_target_disadvantage(self) -> None:
        """Attacks against an invisible target have disadvantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["invisible"]
        )
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_advantage_and_disadvantage_cancel(self) -> None:
        """Advantage and disadvantage from different sources cancel each other."""
        # Invisible attacker (advantage) + prone attacker (disadvantage) → straight roll
        result = get_attack_modifiers(
            attacker_conditions=["invisible", "prone"],
            target_conditions=[],
            ranged=False,
        )
        assert result == {"advantage": False, "disadvantage": False}

    @pytest.mark.unit
    def test_multiple_advantages_still_cancel_single_disadvantage(self) -> None:
        """Per 5e rules, multiple advantage sources still cancel one disadvantage."""
        # stunned + blinded target (advantage) vs prone attacker (disadvantage)
        result = get_attack_modifiers(
            attacker_conditions=["prone"],
            target_conditions=["stunned", "blinded"],
            ranged=False,
        )
        assert result == {"advantage": False, "disadvantage": False}

    @pytest.mark.unit
    def test_unconscious_target_advantage(self) -> None:
        """Attacks against an unconscious target have advantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["unconscious"]
        )
        assert result["advantage"] is True

    @pytest.mark.unit
    def test_poisoned_attacker_disadvantage(self) -> None:
        """A poisoned attacker has disadvantage on attack rolls."""
        result = get_attack_modifiers(
            attacker_conditions=["poisoned"], target_conditions=[]
        )
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_restrained_attacker_disadvantage(self) -> None:
        """A restrained attacker has disadvantage on attacks."""
        result = get_attack_modifiers(
            attacker_conditions=["restrained"], target_conditions=[]
        )
        assert result["disadvantage"] is True

    @pytest.mark.unit
    def test_restrained_target_advantage(self) -> None:
        """Attacks against a restrained target have advantage."""
        result = get_attack_modifiers(
            attacker_conditions=[], target_conditions=["restrained"]
        )
        assert result["advantage"] is True

    @pytest.mark.unit
    def test_unknown_condition_ignored(self) -> None:
        """Unknown condition strings should be silently ignored."""
        result = get_attack_modifiers(
            attacker_conditions=["flying"],
            target_conditions=["burning"],
        )
        assert result == {"advantage": False, "disadvantage": False}
