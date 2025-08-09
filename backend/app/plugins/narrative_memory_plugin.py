"""
Narrative Memory Plugin for the Semantic Kernel.
This plugin provides memory storage and retrieval for narrative elements.
"""

import logging
from typing import Dict, Any
import datetime

from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class NarrativeMemoryPlugin:
    """
    Plugin that provides narrative memory capabilities to the agents.
    Stores and retrieves key facts, events, and narrative elements.
    """

    def __init__(self):
        """Initialize the narrative memory plugin."""
        # In-memory storage for narrative elements
        # In a production system, this would use a persistent store
        self.memories = {}
        self.events = []
        self.npcs = {}
        self.locations = {}
        self.story_arcs = {}  # For tracking story arc memories
        self.character_arcs = {}  # For tracking character development arcs

    @kernel_function(
        description="Store a narrative fact in memory.", name="remember_fact"
    )
    def remember_fact(
        self, fact: str, category: str, importance: int = 5
    ) -> Dict[str, Any]:
        """
        Store a narrative fact in memory.

        Args:
            fact: The fact to remember
            category: Category of the fact (character, location, plot, etc.)
            importance: Importance of the fact (1-10)

        Returns:
            Dict[str, Any]: Confirmation of the stored fact
        """
        try:
            fact_id = f"fact_{len(self.memories) + 1}"

            # Create the memory entry
            memory = {
                "id": fact_id,
                "content": fact,
                "category": category,
                "importance": importance,
                "created_at": datetime.datetime.now().isoformat(),
                "last_accessed": datetime.datetime.now().isoformat(),
            }

            # Store the memory
            self.memories[fact_id] = memory

            return {
                "status": "success",
                "message": "Fact stored in narrative memory",
                "fact_id": fact_id,
            }
        except Exception as e:
            logger.error(f"Error storing fact in memory: {str(e)}")
            return {"status": "error", "message": f"Failed to store fact: {str(e)}"}

    @kernel_function(
        description="Record a narrative event in the campaign timeline.",
        name="record_event",
    )
    def record_event(
        self, event: str, location: str, characters: str, importance: int = 5
    ) -> Dict[str, Any]:
        """
        Record a narrative event in the campaign timeline.

        Args:
            event: Description of the event
            location: Where the event occurred
            characters: Characters involved in the event (comma-separated)
            importance: Importance of the event (1-10)

        Returns:
            Dict[str, Any]: Confirmation of the recorded event
        """
        try:
            event_id = f"event_{len(self.events) + 1}"

            # Parse characters
            character_list = [c.strip() for c in characters.split(",")]

            # Create the event entry
            event_entry = {
                "id": event_id,
                "description": event,
                "location": location,
                "characters": character_list,
                "importance": importance,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            # Store the event
            self.events.append(event_entry)

            return {
                "status": "success",
                "message": "Event recorded in narrative timeline",
                "event_id": event_id,
            }
        except Exception as e:
            logger.error(f"Error recording event: {str(e)}")
            return {"status": "error", "message": f"Failed to record event: {str(e)}"}

    @kernel_function(
        description="Retrieve facts related to a specific query or category.",
        name="recall_facts",
    )
    def recall_facts(self, query: str = "", category: str = "") -> Dict[str, Any]:
        """
        Retrieve facts related to a specific query or category.

        Args:
            query: Search terms to filter facts
            category: Category to filter facts (optional)

        Returns:
            Dict[str, Any]: List of relevant facts
        """
        try:
            # Filter memories based on query and category
            filtered_memories = []

            for memory_id, memory in self.memories.items():
                # Update access time
                memory["last_accessed"] = datetime.datetime.now().isoformat()

                # Apply filters
                matches_category = not category or memory["category"] == category
                matches_query = not query or query.lower() in memory["content"].lower()

                if matches_category and matches_query:
                    filtered_memories.append(memory)

            # Sort by importance
            filtered_memories.sort(key=lambda m: m["importance"], reverse=True)

            return {
                "status": "success",
                "facts": filtered_memories,
                "count": len(filtered_memories),
            }
        except Exception as e:
            logger.error(f"Error recalling facts: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to recall facts: {str(e)}",
                "facts": [],
            }

    @kernel_function(
        description="Retrieve a timeline of recent events.", name="recall_timeline"
    )
    def recall_timeline(
        self, character: str = "", location: str = "", limit: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve a timeline of recent events.

        Args:
            character: Filter events by character involvement (optional)
            location: Filter events by location (optional)
            limit: Maximum number of events to return

        Returns:
            Dict[str, Any]: Timeline of events
        """
        try:
            # Filter events based on character and location
            filtered_events = []

            for event in self.events:
                # Apply filters
                matches_character = not character or character.lower() in [
                    c.lower() for c in event["characters"]
                ]
                matches_location = (
                    not location or location.lower() in event["location"].lower()
                )

                if matches_character and matches_location:
                    filtered_events.append(event)

            # Sort by timestamp (newest first)
            filtered_events.sort(key=lambda e: e["timestamp"], reverse=True)

            # Apply limit
            filtered_events = filtered_events[:limit]

            return {
                "status": "success",
                "events": filtered_events,
                "count": len(filtered_events),
            }
        except Exception as e:
            logger.error(f"Error recalling timeline: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to recall timeline: {str(e)}",
                "events": [],
            }

    @kernel_function(
        description="Add or update an NPC in the campaign.", name="update_npc"
    )
    def update_npc(
        self, name: str, description: str, location: str, relationships: str = ""
    ) -> Dict[str, Any]:
        """
        Add or update an NPC in the campaign.

        Args:
            name: Name of the NPC
            description: Description of the NPC
            location: Current location of the NPC
            relationships: NPC's relationships to characters or other NPCs (optional)

        Returns:
            Dict[str, Any]: The updated NPC information
        """
        try:
            # Create or update the NPC entry
            if name in self.npcs:
                npc = self.npcs[name]
                npc["description"] = description
                npc["location"] = location

                if relationships:
                    npc["relationships"] = relationships

                npc["last_updated"] = datetime.datetime.now().isoformat()
            else:
                npc = {
                    "name": name,
                    "description": description,
                    "location": location,
                    "relationships": relationships,
                    "created_at": datetime.datetime.now().isoformat(),
                    "last_updated": datetime.datetime.now().isoformat(),
                }

                self.npcs[name] = npc

            return {"status": "success", "message": f"NPC {name} updated", "npc": npc}
        except Exception as e:
            logger.error(f"Error updating NPC: {str(e)}")
            return {"status": "error", "message": f"Failed to update NPC: {str(e)}"}

    @kernel_function(
        description="Retrieve information about a specific NPC.", name="get_npc"
    )
    def get_npc(self, name: str) -> Dict[str, Any]:
        """
        Retrieve information about a specific NPC.

        Args:
            name: Name of the NPC

        Returns:
            Dict[str, Any]: Information about the NPC
        """
        try:
            if name in self.npcs:
                npc = self.npcs[name]

                # Update last accessed time
                npc["last_accessed"] = datetime.datetime.now().isoformat()

                return {"status": "success", "npc": npc}
            else:
                return {"status": "not_found", "message": f"NPC {name} not found"}
        except Exception as e:
            logger.error(f"Error retrieving NPC: {str(e)}")
            return {"status": "error", "message": f"Failed to retrieve NPC: {str(e)}"}

    @kernel_function(
        description="Track progress of a story arc in the narrative memory.",
        name="track_story_arc",
    )
    def track_story_arc(
        self,
        arc_id: str,
        arc_title: str,
        progress: str,
        key_events: str = "",
        character_impact: str = "",
    ) -> Dict[str, Any]:
        """
        Track the progress and impact of a story arc.

        Args:
            arc_id: Unique identifier for the story arc
            arc_title: Title of the story arc
            progress: Current progress description
            key_events: Comma-separated list of key events in this arc
            character_impact: How this arc has impacted character development

        Returns:
            Dict[str, Any]: Confirmation of story arc tracking
        """
        try:
            # Parse key events
            events_list = [e.strip() for e in key_events.split(",") if e.strip()]

            # Create or update story arc memory
            if arc_id in self.story_arcs:
                arc_memory = self.story_arcs[arc_id]
                arc_memory["progress"] = progress
                arc_memory["key_events"].extend(events_list)
                if character_impact:
                    arc_memory["character_impact"] = character_impact
                arc_memory["last_updated"] = datetime.datetime.now().isoformat()
            else:
                arc_memory = {
                    "id": arc_id,
                    "title": arc_title,
                    "progress": progress,
                    "key_events": events_list,
                    "character_impact": character_impact,
                    "created_at": datetime.datetime.now().isoformat(),
                    "last_updated": datetime.datetime.now().isoformat(),
                }
                self.story_arcs[arc_id] = arc_memory

            return {
                "status": "success",
                "message": f"Story arc '{arc_title}' progress tracked",
                "arc_id": arc_id,
            }
        except Exception as e:
            logger.error(f"Error tracking story arc: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to track story arc: {str(e)}",
            }

    @kernel_function(
        description="Record a character development moment or arc progression.",
        name="record_character_development",
    )
    def record_character_development(
        self,
        character_id: str,
        development_type: str,
        description: str,
        story_arc_id: str = "",
    ) -> Dict[str, Any]:
        """
        Record character development moments and personal growth arcs.

        Args:
            character_id: ID of the character
            development_type: Type of development (personality, skills, relationships, backstory)
            description: Description of the development
            story_arc_id: Associated story arc ID (optional)

        Returns:
            Dict[str, Any]: Confirmation of character development recording
        """
        try:
            development_id = f"dev_{len(self.character_arcs) + 1}"

            # Create character development entry
            development = {
                "id": development_id,
                "character_id": character_id,
                "type": development_type,
                "description": description,
                "story_arc_id": story_arc_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            # Track in character arcs
            if character_id not in self.character_arcs:
                self.character_arcs[character_id] = []

            self.character_arcs[character_id].append(development)

            return {
                "status": "success",
                "message": "Character development recorded",
                "development_id": development_id,
            }
        except Exception as e:
            logger.error(f"Error recording character development: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to record character development: {str(e)}",
            }

    @kernel_function(
        description="Retrieve story arc memories for narrative continuity.",
        name="recall_story_arcs",
    )
    def recall_story_arcs(
        self, character_id: str = "", status: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieve story arc memories for narrative continuity.

        Args:
            character_id: Filter by character involvement (optional)
            status: Filter by arc status like "active", "completed" (optional)

        Returns:
            Dict[str, Any]: Story arc memories
        """
        try:
            filtered_arcs = []

            for arc_id, arc_memory in self.story_arcs.items():
                # Apply filters (simplified filtering for now)
                matches_character = not character_id or character_id in arc_memory.get(
                    "character_impact", ""
                )
                matches_status = (
                    not status or status in arc_memory.get("progress", "").lower()
                )

                if matches_character and matches_status:
                    # Update last accessed
                    arc_memory["last_accessed"] = datetime.datetime.now().isoformat()
                    filtered_arcs.append(arc_memory)

            # Sort by last updated
            filtered_arcs.sort(key=lambda a: a["last_updated"], reverse=True)

            return {
                "status": "success",
                "story_arcs": filtered_arcs,
                "count": len(filtered_arcs),
            }
        except Exception as e:
            logger.error(f"Error recalling story arcs: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to recall story arcs: {str(e)}",
                "story_arcs": [],
            }
