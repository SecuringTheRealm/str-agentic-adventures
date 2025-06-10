"""
API routes for the AI Dungeon Master application.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from typing import Dict, Any, List, Optional

from app.models.game_models import (
    CreateCharacterRequest,
    PlayerInput,
    GameResponse,
    CharacterSheet,
    Campaign
)
from app.agents.dungeon_master_agent import dungeon_master
from app.agents.scribe_agent import scribe

router = APIRouter(tags=["game"])

@router.post("/character", response_model=CharacterSheet)
async def create_character(character_data: CreateCharacterRequest):
    """Create a new player character."""
    try:
        # Convert Pydantic model to dictionary for the agent
        character_dict = character_data.dict()

        # Rename character_class to class for the agent
        character_dict["class"] = character_dict.pop("character_class")

        # Create character via Scribe agent
        character_sheet = await scribe.create_character(character_dict)

        if "error" in character_sheet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=character_sheet["error"]
            )

        return character_sheet
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create character: {str(e)}"
        )

@router.get("/character/{character_id}", response_model=Dict[str, Any])
async def get_character(character_id: str):
    """Retrieve a character sheet by ID."""
    character = await scribe.get_character(character_id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )

    return character

@router.post("/input", response_model=GameResponse)
async def process_player_input(player_input: PlayerInput):
    """Process player input and get game response."""
    try:
        # Get character and campaign context
        character = await scribe.get_character(player_input.character_id)

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {player_input.character_id} not found"
            )

        # Create context for the Dungeon Master agent
        context = {
            "character_id": player_input.character_id,
            "campaign_id": player_input.campaign_id,
            "character_name": character.get("name", "Adventurer"),
            "character_class": character.get("class", "Fighter"),
            "character_level": str(character.get("level", 1))
        }

        # Process the input through the Dungeon Master agent
        response = await dungeon_master.process_input(player_input.message, context)

        # For now, return a simple response
        return GameResponse(
            message=response,
            state_updates={},
            combat_updates=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}"
        )
