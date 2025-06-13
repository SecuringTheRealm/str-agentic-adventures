"""
Combat Cartographer Agent - Generates tactical battle maps for combat encounters.
"""

import logging
from typing import Dict, Any, Optional

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
        try:
            # Import combat cartographer-specific plugins
            from app.plugins.map_generation_plugin import MapGenerationPlugin
            from app.plugins.tactical_analysis_plugin import TacticalAnalysisPlugin
            from app.plugins.terrain_assessment_plugin import TerrainAssessmentPlugin
            from app.plugins.battle_positioning_plugin import BattlePositioningPlugin
            from app.plugins.environmental_hazards_plugin import EnvironmentalHazardsPlugin

            # Define plugin configuration: (PluginClass, attribute_name, skill_name)
            plugins_config = [
                (MapGenerationPlugin, "map_generation", "MapGeneration"),
                (TacticalAnalysisPlugin, "tactical_analysis", "TacticalAnalysis"),
                (TerrainAssessmentPlugin, "terrain_assessment", "TerrainAssessment"),
                (BattlePositioningPlugin, "battle_positioning", "BattlePositioning"),
                (EnvironmentalHazardsPlugin, "environmental_hazards", "EnvironmentalHazards"),
            ]

            # Register plugins using the configuration
            for plugin_class, attribute_name, skill_name in plugins_config:
                # Create plugin instance
                plugin_instance = plugin_class()
                
                # Register plugin with the kernel
                self.kernel.add_plugin(plugin_instance, skill_name)
                
                # Store reference for direct access
                setattr(self, attribute_name, plugin_instance)

            logger.info("Combat Cartographer agent skills registered successfully")
        except ImportError as e:
            logger.error(f"Error importing Combat Cartographer agent skills: {str(e)}")
            raise
        except (AttributeError, ValueError) as e:
            logger.error(f"Error registering Combat Cartographer agent skills: {str(e)}")
            raise

    async def generate_battle_map(
        self,
        environment_context: Dict[str, Any],
        combat_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
                prompt=prompt, size="1024x1024", quality="standard", style="vivid"
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
                        "style": image_result["style"],
                    },
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
                    "error": image_result.get("error", "Battle map generation failed"),
                }

            # Store the battle map
            self.battle_maps[map_id] = battle_map

            return battle_map

        except Exception as e:
            logger.error(f"Error generating battle map: {str(e)}")
            return {"error": "Failed to generate battle map"}

    async def update_map_with_combat_state(
        self, map_id: str, combat_state: Dict[str, Any]
    ) -> Dict[str, Any]:
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

            # Implement logic to update the map with current combat state
            import datetime

            # Update basic combat state
            battle_map["combat_state"] = combat_state
            battle_map["last_updated"] = datetime.datetime.now().isoformat()

            # Process combatant positions
            if "combatants" in combat_state:
                positions = {}
                for combatant in combat_state["combatants"]:
                    combatant_id = combatant.get("id", combatant.get("name", "unknown"))
                    position = combatant.get("position", {"x": 0, "y": 0})
                    status = combatant.get(
                        "status", "active"
                    )  # active, unconscious, dead, etc.

                    positions[combatant_id] = {
                        "position": position,
                        "status": status,
                        "initiative": combatant.get("initiative", 0),
                        "hp": combatant.get("hp", {}),
                    }

                battle_map["combatant_positions"] = positions

            # Track active effects and conditions
            if "effects" in combat_state:
                active_effects = []
                for effect in combat_state["effects"]:
                    effect_data = {
                        "name": effect.get("name", "Unknown Effect"),
                        "area": effect.get("area", {"x": 0, "y": 0, "radius": 0}),
                        "duration": effect.get("duration", 0),
                        "effect_type": effect.get("type", "environmental"),
                        "description": effect.get("description", ""),
                    }
                    active_effects.append(effect_data)

                battle_map["active_effects"] = active_effects

            # Update turn order and initiative
            if "turn_order" in combat_state:
                battle_map["initiative_order"] = combat_state["turn_order"]
                battle_map["current_turn"] = combat_state.get("current_turn", 0)
                battle_map["round_number"] = combat_state.get("round", 1)

            # Track environmental changes
            if "environmental_changes" in combat_state:
                changes = combat_state["environmental_changes"]
                if "environmental_state" not in battle_map:
                    battle_map["environmental_state"] = {}

                # Update lighting conditions
                if "lighting" in changes:
                    battle_map["environmental_state"]["lighting"] = changes["lighting"]

                # Update visibility conditions (fog, darkness, etc.)
                if "visibility" in changes:
                    battle_map["environmental_state"]["visibility"] = changes[
                        "visibility"
                    ]

                # Update terrain modifications (broken walls, new obstacles, etc.)
                if "terrain_modifications" in changes:
                    if "terrain_modifications" not in battle_map["environmental_state"]:
                        battle_map["environmental_state"]["terrain_modifications"] = []
                    battle_map["environmental_state"]["terrain_modifications"].extend(
                        changes["terrain_modifications"]
                    )

            # Calculate map statistics for tactical information
            battle_map["map_statistics"] = self._calculate_map_stats(battle_map)

            # Add update metadata
            battle_map["update_metadata"] = {
                "update_type": "combat_state_update",
                "updates_applied": list(combat_state.keys()),
                "timestamp": battle_map["last_updated"],
                "map_version": battle_map.get("map_version", 1) + 1,
            }
            battle_map["map_version"] = battle_map.get("map_version", 1) + 1

            logger.info(f"Successfully updated battle map {map_id} with combat state")
            return battle_map

        except Exception as e:
            logger.error(f"Error updating battle map: {str(e)}")
            return {"error": "Failed to update battle map"}

    def _calculate_map_stats(self, battle_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate tactical statistics for the battle map.

        Args:
            battle_map: The battle map data

        Returns:
            Dict[str, Any]: Map statistics including combatant counts, area coverage, etc.
        """
        stats = {
            "total_combatants": 0,
            "active_combatants": 0,
            "unconscious_combatants": 0,
            "dead_combatants": 0,
            "active_effects_count": 0,
            "area_utilization": 0.0,
        }

        # Count combatants by status
        if "combatant_positions" in battle_map:
            positions = battle_map["combatant_positions"]
            stats["total_combatants"] = len(positions)

            for combatant_data in positions.values():
                status = combatant_data.get("status", "active")
                if status == "active":
                    stats["active_combatants"] += 1
                elif status == "unconscious":
                    stats["unconscious_combatants"] += 1
                elif status == "dead":
                    stats["dead_combatants"] += 1

        # Count active effects
        if "active_effects" in battle_map:
            stats["active_effects_count"] = len(battle_map["active_effects"])

        # Calculate area utilization (rough estimate)
        if stats["total_combatants"] > 0:
            # Assume each combatant occupies roughly 5x5 feet (1 square)
            occupied_squares = stats["total_combatants"]
            # Rough map size estimation (could be enhanced with actual map dimensions)
            estimated_total_squares = 400  # 20x20 grid as default
            stats["area_utilization"] = min(
                occupied_squares / estimated_total_squares, 1.0
            )

        return stats


# Lazy singleton instance
_combat_cartographer = None


def get_combat_cartographer():
    """Get the combat cartographer instance, creating it if necessary."""
    global _combat_cartographer
    if _combat_cartographer is None:
        _combat_cartographer = CombatCartographerAgent()
    return _combat_cartographer


# For backward compatibility during import-time checks
combat_cartographer = None
