"""Game session flow routes."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.agents.dungeon_master_agent import get_dungeon_master
from app.agents.narrator_agent import get_narrator
from app.agents.orchestration import (
    detect_agent_triggers,
    orchestrate_specialist_agents,
)
from app.agents.scribe_agent import get_scribe
from app.api.routes._shared import limiter
from app.api.routes.combat_routes import (
    process_combat_action,
    process_exploration_action,
    process_general_action,
    process_skill_check,
)
from app.models.game_models import (
    GameResponse,
    PlayerInput,
)
from app.services.campaign_service import campaign_service
from app.services.prompt_shield_service import prompt_shield_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])


@router.post("/input", response_model=GameResponse)
@limiter.limit("10/minute")
async def process_player_input(request: Request, player_input: PlayerInput):  # noqa: ARG001
    """Process player input and get game response."""
    try:
        # Check for prompt injection attacks before processing
        shield_result = await prompt_shield_service.check_user_input(
            player_input.message
        )
        if shield_result.attack_detected:
            logger.warning("Prompt injection attack detected in player input.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input blocked: potential prompt injection attack detected.",
            )

        # Try to get character and campaign context, but fallback gracefully
        character = None
        try:
            character = await get_scribe().get_character(player_input.character_id)
        except Exception as e:
            logger.warning(
                "Could not retrieve character %s: %s", player_input.character_id, str(e)
            )

        # Use fallback character info if character not found or error occurred
        if character is None:
            character = {
                "id": player_input.character_id,
                "name": "Adventurer",
                "class": "Fighter",
                "level": 1,
            }

        # Create context for the Dungeon Master agent
        context = {
            "character_id": player_input.character_id,
            "campaign_id": player_input.campaign_id,
            "character_name": character.get("name", "Adventurer"),
            "character_class": character.get("class", "Fighter"),
            "character_level": str(character.get("level", 1)),
        }

        # Process the input through the Dungeon Master agent
        dm_response = await get_dungeon_master().process_input(
            player_input.message, context
        )
        logger.info("DM response payload: %s", dm_response)

        # Auto-detect and invoke specialist agents based on context
        dm_message = dm_response.get("message", "")
        triggers = detect_agent_triggers(dm_message, player_input.message)
        specialist_results: dict[str, Any] = {}
        if triggers:
            logger.info("Orchestration triggers detected: %s", triggers)
            specialist_results = await orchestrate_specialist_agents(
                triggers=triggers,
                player_input=player_input.message,
                game_state=context,
                session_id=player_input.campaign_id or "",
            )
            logger.info("Specialist agent results: %s", list(specialist_results.keys()))

        # Merge specialist outputs into state_updates so the frontend
        # receives them alongside the DM narrative.
        merged_state = dm_response.get("state_updates", {})
        merged_state.update(specialist_results)

        # If combat was triggered by orchestration, surface it as combat_updates
        combat_updates = dm_response.get("combat_updates")
        if "combat_update" in specialist_results and combat_updates is None:
            combat_updates = specialist_results["combat_update"]

        # Transform the DM response to the GameResponse format
        images = []
        for visual in dm_response.get("visuals", []):
            if visual and "image_url" in visual and visual["image_url"]:
                images.append(visual["image_url"])

        return GameResponse(
            message=dm_message,
            images=images,
            state_updates=merged_state,
            combat_updates=combat_updates,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process input: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}",
        ) from None


@router.post("/campaign/generate-world", response_model=dict[str, Any])
@limiter.limit("10/minute")
async def generate_campaign_world(request: Request, campaign_data: dict[str, Any]):  # noqa: ARG001
    """Generate world description and setting for a new campaign."""
    try:
        campaign_name = campaign_data.get("name", "Unnamed Campaign")
        setting = campaign_data.get("setting", "fantasy")
        tone = campaign_data.get("tone", "heroic")
        homebrew_rules = campaign_data.get("homebrew_rules", [])

        # Generate world description based on inputs
        world_description = await generate_world_description(
            campaign_name, setting, tone, homebrew_rules
        )

        return {
            "world_description": world_description,
            "setting": setting,
            "tone": tone,
            "generated_elements": {
                "major_locations": generate_major_locations(setting),
                "notable_npcs": generate_notable_npcs(setting, tone),
                "plot_hooks": generate_plot_hooks(setting, tone),
                "world_lore": generate_world_lore(setting),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate campaign world: {str(e)}",
        ) from e


@router.post("/campaign/{campaign_id}/start-session", response_model=dict[str, Any])
async def start_game_session(campaign_id: str, session_data: dict[str, Any]):
    """Start a new game session for a campaign."""
    try:
        character_ids = session_data.get("character_ids", [])
        session_type = session_data.get(
            "type", "exploration"
        )  # exploration, combat, social

        # Initialize session state
        return {
            "session_id": f"session_{campaign_id}_{hash(str(character_ids))}",
            "campaign_id": campaign_id,
            "character_ids": character_ids,
            "type": session_type,
            "status": "active",
            "current_scene": generate_opening_scene(session_type),
            "available_actions": generate_available_actions(session_type),
            "scene_count": 1,
            "started_at": str(datetime.now()),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start game session: {str(e)}",
        ) from e


@router.post("/campaign/{campaign_id}/opening-narrative", response_model=dict[str, Any])
async def get_opening_narrative(campaign_id: str, request_data: dict[str, Any]):
    """Generate an atmospheric opening narrative for a new game session.

    Returns a scene description, quest hook, and 2-3 suggested actions based on
    the campaign setting and character context.
    """
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found",
            ) from None

        campaign_context = {
            "id": campaign_id,
            "name": campaign.name,
            "setting": campaign.setting,
            "tone": campaign.tone,
            "world_description": campaign.world_description or "",
        }
        character_context = request_data.get("character", {})

        opening = await get_narrator().generate_opening_narrative(
            campaign_context=campaign_context,
            character_context=character_context,
        )
        return opening

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate opening narrative: {str(e)}",
        ) from e


@router.post("/session/{session_id}/action", response_model=dict[str, Any])
async def process_player_action(session_id: str, action_data: dict[str, Any]):
    """Process a player action within a game session."""
    try:
        action_type = action_data.get("type", "general")
        description = action_data.get("description", "")
        character_id = action_data.get("character_id")
        dice_rolls = action_data.get("dice_rolls", [])

        # Process the action based on type
        if action_type == "combat":
            result = await process_combat_action(
                session_id, character_id, description, dice_rolls
            )
        elif action_type == "skill_check":
            result = await process_skill_check(
                session_id, character_id, description, dice_rolls
            )
        elif action_type == "exploration":
            result = await process_exploration_action(
                session_id, character_id, description
            )
        else:
            result = await process_general_action(session_id, character_id, description)

        # Update session state
        result["session_id"] = session_id
        result["timestamp"] = str(datetime.now())

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process player action: {str(e)}",
        ) from e


# Helper functions for campaign generation
async def generate_world_description(
    name: str, setting: str, tone: str, homebrew_rules: list[str]
) -> str:
    """Generate a world description for the campaign."""
    descriptions = {
        "fantasy": f"The realm of {name} is a land of magic and wonder, where ancient forests hide forgotten secrets and mighty kingdoms rise and fall with the tides of time.",
        "urban": f"The sprawling metropolis of {name} is a city of shadows and neon, where corporate towers pierce the smog-filled sky and danger lurks in every alley.",
        "post_apocalyptic": f"The wasteland of {name} stretches endlessly under a poisoned sky, where survivors eke out existence among the ruins of civilization.",
        "space": f"The star system of {name} spans multiple worlds and space stations, where alien civilizations and human colonies struggle for dominance among the stars.",
    }

    base_description = descriptions.get(
        setting, f"The world of {name} awaits your exploration."
    )

    if tone == "dark":
        base_description += (
            " Dark forces move in the shadows, and hope is a precious commodity."
        )
    elif tone == "heroic":
        base_description += " Heroes are needed to stand against the forces of darkness and protect the innocent."
    elif tone == "comedic":
        base_description += (
            " Adventure and mishaps await around every corner in this whimsical realm."
        )

    if homebrew_rules:
        base_description += (
            f" Special rules govern this realm: {', '.join(homebrew_rules)}."
        )

    return base_description


def generate_major_locations(setting: str) -> list[dict[str, str]]:
    """Generate major locations for the campaign world."""
    locations = {
        "fantasy": [
            {
                "name": "The Crystal Caverns",
                "type": "dungeon",
                "description": "Ancient caves filled with magical crystals and dangerous creatures.",
            },
            {
                "name": "Goldenheart City",
                "type": "city",
                "description": "A bustling trade hub ruled by merchant princes.",
            },
            {
                "name": "The Whispering Woods",
                "type": "wilderness",
                "description": "A mystical forest where the trees themselves are said to speak.",
            },
        ],
        "urban": [
            {
                "name": "The Undercity",
                "type": "district",
                "description": "A lawless underground network of tunnels and abandoned stations.",
            },
            {
                "name": "Corporate Plaza",
                "type": "building",
                "description": "The gleaming headquarters of the city's most powerful corporations.",
            },
            {
                "name": "The Neon Strip",
                "type": "district",
                "description": "A vibrant entertainment district that never sleeps.",
            },
        ],
    }
    return locations.get(setting, [])


def generate_notable_npcs(setting: str, tone: str) -> list[dict[str, str]]:
    """Generate notable NPCs for the campaign."""
    npcs = [
        {
            "name": "Sage Meridian",
            "role": "mentor",
            "description": "An wise old scholar with secrets of the past.",
        },
        {
            "name": "Captain Redhawk",
            "role": "ally",
            "description": "A brave leader who fights for justice.",
        },
        {
            "name": "The Shadow Broker",
            "role": "neutral",
            "description": "A mysterious figure who trades in information.",
        },
    ]

    if tone == "dark":
        npcs.append(
            {
                "name": "Lord Malachar",
                "role": "antagonist",
                "description": "A cruel tyrant who rules through fear.",
            }
        )
    elif tone == "comedic":
        npcs.append(
            {
                "name": "Bumblethorne the Accident-Prone",
                "role": "comic relief",
                "description": "A well-meaning wizard whose spells rarely work as intended.",
            }
        )

    return npcs


def generate_plot_hooks(setting: str, tone: str) -> list[str]:
    """Generate plot hooks for the campaign."""
    return [
        "Ancient artifacts have been stolen from the museum, and the thieves left behind only cryptic symbols.",
        "Strange disappearances plague the local area, and survivors speak of shadowy figures in the night.",
        "A powerful ally has gone missing, and their last known location was a dangerous territory.",
    ]


def generate_world_lore(setting: str) -> list[str]:
    """Generate world lore elements."""
    return [
        "Long ago, a great cataclysm reshaped the world, leaving scars that still influence events today.",
        "An ancient prophecy speaks of heroes who will arise in the realm's darkest hour.",
        "Hidden throughout the world are artifacts of immense power, sought by many but understood by few.",
    ]


def generate_opening_scene(session_type: str) -> str:
    """Generate an opening scene for a game session."""
    scenes = {
        "exploration": "You find yourselves at the entrance to an unexplored region, with adventure calling from beyond.",
        "combat": "Danger approaches! Ready your weapons and prepare for battle!",
        "social": "You enter a bustling tavern where information and intrigue flow as freely as the ale.",
    }
    return scenes.get(session_type, "Your adventure begins...")


def generate_available_actions(session_type: str) -> list[str]:
    """Generate available actions for a session type."""
    actions = {
        "exploration": [
            "Investigate the area",
            "Search for clues",
            "Move to a new location",
            "Rest and recover",
        ],
        "combat": [
            "Attack an enemy",
            "Cast a spell",
            "Use an item",
            "Move to a new position",
            "Defend",
        ],
        "social": [
            "Start a conversation",
            "Gather information",
            "Make a deal",
            "Intimidate someone",
        ],
    }
    return actions.get(session_type, ["Take an action"])
