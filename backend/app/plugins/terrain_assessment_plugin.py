"""
Terrain Assessment Plugin for the Semantic Kernel.
This plugin provides terrain analysis capabilities for combat encounters.
"""

import logging
from typing import Any

# Note: Converted from Semantic Kernel plugin to direct function calls

logger = logging.getLogger(__name__)


class TerrainAssessmentPlugin:
    """
    Plugin that provides terrain assessment capabilities for combat scenarios.
    Analyzes terrain features, movement effects, and tactical implications.
    """

    def __init__(self) -> None:
        """Initialize the terrain assessment plugin."""
        self.terrain_database = {}

    # @kernel_function(
        description="Assess terrain features and their tactical implications.",
        name="assess_terrain_features",
    )
    def assess_terrain_features(
        self, terrain_description: str, map_size: str = "medium"
    ) -> dict[str, Any]:
        """
        Assess terrain features and their impact on combat.

        Args:
            terrain_description: Description of the terrain and features
            map_size: Size of the map area being assessed

        Returns:
            Dict[str, Any]: Terrain assessment with tactical implications
        """
        try:
            terrain_features = self._parse_terrain_features(terrain_description)

            assessment = {
                "identified_features": terrain_features,
                "movement_analysis": self._analyze_movement_effects(terrain_features),
                "cover_analysis": self._analyze_cover_opportunities(terrain_features),
                "tactical_implications": self._assess_tactical_implications(
                    terrain_features
                ),
                "hazard_assessment": self._identify_terrain_hazards(terrain_features),
                "strategic_value": self._evaluate_strategic_value(
                    terrain_features, map_size
                ),
            }

            return {
                "status": "success",
                "terrain_assessment": assessment,
                "assessment_confidence": "high",
            }

        except Exception as e:
            logger.error(f"Error assessing terrain features: {str(e)}")
            return {"status": "error", "error": f"Terrain assessment failed: {str(e)}"}

    # @kernel_function(
        description="Analyze movement costs and restrictions across terrain types.",
        name="analyze_movement_costs",
    )
    def analyze_movement_costs(
        self, terrain_types: str, unit_types: str = "standard"
    ) -> dict[str, Any]:
        """
        Analyze movement costs across different terrain types.

        Args:
            terrain_types: Types of terrain present on the map
            unit_types: Types of units that will traverse the terrain

        Returns:
            Dict[str, Any]: Movement cost analysis for different terrains
        """
        try:
            movement_analysis = {
                "terrain_movement_costs": self._calculate_movement_costs(terrain_types),
                "unit_specific_effects": self._analyze_unit_movement_effects(
                    unit_types
                ),
                "optimal_paths": self._suggest_optimal_paths(terrain_types),
                "movement_restrictions": self._identify_movement_restrictions(
                    terrain_types
                ),
                "traversal_strategies": self._recommend_traversal_strategies(
                    terrain_types, unit_types
                ),
            }

            return {
                "status": "success",
                "movement_analysis": movement_analysis,
                "terrain_types": terrain_types,
            }

        except Exception as e:
            logger.error(f"Error analyzing movement costs: {str(e)}")
            return {"status": "error", "error": f"Movement analysis failed: {str(e)}"}

    # @kernel_function(
        description="Evaluate terrain for defensive positioning and fortification potential.",
        name="evaluate_defensive_terrain",
    )
    def evaluate_defensive_terrain(
        self, terrain_description: str, defensive_objectives: str = "general"
    ) -> dict[str, Any]:
        """
        Evaluate terrain for defensive capabilities and positioning.

        Args:
            terrain_description: Description of terrain features
            defensive_objectives: Specific defensive goals (chokepoint, high_ground, etc.)

        Returns:
            Dict[str, Any]: Defensive terrain evaluation
        """
        try:
            defensive_analysis = {
                "defensive_positions": self._identify_defensive_positions(
                    terrain_description
                ),
                "chokepoints": self._find_chokepoints(terrain_description),
                "fortification_potential": self._assess_fortification_potential(
                    terrain_description
                ),
                "escape_routes": self._map_escape_routes(terrain_description),
                "defensive_advantages": self._catalog_defensive_advantages(
                    terrain_description
                ),
                "vulnerabilities": self._identify_defensive_vulnerabilities(
                    terrain_description
                ),
            }

            return {
                "status": "success",
                "defensive_evaluation": defensive_analysis,
                "objectives": defensive_objectives,
            }

        except Exception as e:
            logger.error(f"Error evaluating defensive terrain: {str(e)}")
            return {
                "status": "error",
                "error": f"Defensive evaluation failed: {str(e)}",
            }

    def _parse_terrain_features(self, terrain_description: str) -> list[dict[str, Any]]:
        """Parse terrain description to identify features."""
        features = []
        description_lower = terrain_description.lower()

        # Define terrain feature patterns
        terrain_patterns = {
            "forest": {
                "type": "natural",
                "cover": "partial",
                "movement_cost": 2,
                "concealment": True,
            },
            "hill": {
                "type": "elevation",
                "cover": "none",
                "movement_cost": 2,
                "elevation_bonus": True,
            },
            "mountain": {
                "type": "elevation",
                "cover": "full",
                "movement_cost": 3,
                "elevation_bonus": True,
            },
            "river": {
                "type": "water",
                "cover": "none",
                "movement_cost": 4,
                "hazard": "drowning",
            },
            "swamp": {
                "type": "difficult",
                "cover": "partial",
                "movement_cost": 3,
                "hazard": "disease",
            },
            "wall": {
                "type": "barrier",
                "cover": "full",
                "movement_cost": "impassable",
                "blocks_sight": True,
            },
            "door": {
                "type": "passage",
                "cover": "none",
                "movement_cost": 1,
                "controllable": True,
            },
            "bridge": {
                "type": "passage",
                "cover": "none",
                "movement_cost": 1,
                "chokepoint": True,
            },
            "cliff": {
                "type": "elevation",
                "cover": "none",
                "movement_cost": "impassable",
                "fall_hazard": True,
            },
            "ice": {
                "type": "slippery",
                "cover": "none",
                "movement_cost": 2,
                "hazard": "falling",
            },
            "lava": {
                "type": "hazard",
                "cover": "none",
                "movement_cost": "impassable",
                "damage": "fire",
            },
            "rubble": {
                "type": "difficult",
                "cover": "partial",
                "movement_cost": 2,
                "unstable": True,
            },
        }

        for pattern, properties in terrain_patterns.items():
            if pattern in description_lower:
                features.append(
                    {
                        "name": pattern,
                        **properties,
                        "description": f"{pattern.capitalize()} terrain feature",
                    }
                )

        return features

    def _analyze_movement_effects(
        self, terrain_features: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze how terrain affects movement."""
        movement_effects = {
            "standard_movement": [],
            "difficult_terrain": [],
            "impassable_areas": [],
            "enhanced_movement": [],
        }

        for feature in terrain_features:
            cost = feature.get("movement_cost", 1)
            name = feature["name"]

            if cost == "impassable":
                movement_effects["impassable_areas"].append(name)
            elif isinstance(cost, int) and cost > 2:
                movement_effects["difficult_terrain"].append(name)
            elif isinstance(cost, int) and cost == 1:
                movement_effects["standard_movement"].append(name)

        return movement_effects

    def _analyze_cover_opportunities(
        self, terrain_features: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze cover opportunities provided by terrain."""
        cover_analysis = {
            "full_cover": [],
            "partial_cover": [],
            "concealment": [],
            "no_cover": [],
        }

        for feature in terrain_features:
            cover_type = feature.get("cover", "none")
            name = feature["name"]

            if cover_type == "full":
                cover_analysis["full_cover"].append(name)
            elif cover_type == "partial":
                cover_analysis["partial_cover"].append(name)
            elif feature.get("concealment"):
                cover_analysis["concealment"].append(name)
            else:
                cover_analysis["no_cover"].append(name)

        return cover_analysis

    def _assess_tactical_implications(
        self, terrain_features: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Assess tactical implications of terrain features."""
        implications = []

        for feature in terrain_features:
            name = feature["name"]

            # Elevation advantages
            if feature.get("elevation_bonus"):
                implications.append(
                    {
                        "feature": name,
                        "implication": "elevation_advantage",
                        "effect": "Provides range and accuracy bonuses",
                        "tactical_value": "high",
                    }
                )

            # Chokepoints
            if feature.get("chokepoint"):
                implications.append(
                    {
                        "feature": name,
                        "implication": "chokepoint_control",
                        "effect": "Limits enemy movement options",
                        "tactical_value": "high",
                    }
                )

            # Hazards
            if feature.get("hazard"):
                implications.append(
                    {
                        "feature": name,
                        "implication": "environmental_hazard",
                        "effect": f"Risk of {feature['hazard']}",
                        "tactical_value": "negative",
                    }
                )

        return implications

    def _identify_terrain_hazards(
        self, terrain_features: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Identify potential hazards in the terrain."""
        hazards = []

        for feature in terrain_features:
            if "hazard" in feature:
                hazards.append(
                    {
                        "source": feature["name"],
                        "hazard_type": feature["hazard"],
                        "severity": self._assess_hazard_severity(feature),
                        "mitigation": self._suggest_hazard_mitigation(feature),
                    }
                )

        return hazards

    def _evaluate_strategic_value(
        self, terrain_features: list[dict[str, Any]], map_size: str
    ) -> dict[str, Any]:
        """Evaluate the strategic value of terrain features."""
        return {
            "key_terrain": [
                f["name"]
                for f in terrain_features
                if f.get("elevation_bonus") or f.get("chokepoint")
            ],
            "control_priority": "high"
            if any(f.get("chokepoint") for f in terrain_features)
            else "medium",
            "defensive_value": "high"
            if any(f.get("cover") == "full" for f in terrain_features)
            else "medium",
            "mobility_impact": "significant"
            if len([f for f in terrain_features if f.get("movement_cost", 1) > 2]) > 2
            else "minimal",
        }

    def _calculate_movement_costs(self, terrain_types: str) -> dict[str, int]:
        """Calculate movement costs for different terrain types."""
        base_costs = {
            "plains": 1,
            "forest": 2,
            "hills": 2,
            "mountains": 3,
            "swamp": 3,
            "desert": 2,
            "ice": 2,
            "rubble": 2,
            "water": 4,
        }

        present_terrain = {}
        for terrain_type, cost in base_costs.items():
            if terrain_type in terrain_types.lower():
                present_terrain[terrain_type] = cost

        return present_terrain

    def _analyze_unit_movement_effects(self, unit_types: str) -> dict[str, Any]:
        """Analyze how different unit types are affected by terrain."""
        return {
            "infantry": {
                "forest": "normal",
                "hills": "reduced_speed",
                "water": "restricted",
            },
            "cavalry": {
                "forest": "restricted",
                "hills": "normal",
                "water": "very_restricted",
            },
            "flying": {"all_terrain": "unaffected", "indoor": "restricted"},
            "aquatic": {"water": "enhanced", "land": "restricted"},
        }

    def _suggest_optimal_paths(self, terrain_types: str) -> list[str]:
        """Suggest optimal movement paths based on terrain."""
        paths = []

        if "plains" in terrain_types.lower():
            paths.append("Use open plains for rapid movement")
        if "hill" in terrain_types.lower():
            paths.append("Follow ridgelines for elevation advantage")
        if "forest" in terrain_types.lower():
            paths.append("Use forest edges for concealment while maintaining mobility")

        return paths

    def _identify_movement_restrictions(
        self, terrain_types: str
    ) -> list[dict[str, Any]]:
        """Identify movement restrictions imposed by terrain."""
        restrictions = []

        terrain_restrictions = {
            "water": {
                "restriction": "requires_swimming",
                "affected_units": "non_aquatic",
            },
            "mountain": {
                "restriction": "climbing_required",
                "affected_units": "ground_units",
            },
            "swamp": {"restriction": "disease_risk", "affected_units": "all_units"},
            "lava": {
                "restriction": "fire_damage",
                "affected_units": "non_immune_units",
            },
        }

        for terrain, details in terrain_restrictions.items():
            if terrain in terrain_types.lower():
                restrictions.append({"terrain": terrain, **details})

        return restrictions

    def _recommend_traversal_strategies(
        self, terrain_types: str, unit_types: str
    ) -> list[str]:
        """Recommend strategies for traversing different terrain."""
        strategies = [
            "Plan routes to minimize difficult terrain exposure",
            "Use scouts to identify safe paths through hazardous areas",
            "Coordinate unit movement to maintain formation integrity",
        ]

        if "water" in terrain_types.lower():
            strategies.append("Secure boats or find fords for water crossings")
        if "mountain" in terrain_types.lower():
            strategies.append("Use switchback paths to manage elevation changes")

        return strategies

    def _identify_defensive_positions(
        self, terrain_description: str
    ) -> list[dict[str, Any]]:
        """Identify strong defensive positions in the terrain."""
        positions = []

        defensive_features = {
            "hill": {"advantage": "elevation", "type": "high_ground"},
            "cliff": {"advantage": "protected_flank", "type": "natural_barrier"},
            "river": {"advantage": "natural_moat", "type": "water_barrier"},
            "wall": {"advantage": "artificial_cover", "type": "fortification"},
        }

        for feature, properties in defensive_features.items():
            if feature in terrain_description.lower():
                positions.append(
                    {"feature": feature, **properties, "defensive_value": "high"}
                )

        return positions

    def _find_chokepoints(self, terrain_description: str) -> list[dict[str, Any]]:
        """Find natural chokepoints in the terrain."""
        chokepoints = []

        chokepoint_features = ["bridge", "pass", "door", "gate", "narrow", "corridor"]

        for feature in chokepoint_features:
            if feature in terrain_description.lower():
                chokepoints.append(
                    {
                        "type": feature,
                        "control_value": "high",
                        "tactical_importance": "critical",
                    }
                )

        return chokepoints

    def _assess_fortification_potential(
        self, terrain_description: str
    ) -> dict[str, Any]:
        """Assess potential for creating fortifications."""
        return {
            "natural_defenses": "high"
            if any(
                word in terrain_description.lower()
                for word in ["cliff", "river", "hill"]
            )
            else "low",
            "build_potential": "high"
            if "flat" in terrain_description.lower()
            else "medium",
            "material_availability": "high"
            if any(
                word in terrain_description.lower()
                for word in ["stone", "wood", "rock"]
            )
            else "low",
        }

    def _map_escape_routes(self, terrain_description: str) -> list[str]:
        """Map potential escape routes."""
        routes = ["Multiple exit points recommended"]

        if "forest" in terrain_description.lower():
            routes.append("Forest provides concealment for withdrawal")
        if "hill" in terrain_description.lower():
            routes.append("Use reverse slope for covered withdrawal")

        return routes

    def _catalog_defensive_advantages(self, terrain_description: str) -> list[str]:
        """Catalog defensive advantages of the terrain."""
        advantages = []

        advantage_keywords = {
            "elevation": "Height advantage for ranged combat",
            "cover": "Protection from ranged attacks",
            "concealment": "Hidden movement capabilities",
            "chokepoint": "Force enemy into narrow approaches",
        }

        for keyword, advantage in advantage_keywords.items():
            if keyword in terrain_description.lower():
                advantages.append(advantage)

        return advantages

    def _identify_defensive_vulnerabilities(
        self, terrain_description: str
    ) -> list[str]:
        """Identify defensive vulnerabilities in the terrain."""
        vulnerabilities = []

        vulnerability_keywords = {
            "flat": "No natural cover or concealment",
            "open": "Exposed to ranged attacks from multiple directions",
            "swamp": "Limited mobility for repositioning",
            "narrow": "Risk of being trapped or surrounded",
        }

        for keyword, vulnerability in vulnerability_keywords.items():
            if keyword in terrain_description.lower():
                vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _assess_hazard_severity(self, feature: dict[str, Any]) -> str:
        """Assess the severity of a terrain hazard."""
        hazard_type = feature.get("hazard", "")

        severity_map = {
            "drowning": "high",
            "falling": "medium",
            "fire": "high",
            "disease": "medium",
            "poison": "high",
        }

        return severity_map.get(hazard_type, "low")

    def _suggest_hazard_mitigation(self, feature: dict[str, Any]) -> str:
        """Suggest mitigation strategies for terrain hazards."""
        hazard_type = feature.get("hazard", "")

        mitigation_map = {
            "drowning": "Use rope or flotation devices",
            "falling": "Secure climbing equipment",
            "fire": "Fire resistance spells or equipment",
            "disease": "Antidotes and protective gear",
            "poison": "Poison immunity or neutralization",
        }

        return mitigation_map.get(hazard_type, "Exercise caution")
