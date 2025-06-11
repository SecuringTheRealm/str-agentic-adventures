"""
Artist Agent - Generates visual imagery for the game.
"""
import logging
from typing import Dict, Any, List, Optional

import semantic_kernel as sk

from app.kernel_setup import kernel_manager
from app.services.image_generation_service import image_service

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
            equipment = character_details.get("equipment", "")
            
            # Create a detailed prompt for image generation
            prompt_parts = [f"Fantasy character portrait of {name}, a {race} {character_class}"]
            
            if appearance:
                prompt_parts.append(f"Appearance: {appearance}")
            if equipment:
                prompt_parts.append(f"Equipment: {equipment}")
                
            prompt_parts.extend([
                "High quality digital art",
                "Fantasy RPG style",
                "Detailed character portrait",
                "Professional artwork"
            ])
            
            prompt = ". ".join(prompt_parts)
            
            # Generate the image using the image service
            image_result = await image_service.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="natural"
            )
            
            portrait = {
                "id": art_id,
                "type": "character_portrait",
                "character_name": name,
                "description": prompt,
                "image_url": image_result.get("image_url"),
                "image_id": image_result.get("id"),
                "generated_at": image_result.get("created_at"),
                "placeholder": image_result.get("placeholder", False)
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
            weather = scene_context.get("weather", "")
            notable_elements = scene_context.get("notable_elements", [])
            characters_present = scene_context.get("characters_present", [])
            
            # Create a detailed prompt for image generation
            prompt_parts = [f"Fantasy scene illustration of a {mood} {location} during {time}"]
            
            if weather:
                prompt_parts.append(f"Weather: {weather}")
            if notable_elements:
                prompt_parts.append(f"Notable features: {', '.join(notable_elements)}")
            if characters_present:
                prompt_parts.append(f"Characters present: {', '.join(characters_present)}")
                
            prompt_parts.extend([
                "High quality digital art",
                "Fantasy RPG environment",
                "Atmospheric lighting",
                "Detailed landscape",
                "Professional game art style"
            ])
            
            prompt = ". ".join(prompt_parts)
            
            # Generate the image using the image service
            image_result = await image_service.generate_image(
                prompt=prompt,
                size="1792x1024",  # Landscape format for scenes
                quality="standard",
                style="natural"
            )
            
            illustration = {
                "id": art_id,
                "type": "scene_illustration",
                "location": location,
                "description": prompt,
                "image_url": image_result.get("image_url"),
                "image_id": image_result.get("id"),
                "generated_at": image_result.get("created_at"),
                "placeholder": image_result.get("placeholder", False)
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
            material = item_details.get("material", "")
            
            # Create a detailed prompt for image generation
            prompt_parts = [f"Fantasy {rarity} {item_type} named '{name}'"]
            
            if description:
                prompt_parts.append(f"Description: {description}")
            if magical_properties:
                prompt_parts.append(f"Magical properties: {magical_properties}")
            if material:
                prompt_parts.append(f"Made of: {material}")
                
            prompt_parts.extend([
                "High quality digital art",
                "Fantasy RPG item",
                "Detailed equipment illustration",
                "Clean background",
                "Professional game asset style"
            ])
            
            prompt = ". ".join(prompt_parts)
            
            # Generate the image using the image service
            image_result = await image_service.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="natural"
            )
            
            item_visualization = {
                "id": art_id,
                "type": "item_visualization",
                "item_name": name,
                "description": prompt,
                "image_url": image_result.get("image_url"),
                "image_id": image_result.get("id"),
                "generated_at": image_result.get("created_at"),
                "placeholder": image_result.get("placeholder", False)
            }
            
            # Store the generated art
            self.generated_art[art_id] = item_visualization
            
            return item_visualization
            
        except Exception as e:
            logger.error(f"Error creating item visualization: {str(e)}")
            return {"error": "Failed to create item visualization"}

# Singleton instance
artist = ArtistAgent()
