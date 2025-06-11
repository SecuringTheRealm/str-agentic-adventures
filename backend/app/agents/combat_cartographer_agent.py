"""
Combat Cartographer Agent - Generates tactical battle maps for combat encounters.
"""
import logging
from typing import Dict, Any, List, Optional
import base64
import os
from datetime import datetime

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureTextToImage

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
        self._register_skills()
        
        # Store map references
        self.battle_maps = {}

    def _register_skills(self):
        """Register necessary skills for the Combat Cartographer agent."""
        # Will register skills once implemented
        pass

    def _get_image_service(self) -> AzureTextToImage:
        """Get the text-to-image service from the kernel."""
        # Get the service by type
        services = self.kernel.get_services_by_type(AzureTextToImage)
        if not services:
            raise ValueError("No text-to-image service configured in kernel")
        return services[0]

    async def _generate_and_store_map_image(self, description: str, map_id: str) -> str:
        """
        Generate a battle map image and store it, returning the URL.
        
        Args:
            description: Description for map generation
            map_id: Unique identifier for the map
            
        Returns:
            str: URL or base64 data URL of the generated map
        """
        try:
            image_service = self._get_image_service()
            
            # Generate the map image
            image_data = await image_service.generate_image(
                description=description,
                width=1024,
                height=1024
            )
            
            # For now, return as base64 data URL since we don't have blob storage set up
            if isinstance(image_data, bytes):
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/png;base64,{base64_data}"
            elif isinstance(image_data, str):
                # Assume it's already a URL or base64 string
                return image_data
            else:
                raise ValueError(f"Unexpected image data type: {type(image_data)}")
                
        except Exception as e:
            logger.error(f"Error generating map image: {str(e)}")
            # Return a placeholder for failed generation
            return None

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
            location = environment_context.get("location", "generic")
            terrain = environment_context.get("terrain", "plain")
            size = environment_context.get("size", "medium")
            features = environment_context.get("features", [])
            obstacles = environment_context.get("obstacles", [])
            cover_elements = environment_context.get("cover_elements", [])
            
            # Create a detailed description for tactical battle map generation
            map_description = f"Top-down tactical battle map of a {terrain} {location}, grid-based RPG battle map, {size} size."
            
            if features:
                map_description += f" Environmental features: {', '.join(features)}."
                
            if obstacles:
                map_description += f" Obstacles: {', '.join(obstacles)}."
                
            if cover_elements:
                map_description += f" Cover elements: {', '.join(cover_elements)}."
                
            if combat_context:
                encounter_type = combat_context.get("encounter_type", "")
                if encounter_type:
                    map_description += f" Designed for {encounter_type} encounter."
                    
            map_description += " Professional tactical grid map, clear visibility, strategic positioning, fantasy RPG style."
            
            # Generate the actual battle map image
            image_url = await self._generate_and_store_map_image(map_description, map_id)
                
            battle_map = {
                "id": map_id,
                "name": f"{location.capitalize()} Battle Map",
                "description": map_description,
                "size": size,
                "terrain": terrain,
                "features": features,
                "image_url": image_url
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
