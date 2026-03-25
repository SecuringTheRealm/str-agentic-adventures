"""Deterministic attack and damage resolution functions for D&D 5e rules."""

import random
import re
from typing import TypedDict


class AttackResult(TypedDict):
    hit: bool
    critical: bool
    roll: int
    total: int


class DamageResult(TypedDict):
    rolls: list[int]
    modifier: int
    total: int


def _roll_d20() -> int:
    return random.randint(1, 20)  # noqa: S311


def resolve_attack(
    attack_bonus: int,
    target_ac: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> AttackResult:
    """Roll d20 + attack_bonus vs target AC.

    Returns {hit: bool, critical: bool, roll: int, total: int}

    - Natural 20 is a critical hit (always hits).
    - Natural 1 is a critical miss (always misses).
    - Advantage: roll 2d20, take higher.
    - Disadvantage: roll 2d20, take lower.
    - Advantage + disadvantage cancel out (roll normally).
    """
    net_advantage = advantage and not disadvantage
    net_disadvantage = disadvantage and not advantage

    if net_advantage:
        roll1, roll2 = _roll_d20(), _roll_d20()
        roll = max(roll1, roll2)
    elif net_disadvantage:
        roll1, roll2 = _roll_d20(), _roll_d20()
        roll = min(roll1, roll2)
    else:
        roll = _roll_d20()

    total = roll + attack_bonus
    critical = roll == 20
    miss = roll == 1

    if critical:
        hit = True
    elif miss:
        hit = False
    else:
        hit = total >= target_ac

    return {
        "hit": hit,
        "critical": critical,
        "roll": roll,
        "total": total,
    }


def calculate_damage(
    damage_dice: str, modifier: int = 0, critical: bool = False
) -> DamageResult:
    """Roll damage dice + modifier.

    Accepts standard notation such as "2d6" or "1d8" (modifier is passed separately).
    Critical hit doubles the number of dice rolled (not the modifier).

    Returns {rolls: list, modifier: int, total: int}
    """
    match = re.fullmatch(r"(\d*)d(\d+)", damage_dice.strip())
    if not match:
        raise ValueError(f"Invalid damage dice notation: {damage_dice!r}")

    num_dice = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))

    if critical:
        num_dice *= 2

    rolls = [random.randint(1, sides) for _ in range(num_dice)]  # noqa: S311
    total = sum(rolls) + modifier

    return {
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
    }
