"""Character CRUD and progression routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status

from app.agents.scribe_agent import get_scribe
from app.config import ConfigDep
from app.models.game_models import (
    AwardExperienceRequest,
    CharacterSheet,
    CreateCharacterRequest,
    EncumbranceResponse,
    EquipmentResponse,
    LevelUpRequest,
    ManageEquipmentRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["characters"])


@router.post("/character", response_model=CharacterSheet, status_code=status.HTTP_201_CREATED)
async def create_character(character_data: CreateCharacterRequest, config: ConfigDep) -> dict[str, Any]:
    """Create a new player character."""
    try:
        # Convert Pydantic model to dictionary for the agent
        character_dict = character_data.model_dump()

        # Rename character_class to class for the agent
        character_dict["class"] = character_dict.pop("character_class")

        # Create character via Scribe agent (handles fallback mode internally)
        character_sheet = await get_scribe().create_character(character_dict)

        if "error" in character_sheet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=character_sheet["error"]
            )

        return character_sheet
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Handle configuration errors specifically
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
async def get_character(character_id: str, config: ConfigDep) -> dict[str, Any]:
    """Retrieve a character sheet by ID."""
    try:
        # Get character from Scribe agent (handles fallback mode internally)
        character = await get_scribe().get_character(character_id)

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        return character
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Handle configuration errors specifically
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
async def level_up_character(character_id: str, level_up_data: LevelUpRequest) -> dict[str, Any]:
    """Level up a character."""
    try:
        # Level up the character via Scribe agent
        result = await get_scribe().level_up_character(
            character_id,
            level_up_data.ability_improvements,
            use_average_hp=True,  # Default to average HP
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
async def award_experience(character_id: str, experience_data: AwardExperienceRequest) -> dict[str, Any]:
    """Award experience points to a character."""
    try:
        result = await get_scribe().award_experience(character_id, experience_data.experience_points)

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
async def get_progression_info(character_id: str) -> dict[str, Any]:
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


@router.post("/character/{character_id}/equipment", response_model=EquipmentResponse)
async def manage_equipment(character_id: str, request: ManageEquipmentRequest) -> dict[str, Any]:
    """Equip/unequip items with stat effects."""
    try:
        # This would integrate with a character storage system
        # For now, simulate equipment management with basic stat effects

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
            # Reverse the stat changes for unequipping
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage equipment: {str(e)}",
        ) from e


@router.get("/character/{character_id}/encumbrance", response_model=EncumbranceResponse)
async def get_encumbrance(character_id: str, response: Response) -> dict[str, Any]:
    """Calculate carrying capacity and weight."""
    try:
        # Stub: returns hardcoded data until real character storage is wired up
        response.headers["X-Fallback"] = "true"

        # Simulate character strength-based carrying capacity
        strength_score = 15  # Would be retrieved from character data
        carrying_capacity = strength_score * 15  # 15 lbs per point of Strength
        current_weight = 85.5  # Would be calculated from actual inventory

        # Determine encumbrance level
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
