"""
Scribe Agent - Manages character sheets and game data.
"""
import logging
import json
from typing import Dict, Any, List, Optional

try:
    import semantic_kernel as sk
    from semantic_kernel.orchestration.context_variables import ContextVariables
except ImportError:
    # Handle new semantic kernel API
    import semantic_kernel as sk
    ContextVariables = None

from app.kernel_setup import kernel_manager
from app.plugins.npc_management_plugin import NPCManagementPlugin

logger = logging.getLogger(__name__)

class ScribeAgent:
    """
    Scribe Agent that manages character sheets, inventory, equipment, and game data.
    This agent is responsible for tracking and updating structured game data.
    """

    def __init__(self):
        """Initialize the Scribe agent with its own kernel instance."""
        try:
            self.kernel = kernel_manager.create_kernel()
        except Exception as e:
            logger.warning(f"Could not create kernel: {e}. Operating in standalone mode.")
            self.kernel = None
        
        self._register_skills()

        # In-memory storage for testing - would be replaced with persistent storage
        self.characters = {}
        self.npcs = {}
        self.inventory = {}
        
        # Initialize NPC management plugin
        self.npc_manager = NPCManagementPlugin()

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

            # Store character
            self.characters[character_id] = character_sheet

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
            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]

            # Apply updates (simplified for now)
            for key, value in updates.items():
                if key in character and not key == "id":  # Don't allow changing the ID
                    character[key] = value

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
        return self.characters.get(character_id)

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

    # NPC Management Methods
    async def create_npc(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new NPC using the NPC management plugin.

        Args:
            npc_data: Dictionary containing NPC creation details

        Returns:
            Dict[str, Any]: The created NPC information
        """
        try:
            result = self.npc_manager.create_npc(
                name=npc_data.get("name", "Unnamed NPC"),
                description=npc_data.get("description", "A mysterious figure"),
                race=npc_data.get("race", "human"),
                role=npc_data.get("role", "commoner"),
                location=npc_data.get("location", "unknown"),
                personality=npc_data.get("personality", "neutral")
            )
            
            # Also store in legacy format for compatibility
            if result["status"] == "success":
                npc_id = result["npc_id"]
                self.npcs[npc_id] = result["npc"]
                
            return result

        except Exception as e:
            logger.error(f"Error creating NPC: {str(e)}")
            return {"error": "Failed to create NPC"}

    async def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get NPC details by ID.

        Args:
            npc_id: ID of the NPC

        Returns:
            Optional[Dict[str, Any]]: NPC information or None if not found
        """
        try:
            result = self.npc_manager.get_npc_details(npc_id)
            if result["status"] == "success":
                return result["npc"]
            return None

        except Exception as e:
            logger.error(f"Error getting NPC: {str(e)}")
            return None

    async def update_npc_relationship(
        self, 
        npc_id: str, 
        character_id: str, 
        relationship_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update relationship between NPC and character.

        Args:
            npc_id: ID of the NPC
            character_id: ID of the character
            relationship_changes: Dictionary with relationship changes

        Returns:
            Dict[str, Any]: Updated relationship information
        """
        try:
            result = self.npc_manager.update_npc_relationship(
                npc_id=npc_id,
                character_id=character_id,
                affection_change=relationship_changes.get("affection_change", 0),
                trust_change=relationship_changes.get("trust_change", 0),
                respect_change=relationship_changes.get("respect_change", 0),
                event_description=relationship_changes.get("event_description", "")
            )
            return result

        except Exception as e:
            logger.error(f"Error updating NPC relationship: {str(e)}")
            return {"error": "Failed to update relationship"}

    async def get_npcs_in_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Get all NPCs in a specific location.

        Args:
            location: Name of the location

        Returns:
            List[Dict[str, Any]]: List of NPCs in the location
        """
        try:
            result = self.npc_manager.get_npcs_in_location(location)
            if result["status"] == "success":
                return result["npcs"]
            return []

        except Exception as e:
            logger.error(f"Error getting NPCs in location: {str(e)}")
            return []

    async def generate_npc_interaction(
        self, 
        npc_id: str, 
        character_id: str, 
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an NPC interaction response.

        Args:
            npc_id: ID of the NPC
            character_id: ID of the character
            interaction_data: Interaction context and details

        Returns:
            Dict[str, Any]: NPC response and interaction result
        """
        try:
            result = self.npc_manager.generate_npc_response(
                npc_id=npc_id,
                character_id=character_id,
                player_message=interaction_data.get("message", ""),
                context=interaction_data.get("context", "")
            )
            return result

        except Exception as e:
            logger.error(f"Error generating NPC interaction: {str(e)}")
            return {"error": "Failed to generate NPC interaction"}

# Singleton instance
scribe = ScribeAgent()
