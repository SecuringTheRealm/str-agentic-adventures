"""
Scribe Agent - Manages character sheets and game data.
"""
import logging
import json
from typing import Dict, Any, List, Optional

import semantic_kernel as sk

from app.kernel_setup import kernel_manager
from app.persistence import PersistentAgent, session_manager

logger = logging.getLogger(__name__)

class ScribeAgent(PersistentAgent):
    """
    Scribe Agent that manages character sheets, inventory, equipment, and game data.
    This agent is responsible for tracking and updating structured game data.
    """

    def __init__(self):
        """Initialize the Scribe agent with its own kernel instance."""
        super().__init__("scribe")
        self.kernel = kernel_manager.create_kernel()
        self._register_skills()

        # In-memory storage for testing - would be replaced with persistent storage
        self.characters = {}
        self.npcs = {}
        self.inventory = {}

    def _register_skills(self):
        """Register necessary skills for the Scribe agent."""
        # Will register skills once implemented
        pass

    async def create_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new character sheet based on provided data.

        Args:
            character_data: Dictionary containing character creation details

        Returns:
            Dict[str, Any]: The created character sheet
        """
        try:
            character_id = character_data.get("id", f"character_{len(self.characters) + 1}")

            # Create basic character sheet structure
            character_sheet = {
                "id": character_id,
                "name": character_data.get("name", "Unnamed Adventurer"),
                "race": character_data.get("race", "Human"),
                "class": character_data.get("class", "Fighter"),
                "level": character_data.get("level", 1),
                "abilities": {
                    "strength": character_data.get("strength", 10),
                    "dexterity": character_data.get("dexterity", 10),
                    "constitution": character_data.get("constitution", 10),
                    "intelligence": character_data.get("intelligence", 10),
                    "wisdom": character_data.get("wisdom", 10),
                    "charisma": character_data.get("charisma", 10)
                },
                "hitPoints": {
                    "current": character_data.get("hitPoints", 10),
                    "maximum": character_data.get("hitPoints", 10)
                },
                "inventory": []
            }

            # Store character in memory for backwards compatibility
            self.characters[character_id] = character_sheet
            
            # Store character persistently
            await self.save_agent_data(f"character_{character_id}", character_sheet)

            return character_sheet

        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            return {"error": "Failed to create character"}

    async def update_character(self, character_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing character sheet.

        Args:
            character_id: The ID of the character to update
            updates: Dictionary containing fields to update

        Returns:
            Dict[str, Any]: The updated character sheet
        """
        try:
            character = await self.get_character(character_id)
            if not character:
                return {"error": f"Character {character_id} not found"}

            # Apply updates (simplified for now)
            for key, value in updates.items():
                if key in character and not key == "id":  # Don't allow changing the ID
                    character[key] = value

            # Update memory cache
            self.characters[character_id] = character
            
            # Save to persistence
            await self.save_agent_data(f"character_{character_id}", character)

            return character

        except Exception as e:
            logger.error(f"Error updating character: {str(e)}")
            return {"error": "Failed to update character"}

    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a character sheet by ID.

        Args:
            character_id: The ID of the character to retrieve

        Returns:
            Optional[Dict[str, Any]]: The character sheet if found, None otherwise
        """
        # Try memory first for backwards compatibility
        if character_id in self.characters:
            return self.characters[character_id]
        
        # Try loading from persistence
        character = await self.load_agent_data(f"character_{character_id}")
        if character:
            # Cache in memory
            self.characters[character_id] = character
        
        return character

    async def add_to_inventory(self, character_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an item to a character's inventory.

        Args:
            character_id: The ID of the character
            item: Dictionary containing item details

        Returns:
            Dict[str, Any]: The updated inventory
        """
        try:
            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]
            inventory = character.get("inventory", [])
            inventory.append(item)
            character["inventory"] = inventory

            return {"inventory": inventory}

        except Exception as e:
            logger.error(f"Error adding to inventory: {str(e)}")
            return {"error": "Failed to add item to inventory"}

    async def save_to_session(self, session_id: str) -> bool:
        """
        Save scribe agent state to a session.
        
        Args:
            session_id: The session ID to save to
            
        Returns:
            bool: True if successful
        """
        try:
            agent_data = {
                "characters": self.characters,
                "npcs": self.npcs,
                "inventory": self.inventory
            }
            return await super().save_to_session(session_id, agent_data)
        except Exception as e:
            logger.error(f"Error saving to session {session_id}: {str(e)}")
            return False
    
    async def load_from_session(self, session_id: str) -> bool:
        """
        Load scribe agent state from a session.
        
        Args:
            session_id: The session ID to load from
            
        Returns:
            bool: True if successful
        """
        try:
            agent_data = await self.get_session_data(session_id)
            if agent_data:
                self.characters = agent_data.get("characters", {})
                self.npcs = agent_data.get("npcs", {})
                self.inventory = agent_data.get("inventory", {})
                logger.info(f"Loaded scribe state from session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading from session {session_id}: {str(e)}")
            return False

# Singleton instance
scribe = ScribeAgent()
