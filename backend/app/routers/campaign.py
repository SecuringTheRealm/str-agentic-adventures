"""Campaign-related API routes."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.agents.narrator_agent import get_narrator
from app.config import ConfigDep
from app.models.game_models import (
    NPC,
    Abilities,
    AIAssistanceRequest,
    AIAssistanceResponse,
    AIContentGenerationRequest,
    AIContentGenerationResponse,
    Campaign,
    CampaignListResponse,
    CampaignUpdateRequest,
    CloneCampaignRequest,
    CreateCampaignRequest,
    CreateNPCRequest,
    HitPoints,
    NPCPersonality,
)
from app.services.campaign_service import campaign_service

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["campaign"])


@router.post("/campaign", response_model=Campaign)
async def create_campaign(campaign_data: CreateCampaignRequest, config: ConfigDep) -> Campaign:
    """Create a new campaign."""
    try:
        return campaign_service.create_campaign(campaign_data)
    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if "Azure OpenAI configuration" in error_msg:
            logger.exception("Configuration error during campaign creation")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_msg
            ) from None
        logger.exception("Validation error during campaign creation")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except Exception as e:
        logger.exception("Unexpected error during campaign creation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        ) from None


@router.get("/campaigns", response_model=CampaignListResponse)
async def list_campaigns() -> CampaignListResponse:
    """List all campaigns including templates and custom campaigns."""
    try:
        all_campaigns = campaign_service.list_campaigns()
        templates = campaign_service.get_templates()

        return CampaignListResponse(campaigns=all_campaigns, templates=templates)
    except Exception as e:
        logger.exception("Error listing campaigns")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        ) from e


@router.get("/campaign/templates")
async def get_campaign_templates() -> dict[str, Any]:
    """Get pre-built campaign templates."""
    try:
        templates = campaign_service.get_templates()
        return {"templates": templates}
    except Exception as e:
        logger.exception("Error getting campaign templates")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}",
        ) from None


@router.get("/campaign/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str) -> Campaign:
    """Get a specific campaign by ID."""
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found",
            ) from None
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}",
        ) from None


@router.put("/campaign/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, updates: CampaignUpdateRequest) -> Campaign:
    """Update an existing campaign."""
    try:
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid updates provided",
            ) from None

        updated_campaign = campaign_service.update_campaign(campaign_id, update_data)
        if not updated_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found",
            )

        return updated_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        ) from None


@router.post("/campaign/clone", response_model=Campaign)
async def clone_campaign(clone_data: CloneCampaignRequest) -> Campaign:
    """Clone a template campaign for customization."""
    try:
        cloned_campaign = campaign_service.clone_campaign(
            clone_data.template_id, clone_data.new_name
        )

        if not cloned_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template campaign {clone_data.template_id} not found",
            )

        return cloned_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone campaign: {str(e)}",
        ) from None


@router.delete("/campaign/{campaign_id}")
async def delete_campaign(campaign_id: str) -> dict[str, str]:
    """Delete a custom campaign (templates cannot be deleted)."""
    try:
        success = campaign_service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found or cannot be deleted",
            ) from None

        return {"message": "Campaign deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}",
        ) from None


@router.post("/campaign/ai-assist", response_model=AIAssistanceResponse)
async def get_ai_assistance(request: AIAssistanceRequest) -> AIAssistanceResponse:
    """Get AI assistance for campaign text enhancement."""
    try:
        suggestions = []
        enhanced_text = None

        if request.context_type == "setting":
            suggestions = [
                "Add more sensory details (sights, sounds, smells)",
                "Include potential conflict sources or tensions",
                "Describe the political or social climate",
                "Mention notable landmarks or geographical features",
            ]
        elif request.context_type == "description":
            suggestions = [
                "Expand on character motivations",
                "Add more dialogue or character interactions",
                "Include environmental details that set the mood",
                "Consider adding a plot twist or complication",
            ]
        elif request.context_type == "plot_hook":
            suggestions = [
                "Make the stakes more personal for the characters",
                "Add a time pressure element",
                "Include moral dilemmas or difficult choices",
                "Connect to character backstories",
            ]
        else:
            suggestions = [
                "Consider your target audience and tone",
                "Add specific details that engage the senses",
                "Think about cause and effect relationships",
                "Ensure consistency with your campaign world",
            ]

        enhanced_text = None
        if request.text:
            text = request.text.strip()

            if request.context_type == "setting":
                enhanced_text = (
                    f"{text}\n\nThe air carries subtle hints of the"
                    " environment's character, while distant sounds suggest"
                    " the life and activity that defines this place."
                )
            elif request.context_type == "description":
                enhanced_text = (
                    f"{text}\n\nBeneath the surface details lies a sense of"
                    " deeper significance, as if each element serves a"
                    " purpose in the larger tapestry of the story."
                )
            elif request.context_type == "plot_hook":
                enhanced_text = (
                    f"{text}\n\nTime seems to be of the essence, and the"
                    " consequences of action\u2014or inaction\u2014weigh heavily"
                    " on the minds of those involved."
                )
            else:
                enhanced_text = (
                    f"{text}\n\nThis element resonates with potential,"
                    " offering opportunities for creative development"
                    " and meaningful narrative engagement."
                )

        return AIAssistanceResponse(
            suggestions=suggestions, enhanced_text=enhanced_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI assistance: {str(e)}",
        ) from e


@router.post("/campaign/ai-generate", response_model=AIContentGenerationResponse)
@limiter.limit("10/minute")
async def generate_ai_content(  # noqa: ARG001
    request: Request,
    request_body: AIContentGenerationRequest,
) -> AIContentGenerationResponse:
    """Generate AI content based on a specific suggestion and current text."""
    try:
        from app.azure_openai_client import azure_openai_client

        system_prompt = (
            "You are an expert D&D campaign writer helping"
            " to enhance campaign content.\n"
            "Your task is to generate creative, contextual"
            " content based on a specific suggestion.\n\n"
            "Guidelines:\n"
            "- Generate 2-4 sentences of high-quality"
            " content that fulfills the suggestion\n"
            "- If there's existing text, build upon it"
            " naturally and coherently\n"
            "- Match the campaign tone specified by the user\n"
            "- Be specific and evocative, not generic\n"
            "- Focus on details that enhance the game experience\n"
            "- Don't repeat the suggestion text itself\n\n"
            "Respond with ONLY the generated content, no explanations or meta-text."
        )

        user_prompt = (
            f"Campaign Tone: {request_body.campaign_tone}\n"
            f"Context Type: {request_body.context_type}\n"
            f"Current field content: {request_body.current_text or '(empty)'}\n\n"
            f"Suggestion to implement: {request_body.suggestion}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        generated_content = await azure_openai_client.chat_completion(
            messages, temperature=0.7, max_tokens=300
        )

        if not generated_content or generated_content.strip() == "":
            return AIContentGenerationResponse(
                generated_content="", success=False, error="Failed to generate content"
            )

        return AIContentGenerationResponse(
            generated_content=generated_content.strip(), success=True
        )

    except Exception as e:
        return AIContentGenerationResponse(
            generated_content="",
            success=False,
            error=f"Failed to generate AI content: {str(e)}",
        )


@router.post("/campaign/generate-world", response_model=dict[str, Any])
@limiter.limit("10/minute")
async def generate_campaign_world(request: Request, campaign_data: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    """Generate world description and setting for a new campaign."""
    try:
        campaign_name = campaign_data.get("name", "Unnamed Campaign")
        setting = campaign_data.get("setting", "fantasy")
        tone = campaign_data.get("tone", "heroic")
        homebrew_rules = campaign_data.get("homebrew_rules", [])

        world_description = await _generate_world_description(
            campaign_name, setting, tone, homebrew_rules
        )

        return {
            "world_description": world_description,
            "setting": setting,
            "tone": tone,
            "generated_elements": {
                "major_locations": _generate_major_locations(setting),
                "notable_npcs": _generate_notable_npcs(setting, tone),
                "plot_hooks": _generate_plot_hooks(setting, tone),
                "world_lore": _generate_world_lore(setting),
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
        session_type = session_data.get("type", "exploration")

        return {
            "session_id": f"session_{campaign_id}_{hash(str(character_ids))}",
            "campaign_id": campaign_id,
            "character_ids": character_ids,
            "type": session_type,
            "status": "active",
            "current_scene": _generate_opening_scene(session_type),
            "available_actions": _generate_available_actions(session_type),
            "scene_count": 1,
            "started_at": str(datetime.now()),
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


@router.post("/campaign/{campaign_id}/npcs", response_model=NPC)
async def create_campaign_npc(campaign_id: str, request: CreateNPCRequest) -> NPC:
    """Create and manage campaign NPCs."""
    try:
        import random

        sample_traits = [
            "Honest", "Deceitful", "Brave", "Cowardly", "Generous", "Greedy",
            "Kind", "Cruel", "Optimistic", "Pessimistic", "Curious", "Secretive",
        ]

        sample_mannerisms = [
            "Speaks softly", "Gestures wildly", "Never makes eye contact",
            "Constantly fidgets", "Uses elaborate vocabulary", "Speaks in short sentences",
        ]

        personality = NPCPersonality(
            traits=random.sample(sample_traits, 2),
            mannerisms=random.sample(sample_mannerisms, 1),
            motivations=["Survive and prosper", "Help their family"],
        )

        abilities = Abilities(
            strength=random.randint(8, 16),  # noqa: S311
            dexterity=random.randint(8, 16),  # noqa: S311
            constitution=random.randint(8, 16),  # noqa: S311
            intelligence=random.randint(8, 16),  # noqa: S311
            wisdom=random.randint(8, 16),  # noqa: S311
            charisma=random.randint(8, 16),  # noqa: S311
        )

        hit_points = HitPoints(
            current=random.randint(4, 12),  # noqa: S311
            maximum=random.randint(4, 12),  # noqa: S311
        )

        return NPC(
            name=request.name,
            race=request.race,
            gender=request.gender,
            age=request.age,
            occupation=request.occupation,
            location=request.location,
            campaign_id=campaign_id,
            personality=personality,
            abilities=abilities,
            hit_points=hit_points,
            armor_class=10 + ((abilities.dexterity - 10) // 2),
            importance=request.importance,
            story_role=request.story_role,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NPC: {str(e)}",
        ) from e


# ---------------------------------------------------------------------------
# Helper functions for campaign/world generation
# ---------------------------------------------------------------------------


async def _generate_world_description(
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


def _generate_major_locations(setting: str) -> list[dict[str, str]]:
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


def _generate_notable_npcs(setting: str, tone: str) -> list[dict[str, str]]:
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


def _generate_plot_hooks(setting: str, tone: str) -> list[str]:
    """Generate plot hooks for the campaign."""
    return [
        "Ancient artifacts have been stolen from the museum, and the thieves left behind only cryptic symbols.",
        "Strange disappearances plague the local area, and survivors speak of shadowy figures in the night.",
        "A powerful ally has gone missing, and their last known location was a dangerous territory.",
    ]


def _generate_world_lore(setting: str) -> list[str]:
    """Generate world lore elements."""
    return [
        "Long ago, a great cataclysm reshaped the world, leaving scars that still influence events today.",
        "An ancient prophecy speaks of heroes who will arise in the realm's darkest hour.",
        "Hidden throughout the world are artifacts of immense power, sought by many but understood by few.",
    ]


def _generate_opening_scene(session_type: str) -> str:
    """Generate an opening scene for a game session."""
    scenes = {
        "exploration": "You find yourselves at the entrance to an unexplored region, with adventure calling from beyond.",
        "combat": "Danger approaches! Ready your weapons and prepare for battle!",
        "social": "You enter a bustling tavern where information and intrigue flow as freely as the ale.",
    }
    return scenes.get(session_type, "Your adventure begins...")


def _generate_available_actions(session_type: str) -> list[str]:
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
