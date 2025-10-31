"""
Narrative Generation Plugin for the Agent Framework.
This plugin provides dynamic storyline generation and branching narrative capabilities.
"""

import datetime
import json
import logging
import random
from typing import Any

# Note: Converted from Agent plugin to direct function calls

from app.models.game_models import (
    NarrativeChoice,
    NarrativeEvent,
    NarrativeState,
    PlotPoint,
    StoryArc,
)

logger = logging.getLogger(__name__)


class NarrativeGenerationPlugin:
    """
    Plugin that provides narrative generation capabilities for dynamic storylines and branching narratives.
    Manages story arcs, plot points, player choices, and narrative state tracking.
    """

    def __init__(self) -> None:
        """Initialize the narrative generation plugin."""
        # In-memory storage for narrative elements
        # In a production system, this would use a persistent store
        self.story_arcs = {}  # StoryArc objects by ID
        self.plot_points = {}  # PlotPoint objects by ID
        self.narrative_choices = {}  # NarrativeChoice objects by ID
        self.narrative_states = {}  # NarrativeState objects by campaign_id
        self.narrative_events = []  # List of NarrativeEvent objects
        self.choice_templates = self._initialize_choice_templates()
        self.plot_templates = self._initialize_plot_templates()

    def _initialize_choice_templates(self) -> dict[str, dict[str, Any]]:
        """Initialize templates for common narrative choices."""
        return {
            "exploration": {
                "investigate": {
                    "text": "Investigate further",
                    "consequences": {"info_gained": True},
                },
                "proceed": {
                    "text": "Proceed cautiously",
                    "consequences": {"safety": True},
                },
                "retreat": {
                    "text": "Retreat and regroup",
                    "consequences": {"resources_preserved": True},
                },
            },
            "social": {
                "persuade": {
                    "text": "Try to persuade",
                    "consequences": {"relationship_change": 1},
                },
                "intimidate": {
                    "text": "Use intimidation",
                    "consequences": {"relationship_change": -1, "fear_gained": True},
                },
                "negotiate": {
                    "text": "Negotiate a deal",
                    "consequences": {"compromise_reached": True},
                },
            },
            "combat": {
                "attack": {
                    "text": "Attack immediately",
                    "consequences": {"combat_initiated": True},
                },
                "defend": {
                    "text": "Take defensive position",
                    "consequences": {"defense_bonus": True},
                },
                "flee": {
                    "text": "Attempt to escape",
                    "consequences": {"combat_avoided": True, "reputation_change": -1},
                },
            },
        }

    def _initialize_plot_templates(self) -> dict[str, dict[str, Any]]:
        """Initialize templates for common plot point types."""
        return {
            "introduction": {
                "call_to_adventure": {
                    "title": "The Call to Adventure",
                    "description": "A mysterious figure approaches with an urgent quest",
                    "triggers": {"location": "tavern", "time": "evening"},
                },
                "inciting_incident": {
                    "title": "The Inciting Incident",
                    "description": "An unexpected event changes everything",
                    "triggers": {"story_progress": 0.1},
                },
            },
            "conflict": {
                "rising_tension": {
                    "title": "Rising Tension",
                    "description": "The stakes increase and obstacles multiply",
                    "triggers": {"story_progress": 0.3},
                },
                "moral_dilemma": {
                    "title": "Moral Dilemma",
                    "description": "Players must choose between competing values",
                    "triggers": {"character_development": True},
                },
            },
            "climax": {
                "final_confrontation": {
                    "title": "Final Confrontation",
                    "description": "The ultimate challenge that will determine the outcome",
                    "triggers": {"story_progress": 0.8},
                }
            },
        }

#     # @kernel_function(
#         description="Create a new story arc with plot points and narrative structure.",
#         name="create_story_arc",
#     )
    def create_story_arc(
        self,
        title: str,
        description: str,
        arc_type: str = "main",
        themes: str = "",
        character_ids: str = "",
    ) -> dict[str, Any]:
        """
        Create a new story arc with associated plot points.

        Args:
            title: Title of the story arc
            description: Description of the story arc
            arc_type: Type of arc (main, side, character, world)
            themes: Comma-separated list of themes
            character_ids: Comma-separated list of character IDs involved

        Returns:
            Dict[str, Any]: The created story arc information
        """
        try:
            # Parse themes and characters
            theme_list = [t.strip() for t in themes.split(",") if t.strip()]
            character_list = [c.strip() for c in character_ids.split(",") if c.strip()]

            # Create the story arc
            story_arc = StoryArc(
                title=title,
                description=description,
                type=arc_type,
                themes=theme_list,
                characters_involved=character_list,
            )

            # Store the story arc
            self.story_arcs[story_arc.id] = story_arc

            # Generate initial plot points based on arc type
            initial_points = self._generate_initial_plot_points(story_arc)
            story_arc.plot_points = [p.id for p in initial_points]

            return {
                "status": "success",
                "message": f"Story arc '{title}' created successfully",
                "story_arc_id": story_arc.id,
                "plot_points_generated": len(initial_points),
            }
        except Exception as e:
            logger.error(f"Error creating story arc: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create story arc: {str(e)}",
            }

#     # @kernel_function(
#         description="Generate narrative choices for a given situation.",
#         name="generate_choices",
#     )
    def generate_choices(
        self,
        situation: str,
        context: str = "",
        choice_type: str = "general",
        num_choices: int = 3,
    ) -> dict[str, Any]:
        """
        Generate narrative choices for a given situation.

        Args:
            situation: Description of the current situation
            context: Additional context about the story state
            choice_type: Type of choices to generate (exploration, social, combat, general)
            num_choices: Number of choices to generate

        Returns:
            Dict[str, Any]: Generated narrative choices
        """
        try:
            choices = []

            # Get templates for the specified choice type
            templates = self.choice_templates.get(choice_type, {})

            if templates:
                # Use templates as starting point
                template_keys = list(templates.keys())
                for i in range(min(num_choices, len(template_keys))):
                    template = templates[template_keys[i]]
                    choice = NarrativeChoice(
                        text=template["text"],
                        description=f"In this situation: {situation}",
                        consequences=template.get("consequences", {}),
                    )
                    choices.append(choice)
                    self.narrative_choices[choice.id] = choice

            # Generate additional creative choices if needed
            remaining = num_choices - len(choices)
            for i in range(remaining):
                choice = NarrativeChoice(
                    text=f"Creative option {i + 1}",
                    description=f"A unique approach to: {situation}",
                    consequences={"creative_solution": True},
                )
                choices.append(choice)
                self.narrative_choices[choice.id] = choice

            return {
                "status": "success",
                "choices": [
                    {"id": c.id, "text": c.text, "description": c.description}
                    for c in choices
                ],
                "situation": situation,
                "context": context,
            }
        except Exception as e:
            logger.error(f"Error generating choices: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate choices: {str(e)}",
            }

#     # @kernel_function(
#         description="Process a player's narrative choice and determine consequences.",
#         name="process_choice",
#     )
    def process_choice(
        self,
        choice_id: str,
        campaign_id: str,
        character_id: str = "",
        additional_context: str = "",
    ) -> dict[str, Any]:
        """
        Process a player's narrative choice and apply consequences.

        Args:
            choice_id: ID of the chosen narrative choice
            campaign_id: ID of the current campaign
            character_id: ID of the character making the choice
            additional_context: Additional context for processing

        Returns:
            Dict[str, Any]: Results of the choice processing
        """
        try:
            # Get the choice
            if choice_id not in self.narrative_choices:
                return {"status": "error", "message": "Choice not found"}

            choice = self.narrative_choices[choice_id]

            # Get or create narrative state for campaign
            if campaign_id not in self.narrative_states:
                self.narrative_states[campaign_id] = NarrativeState(
                    campaign_id=campaign_id
                )

            narrative_state = self.narrative_states[campaign_id]

            # Process consequences
            consequences = choice.consequences.copy()
            narrative_outcomes = self._apply_choice_consequences(
                choice, narrative_state, character_id
            )

            # Record the choice event
            event = NarrativeEvent(
                title=f"Choice Made: {choice.text}",
                description=f"Player chose: {choice.text}",
                event_type="choice_made",
                characters_involved=[character_id] if character_id else [],
                choices_made=[choice_id],
                consequences=consequences,
            )
            self.narrative_events.append(event)

            # Update narrative state
            narrative_state.last_updated = datetime.datetime.now()
            if choice_id in narrative_state.pending_choices:
                narrative_state.pending_choices.remove(choice_id)

            return {
                "status": "success",
                "message": "Choice processed successfully",
                "choice": choice.text,
                "consequences": consequences,
                "narrative_outcomes": narrative_outcomes,
                "event_id": event.id,
            }
        except Exception as e:
            logger.error(f"Error processing choice: {str(e)}")
            return {"status": "error", "message": f"Failed to process choice: {str(e)}"}

#     # @kernel_function(
#         description="Advance the narrative by checking plot point triggers and updating story state.",
#         name="advance_narrative",
#     )
    def advance_narrative(
        self, campaign_id: str, current_situation: str = "", trigger_data: str = ""
    ) -> dict[str, Any]:
        """
        Advance the narrative by checking plot point triggers and updating story state.

        Args:
            campaign_id: ID of the current campaign
            current_situation: Description of the current situation
            trigger_data: JSON string of trigger data to check against

        Returns:
            Dict[str, Any]: Narrative advancement results
        """
        try:
            # Get narrative state
            if campaign_id not in self.narrative_states:
                self.narrative_states[campaign_id] = NarrativeState(
                    campaign_id=campaign_id
                )

            narrative_state = self.narrative_states[campaign_id]

            # Parse trigger data
            triggers = {}
            if trigger_data:
                try:
                    triggers = json.loads(trigger_data)
                except (json.JSONDecodeError, TypeError):
                    triggers = {}

            # Check for plot point activations
            activated_points = []
            completed_points = []

            for arc_id in narrative_state.active_story_arcs:
                if arc_id in self.story_arcs:
                    arc = self.story_arcs[arc_id]
                    arc_results = self._check_plot_point_triggers(
                        arc, triggers, narrative_state
                    )
                    activated_points.extend(arc_results["activated"])
                    completed_points.extend(arc_results["completed"])

            # Generate new choices if needed
            new_choices = []
            if activated_points or current_situation:
                choice_result = self.generate_choices(
                    current_situation or "The story continues...",
                    context=f"Active plot points: {len(activated_points)}",
                    num_choices=3,
                )
                if choice_result["status"] == "success":
                    new_choices = choice_result["choices"]
                    narrative_state.pending_choices.extend(
                        [c["id"] for c in new_choices]
                    )

            # Update narrative state
            narrative_state.last_updated = datetime.datetime.now()

            return {
                "status": "success",
                "activated_plot_points": activated_points,
                "completed_plot_points": completed_points,
                "new_choices": new_choices,
                "narrative_state_updated": True,
            }
        except Exception as e:
            logger.error(f"Error advancing narrative: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to advance narrative: {str(e)}",
            }

#     # @kernel_function(
#         description="Get the current narrative state for a campaign.",
#         name="get_narrative_state",
#     )
    def get_narrative_state(self, campaign_id: str) -> dict[str, Any]:
        """
        Get the current narrative state for a campaign.

        Args:
            campaign_id: ID of the campaign

        Returns:
            Dict[str, Any]: Current narrative state information
        """
        try:
            if campaign_id not in self.narrative_states:
                return {
                    "status": "not_found",
                    "message": "No narrative state found for campaign",
                }

            state = self.narrative_states[campaign_id]

            # Get active story arcs details
            active_arcs = []
            for arc_id in state.active_story_arcs:
                if arc_id in self.story_arcs:
                    arc = self.story_arcs[arc_id]
                    active_arcs.append(
                        {
                            "id": arc.id,
                            "title": arc.title,
                            "type": arc.type,
                            "status": arc.status,
                            "current_point": arc.current_point,
                        }
                    )

            # Get pending choices details
            pending_choices = []
            for choice_id in state.pending_choices:
                if choice_id in self.narrative_choices:
                    choice = self.narrative_choices[choice_id]
                    pending_choices.append(
                        {
                            "id": choice.id,
                            "text": choice.text,
                            "description": choice.description,
                        }
                    )

            return {
                "status": "success",
                "campaign_id": campaign_id,
                "current_scene": state.current_scene,
                "active_story_arcs": active_arcs,
                "pending_choices": pending_choices,
                "narrative_flags": state.narrative_flags,
                "last_updated": state.last_updated.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting narrative state: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get narrative state: {str(e)}",
            }

    def _generate_initial_plot_points(self, story_arc: StoryArc) -> list[PlotPoint]:
        """Generate initial plot points for a story arc based on its type."""
        plot_points = []

        # Get templates based on arc type
        if story_arc.type == "main":
            # Main story arc gets full structure
            templates = ["introduction", "conflict", "climax"]
        elif story_arc.type == "side":
            # Side quest gets simpler structure
            templates = ["introduction", "conflict"]
        else:
            # Character/world arcs get custom structure
            templates = ["introduction"]

        for template_type in templates:
            if template_type in self.plot_templates:
                template_options = list(self.plot_templates[template_type].keys())
                if template_options:
                    template_key = random.choice(template_options)  # noqa: S311
                    template = self.plot_templates[template_type][template_key]

                    plot_point = PlotPoint(
                        title=template["title"],
                        description=template["description"],
                        type=template_type,
                        triggers=template.get("triggers", {}),
                        importance=7 if story_arc.type == "main" else 5,
                    )
                    plot_points.append(plot_point)
                    self.plot_points[plot_point.id] = plot_point

        return plot_points

    def _apply_choice_consequences(
        self,
        choice: NarrativeChoice,
        narrative_state: NarrativeState,
        character_id: str,
    ) -> dict[str, Any]:
        """Apply the consequences of a narrative choice to the story state."""
        outcomes = {}

        for consequence_type, value in choice.consequences.items():
            if consequence_type == "relationship_change":
                # Update character relationships
                if character_id not in narrative_state.character_relationships:
                    narrative_state.character_relationships[character_id] = {}
                # This would be expanded with actual relationship tracking logic
                outcomes["relationship_updated"] = True

            elif consequence_type == "narrative_flag":
                # Set narrative flags
                narrative_state.narrative_flags[value] = True
                outcomes["flag_set"] = value

            elif consequence_type == "world_state_change":
                # Update world state
                narrative_state.world_state.update(
                    value if isinstance(value, dict) else {}
                )
                outcomes["world_updated"] = True

        return outcomes

    def _check_plot_point_triggers(
        self,
        story_arc: StoryArc,
        triggers: dict[str, Any],
        narrative_state: NarrativeState,
    ) -> dict[str, list]:
        """Check if any plot points in the story arc should be activated or completed."""
        activated = []
        completed = []

        for plot_point_id in story_arc.plot_points:
            if plot_point_id in self.plot_points:
                plot_point = self.plot_points[plot_point_id]

                # Check if plot point should be activated
                if plot_point.status == "pending" and self._check_triggers(
                    plot_point.triggers, triggers
                ):
                    plot_point.status = "active"
                    story_arc.current_point = plot_point_id
                    activated.append(
                        {
                            "id": plot_point.id,
                            "title": plot_point.title,
                            "type": plot_point.type,
                        }
                    )

                # Check if active plot point should be completed
                elif plot_point.status == "active" and self._check_completion_criteria(
                    plot_point, narrative_state
                ):
                    plot_point.status = "completed"
                    completed.append(
                        {
                            "id": plot_point.id,
                            "title": plot_point.title,
                            "type": plot_point.type,
                        }
                    )

        return {"activated": activated, "completed": completed}

    def _check_triggers(
        self, plot_triggers: dict[str, Any], current_triggers: dict[str, Any]
    ) -> bool:
        """Check if plot point triggers are satisfied."""
        if not plot_triggers:
            return True

        for trigger_key, trigger_value in plot_triggers.items():
            if trigger_key not in current_triggers:
                return False
            if current_triggers[trigger_key] != trigger_value:
                return False

        return True

    def _check_completion_criteria(
        self, plot_point: PlotPoint, narrative_state: NarrativeState
    ) -> bool:
        """Check if a plot point should be marked as completed with sophisticated logic."""

        # Check for explicit completion flags
        if f"complete_{plot_point.id}" in narrative_state.narrative_flags:
            return True

        # Check for general completion flag
        if "completion_flag" in narrative_state.narrative_flags:
            return True

        # Analyze plot point type and requirements
        plot_type = plot_point.plot_type
        completion_requirements = self._get_completion_requirements(plot_type)

        # Check specific completion criteria based on plot type
        if plot_type == "quest":
            return self._check_quest_completion(plot_point, narrative_state)
        if plot_type == "encounter":
            return self._check_encounter_completion(plot_point, narrative_state)
        if plot_type == "exploration":
            return self._check_exploration_completion(plot_point, narrative_state)
        if plot_type == "social":
            return self._check_social_completion(plot_point, narrative_state)

        # Fallback: Check if enough narrative events have occurred for this plot point
        related_events = [
            e for e in self.narrative_events if e.plot_point_id == plot_point.id
        ]

        return len(related_events) >= completion_requirements.get("min_events", 3)

    def _get_completion_requirements(self, plot_type: str) -> dict[str, Any]:
        """Get completion requirements for different plot types."""
        requirements = {
            "quest": {
                "min_events": 5,
                "requires_objective": True,
                "requires_resolution": True,
            },
            "encounter": {"min_events": 2, "requires_combat_resolution": True},
            "exploration": {"min_events": 3, "requires_discovery": True},
            "social": {
                "min_events": 4,
                "requires_interaction": True,
                "requires_relationship_change": True,
            },
            "mystery": {
                "min_events": 6,
                "requires_clues": 3,
                "requires_revelation": True,
            },
        }
        return requirements.get(plot_type, {"min_events": 3})

    def _check_quest_completion(
        self, plot_point: PlotPoint, narrative_state: NarrativeState
    ) -> bool:
        """Check if a quest plot point is completed."""
        # Check for quest-specific completion flags
        quest_flags = [
            f
            for f in narrative_state.narrative_flags
            if f.startswith(f"quest_{plot_point.id}")
        ]

        # Quest completion criteria
        has_objective_met = any("objective_complete" in flag for flag in quest_flags)
        has_reward_received = any("reward" in flag for flag in quest_flags)
        has_resolution = any(
            "resolved" in flag or "completed" in flag for flag in quest_flags
        )

        return has_objective_met and (has_reward_received or has_resolution)

    def _check_encounter_completion(
        self, plot_point: PlotPoint, narrative_state: NarrativeState
    ) -> bool:
        """Check if an encounter plot point is completed."""
        encounter_flags = [
            f
            for f in narrative_state.narrative_flags
            if f.startswith(f"encounter_{plot_point.id}")
        ]

        # Encounter completion criteria
        has_combat_end = any(
            "combat_end" in flag or "victory" in flag or "defeated" in flag
            for flag in encounter_flags
        )
        has_outcome = any("outcome" in flag for flag in encounter_flags)

        return has_combat_end or has_outcome

    def _check_exploration_completion(
        self, plot_point: PlotPoint, narrative_state: NarrativeState
    ) -> bool:
        """Check if an exploration plot point is completed."""
        exploration_flags = [
            f
            for f in narrative_state.narrative_flags
            if f.startswith(f"explore_{plot_point.id}")
        ]

        # Exploration completion criteria
        has_discovery = any(
            "discovered" in flag or "found" in flag for flag in exploration_flags
        )
        has_location_visited = any(
            "visited" in flag or "entered" in flag for flag in exploration_flags
        )

        return has_discovery or has_location_visited

    def _check_social_completion(
        self, plot_point: PlotPoint, narrative_state: NarrativeState
    ) -> bool:
        """Check if a social plot point is completed."""
        social_flags = [
            f
            for f in narrative_state.narrative_flags
            if f.startswith(f"social_{plot_point.id}")
        ]

        # Social completion criteria
        has_interaction = any(
            "conversation" in flag or "negotiation" in flag for flag in social_flags
        )
        has_relationship_change = any(
            "relationship" in flag or "reputation" in flag for flag in social_flags
        )
        has_outcome = any(
            "agreement" in flag or "disagreement" in flag or "resolved" in flag
            for flag in social_flags
        )

        return has_interaction and (has_relationship_change or has_outcome)
