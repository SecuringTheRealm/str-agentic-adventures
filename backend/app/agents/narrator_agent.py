"""
Narrator Agent - Manages campaign narrative and story elements.
"""

import logging
from typing import Any

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments

from app.kernel_setup import kernel_manager

logger = logging.getLogger(__name__)


class NarratorAgent:
    """
    Narrator Agent that manages campaign narrative, storylines, and descriptions.
    This agent is responsible for generating rich descriptions and determining narrative outcomes.
    """

    def __init__(self) -> None:
        """Initialize the Narrator agent with its own kernel instance."""
        # Initialize basic attributes first
        self._fallback_mode = False
        self.kernel: Kernel | None = None
        self.chat_service: AzureChatCompletion | None = None

        try:
            # Try to get the shared kernel from kernel manager
            self.kernel = kernel_manager.get_kernel()
            if self.kernel is None:
                # Kernel manager is in fallback mode
                self._fallback_mode = True
                logger.warning(
                    "Narrator agent operating in fallback mode - Azure OpenAI not configured"
                )
                self._initialize_fallback_components()
            else:
                # Get the chat service from the kernel
                self.chat_service = self.kernel.get_service(type=AzureChatCompletion)
                self._register_skills()
                logger.info("Narrator agent initialized with Semantic Kernel")

        except Exception as e:
            logger.warning(
                f"Failed to initialize Narrator agent with Semantic Kernel: {e}. "
                "Operating in fallback mode."
            )
            self._fallback_mode = True
            self._initialize_fallback_components()

    def _initialize_fallback_components(self) -> None:
        """Initialize fallback components when Azure OpenAI is not available."""
        self._fallback_mode = True
        # Basic fallback - no advanced narrative generation
        logger.info("Narrator agent initialized in fallback mode")

    def _register_skills(self) -> None:
        """Register necessary skills for the Narrator agent."""
        try:
            # Import plugins
            from app.plugins.narrative_generation_plugin import (
                NarrativeGenerationPlugin,
            )
            from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            # Create plugin instances
            narrative_memory = NarrativeMemoryPlugin()
            rules_engine = RulesEnginePlugin()
            narrative_generation = NarrativeGenerationPlugin()

            # Register plugins with the kernel using new API
            self.kernel.add_plugin(narrative_memory, "Memory")
            self.kernel.add_plugin(rules_engine, "Rules")
            self.kernel.add_plugin(narrative_generation, "Narrative")

            # Store references for direct access
            self.narrative_memory = narrative_memory
            self.narrative_generation = narrative_generation

            logger.info("Narrator agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Narrator agent plugins: {str(e)}")
            # Don't raise - enter fallback mode instead
            self._fallback_mode = True
            logger.warning(
                "Narrator agent entering fallback mode - using basic functionality without advanced plugins"
            )

    async def describe_scene(self, scene_context: dict[str, Any]) -> str:
        """
        Generate a rich description of a scene based on the provided context.

        Args:
            scene_context: Dictionary containing scene details

        Returns:
            str: Descriptive narrative of the scene
        """
        try:
            # Create kernel arguments
            arguments = KernelArguments()

            # Add scene context arguments
            for key, value in scene_context.items():
                if isinstance(value, str):
                    arguments[key] = value

            # Get campaign context and narrative state
            campaign_id = scene_context.get("campaign_id", "")
            if campaign_id and hasattr(self, "narrative_generation"):
                narrative_state = self.narrative_generation.get_narrative_state(
                    campaign_id
                )

                # Incorporate active story arcs into scene description
                if narrative_state.get("status") == "success":
                    active_arcs = narrative_state.get("active_story_arcs", [])
                    if active_arcs:
                        arguments["active_story_arcs"] = ", ".join(
                            [arc["title"] for arc in active_arcs]
                        )

            # Generate enhanced scene description
            location = scene_context.get("location", "an unknown place")
            time = scene_context.get("time", "an indeterminate time")
            mood = scene_context.get("mood", "mysterious")

            # Check for relevant memories to enhance description
            if hasattr(self, "narrative_memory"):
                location_memories = self.narrative_memory.recall_facts("", "location")
                if (
                    location_memories.get("status") == "success"
                    and location_memories["facts"]
                ):
                    # Use memory to enrich location description
                    relevant_facts = [
                        f["content"] for f in location_memories["facts"][:2]
                    ]
                    if relevant_facts:
                        arguments["location_history"] = ". ".join(relevant_facts)

            # Generate contextual description based on narrative state
            base_description = f"You find yourself in {location} during {time}."

            # Add atmospheric details based on mood and active story arcs
            if mood == "tense":
                atmosphere = " The air crackles with tension, and shadows seem to move of their own accord."
            elif mood == "peaceful":
                atmosphere = " A sense of calm pervades the area, offering a momentary respite from your adventures."
            elif mood == "mysterious":
                atmosphere = " Mystery hangs in the air like a thick fog, hinting at secrets yet to be discovered."
            else:
                atmosphere = " The atmosphere is charged with possibility as your adventure continues."

            # Add story arc context if available
            arc_context = ""
            if arguments.get("active_story_arcs"):
                arc_context = f" Your ongoing adventures in {arguments['active_story_arcs']} weigh on your mind."

            # Combine elements for rich description
            full_description = base_description + atmosphere + arc_context

            # Record this scene in memory
            if hasattr(self, "narrative_memory") and campaign_id:
                self.narrative_memory.record_event(
                    f"Scene described: {location}",
                    location,
                    scene_context.get("characters", ""),
                    3,
                )

            # Enhance description with Semantic Kernel if available
            if not getattr(self, "_fallback_mode", False) and self.chat_service:
                chat_history = ChatHistory()
                chat_history.add_system_message("You are a world class game narrator.")
                chat_history.add_user_message(full_description)

                settings = PromptExecutionSettings(temperature=0.7)
                try:
                    response = await self.chat_service.get_chat_message_contents(
                        chat_history=chat_history,
                        settings=settings,
                    )
                    return str(response[0]) if response else full_description
                except Exception as error:  # pragma: no cover - fallback path
                    logger.error("AI enhancement failed: %s", error)
                    return full_description
            else:
                # Fallback mode - return basic description
                return full_description

        except Exception as e:
            logger.error(f"Error generating scene description: {str(e)}")
            return (
                "The scene before you is still taking shape in the mists of creation."
            )

    async def process_action(
        self, action: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process a player action and determine narrative outcome.

        Args:
            action: The action the player is attempting
            context: The current game context

        Returns:
            Dict[str, Any]: The outcome of the action, including success/failure, description, and any updates to game state
        """
        try:
            campaign_id = context.get("campaign_id", "")
            character_id = context.get("character_id", "")

            # Generate appropriate narrative choices if this is a decision point
            if hasattr(self, "narrative_generation"):
                # Determine choice type based on action context
                choice_type = "general"
                if any(
                    word in action.lower() for word in ["fight", "attack", "combat"]
                ):
                    choice_type = "combat"
                elif any(
                    word in action.lower()
                    for word in ["talk", "speak", "persuade", "negotiate"]
                ):
                    choice_type = "social"
                elif any(
                    word in action.lower()
                    for word in ["explore", "investigate", "search"]
                ):
                    choice_type = "exploration"

                # Generate choices for this situation
                choices_result = self.narrative_generation.generate_choices(
                    situation=action,
                    context=str(context),
                    choice_type=choice_type,
                    num_choices=3,
                )

                # Advance the narrative based on the action
                advance_result = self.narrative_generation.advance_narrative(
                    campaign_id=campaign_id,
                    current_situation=action,
                    trigger_data=f'{{"action": "{action}", "character_id": "{character_id}"}}',
                )

                # Determine success and consequences
                success = True
                consequences = {}
                description = f"You attempt to {action}."

                # Add narrative outcomes based on story progression
                if advance_result.get("status") == "success":
                    activated_points = advance_result.get("activated_plot_points", [])
                    if activated_points:
                        description += " Your action triggers significant developments in the story."
                        consequences["plot_points_activated"] = [
                            p["title"] for p in activated_points
                        ]

                    completed_points = advance_result.get("completed_plot_points", [])
                    if completed_points:
                        description += (
                            " You have successfully resolved important story elements."
                        )
                        consequences["plot_points_completed"] = [
                            p["title"] for p in completed_points
                        ]

                # Include available choices in the response
                if choices_result.get("status") == "success":
                    consequences["narrative_choices"] = choices_result["choices"]
            else:
                # Fallback to simple processing
                success = True
                description = f"You attempt to {action} and succeed."
                consequences = {}

            # Record the action in memory
            if hasattr(self, "narrative_memory") and campaign_id:
                self.narrative_memory.record_event(
                    f"Action performed: {action}",
                    context.get("location", "unknown location"),
                    character_id,
                    4,
                )

                # Track character development if applicable
                if any(
                    word in action.lower()
                    for word in ["help", "save", "protect", "sacrifice"]
                ):
                    self.narrative_memory.record_character_development(
                        character_id=character_id,
                        development_type="personality",
                        description=f"Showed heroic qualities by {action}",
                        story_arc_id=context.get("story_arc_id", ""),
                    )

            return {
                "success": success,
                "description": description,
                "state_updates": consequences,
            }

        except Exception as e:
            logger.error(f"Error processing action: {str(e)}")
            return {
                "success": False,
                "description": "Something unexpected happens, preventing your action.",
                "state_updates": {},
            }

    async def create_campaign_story(
        self, campaign_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create initial story arcs and narrative structure for a new campaign.

        Args:
            campaign_context: Dictionary containing campaign details like setting, tone, characters

        Returns:
            Dict[str, Any]: Results of story creation including created arcs and initial choices
        """
        try:
            campaign_id = campaign_context.get("campaign_id", "")
            setting = campaign_context.get("setting", "fantasy")
            tone = campaign_context.get("tone", "heroic")
            characters = campaign_context.get("characters", [])

            if not campaign_id:
                return {"success": False, "message": "Campaign ID is required"}

            created_arcs = []

            if hasattr(self, "narrative_generation"):
                # Create main story arc
                main_arc_result = self.narrative_generation.create_story_arc(
                    title=f"The {setting.title()} Adventure",
                    description=f"A {tone} adventure set in a {setting} world where heroes rise to face great challenges.",
                    arc_type="main",
                    themes=f"{tone}, adventure, discovery",
                    character_ids=",".join(characters)
                    if isinstance(characters, list)
                    else str(characters),
                )

                if main_arc_result.get("status") == "success":
                    created_arcs.append(main_arc_result)

                    # Activate the main arc in narrative state
                    narrative_state = self.narrative_generation.get_narrative_state(
                        campaign_id
                    )
                    if narrative_state.get("status") == "not_found":
                        # Initialize narrative state for new campaign
                        from app.models.game_models import NarrativeState

                        new_state = NarrativeState(campaign_id=campaign_id)
                        new_state.active_story_arcs.append(
                            main_arc_result["story_arc_id"]
                        )
                        self.narrative_generation.narrative_states[campaign_id] = (
                            new_state
                        )
                    else:
                        # Add to existing state
                        if campaign_id in self.narrative_generation.narrative_states:
                            self.narrative_generation.narrative_states[
                                campaign_id
                            ].active_story_arcs.append(main_arc_result["story_arc_id"])

                # Create character-specific arcs if multiple characters
                if isinstance(characters, list) and len(characters) > 1:
                    character_arc_result = self.narrative_generation.create_story_arc(
                        title="Bonds of Fellowship",
                        description="The developing relationships and shared experiences of the adventuring party.",
                        arc_type="character",
                        themes="friendship, loyalty, growth",
                        character_ids=",".join(characters),
                    )

                    if character_arc_result.get("status") == "success":
                        created_arcs.append(character_arc_result)

                        # Add to narrative state
                        if campaign_id in self.narrative_generation.narrative_states:
                            self.narrative_generation.narrative_states[
                                campaign_id
                            ].active_story_arcs.append(
                                character_arc_result["story_arc_id"]
                            )

            # Record campaign creation in memory
            if hasattr(self, "narrative_memory"):
                self.narrative_memory.remember_fact(
                    f"Campaign started with {len(created_arcs)} story arcs in a {setting} setting",
                    "campaign",
                    8,
                )

                self.narrative_memory.record_event(
                    f"Campaign '{campaign_context.get('name', 'Untitled')}' begins",
                    setting,
                    ",".join(characters)
                    if isinstance(characters, list)
                    else str(characters),
                    9,
                )

            return {
                "success": True,
                "message": f"Campaign story created with {len(created_arcs)} story arcs",
                "created_arcs": created_arcs,
                "campaign_id": campaign_id,
            }

        except Exception as e:
            logger.error(f"Error creating campaign story: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to create campaign story: {str(e)}",
            }

    async def get_narrative_status(self, campaign_id: str) -> dict[str, Any]:
        """
        Get the current narrative status and available choices for a campaign.

        Args:
            campaign_id: ID of the campaign

        Returns:
            Dict[str, Any]: Current narrative status including active arcs, choices, and story state
        """
        try:
            if not hasattr(self, "narrative_generation"):
                return {
                    "success": False,
                    "message": "Narrative generation not available",
                }

            # Get narrative state
            narrative_state = self.narrative_generation.get_narrative_state(campaign_id)

            if narrative_state.get("status") != "success":
                return {
                    "success": False,
                    "message": "No narrative state found for campaign",
                }

            # Get recent events from memory
            recent_events = []
            if hasattr(self, "narrative_memory"):
                timeline_result = self.narrative_memory.recall_timeline(limit=5)
                if timeline_result.get("status") == "success":
                    recent_events = timeline_result.get("events", [])

            # Get story arc summaries
            arc_summaries = []
            if hasattr(self, "narrative_memory"):
                arcs_result = self.narrative_memory.recall_story_arcs()
                if arcs_result.get("status") == "success":
                    arc_summaries = arcs_result.get("story_arcs", [])

            return {
                "success": True,
                "narrative_state": narrative_state,
                "recent_events": recent_events,
                "story_arc_summaries": arc_summaries,
                "campaign_id": campaign_id,
            }

        except Exception as e:
            logger.error(f"Error getting narrative status: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get narrative status: {str(e)}",
            }


# Lazy singleton instance
_narrator = None


def get_narrator():
    """Get the narrator instance, creating it if necessary."""
    global _narrator
    if _narrator is None:
        _narrator = NarratorAgent()
    return _narrator


# For backward compatibility during import-time checks
narrator = None
