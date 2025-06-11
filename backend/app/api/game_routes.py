"""
API routes for the AI Dungeon Master application.
"""
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
        image_type = image_request.get("image_type")
        details = image_request.get("details", {})
        
        if image_type == "character_portrait":
            result = await artist.generate_character_portrait(details)
        elif image_type == "scene_illustration":
            result = await artist.illustrate_scene(details)
        elif image_type == "item_visualization":
            result = await artist.create_item_visualization(details)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {image_type}"
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}"
        )

@router.post("/battle-map", response_model=Dict[str, Any])
async def generate_battle_map(map_request: Dict[str, Any]):
    """Generate a battle map based on environment details."""
    try:
        environment = map_request.get("environment", {})
        combat_context = map_request.get("combat_context")
        
        battle_map = await combat_cartographer.generate_battle_map(environment, combat_context)
        
        return battle_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}"
        )

@router.get("/battle-map/templates", response_model=Dict[str, Any])
async def get_map_templates():
    """Get available battle map templates."""
    try:
        templates = await combat_cartographer.get_map_templates()
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get map templates: {str(e)}"
        )

@router.post("/battle-map/{map_id}/update", response_model=Dict[str, Any])
async def update_battle_map(map_id: str, update_request: Dict[str, Any]):
    """Update a battle map with combat state."""
    try:
        combat_state = update_request.get("combat_state", {})
        
        updated_map = await combat_cartographer.update_map_with_combat_state(map_id, combat_state)
        
        if "error" in updated_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=updated_map["error"]
            )
        
        return updated_map
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update battle map: {str(e)}"
        )

@router.post("/battle-map/{map_id}/variation", response_model=Dict[str, Any])
async def generate_map_variation(map_id: str, variation_request: Dict[str, Any]):
    """Generate a variation of an existing battle map."""
    try:
        variation_type = variation_request.get("variation_type", "minor")
        
        variation_map = await combat_cartographer.generate_map_variation(map_id, variation_type)
        
        if "error" in variation_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=variation_map["error"]
            )
        
        return variation_map
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate map variation: {str(e)}"
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
