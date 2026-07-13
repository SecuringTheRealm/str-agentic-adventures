"""Character CRUD and progression routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.config import ConfigDep
from app.models.api_models import (
    AwardExperienceResult,
    CharacterGetResponse,
    LevelUpResult,
    ProgressionInfoResponse,
)
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
        logger.exception("Failed to create character")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.get("/character/{character_id}", response_model=CharacterGetResponse)
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
        logger.exception("Failed to retrieve character")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.post("/character/{character_id}/level-up", response_model=LevelUpResult)
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
    except Exception:
        logger.exception("Failed to level up character")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.post(
    "/character/{character_id}/award-experience", response_model=AwardExperienceResult
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
    except Exception:
        logger.exception("Failed to award experience")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.get(
    "/character/{character_id}/progression-info", response_model=ProgressionInfoResponse
)
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
        current_class = character.get("character_class", "fighter")
        asi_used = character.get("ability_score_improvements_used", 0)

        level_info = rules_engine.calculate_level(current_experience)
        asi_info = rules_engine.check_asi_eligibility(
            current_level, asi_used, current_class
        )
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
    except Exception:
        logger.exception("Failed to get progression info")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.post("/character/{character_id}/equipment", response_model=EquipmentResponse)
async def manage_equipment(character_id: str, request: ManageEquipmentRequest) -> dict[str, Any]:
    """Equip/unequip items against the character's real inventory."""
    try:
        if not request.slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="slot is required",
            )

        scribe = get_scribe()
        if request.action == "equip":
            result = await scribe.equip_item(
                character_id, request.equipment_id, request.slot.value
            )
            item = result.get("equipped_item")
        elif request.action == "unequip":
            result = await scribe.unequip_item(character_id, request.slot.value)
            item = result.get("unequipped_item")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}",
            )

        if result.get("error"):
            error_status = (
                status.HTTP_404_NOT_FOUND
                if "not found" in result["error"]
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(status_code=error_status, detail=result["error"])

        # Stat changes come from the real item's own effects data; unset for
        # items with no recorded effects (never fabricated).
        effects = (item or {}).get("effects", {})
        stat_changes = {
            stat: value for stat, value in effects.items() if isinstance(value, int)
        }
        if request.action == "unequip":
            stat_changes = {stat: -value for stat, value in stat_changes.items()}

        return EquipmentResponse(
            success=True,
            message=f"Successfully {request.action}ped {request.equipment_id}",
            stat_changes=stat_changes,
            armor_class_change=stat_changes.get("armor_class", 0),
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to manage equipment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.get("/character/{character_id}/encumbrance", response_model=EncumbranceResponse)
async def get_encumbrance(character_id: str) -> dict[str, Any]:
    """Calculate carrying capacity and weight from the character's real inventory."""
    try:
        result = await get_scribe().calculate_encumbrance(character_id)
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=result["error"]
            )

        return EncumbranceResponse(
            character_id=character_id,
            current_weight=result["total_weight"],
            carrying_capacity=result["carrying_capacity"],
            encumbrance_level=result["encumbrance_level"],
            speed_penalty=result["speed_penalty"],
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to calculate encumbrance")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None
