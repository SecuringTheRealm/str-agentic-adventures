"""
Combat Cartographer Agent - Generates tactical battle maps for combat encounters.
"""
import logging
from typing import Dict, Any

from app.azure_openai_client import AzureOpenAIClient
from app.kernel_setup import kernel_manager

logger = logging.getLogger(__name__)

class CombatCartographerAgent:
    """
    Combat Cartographer Agent that creates tactical battle maps based on narrative context.
    This agent is responsible for generating visual representations of combat environments.
    """

    def __init__(self):
        """Initialize the Combat Cartographer agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self.azure_client = AzureOpenAIClient()
        self._register_skills()
        
        # Store map references
        self.battle_maps = {}

    def _register_skills(self):
        """Register necessary skills for the Combat Cartographer agent."""
        # Will register skills once implemented
        pass

    async def generate_battle_map(self, environment_context: Dict[str, Any], combat_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a battle map based on environment context and combat requirements.
        
        Args:
            environment_context: Description of the environment (location, features, etc.)
            combat_context: Optional combat information to influence map generation
            
        Returns:
            Dict[str, Any]: Details of the generated battle map, including image reference
        """
        try:
            # Create map ID
            map_id = f"map_{len(self.battle_maps) + 1}"
            
            # Extract key environment details
            location = environment_context.get("location", "generic battlefield")
            terrain = environment_context.get("terrain", "plain")
            size = environment_context.get("size", "medium")
            features = environment_context.get("features", [])
            hazards = environment_context.get("hazards", [])
            
            # Create a detailed prompt for tactical battle map generation
            prompt = f"Top-down tactical battle map of a {terrain} {location}"
            if features:
                prompt += f" with {', '.join(features)}"
            if hazards:
                prompt += f", including {', '.join(hazards)}"
            
            # Add tactical map specifics
            prompt += ". Grid-based tactical map, D&D battle map style, clear terrain features, strategic positioning elements, top-down orthographic view, detailed but clear, suitable for tabletop RPG combat"
            
            # Generate the map using Azure OpenAI DALL-E
            image_result = await self.azure_client.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            if image_result["success"]:
                battle_map = {
                    "id": map_id,
                    "name": f"{location.capitalize()} Battle Map",
                    "description": prompt,
                    "size": size,
                    "terrain": terrain,
                    "features": features,
                    "hazards": hazards,
                    "image_url": image_result["image_url"],
                    "revised_prompt": image_result.get("revised_prompt", prompt),
                    "environment_context": environment_context,
                    "combat_context": combat_context,
                    "generation_details": {
                        "size": image_result["size"],
                        "quality": image_result["quality"],
                        "style": image_result["style"]
                    }
                }
            else:
                # Fallback to placeholder if generation fails
                battle_map = {
                    "id": map_id,
                    "name": f"{location.capitalize()} Battle Map",
                    "description": prompt,
                    "size": size,
                    "terrain": terrain,
                    "features": features,
                    "image_url": None,
                    "error": image_result.get("error", "Battle map generation failed")
                }
            
            # Store the battle map
            self.battle_maps[map_id] = battle_map
            
            return battle_map
            
        except Exception as e:
            logger.error(f"Error generating battle map: {str(e)}")
            return {"error": "Failed to generate battle map"}
    
    async def update_map_with_combat_state(self, map_id: str, combat_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing battle map with current combat state (positions, etc.).
        
        Args:
            map_id: ID of the map to update
            combat_state: Current state of the combat (positions, active elements)
            
        Returns:
            Dict[str, Any]: The updated battle map
        """
        try:
            if map_id not in self.battle_maps:
                return {"error": f"Battle map {map_id} not found"}
                
            battle_map = self.battle_maps[map_id]
            
            # TODO: Implement logic to update the map with current combat state
            # For now, we'll just return the existing map with a note
            
            battle_map["combat_state"] = combat_state
            battle_map["last_updated"] = "now"  # Would be an actual timestamp
            
            return battle_map
            
        except Exception as e:
            logger.error(f"Error updating battle map: {str(e)}")
            return {"error": "Failed to update battle map"}

# Singleton instance
combat_cartographer = CombatCartographerAgent()
