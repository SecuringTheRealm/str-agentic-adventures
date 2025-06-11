"""
Dungeon Master Agent - The orchestrator agent that coordinates all other agents.
"""
import logging
from typing import Dict, Any, List, Tuple, Optional
import json

import semantic_kernel as sk
from semantic_kernel.functions import KernelPlugin

from app.kernel_setup import kernel_manager
# Temporarily comment out other agent imports while fixing semantic kernel issues
# from app.agents.narrator_agent import narrator
# from app.agents.scribe_agent import scribe
# from app.agents.combat_mc_agent import combat_mc
# from app.agents.combat_cartographer_agent import combat_cartographer
# from app.agents.artist_agent import artist

logger = logging.getLogger(__name__)

class DungeonMasterAgent:
    """
    Dungeon Master Agent that acts as the orchestrator for all other agents.
    This is the primary user-facing agent that manages player interactions and conversation flow.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self._register_plugins()
        
        # Game session tracking
        self.active_sessions = {}

    def _register_plugins(self):
        """Register necessary plugins for the Dungeon Master agent."""
        try:
            # Import plugins
            from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
            from app.plugins.rules_engine_plugin import RulesEnginePlugin
            
            # Create plugin instances
            narrative_memory = NarrativeMemoryPlugin()
            rules_engine = RulesEnginePlugin()
            
            # Register plugins with the kernel using new API
            memory_plugin = KernelPlugin.from_object("Memory", narrative_memory, description="Narrative memory management")
            rules_plugin = KernelPlugin.from_object("Rules", rules_engine, description="D&D 5e rules engine")
            
            self.kernel.add_plugin(memory_plugin)
            self.kernel.add_plugin(rules_plugin)
            
            logger.info("Dungeon Master agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Dungeon Master agent plugins: {str(e)}")
            # Continue without failing - we'll have reduced functionality
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
            campaign_id = campaign_data.get("id", f"campaign_{len(self.active_sessions) + 1}")
            
            # Create basic campaign
            campaign = {
                "id": campaign_id,
                "name": campaign_data.get("name", "Unnamed Adventure"),
                "setting": campaign_data.get("setting", "fantasy"),
                "tone": campaign_data.get("tone", "heroic"),
                "homebrew_rules": campaign_data.get("homebrew_rules", []),
                "characters": [],
                "session_log": [],
                "state": "created"
            }
            
            # Generate world concept with Narrator
            world_context = {
                "setting": campaign["setting"],
                "tone": campaign["tone"]
            }
            
            world_description = await narrator.describe_scene(world_context)
            campaign["world_description"] = world_description
            
            # Generate world concept art with Artist
            world_art = await artist.illustrate_scene(world_context)
            campaign["world_art"] = world_art
            
            # Store campaign
            self.active_sessions[campaign_id] = campaign
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {"error": "Failed to create campaign"}

    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
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
                "combat_updates": None
            }
            
            # Route to appropriate agents based on input type
            if input_type == "narrative":
                # Handle narrative input with Narrator agent
                narrative_result = await narrator.process_action(user_input, context)
                response["message"] = narrative_result.get("description", "")
                response["state_updates"] = narrative_result.get("state_updates", {})
                
                # Generate scene illustration if significant
                if narrative_result.get("significant_moment", False):
                    scene_art = await artist.illustrate_scene(narrative_result.get("scene_context", {}))
                    response["visuals"].append(scene_art)
                    
            elif input_type == "character":
                # Handle character-related input with Scribe agent
                character_result = await scribe.update_character(
                    context.get("character_id"), 
                    input_details
                )
                response["message"] = f"Your character has been updated."
                response["state_updates"] = {"character": character_result}
                
            elif input_type == "combat":
                # Handle combat input with Combat MC agent
                if context.get("combat_state") == "active":
                    combat_result = await combat_mc.process_combat_action(
                        user_input, 
                        context.get("combat_id"),
                        context.get("character_id")
                    )
                    response["message"] = combat_result.get("description", "")
                    response["combat_updates"] = combat_result.get("updates", {})
                    
                    # Update battle map if needed
                    if "map_id" in context:
                        updated_map = await combat_cartographer.update_map_with_combat_state(
                            context["map_id"],
                            combat_result.get("updates", {})
                        )
                        response["visuals"].append(updated_map)
                else:
                    # Initiate combat if needed
                    combat_context = {
                        "location": context.get("location", "unknown"),
                        "encounter_type": input_details.get("encounter_type", "random")
                    }
                    encounter = await combat_mc.create_encounter(
                        {"members": [{"id": context.get("character_id")}]},
                        combat_context
                    )
                    
                    # Generate battle map
                    battle_map = await combat_cartographer.generate_battle_map(
                        combat_context, 
                        encounter
                    )
                    
                    response["message"] = "Combat has begun! Roll for initiative!"
                    response["combat_updates"] = encounter
                    response["visuals"].append(battle_map)
            
            # If no input type was matched, provide generic response
            if not response["message"]:
                response["message"] = f"I understand your request '{user_input}'. How would you like to proceed?"

            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                "message": "I'm sorry, I encountered an issue processing your request. Please try again.",
                "error": str(e)
            }
    
    async def _analyze_input(self, user_input: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze user input to determine its type and extract relevant details.
        
        Args:
            user_input: The player's input text
            context: Current game context
        
        Returns:
            Tuple[str, Dict[str, Any]]: Input type and extracted details
        """
        # TODO: Implement proper input analysis with Semantic Kernel
        # For now, use a simple keyword-based approach
        
        input_lower = user_input.lower()
        
        # Check for combat indicators
        if any(term in input_lower for term in ["attack", "fight", "cast spell", "initiative", "roll"]):
            return "combat", {"action_type": "attack"}
            
        # Check for character update indicators
        if any(term in input_lower for term in ["inventory", "equip", "level up", "spell", "ability"]):
            return "character", {"update_type": "inventory"}
            
        # Default to narrative
        return "narrative", {}

# Singleton instance
dungeon_master = DungeonMasterAgent()
