"""Spell system routes."""

import logging
import random
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    CastSpellRequest,
    CharacterClass,
    ConcentrationCheckResponse,
    ConcentrationRequest,
    ManageSpellSlotsRequest,
    ManageSpellsRequest,
    Spell,
    SpellAttackBonusRequest,
    SpellCastingResponse,
    SpellListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["spells"])


@router.post("/character/{character_id}/spells", response_model=dict[str, Any])
async def manage_character_spells(character_id: str, request: ManageSpellsRequest):
    """Manage known spells for a character."""
    try:
        # This would integrate with a character storage system
        # For now, returning a success response with the action performed
        return {
            "character_id": character_id,
            "action": request.action,
            "spell_ids": request.spell_ids,
            "success": True,
            "message": f"Successfully {request.action} spells for character {character_id}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage character spells: {str(e)}",
        ) from e


@router.post("/character/{character_id}/spell-slots", response_model=dict[str, Any])
async def manage_spell_slots(character_id: str, request: ManageSpellSlotsRequest):
    """Manage spell slot usage and recovery for a character."""
    try:
        # This would integrate with a character storage system
        # For now, returning a success response with the action performed
        return {
            "character_id": character_id,
            "action": request.action,
            "slot_level": request.slot_level,
            "count": request.count,
            "success": True,
            "message": f"Successfully {request.action} spell slots for character {character_id}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage spell slots: {str(e)}",
        ) from e


@router.post("/combat/{combat_id}/cast-spell", response_model=SpellCastingResponse)
async def cast_spell_in_combat(combat_id: str, request: CastSpellRequest):
    """Cast spells during combat with sophisticated effect resolution."""
    try:
        # Load spell from database if available, otherwise use default effects
        spell_data = await _get_spell_data(request.spell_id)

        # Calculate spell effects based on spell data and casting level
        spell_effects = await _calculate_spell_effects(
            spell_data, request.slot_level, request.target_ids, combat_id
        )

        # Process concentration spells
        concentration_needed = spell_data.get("concentration", False) or spell_data.get(
            "requires_concentration", False
        )
        concentration_broken = False

        if concentration_needed:
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            rules_engine = RulesEnginePlugin()

            # Start concentration on the spell
            concentration_result = rules_engine.start_concentration(
                request.character_id,
                spell_data,
                duration_rounds=10,  # Default 1 minute duration
            )

            if not concentration_result.get("success", False):
                # If concentration failed to start, it could mean the spell doesn't require it
                # or there was an error, but we'll continue with the spell casting
                pass

        return SpellCastingResponse(
            success=True,
            message=f"Spell '{spell_data.get('name', request.spell_id)}' cast successfully in combat {combat_id}",
            spell_effects=spell_effects,
            concentration_broken=concentration_broken,
            slot_used=True,
        )
    except Exception as e:
        return SpellCastingResponse(
            success=False, message=f"Failed to cast spell: {str(e)}"
        )


async def _get_spell_data(spell_id: str) -> dict[str, Any]:
    """Get spell data from database or return default spell structure."""
    from app.database import get_session_context
    from app.models.db_models import Spell as DBSpell

    try:
        with get_session_context() as db:
            spell = db.query(DBSpell).filter(DBSpell.id == spell_id).first()
            if spell:
                return {
                    "id": spell.id,
                    "name": spell.name,
                    "level": spell.level,
                    "school": spell.school,
                    "damage_dice": spell.damage_dice,
                    "save_type": spell.save_type,
                    "concentration": spell.concentration,
                    "ritual": spell.ritual,
                    "components": spell.components,
                    "description": spell.description,
                    "higher_levels": spell.higher_levels,
                    **spell.data,
                }
    except Exception:
        pass  # Fall back to basic spell data

    # Default spell data for unknown spells
    return _get_default_spell_data(spell_id)


def _get_default_spell_data(spell_id: str) -> dict[str, Any]:
    """Get default spell data for common spells."""
    # Common D&D 5e spells with basic data
    default_spells = {
        "magic_missile": {
            "name": "Magic Missile",
            "level": 1,
            "school": "evocation",
            "damage_dice": "1d4+1",
            "save_type": None,
            "concentration": False,
            "auto_hit": True,
            "base_missiles": 3,
        },
        "fireball": {
            "name": "Fireball",
            "level": 3,
            "school": "evocation",
            "damage_dice": "8d6",
            "save_type": "dexterity",
            "concentration": False,
            "area_effect": True,
            "radius": 20,
        },
        "healing_word": {
            "name": "Healing Word",
            "level": 1,
            "school": "evocation",
            "healing_dice": "1d4",
            "save_type": None,
            "concentration": False,
            "range": 60,
            "bonus_action": True,
        },
        "shield": {
            "name": "Shield",
            "level": 1,
            "school": "abjuration",
            "ac_bonus": 5,
            "save_type": None,
            "concentration": False,
            "duration": "1 round",
            "reaction": True,
        },
        "cure_wounds": {
            "name": "Cure Wounds",
            "level": 1,
            "school": "evocation",
            "healing_dice": "1d8",
            "save_type": None,
            "concentration": False,
            "touch": True,
        },
    }

    return default_spells.get(
        spell_id,
        {
            "name": spell_id.replace("_", " ").title(),
            "level": 1,
            "school": "unknown",
            "concentration": False,
        },
    )


async def _calculate_spell_effects(
    spell_data: dict[str, Any],
    cast_level: int,
    target_ids: list[str] | None,
    combat_id: str,
) -> dict[str, Any]:
    """Calculate sophisticated spell effects based on spell data and level."""
    effects = {
        "spell_name": spell_data.get("name", "Unknown Spell"),
        "spell_level": cast_level,
        "base_level": spell_data.get("level", 1),
        "school": spell_data.get("school", "unknown"),
        "target_count": len(target_ids) if target_ids else 1,
        "combat_id": combat_id,
        "effects": [],
        "damage": None,
        "healing": None,
        "save_required": spell_data.get("save_type") is not None,
        "save_type": spell_data.get("save_type"),
        "concentration": spell_data.get("concentration", False),
    }

    upcast_levels = cast_level - spell_data.get("level", 1)

    # Calculate damage effects
    if spell_data.get("damage_dice"):
        base_damage = spell_data["damage_dice"]
        if upcast_levels > 0 and spell_data.get("higher_levels"):
            # Apply upcast damage scaling
            additional_dice = upcast_levels * _get_upcast_scaling(spell_data["name"])
            effects["damage"] = f"{base_damage} + {additional_dice}d6"
        else:
            effects["damage"] = base_damage
        effects["effects"].append(f"Deals {effects['damage']} damage")

    # Calculate healing effects
    if spell_data.get("healing_dice"):
        base_healing = spell_data["healing_dice"]
        if upcast_levels > 0:
            additional_healing = upcast_levels
            effects["healing"] = f"{base_healing} + {additional_healing}"
        else:
            effects["healing"] = base_healing
        effects["effects"].append(f"Heals {effects['healing']} hit points")

    # Special spell effects
    if spell_data.get("auto_hit"):
        effects["effects"].append("Automatically hits target(s)")

    if spell_data.get("area_effect"):
        radius = spell_data.get("radius", 10)
        effects["effects"].append(f"Area effect: {radius} foot radius")

    if spell_data.get("ac_bonus"):
        effects["effects"].append(f"Grants +{spell_data['ac_bonus']} AC")

    # Magic Missile special handling
    if spell_data.get("name") == "Magic Missile":
        base_missiles = spell_data.get("base_missiles", 3)
        total_missiles = base_missiles + upcast_levels
        effects["effects"].append(f"Fires {total_missiles} missiles")
        effects["damage"] = (
            f"{total_missiles} missiles, each dealing 1d4+1 force damage"
        )

    if upcast_levels > 0:
        effects["effects"].append(
            f"Cast at {cast_level} level (+{upcast_levels} levels)"
        )

    return effects


def _get_upcast_scaling(spell_name: str) -> int:
    """Get damage dice scaling for upcasting spells."""
    scaling_table = {
        "Fireball": 1,  # +1d6 per level
        "Lightning Bolt": 1,  # +1d6 per level
        "Scorching Ray": 1,  # +1 ray per level
        "Cure Wounds": 1,  # +1d8 per level
        "Healing Word": 1,  # +1d4 per level
    }
    return scaling_table.get(spell_name, 1)


@router.get("/spells/list", response_model=SpellListResponse)
async def get_spell_list(
    character_class: CharacterClass | None = None,
    spell_level: int | None = None,
    school: str | None = None,
):
    """Get available spells by class and level."""
    try:
        from app.srd_data import load_spells

        # Load spells from SRD data
        spell_data = load_spells()

        # Convert to Spell objects
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

        # Filter spells based on parameters
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
):
    """Calculate spell save DC for a character."""
    try:
        # Map character classes to their spellcasting abilities
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

        # Get spellcasting ability for the class
        spellcasting_ability = spellcasting_abilities.get(character_class.value)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {character_class.value} is not a spellcasting class",
            )

        # Calculate ability modifier: (ability_score - 10) // 2
        ability_modifier = (spellcasting_ability_score - 10) // 2

        # Calculate proficiency bonus based on level
        proficiency_bonus = 2
        if level >= 17:
            proficiency_bonus = 6
        elif level >= 13:
            proficiency_bonus = 5
        elif level >= 9:
            proficiency_bonus = 4
        elif level >= 5:
            proficiency_bonus = 3

        # Spell save DC = 8 + proficiency bonus + ability modifier
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
        # Re-raise HTTPExceptions to maintain proper status codes
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell save DC: {str(e)}",
        ) from None


@router.post(
    "/character/{character_id}/concentration", response_model=ConcentrationCheckResponse
)
async def manage_concentration(character_id: str, request: ConcentrationRequest):
    """Manage spell concentration tracking for a character."""
    try:
        if request.action == "start":
            if not request.spell_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="spell_id required for starting concentration",
                ) from None

            return ConcentrationCheckResponse(
                success=True, concentration_maintained=True, dc=10, spell_ended=False
            )

        if request.action == "end":
            return ConcentrationCheckResponse(
                success=True, concentration_maintained=False, dc=0, spell_ended=True
            )

        if request.action == "check":
            if request.damage_taken is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="damage_taken required for concentration check",
                )

            # Calculate concentration DC (half damage taken, minimum 10)
            dc = max(10, request.damage_taken // 2)

            # This would normally involve rolling a Constitution saving throw
            # For now, returning a simulated result
            roll_result = (
                random.randint(1, 20) + 3  # noqa: S311
            )  # Assuming +3 Constitution modifier
            maintained = roll_result >= dc

            return ConcentrationCheckResponse(
                success=True,
                concentration_maintained=maintained,
                dc=dc,
                roll_result=roll_result,
                spell_ended=not maintained,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {request.action}",
        )

    except HTTPException:
        raise
    except Exception:
        return ConcentrationCheckResponse(
            success=False, concentration_maintained=False, dc=0, spell_ended=True
        )


@router.post("/spells/attack-bonus", response_model=dict[str, Any])
async def calculate_spell_attack_bonus(request: SpellAttackBonusRequest):
    """Calculate spell attack bonus for a character."""
    try:
        # Map character classes to their spellcasting abilities
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

        # Get spellcasting ability for the class
        spellcasting_ability = spellcasting_abilities.get(request.character_class)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {request.character_class.value} is not a spellcasting class",
            )

        # Calculate ability modifier: (ability_score - 10) // 2
        ability_modifier = (request.spellcasting_ability_score - 10) // 2

        # Calculate proficiency bonus based on level
        proficiency_bonus = 2
        if request.level >= 17:
            proficiency_bonus = 6
        elif request.level >= 13:
            proficiency_bonus = 5
        elif request.level >= 9:
            proficiency_bonus = 4
        elif request.level >= 5:
            proficiency_bonus = 3

        # Spell attack bonus = proficiency bonus + ability modifier
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
        # Re-raise HTTPExceptions to maintain proper status codes
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell attack bonus: {str(e)}",
        ) from None
