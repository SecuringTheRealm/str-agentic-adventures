"""
Map Generation Plugin for the Semantic Kernel.
This plugin provides map generation capabilities for combat encounters.
"""

import logging
from typing import Any

# Note: Converted from Semantic Kernel plugin to direct function calls

logger = logging.getLogger(__name__)


class MapGenerationPlugin:
    """
    Plugin that provides map generation capabilities for combat scenarios.
    Handles map layout generation, grid systems, and tactical positioning.
    """

    def __init__(self) -> None:
        """Initialize the map generation plugin."""
        self.map_cache = {}

    # @kernel_function(
        description="Generate a tactical battle map based on environment context.",
        name="generate_tactical_map",
    )
    def generate_tactical_map(
        self,
        environment_context: str,
        map_size: str = "medium",
        grid_type: str = "square",
    ) -> dict[str, Any]:
        """
        Generate a tactical battle map based on environment context.

        Args:
            environment_context: Description of the environment and features
            map_size: Size of the map (small, medium, large)
            grid_type: Type of grid system (square, hex)

        Returns:
            Dict[str, Any]: Map generation parameters and layout information
        """
        try:
            # Define map dimensions based on size
            size_dimensions = {
                "small": {"width": 15, "height": 15, "squares": 225},
                "medium": {"width": 20, "height": 20, "squares": 400},
                "large": {"width": 30, "height": 30, "squares": 900},
            }

            dimensions = size_dimensions.get(map_size, size_dimensions["medium"])

            # Parse environment context for map features
            features = self._extract_map_features(environment_context)

            map_data = {
                "dimensions": dimensions,
                "grid_type": grid_type,
                "environment_context": environment_context,
                "extracted_features": features,
                "map_layout": {
                    "entry_points": self._calculate_entry_points(dimensions),
                    "terrain_zones": self._define_terrain_zones(features, dimensions),
                    "strategic_positions": self._identify_strategic_positions(
                        features, dimensions
                    ),
                },
                "tactical_considerations": {
                    "chokepoints": len(
                        [f for f in features if f.get("type") == "passage"]
                    ),
                    "cover_areas": len(
                        [f for f in features if f.get("provides_cover", False)]
                    ),
                    "elevation_changes": len(
                        [f for f in features if "elevation" in f.get("properties", [])]
                    ),
                },
            }

            return {
                "status": "success",
                "map_data": map_data,
                "generation_notes": "Tactical map layout generated successfully",
            }

        except Exception as e:
            logger.error(f"Error generating tactical map: {str(e)}")
            return {"status": "error", "error": f"Map generation failed: {str(e)}"}

    # @kernel_function(
        description="Create a map grid system with positioning coordinates.",
        name="create_grid_system",
    )
    def create_grid_system(
        self, width: int = 20, height: int = 20, grid_type: str = "square"
    ) -> dict[str, Any]:
        """
        Create a grid system for tactical positioning.

        Args:
            width: Width of the map in grid squares
            height: Height of the map in grid squares
            grid_type: Type of grid (square, hex)

        Returns:
            Dict[str, Any]: Grid system data and coordinate mappings
        """
        try:
            if grid_type == "square":
                grid_data = {
                    "type": "square",
                    "dimensions": {"width": width, "height": height},
                    "total_squares": width * height,
                    "coordinate_system": "cartesian",
                    "square_size_feet": 5,
                    "movement_rules": {"diagonal_cost": 1.5, "cardinal_cost": 1.0},
                }
            elif grid_type == "hex":
                grid_data = {
                    "type": "hex",
                    "dimensions": {"width": width, "height": height},
                    "total_hexes": width * height,
                    "coordinate_system": "axial",
                    "hex_size_feet": 5,
                    "movement_rules": {"all_directions_cost": 1.0},
                }
            else:
                raise ValueError(f"Unsupported grid type: {grid_type}")

            return {
                "status": "success",
                "grid_system": grid_data,
                "positioning_guide": self._create_positioning_guide(grid_data),
            }

        except Exception as e:
            logger.error(f"Error creating grid system: {str(e)}")
            return {
                "status": "error",
                "error": f"Grid system creation failed: {str(e)}",
            }

    def _extract_map_features(self, environment_context: str) -> list:
        """Extract map features from environment description."""
        features = []
        context_lower = environment_context.lower()

        # Common terrain features
        feature_keywords = {
            "wall": {
                "type": "obstacle",
                "provides_cover": True,
                "blocks_movement": True,
            },
            "tree": {
                "type": "natural",
                "provides_cover": True,
                "blocks_movement": False,
            },
            "rock": {
                "type": "natural",
                "provides_cover": True,
                "blocks_movement": True,
            },
            "water": {"type": "hazard", "properties": ["difficult_terrain", "aquatic"]},
            "pit": {"type": "hazard", "properties": ["elevation", "trap"]},
            "bridge": {"type": "passage", "properties": ["elevation", "chokepoint"]},
            "door": {"type": "passage", "blocks_movement": False},
            "stairs": {"type": "passage", "properties": ["elevation"]},
            "pillar": {
                "type": "obstacle",
                "provides_cover": True,
                "blocks_movement": True,
            },
        }

        for keyword, properties in feature_keywords.items():
            if keyword in context_lower:
                features.append({"name": keyword, **properties})

        return features

    def _calculate_entry_points(self, dimensions: dict[str, int]) -> list:
        """Calculate potential entry points for the map."""
        width, height = dimensions["width"], dimensions["height"]

        return [
            {"position": [0, height // 2], "side": "west", "type": "edge"},
            {"position": [width - 1, height // 2], "side": "east", "type": "edge"},
            {"position": [width // 2, 0], "side": "north", "type": "edge"},
            {"position": [width // 2, height - 1], "side": "south", "type": "edge"},
        ]

    def _define_terrain_zones(self, features: list, dimensions: dict[str, int]) -> list:
        """Define terrain zones based on features."""
        zones = []

        # Default open terrain zone
        zones.append(
            {
                "type": "open_terrain",
                "area": {
                    "x": 5,
                    "y": 5,
                    "width": dimensions["width"] - 10,
                    "height": dimensions["height"] - 10,
                },
                "movement_cost": 1.0,
                "description": "Open battlefield area",
            }
        )

        # Add zones based on features
        for feature in features:
            if feature.get("type") == "hazard":
                zones.append(
                    {
                        "type": "hazardous_terrain",
                        "feature": feature["name"],
                        "movement_cost": 2.0,
                        "description": f"Area affected by {feature['name']}",
                    }
                )

        return zones

    def _identify_strategic_positions(
        self, features: list, dimensions: dict[str, int]
    ) -> list:
        """Identify strategic positions on the map."""
        positions = []

        # Corner positions (often strategic)
        corners = [
            {
                "position": [2, 2],
                "type": "corner",
                "advantage": "multiple_escape_routes",
            },
            {
                "position": [dimensions["width"] - 3, 2],
                "type": "corner",
                "advantage": "multiple_escape_routes",
            },
            {
                "position": [2, dimensions["height"] - 3],
                "type": "corner",
                "advantage": "multiple_escape_routes",
            },
            {
                "position": [dimensions["width"] - 3, dimensions["height"] - 3],
                "type": "corner",
                "advantage": "multiple_escape_routes",
            },
        ]
        positions.extend(corners)

        # High ground positions if elevation features present
        if any("elevation" in feature.get("properties", []) for feature in features):
            positions.append(
                {
                    "position": [dimensions["width"] // 2, dimensions["height"] // 2],
                    "type": "elevated",
                    "advantage": "high_ground_bonus",
                }
            )

        return positions

    def _create_positioning_guide(self, grid_data: dict[str, Any]) -> dict[str, Any]:
        """Create a guide for positioning units on the grid."""
        return {
            "coordinate_format": "x,y from bottom-left origin",
            "movement_measurement": f"Each square = {grid_data.get('square_size_feet', grid_data.get('hex_size_feet', 5))} feet",
            "positioning_tips": [
                "Place ranged units in positions with clear sight lines",
                "Use terrain features for cover and tactical advantage",
                "Consider chokepoints for controlling enemy movement",
                "Position healers with easy access to frontline fighters",
            ],
        }
