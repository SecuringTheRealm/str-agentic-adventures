"""Spell-related API routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    CharacterClass,
    Spell,
    SpellAttackBonusRequest,
    SpellListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["spells"])


@router.get("/spells/list", response_model=SpellListResponse)
async def get_spell_list(
    character_class: CharacterClass | None = None,
    spell_level: int | None = None,
    school: str | None = None,
) -> dict[str, Any]:
    """Get available spells by class and level."""
    try:
        from app.srd_data import load_spells

        spell_data = load_spells()

        spells = []
        for spell_dict in spell_data:
            spell = Spell(
                id=spell_dict.get("id", ""),
                name=spell_dict.get("name", ""),
                level=spell_dict.get("level", 0),
                school=spell_dict.get("school", ""),
                casting_time=spell_dict.get("casting_time", ""),
                range=spell_dict.get("range", ""),
                components=spell_dict.get("components", ""),
                duration=spell_dict.get("duration", ""),
                description=spell_dict.get("description", ""),
                requires_concentration=spell_dict.get("requires_concentration", False),
                available_classes=spell_dict.get("available_classes", []),
            )
            spells.append(spell)

        filtered_spells = spells
        if character_class:
            filtered_spells = [
                s
                for s in filtered_spells
                if character_class.value in s.available_classes
            ]
        if spell_level is not None:
            filtered_spells = [s for s in filtered_spells if s.level == spell_level]
        if school:
            filtered_spells = [
                s for s in filtered_spells if s.school.lower() == school.lower()
            ]

        return SpellListResponse(
            spells=filtered_spells, total_count=len(filtered_spells)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get spell list: {str(e)}",
        ) from e


@router.post("/spells/save-dc", response_model=dict[str, Any])
async def calculate_spell_save_dc_endpoint(
    character_class: CharacterClass, level: int, spellcasting_ability_score: int
) -> dict[str, Any]:
    """Calculate spell save DC for a character."""
    try:
        spellcasting_abilities = {
            "wizard": "intelligence",
            "artificer": "intelligence",
            "cleric": "wisdom",
            "druid": "wisdom",
            "ranger": "wisdom",
            "bard": "charisma",
            "paladin": "charisma",
            "sorcerer": "charisma",
            "warlock": "charisma",
        }

        spellcasting_ability = spellcasting_abilities.get(character_class.value)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {character_class.value} is not a spellcasting class",
            )

        ability_modifier = (spellcasting_ability_score - 10) // 2

        proficiency_bonus = 2
        if level >= 17:
            proficiency_bonus = 6
        elif level >= 13:
            proficiency_bonus = 5
        elif level >= 9:
            proficiency_bonus = 4
        elif level >= 5:
            proficiency_bonus = 3

        save_dc = 8 + proficiency_bonus + ability_modifier

        return {
            "save_dc": save_dc,
            "character_class": character_class.value,
            "level": level,
            "spellcasting_ability": spellcasting_ability,
            "spellcasting_ability_score": spellcasting_ability_score,
            "ability_modifier": ability_modifier,
            "proficiency_bonus": proficiency_bonus,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell save DC: {str(e)}",
        ) from None


@router.post("/spells/attack-bonus", response_model=dict[str, Any])
async def calculate_spell_attack_bonus(request: SpellAttackBonusRequest) -> dict[str, Any]:
    """Calculate spell attack bonus for a character."""
    try:
        spellcasting_abilities = {
            "wizard": "intelligence",
            "artificer": "intelligence",
            "cleric": "wisdom",
            "druid": "wisdom",
            "ranger": "wisdom",
            "bard": "charisma",
            "paladin": "charisma",
            "sorcerer": "charisma",
            "warlock": "charisma",
        }

        spellcasting_ability = spellcasting_abilities.get(request.character_class)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {request.character_class.value} is not a spellcasting class",
            )

        ability_modifier = (request.spellcasting_ability_score - 10) // 2

        proficiency_bonus = 2
        if request.level >= 17:
            proficiency_bonus = 6
        elif request.level >= 13:
            proficiency_bonus = 5
        elif request.level >= 9:
            proficiency_bonus = 4
        elif request.level >= 5:
            proficiency_bonus = 3

        spell_attack_bonus = proficiency_bonus + ability_modifier

        return {
            "character_class": request.character_class,
            "level": request.level,
            "spellcasting_ability": spellcasting_ability,
            "spellcasting_ability_score": request.spellcasting_ability_score,
            "ability_modifier": ability_modifier,
            "proficiency_bonus": proficiency_bonus,
            "spell_attack_bonus": spell_attack_bonus,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell attack bonus: {str(e)}",
        ) from None
