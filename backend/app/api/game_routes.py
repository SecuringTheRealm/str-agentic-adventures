"""
API routes for the AI Dungeon Master application.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from typing import Dict, Any, List, Optional

from app.models.game_models import (
    CreateCharacterRequest,
    CreateCampaignRequest,
    PlayerInput,
    GameResponse,
    CharacterSheet,
    Campaign,
    GenerateImageRequest,
    BattleMapRequest
)
from app.agents.dungeon_master_agent import dungeon_master
from app.agents.scribe_agent import scribe
from app.agents.narrator_agent import narrator
from app.agents.combat_mc_agent import combat_mc
from app.agents.combat_cartographer_agent import combat_cartographer
from app.agents.artist_agent import artist

router = APIRouter(tags=["game"])
logger = logging.getLogger(__name__)

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

@router.post("/campaign", response_model=Dict[str, Any])
async def create_campaign(campaign_data: Dict[str, Any]):
    """Create a new campaign."""
    try:
        campaign = await dungeon_master.create_campaign(campaign_data)

        if "error" in campaign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=campaign["error"]
            )

        return campaign
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.post("/generate-image", response_model=Dict[str, Any])
async def generate_image(image_request: Dict[str, Any]):
    """Generate an image based on the request details."""
    try:
        # Validate required fields
        image_type = image_request.get("image_type")
        if not image_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_type is required"
            )
        
        details = image_request.get("details", {})
        if not details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="details are required"
            )
        
        # Generate image based on type
        if image_type == "character_portrait":
            # Validate character portrait requirements
            if not details.get("name"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Character name is required for portrait generation"
                )
            result = await artist.generate_character_portrait(details)
        elif image_type == "scene_illustration":
            # Validate scene illustration requirements
            if not details.get("location"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Location is required for scene illustration"
                )
            result = await artist.illustrate_scene(details)
        elif image_type == "item_visualization":
            # Validate item visualization requirements
            if not details.get("name"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item name is required for item visualization"
                )
            result = await artist.create_item_visualization(details)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {image_type}. Supported types: character_portrait, scene_illustration, item_visualization"
            )

        # Check if generation was successful
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}"
        )

@router.post("/battle-map", response_model=Dict[str, Any])
async def generate_battle_map(map_request: Dict[str, Any]):
    """Generate a battle map based on environment details."""
    try:
        # Validate required fields
        environment = map_request.get("environment", {})
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="environment details are required"
            )
        
        # Validate environment has at least location
        if not environment.get("location"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="environment.location is required for battle map generation"
            )
        
        combat_context = map_request.get("combat_context")
        
        battle_map = await combat_cartographer.generate_battle_map(environment, combat_context)
        
        # Check if generation was successful
        if "error" in battle_map:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=battle_map["error"]
            )
        
        return battle_map
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in battle map generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}"
        )

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
        dm_response = await dungeon_master.process_input(player_input.message, context)

        # Transform the DM response to the GameResponse format
        images = []
        for visual in dm_response.get("visuals", []):
            if visual and "image_url" in visual and visual["image_url"]:
                images.append(visual["image_url"])

        return GameResponse(
            message=dm_response.get("message", ""),
            images=images,
            state_updates=dm_response.get("state_updates", {}),
            combat_updates=dm_response.get("combat_updates")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}"
        )
