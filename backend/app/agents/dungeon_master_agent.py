"""
Dungeon Master Agent - The orchestrator agent that coordinates all other agents.
"""
import logging
from typing import Dict, Any, Tuple

import semantic_kernel as sk

from app.kernel_setup import kernel_manager
from app.agents.narrator_agent import narrator
from app.agents.scribe_agent import scribe
from app.agents.combat_mc_agent import combat_mc
from app.agents.combat_cartographer_agent import combat_cartographer
from app.agents.artist_agent import artist

# New imports for enhanced orchestration
from app.core.base_agent import BaseAgent
from app.core.orchestration import workflow_orchestrator, CampaignWorkflowBuilder
from app.core.task_allocation import task_allocator
from app.models.communication_models import (
    AgentCapability, AgentTask, TaskPriority
)

logger = logging.getLogger(__name__)

class DungeonMasterAgent(BaseAgent):
    """
    Dungeon Master Agent that acts as the orchestrator for all other agents.
    This is the primary user-facing agent that manages player interactions and conversation flow.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent with its own kernel instance."""
        super().__init__("dungeon_master", "orchestration")
        self.kernel = kernel_manager.create_kernel()
        self._register_plugins()
        
        # Game session tracking
        self.active_sessions = {}

    def _initialize_capabilities(self) -> None:
        """Initialize Dungeon Master capabilities."""
        self._capabilities = [
            AgentCapability(
                name="campaign_orchestration",
                description="Coordinate multiple agents for campaign creation",
                estimated_duration=60
            ),
            AgentCapability(
                name="input_analysis",
                description="Analyze player input and route to appropriate agents",
                estimated_duration=5
            ),
            AgentCapability(
                name="response_synthesis",
                description="Synthesize responses from multiple agents",
                estimated_duration=10
            ),
            AgentCapability(
                name="workflow_management",
                description="Manage complex multi-agent workflows",
                estimated_duration=30
            )
        ]

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
            self.kernel.add_plugin(narrative_memory, plugin_name="Memory")
            self.kernel.add_plugin(rules_engine, plugin_name="Rules")
            
            logger.info("Dungeon Master agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Dungeon Master agent plugins: {str(e)}")
            # Continue without failing - we'll have reduced functionality
            pass

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign using the enhanced workflow system.
        
        Args:
            campaign_data: Campaign settings and preferences
            
        Returns:
            Dict[str, Any]: The created campaign
        """
        try:
            campaign_id = campaign_data.get("id", f"campaign_{len(self.active_sessions) + 1}")
            
            # Create basic campaign structure
            campaign = {
                "id": campaign_id,
                "name": campaign_data.get("name", "Unnamed Adventure"),
                "setting": campaign_data.get("setting", "fantasy"),
                "tone": campaign_data.get("tone", "heroic"),
                "homebrew_rules": campaign_data.get("homebrew_rules", []),
                "characters": [],
                "session_log": [],
                "state": "creating"
            }
            
            # Store campaign
            self.active_sessions[campaign_id] = campaign
            
            # Create and execute campaign creation workflow
            workflow = CampaignWorkflowBuilder.create_campaign_creation_workflow(campaign_data)
            workflow_id = await workflow_orchestrator.create_workflow(workflow)
            
            # Store workflow ID with campaign for tracking
            campaign["workflow_id"] = workflow_id
            
            logger.info(f"Started campaign creation workflow {workflow_id} for campaign {campaign_id}")
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {"error": "Failed to create campaign"}

    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input using enhanced task allocation and coordination.

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
            
            # Route to appropriate handling based on input complexity
            if input_type == "combat" and context.get("combat_state") != "active":
                # Complex combat initiation - use workflow
                response = await self._handle_complex_combat_workflow(user_input, context, input_details)
                
            elif input_type == "narrative" and input_details.get("complexity", "simple") == "complex":
                # Complex narrative scenario - use task allocation
                response = await self._handle_complex_narrative_tasks(user_input, context, input_details)
                
            else:
                # Simple scenarios - direct agent calls (backward compatibility)
                response = await self._handle_simple_input(user_input, context, input_type, input_details)
            
            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                "message": "I'm sorry, I encountered an issue processing your request. Please try again.",
                "error": str(e)
            }
    
    async def _handle_complex_combat_workflow(self, user_input: str, context: Dict[str, Any], 
                                            input_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex combat scenarios using workflows."""
        try:
            # Create combat encounter workflow
            encounter_data = {
                "location": context.get("location", "unknown"),
                "encounter_type": input_details.get("encounter_type", "random"),
                "user_input": user_input,
                "character_id": context.get("character_id"),
                "campaign_id": context.get("campaign_id")
            }
            
            workflow = CampaignWorkflowBuilder.create_combat_encounter_workflow(encounter_data)
            workflow_id = await workflow_orchestrator.create_workflow(workflow)
            
            return {
                "message": "Setting up combat encounter...",
                "workflow_id": workflow_id,
                "state_updates": {"combat_state": "initializing"}
            }
            
        except Exception as e:
            logger.error(f"Error in complex combat workflow: {str(e)}")
            return {"message": "Failed to initiate combat encounter", "error": str(e)}
    
    async def _handle_complex_narrative_tasks(self, user_input: str, context: Dict[str, Any], 
                                            input_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex narrative scenarios using task allocation."""
        try:
            # Create multiple coordinated tasks
            tasks = []
            
            # Primary narrative task
            narrative_task = AgentTask(
                name="Process Narrative Action",
                description=f"Process complex narrative input: {user_input}",
                agent_type="narrative",
                priority=TaskPriority.HIGH,
                parameters={
                    "action": "process_action",
                    "user_input": user_input,
                    "context": context
                }
            )
            narrative_task_id = await task_allocator.submit_task(narrative_task)
            tasks.append(narrative_task_id)
            
            # Conditional illustration task
            if input_details.get("visual_elements", False):
                illustration_task = AgentTask(
                    name="Generate Scene Illustration",
                    description="Create visual representation of the scene",
                    agent_type="visual",
                    priority=TaskPriority.MEDIUM,
                    parameters={
                        "action": "illustrate_scene",
                        "scene_context": {"user_input": user_input}
                    },
                    dependencies=[narrative_task_id]
                )
                await task_allocator.submit_task(illustration_task)
            
            # Character update task if needed
            if input_details.get("character_changes", False):
                character_task = AgentTask(
                    name="Update Character",
                    description="Update character based on narrative changes",
                    agent_type="character",
                    priority=TaskPriority.MEDIUM,
                    parameters={
                        "action": "update_character",
                        "character_id": context.get("character_id"),
                        "changes": input_details.get("character_changes")
                    },
                    dependencies=[narrative_task_id]
                )
                await task_allocator.submit_task(character_task)
            
            return {
                "message": "Processing your action across multiple systems...",
                "tasks": tasks,
                "state_updates": {"processing": True}
            }
            
        except Exception as e:
            logger.error(f"Error in complex narrative tasks: {str(e)}")
            return {"message": "Failed to process complex narrative action", "error": str(e)}
    
    async def _handle_simple_input(self, user_input: str, context: Dict[str, Any], 
                                 input_type: str, input_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle simple input scenarios with direct agent calls."""
        response = {
            "message": "",
            "narration": "",
            "state_updates": {},
            "visuals": [],
            "combat_updates": None
        }
        
        # Route to appropriate agents based on input type (existing logic)
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
            response["message"] = "Your character has been updated."
            response["state_updates"] = {"character": character_result}
            
        elif input_type == "combat":
            # Handle active combat with Combat MC agent
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
        
        # If no input type was matched, provide generic response
        if not response["message"]:
            response["message"] = f"I understand your request '{user_input}'. How would you like to proceed?"

        return response
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action for the Dungeon Master agent.
        
        Args:
            action: The action to execute
            parameters: Action parameters
            
        Returns:
            Dict[str, Any]: Action result
        """
        try:
            if action == "create_campaign":
                return await self.create_campaign(parameters)
            elif action == "process_input":
                user_input = parameters.get("user_input", "")
                context = parameters.get("context", {})
                return await self.process_input(user_input, context)
            elif action == "orchestrate_workflow":
                workflow_data = parameters.get("workflow_data", {})
                workflow = CampaignWorkflowBuilder.create_campaign_creation_workflow(workflow_data)
                workflow_id = await workflow_orchestrator.create_workflow(workflow)
                return {"workflow_id": workflow_id, "status": "started"}
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}")
            return {"error": str(e)}
    
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
