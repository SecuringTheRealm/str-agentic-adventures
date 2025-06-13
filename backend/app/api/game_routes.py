"""
API routes for the AI Dungeon Master application.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.game_models import (
    CreateCharacterRequest,
    PlayerInput,
    GameResponse,
    CharacterSheet,
    LevelUpRequest,
    SpellAttackBonusRequest,
    CreateCampaignRequest,
    CampaignUpdateRequest,
    CloneCampaignRequest,
    CampaignListResponse,
    AIAssistanceRequest,
    AIAssistanceResponse,
    AIContentGenerationRequest,
    AIContentGenerationResponse,
    Campaign,
    Spell,
    CharacterClass,
    ManageSpellsRequest,
    ManageSpellSlotsRequest,
    CastSpellRequest,
    SpellListRequest,
    ConcentrationRequest,
    SpellListResponse,
    SpellCastingResponse,
    ConcentrationCheckResponse,
    Equipment,
    ItemType,
    ItemRarity,
    EquipmentSlot,
    ManageEquipmentRequest,
    EncumbranceRequest,
    MagicalEffectsRequest,
    ItemCatalogRequest,
    EquipmentResponse,
    EncumbranceResponse,
    ItemCatalogResponse,
    MagicalEffectsResponse,
    NPC,
    NPCPersonality,
    NPCInteraction,
    CreateNPCRequest,
    UpdateNPCRequest,
    NPCInteractionRequest,
    GenerateNPCStatsRequest,
    NPCPersonalityRequest,
    NPCListResponse,
    NPCInteractionResponse,
    NPCStatsResponse,
)
from app.agents.dungeon_master_agent import get_dungeon_master
from app.agents.scribe_agent import get_scribe
from app.agents.combat_cartographer_agent import get_combat_cartographer
from app.agents.artist_agent import get_artist
from app.services.campaign_service import campaign_service

# Create a logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(tags=["game"])


@router.post("/character", response_model=CharacterSheet)
async def create_character(character_data: CreateCharacterRequest):
    """Create a new player character."""
    try:
        # Convert Pydantic model to dictionary for the agent
        character_dict = character_data.model_dump()

        # Rename character_class to class for the agent
        character_dict["class"] = character_dict.pop("character_class")

        # Create character via Scribe agent
        character_sheet = await get_scribe().create_character(character_dict)

        if "error" in character_sheet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=character_sheet["error"]
            )

        return character_sheet
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create character: {str(e)}",
        )


@router.get("/character/{character_id}", response_model=Dict[str, Any])
async def get_character(character_id: str):
    """Retrieve a character sheet by ID."""
    character = await get_scribe().get_character(character_id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )

    return character


@router.post("/campaign", response_model=Campaign)
async def create_campaign(campaign_data: CreateCampaignRequest):
    """Create a new campaign."""
    try:
        campaign = campaign_service.create_campaign(campaign_data)
        return campaign
    except ValueError as e:
        # Handle configuration errors specifically
        error_msg = str(e)
        if "Azure OpenAI configuration" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_msg
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.get("/campaigns", response_model=CampaignListResponse)
async def list_campaigns():
    """List all campaigns including templates and custom campaigns."""
    try:
        all_campaigns = campaign_service.list_campaigns()
        templates = campaign_service.get_templates()
        
        return CampaignListResponse(
            campaigns=all_campaigns,
            templates=templates
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}",
        )


@router.get("/campaign/templates")
async def get_campaign_templates():
    """Get pre-built campaign templates."""
    try:
        templates = campaign_service.get_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}",
        )


@router.get("/campaign/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get a specific campaign by ID."""
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found"
            )
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}",
        )


@router.put("/campaign/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, updates: CampaignUpdateRequest):
    """Update an existing campaign."""
    try:
        # Convert to dict, excluding None values
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid updates provided"
            )
        
        updated_campaign = campaign_service.update_campaign(campaign_id, update_data)
        if not updated_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found"
            )
        
        return updated_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        )


@router.post("/campaign/clone", response_model=Campaign)
async def clone_campaign(clone_data: CloneCampaignRequest):
    """Clone a template campaign for customization."""
    try:
        cloned_campaign = campaign_service.clone_campaign(
            clone_data.template_id,
            clone_data.new_name
        )
        
        if not cloned_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template campaign {clone_data.template_id} not found"
            )
        
        return cloned_campaign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone campaign: {str(e)}",
        )


@router.delete("/campaign/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a custom campaign (templates cannot be deleted)."""
    try:
        success = campaign_service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign {campaign_id} not found or cannot be deleted"
            )
        
        return {"message": "Campaign deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}",
        )


@router.post("/campaign/ai-assist", response_model=AIAssistanceResponse)
async def get_ai_assistance(request: AIAssistanceRequest):
    """Get AI assistance for campaign text enhancement."""
    try:
        # For now, provide simple suggestions based on context type
        # In a full implementation, this would use the AI agents
        suggestions = []
        enhanced_text = None
        
        if request.context_type == "setting":
            suggestions = [
                "Add more sensory details (sights, sounds, smells)",
                "Include potential conflict sources or tensions",
                "Describe the political or social climate",
                "Mention notable landmarks or geographical features"
            ]
        elif request.context_type == "description":
            suggestions = [
                "Expand on character motivations",
                "Add more dialogue or character interactions",
                "Include environmental details that set the mood",
                "Consider adding a plot twist or complication"
            ]
        elif request.context_type == "plot_hook":
            suggestions = [
                "Make the stakes more personal for the characters",
                "Add a time pressure element",
                "Include moral dilemmas or difficult choices",
                "Connect to character backstories"
            ]
        else:
            suggestions = [
                "Consider your target audience and tone",
                "Add specific details that engage the senses",
                "Think about cause and effect relationships",
                "Ensure consistency with your campaign world"
            ]
        
        # Simple text enhancement - in a full implementation this would use AI
        if request.text:
            enhanced_text = f"Enhanced: {request.text}"
        
        return AIAssistanceResponse(
            suggestions=suggestions,
            enhanced_text=enhanced_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI assistance: {str(e)}",
        )


@router.post("/campaign/ai-generate", response_model=AIContentGenerationResponse)
async def generate_ai_content(request: AIContentGenerationRequest):
    """Generate AI content based on a specific suggestion and current text."""
    try:
        from app.azure_openai_client import AzureOpenAIClient
        
        # Initialize the Azure OpenAI client
        openai_client = AzureOpenAIClient()
        
        # Create contextual prompt based on suggestion type and content
        system_prompt = f"""You are an expert D&D campaign writer helping to enhance campaign content.
Your task is to generate creative, contextual content based on a specific suggestion.
Campaign Tone: {request.campaign_tone}
Context Type: {request.context_type}
Current Text: {request.current_text or "None"}

The user wants you to: {request.suggestion}

Guidelines:
- Generate 2-4 sentences of high-quality content that fulfills the suggestion
- If there's existing text, build upon it naturally and coherently
- Match the campaign tone ({request.campaign_tone})
- Be specific and evocative, not generic
- Focus on details that enhance the game experience
- Don't repeat the suggestion text itself

Respond with ONLY the generated content, no explanations or meta-text."""

        user_prompt = f"Current field content: {request.current_text or '(empty)'}\n\nSuggestion to implement: {request.suggestion}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate content using Azure OpenAI
        generated_content = await openai_client.chat_completion(
            messages,
            temperature=0.7,
            max_tokens=300
        )
        
        if not generated_content or generated_content.strip() == "":
            return AIContentGenerationResponse(
                generated_content="",
                success=False,
                error="Failed to generate content"
            )
        
        return AIContentGenerationResponse(
            generated_content=generated_content.strip(),
            success=True
        )
        
    except Exception as e:
        return AIContentGenerationResponse(
            generated_content="",
            success=False,
            error=f"Failed to generate AI content: {str(e)}"
        )


@router.post("/generate-image", response_model=Dict[str, Any])
async def generate_image(image_request: Dict[str, Any]):
    """Generate an image based on the request details."""
    try:
        image_type = image_request.get("image_type")
        details = image_request.get("details", {})

        if image_type == "character_portrait":
            result = await get_artist().generate_character_portrait(details)
        elif image_type == "scene_illustration":
            result = await get_artist().illustrate_scene(details)
        elif image_type == "item_visualization":
            result = await get_artist().create_item_visualization(details)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {image_type}",
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}",
        )


@router.post("/battle-map", response_model=Dict[str, Any])
async def generate_battle_map(map_request: Dict[str, Any]):
    """Generate a battle map based on environment details."""
    try:
        environment = map_request.get("environment", {})
        combat_context = map_request.get("combat_context")

        battle_map = await get_combat_cartographer().generate_battle_map(
            environment, combat_context
        )

        return battle_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}",
        )


@router.post("/input", response_model=GameResponse)
async def process_player_input(player_input: PlayerInput):
    """Process player input and get game response."""
    try:
        # Try to get character and campaign context, but fallback gracefully
        character = None
        try:
            character = await get_scribe().get_character(player_input.character_id)
        except Exception as e:
            logger.warning(f"Could not retrieve character {player_input.character_id}: {str(e)}")
            # Use fallback character info
            character = {
                "id": player_input.character_id,
                "name": "Adventurer",
                "class": "Fighter", 
                "level": 1
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

        # Transform the DM response to the GameResponse format
        images = []
        for visual in dm_response.get("visuals", []):
            if visual and "image_url" in visual and visual["image_url"]:
                images.append(visual["image_url"])

        return GameResponse(
            message=dm_response.get("message", ""),
            images=images,
            state_updates=dm_response.get("state_updates", {}),
            combat_updates=dm_response.get("combat_updates"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process input: {str(e)}",
        )


@router.post("/character/{character_id}/level-up", response_model=Dict[str, Any])
async def level_up_character(character_id: str, level_up_data: LevelUpRequest):
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
        )


@router.post(
    "/character/{character_id}/award-experience", response_model=Dict[str, Any]
)
async def award_experience(character_id: str, experience_data: Dict[str, int]):
    """Award experience points to a character."""
    try:
        experience_points = experience_data.get("experience_points", 0)
        if experience_points <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Experience points must be greater than 0",
            )

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
        )


@router.get("/character/{character_id}/progression-info", response_model=Dict[str, Any])
async def get_progression_info(character_id: str):
    """Get progression information for a character."""
    try:
        character = await get_scribe().get_character(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

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
        )


# Dice rolling endpoints
@router.post("/dice/roll", response_model=Dict[str, Any])
async def roll_dice(dice_data: Dict[str, str]):
    """Roll dice using D&D notation."""
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        dice_notation = dice_data.get("notation", "1d20")
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
        )


@router.post("/dice/roll-with-character", response_model=Dict[str, Any])
async def roll_dice_with_character(roll_data: Dict[str, Any]):
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
        )


@router.post("/dice/manual-roll", response_model=Dict[str, Any])
async def input_manual_roll(manual_data: Dict[str, Any]):
    """Input a manual dice roll result."""
    try:
        from app.plugins.rules_engine_plugin import RulesEnginePlugin

        dice_notation = manual_data.get("notation", "1d20")
        result = manual_data.get("result")

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roll result is required",
            )

        rules_engine = RulesEnginePlugin()
        manual_result = rules_engine.input_manual_roll(dice_notation, result)

        return manual_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to input manual roll: {str(e)}",
        )


# Campaign creation and world generation endpoints
@router.post("/campaign/generate-world", response_model=Dict[str, Any])
async def generate_campaign_world(campaign_data: Dict[str, Any]):
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
        )


@router.post("/campaign/{campaign_id}/start-session", response_model=Dict[str, Any])
async def start_game_session(campaign_id: str, session_data: Dict[str, Any]):
    """Start a new game session for a campaign."""
    try:
        character_ids = session_data.get("character_ids", [])
        session_type = session_data.get(
            "type", "exploration"
        )  # exploration, combat, social

        # Initialize session state
        session_state = {
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

        return session_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start game session: {str(e)}",
        )


@router.post("/session/{session_id}/action", response_model=Dict[str, Any])
async def process_player_action(session_id: str, action_data: Dict[str, Any]):
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
        )


# Combat workflow endpoints
@router.post("/combat/initialize", response_model=Dict[str, Any])
async def initialize_combat(combat_data: Dict[str, Any]):
    """Initialize a new combat encounter."""
    try:
        session_id = combat_data.get("session_id")
        participants = combat_data.get("participants", [])
        environment = combat_data.get("environment", "standard")

        # Generate initiative order
        initiative_order = []
        for participant in participants:
            if participant.get("type") == "player":
                # Players roll initiative
                from app.plugins.rules_engine_plugin import RulesEnginePlugin

                rules_engine = RulesEnginePlugin()
                character = await get_scribe().get_character(
                    participant["character_id"]
                )
                if "error" not in character:
                    dex_modifier = (character["abilities"]["dexterity"] - 10) // 2
                    initiative_roll = rules_engine.roll_dice("1d20")
                    initiative_total = initiative_roll["total"] + dex_modifier
                else:
                    initiative_total = 10  # Default if character not found

                initiative_order.append(
                    {
                        "type": "player",
                        "id": participant["character_id"],
                        "name": participant.get("name", "Player"),
                        "initiative": initiative_total,
                    }
                )
            else:
                # NPCs/enemies get random initiative
                from random import randint

                initiative_order.append(
                    {
                        "type": "npc",
                        "id": participant["id"],
                        "name": participant.get("name", "NPC"),
                        "initiative": randint(1, 20)
                        + participant.get("dex_modifier", 0),
                    }
                )

        # Sort by initiative (highest first)
        initiative_order.sort(key=lambda x: x["initiative"], reverse=True)

        combat_state = {
            "combat_id": f"combat_{session_id}_{hash(str(participants))}",
            "session_id": session_id,
            "status": "active",
            "round": 1,
            "current_turn": 0,
            "initiative_order": initiative_order,
            "environment": environment,
            "battle_map_requested": True,
            "started_at": str(datetime.now()),
        }

        return combat_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize combat: {str(e)}",
        )


@router.post("/combat/{combat_id}/turn", response_model=Dict[str, Any])
async def process_combat_turn(combat_id: str, turn_data: Dict[str, Any]):
    """Process a single combat turn."""
    try:
        action_type = turn_data.get(
            "action", "attack"
        )  # attack, move, spell, item, etc.
        target_id = turn_data.get("target_id")
        character_id = turn_data.get("character_id")
        dice_result = turn_data.get("dice_result")

        # Process the combat action
        turn_result = {
            "combat_id": combat_id,
            "character_id": character_id,
            "action": action_type,
            "target_id": target_id,
            "success": False,
            "damage": 0,
            "description": "",
            "next_turn": True,
        }

        if action_type == "attack" and dice_result:
            # Process attack
            target_ac = turn_data.get("target_ac", 15)  # Default AC
            if dice_result["total"] >= target_ac:
                # Hit! Calculate damage
                damage_dice = turn_data.get("damage_dice", "1d6")
                from app.plugins.rules_engine_plugin import RulesEnginePlugin

                rules_engine = RulesEnginePlugin()
                damage_result = rules_engine.roll_dice(damage_dice)

                turn_result.update(
                    {
                        "success": True,
                        "damage": damage_result["total"],
                        "description": f"Attack hits for {damage_result['total']} damage!",
                        "damage_roll": damage_result,
                    }
                )
            else:
                turn_result.update(
                    {
                        "success": False,
                        "description": f"Attack misses (rolled {dice_result['total']} vs AC {target_ac})",
                    }
                )

        turn_result["timestamp"] = str(datetime.now())
        return turn_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process combat turn: {str(e)}",
        )


# Helper functions for campaign generation
async def generate_world_description(
    name: str, setting: str, tone: str, homebrew_rules: List[str]
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


def generate_major_locations(setting: str) -> List[Dict[str, str]]:
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


def generate_notable_npcs(setting: str, tone: str) -> List[Dict[str, str]]:
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


def generate_plot_hooks(setting: str, tone: str) -> List[str]:
    """Generate plot hooks for the campaign."""
    hooks = [
        "Ancient artifacts have been stolen from the museum, and the thieves left behind only cryptic symbols.",
        "Strange disappearances plague the local area, and survivors speak of shadowy figures in the night.",
        "A powerful ally has gone missing, and their last known location was a dangerous territory.",
    ]
    return hooks


def generate_world_lore(setting: str) -> List[str]:
    """Generate world lore elements."""
    lore = [
        "Long ago, a great cataclysm reshaped the world, leaving scars that still influence events today.",
        "An ancient prophecy speaks of heroes who will arise in the realm's darkest hour.",
        "Hidden throughout the world are artifacts of immense power, sought by many but understood by few.",
    ]
    return lore


def generate_opening_scene(session_type: str) -> str:
    """Generate an opening scene for a game session."""
    scenes = {
        "exploration": "You find yourselves at the entrance to an unexplored region, with adventure calling from beyond.",
        "combat": "Danger approaches! Ready your weapons and prepare for battle!",
        "social": "You enter a bustling tavern where information and intrigue flow as freely as the ale.",
    }
    return scenes.get(session_type, "Your adventure begins...")


def generate_available_actions(session_type: str) -> List[str]:
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


# Individual action processors
async def process_combat_action(
    session_id: str, character_id: str, description: str, dice_rolls: List[Dict]
) -> Dict[str, Any]:
    """Process a combat action."""
    return {
        "type": "combat",
        "description": description,
        "result": "Combat action processed - dice rolls applied",
        "dice_rolls": dice_rolls,
        "effects": ["Damage dealt", "Position changed"],
        "next_actions": ["Continue combat", "End turn"],
    }


async def process_skill_check(
    session_id: str, character_id: str, description: str, dice_rolls: List[Dict]
) -> Dict[str, Any]:
    """Process a skill check action."""
    success = (
        any(roll.get("total", 0) >= 15 for roll in dice_rolls) if dice_rolls else False
    )
    return {
        "type": "skill_check",
        "description": description,
        "result": "Success!" if success else "Failure!",
        "success": success,
        "dice_rolls": dice_rolls,
        "next_actions": ["Continue exploring", "Try a different approach"],
    }


async def process_exploration_action(
    session_id: str, character_id: str, description: str
) -> Dict[str, Any]:
    """Process an exploration action."""
    return {
        "type": "exploration",
        "description": description,
        "result": "You discover something interesting in your exploration.",
        "discoveries": [
            "A hidden passage",
            "An ancient inscription",
            "Signs of recent activity",
        ],
        "next_actions": ["Investigate further", "Move to a new area", "Rest here"],
    }


async def process_general_action(
    session_id: str, character_id: str, description: str
) -> Dict[str, Any]:
    """Process a general action."""
    return {
        "type": "general",
        "description": description,
        "result": "Your action has consequences that ripple through the world.",
        "effects": ["The situation changes", "New opportunities arise"],
        "next_actions": ["Continue the adventure", "Try something else"],
    }


# Spell System API Endpoints

@router.post("/character/{character_id}/spells", response_model=Dict[str, Any])
async def manage_character_spells(character_id: str, request: ManageSpellsRequest):
    """Manage known spells for a character."""
    try:
        # This would integrate with a character storage system
        # For now, returning a success response with the action performed
        return {
            "character_id": character_id,
            "action": request.action,
            "spell_ids": request.spell_ids,
            "success": True,
            "message": f"Successfully {request.action} spells for character {character_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage character spells: {str(e)}"
        )

@router.post("/character/{character_id}/spell-slots", response_model=Dict[str, Any])
async def manage_spell_slots(character_id: str, request: ManageSpellSlotsRequest):
    """Manage spell slot usage and recovery for a character."""
    try:
        # This would integrate with a character storage system
        # For now, returning a success response with the action performed
        return {
            "character_id": character_id,
            "action": request.action,
            "slot_level": request.slot_level,
            "count": request.count,
            "success": True,
            "message": f"Successfully {request.action} spell slots for character {character_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage spell slots: {str(e)}"
        )

@router.post("/combat/{combat_id}/cast-spell", response_model=SpellCastingResponse)
async def cast_spell_in_combat(combat_id: str, request: CastSpellRequest):
    """Cast spells during combat with effect resolution."""
    try:
        # Basic spell effects - in a real implementation this would be more sophisticated
        spell_effects = {
            "spell_name": request.spell_id,
            "spell_level": request.slot_level,
            "target_count": len(request.target_ids) if request.target_ids else 1,
            "effects": [f"Spell {request.spell_id} cast at level {request.slot_level}"],
            "combat_id": combat_id
        }
        
        return SpellCastingResponse(
            success=True,
            message=f"Spell cast successfully in combat {combat_id}",
            spell_effects=spell_effects,
            slot_used=True
        )
    except Exception as e:
        return SpellCastingResponse(
            success=False,
            message=f"Failed to cast spell: {str(e)}"
        )

@router.get("/spells/list", response_model=SpellListResponse)
async def get_spell_list(
    character_class: Optional[CharacterClass] = None,
    spell_level: Optional[int] = None,
    school: Optional[str] = None
):
    """Get available spells by class and level."""
    try:
        # This would query a spell database
        # For now, returning some sample spells
        sample_spells = [
            Spell(
                name="Magic Missile",
                level=1,
                school="Evocation",
                casting_time="1 action",
                range="120 feet",
                components="V, S",
                duration="Instantaneous",
                description="Three darts of magical force hit their targets.",
                available_classes=["wizard", "sorcerer"]
            ),
            Spell(
                name="Fireball",
                level=3,
                school="Evocation", 
                casting_time="1 action",
                range="150 feet",
                components="V, S, M",
                duration="Instantaneous",
                description="A bright flash of energy streaks toward a point within range.",
                available_classes=["wizard", "sorcerer"]
            ),
            Spell(
                name="Cure Wounds",
                level=1,
                school="Evocation",
                casting_time="1 action", 
                range="Touch",
                components="V, S",
                duration="Instantaneous",
                description="Restores hit points to a creature you touch.",
                available_classes=["cleric", "druid", "paladin", "ranger"]
            )
        ]
        
        # Filter spells based on parameters
        filtered_spells = sample_spells
        if character_class:
            filtered_spells = [s for s in filtered_spells if character_class.value in s.available_classes]
        if spell_level is not None:
            filtered_spells = [s for s in filtered_spells if s.level == spell_level]
        if school:
            filtered_spells = [s for s in filtered_spells if s.school.lower() == school.lower()]
        
        return SpellListResponse(
            spells=filtered_spells,
            total_count=len(filtered_spells)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get spell list: {str(e)}"
        )

@router.post("/spells/save-dc", response_model=Dict[str, Any])
async def calculate_spell_save_dc_endpoint(
    character_class: CharacterClass,
    level: int,
    spellcasting_ability_score: int
):
    """Calculate spell save DC for a character."""
    try:
        # Map character classes to their spellcasting abilities
        spellcasting_abilities = {
            "wizard": "intelligence",
            "artificer": "intelligence", 
            "cleric": "wisdom",
            "druid": "wisdom",
            "ranger": "wisdom",
            "bard": "charisma",
            "paladin": "charisma", 
            "sorcerer": "charisma",
            "warlock": "charisma"
        }
        
        # Get spellcasting ability for the class
        spellcasting_ability = spellcasting_abilities.get(character_class.value)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {character_class.value} is not a spellcasting class"
            )
        
        # Calculate ability modifier: (ability_score - 10) // 2
        ability_modifier = (spellcasting_ability_score - 10) // 2
        
        # Calculate proficiency bonus based on level
        proficiency_bonus = 2
        if level >= 17:
            proficiency_bonus = 6
        elif level >= 13:
            proficiency_bonus = 5
        elif level >= 9:
            proficiency_bonus = 4
        elif level >= 5:
            proficiency_bonus = 3
        
        # Spell save DC = 8 + proficiency bonus + ability modifier
        save_dc = 8 + proficiency_bonus + ability_modifier
        
        return {
            "save_dc": save_dc,
            "character_class": character_class.value,
            "level": level,
            "spellcasting_ability": spellcasting_ability,
            "spellcasting_ability_score": spellcasting_ability_score,
            "ability_modifier": ability_modifier,
            "proficiency_bonus": proficiency_bonus
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions to maintain proper status codes
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell save DC: {str(e)}"
        )

@router.post("/character/{character_id}/concentration", response_model=ConcentrationCheckResponse)
async def manage_concentration(character_id: str, request: ConcentrationRequest):
    """Manage spell concentration tracking for a character."""
    try:
        if request.action == "start":
            if not request.spell_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="spell_id required for starting concentration"
                )
            
            return ConcentrationCheckResponse(
                success=True,
                concentration_maintained=True,
                dc=10,
                spell_ended=False
            )
        
        elif request.action == "end":
            return ConcentrationCheckResponse(
                success=True,
                concentration_maintained=False,
                dc=0,
                spell_ended=True
            )
        
        elif request.action == "check":
            if request.damage_taken is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="damage_taken required for concentration check"
                )
            
            # Calculate concentration DC (half damage taken, minimum 10)
            dc = max(10, request.damage_taken // 2)
            
            # This would normally involve rolling a Constitution saving throw
            # For now, returning a simulated result
            import random
            roll_result = random.randint(1, 20) + 3  # Assuming +3 Constitution modifier
            maintained = roll_result >= dc
            
            return ConcentrationCheckResponse(
                success=True,
                concentration_maintained=maintained,
                dc=dc,
                roll_result=roll_result,
                spell_ended=not maintained
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return ConcentrationCheckResponse(
            success=False,
            concentration_maintained=False,
            dc=0,
            spell_ended=True
        )


@router.post("/spells/attack-bonus", response_model=Dict[str, Any])
async def calculate_spell_attack_bonus(request: SpellAttackBonusRequest):
    """Calculate spell attack bonus for a character."""
    try:
        # Map character classes to their spellcasting abilities
        spellcasting_abilities = {
            "wizard": "intelligence",
            "artificer": "intelligence", 
            "cleric": "wisdom",
            "druid": "wisdom",
            "ranger": "wisdom",
            "bard": "charisma",
            "paladin": "charisma", 
            "sorcerer": "charisma",
            "warlock": "charisma"
        }
        
        # Get spellcasting ability for the class
        spellcasting_ability = spellcasting_abilities.get(request.character_class)
        if not spellcasting_ability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Class {request.character_class.value} is not a spellcasting class"
            )
        
        # Calculate ability modifier: (ability_score - 10) // 2
        ability_modifier = (request.spellcasting_ability_score - 10) // 2
        
        # Calculate proficiency bonus based on level
        proficiency_bonus = 2
        if request.level >= 17:
            proficiency_bonus = 6
        elif request.level >= 13:
            proficiency_bonus = 5
        elif request.level >= 9:
            proficiency_bonus = 4
        elif request.level >= 5:
            proficiency_bonus = 3
        
        # Spell attack bonus = proficiency bonus + ability modifier
        spell_attack_bonus = proficiency_bonus + ability_modifier
        
        return {
            "character_class": request.character_class,
            "level": request.level,
            "spellcasting_ability": spellcasting_ability,
            "spellcasting_ability_score": request.spellcasting_ability_score,
            "ability_modifier": ability_modifier,
            "proficiency_bonus": proficiency_bonus,
            "spell_attack_bonus": spell_attack_bonus
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions to maintain proper status codes
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate spell attack bonus: {str(e)}"
        )

# Enhanced Inventory System API Endpoints

@router.post("/character/{character_id}/equipment", response_model=EquipmentResponse)
async def manage_equipment(character_id: str, request: ManageEquipmentRequest):
    """Equip/unequip items with stat effects."""
    try:
        # This would integrate with a character storage system
        # For now, simulate equipment management with basic stat effects
        
        sample_stat_effects = {
            "plate_armor": {"armor_class": 8, "stealth": -1},
            "magic_sword": {"attack_bonus": 1, "damage_bonus": 1},
            "ring_of_protection": {"armor_class": 1, "saving_throws": 1}
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
                detail=f"Invalid action: {request.action}"
            )
        
        return EquipmentResponse(
            success=True,
            message=message,
            stat_changes=stat_changes,
            armor_class_change=armor_class_change
        )
    except HTTPException:
        raise
    except Exception as e:
        return EquipmentResponse(
            success=False,
            message=f"Failed to manage equipment: {str(e)}"
        )

@router.get("/character/{character_id}/encumbrance", response_model=EncumbranceResponse)
async def get_encumbrance(character_id: str):
    """Calculate carrying capacity and weight."""
    try:
        # This would normally calculate from actual character data
        # For now, returning sample encumbrance data
        
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
            speed_penalty=speed_penalty
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate encumbrance: {str(e)}"
        )

@router.post("/items/magical-effects", response_model=MagicalEffectsResponse)
async def manage_magical_effects(request: MagicalEffectsRequest):
    """Apply magical item effects to character stats."""
    try:
        # Sample magical item effects
        magical_effects = {
            "cloak_of_elvenkind": {
                "stealth": 2,
                "perception": 2,
                "effects": ["Advantage on Dexterity (Stealth) checks", "Disadvantage on Perception checks against you"]
            },
            "gauntlets_of_ogre_power": {
                "strength": 19,  # Sets Strength to 19 if it's lower
                "effects": ["Strength becomes 19", "Advantage on Strength checks"]
            },
            "ring_of_mind_shielding": {
                "effects": ["Immune to charm", "Mind cannot be read", "Soul protected"]
            }
        }
        
        item_effects = magical_effects.get(request.item_id.lower(), {})
        
        if request.action == "apply":
            message = f"Applied magical effects of {request.item_id}"
            active_effects = item_effects.get("effects", [])
            stat_modifiers = {k: v for k, v in item_effects.items() if k != "effects"}
        elif request.action == "remove":
            message = f"Removed magical effects of {request.item_id}"
            active_effects = []
            stat_modifiers = {}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}"
            )
        
        return MagicalEffectsResponse(
            success=True,
            message=message,
            active_effects=active_effects,
            stat_modifiers=stat_modifiers
        )
    except HTTPException:
        raise
    except Exception as e:
        return MagicalEffectsResponse(
            success=False,
            message=f"Failed to manage magical effects: {str(e)}",
            active_effects=[],
            stat_modifiers={}
        )

@router.get("/items/catalog", response_model=ItemCatalogResponse)
async def get_item_catalog(
    item_type: Optional[ItemType] = None,
    rarity: Optional[ItemRarity] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
):
    """Browse available items with rarity and value information."""
    try:
        # Sample equipment catalog
        sample_items = [
            Equipment(
                name="Longsword",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.COMMON,
                weight=3.0,
                value=15,
                damage_dice="1d8",
                damage_type="slashing",
                properties=["versatile"]
            ),
            Equipment(
                name="Plate Armor",
                item_type=ItemType.ARMOR,
                rarity=ItemRarity.COMMON,
                weight=65.0,
                value=1500,
                armor_class=18,
                stat_modifiers={"stealth": -1}
            ),
            Equipment(
                name="Ring of Protection",
                item_type=ItemType.RING,
                rarity=ItemRarity.RARE,
                weight=0.1,
                value=3500,
                requires_attunement=True,
                is_magical=True,
                stat_modifiers={"armor_class": 1, "saving_throws": 1}
            ),
            Equipment(
                name="Flame Tongue",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.RARE,
                weight=3.0,
                value=5000,
                requires_attunement=True,
                is_magical=True,
                damage_dice="1d8",
                damage_type="slashing",
                special_abilities=["Fire damage", "Light source"],
                properties=["versatile"]
            ),
            Equipment(
                name="Thieves' Tools",
                item_type=ItemType.TOOL,
                rarity=ItemRarity.COMMON,
                weight=1.0,
                value=25
            )
        ]
        
        # Filter items based on parameters
        filtered_items = sample_items
        if item_type:
            filtered_items = [item for item in filtered_items if item.item_type == item_type]
        if rarity:
            filtered_items = [item for item in filtered_items if item.rarity == rarity]
        if min_value is not None:
            filtered_items = [item for item in filtered_items if item.value and item.value >= min_value]
        if max_value is not None:
            filtered_items = [item for item in filtered_items if item.value and item.value <= max_value]
        
        return ItemCatalogResponse(
            items=filtered_items,
            total_count=len(filtered_items)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get item catalog: {str(e)}"
        )

# Enhanced NPC Management API Endpoints

@router.post("/campaign/{campaign_id}/npcs", response_model=NPC)
async def create_campaign_npc(campaign_id: str, request: CreateNPCRequest):
    """Create and manage campaign NPCs."""
    try:
        # Generate basic personality traits if not provided
        import random
        
        sample_traits = [
            "Honest", "Deceitful", "Brave", "Cowardly", "Generous", "Greedy",
            "Kind", "Cruel", "Optimistic", "Pessimistic", "Curious", "Secretive"
        ]
        
        sample_mannerisms = [
            "Speaks softly", "Gestures wildly", "Never makes eye contact",
            "Constantly fidgets", "Uses elaborate vocabulary", "Speaks in short sentences"
        ]
        
        # Create NPC with generated personality
        personality = NPCPersonality(
            traits=random.sample(sample_traits, 2),
            mannerisms=random.sample(sample_mannerisms, 1),
            motivations=["Survive and prosper", "Help their family"]
        )
        
        # Generate basic abilities for the NPC
        from app.models.game_models import Abilities, HitPoints
        abilities = Abilities(
            strength=random.randint(8, 16),
            dexterity=random.randint(8, 16),
            constitution=random.randint(8, 16),
            intelligence=random.randint(8, 16),
            wisdom=random.randint(8, 16),
            charisma=random.randint(8, 16)
        )
        
        hit_points = HitPoints(
            current=random.randint(4, 12),
            maximum=random.randint(4, 12)
        )
        
        npc = NPC(
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
            story_role=request.story_role
        )
        
        return npc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NPC: {str(e)}"
        )

@router.get("/npc/{npc_id}/personality", response_model=NPCPersonality)
async def get_npc_personality(npc_id: str):
    """Get NPC personality traits and behaviors."""
    try:
        # This would normally retrieve from a database
        # For now, return a sample personality
        personality = NPCPersonality(
            traits=["Honest", "Brave"],
            ideals=["Justice", "Freedom"],
            bonds=["Loyal to the crown", "Protects the innocent"],
            flaws=["Quick to anger", "Overly trusting"],
            mannerisms=["Speaks with authority", "Always stands straight"],
            appearance="Tall and imposing with graying hair",
            motivations=["Maintain law and order", "Protect the city"]
        )
        
        return personality
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NPC personality: {str(e)}"
        )

@router.post("/npc/{npc_id}/interaction", response_model=NPCInteractionResponse)
async def log_npc_interaction(npc_id: str, request: NPCInteractionRequest):
    """Log and retrieve NPC interaction history."""
    try:
        # Create interaction record
        interaction = NPCInteraction(
            npc_id=npc_id,
            character_id=request.character_id,
            interaction_type=request.interaction_type,
            summary=request.summary,
            outcome=request.outcome,
            relationship_change=request.relationship_change
        )
        
        # This would normally be stored in a database
        # For now, return success response
        
        # Calculate new relationship level (simulated)
        import random
        current_level = random.randint(-50, 50)  # Would be retrieved from database
        new_level = max(-100, min(100, current_level + request.relationship_change))
        
        return NPCInteractionResponse(
            success=True,
            message=f"Interaction logged successfully for NPC {npc_id}",
            interaction_id=interaction.id,
            new_relationship_level=new_level
        )
    except Exception as e:
        return NPCInteractionResponse(
            success=False,
            message=f"Failed to log NPC interaction: {str(e)}",
            interaction_id=""
        )

@router.post("/npc/{npc_id}/generate-stats", response_model=NPCStatsResponse)
async def generate_npc_stats(npc_id: str, request: GenerateNPCStatsRequest):
    """Generate combat stats for NPCs dynamically."""
    try:
        import random
        
        level = request.level or 1
        role = request.role
        
        # Generate stats based on role and level
        stat_templates = {
            "civilian": {
                "hit_dice": "1d4",
                "armor_class_base": 10,
                "proficiency_bonus": 2,
                "abilities_mod": 0
            },
            "guard": {
                "hit_dice": "1d8",
                "armor_class_base": 16,
                "proficiency_bonus": 2,
                "abilities_mod": 2
            },
            "soldier": {
                "hit_dice": "1d10",
                "armor_class_base": 18,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 3
            },
            "spellcaster": {
                "hit_dice": "1d6",
                "armor_class_base": 12,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 4
            },
            "rogue": {
                "hit_dice": "1d8",
                "armor_class_base": 14,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 3
            }
        }
        
        template = stat_templates.get(role, stat_templates["civilian"])
        
        # Generate hit points
        hit_dice_num = int(template["hit_dice"].split("d")[1])
        hit_points = sum(random.randint(1, hit_dice_num) for _ in range(level))
        hit_points += level * 1  # Constitution modifier (assumed +1)
        
        # Generate abilities
        base_stat = 10 + template["abilities_mod"]
        abilities = {
            "strength": base_stat + random.randint(-2, 2),
            "dexterity": base_stat + random.randint(-2, 2),
            "constitution": base_stat + random.randint(-2, 2),
            "intelligence": base_stat + random.randint(-2, 2),
            "wisdom": base_stat + random.randint(-2, 2),
            "charisma": base_stat + random.randint(-2, 2)
        }
        
        # Role-specific stat adjustments
        if role == "soldier":
            abilities["strength"] += 2
            abilities["constitution"] += 2
        elif role == "spellcaster":
            abilities["intelligence"] += 3
            abilities["wisdom"] += 2
        elif role == "rogue":
            abilities["dexterity"] += 3
            abilities["charisma"] += 1
        elif role == "guard":
            abilities["strength"] += 1
            abilities["constitution"] += 1
        
        generated_stats = {
            "level": level,
            "hit_points": {
                "current": hit_points,
                "maximum": hit_points
            },
            "armor_class": template["armor_class_base"] + ((abilities["dexterity"] - 10) // 2),
            "proficiency_bonus": template["proficiency_bonus"],
            "abilities": abilities,
            "role": role,
            "challenge_rating": level / 2 if level > 1 else 0.25
        }
        
        return NPCStatsResponse(
            success=True,
            message=f"Generated {role} stats for level {level} NPC",
            generated_stats=generated_stats
        )
    except Exception as e:
        return NPCStatsResponse(
            success=False,
            message=f"Failed to generate NPC stats: {str(e)}",
            generated_stats={}
        )
