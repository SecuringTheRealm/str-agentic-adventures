"""D&D 5e rules engine: attack, damage, HP, death saves, initiative, conditions.

Also implements mechanical level-up helpers: check_level_up, calculate_level_up_hp,
get_proficiency_bonus, and is_asi_level.
"""

import random
import re
from enum import Enum
from typing import TypedDict

from app.srd_data import CLASS_HIT_DICE, XP_THRESHOLDS, get_features_at_level


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


class Condition(str, Enum):
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


# Maximum value for any single ability score (D&D 5e SRD)
_ABILITY_SCORE_CAP = 20

_VALID_ABILITIES = frozenset(
    ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
)


def _ability_modifier(score: int) -> int:
    """Calculate the ability modifier for a given score."""
    return (score - 10) // 2


def apply_level_up(
    character_data: dict,
    choices: dict | None = None,
    use_average_hp: bool = True,
) -> dict:
    """Apply a level up to a character, returning the updated data.

    Performs the following steps:
    1. Validates that the character has enough XP and is not already level 20.
    2. Increments level.
    3. Recalculates proficiency bonus.
    4. Increases HP (average or rolled, plus CON modifier).
    5. Applies Ability Score Improvement if this is an ASI level and choices
       are provided (``{"asi": {"strength": 2}}`` or
       ``{"asi": {"dexterity": 1, "wisdom": 1}}``).
    6. Looks up class features gained at the new level.

    Args:
        character_data: A dict representation of the character sheet.
        choices: Optional dict with an ``"asi"`` key mapping ability names
            to point increases (must total exactly 2).
        use_average_hp: If ``True`` use the fixed average HP gain; otherwise
            roll the hit die.

    Returns:
        A dict with keys:
            success (bool), new_level (int), hp_gained (int),
            new_proficiency_bonus (int), ability_improvements (dict),
            features_gained (list[str]), message (str), updated_character (dict).

    Raises:
        ValueError: If the level-up is not valid or ASI choices are invalid.
    """
    current_level: int = character_data.get("level", 1)
    experience: int = character_data.get("experience", 0)

    # --- guard: max level ---
    if current_level >= 20:
        raise ValueError("Character is already at the maximum level (20).")

    # --- guard: insufficient XP ---
    if not check_level_up(experience, current_level):
        next_threshold = XP_THRESHOLDS.get(current_level + 1, 0)
        raise ValueError(
            f"Not enough XP to level up. Current: {experience}, "
            f"required for level {current_level + 1}: {next_threshold}."
        )

    new_level = current_level + 1

    # --- proficiency bonus ---
    new_proficiency = get_proficiency_bonus(new_level)

    # --- HP increase ---
    char_class: str = character_data.get("character_class", "fighter")
    abilities: dict = character_data.get("abilities", {})
    con_score: int = (
        abilities.get("constitution", 10)
        if isinstance(abilities, dict)
        else 10
    )
    con_mod = _ability_modifier(con_score)
    hp_gained = calculate_level_up_hp(char_class, con_mod, use_average=use_average_hp)

    # --- ASI handling ---
    ability_improvements: dict[str, int] = {}
    if is_asi_level(new_level) and choices and "asi" in choices:
        asi = choices["asi"]
        if not isinstance(asi, dict):
            raise ValueError(
                "ASI choices must be a dict mapping ability names "
                "to increases."
            )
        total = sum(asi.values())
        if total != 2:
            raise ValueError(
                f"ASI points must total exactly 2, got {total}."
            )
        for ability_name, increase in asi.items():
            if ability_name not in _VALID_ABILITIES:
                raise ValueError(
                    f"Invalid ability name: {ability_name!r}."
                )
            if increase not in (1, 2):
                raise ValueError(
                    f"Each ability increase must be 1 or 2, "
                    f"got {increase} for {ability_name}."
                )
            current_score = (
                abilities.get(ability_name, 10)
                if isinstance(abilities, dict)
                else 10
            )
            if current_score + increase > _ABILITY_SCORE_CAP:
                raise ValueError(
                    f"Cannot increase {ability_name} above "
                    f"{_ABILITY_SCORE_CAP} "
                    f"(current {current_score} + {increase})."
                )
        ability_improvements = dict(asi)

    # --- class features at new level ---
    features_gained = get_features_at_level(char_class, new_level)

    # --- build updated character dict ---
    updated = dict(character_data)
    updated["level"] = new_level
    updated["proficiency_bonus"] = new_proficiency

    # Update HP
    hp = updated.get("hit_points", {})
    if isinstance(hp, dict):
        hp["maximum"] = hp.get("maximum", 0) + hp_gained
        hp["current"] = hp.get("current", 0) + hp_gained
        updated["hit_points"] = hp

    # Apply ASI
    if ability_improvements:
        if not isinstance(updated.get("abilities"), dict):
            updated["abilities"] = {}
        for ability_name, increase in ability_improvements.items():
            current_val = updated["abilities"].get(ability_name, 10)
            updated["abilities"][ability_name] = min(
                current_val + increase, _ABILITY_SCORE_CAP
            )
        updated["ability_score_improvements_used"] = (
            updated.get("ability_score_improvements_used", 0) + 1
        )

    # Record features
    existing_features: list = updated.get("features", [])
    for feat_name in features_gained:
        existing_features.append(
            {
                "name": feat_name,
                "source": "class",
                "level_gained": new_level,
            }
        )
    updated["features"] = existing_features

    return {
        "success": True,
        "new_level": new_level,
        "hp_gained": hp_gained,
        "new_proficiency_bonus": new_proficiency,
        "ability_improvements": ability_improvements,
        "features_gained": features_gained,
        "message": f"Levelled up to level {new_level}!",
        "updated_character": updated,
    }


# ---------------------------------------------------------------------------
# Armor & Weapon SRD tables
# ---------------------------------------------------------------------------

# Each entry: (base_ac, add_dex: bool, max_dex_bonus: int | None)
# max_dex_bonus=None means unlimited DEX bonus
ARMOR_TABLE: dict[str, tuple[int, bool, int | None]] = {
    "padded": (11, True, None),
    "leather": (11, True, None),
    "studded leather": (12, True, None),
    "hide": (12, True, 2),
    "chain shirt": (13, True, 2),
    "scale mail": (14, True, 2),
    "breastplate": (14, True, 2),
    "half plate": (15, True, 2),
    "ring mail": (14, False, 0),
    "chain mail": (16, False, 0),
    "splint": (17, False, 0),
    "plate": (18, False, 0),
}

# Each entry: {damage_dice, damage_type, properties, weight}
WEAPON_TABLE: dict[str, dict] = {
    "club": {
        "damage_dice": "1d4",
        "damage_type": "bludgeoning",
        "properties": ["light"],
        "weight": 2.0,
    },
    "dagger": {
        "damage_dice": "1d4",
        "damage_type": "piercing",
        "properties": ["finesse", "light", "thrown"],
        "weight": 1.0,
    },
    "handaxe": {
        "damage_dice": "1d6",
        "damage_type": "slashing",
        "properties": ["light", "thrown"],
        "weight": 2.0,
    },
    "mace": {
        "damage_dice": "1d6",
        "damage_type": "bludgeoning",
        "properties": [],
        "weight": 4.0,
    },
    "quarterstaff": {
        "damage_dice": "1d6",
        "damage_type": "bludgeoning",
        "properties": ["versatile"],
        "weight": 4.0,
    },
    "shortsword": {
        "damage_dice": "1d6",
        "damage_type": "piercing",
        "properties": ["finesse", "light"],
        "weight": 2.0,
    },
    "longsword": {
        "damage_dice": "1d8",
        "damage_type": "slashing",
        "properties": ["versatile"],
        "weight": 3.0,
    },
    "greataxe": {
        "damage_dice": "1d12",
        "damage_type": "slashing",
        "properties": ["heavy", "two-handed"],
        "weight": 7.0,
    },
    "greatsword": {
        "damage_dice": "2d6",
        "damage_type": "slashing",
        "properties": ["heavy", "two-handed"],
        "weight": 6.0,
    },
    "shortbow": {
        "damage_dice": "1d6",
        "damage_type": "piercing",
        "properties": ["ammunition", "two-handed"],
        "weight": 2.0,
    },
    "longbow": {
        "damage_dice": "1d8",
        "damage_type": "piercing",
        "properties": ["ammunition", "heavy", "two-handed"],
        "weight": 2.0,
    },
    "rapier": {
        "damage_dice": "1d8",
        "damage_type": "piercing",
        "properties": ["finesse"],
        "weight": 2.0,
    },
}


def calculate_ac(
    armor_name: str | None, shield_equipped: bool, dex_modifier: int
) -> int:
    """Calculate AC from equipped armor + shield + DEX.

    Args:
        armor_name: Lowercase armor name (e.g. "chain mail"), or None for no armor.
        shield_equipped: Whether a shield is equipped (+2 AC).
        dex_modifier: The character's Dexterity modifier.

    Returns:
        Calculated armour class value.
    """
    if armor_name is None:
        # No armor: 10 + DEX
        ac = 10 + dex_modifier
    else:
        entry = ARMOR_TABLE.get(armor_name.lower())
        if entry is None:
            # Unknown armor falls back to no-armor calculation
            ac = 10 + dex_modifier
        else:
            base_ac, adds_dex, max_dex = entry
            if adds_dex:
                if max_dex is None:
                    dex_bonus = dex_modifier
                else:
                    dex_bonus = min(dex_modifier, max_dex)
                ac = base_ac + dex_bonus
            else:
                ac = base_ac

    if shield_equipped:
        ac += 2

    return ac


def get_weapon_stats(weapon_name: str) -> dict:
    """Look up weapon damage dice and properties from the SRD table.

    Args:
        weapon_name: Case-insensitive weapon name (e.g. "longsword").

    Returns:
        Dict with damage_dice, damage_type, properties, and weight.
        Returns a default entry for unknown weapons.
    """
    entry = WEAPON_TABLE.get(weapon_name.lower())
    if entry is not None:
        return dict(entry)
    # Fallback for unknown weapons
    return {
        "damage_dice": "1d4",
        "damage_type": "bludgeoning",
        "properties": [],
        "weight": 1.0,
    }
