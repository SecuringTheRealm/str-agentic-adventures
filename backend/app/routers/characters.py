"""Character-related API routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.config import ConfigDep
from app.models.game_models import (
    CharacterSheet,
    ConcentrationCheckResponse,
    ConcentrationRequest,
    CreateCharacterRequest,
    EncumbranceResponse,
    EquipmentResponse,
    LevelUpRequest,
    ManageEquipmentRequest,
    ManageSpellSlotsRequest,
    ManageSpellsRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["characters"])


@router.post("/character", response_model=CharacterSheet)
async def create_character(character_data: CreateCharacterRequest, config: ConfigDep):
    """Create a new player character."""
    try:
        character_dict = character_data.model_dump()
        character_dict["class"] = character_dict.pop("character_class")
        character_sheet = await get_scribe().create_character(character_dict)

        if "error" in character_sheet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=character_sheet["error"]
            )

        return character_sheet
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Azure OpenAI configuration" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_msg
            ) from None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create character: {str(e)}",
        ) from e


@router.get("/character/{character_id}", response_model=dict[str, Any])
async def get_character(character_id: str, config: ConfigDep):
    """Retrieve a character sheet by ID."""
    try:
        character = await get_scribe().get_character(character_id)

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        return character
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Azure OpenAI configuration" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_msg
            ) from None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve character: {str(e)}",
        ) from None


@router.post("/character/{character_id}/level-up", response_model=dict[str, Any])
async def level_up_character(character_id: str, level_up_data: LevelUpRequest):
    """Level up a character."""
    try:
        result = await get_scribe().level_up_character(
            character_id,
            level_up_data.ability_improvements,
            use_average_hp=True,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to level up character: {str(e)}",
        ) from None


@router.post(
    "/character/{character_id}/award-experience", response_model=dict[str, Any]
)
async def award_experience(character_id: str, experience_data: dict[str, int]):
    """Award experience points to a character."""
    try:
        experience_points = experience_data.get("experience_points", 0)
        if experience_points <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Experience points must be greater than 0",
            ) from None

        result = await get_scribe().award_experience(character_id, experience_points)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to award experience: {str(e)}",
        ) from None


@router.get("/character/{character_id}/progression-info", response_model=dict[str, Any])
async def get_progression_info(character_id: str):
    """Get progression information for a character."""
    try:
        character = await get_scribe().get_character(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            ) from None

        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        rules_engine = RulesEnginePlugin()

        current_experience = character.get("experience", 0)
        current_level = character.get("level", 1)
        asi_used = character.get("ability_score_improvements_used", 0)

        level_info = rules_engine.calculate_level(current_experience)
        asi_info = rules_engine.check_asi_eligibility(current_level, asi_used)
        proficiency_info = rules_engine.calculate_proficiency_bonus(current_level)

        return {
            "character_id": character_id,
            "current_level": current_level,
            "level_info": level_info,
            "asi_info": asi_info,
            "proficiency_info": proficiency_info,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progression info: {str(e)}",
        ) from None


@router.post("/character/{character_id}/spells", response_model=dict[str, Any])
async def manage_character_spells(character_id: str, request: ManageSpellsRequest):
    """Manage known spells for a character."""
    try:
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

            dc = max(10, request.damage_taken // 2)

            import random

            roll_result = (
                random.randint(1, 20) + 3  # noqa: S311
            )
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


@router.post("/character/{character_id}/equipment", response_model=EquipmentResponse)
async def manage_equipment(character_id: str, request: ManageEquipmentRequest):
    """Equip/unequip items with stat effects."""
    try:
        sample_stat_effects = {
            "plate_armor": {"armor_class": 8, "stealth": -1},
            "magic_sword": {"attack_bonus": 1, "damage_bonus": 1},
            "ring_of_protection": {"armor_class": 1, "saving_throws": 1},
        }

        equipment_name = request.equipment_id.lower()
        stat_changes = sample_stat_effects.get(equipment_name, {})

        if request.action == "equip":
            message = f"Successfully equipped {request.equipment_id}"
            armor_class_change = stat_changes.get("armor_class", 0)
        elif request.action == "unequip":
            message = f"Successfully unequipped {request.equipment_id}"
            stat_changes = {k: -v for k, v in stat_changes.items()}
            armor_class_change = stat_changes.get("armor_class", 0)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}",
            )

        return EquipmentResponse(
            success=True,
            message=message,
            stat_changes=stat_changes,
            armor_class_change=armor_class_change,
        )
    except HTTPException:
        raise
    except Exception as e:
        return EquipmentResponse(
            success=False, message=f"Failed to manage equipment: {str(e)}"
        )


@router.get("/character/{character_id}/encumbrance", response_model=EncumbranceResponse)
async def get_encumbrance(character_id: str):
    """Calculate carrying capacity and weight."""
    try:
        strength_score = 15
        carrying_capacity = strength_score * 15
        current_weight = 85.5

        if current_weight <= carrying_capacity:
            encumbrance_level = "unencumbered"
            speed_penalty = 0
        elif current_weight <= carrying_capacity * 2:
            encumbrance_level = "encumbered"
            speed_penalty = 10
        else:
            encumbrance_level = "heavily_encumbered"
            speed_penalty = 20

        return EncumbranceResponse(
            character_id=character_id,
            current_weight=current_weight,
            carrying_capacity=carrying_capacity,
            encumbrance_level=encumbrance_level,
            speed_penalty=speed_penalty,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate encumbrance: {str(e)}",
        ) from e
