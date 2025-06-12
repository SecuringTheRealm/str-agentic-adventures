"""
Artist Agent - Generates visual imagery for the game.
"""
import logging
from typing import Dict, Any

from app.azure_openai_client import AzureOpenAIClient
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
        self.azure_client = AzureOpenAIClient()
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
            gender = character_details.get("gender", "")
            description = character_details.get("description", "")
            
            # Create a detailed prompt for DALL-E
            prompt = f"Fantasy character portrait of {name}, a {race} {character_class}"
            if gender:
                prompt = f"Fantasy character portrait of {name}, a {gender} {race} {character_class}"
            
            # Add physical description if available
            if description:
                prompt += f". {description}"
            
            # Add D&D fantasy styling
            prompt += ". High quality digital art, fantasy RPG character, detailed armor or clothing, atmospheric lighting, professional character portrait"
            
            # Generate the image using Azure OpenAI DALL-E
            image_result = await self.azure_client.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            if image_result["success"]:
                portrait = {
                    "id": art_id,
                    "type": "character_portrait",
                    "character_name": name,
                    "description": prompt,
                    "image_url": image_result["image_url"],
                    "revised_prompt": image_result.get("revised_prompt", prompt),
                    "generation_details": {
                        "size": image_result["size"],
                        "quality": image_result["quality"],
                        "style": image_result["style"]
                    }
                }
            else:
                # Fallback to placeholder if generation fails
                portrait = {
                    "id": art_id,
                    "type": "character_portrait",
                    "character_name": name,
                    "description": prompt,
                    "image_url": None,
                    "error": image_result.get("error", "Image generation failed")
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
            weather = scene_context.get("weather", "")
            
            # Create a detailed prompt for DALL-E
            prompt = f"Fantasy illustration of a {mood} {location} during {time}"
            if notable_elements:
                prompt += f", featuring {', '.join(notable_elements)}"
            if weather:
                prompt += f", {weather} weather"
            
            # Add D&D fantasy styling
            prompt += ". High quality digital art, fantasy RPG environment, detailed textures, atmospheric lighting, cinematic composition, concept art style"
            
            # Generate the image using Azure OpenAI DALL-E
            image_result = await self.azure_client.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            if image_result["success"]:
                illustration = {
                    "id": art_id,
                    "type": "scene_illustration",
                    "location": location,
                    "description": prompt,
                    "image_url": image_result["image_url"],
                    "revised_prompt": image_result.get("revised_prompt", prompt),
                    "scene_details": {
                        "mood": mood,
                        "time": time,
                        "notable_elements": notable_elements,
                        "weather": weather
                    },
                    "generation_details": {
                        "size": image_result["size"],
                        "quality": image_result["quality"],
                        "style": image_result["style"]
                    }
                }
            else:
                # Fallback to placeholder if generation fails
                illustration = {
                    "id": art_id,
                    "type": "scene_illustration",
                    "location": location,
                    "description": prompt,
                    "image_url": None,
                    "error": image_result.get("error", "Image generation failed")
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
            magical = item_details.get("magical", False)
            
            # Create a detailed prompt for DALL-E
            prompt = f"Fantasy {rarity} {item_type} named '{name}'"
            if magical:
                prompt += ", magical item with glowing or mystical properties"
            if description:
                prompt += f". {description}"
            
            # Add D&D fantasy styling
            prompt += ". High quality digital art, fantasy RPG item, detailed textures, studio lighting, clean background, item showcase style"
            
            # Generate the image using Azure OpenAI DALL-E
            image_result = await self.azure_client.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            if image_result["success"]:
                item_visualization = {
                    "id": art_id,
                    "type": "item_visualization",
                    "item_name": name,
                    "description": prompt,
                    "image_url": image_result["image_url"],
                    "revised_prompt": image_result.get("revised_prompt", prompt),
                    "item_details": {
                        "item_type": item_type,
                        "rarity": rarity,
                        "magical": magical,
                        "description": description
                    },
                    "generation_details": {
                        "size": image_result["size"],
                        "quality": image_result["quality"],
                        "style": image_result["style"]
                    }
                }
            else:
                # Fallback to placeholder if generation fails
                item_visualization = {
                    "id": art_id,
                    "type": "item_visualization",
                    "item_name": name,
                    "description": prompt,
                    "image_url": None,
                    "error": image_result.get("error", "Image generation failed")
                }
            
            # Store the generated art
            self.generated_art[art_id] = item_visualization
            
            return item_visualization
            
        except Exception as e:
            logger.error(f"Error creating item visualization: {str(e)}")
            return {"error": "Failed to create item visualization"}

# Lazy singleton instance
_artist = None

def get_artist():
    """Get the artist instance, creating it if necessary."""
    global _artist
    if _artist is None:
        _artist = ArtistAgent()
    return _artist

# For backward compatibility during import-time checks
artist = None
