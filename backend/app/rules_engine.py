"""D&D 5e rules engine: attack, damage, HP, death saves, initiative, conditions.

Also implements mechanical level-up helpers: check_level_up, calculate_level_up_hp,
get_proficiency_bonus, and is_asi_level.
"""

import random
import re
from enum import StrEnum
from typing import TypedDict

from app.srd_data import CLASS_HIT_DICE, XP_THRESHOLDS


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


# ---------------------------------------------------------------------------
# Combat turn tracking
# ---------------------------------------------------------------------------


def get_active_combatant(turn_order: list[dict], current_turn: int) -> dict | None:
    """Return the combatant whose turn it currently is.

    Args:
        turn_order: Ordered list of combatants (highest initiative first).
        current_turn: Zero-based index into *turn_order* for the active slot.

    Returns:
        The combatant dict at *current_turn*, or ``None`` if the list is empty
        or *current_turn* is out of range.
    """
    if not turn_order or current_turn < 0 or current_turn >= len(turn_order):
        return None
    return turn_order[current_turn]


def is_combatant_turn(
    turn_order: list[dict], current_turn: int, combatant_id: str
) -> bool:
    """Return ``True`` only if it is *combatant_id*'s turn to act.

    Args:
        turn_order: Ordered list of combatants.
        current_turn: Zero-based index of the active slot.
        combatant_id: The ``id`` field of the combatant to check.

    Returns:
        ``True`` if the active combatant's id matches *combatant_id*.
    """
    active = get_active_combatant(turn_order, current_turn)
    if active is None:
        return False
    return active.get("id") == combatant_id


def advance_turn(
    turn_order: list[dict], current_turn: int, current_round: int
) -> dict:
    """Advance to the next combatant in initiative order.

    When the last combatant in the turn order acts, the round counter
    increments and the order wraps back to index 0 (top of initiative).

    Args:
        turn_order: Ordered list of combatants (must not be empty).
        current_turn: Zero-based index of the just-finished turn.
        current_round: Current round number (1-based).

    Returns:
        A dict with:
            current_turn (int): Index of the next active combatant.
            current_round (int): Updated round number.
            round_advanced (bool): ``True`` if the round counter incremented.

    Raises:
        ValueError: If *turn_order* is empty.
    """
    if not turn_order:
        raise ValueError("turn_order must not be empty")

    next_turn = current_turn + 1
    round_advanced = False

    if next_turn >= len(turn_order):
        next_turn = 0
        current_round += 1
        round_advanced = True

    return {
        "current_turn": next_turn,
        "current_round": current_round,
        "round_advanced": round_advanced,
    }


def remove_combatant(
    turn_order: list[dict], current_turn: int, combatant_id: str
) -> dict:
    """Remove a combatant from the turn order (e.g. they were killed).

    The *current_turn* index is adjusted so that the correct next combatant
    remains active after the removal:

    * If the removed combatant was *before* the current slot, the index
      decrements by one (the active slot slides left by one position).
    * If the removed combatant *is* the active slot and they were the last
      entry, the index wraps to 0.
    * If the combatant is not found, the original turn order and index are
      returned unchanged.

    Args:
        turn_order: Current ordered list of combatants.
        current_turn: Zero-based index of the active slot.
        combatant_id: The ``id`` of the combatant to remove.

    Returns:
        A dict with:
            turn_order (list[dict]): Updated turn order without the removed combatant.
            current_turn (int): Adjusted index of the active slot.
    """
    idx = next(
        (i for i, c in enumerate(turn_order) if c.get("id") == combatant_id), None
    )

    if idx is None:
        return {"turn_order": list(turn_order), "current_turn": current_turn}

    new_order = [c for c in turn_order if c.get("id") != combatant_id]

    if idx < current_turn:
        # Removed someone before the active slot; slide the index back.
        current_turn -= 1
    elif idx == current_turn and current_turn >= len(new_order):
        # Active combatant was last in the list; wrap around.
        current_turn = 0

    return {"turn_order": new_order, "current_turn": current_turn}


# ---------------------------------------------------------------------------
# Conditions system
# ---------------------------------------------------------------------------


class Condition(StrEnum):
    """D&D 5e conditions per SRD."""

    PRONE = "prone"
    STUNNED = "stunned"
    FRIGHTENED = "frightened"
    UNCONSCIOUS = "unconscious"
    GRAPPLED = "grappled"
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    RESTRAINED = "restrained"


# Effects each condition imposes, per SRD rules.
# Keys map to boolean flags consumed by get_attack_modifiers and other helpers.
CONDITION_EFFECTS: dict[str, dict[str, bool]] = {
    Condition.PRONE: {
        "attack_disadvantage": True,
        "melee_attacker_advantage": True,
        "ranged_attacker_disadvantage": True,
    },
    Condition.STUNNED: {
        "incapacitated": True,
        "auto_fail_str_dex_saves": True,
        "attacker_advantage": True,
    },
    Condition.FRIGHTENED: {
        "ability_check_disadvantage": True,
        "attack_disadvantage": True,
        "cannot_move_closer": True,
    },
    Condition.UNCONSCIOUS: {
        "incapacitated": True,
        "auto_fail_str_dex_saves": True,
        "attacker_advantage": True,
        "prone": True,
        "auto_crit_melee": True,
    },
    Condition.GRAPPLED: {
        "speed_zero": True,
    },
    Condition.BLINDED: {
        "attack_disadvantage": True,
        "attacker_advantage": True,
    },
    Condition.CHARMED: {
        "cannot_attack_charmer": True,
        "charmer_social_advantage": True,
    },
    Condition.DEAFENED: {
        "cannot_hear": True,
    },
    Condition.INCAPACITATED: {
        "incapacitated": True,
    },
    Condition.INVISIBLE: {
        "attack_advantage": True,
        "attacker_disadvantage": True,
    },
    Condition.PARALYZED: {
        "incapacitated": True,
        "auto_fail_str_dex_saves": True,
        "attacker_advantage": True,
        "auto_crit_melee": True,
    },
    Condition.PETRIFIED: {
        "incapacitated": True,
        "auto_fail_str_dex_saves": True,
        "attacker_advantage": True,
        "resistance_nonmagical": True,
        "immune_poison_disease": True,
    },
    Condition.POISONED: {
        "attack_disadvantage": True,
        "ability_check_disadvantage": True,
    },
    Condition.RESTRAINED: {
        "speed_zero": True,
        "attack_disadvantage": True,
        "attacker_advantage": True,
        "dex_save_disadvantage": True,
    },
}


def apply_condition(combatant_conditions: list[str], condition: Condition) -> list[str]:
    """Add a condition to a combatant's condition list (no duplicates).

    Args:
        combatant_conditions: Current list of condition strings for the combatant.
        condition: The :class:`Condition` to apply.

    Returns:
        A new list with the condition added (or the same list if already present).
    """
    value = condition.value
    if value in combatant_conditions:
        return list(combatant_conditions)
    return list(combatant_conditions) + [value]


def remove_condition(
    combatant_conditions: list[str], condition: Condition
) -> list[str]:
    """Remove a condition from a combatant's condition list.

    Args:
        combatant_conditions: Current list of condition strings for the combatant.
        condition: The :class:`Condition` to remove.

    Returns:
        A new list with the condition removed (unchanged if not present).
    """
    value = condition.value
    return [c for c in combatant_conditions if c != value]


def get_attack_modifiers(
    attacker_conditions: list[str],
    target_conditions: list[str],
    *,
    ranged: bool = False,
) -> dict[str, bool]:
    """Return advantage/disadvantage flags for an attack roll.

    Aggregates all condition effects for the attacker and target and resolves
    the final advantage/disadvantage state per 5e rules (advantage and
    disadvantage cancel each other out regardless of how many sources exist).

    Args:
        attacker_conditions: Condition strings active on the attacker.
        target_conditions: Condition strings active on the target.
        ranged: Whether the attack is a ranged attack (affects prone, etc.).

    Returns:
        A dict with keys ``advantage`` and ``disadvantage`` (both ``bool``).
    """
    has_advantage = False
    has_disadvantage = False

    # --- Effects from attacker's own conditions ---
    for cond_str in attacker_conditions:
        try:
            cond = Condition(cond_str)
        except ValueError:
            continue
        effects = CONDITION_EFFECTS.get(cond, {})

        if effects.get("attack_disadvantage"):
            has_disadvantage = True
        if effects.get("attack_advantage"):
            has_advantage = True

    # --- Effects from target's conditions on the attacker ---
    for cond_str in target_conditions:
        try:
            cond = Condition(cond_str)
        except ValueError:
            continue
        effects = CONDITION_EFFECTS.get(cond, {})

        # Generic "all attacks have advantage against this target"
        if effects.get("attacker_advantage"):
            has_advantage = True

        # Generic "all attacks have disadvantage against this target"
        if effects.get("attacker_disadvantage"):
            has_disadvantage = True

        # Prone: melee → advantage, ranged → disadvantage
        if cond == Condition.PRONE:
            if ranged:
                has_disadvantage = True
            else:
                has_advantage = True

    # Per 5e rules: advantage and disadvantage cancel regardless of count
    if has_advantage and has_disadvantage:
        return {"advantage": False, "disadvantage": False}

    return {"advantage": has_advantage, "disadvantage": has_disadvantage}


# ---------------------------------------------------------------------------
# Level-up mechanics
# ---------------------------------------------------------------------------


def check_level_up(current_xp: int, current_level: int) -> bool:
    """Check if XP meets threshold for next level."""
    next_level = current_level + 1
    if next_level > 20:
        return False
    return current_xp >= XP_THRESHOLDS.get(next_level, float("inf"))


def calculate_level_up_hp(
    char_class: str, constitution_modifier: int, use_average: bool = True
) -> int:
    """Calculate HP gained on level up. Average or roll hit die + CON mod."""
    hit_die = CLASS_HIT_DICE.get(char_class, 8)
    if use_average:
        return (hit_die // 2 + 1) + constitution_modifier
    return max(1, random.randint(1, hit_die) + constitution_modifier)  # noqa: S311


def get_proficiency_bonus(level: int) -> int:
    """Proficiency bonus by level (2 at L1–4, 3 at L5–8, …, 6 at L17–20)."""
    return (level - 1) // 4 + 2


def is_asi_level(level: int) -> bool:
    """Check if this level grants an Ability Score Improvement."""
    return level in (4, 8, 12, 16, 19)
