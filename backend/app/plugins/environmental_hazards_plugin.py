"""
Environmental Hazards Plugin for the Semantic Kernel.
This plugin provides environmental hazard assessment and management for combat encounters.
"""
import logging
from typing import Dict, Any, List

from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class EnvironmentalHazardsPlugin:
    """
    Plugin that provides environmental hazard assessment and management capabilities.
    Identifies, analyzes, and provides mitigation strategies for environmental dangers.
    """

    def __init__(self):
        """Initialize the environmental hazards plugin."""
        self.hazard_database = {}
        self.mitigation_strategies = {}

    @kernel_function(
        description="Identify and assess environmental hazards in the combat area.",
        name="identify_environmental_hazards"
    )
    def identify_environmental_hazards(self, environment_description: str, 
                                     weather_conditions: str = "normal") -> Dict[str, Any]:
        """
        Identify and assess environmental hazards in the combat area.
        
        Args:
            environment_description: Description of the environment and its features
            weather_conditions: Current weather conditions affecting hazards
            
        Returns:
            Dict[str, Any]: Comprehensive hazard assessment
        """
        try:
            identified_hazards = self._scan_for_hazards(environment_description, weather_conditions)
            
            hazard_assessment = {
                "identified_hazards": identified_hazards,
                "hazard_severity": self._assess_hazard_severity(identified_hazards),
                "affected_areas": self._map_affected_areas(identified_hazards),
                "temporal_factors": self._analyze_temporal_factors(identified_hazards, weather_conditions),
                "interaction_effects": self._analyze_hazard_interactions(identified_hazards),
                "risk_mitigation": self._suggest_initial_mitigation(identified_hazards)
            }
            
            return {
                "status": "success",
                "hazard_assessment": hazard_assessment,
                "assessment_timestamp": self._get_timestamp(),
                "weather_context": weather_conditions
            }
            
        except Exception as e:
            logger.error(f"Error identifying environmental hazards: {str(e)}")
            return {
                "status": "error",
                "error": f"Hazard identification failed: {str(e)}"
            }

    @kernel_function(
        description="Provide hazard mitigation strategies and safety protocols.",
        name="provide_hazard_mitigation"
    )
    def provide_hazard_mitigation(self, hazard_types: str, party_capabilities: str = "standard",
                                 urgency_level: str = "medium") -> Dict[str, Any]:
        """
        Provide comprehensive hazard mitigation strategies.
        
        Args:
            hazard_types: Types of hazards that need mitigation
            party_capabilities: Capabilities and resources available to the party
            urgency_level: How quickly mitigation is needed
            
        Returns:
            Dict[str, Any]: Detailed mitigation strategies and protocols
        """
        try:
            mitigation_plan = {
                "immediate_actions": self._generate_immediate_actions(hazard_types, urgency_level),
                "equipment_requirements": self._determine_equipment_needs(hazard_types),
                "spell_solutions": self._suggest_magical_solutions(hazard_types, party_capabilities),
                "tactical_adjustments": self._recommend_tactical_adjustments(hazard_types),
                "safety_protocols": self._establish_safety_protocols(hazard_types),
                "contingency_plans": self._develop_contingency_plans(hazard_types)
            }
            
            return {
                "status": "success",
                "mitigation_plan": mitigation_plan,
                "hazard_context": hazard_types,
                "urgency": urgency_level
            }
            
        except Exception as e:
            logger.error(f"Error providing hazard mitigation: {str(e)}")
            return {
                "status": "error",
                "error": f"Mitigation planning failed: {str(e)}"
            }

    @kernel_function(
        description="Monitor dynamic hazards and provide real-time updates.",
        name="monitor_dynamic_hazards"
    )
    def monitor_dynamic_hazards(self, current_hazards: str, combat_round: int = 1,
                               environmental_changes: str = "") -> Dict[str, Any]:
        """
        Monitor dynamic hazards and provide real-time hazard updates.
        
        Args:
            current_hazards: Currently active hazards
            combat_round: Current combat round for temporal tracking
            environmental_changes: Any changes to the environment
            
        Returns:
            Dict[str, Any]: Dynamic hazard monitoring data
        """
        try:
            monitoring_data = {
                "hazard_evolution": self._track_hazard_evolution(current_hazards, combat_round),
                "new_hazards": self._detect_new_hazards(environmental_changes),
                "hazard_predictions": self._predict_hazard_changes(current_hazards, combat_round),
                "timing_alerts": self._generate_timing_alerts(current_hazards, combat_round),
                "escalation_warnings": self._assess_escalation_risk(current_hazards),
                "updated_mitigation": self._update_mitigation_strategies(current_hazards, combat_round)
            }
            
            return {
                "status": "success",
                "monitoring_data": monitoring_data,
                "combat_round": combat_round,
                "monitoring_timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring dynamic hazards: {str(e)}")
            return {
                "status": "error",
                "error": f"Hazard monitoring failed: {str(e)}"
            }

    def _scan_for_hazards(self, environment_description: str, weather_conditions: str) -> List[Dict[str, Any]]:
        """Scan environment description for potential hazards."""
        hazards = []
        env_lower = environment_description.lower()
        weather_lower = weather_conditions.lower()
        
        # Define hazard patterns
        hazard_patterns = {
            "fire": {
                "triggers": ["lava", "flame", "fire", "burning", "torch", "brazier"],
                "type": "elemental",
                "damage_type": "fire",
                "spread_potential": True,
                "severity": "high"
            },
            "water": {
                "triggers": ["river", "lake", "pond", "flooding", "deep water"],
                "type": "drowning",
                "damage_type": "suffocation",
                "spread_potential": False,
                "severity": "medium"
            },
            "falling": {
                "triggers": ["cliff", "pit", "chasm", "height", "elevated", "ledge"],
                "type": "falling",
                "damage_type": "bludgeoning",
                "spread_potential": False,
                "severity": "high"
            },
            "poison": {
                "triggers": ["toxic", "poison", "gas", "fumes", "swamp gas"],
                "type": "poison",
                "damage_type": "poison",
                "spread_potential": True,
                "severity": "medium"
            },
            "ice": {
                "triggers": ["ice", "frozen", "slippery", "icicle"],
                "type": "slipping",
                "damage_type": "bludgeoning",
                "spread_potential": False,
                "severity": "low"
            },
            "lightning": {
                "triggers": ["storm", "electrical", "lightning", "thunder"],
                "type": "electrical",
                "damage_type": "lightning",
                "spread_potential": True,
                "severity": "high"
            },
            "unstable_terrain": {
                "triggers": ["unstable", "crumbling", "weak floor", "rubble"],
                "type": "structural",
                "damage_type": "bludgeoning",
                "spread_potential": True,
                "severity": "medium"
            }
        }
        
        # Scan for each hazard type
        for hazard_name, properties in hazard_patterns.items():
            for trigger in properties["triggers"]:
                if trigger in env_lower:
                    hazard = {
                        "name": hazard_name,
                        "trigger_word": trigger,
                        **properties,
                        "weather_enhanced": self._check_weather_enhancement(hazard_name, weather_lower)
                    }
                    hazards.append(hazard)
                    break  # Only add each hazard type once
        
        # Weather-specific hazards
        weather_hazards = self._identify_weather_hazards(weather_lower)
        hazards.extend(weather_hazards)
        
        return hazards

    def _check_weather_enhancement(self, hazard_name: str, weather_conditions: str) -> bool:
        """Check if weather conditions enhance specific hazards."""
        weather_enhancements = {
            "fire": ["dry", "wind", "drought"],
            "ice": ["cold", "freezing", "winter", "snow"],
            "lightning": ["storm", "rain", "thunder"],
            "water": ["rain", "storm", "flood"]
        }
        
        enhancers = weather_enhancements.get(hazard_name, [])
        return any(enhancer in weather_conditions for enhancer in enhancers)

    def _identify_weather_hazards(self, weather_conditions: str) -> List[Dict[str, Any]]:
        """Identify hazards specifically caused by weather."""
        weather_hazards = []
        
        weather_hazard_map = {
            "storm": {
                "name": "severe_weather",
                "type": "weather",
                "damage_type": "various",
                "severity": "medium",
                "effects": ["reduced_visibility", "difficult_movement"]
            },
            "fog": {
                "name": "low_visibility", 
                "type": "visibility",
                "damage_type": "none",
                "severity": "low",
                "effects": ["concealment", "navigation_difficulty"]
            },
            "blizzard": {
                "name": "extreme_cold",
                "type": "temperature",
                "damage_type": "cold",
                "severity": "high",
                "effects": ["exhaustion", "hypothermia"]
            }
        }
        
        for weather_type, hazard_data in weather_hazard_map.items():
            if weather_type in weather_conditions:
                weather_hazards.append(hazard_data)
        
        return weather_hazards

    def _assess_hazard_severity(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall severity of identified hazards."""
        if not hazards:
            return {"overall": "none", "breakdown": {}}
        
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for hazard in hazards:
            severity = hazard.get("severity", "low")
            if hazard.get("weather_enhanced"):
                # Upgrade severity if weather-enhanced
                severity_upgrade = {"low": "medium", "medium": "high", "high": "critical"}
                severity = severity_upgrade.get(severity, severity)
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Determine overall severity
        if severity_counts["critical"] > 0:
            overall = "critical"
        elif severity_counts["high"] > 0:
            overall = "high"
        elif severity_counts["medium"] > 0:
            overall = "medium"
        elif severity_counts["low"] > 0:
            overall = "low"
        else:
            overall = "none"
        
        return {
            "overall": overall,
            "breakdown": severity_counts,
            "hazard_count": len(hazards)
        }

    def _map_affected_areas(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map areas affected by each hazard."""
        affected_areas = {}
        
        for hazard in hazards:
            hazard_name = hazard["name"]
            area_data = {
                "coverage": self._estimate_hazard_coverage(hazard),
                "spread_pattern": self._determine_spread_pattern(hazard),
                "safe_zones": self._identify_safe_zones(hazard),
                "entry_restriction": self._assess_entry_risk(hazard)
            }
            affected_areas[hazard_name] = area_data
        
        return affected_areas

    def _estimate_hazard_coverage(self, hazard: Dict[str, Any]) -> str:
        """Estimate how much area a hazard covers."""
        coverage_map = {
            "fire": "expanding_area",
            "water": "fixed_area", 
            "falling": "point_sources",
            "poison": "area_effect",
            "ice": "surface_area",
            "lightning": "random_strikes",
            "unstable_terrain": "structural_zones"
        }
        return coverage_map.get(hazard["name"], "localized")

    def _determine_spread_pattern(self, hazard: Dict[str, Any]) -> str:
        """Determine how a hazard spreads over time."""
        if hazard.get("spread_potential"):
            spread_patterns = {
                "fire": "radial_expansion",
                "poison": "wind_carried",
                "lightning": "conductive_paths",
                "unstable_terrain": "cascading_failure"
            }
            return spread_patterns.get(hazard["name"], "contained")
        return "static"

    def _identify_safe_zones(self, hazard: Dict[str, Any]) -> List[str]:
        """Identify areas safe from the hazard."""
        safe_zone_map = {
            "fire": ["water_areas", "stone_surfaces", "fire_resistant_areas"],
            "water": ["elevated_ground", "dry_areas", "platforms"],
            "falling": ["stable_ground", "covered_areas", "low_elevation"],
            "poison": ["high_ground", "well_ventilated_areas", "air_sources"],
            "ice": ["rough_surfaces", "heated_areas", "non_slippery_terrain"],
            "lightning": ["enclosed_areas", "low_ground", "non_conductive_materials"]
        }
        return safe_zone_map.get(hazard["name"], ["retreat_to_safe_distance"])

    def _assess_entry_risk(self, hazard: Dict[str, Any]) -> str:
        """Assess risk level for entering hazard areas."""
        risk_levels = {
            "low": ["ice"],
            "medium": ["water", "unstable_terrain"],
            "high": ["fire", "poison", "falling"],
            "extreme": ["lava", "lightning"]
        }
        
        for risk_level, hazard_types in risk_levels.items():
            if hazard["name"] in hazard_types:
                return risk_level
        return "medium"

    def _analyze_temporal_factors(self, hazards: List[Dict[str, Any]], weather_conditions: str) -> Dict[str, Any]:
        """Analyze how hazards change over time."""
        return {
            "time_sensitive_hazards": [h["name"] for h in hazards if h.get("spread_potential")],
            "weather_dependent": [h["name"] for h in hazards if h.get("weather_enhanced")],
            "escalation_potential": self._assess_escalation_timeline(hazards),
            "resolution_timeline": self._estimate_resolution_time(hazards)
        }

    def _analyze_hazard_interactions(self, hazards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze how hazards might interact with each other."""
        interactions = []
        hazard_names = [h["name"] for h in hazards]
        
        # Define interaction patterns
        interaction_rules = {
            ("fire", "water"): {"type": "neutralization", "result": "steam_creation"},
            ("fire", "ice"): {"type": "melting", "result": "water_hazard"},
            ("lightning", "water"): {"type": "amplification", "result": "electrical_conductivity"},
            ("poison", "fire"): {"type": "amplification", "result": "toxic_smoke"},
            ("unstable_terrain", "fire"): {"type": "amplification", "result": "structural_collapse"}
        }
        
        # Check for interactions
        for (hazard1, hazard2), interaction in interaction_rules.items():
            if hazard1 in hazard_names and hazard2 in hazard_names:
                interactions.append({
                    "hazards": [hazard1, hazard2],
                    **interaction
                })
        
        return interactions

    def _suggest_initial_mitigation(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest initial mitigation strategies."""
        mitigation_suggestions = {}
        
        for hazard in hazards:
            hazard_name = hazard["name"]
            suggestions = self._get_basic_mitigation(hazard_name)
            mitigation_suggestions[hazard_name] = suggestions
        
        return mitigation_suggestions

    def _get_basic_mitigation(self, hazard_name: str) -> List[str]:
        """Get basic mitigation strategies for a hazard type."""
        mitigation_map = {
            "fire": ["use_water_or_sand", "create_firebreaks", "fire_resistance_spells"],
            "water": ["use_rope_for_safety", "swim_checks", "water_breathing_spells"],
            "falling": ["secure_climbing_gear", "feather_fall_spells", "avoid_edges"],
            "poison": ["hold_breath", "neutralize_poison", "protection_from_poison"],
            "ice": ["use_crampons", "sand_for_traction", "careful_movement"],
            "lightning": ["avoid_metal", "stay_low", "lightning_protection"],
            "unstable_terrain": ["test_surfaces", "distribute_weight", "stone_shape_spells"]
        }
        return mitigation_map.get(hazard_name, ["exercise_extreme_caution"])

    def _generate_immediate_actions(self, hazard_types: str, urgency_level: str) -> List[Dict[str, Any]]:
        """Generate immediate actions for hazard mitigation."""
        actions = []
        
        urgency_actions = {
            "low": {"time_limit": "several_rounds", "approach": "methodical"},
            "medium": {"time_limit": "next_round", "approach": "efficient"},
            "high": {"time_limit": "this_round", "approach": "emergency"},
            "critical": {"time_limit": "immediately", "approach": "survival"}
        }
        
        action_context = urgency_actions.get(urgency_level, urgency_actions["medium"])
        
        # Generate actions based on hazard types
        hazard_list = hazard_types.lower().split(",") if "," in hazard_types else [hazard_types.lower()]
        
        for hazard in hazard_list:
            hazard = hazard.strip()
            if "fire" in hazard:
                actions.append({
                    "action": "extinguish_or_avoid_fire",
                    "priority": "high",
                    "method": "water_magic_or_retreat",
                    "time_required": action_context["time_limit"]
                })
            elif "poison" in hazard:
                actions.append({
                    "action": "neutralize_poison_effects",
                    "priority": "high",
                    "method": "antidotes_or_spells",
                    "time_required": action_context["time_limit"]
                })
        
        return actions

    def _determine_equipment_needs(self, hazard_types: str) -> Dict[str, List[str]]:
        """Determine equipment needed for hazard mitigation."""
        equipment_needs = {
            "essential": [],
            "recommended": [],
            "optional": []
        }
        
        hazard_equipment = {
            "fire": {
                "essential": ["water_source", "fire_blanket"],
                "recommended": ["fire_resistance_potions"],
                "optional": ["sand_for_smothering"]
            },
            "water": {
                "essential": ["rope", "flotation_devices"],
                "recommended": ["swimming_gear"],
                "optional": ["water_breathing_apparatus"]
            },
            "poison": {
                "essential": ["antidotes", "protective_masks"],
                "recommended": ["neutralization_agents"],
                "optional": ["air_filtration_devices"]
            }
        }
        
        # Aggregate equipment needs
        for hazard_type, equipment in hazard_equipment.items():
            if hazard_type in hazard_types.lower():
                for category in equipment_needs:
                    equipment_needs[category].extend(equipment.get(category, []))
        
        return equipment_needs

    def _suggest_magical_solutions(self, hazard_types: str, party_capabilities: str) -> List[Dict[str, Any]]:
        """Suggest magical solutions for hazard mitigation."""
        magical_solutions = []
        
        magic_solutions_map = {
            "fire": [
                {"spell": "Create Water", "level": 1, "effect": "extinguish_fires"},
                {"spell": "Protection from Energy", "level": 3, "effect": "fire_resistance"},
                {"spell": "Control Water", "level": 4, "effect": "flood_area"}
            ],
            "poison": [
                {"spell": "Neutralize Poison", "level": 3, "effect": "remove_poison"},
                {"spell": "Protection from Poison", "level": 2, "effect": "prevent_poisoning"},
                {"spell": "Purify Food and Drink", "level": 1, "effect": "cleanse_toxins"}
            ],
            "falling": [
                {"spell": "Feather Fall", "level": 1, "effect": "prevent_fall_damage"},
                {"spell": "Fly", "level": 3, "effect": "aerial_mobility"},
                {"spell": "Levitate", "level": 2, "effect": "vertical_movement"}
            ]
        }
        
        for hazard_type, spells in magic_solutions_map.items():
            if hazard_type in hazard_types.lower():
                magical_solutions.extend(spells)
        
        return magical_solutions

    def _recommend_tactical_adjustments(self, hazard_types: str) -> List[str]:
        """Recommend tactical adjustments for dealing with hazards."""
        adjustments = []
        
        tactical_adjustments_map = {
            "fire": ["maintain_distance", "use_ranged_attacks", "create_firebreaks"],
            "water": ["secure_footing", "buddy_system", "test_depth"],
            "poison": ["avoid_low_areas", "use_wind_direction", "limit_exposure_time"],
            "falling": ["secure_movement", "test_surfaces", "use_safety_lines"],
            "ice": ["slow_careful_movement", "use_traction_aids", "avoid_running"],
            "lightning": ["avoid_high_ground", "remove_metal", "seek_shelter"]
        }
        
        for hazard_type, tactics in tactical_adjustments_map.items():
            if hazard_type in hazard_types.lower():
                adjustments.extend(tactics)
        
        return list(set(adjustments))  # Remove duplicates

    def _establish_safety_protocols(self, hazard_types: str) -> Dict[str, List[str]]:
        """Establish safety protocols for hazard management."""
        return {
            "communication": ["establish_warning_signals", "maintain_visual_contact"],
            "movement": ["designated_pathfinder", "single_file_through_hazards"],
            "emergency": ["emergency_retreat_signal", "buddy_system_accountability"],
            "equipment": ["regular_equipment_checks", "backup_safety_gear"]
        }

    def _develop_contingency_plans(self, hazard_types: str) -> List[Dict[str, Any]]:
        """Develop contingency plans for worst-case scenarios."""
        return [
            {
                "scenario": "party_member_affected",
                "response": "immediate_rescue_and_treatment_protocols"
            },
            {
                "scenario": "hazard_escalation",
                "response": "evacuation_to_predetermined_safe_zone"
            },
            {
                "scenario": "equipment_failure",
                "response": "improvised_solutions_and_magical_alternatives"
            }
        ]

    def _track_hazard_evolution(self, current_hazards: str, combat_round: int) -> Dict[str, Any]:
        """Track how hazards evolve over time."""
        return {
            "spreading_hazards": ["fire", "poison_gas"],
            "diminishing_hazards": ["unstable_ice"],
            "cycling_hazards": ["geysers", "lightning_strikes"],
            "round_predictions": {
                "next_round": "fire_spread_expected",
                "in_3_rounds": "structural_collapse_possible"
            }
        }

    def _detect_new_hazards(self, environmental_changes: str) -> List[Dict[str, Any]]:
        """Detect new hazards created by environmental changes."""
        new_hazards = []
        
        if "collapse" in environmental_changes.lower():
            new_hazards.append({
                "name": "falling_debris",
                "type": "structural",
                "severity": "medium",
                "cause": "structural_damage"
            })
        
        if "explosion" in environmental_changes.lower():
            new_hazards.append({
                "name": "fire_spread",
                "type": "elemental",
                "severity": "high",
                "cause": "explosive_event"
            })
        
        return new_hazards

    def _predict_hazard_changes(self, current_hazards: str, combat_round: int) -> List[Dict[str, Any]]:
        """Predict future hazard changes."""
        predictions = []
        
        # Example predictions based on common hazard patterns
        if "fire" in current_hazards.lower():
            predictions.append({
                "hazard": "fire",
                "prediction": "spread_to_adjacent_areas",
                "timeline": f"round_{combat_round + 2}",
                "confidence": "high"
            })
        
        return predictions

    def _generate_timing_alerts(self, current_hazards: str, combat_round: int) -> List[str]:
        """Generate timing-based alerts for hazard management."""
        alerts = []
        
        # Generate round-based alerts
        if combat_round % 3 == 0:  # Every 3 rounds
            alerts.append("Check for hazard evolution and new developments")
        
        if "fire" in current_hazards.lower():
            alerts.append("Fire spreading - consider immediate containment")
        
        return alerts

    def _assess_escalation_risk(self, current_hazards: str) -> Dict[str, Any]:
        """Assess risk of hazard escalation."""
        return {
            "escalation_probability": "medium",
            "escalation_triggers": ["combat_actions", "spell_effects", "time_passage"],
            "escalation_timeline": "2-4_rounds",
            "escalation_severity": "could_become_critical"
        }

    def _update_mitigation_strategies(self, current_hazards: str, combat_round: int) -> Dict[str, Any]:
        """Update mitigation strategies based on current situation."""
        return {
            "priority_changes": "focus_on_spreading_hazards",
            "new_options": ["environmental_spells", "tactical_retreat"],
            "resource_allocation": "prioritize_protection_over_offense",
            "timing_considerations": "act_before_next_escalation"
        }

    def _assess_escalation_timeline(self, hazards: List[Dict[str, Any]]) -> Dict[str, str]:
        """Assess timeline for hazard escalation."""
        timeline = {}
        for hazard in hazards:
            if hazard.get("spread_potential"):
                timeline[hazard["name"]] = "2-3_rounds"
            else:
                timeline[hazard["name"]] = "stable"
        return timeline

    def _estimate_resolution_time(self, hazards: List[Dict[str, Any]]) -> Dict[str, str]:
        """Estimate time needed to resolve each hazard."""
        resolution_times = {}
        for hazard in hazards:
            severity = hazard.get("severity", "medium")
            time_map = {
                "low": "1_round",
                "medium": "2-3_rounds", 
                "high": "4-6_rounds",
                "critical": "immediate_action_required"
            }
            resolution_times[hazard["name"]] = time_map.get(severity, "unknown")
        return resolution_times

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()