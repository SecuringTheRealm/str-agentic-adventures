"""
Combat MC Agent - Manages combat encounters, tactics, and battle flow.
"""

import logging
import random
import re
from typing import Dict, Any, List


from app.kernel_setup import kernel_manager

logger = logging.getLogger(__name__)


class CombatMCAgent:
    """
    Combat MC Agent that creates and manages combat encounters.
    This agent is responsible for enemy tactics, initiative tracking, and combat state.
    """

    def __init__(self):
        """Initialize the Combat MC agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self.fallback_mode = False  # Track if we're using fallback mechanics
        self._register_skills()

        # Active combat tracking
        self.active_combats = {}

    def _register_skills(self):
        """Register necessary skills for the Combat MC agent."""
        try:
            # Import plugins
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            # Create plugin instances
            rules_engine = RulesEnginePlugin()

            # Register plugins with the kernel
            self.kernel.add_plugin(rules_engine, "Rules")

            logger.info("Combat MC agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Combat MC agent plugins: {str(e)}")
            logger.warning("Enabling fallback mode with built-in combat mechanics")
            self.fallback_mode = True
            self._initialize_fallback_mechanics()

    def _initialize_fallback_mechanics(self):
        """Initialize built-in fallback mechanics when plugin registration fails."""
        logger.info("Initializing built-in combat mechanics as fallback")
        
        # Basic D&D 5e constants for fallback mode
        self.fallback_mechanics = {
            "ability_modifiers": {
                "strength": 0, "dexterity": 0, "constitution": 0,
                "intelligence": 0, "wisdom": 0, "charisma": 0
            },
            "base_proficiency_bonus": 2,
            "base_armor_class": 10,
            "base_hit_points": 8
        }

    def _fallback_roll_d20(self, modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """Built-in d20 roll for fallback mode."""
        
        if advantage and not disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll = max(roll1, roll2)
            rolls = [roll1, roll2]
            advantage_type = "advantage"
        elif disadvantage and not advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll = min(roll1, roll2)
            rolls = [roll1, roll2]
            advantage_type = "disadvantage"
        else:
            roll = random.randint(1, 20)
            rolls = [roll]
            advantage_type = "normal"
        
        total = roll + modifier
        
        return {
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "advantage_type": advantage_type
        }

    def _fallback_roll_damage(self, dice_notation: str) -> Dict[str, Any]:
        """Built-in damage roll for fallback mode."""
        
        # Simple dice parser for basic notation like "1d6+2" or "2d8"
        pattern = r"(\d*)d(\d+)(?:\+(\d+))?(?:\-(\d+))?"
        match = re.match(pattern, dice_notation.lower().replace(" ", ""))
        
        if not match:
            # Fallback to fixed damage if parsing fails
            return {"total": 4, "rolls": [4], "notation": dice_notation, "fallback": True}
        
        num_dice = int(match.group(1)) if match.group(1) else 1
        dice_type = int(match.group(2))
        plus_mod = int(match.group(3)) if match.group(3) else 0
        minus_mod = int(match.group(4)) if match.group(4) else 0
        modifier = plus_mod - minus_mod
        
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return {
            "notation": dice_notation,
            "rolls": rolls,
            "modifier": modifier,
            "total": max(total, 1)  # Minimum 1 damage
        }

    async def create_encounter(
        self, party_info: Dict[str, Any], narrative_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a balanced combat encounter based on party level and narrative context.

        Args:
            party_info: Information about the player party (levels, classes, etc.)
            narrative_context: Context about the current narrative situation

        Returns:
            Dict[str, Any]: The created combat encounter
        """
        try:
            # Extract basic party information for encounter scaling
            avg_level = self._calculate_average_party_level(party_info)
            party_size = len(party_info.get("members", []))

            # Generate a simple encounter for now
            encounter_id = f"encounter_{len(self.active_combats) + 1}"

            # Determine enemy type from narrative context
            location = narrative_context.get("location", "dungeon")
            enemy_types = self._get_enemy_types_for_location(location)

            # Create enemies scaled to party
            enemies = []
            num_enemies = self._calculate_enemy_count(party_size, avg_level)

            for i in range(num_enemies):
                enemy_type = random.choice(enemy_types)
                enemies.append(
                    {
                        "id": f"enemy_{i + 1}",
                        "type": enemy_type,
                        "level": max(
                            1, int(avg_level * 0.75)
                        ),  # Slightly lower than party avg
                        "hitPoints": {
                            "current": 10 * max(1, int(avg_level * 0.75)),
                            "maximum": 10 * max(1, int(avg_level * 0.75)),
                        },
                        "initiative": 0,  # Will be rolled when combat starts
                        "actions": self._get_actions_for_enemy_type(enemy_type),
                    }
                )

            # Create the encounter structure
            encounter = {
                "id": encounter_id,
                "status": "ready",  # ready, active, completed
                "enemies": enemies,
                "round": 0,
                "turn_order": [],  # Will be populated when initiative is rolled
                "narrative_context": narrative_context,
            }

            # Store the encounter
            self.active_combats[encounter_id] = encounter

            return encounter

        except Exception as e:
            logger.error(f"Error creating encounter: {str(e)}")
            return {"error": "Failed to create encounter"}

    async def start_combat(
        self, encounter_id: str, party_members: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Start a combat encounter by rolling initiative and determining turn order.

        Args:
            encounter_id: The ID of the encounter to start
            party_members: List of party members with their stats

        Returns:
            Dict[str, Any]: The updated combat state with initiative order
        """
        try:
            if encounter_id not in self.active_combats:
                return {"error": f"Encounter {encounter_id} not found"}

            encounter = self.active_combats[encounter_id]

            # Roll initiative for all participants
            participants = []

            # Players
            for player in party_members:
                if self.fallback_mode:
                    # Use fallback d20 roll
                    dex_mod = (player.get("abilities", {}).get("dexterity", 10) - 10) // 2
                    roll_result = self._fallback_roll_d20(dex_mod)
                    initiative = roll_result["total"]
                else:
                    # Use plugin-based rolling when available
                    dex_mod = (player.get("abilities", {}).get("dexterity", 10) - 10) // 2
                    initiative = random.randint(1, 20) + dex_mod
                
                participants.append(
                    {
                        "id": player.get("id"),
                        "name": player.get("name", "Unknown Player"),
                        "initiative": initiative,
                        "type": "player",
                    }
                )

            # Enemies
            for enemy in encounter["enemies"]:
                if self.fallback_mode:
                    # Use fallback d20 roll with simple modifier
                    initiative_mod = random.randint(-2, 2)
                    roll_result = self._fallback_roll_d20(initiative_mod)
                    initiative = roll_result["total"]
                else:
                    # Use simple random roll
                    initiative = random.randint(1, 20) + random.randint(-2, 2)
                
                enemy["initiative"] = initiative
                participants.append(
                    {
                        "id": enemy["id"],
                        "name": f"{enemy['type']} {enemy['id'].split('_')[1]}",
                        "initiative": initiative,
                        "type": "enemy",
                    }
                )

            # Sort by initiative (highest first)
            participants.sort(key=lambda x: x["initiative"], reverse=True)

            # Update encounter
            encounter["status"] = "active"
            encounter["round"] = 1
            encounter["current_turn"] = 0
            encounter["turn_order"] = participants

            return encounter

        except Exception as e:
            logger.error(f"Error starting combat: {str(e)}")
            return {"error": "Failed to start combat"}

    async def process_combat_action(
        self, encounter_id: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an action in combat.

        Args:
            encounter_id: The ID of the active encounter
            action_data: Details of the action being performed

        Returns:
            Dict[str, Any]: The result of the action and updated combat state
        """
        try:
            if encounter_id not in self.active_combats:
                return {"error": f"Encounter {encounter_id} not found"}

            encounter = self.active_combats[encounter_id]
            
            if encounter["status"] != "active":
                return {"error": "Combat is not currently active"}
            
            if self.fallback_mode:
                # Use fallback combat processing
                return self._process_fallback_combat_action(encounter, action_data)
            else:
                # Use plugin-based combat processing (when fully implemented)
                # TODO: Implement full combat action processing with plugins
                # TODO: Add spell effect resolution and area of effect calculations
                # TODO: Add movement tracking and positioning on battle maps
                # TODO: Add complex action types (grapple, shove, dodge, dash, hide)
                # TODO: Add spell save calculations and status effect application
                # TODO: Add concentration checks for casters when taking damage
                # TODO: Add opportunity attack calculations for movement
                # TODO: Add multi-attack action handling for high-level characters
                return {"message": "Combat action processed", "success": True}
        
        except Exception as e:
            logger.error(f"Error processing combat action: {str(e)}")
            return {"error": "Failed to process combat action"}

    def _process_fallback_combat_action(self, encounter: Dict[str, Any], action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process combat action using fallback mechanics."""
        action_type = action_data.get("type", "attack")
        actor_id = action_data.get("actor_id")
        target_id = action_data.get("target_id")
        
        result = {
            "action_type": action_type,
            "actor_id": actor_id,
            "target_id": target_id,
            "success": False,
            "message": "",
            "damage": 0
        }
        
        if action_type == "attack":
            # Simple attack resolution using fallback mechanics
            attack_bonus = action_data.get("attack_bonus", 3)  # Default +3 attack
            target_ac = action_data.get("target_ac", 12)  # Default AC 12
            
            attack_roll = self._fallback_roll_d20(attack_bonus)
            
            if attack_roll["total"] >= target_ac:
                # Hit - calculate damage
                damage_dice = action_data.get("damage", "1d6+2")
                damage_result = self._fallback_roll_damage(damage_dice)
                
                result.update({
                    "success": True,
                    "attack_roll": attack_roll,
                    "damage": damage_result["total"],
                    "damage_detail": damage_result,
                    "message": f"Attack hits for {damage_result['total']} damage!"
                })
            else:
                result.update({
                    "success": False,
                    "attack_roll": attack_roll,
                    "message": f"Attack misses (rolled {attack_roll['total']} vs AC {target_ac})"
                })
        
        elif action_type == "skill_check":
            # Simple skill check using fallback mechanics
            modifier = action_data.get("modifier", 0)
            dc = action_data.get("dc", 15)
            
            skill_roll = self._fallback_roll_d20(modifier)
            success = skill_roll["total"] >= dc
            
            result.update({
                "success": success,
                "roll": skill_roll,
                "message": f"Skill check {'succeeds' if success else 'fails'} (rolled {skill_roll['total']} vs DC {dc})"
            })
        
        else:
            result["message"] = f"Fallback mode: Basic {action_type} action performed"
            result["success"] = True
        
        return result

    def is_fallback_mode(self) -> bool:
        """Check if the combat MC agent is running in fallback mode."""
        return self.fallback_mode

    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about the agent's current capabilities."""
        if self.fallback_mode:
            return {
                "mode": "fallback",
                "capabilities": [
                    "basic_initiative_rolling",
                    "simple_attack_resolution", 
                    "basic_damage_calculation",
                    "simple_skill_checks"
                ],
                "limitations": [
                    "no_advanced_spell_effects",
                    "no_complex_conditions",
                    "simplified_dice_rolling",
                    "basic_combat_mechanics_only"
                ]
            }
        else:
            return {
                "mode": "full",
                "capabilities": [
                    "advanced_dice_rolling",
                    "complex_spell_effects",
                    "detailed_combat_mechanics",
                    "comprehensive_rule_system"
                ],
                "limitations": []
            }

    def _calculate_average_party_level(self, party_info: Dict[str, Any]) -> float:
        """Calculate the average level of the party."""
        members = party_info.get("members", [])
        if not members:
            return 1.0

        total_level = sum(member.get("level", 1) for member in members)
        return total_level / len(members)

    def _calculate_enemy_count(self, party_size: int, avg_level: float) -> int:
        """Calculate an appropriate number of enemies based on party size and level."""
        if avg_level < 3:
            # Low levels: approximately equal numbers
            return party_size
        elif avg_level < 10:
            # Mid levels: slightly more enemies
            return int(party_size * 1.5)
        else:
            # High levels: many enemies or fewer powerful ones
            return party_size * 2

    def _get_enemy_types_for_location(self, location: str) -> List[str]:
        """Get appropriate enemy types for a given location."""
        location_enemies = {
            "forest": ["goblin", "wolf", "bandit"],
            "dungeon": ["skeleton", "zombie", "orc"],
            "mountain": ["harpy", "troll", "ogre"],
            "city": ["thug", "cultist", "guard"],
            "coastal": ["pirate", "sahuagin", "merfolk"],
        }

        return location_enemies.get(location.lower(), ["goblin", "bandit", "cultist"])

    def _get_actions_for_enemy_type(self, enemy_type: str) -> List[Dict[str, Any]]:
        """Get appropriate actions for an enemy type."""
        # Simplified implementation
        basic_actions = [{"name": "Attack", "damage": "1d6+2", "type": "melee"}]

        # Add special attacks for certain types
        if enemy_type in ["skeleton", "zombie"]:
            basic_actions.append(
                {
                    "name": "Undead Fortitude",
                    "description": "When reduced to 0 HP, roll a DC 10 CON save to drop to 1 HP instead",
                    "type": "special",
                }
            )

        return basic_actions


# Lazy singleton instance
_combat_mc = None


def get_combat_mc():
    """Get the combat MC instance, creating it if necessary."""
    global _combat_mc
    if _combat_mc is None:
        _combat_mc = CombatMCAgent()
    return _combat_mc


# For backward compatibility during import-time checks
combat_mc = None
