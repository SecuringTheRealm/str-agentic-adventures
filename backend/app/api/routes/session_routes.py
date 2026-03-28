"""Game session flow routes."""

import logging
import uuid
from datetime import UTC, datetime
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
from app.auto_save import check_and_schedule_auto_save
from app.config import get_settings
from app.models.game_models import (
    GameResponse,
    PlayerInput,
)
from app.services.campaign_service import campaign_service
from app.services.game_context_service import build_game_context, build_state_updates
from app.services.prompt_shield_service import prompt_shield_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])


@router.post("/input", response_model=GameResponse)
@limiter.limit("30/minute")
async def process_player_input(  # noqa: ARG001
    request: Request, player_input: PlayerInput,
) -> GameResponse:
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

        # Build rich game context from campaign state, character stats,
        # equipment, and combat-derived values (Step 1 of #416).
        context = build_game_context(
            character_id=player_input.character_id,
            campaign_id=player_input.campaign_id,
            character_data=character,
        )

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

        # Build enriched state_updates with character HP, conditions,
        # equipped weapon, and spell slots (Step 5 of #416).
        merged_state = build_state_updates(context, dm_response)
        merged_state.update(specialist_results)

        # If combat was triggered by orchestration, surface it as combat_updates
        combat_updates = dm_response.get("combat_updates")
        if "combat_update" in specialist_results and combat_updates is None:
            combat_updates = specialist_results["combat_update"]

        # Auto-save: persist game state every N player interactions
        settings = get_settings()
        conversation_history = dm_response.get("conversation_history", [])
        auto_saved, interaction_count = check_and_schedule_auto_save(
            campaign_id=player_input.campaign_id or "",
            auto_save_interval=settings.auto_save_interval,
            conversation_history=conversation_history,
            character_data=character,
        )
        if auto_saved:
            from datetime import UTC, datetime

            merged_state["auto_saved"] = True
            merged_state["last_auto_save"] = datetime.now(UTC).isoformat()

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
@limiter.limit("30/minute")
async def generate_campaign_world(  # noqa: ARG001
    request: Request, campaign_data: dict[str, Any],
) -> dict[str, Any]:
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
async def start_game_session(campaign_id: str, session_data: dict[str, Any]) -> dict[str, Any]:
    """Start a new game session for a campaign."""
    try:
        character_ids = session_data.get("character_ids", [])
        session_type = session_data.get(
            "type", "exploration"
        )  # exploration, combat, social

        # Initialize session state
        return {
            "session_id": f"session_{campaign_id}_{uuid.uuid4().hex[:8]}",
            "campaign_id": campaign_id,
            "character_ids": character_ids,
            "type": session_type,
            "status": "active",
            "current_scene": generate_opening_scene(session_type),
            "available_actions": generate_available_actions(session_type),
            "scene_count": 1,
            "started_at": str(datetime.now(UTC)),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start game session: {str(e)}",
        ) from e


@router.post("/campaign/{campaign_id}/opening-narrative", response_model=dict[str, Any])
async def get_opening_narrative(campaign_id: str, request_data: dict[str, Any]) -> dict[str, Any]:
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

        return await get_narrator().generate_opening_narrative(
            campaign_context=campaign_context,
            character_context=character_context,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate opening narrative: {str(e)}",
        ) from e


@router.post("/session/{session_id}/action", response_model=dict[str, Any])
async def process_player_action(session_id: str, action_data: dict[str, Any]) -> dict[str, Any]:
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
        result["timestamp"] = str(datetime.now(UTC))

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


# ---------------------------------------------------------------------------
# Multiplayer Session Management Endpoints
# ---------------------------------------------------------------------------


@router.post("/session/create", response_model=dict[str, Any])
async def create_multiplayer_session(body: dict[str, Any]) -> dict[str, Any]:
    """Create a new multiplayer game session for a campaign."""
    from app.services.session_manager import session_manager

    campaign_id = body.get("campaign_id")
    if not campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="campaign_id is required",
        )
    try:
        return session_manager.create_session(campaign_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {e}",
        ) from e


@router.get("/session/{session_id}", response_model=dict[str, Any])
async def get_multiplayer_session(session_id: str) -> dict[str, Any]:
    """Get session details including participants."""
    from app.services.session_manager import session_manager

    result = session_manager.get_session(session_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return result


@router.get("/session/{session_id}/participants", response_model=list[dict[str, Any]])
async def list_session_participants(session_id: str) -> list[dict[str, Any]]:
    """List participants in a session."""
    from app.services.session_manager import session_manager

    return session_manager.get_participants(session_id)


@router.post("/session/{session_id}/turn/advance", response_model=dict[str, Any])
async def advance_session_turn(session_id: str) -> dict[str, Any]:
    """Advance to the next turn in a session."""
    from app.api.websocket_routes import broadcast_turn_advance
    from app.services.session_manager import session_manager

    try:
        next_character_id = session_manager.advance_turn(session_id)
        # Look up participant name for the broadcast
        participants = session_manager.get_participants(session_id)
        player_name = "Unknown"
        campaign_id: str | None = None
        for p in participants:
            if p["character_id"] == next_character_id:
                player_name = p["player_name"]
                break

        session_data = session_manager.get_session(session_id)
        if session_data:
            campaign_id = session_data.get("campaign_id")

        if campaign_id:
            await broadcast_turn_advance(campaign_id, next_character_id, player_name)

        return {
            "character_id": next_character_id,
            "player_name": player_name,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/session/{session_id}/end", response_model=dict[str, Any])
async def end_multiplayer_session(session_id: str) -> dict[str, Any]:
    """End a multiplayer game session."""
    from app.services.session_manager import session_manager

    try:
        return session_manager.end_session(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
