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

    @kernel_function(
        description="Store a narrative fact in memory.",
        name="remember_fact"
    )
    def remember_fact(self, fact: str, category: str, importance: int = 5) -> str:
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
                "last_accessed": datetime.datetime.now().isoformat()
            }
            
            # Store the memory
            self.memories[fact_id] = memory
            
            return f"Fact stored successfully with ID: {fact_id}"
        except Exception as e:
            logger.error(f"Error storing fact in memory: {str(e)}")
            return f"Failed to store fact: {str(e)}"

    @kernel_function(
        description="Record a narrative event in the campaign timeline.",
        name="record_event"
    )
    def record_event(self, event: str, location: str, characters: str, importance: int = 5) -> str:
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
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Store the event
            self.events.append(event_entry)
            
            return f"Event recorded successfully with ID: {event_id}"
        except Exception as e:
            logger.error(f"Error recording event: {str(e)}")
            return f"Failed to record event: {str(e)}"

    @kernel_function(
        description="Retrieve facts related to a specific query or category.",
        name="recall_facts"
    )
    def recall_facts(self, query: str = "", category: str = "") -> str:
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
            
            if filtered_memories:
                result = f"Found {len(filtered_memories)} relevant facts:\n"
                for memory in filtered_memories[:5]:  # Limit to top 5
                    result += f"- [{memory['category']}] {memory['content']} (importance: {memory['importance']})\n"
                return result
            else:
                return "No relevant facts found in memory."
        except Exception as e:
            logger.error(f"Error recalling facts: {str(e)}")
            return f"Failed to recall facts: {str(e)}"

    @kernel_function(
        description="Retrieve a timeline of recent events.",
        name="recall_timeline"
    )
    def recall_timeline(self, character: str = "", location: str = "", limit: int = 5) -> str:
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
                matches_character = not character or character.lower() in [c.lower() for c in event["characters"]]
                matches_location = not location or location.lower() in event["location"].lower()
                
                if matches_character and matches_location:
                    filtered_events.append(event)
            
            # Sort by timestamp (newest first)
            filtered_events.sort(key=lambda e: e["timestamp"], reverse=True)
            
            # Apply limit
            filtered_events = filtered_events[:limit]
            
            if filtered_events:
                result = f"Recent events timeline ({len(filtered_events)} events):\n"
                for event in filtered_events:
                    result += f"- {event['description']} at {event['location']} "
                    result += f"(characters: {', '.join(event['characters'])})\n"
                return result
            else:
                return "No recent events found in timeline."
        except Exception as e:
            logger.error(f"Error recalling timeline: {str(e)}")
            return f"Failed to recall timeline: {str(e)}"

    @kernel_function(
        description="Add or update an NPC in the campaign.",
        name="update_npc"
    )
    def update_npc(self, name: str, description: str, location: str, relationships: str = "") -> str:
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
                    "last_updated": datetime.datetime.now().isoformat()
                }
                
                self.npcs[name] = npc
            
            return f"NPC {name} updated successfully at {location}"
        except Exception as e:
            logger.error(f"Error updating NPC: {str(e)}")
            return f"Failed to update NPC: {str(e)}"

    @kernel_function(
        description="Retrieve information about a specific NPC.",
        name="get_npc"
    )
    def get_npc(self, name: str) -> str:
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
                
                result = f"NPC: {npc['name']}\n"
                result += f"Description: {npc['description']}\n"
                result += f"Location: {npc['location']}\n"
                if npc.get('relationships'):
                    result += f"Relationships: {npc['relationships']}\n"
                return result
            else:
                return f"NPC {name} not found in records."
        except Exception as e:
            logger.error(f"Error retrieving NPC: {str(e)}")
            return f"Failed to retrieve NPC: {str(e)}"
