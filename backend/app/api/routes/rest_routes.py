"""Short and long rest routes for D&D rest mechanics."""

import logging
import random

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    CharacterClass,
    CharacterSheet,
    RestRequest,
    RestResponse,
    RestType,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rest"])

HIT_DIE_SIZE: dict[CharacterClass, int] = {
    CharacterClass.BARBARIAN: 12,
    CharacterClass.FIGHTER: 10,
    CharacterClass.PALADIN: 10,
    CharacterClass.RANGER: 10,
    CharacterClass.MONK: 8,
    CharacterClass.CLERIC: 8,
    CharacterClass.DRUID: 8,
    CharacterClass.ROGUE: 8,
    CharacterClass.BARD: 8,
    CharacterClass.WARLOCK: 8,
    CharacterClass.WIZARD: 6,
    CharacterClass.SORCERER: 6,
}


def _con_modifier(character: CharacterSheet) -> int:
    """Calculate Constitution modifier from ability score."""
    return (character.abilities.constitution - 10) // 2


def calculate_short_rest(
    character: CharacterSheet, hit_dice_to_spend: int
) -> dict:
    """Apply short rest effects: spend hit dice to heal, warlocks recover spell slots.

    Args:
        character: The character taking a short rest.
        hit_dice_to_spend: Number of hit dice the player wants to spend.

    Returns:
        Dict with hp_recovered, hit_dice_remaining, spell_slots_recovered, character.
    """
    dice_available = (
        character.hit_dice_remaining
        if character.hit_dice_remaining is not None
        else character.level
    )
    dice_to_use = min(hit_dice_to_spend, dice_available)
    die_size = HIT_DIE_SIZE.get(character.character_class, 8)
    con_mod = _con_modifier(character)

    hp_recovered = 0
    for _ in range(dice_to_use):
        roll = random.randint(1, die_size)  # noqa: S311
        healing = max(1, roll + con_mod)
        hp_recovered += healing

    new_hp = min(
        character.hit_points.current + hp_recovered,
        character.hit_points.maximum,
    )
    actual_recovery = new_hp - character.hit_points.current
    character.hit_points.current = new_hp
    character.hit_dice_remaining = dice_available - dice_to_use

    # Warlocks recover spell slots on short rest
    spell_slots_recovered: list[int] = []
    if (
        character.character_class == CharacterClass.WARLOCK
        and character.spellcasting
    ):
        for slot in character.spellcasting.spell_slots:
            if slot.used > 0:
                spell_slots_recovered.append(slot.level)
                slot.used = 0

    return {
        "hp_recovered": actual_recovery,
        "hit_dice_remaining": character.hit_dice_remaining,
        "spell_slots_recovered": spell_slots_recovered,
        "character": character,
    }


def calculate_long_rest(character: CharacterSheet) -> dict:
    """Apply long rest effects: full HP, all spell slots, half hit dice, reduce exhaustion.

    Args:
        character: The character taking a long rest.

    Returns:
        Dict with hp_recovered, hit_dice_remaining, exhaustion_level,
        spell_slots_recovered, character.
    """
    # Full HP recovery
    hp_recovered = (
        character.hit_points.maximum - character.hit_points.current
    )
    character.hit_points.current = character.hit_points.maximum

    # Recover all spell slots
    spell_slots_recovered: list[int] = []
    if character.spellcasting:
        for slot in character.spellcasting.spell_slots:
            if slot.used > 0:
                spell_slots_recovered.append(slot.level)
                slot.used = 0

    # Recover half total hit dice (minimum 1), capped at level
    dice_available = (
        character.hit_dice_remaining
        if character.hit_dice_remaining is not None
        else character.level
    )
    dice_to_recover = max(1, character.level // 2)
    character.hit_dice_remaining = min(
        dice_available + dice_to_recover, character.level
    )

    # Reduce exhaustion by 1
    character.exhaustion_level = max(0, character.exhaustion_level - 1)

    return {
        "hp_recovered": hp_recovered,
        "hit_dice_remaining": character.hit_dice_remaining,
        "exhaustion_level": character.exhaustion_level,
        "spell_slots_recovered": spell_slots_recovered,
        "character": character,
    }


@router.post("/game/rest", response_model=RestResponse)
async def rest(request: RestRequest) -> RestResponse:
    """Take a short or long rest."""
    try:
        from app.agents.scribe_agent import get_scribe

        scribe = get_scribe()
        character = await scribe.get_character(request.character_id)
        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found",
            )

        if request.rest_type == RestType.SHORT:
            result = calculate_short_rest(
                character, request.hit_dice_to_spend
            )
            message = (
                f"Short rest complete. Recovered {result['hp_recovered']} HP."
            )
        else:
            result = calculate_long_rest(character)
            message = (
                f"Long rest complete. Recovered {result['hp_recovered']} HP."
            )

        character_data = result["character"]
        if hasattr(character_data, "model_dump"):
            character_data = character_data.model_dump()
        await scribe.update_character(request.character_id, character_data)

        return RestResponse(
            success=True,
            message=message,
            hp_recovered=result["hp_recovered"],
            spell_slots_recovered=result.get("spell_slots_recovered", []),
            hit_dice_remaining=result["hit_dice_remaining"],
            exhaustion_level=result["character"].exhaustion_level,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Rest failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rest failed: {e}",
        ) from e
