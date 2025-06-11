"""
NPC Integration Service - Provides high-level NPC management for game agents.
This service acts as a bridge between game agents and the NPC management plugin.
"""
import logging
from typing import Dict, Any, List, Optional
from app.plugins.npc_management_plugin import NPCManagementPlugin

logger = logging.getLogger(__name__)

class NPCIntegrationService:
    """
    Service that provides high-level NPC management functionality for game agents.
    This service encapsulates NPC management operations in a way that's easy for agents to use.
    """

    def __init__(self):
        """Initialize the NPC integration service."""
        self.npc_manager = NPCManagementPlugin()
        
    def create_story_npc(
        self, 
        name: str, 
        description: str, 
        location: str,
        role_in_story: str = "background",
        personality_traits: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create an NPC specifically for story/narrative purposes.
        
        Args:
            name: Name of the NPC
            description: Description of the NPC
            location: Where the NPC is located
            role_in_story: Role in the story (quest_giver, ally, enemy, etc.)
            personality_traits: List of personality traits
            
        Returns:
            Dict[str, Any]: Created NPC information
        """
        try:
            # Determine NPC role and personality based on story role
            npc_role = self._map_story_role_to_npc_role(role_in_story)
            personality = self._determine_personality_from_traits(personality_traits)
            
            result = self.npc_manager.create_npc(
                name=name,
                description=description,
                race="human",  # Default to human, can be enhanced later
                role=npc_role,
                location=location,
                personality=personality
            )
            
            if result["status"] == "success":
                # Add story-specific information
                npc_id = result["npc_id"]
                npc = self.npc_manager.npcs[npc_id]
                npc.memory.important_facts.extend([
                    f"Role in story: {role_in_story}",
                    f"Created for narrative purposes in {location}"
                ])
                
                if personality_traits:
                    npc.memory.important_facts.append(f"Personality traits: {', '.join(personality_traits)}")
                    
                logger.info(f"Created story NPC: {name} ({npc_id}) in {location}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error creating story NPC: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create story NPC: {str(e)}"
            }

    def get_npcs_for_scene(self, location: str, scene_context: str = "") -> List[Dict[str, Any]]:
        """
        Get NPCs relevant for a particular scene/location.
        
        Args:
            location: Location where the scene takes place
            scene_context: Additional context about the scene
            
        Returns:
            List[Dict[str, Any]]: NPCs relevant to the scene
        """
        try:
            result = self.npc_manager.get_npcs_in_location(location)
            
            if result["status"] == "success":
                npcs = result["npcs"]
                
                # Enhance NPC information for scene context
                for npc in npcs:
                    npc_details = self.npc_manager.get_npc_details(npc["id"])
                    if npc_details["status"] == "success":
                        full_npc = npc_details["npc"]
                        npc["current_mood"] = self._determine_npc_mood(full_npc, scene_context)
                        npc["likely_actions"] = self._suggest_npc_actions(full_npc, scene_context)
                        
                return npcs
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting NPCs for scene: {str(e)}")
            return []

    def handle_npc_interaction(
        self, 
        npc_name_or_id: str, 
        character_id: str, 
        interaction_type: str,
        player_action: str,
        scene_context: str = ""
    ) -> Dict[str, Any]:
        """
        Handle a player interaction with an NPC.
        
        Args:
            npc_name_or_id: Name or ID of the NPC
            character_id: ID of the character interacting
            interaction_type: Type of interaction (conversation, trade, etc.)
            player_action: What the player is doing/saying
            scene_context: Context of the current scene
            
        Returns:
            Dict[str, Any]: NPC response and interaction result
        """
        try:
            # Find NPC by name or ID
            npc_id = self._find_npc_by_name_or_id(npc_name_or_id)
            if not npc_id:
                return {
                    "status": "error",
                    "message": f"NPC '{npc_name_or_id}' not found"
                }
            
            # Generate the interaction
            result = self.npc_manager.generate_npc_response(
                npc_id=npc_id,
                character_id=character_id,
                player_message=player_action,
                context=f"{interaction_type} - {scene_context}"
            )
            
            # Enhance response with narrative context
            if result["status"] == "success":
                npc_details = self.npc_manager.get_npc_details(npc_id)
                if npc_details["status"] == "success":
                    npc = npc_details["npc"]
                    result["narrative_context"] = {
                        "npc_mood": self._determine_npc_mood(npc, scene_context),
                        "relationship_hint": self._get_relationship_hint(result["relationship_status"]),
                        "suggested_followup": self._suggest_followup_actions(npc, interaction_type)
                    }
                    
            return result
            
        except Exception as e:
            logger.error(f"Error handling NPC interaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to handle NPC interaction: {str(e)}"
            }

    def update_npc_story_state(
        self, 
        npc_name_or_id: str, 
        story_event: str,
        impact_on_npc: str,
        relationship_changes: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Update an NPC's state based on story events.
        
        Args:
            npc_name_or_id: Name or ID of the NPC
            story_event: Description of the story event
            impact_on_npc: How the event affects the NPC
            relationship_changes: Changes to relationships with characters
            
        Returns:
            Dict[str, Any]: Update result
        """
        try:
            npc_id = self._find_npc_by_name_or_id(npc_name_or_id)
            if not npc_id:
                return {
                    "status": "error",
                    "message": f"NPC '{npc_name_or_id}' not found"
                }
            
            # Update NPC memory with the story event
            npc = self.npc_manager.npcs[npc_id]
            npc.memory.witnessed_events.append(f"{story_event} - {impact_on_npc}")
            
            # Update relationships if specified
            if relationship_changes:
                for character_id, changes in relationship_changes.items():
                    self.npc_manager.update_npc_relationship(
                        npc_id=npc_id,
                        character_id=character_id,
                        affection_change=changes.get("affection", 0),
                        trust_change=changes.get("trust", 0),
                        respect_change=changes.get("respect", 0),
                        event_description=story_event
                    )
            
            logger.info(f"Updated NPC {npc_name_or_id} story state: {story_event}")
            
            return {
                "status": "success",
                "message": f"Updated {npc_name_or_id} story state",
                "npc_id": npc_id
            }
            
        except Exception as e:
            logger.error(f"Error updating NPC story state: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update NPC story state: {str(e)}"
            }

    def get_npc_story_summary(self, location: str = "") -> Dict[str, Any]:
        """
        Get a summary of NPCs and their current story state for narrative purposes.
        
        Args:
            location: Optional location filter
            
        Returns:
            Dict[str, Any]: Summary of NPCs and their story relevance
        """
        try:
            if location:
                npcs_result = self.npc_manager.get_npcs_in_location(location)
                npcs = npcs_result.get("npcs", []) if npcs_result["status"] == "success" else []
            else:
                # Get all NPCs
                npcs = []
                for npc in self.npc_manager.npcs.values():
                    npcs.append({
                        "id": npc.id,
                        "name": npc.name,
                        "description": npc.description,
                        "role": npc.role.value,
                        "personality": npc.personality.value,
                        "current_location": npc.current_location
                    })
            
            # Create story-relevant summaries
            story_summary = {
                "location": location or "All locations",
                "npc_count": len(npcs),
                "npcs": []
            }
            
            for npc_info in npcs:
                npc_details = self.npc_manager.get_npc_details(npc_info["id"])
                if npc_details["status"] == "success":
                    npc = npc_details["npc"]
                    story_summary["npcs"].append({
                        "name": npc["name"],
                        "role": npc["role"],
                        "location": npc["current_location"],
                        "availability": "available" if npc["is_available"] else "unavailable",
                        "recent_interactions": len(npc["memory"]["player_interactions"]),
                        "relationships_count": len(npc["relationships"]),
                        "story_relevance": self._assess_story_relevance(npc)
                    })
            
            return {
                "status": "success",
                "summary": story_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting NPC story summary: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get NPC story summary: {str(e)}"
            }

    # Helper methods
    def _map_story_role_to_npc_role(self, story_role: str) -> str:
        """Map story role to NPC role enum."""
        role_mapping = {
            "quest_giver": "quest_giver",
            "merchant": "merchant",
            "guard": "guard",
            "innkeeper": "innkeeper",
            "ally": "ally",
            "enemy": "rival",
            "background": "commoner",
            "noble": "noble",
            "scholar": "scholar",
            "priest": "priest"
        }
        return role_mapping.get(story_role.lower(), "commoner")

    def _determine_personality_from_traits(self, traits: List[str]) -> str:
        """Determine personality enum from trait list."""
        if not traits:
            return "neutral"
        
        # Simple mapping of traits to personalities
        positive_traits = ["kind", "helpful", "cheerful", "generous"]
        negative_traits = ["hostile", "mean", "angry", "cruel"]
        fearful_traits = ["scared", "timid", "nervous", "anxious"]
        
        trait_str = " ".join(traits).lower()
        
        if any(trait in trait_str for trait in positive_traits):
            return "friendly"
        elif any(trait in trait_str for trait in negative_traits):
            return "hostile"
        elif any(trait in trait_str for trait in fearful_traits):
            return "fearful"
        else:
            return "neutral"

    def _find_npc_by_name_or_id(self, name_or_id: str) -> Optional[str]:
        """Find NPC ID by name or return ID if already provided."""
        # Check if it's already an ID
        if name_or_id in self.npc_manager.npcs:
            return name_or_id
        
        # Search by name
        for npc_id, npc in self.npc_manager.npcs.items():
            if npc.name.lower() == name_or_id.lower():
                return npc_id
        
        return None

    def _determine_npc_mood(self, npc: Dict[str, Any], scene_context: str) -> str:
        """Determine NPC mood based on personality and context."""
        personality = npc.get("personality", "neutral")
        behavior = npc.get("behavior", {})
        
        if "combat" in scene_context.lower() or "danger" in scene_context.lower():
            if behavior.get("bravery", 5) > 7:
                return "determined"
            elif behavior.get("bravery", 5) < 3:
                return "frightened"
            else:
                return "cautious"
        elif "celebration" in scene_context.lower() or "festival" in scene_context.lower():
            return "cheerful" if personality == "friendly" else "indifferent"
        else:
            mood_map = {
                "friendly": "welcoming",
                "hostile": "irritated",
                "neutral": "calm",
                "fearful": "nervous"
            }
            return mood_map.get(personality, "calm")

    def _suggest_npc_actions(self, npc: Dict[str, Any], scene_context: str) -> List[str]:
        """Suggest possible NPC actions based on role and context."""
        role = npc.get("role", "commoner")
        personality = npc.get("personality", "neutral")
        
        base_actions = {
            "merchant": ["offer goods", "negotiate prices", "share rumors"],
            "guard": ["patrol area", "question strangers", "enforce rules"],
            "innkeeper": ["serve drinks", "provide rooms", "share local news"],
            "quest_giver": ["offer quest", "provide information", "give rewards"]
        }
        
        actions = base_actions.get(role, ["observe surroundings", "go about daily business"])
        
        # Modify based on personality
        if personality == "friendly":
            actions.append("greet newcomers")
        elif personality == "hostile":
            actions.append("watch suspiciously")
        elif personality == "fearful":
            actions.append("stay alert for danger")
            
        return actions[:3]  # Return top 3 suggestions

    def _get_relationship_hint(self, relationship_status: Dict[str, Any]) -> str:
        """Get a hint about the relationship status."""
        affection = relationship_status.get("affection", 0)
        trust = relationship_status.get("trust", 0)
        
        if affection > 5 and trust > 5:
            return "The NPC regards you as a trusted friend"
        elif affection < -5 or trust < -5:
            return "The NPC views you with suspicion or dislike"
        elif affection > 0 or trust > 0:
            return "The NPC has a positive impression of you"
        else:
            return "The NPC is neutral towards you"

    def _suggest_followup_actions(self, npc: Dict[str, Any], interaction_type: str) -> List[str]:
        """Suggest possible followup actions for players."""
        role = npc.get("role", "commoner")
        
        if interaction_type == "conversation":
            return ["ask about local events", "inquire about services", "say goodbye"]
        elif interaction_type == "trade":
            return ["browse items", "negotiate price", "complete purchase"]
        else:
            return ["continue conversation", "end interaction", "ask for help"]

    def _assess_story_relevance(self, npc: Dict[str, Any]) -> str:
        """Assess how relevant an NPC is to the current story."""
        interactions = len(npc.get("memory", {}).get("player_interactions", []))
        relationships = len(npc.get("relationships", []))
        role = npc.get("role", "commoner")
        
        if role == "quest_giver" or interactions > 3:
            return "high"
        elif relationships > 0 or interactions > 0:
            return "medium"
        else:
            return "low"

# Singleton instance
npc_service = NPCIntegrationService()