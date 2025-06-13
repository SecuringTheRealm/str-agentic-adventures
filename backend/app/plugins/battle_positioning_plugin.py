"""
Battle Positioning Plugin for the Semantic Kernel.
This plugin provides battle positioning capabilities for combat encounters.
"""
import logging
from typing import Dict, Any, List

from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class BattlePositioningPlugin:
    """
    Plugin that provides battle positioning capabilities for combat scenarios.
    Handles unit placement, formation management, and strategic positioning.
    """

    def __init__(self):
        """Initialize the battle positioning plugin."""
        self.formation_templates = {}
        self.positioning_history = []

    @kernel_function(
        description="Calculate optimal starting positions for combat units.",
        name="calculate_starting_positions"
    )
    def calculate_starting_positions(self, party_composition: str, map_layout: str, 
                                   tactical_objectives: str = "balanced") -> Dict[str, Any]:
        """
        Calculate optimal starting positions for combat units.
        
        Args:
            party_composition: Description of party members and their roles
            map_layout: Layout and features of the battle map
            tactical_objectives: Primary tactical objectives (offensive, defensive, balanced)
            
        Returns:
            Dict[str, Any]: Optimal starting positions for each unit
        """
        try:
            party_units = self._parse_party_composition(party_composition)
            map_features = self._parse_map_layout(map_layout)
            
            positioning_plan = {
                "recommended_positions": self._calculate_unit_positions(party_units, map_features, tactical_objectives),
                "formation_type": self._select_optimal_formation(party_units, tactical_objectives),
                "positioning_rationale": self._explain_positioning_decisions(party_units, map_features),
                "alternative_setups": self._generate_alternative_setups(party_units, map_features),
                "tactical_considerations": self._analyze_positioning_factors(map_features, tactical_objectives)
            }
            
            return {
                "status": "success",
                "positioning_plan": positioning_plan,
                "party_size": len(party_units),
                "objectives": tactical_objectives
            }
            
        except Exception as e:
            logger.error(f"Error calculating starting positions: {str(e)}")
            return {
                "status": "error",
                "error": f"Position calculation failed: {str(e)}"
            }

    @kernel_function(
        description="Recommend formation adjustments during combat.",
        name="recommend_formation_adjustments"
    )
    def recommend_formation_adjustments(self, current_positions: str, combat_state: str, 
                                      tactical_situation: str = "standard") -> Dict[str, Any]:
        """
        Recommend formation adjustments based on current combat state.
        
        Args:
            current_positions: Current positions of all units
            combat_state: Current state of the combat encounter
            tactical_situation: Current tactical situation (advantage, disadvantage, etc.)
            
        Returns:
            Dict[str, Any]: Formation adjustment recommendations
        """
        try:
            # Parse current state
            positions = self._parse_current_positions(current_positions)
            state_analysis = self._analyze_combat_state(combat_state)
            
            adjustments = {
                "immediate_adjustments": self._identify_immediate_adjustments(positions, state_analysis),
                "formation_changes": self._recommend_formation_changes(positions, tactical_situation),
                "priority_repositioning": self._identify_priority_repositioning(positions, state_analysis),
                "movement_coordination": self._plan_coordinated_movement(positions),
                "contingency_positions": self._prepare_contingency_positions(positions, state_analysis)
            }
            
            return {
                "status": "success",
                "adjustments": adjustments,
                "tactical_situation": tactical_situation,
                "urgency": self._assess_adjustment_urgency(state_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error recommending formation adjustments: {str(e)}")
            return {
                "status": "error",
                "error": f"Formation adjustment failed: {str(e)}"
            }

    @kernel_function(
        description="Optimize unit spacing and formation coherence.",
        name="optimize_unit_spacing"
    )
    def optimize_unit_spacing(self, unit_types: str, formation_goal: str = "standard", 
                             threat_level: str = "medium") -> Dict[str, Any]:
        """
        Optimize spacing between units for maximum effectiveness.
        
        Args:
            unit_types: Types and roles of units in the formation
            formation_goal: Desired formation characteristics (tight, loose, flexible)
            threat_level: Current threat level affecting spacing decisions
            
        Returns:
            Dict[str, Any]: Optimal spacing recommendations
        """
        try:
            spacing_plan = {
                "optimal_spacing": self._calculate_optimal_spacing(unit_types, formation_goal),
                "cohesion_guidelines": self._establish_cohesion_guidelines(unit_types),
                "threat_adjustments": self._adjust_for_threat_level(threat_level),
                "spacing_principles": self._define_spacing_principles(formation_goal),
                "formation_integrity": self._maintain_formation_integrity(unit_types, formation_goal)
            }
            
            return {
                "status": "success",
                "spacing_plan": spacing_plan,
                "formation_goal": formation_goal,
                "threat_considerations": threat_level
            }
            
        except Exception as e:
            logger.error(f"Error optimizing unit spacing: {str(e)}")
            return {
                "status": "error",
                "error": f"Spacing optimization failed: {str(e)}"
            }

    def _parse_party_composition(self, party_composition: str) -> List[Dict[str, Any]]:
        """Parse party composition into individual units."""
        units = []
        
        # Basic role detection
        role_keywords = {
            "fighter": {"role": "melee", "priority": "frontline", "spacing": "tight"},
            "wizard": {"role": "caster", "priority": "backline", "spacing": "loose"},
            "cleric": {"role": "support", "priority": "midline", "spacing": "medium"},
            "rogue": {"role": "skirmisher", "priority": "flanker", "spacing": "loose"},
            "ranger": {"role": "ranged", "priority": "backline", "spacing": "medium"},
            "barbarian": {"role": "melee", "priority": "frontline", "spacing": "loose"},
            "paladin": {"role": "tank", "priority": "frontline", "spacing": "tight"},
            "sorcerer": {"role": "caster", "priority": "backline", "spacing": "loose"},
            "warlock": {"role": "caster", "priority": "midline", "spacing": "medium"}
        }
        
        # Extract unit information
        composition_lower = party_composition.lower()
        unit_count = 1
        
        for role, properties in role_keywords.items():
            if role in composition_lower:
                units.append({
                    "id": f"unit_{unit_count}",
                    "class": role,
                    **properties
                })
                unit_count += 1
        
        # If no specific roles found, create generic units
        if not units:
            for i in range(4):  # Default party size
                units.append({
                    "id": f"unit_{i+1}",
                    "class": "adventurer",
                    "role": "mixed",
                    "priority": "midline",
                    "spacing": "medium"
                })
        
        return units

    def _parse_map_layout(self, map_layout: str) -> Dict[str, Any]:
        """Parse map layout to extract tactical features."""
        layout_lower = map_layout.lower()
        
        features = {
            "entry_points": [],
            "cover_areas": [],
            "elevation": [],
            "chokepoints": [],
            "hazards": [],
            "open_areas": []
        }
        
        # Detect layout features
        if "door" in layout_lower or "entrance" in layout_lower:
            features["entry_points"].append("main_entrance")
        if "wall" in layout_lower or "pillar" in layout_lower:
            features["cover_areas"].append("structural_cover")
        if "hill" in layout_lower or "elevated" in layout_lower:
            features["elevation"].append("high_ground")
        if "narrow" in layout_lower or "corridor" in layout_lower:
            features["chokepoints"].append("narrow_passage")
        if "pit" in layout_lower or "trap" in layout_lower:
            features["hazards"].append("environmental_hazard")
        if "open" in layout_lower or "clearing" in layout_lower:
            features["open_areas"].append("open_ground")
        
        return features

    def _calculate_unit_positions(self, party_units: List[Dict], map_features: Dict, 
                                 objectives: str) -> List[Dict[str, Any]]:
        """Calculate specific positions for each unit."""
        positions = []
        
        # Group units by priority lines
        frontline_units = [u for u in party_units if u["priority"] == "frontline"]
        midline_units = [u for u in party_units if u["priority"] == "midline"]  
        backline_units = [u for u in party_units if u["priority"] == "backline"]
        flanker_units = [u for u in party_units if u["priority"] == "flanker"]
        
        # Position frontline units
        for i, unit in enumerate(frontline_units):
            positions.append({
                "unit_id": unit["id"],
                "position": {"x": 5 + i * 2, "y": 3},
                "facing": "north",
                "role_assignment": "frontline_defender",
                "positioning_reason": "Engage enemies directly and protect allies"
            })
        
        # Position midline units
        for i, unit in enumerate(midline_units):
            positions.append({
                "unit_id": unit["id"],
                "position": {"x": 6 + i * 2, "y": 6},
                "facing": "north",
                "role_assignment": "support_and_backup",
                "positioning_reason": "Provide support while maintaining flexibility"
            })
        
        # Position backline units
        for i, unit in enumerate(backline_units):
            positions.append({
                "unit_id": unit["id"],
                "position": {"x": 7 + i * 2, "y": 9},
                "facing": "north",
                "role_assignment": "ranged_support",
                "positioning_reason": "Maximum range while maintaining safety"
            })
        
        # Position flankers
        for i, unit in enumerate(flanker_units):
            side_offset = 8 if i % 2 == 0 else -8
            positions.append({
                "unit_id": unit["id"],
                "position": {"x": 10 + side_offset, "y": 5},
                "facing": "northeast" if side_offset > 0 else "northwest",
                "role_assignment": "flanking_specialist",
                "positioning_reason": "Exploit enemy flanks and provide mobility"
            })
        
        return positions

    def _select_optimal_formation(self, party_units: List[Dict], objectives: str) -> Dict[str, Any]:
        """Select the most appropriate formation for the party."""
        formation_types = {
            "line_formation": {
                "description": "Units arranged in a line across the battlefield",
                "best_for": ["frontal_assault", "defensive_stand"],
                "cohesion": "high",
                "flexibility": "low"
            },
            "wedge_formation": {
                "description": "V-shaped formation for breaking through enemy lines",
                "best_for": ["breakthrough", "concentrated_assault"],
                "cohesion": "medium",
                "flexibility": "medium"
            },
            "staggered_formation": {
                "description": "Units arranged in multiple offset lines",
                "best_for": ["balanced", "adaptive"],
                "cohesion": "medium",
                "flexibility": "high"
            },
            "circular_formation": {
                "description": "Defensive circle with casters in center",
                "best_for": ["defensive", "protection"],
                "cohesion": "high",
                "flexibility": "low"
            }
        }
        
        # Select based on objectives and party composition
        if objectives == "offensive":
            return formation_types["wedge_formation"]
        elif objectives == "defensive":
            return formation_types["circular_formation"]
        else:
            return formation_types["staggered_formation"]

    def _explain_positioning_decisions(self, party_units: List[Dict], map_features: Dict) -> List[str]:
        """Explain the reasoning behind positioning decisions."""
        explanations = []
        
        # Analyze party composition
        has_casters = any(u["role"] == "caster" for u in party_units)
        has_tanks = any(u["role"] in ["tank", "melee"] for u in party_units)
        has_ranged = any(u["role"] == "ranged" for u in party_units)
        
        if has_tanks:
            explanations.append("Tanks positioned forward to intercept enemies and protect allies")
        if has_casters:
            explanations.append("Casters positioned in rear with clear sight lines and escape routes")
        if has_ranged:
            explanations.append("Ranged units positioned for optimal range while avoiding melee")
        
        # Map-based explanations
        if map_features.get("cover_areas"):
            explanations.append("Positioning takes advantage of available cover")
        if map_features.get("elevation"):
            explanations.append("High ground positions prioritized for range advantage")
        if map_features.get("chokepoints"):
            explanations.append("Formation positioned to control key chokepoints")
        
        return explanations

    def _generate_alternative_setups(self, party_units: List[Dict], map_features: Dict) -> List[Dict[str, Any]]:
        """Generate alternative positioning setups."""
        alternatives = []
        
        alternatives.append({
            "name": "aggressive_setup",
            "description": "Forward positioning for immediate pressure",
            "trade_offs": "Higher damage potential but increased risk"
        })
        
        alternatives.append({
            "name": "defensive_setup", 
            "description": "Conservative positioning with fallback options",
            "trade_offs": "Greater safety but slower offensive capability"
        })
        
        alternatives.append({
            "name": "mobile_setup",
            "description": "Loose formation for maximum maneuverability", 
            "trade_offs": "High flexibility but reduced mutual support"
        })
        
        return alternatives

    def _analyze_positioning_factors(self, map_features: Dict, objectives: str) -> Dict[str, Any]:
        """Analyze factors affecting positioning decisions."""
        return {
            "map_constraints": list(map_features.keys()),
            "tactical_priorities": self._determine_tactical_priorities(objectives),
            "risk_factors": self._identify_risk_factors(map_features),
            "opportunity_factors": self._identify_opportunities(map_features)
        }

    def _determine_tactical_priorities(self, objectives: str) -> List[str]:
        """Determine tactical priorities based on objectives."""
        priority_map = {
            "offensive": ["damage_maximization", "enemy_elimination", "aggressive_positioning"],
            "defensive": ["ally_protection", "position_holding", "damage_mitigation"],
            "balanced": ["flexibility", "adaptability", "mutual_support"]
        }
        return priority_map.get(objectives, priority_map["balanced"])

    def _identify_risk_factors(self, map_features: Dict) -> List[str]:
        """Identify positioning risk factors."""
        risks = []
        
        if map_features.get("hazards"):
            risks.append("environmental_hazards")
        if map_features.get("chokepoints"):
            risks.append("potential_bottlenecks")
        if not map_features.get("cover_areas"):
            risks.append("limited_cover_options")
        
        return risks

    def _identify_opportunities(self, map_features: Dict) -> List[str]:
        """Identify positioning opportunities."""
        opportunities = []
        
        if map_features.get("elevation"):
            opportunities.append("elevation_advantage")
        if map_features.get("cover_areas"):
            opportunities.append("tactical_cover")
        if map_features.get("chokepoints"):
            opportunities.append("chokepoint_control")
        
        return opportunities

    def _parse_current_positions(self, current_positions: str) -> Dict[str, Any]:
        """Parse current unit positions."""
        # Simplified parsing - would be more sophisticated in practice
        import re
        
        result = {
            "unit_count": 0,
            "formation_integrity": "unknown",
            "spacing_issues": [],
            "position_vulnerabilities": [],
            "parsed_units": []
        }
        
        if not current_positions or not current_positions.strip():
            return result
            
        # Extract basic patterns from the position description
        lines = current_positions.lower().strip().split('\n')
        unit_patterns = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for position indicators
            position_match = re.search(r'(\w+)\s*(?:at|in|on)\s*(\w+)', line)
            if position_match:
                unit_name = position_match.group(1)
                position = position_match.group(2)
                unit_patterns.append({"unit": unit_name, "position": position})
            
            # Look for formation indicators
            if "formation" in line:
                if "tight" in line or "close" in line:
                    result["formation_integrity"] = "high"
                elif "spread" in line or "scattered" in line:
                    result["formation_integrity"] = "low"
                else:
                    result["formation_integrity"] = "medium"
                    
            # Look for spacing issues
            if "crowded" in line or "clustered" in line:
                result["spacing_issues"].append("overcrowding")
            elif "isolated" in line or "alone" in line:
                result["spacing_issues"].append("isolation")
                
            # Look for vulnerability indicators
            if "exposed" in line or "vulnerable" in line:
                result["position_vulnerabilities"].append("exposure")
            elif "surrounded" in line:
                result["position_vulnerabilities"].append("encirclement")
        
        result["unit_count"] = len(unit_patterns)
        result["parsed_units"] = unit_patterns
        
        # Default values if nothing specific was found
        if result["formation_integrity"] == "unknown":
            result["formation_integrity"] = "medium"
            
        return result

    def _analyze_combat_state(self, combat_state: str) -> Dict[str, Any]:
        """Analyze current combat state."""
        return {
            "threat_level": "medium",
            "initiative_status": "neutral",
            "casualties": "none",
            "enemy_positioning": "unknown"
        }

    def _identify_immediate_adjustments(self, positions: Dict, state_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify adjustments needed immediately."""
        return [
            {
                "type": "spacing_correction",
                "priority": "medium",
                "description": "Adjust unit spacing for better support"
            },
            {
                "type": "facing_adjustment",
                "priority": "low", 
                "description": "Orient units toward primary threats"
            }
        ]

    def _recommend_formation_changes(self, positions: Dict, tactical_situation: str) -> List[str]:
        """Recommend formation changes based on tactical situation."""
        if tactical_situation == "disadvantage":
            return ["Contract formation for mutual support", "Prepare defensive positions"]
        elif tactical_situation == "advantage":
            return ["Extend formation to exploit advantage", "Prepare for pursuit"]
        else:
            return ["Maintain current formation", "Be ready to adapt"]

    def _identify_priority_repositioning(self, positions: Dict, state_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify units that should be repositioned as priority."""
        return [
            {
                "unit": "vulnerable_caster",
                "current_risk": "high",
                "recommended_action": "move_to_safer_position"
            }
        ]

    def _plan_coordinated_movement(self, positions: Dict) -> Dict[str, Any]:
        """Plan coordinated movement to maintain formation."""
        return {
            "movement_sequence": ["tanks_first", "then_support", "finally_ranged"],
            "coordination_signals": ["visual_cues", "predetermined_positions"],
            "fallback_plan": "individual_movement_if_coordination_fails"
        }

    def _prepare_contingency_positions(self, positions: Dict, state_analysis: Dict) -> List[Dict[str, Any]]:
        """Prepare contingency positions for various scenarios."""
        return [
            {
                "scenario": "enemy_flanking",
                "response": "wheel_formation_to_face_threat"
            },
            {
                "scenario": "ally_casualty",
                "response": "close_formation_gaps"
            }
        ]

    def _assess_adjustment_urgency(self, state_analysis: Dict) -> str:
        """Assess how urgently adjustments are needed."""
        threat_level = state_analysis.get("threat_level", "medium")
        
        urgency_map = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "immediate"
        }
        
        return urgency_map.get(threat_level, "medium")

    def _calculate_optimal_spacing(self, unit_types: str, formation_goal: str) -> Dict[str, Any]:
        """Calculate optimal spacing between units."""
        spacing_guidelines = {
            "tight": {"melee": 5, "ranged": 10, "caster": 15},
            "standard": {"melee": 10, "ranged": 15, "caster": 20},
            "loose": {"melee": 15, "ranged": 20, "caster": 25}
        }
        
        return spacing_guidelines.get(formation_goal, spacing_guidelines["standard"])

    def _establish_cohesion_guidelines(self, unit_types: str) -> List[str]:
        """Establish guidelines for maintaining formation cohesion."""
        return [
            "Maintain visual contact between adjacent units",
            "Keep maximum separation distance under 30 feet",
            "Designate formation leader for movement coordination",
            "Establish fallback positions in case of formation break"
        ]

    def _adjust_for_threat_level(self, threat_level: str) -> Dict[str, Any]:
        """Adjust spacing based on threat level."""
        adjustments = {
            "low": {"spacing_modifier": 1.0, "notes": "Standard spacing maintained"},
            "medium": {"spacing_modifier": 0.8, "notes": "Slightly tighter for mutual support"},
            "high": {"spacing_modifier": 0.6, "notes": "Close formation for protection"},
            "critical": {"spacing_modifier": 0.4, "notes": "Very tight defensive formation"}
        }
        
        return adjustments.get(threat_level, adjustments["medium"])

    def _define_spacing_principles(self, formation_goal: str) -> List[str]:
        """Define core principles for unit spacing."""
        principles = {
            "tight": ["Maximize mutual support", "Enable coordinated actions", "Reduce area of effect vulnerability"],
            "loose": ["Maximize mobility", "Reduce area damage", "Enable independent action"],
            "flexible": ["Balance support and mobility", "Adapt to threats", "Maintain options"]
        }
        
        return principles.get(formation_goal, principles["flexible"])

    def _maintain_formation_integrity(self, unit_types: str, formation_goal: str) -> Dict[str, Any]:
        """Guidelines for maintaining formation integrity."""
        return {
            "communication_methods": ["hand_signals", "voice_commands", "magical_communication"],
            "movement_discipline": "maintain_relative_positions",
            "adaptation_protocols": "adjust_spacing_based_on_threats",
            "recovery_procedures": "rally_points_and_reformation_signals"
        }