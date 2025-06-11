"""
Combat Cartographer Agent - Generates tactical battle maps for combat encounters.
"""
import logging
from typing import Dict, Any, List, Optional
import uuid
import asyncio

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureTextToImage

from app.kernel_setup import kernel_manager
from app.config import settings

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
        
        # Map templates for different scenarios
        self.map_templates = {
            "dungeon_room": {
                "size_options": ["small", "medium", "large"],
                "common_features": ["stone walls", "torches", "stairs", "pillars", "treasure chest"],
                "tactical_elements": ["chokepoints", "cover", "elevation"]
            },
            "forest_clearing": {
                "size_options": ["small", "medium", "large"],
                "common_features": ["trees", "bushes", "rocks", "stream", "fallen logs"],
                "tactical_elements": ["natural cover", "difficult terrain", "ambush points"]
            },
            "castle_courtyard": {
                "size_options": ["medium", "large", "massive"],
                "common_features": ["battlements", "gates", "stairs", "fountain", "barracks"],
                "tactical_elements": ["high ground", "fortified positions", "multiple entrances"]
            },
            "cave_chamber": {
                "size_options": ["small", "medium", "large"],
                "common_features": ["stalactites", "stalagmites", "pools", "crevices", "crystal formations"],
                "tactical_elements": ["unstable ground", "limited visibility", "narrow passages"]
            },
            "tavern_interior": {
                "size_options": ["small", "medium"],
                "common_features": ["tables", "chairs", "bar", "fireplace", "stairs to upper floor"],
                "tactical_elements": ["furniture cover", "crowd obstacles", "multiple levels"]
            }
        }

    def _register_skills(self):
        """Register necessary skills for the Combat Cartographer agent."""
        # Initialize Azure Text-to-Image service for DALL-E if credentials available
        try:
            if (settings.azure_openai_endpoint and 
                settings.azure_openai_api_key):
                
                self.image_service = AzureTextToImage(
                    deployment_name="dall-e-3",  # Default DALL-E deployment name
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                logger.info("Azure Text-to-Image service initialized successfully")
            else:
                logger.warning("Azure OpenAI credentials not configured. Image generation will be disabled.")
                self.image_service = None
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Text-to-Image service: {str(e)}")
            self.image_service = None

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
            map_id = f"map_{str(uuid.uuid4())[:8]}"
            
            # Extract and enhance environment details
            location = environment_context.get("location", "generic")
            terrain = environment_context.get("terrain", "plain")
            size = environment_context.get("size", "medium")
            features = environment_context.get("features", [])
            lighting = environment_context.get("lighting", "normal")
            weather = environment_context.get("weather", "clear")
            
            # Apply template if specified
            template = environment_context.get("template")
            if template and template in self.map_templates:
                template_data = self.map_templates[template]
                # Enhance features with template suggestions
                if not features:
                    features = template_data["common_features"][:3]  # Use first 3 features
                # Ensure size is appropriate for template
                if size not in template_data["size_options"]:
                    size = template_data["size_options"][0]
            
            # Build enhanced map description for DALL-E
            map_description = self._build_map_description(
                location, terrain, size, features, lighting, weather, combat_context
            )
            
            # Generate the battle map image
            image_url = None
            if self.image_service:
                try:
                    image_url = await self._generate_map_image(map_description)
                except Exception as e:
                    logger.error(f"Failed to generate map image: {str(e)}")
            
            # Calculate tactical information
            tactical_info = self._calculate_tactical_info(size, terrain, features, combat_context)
            
            battle_map = {
                "id": map_id,
                "name": f"{location.capitalize()} Battle Map",
                "description": map_description,
                "size": size,
                "terrain": terrain,
                "features": features,
                "lighting": lighting,
                "weather": weather,
                "image_url": image_url,
                "tactical_info": tactical_info,
                "combat_state": combat_context or {},
                "template": template,
                "generation_timestamp": "now"  # Would be actual timestamp in production
            }
            
            # Store the battle map
            self.battle_maps[map_id] = battle_map
            logger.info(f"Generated battle map {map_id} for {location}")
            
            return battle_map
            
        except Exception as e:
            logger.error(f"Error generating battle map: {str(e)}")
            return {"error": "Failed to generate battle map"}
    
    def _build_map_description(self, location: str, terrain: str, size: str, features: List[str], 
                             lighting: str, weather: str, combat_context: Dict[str, Any] = None) -> str:
        """Build a detailed description for DALL-E image generation."""
        
        # Base description
        description = f"Top-down tactical battle map view of a {size} {terrain} {location}"
        
        # Add grid specification
        description += " with a tactical grid overlay"
        
        # Add features
        if features:
            description += f" featuring {', '.join(features)}"
        
        # Add lighting conditions
        if lighting != "normal":
            description += f" in {lighting} lighting"
        
        # Add weather if relevant and not clear
        if weather != "clear":
            description += f" during {weather} weather"
        
        # Add combat-specific elements
        if combat_context:
            participants = combat_context.get("participants", [])
            if participants:
                description += f" suitable for {len(participants)} combatants"
        
        # Add style specifications for tactical map
        description += (
            ". Fantasy RPG style, clear grid lines, detailed terrain textures, "
            "suitable for miniature placement, high contrast colors for tactical clarity"
        )
        
        return description
    
    async def _generate_map_image(self, description: str) -> Optional[str]:
        """Generate battle map image using Azure DALL-E."""
        try:
            # Generate the image
            result = await self.image_service.generate_image(
                description,
                width=1024,
                height=1024,
                quality="standard",
                style="vivid"  # For more dynamic and detailed maps
            )
            
            if result and hasattr(result, 'url'):
                return result.url
            elif isinstance(result, str):
                return result
            else:
                logger.warning("Unexpected image generation result format")
                return None
                
        except Exception as e:
            logger.error(f"Error generating map image: {str(e)}")
            return None
    
    def _calculate_tactical_info(self, size: str, terrain: str, features: List[str], 
                               combat_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate tactical information for the battle map."""
        
        # Grid dimensions based on size
        grid_dimensions = {
            "small": {"width": 15, "height": 15},
            "medium": {"width": 25, "height": 25},
            "large": {"width": 35, "height": 35},
            "massive": {"width": 50, "height": 50}
        }
        
        grid = grid_dimensions.get(size, grid_dimensions["medium"])
        
        # Movement considerations based on terrain
        movement_effects = {
            "plain": {"modifier": 1.0, "difficult_areas": []},
            "forest": {"modifier": 0.75, "difficult_areas": ["dense undergrowth"]},
            "mountain": {"modifier": 0.5, "difficult_areas": ["steep slopes", "rocky terrain"]},
            "swamp": {"modifier": 0.5, "difficult_areas": ["mud", "water"]},
            "desert": {"modifier": 0.75, "difficult_areas": ["sand dunes"]},
            "ice": {"modifier": 0.75, "difficult_areas": ["slippery ice"]},
            "dungeon": {"modifier": 1.0, "difficult_areas": ["debris"]},
            "urban": {"modifier": 1.0, "difficult_areas": ["rubble"]}
        }
        
        movement = movement_effects.get(terrain, movement_effects["plain"])
        
        # Cover opportunities based on features
        cover_points = []
        for feature in features:
            if any(cover_term in feature.lower() for cover_term in 
                  ["wall", "pillar", "tree", "rock", "table", "barrel"]):
                cover_points.append(feature)
        
        # Chokepoints and strategic positions
        strategic_info = []
        if any(choke in feature.lower() for feature in features for choke in 
              ["door", "bridge", "stairs", "passage"]):
            strategic_info.append("chokepoints_present")
        
        if any(elevation in feature.lower() for feature in features for elevation in 
              ["stairs", "platform", "hill", "balcony"]):
            strategic_info.append("elevation_advantage")
        
        return {
            "grid_size": grid,
            "movement_modifier": movement["modifier"],
            "difficult_terrain": movement["difficult_areas"],
            "cover_opportunities": cover_points,
            "strategic_elements": strategic_info,
            "recommended_participants": self._calculate_recommended_participants(size)
        }
    
    def _calculate_recommended_participants(self, size: str) -> Dict[str, int]:
        """Calculate recommended number of participants for map size."""
        participant_ranges = {
            "small": {"min": 2, "max": 4, "optimal": 3},
            "medium": {"min": 3, "max": 6, "optimal": 4},
            "large": {"min": 4, "max": 8, "optimal": 6},
            "massive": {"min": 6, "max": 12, "optimal": 8}
        }
        
        return participant_ranges.get(size, participant_ranges["medium"])
    
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
            
            # Update combat state
            battle_map["combat_state"] = combat_state
            battle_map["last_updated"] = "now"  # Would be an actual timestamp
            
            # Process combat positions if provided
            if "positions" in combat_state:
                battle_map["current_positions"] = combat_state["positions"]
            
            # Update turn information
            if "current_turn" in combat_state:
                battle_map["current_turn"] = combat_state["current_turn"]
            
            # Add combat round information
            if "round" in combat_state:
                battle_map["combat_round"] = combat_state["round"]
            
            # Calculate line of sight and movement options if positions are provided
            if "positions" in combat_state and "active_character" in combat_state:
                battle_map["tactical_analysis"] = self._analyze_tactical_situation(
                    battle_map, combat_state
                )
            
            logger.info(f"Updated battle map {map_id} with combat state")
            return battle_map
            
        except Exception as e:
            logger.error(f"Error updating battle map: {str(e)}")
            return {"error": "Failed to update battle map"}
    
    def _analyze_tactical_situation(self, battle_map: Dict[str, Any], combat_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current tactical situation on the map."""
        
        positions = combat_state.get("positions", {})
        active_character = combat_state.get("active_character")
        
        analysis = {
            "character_positions": positions,
            "active_character": active_character,
            "tactical_recommendations": []
        }
        
        # Basic tactical analysis
        if active_character and active_character in positions:
            char_pos = positions[active_character]
            
            # Find nearby enemies
            nearby_enemies = []
            nearby_allies = []
            
            for char_id, pos in positions.items():
                if char_id != active_character:
                    distance = self._calculate_grid_distance(char_pos, pos)
                    
                    # Determine if enemy or ally (simplified logic)
                    char_type = combat_state.get("character_types", {}).get(char_id, "unknown")
                    
                    if distance <= 5:  # Within 5 squares
                        if char_type == "enemy":
                            nearby_enemies.append({"id": char_id, "distance": distance})
                        elif char_type == "ally":
                            nearby_allies.append({"id": char_id, "distance": distance})
            
            analysis["nearby_enemies"] = nearby_enemies
            analysis["nearby_allies"] = nearby_allies
            
            # Generate tactical recommendations
            if nearby_enemies:
                analysis["tactical_recommendations"].append("Enemies in close range - consider positioning")
            
            if len(nearby_enemies) > 1:
                analysis["tactical_recommendations"].append("Multiple enemies nearby - seek cover or allies")
            
            # Check for cover opportunities near character
            tactical_info = battle_map.get("tactical_info", {})
            if tactical_info.get("cover_opportunities"):
                analysis["tactical_recommendations"].append("Cover opportunities available")
        
        return analysis
    
    def _calculate_grid_distance(self, pos1: Dict[str, int], pos2: Dict[str, int]) -> int:
        """Calculate grid distance between two positions."""
        x1, y1 = pos1.get("x", 0), pos1.get("y", 0)
        x2, y2 = pos2.get("x", 0), pos2.get("y", 0)
        
        # Use grid distance (max of x and y differences)
        return max(abs(x2 - x1), abs(y2 - y1))
    
    async def get_map_templates(self) -> Dict[str, Any]:
        """Get available map templates."""
        return {
            "templates": self.map_templates,
            "template_count": len(self.map_templates)
        }
    
    async def generate_map_variation(self, base_map_id: str, variation_type: str = "minor") -> Dict[str, Any]:
        """Generate a variation of an existing map."""
        try:
            if base_map_id not in self.battle_maps:
                return {"error": f"Base map {base_map_id} not found"}
            
            base_map = self.battle_maps[base_map_id]
            
            # Create new map ID
            variation_id = f"var_{str(uuid.uuid4())[:8]}"
            
            # Copy base map data
            variation_map = base_map.copy()
            variation_map["id"] = variation_id
            variation_map["base_map_id"] = base_map_id
            variation_map["variation_type"] = variation_type
            
            # Apply variations based on type
            if variation_type == "minor":
                # Minor changes to features
                features = variation_map.get("features", []).copy()
                if len(features) > 1:
                    # Remove one feature and add a different one
                    features.pop()
                    template = variation_map.get("template")
                    if template and template in self.map_templates:
                        available_features = self.map_templates[template]["common_features"]
                        new_feature = next((f for f in available_features if f not in features), "decorative elements")
                        features.append(new_feature)
                variation_map["features"] = features
            
            elif variation_type == "lighting":
                # Change lighting conditions
                lighting_options = ["dim", "bright", "dark", "magical", "flickering"]
                current_lighting = variation_map.get("lighting", "normal")
                new_lighting = next((l for l in lighting_options if l != current_lighting), "dim")
                variation_map["lighting"] = new_lighting
            
            elif variation_type == "weather":
                # Change weather conditions
                weather_options = ["rain", "fog", "snow", "storm", "wind"]
                current_weather = variation_map.get("weather", "clear")
                new_weather = next((w for w in weather_options if w != current_weather), "fog")
                variation_map["weather"] = new_weather
            
            # Regenerate image with variations
            if self.image_service:
                new_description = self._build_map_description(
                    variation_map.get("location", "generic"),
                    variation_map.get("terrain", "plain"),
                    variation_map.get("size", "medium"),
                    variation_map.get("features", []),
                    variation_map.get("lighting", "normal"),
                    variation_map.get("weather", "clear"),
                    variation_map.get("combat_state")
                )
                
                variation_map["description"] = new_description
                
                try:
                    variation_map["image_url"] = await self._generate_map_image(new_description)
                except Exception as e:
                    logger.error(f"Failed to generate variation image: {str(e)}")
                    variation_map["image_url"] = base_map.get("image_url")  # Fallback to base image
            
            # Store the variation
            self.battle_maps[variation_id] = variation_map
            
            logger.info(f"Generated map variation {variation_id} from base {base_map_id}")
            return variation_map
            
        except Exception as e:
            logger.error(f"Error generating map variation: {str(e)}")
            return {"error": "Failed to generate map variation"}

# Singleton instance
combat_cartographer = CombatCartographerAgent()
