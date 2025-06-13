"""
Combat MC Agent - Manages combat encounters, tactics, and battle flow.
"""

import logging
import random
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
            # TODO: Implement proper fallback behavior when plugin registration fails
            # Consider graceful degradation or alternative combat mechanics
            pass

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
                initiative = random.randint(1, 20) + random.randint(
                    -2, 2
                )  # Simple initiative mod
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
            
            # Extract action information
            action_type = action_data.get("type", "attack")
            actor_id = action_data.get("actor_id")
            target_id = action_data.get("target_id")
            
            result = {"message": "Combat action processed", "success": True}
            
            # Handle damage-dealing actions that might trigger concentration checks
            if action_type in ["attack", "spell_attack"] and "damage" in action_data:
                damage_result = await self._process_damage_action(
                    encounter, actor_id, target_id, action_data
                )
                result.update(damage_result)
            
            # Store updated encounter
            self.active_combats[encounter_id] = encounter
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing combat action: {str(e)}")
            return {"error": f"Failed to process combat action: {str(e)}"}
        
        # TODO: Implement full combat action processing
        # TODO: Add spell effect resolution and area of effect calculations
        # TODO: Add movement tracking and positioning on battle maps
        # TODO: Add complex action types (grapple, shove, dodge, dash, hide)
        # TODO: Add spell save calculations and status effect application
        # TODO: Add opportunity attack calculations for movement
        # TODO: Add multi-attack action handling for high-level characters

    async def _process_damage_action(
        self, encounter: Dict[str, Any], actor_id: str, target_id: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a damage-dealing action and handle concentration checks.

        Args:
            encounter: The active encounter
            actor_id: ID of the actor performing the action
            target_id: ID of the target receiving damage
            action_data: Action details including damage

        Returns:
            Dict[str, Any]: Result of the damage action including concentration checks
        """
        try:
            damage = action_data.get("damage", 0)
            result = {
                "action_type": action_data.get("type"),
                "actor_id": actor_id,
                "target_id": target_id,
                "damage_dealt": damage
            }
            
            # Check if target is concentrating on a spell
            target_concentrating = action_data.get("target_concentrating", False)
            target_constitution = action_data.get("target_constitution", 10)
            target_proficient_con = action_data.get("target_proficient_constitution", False)
            target_proficiency_bonus = action_data.get("target_proficiency_bonus", 2)
            target_war_caster = action_data.get("target_war_caster", False)
            
            if target_concentrating and damage > 0:
                # Use the rules engine to perform concentration check
                from app.plugins.rules_engine_plugin import RulesEnginePlugin
                rules_engine = RulesEnginePlugin()
                
                concentration_result = rules_engine.concentration_check(
                    damage_taken=damage,
                    constitution_score=target_constitution,
                    proficient_in_constitution=target_proficient_con,
                    proficiency_bonus=target_proficiency_bonus,
                    war_caster_feat=target_war_caster
                )
                
                result["concentration_check"] = concentration_result
                
                if not concentration_result.get("success", False):
                    result["concentration_lost"] = True
                    result["message"] = f"Target takes {damage} damage and loses concentration on their spell!"
                else:
                    result["concentration_maintained"] = True
                    result["message"] = f"Target takes {damage} damage but maintains concentration on their spell."
            else:
                result["message"] = f"Target takes {damage} damage."
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing damage action: {str(e)}")
            return {"error": f"Failed to process damage action: {str(e)}"}

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
