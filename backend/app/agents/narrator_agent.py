"""
Narrator Agent - Manages campaign narrative and story elements.
"""

import json
import logging
from typing import Any

from app.agent_client_setup import agent_client_manager
from app.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)


class NarratorAgent:
    """
    Narrator Agent that manages campaign narrative and story elements.
    Uses Azure AI SDK for narrative generation.
    """

    def __init__(self) -> None:
        """Initialize the Narrator agent with Azure AI SDK."""
        # Initialize basic attributes first
        self._fallback_mode = False
        self.azure_client: AzureOpenAIClient | None = None

        try:
            # Try to get the shared chat client from agent client manager
            chat_client = agent_client_manager.get_chat_client()
            if chat_client is None:
                # Agent client manager is in fallback mode
                self._fallback_mode = True
                logger.warning(
                    "Narrator agent operating in fallback mode - "
                    "Azure OpenAI not configured"
                )
                self._initialize_fallback_components()
            else:
                self._register_skills()
                logger.info("Narrator agent initialized with Azure AI SDK")
                try:
                    self.azure_client = AzureOpenAIClient()
                except Exception as azure_error:
                    logger.error(
                        "Failed to initialize Azure OpenAI client for Narrator agent: %s",
                        azure_error,
                    )
                    logger.warning("Narrator agent switching to fallback mode.")
                    self._fallback_mode = True
                    self._initialize_fallback_components()

        except Exception as e:
            logger.warning(
                f"Failed to initialize Narrator agent with Azure AI SDK: {e}. "
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
        # Note: Plugins will be converted to tool functions when needed
        # For now, maintain compatibility by storing plugin references
        try:
            # Import plugins (they still work as standalone modules)
            from app.plugins.narrative_generation_plugin import (
                NarrativeGenerationPlugin,
            )
            from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            # Create plugin instances for direct method access
            self.narrative_memory = NarrativeMemoryPlugin()
            self.rules_engine = RulesEnginePlugin()
            self.narrative_generation = NarrativeGenerationPlugin()

            logger.info("Narrator agent plugins initialized for direct access")
        except Exception as e:
            logger.error(f"Error initializing Narrator agent plugins: {str(e)}")
            # Don't raise - enter fallback mode instead
            self._fallback_mode = True
            logger.warning(
                "Narrator agent entering fallback mode - using basic functionality "
                "without advanced plugins"
            )

    async def describe_scene(self, scene_context: dict[str, Any]) -> str:
        """
        Generate a rich description of a scene based on the provided context.

        Args:
            scene_context: Dictionary containing scene details

        Returns:
            str: Descriptive narrative of the scene
        """
        scene_context = scene_context or {}
        fallback_description, summary = self._build_scene_summary(scene_context)

        if self._fallback_mode or not self.azure_client:
            return fallback_description

        try:
            system_prompt = (
                "You are the Narrator collaborating with a Dungeon Master. "
                "Craft immersive, sensory scene descriptions for players in 3-4 "
                "sentences. Keep the tone cinematic but concise."
            )
            context_json = json.dumps(
                summary,
                ensure_ascii=False,
                default=str,
                indent=2,
            )
            user_message = (
                "Use the scene context below to describe what the players perceive "
                "right now.\n"
                f"{context_json}\n"
                "Focus on actionable details that invite interaction."
            )

            response = await self.azure_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.75,
                max_tokens=350,
            )
            return response.strip() or fallback_description
        except Exception as exc:
            logger.error("Narrator scene generation failed: %s", exc)
            return fallback_description

    def _build_scene_summary(
        self, scene_context: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Create fallback description and structured context for Azure prompts."""
        location = scene_context.get("location", "an unknown place")
        time_of_day = scene_context.get("time", "an indeterminate time")
        mood = scene_context.get("mood", "mysterious")
        campaign_id = scene_context.get("campaign_id", "")

        active_arcs: list[str] = []
        if campaign_id and hasattr(self, "narrative_generation"):
            try:
                narrative_state = self.narrative_generation.get_narrative_state(
                    campaign_id
                )
                if narrative_state.get("status") == "success":
                    active_arcs = [
                        arc["title"]
                        for arc in narrative_state.get("active_story_arcs", [])
                    ]
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("Failed to obtain narrative state: %s", exc)

        location_history: list[str] = []
        if hasattr(self, "narrative_memory"):
            try:
                location_memories = self.narrative_memory.recall_facts("", "location")
                if (
                    location_memories.get("status") == "success"
                    and location_memories.get("facts")
                ):
                    location_history = [
                        fact["content"] for fact in location_memories["facts"][:2]
                    ]
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("Failed to recall narrative memory: %s", exc)

        base_description = f"You find yourself in {location} during {time_of_day}."
        if mood == "tense":
            atmosphere = (
                " The air crackles with tension, and shadows seem to move of their "
                "own accord."
            )
        elif mood == "peaceful":
            atmosphere = (
                " A sense of calm pervades the area, offering a momentary respite "
                "from your adventures."
            )
        elif mood == "mysterious":
            atmosphere = (
                " Mystery hangs in the air like a thick fog, hinting at secrets yet "
                "to be discovered."
            )
        else:
            atmosphere = (
                " The atmosphere is charged with possibility as your adventure "
                "continues."
            )

        arc_context = ""
        if active_arcs:
            arc_context = (
                " Threads of your ongoing adventures in "
                f"{', '.join(active_arcs)} color every decision."
            )

        fallback_description = base_description + atmosphere
        if arc_context:
            fallback_description += f" {arc_context}"

        if hasattr(self, "narrative_memory") and campaign_id:
            try:
                self.narrative_memory.record_event(
                    f"Scene described: {location}",
                    location,
                    scene_context.get("characters", ""),
                    3,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("Failed to record narrative memory: %s", exc)

        summary = {
            "campaign_id": campaign_id,
            "location": location,
            "time": time_of_day,
            "mood": mood,
            "active_story_arcs": active_arcs,
            "location_history": location_history,
            "characters": scene_context.get("characters"),
            "recent_events": scene_context.get("recent_events"),
            "raw_context": {
                key: value
                for key, value in scene_context.items()
                if key
                not in {
                    "campaign_id",
                    "location",
                    "time",
                    "mood",
                    "characters",
                    "recent_events",
                }
            },
        }

        return fallback_description, summary

    async def process_action(
        self, action: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process a player action and determine narrative outcome.

        Args:
            action: The action the player is attempting
            context: The current game context

        Returns:
            Dict[str, Any]: The outcome of the action, including success or failure,
            narration, and any updates to game state.
        """
        try:
            campaign_id = context.get("campaign_id", "")
            character_id = context.get("character_id", "")

            success = True
            description = f"You attempt to {action}."
            consequences: dict[str, Any] = {}

            if hasattr(self, "narrative_generation"):
                choice_type = "general"
                lowered = action.lower()
                if any(
                    word in lowered for word in ["fight", "attack", "combat"]
                ):
                    choice_type = "combat"
                elif any(
                    word in lowered
                    for word in ["talk", "speak", "persuade", "negotiate"]
                ):
                    choice_type = "social"
                elif any(
                    word in lowered for word in ["explore", "investigate", "search"]
                ):
                    choice_type = "exploration"

                choices_result = self.narrative_generation.generate_choices(
                    situation=action,
                    context=str(context),
                    choice_type=choice_type,
                    num_choices=3,
                )

                advance_result = self.narrative_generation.advance_narrative(
                    campaign_id=campaign_id,
                    current_situation=action,
                    trigger_data=json.dumps(
                        {"action": action, "character_id": character_id}
                    ),
                )

                if advance_result.get("status") == "success":
                    activated_points = advance_result.get("activated_plot_points", [])
                    if activated_points:
                        description += (
                            " Your action triggers significant developments in the"
                            " story."
                        )
                        consequences["plot_points_activated"] = [
                            point["title"] for point in activated_points
                        ]

                    completed_points = advance_result.get("completed_plot_points", [])
                    if completed_points:
                        description += (
                            " You have successfully resolved important story elements."
                        )
                        consequences["plot_points_completed"] = [
                            point["title"] for point in completed_points
                        ]

                if choices_result.get("status") == "success":
                    consequences["narrative_choices"] = choices_result["choices"]
            else:
                consequences = {}

            if hasattr(self, "narrative_memory") and campaign_id:
                try:
                    self.narrative_memory.record_event(
                        f"Action performed: {action}",
                        context.get("location", "unknown location"),
                        character_id,
                        4,
                    )

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
                except Exception as exc:  # pragma: no cover - defensive
                    logger.debug("Failed to update narrative memory: %s", exc)

            result = {
                "success": success,
                "description": description,
                "state_updates": consequences,
            }

            if not self._fallback_mode and self.azure_client:
                try:
                    ai_description = await self._generate_action_narration(
                        action, context, result
                    )
                    if ai_description:
                        result["description"] = ai_description
                except Exception as exc:  # pragma: no cover - defensive
                    logger.error("Narrator action generation failed: %s", exc)

            return result

        except Exception as e:
            logger.error(f"Error processing action: {str(e)}")
            return {
                "success": False,
                "description": "Something unexpected happens, preventing your action.",
                "state_updates": {},
            }

    async def _generate_action_narration(
        self, action: str, context: dict[str, Any], result: dict[str, Any]
    ) -> str:
        """Generate a narrated outcome for a player action using Azure OpenAI."""
        system_prompt = (
            "You are the Narrator supporting a Dungeon Master. Summarize player "
            "actions in 2-3 sentences, emphasizing consequences, tone, and hooks for "
            "future decisions."
        )
        payload = {
            "action": action,
            "success": result.get("success"),
            "state_updates": result.get("state_updates"),
            "context": context,
        }
        user_message = (
            "Narrate the outcome of the player's action using the details below.\n"
            f"{json.dumps(payload, ensure_ascii=False, default=str, indent=2)}\n"
            "Keep it grounded in the established scene."
        )

        response = await self.azure_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.strip()

    async def create_campaign_story(
        self, campaign_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create initial story arcs and narrative structure for a new campaign.

        Args:
            campaign_context: Dictionary containing campaign details such as the
            setting, tone, and characters.

        Returns:
            Dict[str, Any]: Results of story creation including created arcs and
            initial choices.
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
