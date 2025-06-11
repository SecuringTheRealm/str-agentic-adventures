"""
Narrative Memory Plugin for the Semantic Kernel.
This plugin provides memory storage and retrieval for narrative elements.
"""
import logging
from typing import Dict, Any, List, Optional
import json
import datetime

from semantic_kernel.functions import kernel_function

from app.persistence import PersistentAgent

logger = logging.getLogger(__name__)

class NarrativeMemoryPlugin(PersistentAgent):
    """
    Plugin that provides narrative memory capabilities to the agents.
    Stores and retrieves key facts, events, and narrative elements.
    """

    def __init__(self):
        """Initialize the narrative memory plugin."""
        super().__init__("narrative_memory")
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
    def remember_fact(self, fact: str, category: str, importance: int = 5) -> Dict[str, Any]:
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
            
            # Save to persistence
            self._save_memories_async()
            
            return {
                "status": "success",
                "message": "Fact stored in narrative memory",
                "fact_id": fact_id
            }
        except Exception as e:
            logger.error(f"Error storing fact in memory: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to store fact: {str(e)}"
            }

    @kernel_function(
        description="Record a narrative event in the campaign timeline.",
        name="record_event"
    )
    def record_event(self, event: str, location: str, characters: str, importance: int = 5) -> Dict[str, Any]:
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
            
            # Save to persistence
            self._save_events_async()
            
            return {
                "status": "success",
                "message": "Event recorded in narrative timeline",
                "event_id": event_id
            }
        except Exception as e:
            logger.error(f"Error recording event: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to record event: {str(e)}"
            }

    @kernel_function(
        description="Retrieve facts related to a specific query or category.",
        name="recall_facts"
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
                "count": len(filtered_memories)
            }
        except Exception as e:
            logger.error(f"Error recalling facts: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to recall facts: {str(e)}",
                "facts": []
            }

    @kernel_function(
        description="Retrieve a timeline of recent events.",
        name="recall_timeline"
    )
    def recall_timeline(self, character: str = "", location: str = "", limit: int = 5) -> Dict[str, Any]:
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
            
            return {
                "status": "success",
                "events": filtered_events,
                "count": len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error recalling timeline: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to recall timeline: {str(e)}",
                "events": []
            }

    @kernel_function(
        description="Add or update an NPC in the campaign.",
        name="update_npc"
    )
    def update_npc(self, name: str, description: str, location: str, relationships: str = "") -> Dict[str, Any]:
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
            
            # Save to persistence
            self._save_npcs_async()
            
            return {
                "status": "success",
                "message": f"NPC {name} updated",
                "npc": npc
            }
        except Exception as e:
            logger.error(f"Error updating NPC: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update NPC: {str(e)}"
            }

    @kernel_function(
        description="Retrieve information about a specific NPC.",
        name="get_npc"
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
                
                return {
                    "status": "success",
                    "npc": npc
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"NPC {name} not found"
                }
        except Exception as e:
            logger.error(f"Error retrieving NPC: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve NPC: {str(e)}"
            }
    
    def _save_memories_async(self):
        """Save memories to persistence (non-blocking)."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.save_agent_data("memories", self.memories))
        except Exception as e:
            logger.error(f"Error scheduling memory save: {str(e)}")
    
    def _save_events_async(self):
        """Save events to persistence (non-blocking)."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.save_agent_data("events", {"events": self.events}))
        except Exception as e:
            logger.error(f"Error scheduling events save: {str(e)}")
    
    def _save_npcs_async(self):
        """Save NPCs to persistence (non-blocking)."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.save_agent_data("npcs", self.npcs))
        except Exception as e:
            logger.error(f"Error scheduling NPCs save: {str(e)}")
    
    async def load_narrative_data(self):
        """Load narrative data from persistence."""
        try:
            # Load memories
            memories_data = await self.load_agent_data("memories")
            if memories_data:
                self.memories = memories_data
            
            # Load events
            events_data = await self.load_agent_data("events")
            if events_data and "events" in events_data:
                self.events = events_data["events"]
            
            # Load NPCs
            npcs_data = await self.load_agent_data("npcs")
            if npcs_data:
                self.npcs = npcs_data
                
            logger.info("Loaded narrative data from persistence")
            return True
        except Exception as e:
            logger.error(f"Error loading narrative data: {str(e)}")
            return False
    
    async def save_to_session(self, session_id: str) -> bool:
        """
        Save narrative memory state to a session.
        
        Args:
            session_id: The session ID to save to
            
        Returns:
            bool: True if successful
        """
        try:
            agent_data = {
                "memories": self.memories,
                "events": self.events,
                "npcs": self.npcs,
                "locations": self.locations
            }
            return await super().save_to_session(session_id, agent_data)
        except Exception as e:
            logger.error(f"Error saving narrative memory to session {session_id}: {str(e)}")
            return False
    
    async def load_from_session(self, session_id: str) -> bool:
        """
        Load narrative memory state from a session.
        
        Args:
            session_id: The session ID to load from
            
        Returns:
            bool: True if successful
        """
        try:
            agent_data = await self.get_session_data(session_id)
            if agent_data:
                self.memories = agent_data.get("memories", {})
                self.events = agent_data.get("events", [])
                self.npcs = agent_data.get("npcs", {})
                self.locations = agent_data.get("locations", {})
                logger.info(f"Loaded narrative memory from session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading narrative memory from session {session_id}: {str(e)}")
            return False
