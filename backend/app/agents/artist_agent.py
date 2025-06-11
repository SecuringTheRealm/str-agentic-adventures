"""
Artist Agent - Generates visual imagery for the game.
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

class ArtistAgent:
    """
    Artist Agent that generates visual imagery based on narrative moments.
    This agent is responsible for creating character portraits, scene illustrations, and visual aids.
    """

    def __init__(self):
        """Initialize the Artist agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self._register_skills()
        
        # Store generated art references
        self.generated_art = {}

    def _register_skills(self):
        """Register necessary skills for the Artist agent."""
        # Will register skills once implemented
        pass

    def _get_image_service(self) -> AzureTextToImage:
        """Get the text-to-image service from the kernel."""
        # Get the service by type
        services = self.kernel.get_services_by_type(AzureTextToImage)
        if not services:
            raise ValueError("No text-to-image service configured in kernel")
        return services[0]

    async def _generate_and_store_image(self, description: str, image_id: str) -> str:
        """
        Generate an image and store it, returning the URL.
        
        Args:
            description: Description for image generation
            image_id: Unique identifier for the image
            
        Returns:
            str: URL or base64 data URL of the generated image
        """
        try:
            image_service = self._get_image_service()
            
            # Generate the image
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
            logger.error(f"Error generating image: {str(e)}")
            # Return a placeholder for failed generation
            return None

    async def generate_character_portrait(self, character_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visual portrait of a character.
        
        Args:
            character_details: Details of the character to visualize
            
        Returns:
            Dict[str, Any]: Details of the generated portrait, including image reference
        """
        try:
            # Generate a unique ID for this artwork
            art_id = f"portrait_{len(self.generated_art) + 1}"
            
            # Extract character details
            name = character_details.get("name", "Unnamed Character")
            race = character_details.get("race", "human")
            character_class = character_details.get("class", "adventurer")
            appearance = character_details.get("appearance", "")
            background = character_details.get("background", "")
            
            # Create a detailed description for the image generation
            description = f"High-quality fantasy character portrait of {name}, a {race} {character_class}."
            if appearance:
                description += f" {appearance}."
            if background:
                description += f" Background: {background}."
            description += " Digital art, detailed, fantasy RPG style, professional character portrait."
            
            # Generate the actual image
            image_url = await self._generate_and_store_image(description, art_id)
            
            portrait = {
                "id": art_id,
                "type": "character_portrait",
                "character_name": name,
                "description": description,
                "image_url": image_url
            }
            
            # Store the generated art
            self.generated_art[art_id] = portrait
            
            return portrait
            
        except Exception as e:
            logger.error(f"Error generating character portrait: {str(e)}")
            return {"error": "Failed to generate character portrait"}
    
    async def illustrate_scene(self, scene_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an illustration of a scene based on the provided context.
        
        Args:
            scene_context: Details of the scene to illustrate
            
        Returns:
            Dict[str, Any]: Details of the generated illustration, including image reference
        """
        try:
            # Generate a unique ID for this artwork
            art_id = f"scene_{len(self.generated_art) + 1}"
            
            # Extract scene details
            location = scene_context.get("location", "fantasy landscape")
            mood = scene_context.get("mood", "atmospheric")
            time = scene_context.get("time", "day")
            notable_elements = scene_context.get("notable_elements", [])
            environment_details = scene_context.get("environment_details", "")
            narrative_context = scene_context.get("narrative_context", "")
            
            # Create a detailed description for the image generation
            description = f"Fantasy scene illustration of a {mood} {location} during {time}."
            
            if notable_elements:
                description += f" Features: {', '.join(notable_elements)}."
            
            if environment_details:
                description += f" Environment: {environment_details}."
            
            if narrative_context:
                description += f" Context: {narrative_context}."
                
            description += " High-quality digital art, fantasy RPG style, detailed environment art, cinematic composition."
            
            # Generate the actual image
            image_url = await self._generate_and_store_image(description, art_id)
            
            illustration = {
                "id": art_id,
                "type": "scene_illustration",
                "location": location,
                "description": description,
                "image_url": image_url
            }
            
            # Store the generated art
            self.generated_art[art_id] = illustration
            
            return illustration
            
        except Exception as e:
            logger.error(f"Error illustrating scene: {str(e)}")
            return {"error": "Failed to illustrate scene"}
    
    async def create_item_visualization(self, item_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visual representation of an important item.
        
        Args:
            item_details: Details of the item to visualize
            
        Returns:
            Dict[str, Any]: Details of the generated item visualization, including image reference
        """
        try:
            # Generate a unique ID for this artwork
            art_id = f"item_{len(self.generated_art) + 1}"
            
            # Extract item details
            name = item_details.get("name", "Mysterious Item")
            item_type = item_details.get("type", "object")
            rarity = item_details.get("rarity", "common")
            description = item_details.get("description", "")
            magical_properties = item_details.get("magical_properties", "")
            materials = item_details.get("materials", "")
            
            # Create a detailed description for the image generation
            image_description = f"Fantasy {rarity} {item_type} named '{name}'."
            
            if description:
                image_description += f" Description: {description}."
            
            if magical_properties:
                image_description += f" Magical properties: {magical_properties}."
                
            if materials:
                image_description += f" Made of: {materials}."
                
            image_description += " High-quality item art, detailed fantasy game item, professional digital art, isolated on neutral background."
            
            # Generate the actual image
            image_url = await self._generate_and_store_image(image_description, art_id)
            
            item_visualization = {
                "id": art_id,
                "type": "item_visualization",
                "item_name": name,
                "description": image_description,
                "image_url": image_url
            }
            
            # Store the generated art
            self.generated_art[art_id] = item_visualization
            
            return item_visualization
            
        except Exception as e:
            logger.error(f"Error creating item visualization: {str(e)}")
            return {"error": "Failed to create item visualization"}

# Singleton instance
artist = ArtistAgent()
