"""
Spell mechanics utilities for D&D 5e rules.

Provides pure functions for concentration tracking and spell calculations.
"""

import random

from pydantic import BaseModel

SPELLCASTING_ABILITY: dict[str, str] = {
    "wizard": "intelligence",
    "cleric": "wisdom",
    "druid": "wisdom",
    "bard": "charisma",
    "sorcerer": "charisma",
    "warlock": "charisma",
    "paladin": "charisma",
    "ranger": "wisdom",
}


class ConcentrationState(BaseModel):
    """Tracks which spell (if any) a caster is currently concentrating on."""

    active_spell: str | None = None
    caster_id: str | None = None


def start_concentration(
    state: ConcentrationState, spell_name: str, caster_id: str
) -> ConcentrationState:
    """Start concentrating on a spell, breaking any existing concentration.

    Args:
        state: Current concentration state.
        spell_name: Name of the spell to concentrate on.
        caster_id: Unique identifier for the caster.

    Returns:
        New ConcentrationState with the given spell active.
    """
    return ConcentrationState(active_spell=spell_name, caster_id=caster_id)


def check_concentration(constitution_modifier: int, damage_taken: int) -> dict:
    """Roll a Constitution saving throw to maintain concentration after taking damage.

    DC = max(10, damage_taken // 2).

    Args:
        constitution_modifier: The caster's Constitution modifier.
        damage_taken: Amount of damage just received.

    Returns:
        dict with keys ``dc`` (int), ``roll`` (int), and ``maintained`` (bool).
    """
    dc = max(10, damage_taken // 2)
    roll = random.randint(1, 20)  # noqa: S311
    total = roll + constitution_modifier
    return {"dc": dc, "roll": roll, "maintained": total >= dc}


def break_concentration(state: ConcentrationState) -> ConcentrationState:
    """End concentration, clearing the active spell.

    Args:
        state: Current concentration state.

    Returns:
        New ConcentrationState with no active spell.
    """
    return ConcentrationState(active_spell=None, caster_id=state.caster_id)


def calculate_spell_save_dc(
    proficiency_bonus: int, spellcasting_ability_modifier: int
) -> int:
    """Calculate the spell save DC for a caster.

    DC = 8 + proficiency bonus + spellcasting ability modifier.

    Args:
        proficiency_bonus: The caster's proficiency bonus.
        spellcasting_ability_modifier: Modifier for the caster's spellcasting ability.

    Returns:
        The spell save DC as an integer.
    """
    return 8 + proficiency_bonus + spellcasting_ability_modifier


def calculate_spell_attack_modifier(
    proficiency_bonus: int, spellcasting_ability_modifier: int
) -> int:
    """Calculate the spell attack roll modifier for a caster.

    Modifier = proficiency bonus + spellcasting ability modifier.

    Args:
        proficiency_bonus: The caster's proficiency bonus.
        spellcasting_ability_modifier: Modifier for the caster's spellcasting ability.

    Returns:
        The spell attack modifier as an integer.
    """
    return proficiency_bonus + spellcasting_ability_modifier
