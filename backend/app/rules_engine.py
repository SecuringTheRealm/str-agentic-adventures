"""D&D 5e rules engine: attack resolution, damage calculation, HP tracking, death saves, and initiative."""

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


# ---------------------------------------------------------------------------
# HP tracking
# ---------------------------------------------------------------------------


def apply_damage(current_hp: int, max_hp: int, damage: int) -> dict:
    """Apply damage to a character.

    Returns a dict with:
        new_hp (int): HP after damage (minimum 0)
        unconscious (bool): True if HP drops to 0
        instant_death (bool): True if remaining damage >= max_hp (massive damage rule)
    """
    if damage < 0:
        damage = 0

    raw_new_hp = current_hp - damage
    overkill = abs(min(raw_new_hp, 0))  # damage beyond what reduced HP to 0
    instant_death = raw_new_hp <= 0 and overkill >= max_hp
    new_hp = max(0, raw_new_hp)
    unconscious = new_hp == 0

    return {
        "new_hp": new_hp,
        "unconscious": unconscious,
        "instant_death": instant_death,
    }


def apply_healing(current_hp: int, max_hp: int, healing: int) -> dict:
    """Apply healing to a character.

    Returns a dict with:
        new_hp (int): HP after healing (capped at max_hp)
    """
    if healing < 0:
        healing = 0

    new_hp = min(current_hp + healing, max_hp)
    return {"new_hp": new_hp}


# ---------------------------------------------------------------------------
# Death saving throws
# ---------------------------------------------------------------------------


def death_saving_throw() -> dict:
    """Roll a d20 death saving throw (DC 10).

    Returns a dict with:
        roll (int): The d20 result
        success (bool): True if roll >= 10
        critical_success (bool): True on natural 20 (regain 1 HP)
        critical_fail (bool): True on natural 1 (counts as 2 failures)
    """
    roll = random.randint(1, 20)  # noqa: S311
    critical_success = roll == 20
    critical_fail = roll == 1
    success = roll >= 10

    return {
        "roll": roll,
        "success": success,
        "critical_success": critical_success,
        "critical_fail": critical_fail,
    }


# ---------------------------------------------------------------------------
# Initiative
# ---------------------------------------------------------------------------


def roll_initiative(combatants: list[dict]) -> list[dict]:
    """Roll initiative for each combatant (d20 + DEX modifier).

    Each combatant dict should contain:
        name (str): Combatant name
        dex_modifier (int): Dexterity modifier (default 0 if missing)

    Returns the list sorted by initiative descending; ties broken by DEX modifier
    (higher DEX modifier wins the tie).
    """
    results = []
    for combatant in combatants:
        dex_mod = combatant.get("dex_modifier", 0)
        roll = random.randint(1, 20)  # noqa: S311
        initiative = roll + dex_mod
        entry = dict(combatant)
        entry["initiative_roll"] = roll
        entry["initiative"] = initiative
        results.append(entry)

    results.sort(
        key=lambda c: (c["initiative"], c.get("dex_modifier", 0)), reverse=True
    )
    return results
