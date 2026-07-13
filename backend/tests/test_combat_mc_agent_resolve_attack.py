"""Tests for the AI-mode (SDK-tool) attack resolution in combat_mc_agent.

Covers F06 (natural-1/natural-20 rules) and F27 (conditions feed advantage/
disadvantage into the roll) for the module-level ``resolve_attack`` function
that the Microsoft Agent Framework SDK registers as an LLM-callable tool.
"""

import json
from unittest.mock import patch

from app.agents.combat_mc_agent import resolve_attack


def _mock_roll(total: int, modifier: int = 3) -> dict:
    """Build a DiceRoller.roll_d20-shaped result for a given total/modifier."""
    return {
        "rolls": [total - modifier],
        "modifier": modifier,
        "total": total,
        "advantage_type": "normal",
    }


class TestResolveAttackCriticals:
    """Natural 20 always hits and crits; natural 1 always misses (SRD p.194)."""

    def test_natural_20_always_hits_and_crits_even_below_ac(self) -> None:
        with (
            patch(
                "app.agents.combat_mc_agent.DiceRoller.roll_d20",
                return_value=_mock_roll(total=23, modifier=3),  # natural 20
            ),
            patch(
                "app.agents.combat_mc_agent.DiceRoller.roll_damage",
                side_effect=[
                    {"rolls": [4], "modifier": 3, "total": 7},
                    {"rolls": [5], "modifier": 0, "total": 5},
                ],
            ),
        ):
            result = json.loads(
                resolve_attack(attack_bonus=3, target_ac=99, damage_dice="1d8+3")
            )

        assert result["critical"] is True
        assert result["hit"] is True
        # Crit doubles the dice: both damage rolls are summed into one total.
        assert result["damage"]["total"] == 12
        assert result["damage"]["rolls"] == [4, 5]

    def test_natural_1_always_misses_even_above_ac(self) -> None:
        with patch(
            "app.agents.combat_mc_agent.DiceRoller.roll_d20",
            return_value=_mock_roll(total=11, modifier=10),  # natural 1
        ):
            result = json.loads(
                resolve_attack(attack_bonus=10, target_ac=5, damage_dice="1d8")
            )

        assert result["critical"] is False
        assert result["hit"] is False
        assert "damage" not in result

    def test_normal_roll_hits_at_or_above_ac(self) -> None:
        with (
            patch(
                "app.agents.combat_mc_agent.DiceRoller.roll_d20",
                return_value=_mock_roll(total=15, modifier=3),  # natural 12
            ),
            patch(
                "app.agents.combat_mc_agent.DiceRoller.roll_damage",
                return_value={"rolls": [4], "modifier": 3, "total": 7},
            ),
        ):
            result = json.loads(
                resolve_attack(attack_bonus=3, target_ac=15, damage_dice="1d8+3")
            )

        assert result["critical"] is False
        assert result["hit"] is True
        assert result["damage"]["total"] == 7

    def test_normal_roll_misses_below_ac(self) -> None:
        with patch(
            "app.agents.combat_mc_agent.DiceRoller.roll_d20",
            return_value=_mock_roll(total=14, modifier=3),  # natural 11
        ):
            result = json.loads(
                resolve_attack(attack_bonus=3, target_ac=15, damage_dice="1d8+3")
            )

        assert result["hit"] is False
        assert "damage" not in result


class TestResolveAttackConditions:
    """Conditions feed into advantage/disadvantage on the attack roll (F27)."""

    def test_target_prone_grants_melee_attacker_advantage(self) -> None:
        with patch(
            "app.agents.combat_mc_agent.DiceRoller.roll_d20",
            return_value=_mock_roll(total=15, modifier=3),
        ) as mock_roll_d20:
            resolve_attack(
                attack_bonus=3,
                target_ac=15,
                damage_dice="1d8",
                target_conditions=["prone"],
            )

        # args are (modifier, advantage, disadvantage) per DiceRoller.roll_d20
        assert mock_roll_d20.call_args.args[1] is True  # advantage
        assert mock_roll_d20.call_args.args[2] is False  # disadvantage

    def test_attacker_restrained_gives_attacker_disadvantage(self) -> None:
        with patch(
            "app.agents.combat_mc_agent.DiceRoller.roll_d20",
            return_value=_mock_roll(total=15, modifier=3),
        ) as mock_roll_d20:
            resolve_attack(
                attack_bonus=3,
                target_ac=15,
                damage_dice="1d8",
                attacker_conditions=["restrained"],
            )

        assert mock_roll_d20.call_args.args[1] is False  # advantage
        assert mock_roll_d20.call_args.args[2] is True  # disadvantage

    def test_explicit_advantage_flag_still_honoured_without_conditions(self) -> None:
        with patch(
            "app.agents.combat_mc_agent.DiceRoller.roll_d20",
            return_value=_mock_roll(total=15, modifier=3),
        ) as mock_roll_d20:
            resolve_attack(
                attack_bonus=3, target_ac=15, damage_dice="1d8", advantage=True
            )

        assert mock_roll_d20.call_args.args[1] is True
        assert mock_roll_d20.call_args.args[2] is False
