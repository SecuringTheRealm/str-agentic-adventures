"""
NPC Management Plugin for the Semantic Kernel.
Provides comprehensive NPC creation, behavior modeling, and interaction capabilities.
"""
import logging
from typing import Dict, Any
import datetime

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from app.models.game_models import (
    NPC, NPCBehavior, NPCInteraction, NPCRelationship, NPCMemory,
    NPCPersonality, NPCRole, CreateNPCRequest, NPCInteractionRequest
)

logger = logging.getLogger(__name__)

class NPCManagementPlugin:
    """
    Plugin that provides comprehensive NPC management capabilities.
    Handles NPC creation, behavior modeling, relationships, and interactions.
    """

    def __init__(self):
        """Initialize the NPC management plugin."""
        # In-memory storage for NPCs and interactions
        # In a production system, this would use a persistent store
        self.npcs: Dict[str, NPC] = {}
        self.interactions: Dict[str, NPCInteraction] = {}

    @kernel_function(
        description="Create a new NPC with comprehensive attributes and behavior.",
        name="create_npc"
    )
    def create_npc(
        self, 
        name: str, 
        description: str, 
        race: str, 
        role: str, 
        location: str,
        personality: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Create a new NPC with comprehensive attributes and behavior.
        
        Args:
            name: Name of the NPC
            description: Physical and background description
            race: Race of the NPC
            role: Role/occupation of the NPC
            location: Current location of the NPC
            personality: Personality type (friendly, hostile, etc.)
            
        Returns:
            Dict[str, Any]: The created NPC information
        """
        try:
            # Validate enum values
            try:
                npc_race = getattr(__import__('app.models.game_models', fromlist=['Race']).Race, race.upper())
            except (AttributeError, ImportError):
                return {
                    "status": "error",
                    "message": f"Invalid race: {race}"
                }
            
            try:
                npc_role = getattr(NPCRole, role.upper())
            except AttributeError:
                return {
                    "status": "error", 
                    "message": f"Invalid role: {role}"
                }
                
            try:
                npc_personality = getattr(NPCPersonality, personality.upper())
            except AttributeError:
                return {
                    "status": "error",
                    "message": f"Invalid personality: {personality}"
                }

            # Create NPC with default behavior based on role and personality
            behavior = self._generate_default_behavior(npc_role, npc_personality)
            
            npc = NPC(
                name=name,
                description=description,
                race=npc_race,
                role=npc_role,
                current_location=location,
                personality=npc_personality,
                behavior=behavior
            )
            
            # Store the NPC
            self.npcs[npc.id] = npc
            
            return {
                "status": "success",
                "message": f"NPC {name} created successfully",
                "npc_id": npc.id,
                "npc": npc.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error creating NPC: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create NPC: {str(e)}"
            }

    @kernel_function(
        description="Retrieve detailed information about a specific NPC.",
        name="get_npc_details"
    )
    def get_npc_details(self, npc_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Dict[str, Any]: Detailed NPC information
        """
        try:
            if npc_id not in self.npcs:
                return {
                    "status": "not_found",
                    "message": f"NPC with ID {npc_id} not found"
                }
            
            npc = self.npcs[npc_id]
            npc.last_interaction = datetime.datetime.now()
            
            return {
                "status": "success",
                "npc": npc.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving NPC details: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve NPC details: {str(e)}"
            }

    @kernel_function(
        description="Generate NPC response based on personality and context.",
        name="generate_npc_response"
    )
    def generate_npc_response(
        self, 
        npc_id: str, 
        character_id: str, 
        player_message: str, 
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate an NPC response based on their personality, relationships, and context.
        
        Args:
            npc_id: ID of the NPC
            character_id: ID of the character interacting
            player_message: What the player said
            context: Additional context for the interaction
            
        Returns:
            Dict[str, Any]: Generated response and interaction updates
        """
        try:
            if npc_id not in self.npcs:
                return {
                    "status": "error",
                    "message": f"NPC with ID {npc_id} not found"
                }
            
            npc = self.npcs[npc_id]
            
            # Check if NPC is available for interaction
            if not npc.is_available:
                return {
                    "status": "unavailable",
                    "message": f"{npc.name} is not available for interaction right now.",
                    "response": f"{npc.name} seems busy and doesn't respond."
                }
            
            # Find existing relationship or create new one
            relationship = self._get_or_create_relationship(npc, character_id)
            
            # Generate response based on NPC personality and relationship
            response = self._generate_contextual_response(npc, relationship, player_message, context)
            
            # Record the interaction
            interaction = NPCInteraction(
                npc_id=npc_id,
                character_id=character_id,
                interaction_type="conversation",
                context={"message": player_message, "context": context},
                outcome="neutral"  # Could be enhanced with sentiment analysis
            )
            
            self.interactions[interaction.id] = interaction
            npc.memory.player_interactions.append({
                "character_id": character_id,
                "message": player_message,
                "timestamp": datetime.datetime.now().isoformat(),
                "npc_response": response
            })
            
            # Update last interaction time
            npc.last_interaction = datetime.datetime.now()
            
            return {
                "status": "success",
                "response": response,
                "npc_name": npc.name,
                "interaction_id": interaction.id,
                "relationship_status": {
                    "affection": relationship.affection,
                    "trust": relationship.trust,
                    "respect": relationship.respect
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating NPC response: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate NPC response: {str(e)}"
            }

    @kernel_function(
        description="Update NPC relationship with a character.",
        name="update_npc_relationship"
    )
    def update_npc_relationship(
        self, 
        npc_id: str, 
        character_id: str, 
        affection_change: int = 0,
        trust_change: int = 0,
        respect_change: int = 0,
        event_description: str = ""
    ) -> Dict[str, Any]:
        """
        Update the relationship between an NPC and a character.
        
        Args:
            npc_id: ID of the NPC
            character_id: ID of the character
            affection_change: Change in affection (-10 to +10)
            trust_change: Change in trust (-10 to +10)
            respect_change: Change in respect (-10 to +10)
            event_description: Description of what caused the relationship change
            
        Returns:
            Dict[str, Any]: Updated relationship information
        """
        try:
            if npc_id not in self.npcs:
                return {
                    "status": "error",
                    "message": f"NPC with ID {npc_id} not found"
                }
            
            npc = self.npcs[npc_id]
            relationship = self._get_or_create_relationship(npc, character_id)
            
            # Apply changes with bounds checking
            relationship.affection = max(-10, min(10, relationship.affection + affection_change))
            relationship.trust = max(-10, min(10, relationship.trust + trust_change))
            relationship.respect = max(-10, min(10, relationship.respect + respect_change))
            
            # Record the event in history
            if event_description:
                relationship.history.append(f"{datetime.datetime.now().isoformat()}: {event_description}")
            
            relationship.last_interaction = datetime.datetime.now()
            
            return {
                "status": "success",
                "message": "Relationship updated",
                "relationship": {
                    "affection": relationship.affection,
                    "trust": relationship.trust,
                    "respect": relationship.respect,
                    "relationship_type": relationship.relationship_type
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating NPC relationship: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update relationship: {str(e)}"
            }

    @kernel_function(
        description="Get all NPCs in a specific location.",
        name="get_npcs_in_location"
    )
    def get_npcs_in_location(self, location: str) -> Dict[str, Any]:
        """
        Get all NPCs currently in a specific location.
        
        Args:
            location: Name of the location
            
        Returns:
            Dict[str, Any]: List of NPCs in the location
        """
        try:
            npcs_in_location = []
            
            for npc in self.npcs.values():
                if npc.current_location.lower() == location.lower() and npc.is_alive and npc.is_available:
                    npcs_in_location.append({
                        "id": npc.id,
                        "name": npc.name,
                        "description": npc.description,
                        "role": npc.role.value,
                        "personality": npc.personality.value
                    })
            
            return {
                "status": "success",
                "location": location,
                "npcs": npcs_in_location,
                "count": len(npcs_in_location)
            }
            
        except Exception as e:
            logger.error(f"Error getting NPCs in location: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get NPCs in location: {str(e)}",
                "npcs": []
            }

    def _generate_default_behavior(self, role: NPCRole, personality: NPCPersonality) -> NPCBehavior:
        """Generate default behavior based on role and personality."""
        behavior = NPCBehavior(default_attitude=personality)
        
        # Adjust behavior based on role
        if role == NPCRole.GUARD:
            behavior.bravery = 8
            behavior.trust_level = 3
            behavior.combat_behavior = "aggressive"
        elif role == NPCRole.MERCHANT:
            behavior.helpfulness = 7
            behavior.trust_level = 6
            behavior.conversation_style = "polite"
        elif role == NPCRole.SCHOLAR:
            behavior.intelligence = 9
            behavior.conversation_style = "eloquent"
        elif role == NPCRole.CRIMINAL:
            behavior.trust_level = 2
            behavior.conversation_style = "gruff"
            behavior.combat_behavior = "flee"
            
        # Adjust based on personality
        if personality == NPCPersonality.FRIENDLY:
            behavior.helpfulness += 2
            behavior.trust_level += 1
        elif personality == NPCPersonality.HOSTILE:
            behavior.helpfulness -= 3
            behavior.trust_level -= 2
            behavior.combat_behavior = "aggressive"
        elif personality == NPCPersonality.FEARFUL:
            behavior.bravery -= 3
            behavior.combat_behavior = "flee"
            
        # Ensure values stay in bounds
        behavior.trust_level = max(0, min(10, behavior.trust_level))
        behavior.bravery = max(0, min(10, behavior.bravery))
        behavior.intelligence = max(0, min(10, behavior.intelligence))
        behavior.helpfulness = max(0, min(10, behavior.helpfulness))
        
        return behavior

    def _get_or_create_relationship(self, npc: NPC, character_id: str) -> NPCRelationship:
        """Get existing relationship or create a new one."""
        for relationship in npc.relationships:
            if relationship.target_id == character_id and relationship.target_type == "character":
                return relationship
        
        # Create new relationship
        new_relationship = NPCRelationship(
            target_id=character_id,
            target_type="character",
            relationship_type="neutral"
        )
        npc.relationships.append(new_relationship)
        return new_relationship

    def _generate_contextual_response(
        self, 
        npc: NPC, 
        relationship: NPCRelationship, 
        player_message: str, 
        context: str
    ) -> str:
        """Generate a contextual response based on NPC attributes and relationship."""
        
        # This is a simplified response generation system
        # In a production system, this would integrate with an LLM
        
        base_responses = {
            NPCPersonality.FRIENDLY: [
                f"Hello there! *{npc.name} smiles warmly*",
                f"*{npc.name} greets you cheerfully*",
                f"Good to see you! How can I help?"
            ],
            NPCPersonality.HOSTILE: [
                f"*{npc.name} glares at you suspiciously*",
                f"What do you want?",
                f"*{npc.name} looks annoyed by the interruption*"
            ],
            NPCPersonality.NEUTRAL: [
                f"*{npc.name} nods in acknowledgment*",
                f"Yes?",
                f"What brings you here?"
            ]
        }
        
        # Modify response based on relationship
        if relationship.affection > 5:
            return f"*{npc.name} brightens upon seeing you* It's wonderful to see you again! {player_message}"
        elif relationship.affection < -5:
            return f"*{npc.name} scowls* You again. What do you want this time?"
        elif relationship.trust > 7:
            return f"*{npc.name} speaks confidentially* I trust you, so I'll be direct with you..."
        
        # Default response based on personality
        responses = base_responses.get(npc.personality, base_responses[NPCPersonality.NEUTRAL])
        return responses[0]  # Simplified - would use more logic in production