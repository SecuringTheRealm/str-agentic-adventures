"""
Dungeon Master Agent - The orchestrator agent that coordinates all other agents.
"""

import logging
from typing import Dict, Any, Tuple
from datetime import datetime

# Note: Updated for newer Semantic Kernel version
# ToolManager import commented out as it's causing issues
# from semantic_kernel.tools.tool_manager import ToolManager

from app.kernel_setup import kernel_manager
from app.agents.narrator_agent import get_narrator
from app.agents.artist_agent import get_artist
from app.agents.scribe_agent import get_scribe
from app.models.game_models import NPCRole
# Temporarily commenting out other agent imports to fix SK compatibility
# from app.agents.combat_mc_agent import combat_mc
# from app.agents.combat_cartographer_agent import combat_cartographer

logger = logging.getLogger(__name__)


class DungeonMasterAgent:
    """
    Dungeon Master Agent that acts as the orchestrator for all other agents.
    This is the primary user-facing agent that manages player interactions and conversation flow.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent with its own kernel instance."""
        try:
            self.kernel = kernel_manager.create_kernel()
            # ToolManager initialization commented out as it's causing issues
            # self.tool_manager = ToolManager(self.kernel)
            self._register_plugins()

            # Game session tracking
            self.active_sessions = {}
        except Exception as e:
            # Check if this is a configuration error
            error_msg = str(e)
            if "validation errors for Settings" in error_msg and (
                "azure_openai" in error_msg or "openai" in error_msg
            ):
                raise ValueError(
                    "Azure OpenAI configuration is missing or invalid. "
                    "This agentic demo requires proper Azure OpenAI setup. "
                    "Please ensure the following environment variables are set: "
                    "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                    "AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
                ) from e
            else:
                # Re-raise other errors as-is
                raise

    def _register_plugins(self):
        """Register necessary plugins for the Dungeon Master agent."""
        try:
            # Import plugins
            from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            # Create plugin instances
            narrative_memory = NarrativeMemoryPlugin()
            rules_engine = RulesEnginePlugin()

            # Register plugins with the kernel using the new API
            self.kernel.add_plugin(narrative_memory, "Memory")
            self.kernel.add_plugin(rules_engine, "Rules")

            # Add tools to the tool manager
            # self.tool_manager.add_tool(narrative_memory.remember_fact)
            # self.tool_manager.add_tool(narrative_memory.recall_facts)
            # self.tool_manager.add_tool(rules_engine.roll_dice)

            logger.info("Dungeon Master agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Dungeon Master agent plugins: {str(e)}")
            # TODO: Implement proper fallback behavior when plugin registration fails
            # Consider graceful degradation or core DM functionality without full plugin suite
            pass

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign based on the provided settings.

        Args:
            campaign_data: Campaign settings and preferences

        Returns:
            Dict[str, Any]: The created campaign
        """
        try:
            campaign_id = campaign_data.get(
                "id", f"campaign_{len(self.active_sessions) + 1}"
            )

            # Create basic campaign
            campaign = {
                "id": campaign_id,
                "name": campaign_data.get("name", "Unnamed Adventure"),
                "setting": campaign_data.get("setting", "fantasy"),
                "tone": campaign_data.get("tone", "heroic"),
                "homebrew_rules": campaign_data.get("homebrew_rules", []),
                "characters": [],
                "session_log": [],
                "state": "created",
            }

            # Generate world concept with Narrator
            world_context = {"setting": campaign["setting"], "tone": campaign["tone"]}

            # Use the get_narrator function to get a narrator instance
            narrator_agent = get_narrator()
            world_description = await narrator_agent.describe_scene(world_context)
            campaign["world_description"] = world_description

            # Use the get_artist function to get an artist instance
            artist_agent = get_artist()
            world_art = await artist_agent.illustrate_scene(world_context)
            campaign["world_art"] = world_art

            # Store campaign
            self.active_sessions[campaign_id] = campaign

            return campaign

        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {"error": "Failed to create campaign"}

    async def create_campaign_npc(self, campaign_id: str, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new NPC for a campaign.

        Args:
            campaign_id: The campaign to add the NPC to
            npc_data: NPC creation data

        Returns:
            Dict[str, Any]: The created NPC data or error
        """
        try:
            # Check if campaign exists
            if campaign_id not in self.active_sessions:
                return {"error": "Campaign not found"}

            campaign = self.active_sessions[campaign_id]
            
            # Create NPC with unique ID
            npc_id = npc_data.get("id", f"npc_{len(campaign.get('npcs', {})) + 1}")
            
            # Generate stats if requested
            if npc_data.get("generate_stats", False):
                npc_data["stats"] = await self._generate_npc_stats(npc_data)
            
            # Create NPC object
            npc = {
                "id": npc_id,
                "name": npc_data.get("name"),
                "race": npc_data.get("race"),
                "role": npc_data.get("role", "neutral"),
                "description": npc_data.get("description"),
                "personality": npc_data.get("personality"),
                "location": npc_data.get("location"),
                "status": "alive",
                "stats": npc_data.get("stats"),
                "relationships": {},
                "notes": npc_data.get("notes"),
                "created_at": datetime.now().isoformat(),
                "last_interaction": None
            }

            # Add NPC to campaign
            if "npcs" not in campaign:
                campaign["npcs"] = {}
            campaign["npcs"][npc_id] = npc

            # Update campaign in storage
            self.active_sessions[campaign_id] = campaign

            return npc

        except Exception as e:
            logger.error(f"Error creating NPC: {str(e)}")
            return {"error": "Failed to create NPC"}

    async def get_campaign_npcs(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get all NPCs for a campaign.

        Args:
            campaign_id: The campaign ID

        Returns:
            Dict[str, Any]: The NPCs data or error
        """
        try:
            if campaign_id not in self.active_sessions:
                return {"error": "Campaign not found"}

            campaign = self.active_sessions[campaign_id]
            npcs = campaign.get("npcs", {})
            
            return {"npcs": npcs}

        except Exception as e:
            logger.error(f"Error getting NPCs: {str(e)}")
            return {"error": "Failed to get NPCs"}

    async def update_campaign_npc(self, campaign_id: str, npc_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing NPC in a campaign.

        Args:
            campaign_id: The campaign ID
            npc_id: The NPC ID to update
            update_data: Data to update

        Returns:
            Dict[str, Any]: The updated NPC data or error
        """
        try:
            if campaign_id not in self.active_sessions:
                return {"error": "Campaign not found"}

            campaign = self.active_sessions[campaign_id]
            npcs = campaign.get("npcs", {})
            
            if npc_id not in npcs:
                return {"error": "NPC not found"}

            # Update NPC fields
            npc = npcs[npc_id]
            for field, value in update_data.items():
                if field != "id":  # Don't allow ID changes
                    npc[field] = value

            # Update campaign in storage
            self.active_sessions[campaign_id] = campaign

            return npc

        except Exception as e:
            logger.error(f"Error updating NPC: {str(e)}")
            return {"error": "Failed to update NPC"}

    async def delete_campaign_npc(self, campaign_id: str, npc_id: str) -> Dict[str, Any]:
        """
        Delete an NPC from a campaign.

        Args:
            campaign_id: The campaign ID
            npc_id: The NPC ID to delete

        Returns:
            Dict[str, Any]: Success confirmation or error
        """
        try:
            if campaign_id not in self.active_sessions:
                return {"error": "Campaign not found"}

            campaign = self.active_sessions[campaign_id]
            npcs = campaign.get("npcs", {})
            
            if npc_id not in npcs:
                return {"error": "NPC not found"}

            # Remove NPC
            del npcs[npc_id]

            # Update campaign in storage
            self.active_sessions[campaign_id] = campaign

            return {"success": True, "message": f"NPC {npc_id} deleted"}

        except Exception as e:
            logger.error(f"Error deleting NPC: {str(e)}")
            return {"error": "Failed to delete NPC"}

    async def _generate_npc_stats(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate combat stats for an NPC.

        Args:
            npc_data: NPC data for context

        Returns:
            Dict[str, Any]: Generated stats
        """
        # Simple stat generation based on role
        role = npc_data.get("role", NPCRole.NEUTRAL)
        
        if role == NPCRole.ANTAGONIST:
            level = 5
            hp = {"current": 65, "maximum": 65}
            ac = 16
            abilities = {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 14
            }
        elif role == NPCRole.ALLY:
            level = 3
            hp = {"current": 27, "maximum": 27}
            ac = 14
            abilities = {
                "strength": 14,
                "dexterity": 13,
                "constitution": 14,
                "intelligence": 12,
                "wisdom": 14,
                "charisma": 13
            }
        else:  # neutral, merchant, etc.
            level = 1
            hp = {"current": 8, "maximum": 8}
            ac = 10
            abilities = {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }

        return {
            "level": level,
            "hit_points": hp,
            "armor_class": ac,
            "abilities": abilities
        }

    async def process_input(
        self, user_input: str, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Process user input and coordinate responses from specialized agents.

        Args:
            user_input: The player's input text
            context: Additional context information (game state, etc.)

        Returns:
            Dict[str, Any]: The response data including messages and any updates
        """
        if not context:
            context = {}

        logger.info(f"Processing player input: {user_input}")

        try:
            # Analyze the input type to determine which agents to invoke
            input_type, input_details = await self._analyze_input(user_input, context)

            # Prepare response object
            response = {
                "message": "",
                "narration": "",
                "state_updates": {},
                "visuals": [],
                "combat_updates": None,
            }

            # Route to appropriate agents based on input type
            if input_type == "narrative":
                # Handle narrative input with Narrator agent
                narrator_agent = get_narrator()
                narrative_result = await narrator_agent.process_action(
                    user_input, context
                )
                response["message"] = narrative_result.get("description", "")
                response["state_updates"] = narrative_result.get("state_updates", {})

                # Generate scene illustration if significant
                if narrative_result.get("significant_moment", False):
                    artist_agent = get_artist()
                    scene_art = await artist_agent.illustrate_scene(
                        narrative_result.get("scene_context", {})
                    )
                    response["visuals"].append(scene_art)

            elif input_type == "character":
                # Handle character-related input with Scribe agent
                scribe_agent = get_scribe()
                character_id = context.get("character_id")
                if character_id:
                    character_result = await scribe_agent.update_character(
                        character_id, input_details
                    )
                    response["message"] = "Your character has been updated."
                    response["state_updates"] = {"character": character_result}
                else:
                    response["message"] = "No character ID provided for update."

            elif input_type == "combat":
                # Combat functionality is temporarily disabled
                response["message"] = "Combat functionality is temporarily disabled."

                # Commented out due to missing combat agent implementation
                # Handle combat input with Combat MC agent
                # if context.get("combat_state") == "active":
                #     combat_mc_agent = get_combat_mc()
                #     combat_result = await combat_mc_agent.process_combat_action(
                #         user_input,
                #         context.get("combat_id"),
                #         context.get("character_id")
                #     )
                #     response["message"] = combat_result.get("description", "")
                #     response["combat_updates"] = combat_result.get("updates", {})
                #
                #     # Update battle map if needed
                #     if "map_id" in context:
                #         combat_cartographer_agent = get_combat_cartographer()
                #         updated_map = await combat_cartographer_agent.update_map_with_combat_state(
                #             context["map_id"],
                #             combat_result.get("updates", {})
                #         )
                #         response["visuals"].append(updated_map)
                # else:
                #     # Initiate combat if needed
                #     combat_context = {
                #         "location": context.get("location", "unknown"),
                #         "encounter_type": input_details.get("encounter_type", "random")
                #     }
                #     combat_mc_agent = get_combat_mc()
                #     encounter = await combat_mc_agent.create_encounter(
                #         {"members": [{"id": context.get("character_id")}]},
                #         combat_context
                #     )
                #
                #     # Generate battle map
                #     combat_cartographer_agent = get_combat_cartographer()
                #     battle_map = await combat_cartographer_agent.generate_battle_map(
                #         combat_context,
                #         encounter
                #     )
                #
                #     response["message"] = "Combat has begun! Roll for initiative!"
                #     response["combat_updates"] = encounter
                #     response["visuals"].append(battle_map)

            # If no input type was matched, provide generic response
            if not response["message"]:
                response["message"] = (
                    f"I understand your request '{user_input}'. How would you like to proceed?"
                )

            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                "message": "I'm sorry, I encountered an issue processing your request. Please try again.",
                "error": str(e),
            }

    async def _analyze_input(
        self, user_input: str, context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze user input to determine its type and extract relevant details.

        Args:
            user_input: The player's input text
            context: Current game context

        Returns:
            Tuple[str, Dict[str, Any]]: Input type and extracted details
        """
        try:
            # Enhanced input analysis using Azure OpenAI for better intent recognition
            from app.azure_openai_client import AzureOpenAIClient

            openai_client = AzureOpenAIClient()

            # Prepare analysis prompt for the AI
            analysis_prompt = f"""
            Analyze the following D&D player input and classify it into one of these categories:
            - "combat" (fighting, attacking, casting spells, initiative, combat actions)
            - "character" (inventory management, leveling up, equipment, abilities, character sheet updates)
            - "narrative" (exploration, roleplay, story actions, talking to NPCs)

            Player input: "{user_input}"
            Current context: {context.get("location", "unknown location")}

            Respond with JSON format:
            {{"category": "combat|character|narrative", "action_type": "specific_action", "confidence": 0.8}}
            """

            messages = [
                {
                    "role": "system",
                    "content": "You are a D&D game assistant that analyzes player intent. Always respond with valid JSON.",
                },
                {"role": "user", "content": analysis_prompt},
            ]

            # Get AI analysis
            response = await openai_client.chat_completion(
                messages, max_tokens=150, temperature=0.3
            )

            # Parse AI response
            import json

            try:
                analysis = json.loads(response.strip())
                category = analysis.get("category", "narrative")
                action_type = analysis.get("action_type", "general")
                confidence = analysis.get("confidence", 0.5)

                # If confidence is too low, fall back to keyword analysis
                if confidence < 0.6:
                    raise ValueError("Low confidence, using fallback")

                return category, {
                    "action_type": action_type,
                    "confidence": confidence,
                    "method": "ai_analysis",
                }

            except (json.JSONDecodeError, ValueError):
                # Fall back to keyword analysis if AI parsing fails
                logger.warning(
                    "AI analysis failed, falling back to keyword-based approach"
                )

        except Exception as e:
            logger.warning(
                f"Enhanced input analysis failed: {str(e)}, using fallback approach"
            )

        # Fallback: Enhanced keyword-based approach with better patterns
        input_lower = user_input.lower()

        # Combat indicators with more comprehensive patterns
        combat_keywords = [
            "attack",
            "fight",
            "cast spell",
            "initiative",
            "roll",
            "hit",
            "damage",
            "sword",
            "bow",
            "magic",
            "spell",
            "fireball",
            "heal",
            "defend",
            "dodge",
            "weapon",
            "armor class",
            "saving throw",
            "d20",
            "strike",
            "shoot",
        ]
        if any(term in input_lower for term in combat_keywords):
            # Determine specific combat action type
            if any(
                term in input_lower for term in ["cast", "spell", "magic", "fireball"]
            ):
                action_type = "spell_casting"
            elif any(
                term in input_lower
                for term in ["attack", "hit", "strike", "sword", "bow"]
            ):
                action_type = "physical_attack"
            elif any(term in input_lower for term in ["roll", "d20", "saving throw"]):
                action_type = "dice_roll"
            else:
                action_type = "combat_general"
            return "combat", {"action_type": action_type, "method": "keyword_analysis"}

        # Character management indicators
        character_keywords = [
            "inventory",
            "equip",
            "level up",
            "spell",
            "ability",
            "stats",
            "character sheet",
            "equipment",
            "items",
            "backpack",
            "armor",
            "experience",
            "skills",
            "proficiency",
        ]
        if any(term in input_lower for term in character_keywords):
            # Determine specific character action type
            if any(
                term in input_lower
                for term in ["inventory", "items", "equipment", "equip"]
            ):
                action_type = "inventory_management"
            elif any(
                term in input_lower for term in ["level up", "experience", "stats"]
            ):
                action_type = "character_advancement"
            elif any(term in input_lower for term in ["spell", "ability", "skills"]):
                action_type = "ability_management"
            else:
                action_type = "character_general"
            return "character", {
                "action_type": action_type,
                "method": "keyword_analysis",
            }

        # Movement and exploration indicators
        movement_keywords = [
            "go",
            "move",
            "walk",
            "run",
            "enter",
            "exit",
            "north",
            "south",
            "east",
            "west",
        ]
        if any(term in input_lower for term in movement_keywords):
            return "narrative", {
                "action_type": "movement",
                "method": "keyword_analysis",
            }

        # Social interaction indicators
        social_keywords = [
            "talk",
            "speak",
            "say",
            "tell",
            "ask",
            "persuade",
            "intimidate",
            "deceive",
        ]
        if any(term in input_lower for term in social_keywords):
            return "narrative", {
                "action_type": "social_interaction",
                "method": "keyword_analysis",
            }

        # Default to narrative with general exploration
        return "narrative", {"action_type": "exploration", "method": "keyword_analysis"}


# Lazy singleton instance
_dungeon_master = None


def get_dungeon_master():
    """Get the dungeon master instance, creating it if necessary."""
    global _dungeon_master
    if _dungeon_master is None:
        _dungeon_master = DungeonMasterAgent()
    return _dungeon_master


# For backward compatibility during import-time checks
dungeon_master = None
