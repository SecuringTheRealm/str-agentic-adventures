"""Dice rolling routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.models.game_models import DiceRollRequest, ManualDiceRollRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dice"])


@router.post("/dice/roll", response_model=dict[str, Any])
async def roll_dice(request: DiceRollRequest) -> dict[str, Any]:
    """Roll dice using D&D notation."""
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        dice_notation = request.notation
        if not dice_notation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dice notation is required",
            )

        rules_engine = RulesEnginePlugin()
        result = rules_engine.roll_dice(dice_notation)

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
            detail=f"Failed to roll dice: {str(e)}",
        ) from None


@router.post("/dice/roll-with-character", response_model=dict[str, Any])
async def roll_dice_with_character(roll_data: dict[str, Any]) -> dict[str, Any]:
    """Roll dice with character context for skill checks."""
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        dice_notation = roll_data.get("notation", "1d20")
        character_id = roll_data.get("character_id")
        skill = roll_data.get("skill")

        if not character_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Character ID is required",
            )

        # Get character data
        character = await get_scribe().get_character(character_id)
        if "error" in character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
            )

        rules_engine = RulesEnginePlugin()
        result = rules_engine.roll_with_character(dice_notation, character, skill)

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
            detail=f"Failed to roll dice with character: {str(e)}",
        ) from None


@router.post("/dice/manual-roll", response_model=dict[str, Any])
async def input_manual_roll(body: ManualDiceRollRequest) -> dict[str, Any]:
    """Input a manual dice roll value.

    Send the physical dice value in the ``value`` field (the legacy
    ``result`` field is still accepted for backwards compatibility).
    """
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        rules_engine = RulesEnginePlugin()
        return rules_engine.input_manual_roll(body.notation, body.value)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to input manual roll: {str(e)}",
        ) from None
