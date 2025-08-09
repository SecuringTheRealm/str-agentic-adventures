"""
Scene Composition Plugin for the Semantic Kernel.
This plugin provides scene illustration and composition capabilities for RPG environments.
"""

import logging
from typing import Any

from semantic_kernel.functions import kernel_function

from app.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)


class SceneCompositionPlugin:
    """
    Plugin that provides scene illustration and composition capabilities.
    Creates detailed environmental scenes, locations, and atmospheric illustrations.
    """

    def __init__(self) -> None:
        """Initialize the scene composition plugin."""
        self.azure_client = AzureOpenAIClient()
        self.scene_library = {}
        self.location_templates = {}
        self.composition_history = []

    @kernel_function(
        description="Generate a detailed scene illustration based on location and context.",
        name="illustrate_scene",
    )
    def illustrate_scene(
        self,
        location_name: str,
        location_type: str = "outdoor",
        time_of_day: str = "day",
        weather: str = "clear",
        mood: str = "neutral",
        notable_elements: str = "",
        characters_present: str = "",
    ) -> dict[str, Any]:
        """
        Generate a detailed scene illustration.

        Args:
            location_name: Name of the location
            location_type: Type of location (outdoor, indoor, dungeon, city, etc.)
            time_of_day: Time (dawn, day, dusk, night)
            weather: Weather conditions
            mood: Mood/atmosphere of the scene
            notable_elements: Comma-separated list of notable elements
            characters_present: Comma-separated list of characters in scene

        Returns:
            Dict[str, Any]: Generated scene illustration details
        """
        try:
            # Parse notable elements and characters
            elements = [e.strip() for e in notable_elements.split(",") if e.strip()]
            characters = [c.strip() for c in characters_present.split(",") if c.strip()]

            # Build scene prompt
            scene_prompt = self._build_scene_prompt(
                location_name,
                location_type,
                time_of_day,
                weather,
                mood,
                elements,
                characters,
            )

            # Generate the scene
            result = self.azure_client.generate_image(
                prompt=scene_prompt,
                size="1792x1024",  # Landscape format for scenes
                quality="standard",
                style="vivid",
            )

            # Create scene ID
            scene_id = f"scene_{len(self.scene_library) + 1}"

            # Store scene data
            scene_data = {
                "scene_id": scene_id,
                "location_name": location_name,
                "location_type": location_type,
                "time_of_day": time_of_day,
                "weather": weather,
                "mood": mood,
                "notable_elements": elements,
                "characters_present": characters,
                "generation_prompt": scene_prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp(),
                "variations": [],
            }

            self.scene_library[scene_id] = scene_data
            self.composition_history.append(scene_data)

            if result.get("success"):
                return {
                    "status": "success",
                    "scene_id": scene_id,
                    "location_name": location_name,
                    "image_url": result["image_url"],
                    "prompt_used": scene_prompt,
                    "revised_prompt": result.get("revised_prompt", scene_prompt),
                    "scene_details": {
                        "type": location_type,
                        "time": time_of_day,
                        "weather": weather,
                        "mood": mood,
                        "elements_count": len(elements),
                    },
                }
            return {
                "status": "error",
                "scene_id": scene_id,
                "error": result.get("error", "Scene generation failed"),
            }

        except Exception as e:
            logger.error(f"Error illustrating scene: {str(e)}")
            return {"status": "error", "error": f"Scene illustration failed: {str(e)}"}

    @kernel_function(
        description="Create a location template for consistent scene generation.",
        name="create_location_template",
    )
    def create_location_template(
        self,
        template_name: str,
        location_type: str,
        base_description: str,
        key_features: str = "",
        lighting_notes: str = "",
        composition_style: str = "",
    ) -> dict[str, Any]:
        """
        Create a location template for consistent scene generation.

        Args:
            template_name: Name for the template
            location_type: Type of location
            base_description: Base description of the location
            key_features: Comma-separated key features
            lighting_notes: Notes about lighting for this location type
            composition_style: Preferred composition style

        Returns:
            Dict[str, Any]: Created location template
        """
        try:
            # Parse features
            features = [f.strip() for f in key_features.split(",") if f.strip()]

            # Create template
            template = {
                "template_name": template_name,
                "location_type": location_type,
                "base_description": base_description,
                "key_features": features,
                "lighting_notes": lighting_notes,
                "composition_style": composition_style,
                "usage_count": 0,
                "created_timestamp": self._get_timestamp(),
                "generated_scenes": [],
            }

            self.location_templates[template_name] = template

            return {
                "status": "success",
                "template_name": template_name,
                "location_type": location_type,
                "key_features": features,
                "message": f"Location template '{template_name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating location template: {str(e)}")
            return {
                "status": "error",
                "error": f"Location template creation failed: {str(e)}",
            }

    @kernel_function(
        description="Generate a scene variation with different lighting or weather.",
        name="generate_scene_variation",
    )
    def generate_scene_variation(
        self,
        base_scene_id: str,
        variation_type: str = "lighting",
        variation_description: str = "",
    ) -> dict[str, Any]:
        """
        Generate a scene variation with different conditions.

        Args:
            base_scene_id: ID of the base scene
            variation_type: Type of variation (lighting, weather, time, mood)
            variation_description: Description of the variation

        Returns:
            Dict[str, Any]: Generated scene variation
        """
        try:
            if base_scene_id not in self.scene_library:
                return {"status": "error", "error": "Base scene not found"}

            base_scene = self.scene_library[base_scene_id]

            # Build variation prompt
            variation_prompt = self._build_variation_prompt(
                base_scene, variation_type, variation_description
            )

            # Generate the variation
            result = self.azure_client.generate_image(
                prompt=variation_prompt,
                size="1792x1024",
                quality="standard",
                style="vivid",
            )

            # Create variation data
            variation_data = {
                "variation_id": f"{base_scene_id}_var_{len(base_scene['variations']) + 1}",
                "base_scene_id": base_scene_id,
                "variation_type": variation_type,
                "variation_description": variation_description,
                "generation_prompt": variation_prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp(),
            }

            # Store variation
            base_scene["variations"].append(variation_data)

            if result.get("success"):
                return {
                    "status": "success",
                    "variation_id": variation_data["variation_id"],
                    "base_scene_id": base_scene_id,
                    "variation_type": variation_type,
                    "image_url": result["image_url"],
                    "prompt_used": variation_prompt,
                    "location_name": base_scene["location_name"],
                }
            return {
                "status": "error",
                "error": result.get("error", "Scene variation generation failed"),
            }

        except Exception as e:
            logger.error(f"Error generating scene variation: {str(e)}")
            return {
                "status": "error",
                "error": f"Scene variation generation failed: {str(e)}",
            }

    @kernel_function(
        description="Create a cinematic establishing shot for a location.",
        name="create_establishing_shot",
    )
    def create_establishing_shot(
        self,
        location_name: str,
        scale: str = "wide",
        focus_point: str = "",
        story_context: str = "",
    ) -> dict[str, Any]:
        """
        Create a cinematic establishing shot for a location.

        Args:
            location_name: Name of the location
            scale: Scale of the shot (wide, medium, close)
            focus_point: Main focus point of the composition
            story_context: Context for the narrative moment

        Returns:
            Dict[str, Any]: Generated establishing shot
        """
        try:
            # Build establishing shot prompt
            prompt = self._build_establishing_shot_prompt(
                location_name, scale, focus_point, story_context
            )

            # Determine optimal size based on scale
            if scale == "wide":
                size = "1792x1024"
            elif scale == "medium":
                size = "1024x1024"
            else:  # close
                size = "1024x1792"

            # Generate the establishing shot
            result = self.azure_client.generate_image(
                prompt=prompt,
                size=size,
                quality="hd",  # Higher quality for cinematic shots
                style="vivid",
            )

            # Create shot data
            shot_id = f"establishing_{len(self.composition_history) + 1}"
            shot_data = {
                "shot_id": shot_id,
                "shot_type": "establishing",
                "location_name": location_name,
                "scale": scale,
                "focus_point": focus_point,
                "story_context": story_context,
                "generation_prompt": prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp(),
            }

            self.composition_history.append(shot_data)

            if result.get("success"):
                return {
                    "status": "success",
                    "shot_id": shot_id,
                    "location_name": location_name,
                    "scale": scale,
                    "image_url": result["image_url"],
                    "prompt_used": prompt,
                    "composition_notes": self._analyze_composition(scale, focus_point),
                }
            return {
                "status": "error",
                "error": result.get("error", "Establishing shot generation failed"),
            }

        except Exception as e:
            logger.error(f"Error creating establishing shot: {str(e)}")
            return {
                "status": "error",
                "error": f"Establishing shot creation failed: {str(e)}",
            }

    @kernel_function(
        description="Generate a battle map overview for tactical combat.",
        name="generate_battle_map",
    )
    def generate_battle_map(
        self,
        battlefield_name: str,
        terrain_type: str = "mixed",
        tactical_elements: str = "",
        scale_reference: str = "grid",
    ) -> dict[str, Any]:
        """
        Generate a battle map overview for tactical combat.

        Args:
            battlefield_name: Name of the battlefield
            terrain_type: Type of terrain (forest, plains, urban, dungeon, etc.)
            tactical_elements: Comma-separated tactical elements (cover, obstacles, etc.)
            scale_reference: Scale reference type (grid, miniatures, overview)

        Returns:
            Dict[str, Any]: Generated battle map
        """
        try:
            # Parse tactical elements
            elements = [e.strip() for e in tactical_elements.split(",") if e.strip()]

            # Build battle map prompt
            map_prompt = self._build_battle_map_prompt(
                battlefield_name, terrain_type, elements, scale_reference
            )

            # Generate the battle map
            result = self.azure_client.generate_image(
                prompt=map_prompt,
                size="1024x1024",  # Square format for battle maps
                quality="standard",
                style="natural",  # More realistic for tactical use
            )

            # Create map data
            map_id = f"battlemap_{len(self.scene_library) + 1}"
            map_data = {
                "map_id": map_id,
                "map_type": "battle",
                "battlefield_name": battlefield_name,
                "terrain_type": terrain_type,
                "tactical_elements": elements,
                "scale_reference": scale_reference,
                "generation_prompt": map_prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp(),
            }

            self.scene_library[map_id] = map_data

            if result.get("success"):
                return {
                    "status": "success",
                    "map_id": map_id,
                    "battlefield_name": battlefield_name,
                    "terrain_type": terrain_type,
                    "image_url": result["image_url"],
                    "prompt_used": map_prompt,
                    "tactical_notes": self._generate_tactical_notes(
                        terrain_type, elements
                    ),
                }
            return {
                "status": "error",
                "error": result.get("error", "Battle map generation failed"),
            }

        except Exception as e:
            logger.error(f"Error generating battle map: {str(e)}")
            return {
                "status": "error",
                "error": f"Battle map generation failed: {str(e)}",
            }

    @kernel_function(
        description="Get composition analysis and recommendations for scenes.",
        name="analyze_scene_composition",
    )
    def analyze_scene_composition(self, scene_id: str) -> dict[str, Any]:
        """
        Analyze scene composition and provide recommendations.

        Args:
            scene_id: ID of the scene to analyze

        Returns:
            Dict[str, Any]: Composition analysis and recommendations
        """
        try:
            if scene_id not in self.scene_library:
                return {"status": "error", "error": "Scene not found"}

            scene = self.scene_library[scene_id]

            # Analyze composition elements
            analysis = {
                "scene_id": scene_id,
                "location_name": scene["location_name"],
                "composition_elements": self._analyze_scene_elements(scene),
                "lighting_analysis": self._analyze_lighting(scene),
                "depth_analysis": self._analyze_depth(scene),
                "focal_points": self._identify_focal_points(scene),
                "recommendations": self._generate_composition_recommendations(scene),
            }

            return {"status": "success", "analysis": analysis}

        except Exception as e:
            logger.error(f"Error analyzing scene composition: {str(e)}")
            return {
                "status": "error",
                "error": f"Scene composition analysis failed: {str(e)}",
            }

    def _build_scene_prompt(
        self,
        location: str,
        loc_type: str,
        time: str,
        weather: str,
        mood: str,
        elements: list[str],
        characters: list[str],
    ) -> str:
        """Build a comprehensive scene prompt."""
        # Start with location description
        prompt = f"Fantasy {loc_type} scene of {location}"

        # Add time and weather
        prompt += f" during {time}"
        if weather and weather != "clear":
            prompt += f", {weather} weather"

        # Add mood/atmosphere
        if mood and mood != "neutral":
            prompt += f", {mood} atmosphere"

        # Add notable elements
        if elements:
            prompt += f", featuring {', '.join(elements)}"

        # Add characters if present
        if characters:
            if len(characters) == 1:
                prompt += f", with {characters[0]} visible in the scene"
            else:
                prompt += f", with {', '.join(characters[:-1])} and {characters[-1]} visible in the scene"

        # Add composition and quality enhancers
        composition_style = self._get_composition_style(loc_type)
        prompt += f". {composition_style}"

        # Add quality descriptors
        prompt += ". High quality digital art, fantasy RPG environment, detailed textures, atmospheric lighting, cinematic composition, concept art style"

        return prompt

    def _build_variation_prompt(
        self, base_scene: dict[str, Any], var_type: str, description: str
    ) -> str:
        """Build a variation prompt based on base scene."""
        base_prompt = base_scene["generation_prompt"]

        # Modify based on variation type
        if var_type == "lighting":
            if "dawn" in description or "sunrise" in description:
                base_prompt = base_prompt.replace("during day", "during dawn")
                base_prompt += ". Golden hour lighting, warm sunrise colors"
            elif "dusk" in description or "sunset" in description:
                base_prompt = base_prompt.replace("during day", "during dusk")
                base_prompt += ". Orange sunset lighting, dramatic sky"
            elif "night" in description:
                base_prompt = base_prompt.replace("during day", "during night")
                base_prompt += ". Moonlight illumination, mysterious shadows"
            elif "storm" in description:
                base_prompt += ". Dramatic storm lighting, dark clouds, lightning"

        elif var_type == "weather":
            if description:
                # Replace existing weather or add new
                base_prompt += f". {description}"

        elif var_type == "mood":
            if description:
                base_prompt += f". {description} mood and atmosphere"

        elif var_type == "time":
            # Update time references
            if description:
                base_prompt = base_prompt.replace(
                    f"during {base_scene['time_of_day']}", f"during {description}"
                )

        return base_prompt

    def _build_establishing_shot_prompt(
        self, location: str, scale: str, focus: str, context: str
    ) -> str:
        """Build an establishing shot prompt."""
        if scale == "wide":
            prompt = f"Wide cinematic establishing shot of {location}"
            prompt += ". Sweeping vista, grand scale, epic composition"
        elif scale == "medium":
            prompt = f"Medium establishing shot of {location}"
            prompt += ". Balanced composition, clear details"
        else:  # close
            prompt = f"Close establishing shot of {location}"
            prompt += ". Intimate view, detailed foreground"

        if focus:
            prompt += f", focusing on {focus}"

        if context:
            prompt += f". {context}"

        # Add cinematic quality
        prompt += ". Cinematic lighting, dramatic composition, film-like quality, establishing shot style, atmospheric depth"

        return prompt

    def _build_battle_map_prompt(
        self, battlefield: str, terrain: str, elements: list[str], scale: str
    ) -> str:
        """Build a battle map prompt."""
        prompt = f"Tactical battle map of {battlefield}, {terrain} terrain"

        if elements:
            prompt += f", with {', '.join(elements)}"

        if scale == "grid":
            prompt += ". Top-down view, grid overlay, tactical perspective"
        elif scale == "miniatures":
            prompt += ". Miniature gaming perspective, clear terrain features"
        else:  # overview
            prompt += ". Strategic overview, clear battlefield layout"

        # Add tactical art style
        prompt += ". Clean tactical art style, clear visibility, strategic gaming map, detailed terrain features"

        return prompt

    def _get_composition_style(self, location_type: str) -> str:
        """Get appropriate composition style for location type."""
        styles = {
            "outdoor": "Sweeping landscape composition with natural depth",
            "indoor": "Architectural composition with interesting angles",
            "dungeon": "Atmospheric perspective with dramatic shadows",
            "city": "Urban composition with leading lines and depth",
            "forest": "Natural framing with organic elements",
            "castle": "Gothic composition with vertical emphasis",
            "tavern": "Cozy interior composition with warm lighting",
            "battlefield": "Dynamic composition suggesting movement and conflict",
        }

        return styles.get(location_type, "Balanced composition with clear focal points")

    def _analyze_composition(self, scale: str, focus: str) -> list[str]:
        """Analyze composition based on scale and focus."""
        notes = []

        if scale == "wide":
            notes.append("Uses wide framing for epic scope")
            notes.append("Emphasizes environmental storytelling")
        elif scale == "medium":
            notes.append("Balanced composition for clarity")
            notes.append("Good balance of detail and context")
        else:
            notes.append("Intimate framing for detail focus")
            notes.append("Strong foreground emphasis")

        if focus:
            notes.append(f"Compositional focus on {focus}")

        return notes

    def _generate_tactical_notes(self, terrain: str, elements: list[str]) -> list[str]:
        """Generate tactical notes for battle map."""
        notes = []

        # Terrain-specific notes
        terrain_notes = {
            "forest": [
                "Dense vegetation provides cover",
                "Limited sight lines",
                "Difficult terrain for movement",
            ],
            "plains": [
                "Open terrain with clear sight lines",
                "Limited cover options",
                "Good for mounted combat",
            ],
            "urban": [
                "Buildings provide cover and elevation",
                "Narrow streets limit movement",
                "Opportunities for ambush",
            ],
            "dungeon": [
                "Confined spaces limit tactics",
                "Chokepoints for defensive positions",
                "Light sources important",
            ],
            "mountains": [
                "Elevation advantages",
                "Difficult terrain",
                "Risk of falling damage",
            ],
            "swamp": [
                "Difficult terrain throughout",
                "Limited visibility",
                "Environmental hazards",
            ],
        }

        notes.extend(terrain_notes.get(terrain, ["Standard terrain considerations"]))

        # Element-specific notes
        for element in elements:
            if "cover" in element.lower():
                notes.append("Provides partial cover for ranged attacks")
            elif "obstacle" in element.lower():
                notes.append("Blocks movement and line of sight")
            elif "elevation" in element.lower():
                notes.append("Provides tactical advantage and cover")

        return notes

    def _analyze_scene_elements(self, scene: dict[str, Any]) -> dict[str, Any]:
        """Analyze compositional elements of a scene."""
        return {
            "location_type": scene["location_type"],
            "environmental_elements": len(scene.get("notable_elements", [])),
            "character_presence": len(scene.get("characters_present", [])),
            "atmospheric_conditions": {
                "time": scene["time_of_day"],
                "weather": scene["weather"],
                "mood": scene["mood"],
            },
        }

    def _analyze_lighting(self, scene: dict[str, Any]) -> dict[str, str]:
        """Analyze lighting characteristics."""
        time = scene["time_of_day"]
        weather = scene["weather"]

        return {
            "primary_source": self._get_primary_light_source(time, weather),
            "direction": self._get_light_direction(time),
            "quality": self._get_light_quality(time, weather),
            "mood_impact": self._get_lighting_mood_impact(time, weather),
        }


    def _analyze_depth(self, scene: dict[str, Any]) -> dict[str, str]:
        """Analyze depth composition."""
        return {
            "foreground": "Elements closest to viewer",
            "midground": "Main subject area",
            "background": "Environmental context and atmosphere",
            "depth_technique": self._get_depth_technique(scene["location_type"]),
        }

    def _identify_focal_points(self, scene: dict[str, Any]) -> list[str]:
        """Identify main focal points in the scene."""
        focal_points = []

        if scene.get("characters_present"):
            focal_points.append("Character figures")

        if scene.get("notable_elements"):
            focal_points.extend(scene["notable_elements"][:2])  # Top 2 elements

        # Add architectural or natural focal points based on location type
        loc_type = scene["location_type"]
        if loc_type == "castle":
            focal_points.append("Castle architecture")
        elif loc_type == "forest":
            focal_points.append("Tree composition")
        elif loc_type == "dungeon":
            focal_points.append("Dungeon entrance or passage")

        return focal_points[:3]  # Limit to 3 main focal points

    def _generate_composition_recommendations(self, scene: dict[str, Any]) -> list[str]:
        """Generate composition improvement recommendations."""
        recommendations = []

        # Based on location type
        loc_type = scene["location_type"]
        if loc_type == "outdoor":
            recommendations.append(
                "Consider using foreground elements to frame the scene"
            )
        elif loc_type == "indoor":
            recommendations.append("Use architectural lines to guide the viewer's eye")

        # Based on lighting
        if scene["time_of_day"] == "night":
            recommendations.append("Ensure adequate light sources for visibility")

        # Based on elements
        if len(scene.get("notable_elements", [])) > 3:
            recommendations.append(
                "Consider simplifying composition to focus on key elements"
            )

        # General recommendations
        recommendations.append("Apply rule of thirds for balanced composition")
        recommendations.append("Use depth of field to establish focal hierarchy")

        return recommendations

    def _get_primary_light_source(self, time: str, weather: str) -> str:
        """Determine primary light source."""
        if time == "night":
            return "Moonlight or artificial sources"
        if time == "dawn" or time == "dusk":
            return "Low-angle sunlight"
        if weather == "stormy":
            return "Diffused sunlight through clouds"
        return "Direct sunlight"

    def _get_light_direction(self, time: str) -> str:
        """Determine light direction."""
        directions = {
            "dawn": "Low angle from east",
            "day": "High angle overhead",
            "dusk": "Low angle from west",
            "night": "Various artificial sources",
        }
        return directions.get(time, "Overhead")

    def _get_light_quality(self, time: str, weather: str) -> str:
        """Determine light quality."""
        if weather == "stormy":
            return "Dramatic and harsh"
        if time == "dawn" or time == "dusk":
            return "Warm and golden"
        if time == "night":
            return "Cool and mysterious"
        return "Bright and natural"

    def _get_lighting_mood_impact(self, time: str, weather: str) -> str:
        """Determine lighting mood impact."""
        if time == "night":
            return "Creates mystery and tension"
        if weather == "stormy":
            return "Adds drama and conflict"
        if time == "dawn":
            return "Suggests hope and new beginnings"
        if time == "dusk":
            return "Creates contemplative atmosphere"
        return "Provides clear, neutral illumination"

    def _get_depth_technique(self, location_type: str) -> str:
        """Get appropriate depth technique for location."""
        techniques = {
            "outdoor": "Atmospheric perspective with distant mountains or horizon",
            "forest": "Layered tree depth with filtering light",
            "dungeon": "Perspective lines of corridors and chambers",
            "city": "Architectural depth with building receding lines",
            "castle": "Vertical depth emphasizing height and grandeur",
        }
        return techniques.get(
            location_type, "Linear perspective with foreground, midground, background"
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime

        return datetime.datetime.now().isoformat()
