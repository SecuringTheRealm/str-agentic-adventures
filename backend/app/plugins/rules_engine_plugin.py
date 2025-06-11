"""
Rules Engine Plugin for the Semantic Kernel.
This plugin provides D&D 5e SRD ruleset functionality to the agents.
"""
import logging
from typing import Dict, Any
import random

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from app.plugins.dnd5e_data import SKILLS, CONDITIONS, DIFFICULTY_CLASSES, SRD_SPELLS

logger = logging.getLogger(__name__)

class RulesEnginePlugin:
    """
    Plugin that provides D&D 5e SRD rules functionality.
    This plugin handles dice rolling, skill checks, and other game mechanics.
    """

    def __init__(self):
        """Initialize the rules engine plugin."""
        pass

    @kernel_function(
        description="Roll dice using standard RPG notation (e.g., 2d6+3).",
        name="roll_dice"
    )
    def roll_dice(self, dice_notation: str) -> Dict[str, Any]:
        """
        Roll dice using standard RPG notation (e.g., 2d6+3).
        
        Args:
            dice_notation: The dice notation to roll (e.g., "1d20", "2d6+3")
            
        Returns:
            Dict[str, Any]: The result of the dice roll
        """
        try:
            # Parse the dice notation
            parts = dice_notation.lower().replace(" ", "")
            
            # Handle modifiers
            modifier = 0
            if "+" in parts:
                parts, mod_str = parts.split("+", 1)
                modifier = int(mod_str)
            elif "-" in parts:
                parts, mod_str = parts.split("-", 1)
                modifier = -int(mod_str)
            
            # Handle dice rolls
            if "d" in parts:
                num_dice, dice_type = parts.split("d", 1)
                num_dice = int(num_dice) if num_dice else 1
                dice_type = int(dice_type)
                
                # Roll the dice
                rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
                total = sum(rolls) + modifier
                
                return {
                    "notation": dice_notation,
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": total
                }
            else:
                # Just a static number
                total = int(parts) + modifier
                return {
                    "notation": dice_notation,
                    "rolls": [],
                    "modifier": modifier,
                    "total": total
                }
        except Exception as e:
            logger.error(f"Error rolling dice: {str(e)}")
            return {
                "notation": dice_notation,
                "error": f"Invalid dice notation: {str(e)}"
            }

    @kernel_function(
        description="Perform a skill check against a target difficulty class (DC).",
        name="skill_check"
    )
    def skill_check(self, ability_score: int, proficient: bool = False, proficiency_bonus: int = 2, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Perform a skill check against a target difficulty class.
        
        Args:
            ability_score: The ability score (e.g., Strength, Dexterity) to use
            proficient: Whether the character is proficient in the skill
            proficiency_bonus: The character's proficiency bonus
            advantage: Whether the character has advantage on the check
            disadvantage: Whether the character has disadvantage on the check
            
        Returns:
            Dict[str, Any]: The result of the skill check
        """
        try:
            # Calculate ability modifier
            ability_modifier = (ability_score - 10) // 2
            
            # Add proficiency if applicable
            total_modifier = ability_modifier
            if proficient:
                total_modifier += proficiency_bonus
            
            # Roll the dice based on advantage/disadvantage
            if advantage and not disadvantage:
                # Roll with advantage (take the higher of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)
                rolls = [roll]
                advantage_type = "normal"
            
            # Calculate total
            total = roll + total_modifier
            
            return {
                "rolls": rolls,
                "ability_modifier": ability_modifier,
                "proficiency_bonus": proficiency_bonus if proficient else 0,
                "total_modifier": total_modifier,
                "advantage_type": advantage_type,
                "total": total
            }
        except Exception as e:
            logger.error(f"Error performing skill check: {str(e)}")
            return {
                "error": f"Error performing skill check: {str(e)}"
            }
    
    @kernel_function(
        description="Calculate whether an attack hits based on the attack roll and target's armor class.",
        name="resolve_attack"
    )
    def resolve_attack(self, attack_bonus: int, target_ac: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Calculate whether an attack hits based on the attack roll and target's armor class.
        
        Args:
            attack_bonus: The attack bonus to add to the roll
            target_ac: The armor class of the target
            advantage: Whether the attack has advantage
            disadvantage: Whether the attack has disadvantage
            
        Returns:
            Dict[str, Any]: The result of the attack roll
        """
        try:
            # Roll the dice based on advantage/disadvantage
            if advantage and not disadvantage:
                # Roll with advantage (take the higher of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)
                rolls = [roll]
                advantage_type = "normal"
            
            # Check for critical hit or miss
            is_critical_hit = roll == 20
            is_critical_miss = roll == 1
            
            # Calculate total
            total = roll + attack_bonus
            
            # Determine if hit
            is_hit = is_critical_hit or (not is_critical_miss and total >= target_ac)
            
            return {
                "rolls": rolls,
                "attack_bonus": attack_bonus,
                "total": total,
                "target_ac": target_ac,
                "advantage_type": advantage_type,
                "is_hit": is_hit,
                "is_critical_hit": is_critical_hit,
                "is_critical_miss": is_critical_miss
            }
        except Exception as e:
            logger.error(f"Error resolving attack: {str(e)}")
            return {
                "error": f"Error resolving attack: {str(e)}"
            }
    
    @kernel_function(
        description="Calculate damage for an attack based on the damage dice and modifiers.",
        name="calculate_damage"
    )
    def calculate_damage(self, damage_dice: str, is_critical: bool = False) -> Dict[str, Any]:
        """
        Calculate damage for an attack based on the damage dice and modifiers.
        
        Args:
            damage_dice: The damage dice notation (e.g., "1d6+3")
            is_critical: Whether this is a critical hit (doubles the dice)
            
        Returns:
            Dict[str, Any]: The calculated damage
        """
        try:
            # Use the roll_dice function to parse and roll the dice
            damage_roll = self.roll_dice(damage_dice)
            
            # If critical hit, add extra damage dice
            if is_critical:
                # Parse the dice notation to get the number of dice and type
                parts = damage_dice.lower().replace(" ", "")
                
                # Handle modifiers (but ignore them for critical calculation)
                if "+" in parts:
                    parts, _ = parts.split("+", 1)
                elif "-" in parts:
                    parts, _ = parts.split("-", 1)
                
                # Handle dice rolls
                if "d" in parts:
                    num_dice, dice_type = parts.split("d", 1)
                    num_dice = int(num_dice) if num_dice else 1
                    dice_type = int(dice_type)
                    
                    # Roll the extra dice for critical hit
                    extra_rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
                    damage_roll["critical_rolls"] = extra_rolls
                    damage_roll["total"] += sum(extra_rolls)
            
            return damage_roll
        except Exception as e:
            logger.error(f"Error calculating damage: {str(e)}")
            return {
                "error": f"Error calculating damage: {str(e)}"
            }

    @kernel_function(
        description="Perform a saving throw for a character.",
        name="saving_throw"
    )
    def saving_throw(self, ability_score: int, proficient: bool = False, proficiency_bonus: int = 2, dc: int = 10, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Perform a saving throw for a character.
        
        Args:
            ability_score: The ability score to use for the save
            proficient: Whether the character is proficient in this save
            proficiency_bonus: The character's proficiency bonus
            dc: The difficulty class to meet or beat
            advantage: Whether the character has advantage
            disadvantage: Whether the character has disadvantage
            
        Returns:
            Dict[str, Any]: The result of the saving throw
        """
        try:
            # Calculate ability modifier
            ability_modifier = (ability_score - 10) // 2
            
            # Add proficiency if applicable
            total_modifier = ability_modifier
            if proficient:
                total_modifier += proficiency_bonus
            
            # Roll the dice based on advantage/disadvantage
            if advantage and not disadvantage:
                # Roll with advantage (take the higher of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)
                rolls = [roll]
                advantage_type = "normal"
            
            # Calculate total
            total = roll + total_modifier
            
            # Determine success
            is_success = total >= dc
            is_critical_success = roll == 20
            is_critical_failure = roll == 1
            
            return {
                "rolls": rolls,
                "ability_modifier": ability_modifier,
                "proficiency_bonus": proficiency_bonus if proficient else 0,
                "total_modifier": total_modifier,
                "advantage_type": advantage_type,
                "total": total,
                "dc": dc,
                "is_success": is_success,
                "is_critical_success": is_critical_success,
                "is_critical_failure": is_critical_failure
            }
        except Exception as e:
            logger.error(f"Error performing saving throw: {str(e)}")
            return {
                "error": f"Error performing saving throw: {str(e)}"
            }

    @kernel_function(
        description="Calculate spell attack bonus and resolve spell attacks.",
        name="spell_attack"
    )
    def spell_attack(self, spell_attack_bonus: int, target_ac: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Calculate spell attack bonus and resolve spell attacks.
        
        Args:
            spell_attack_bonus: The character's spell attack bonus
            target_ac: The armor class of the target
            advantage: Whether the attack has advantage
            disadvantage: Whether the attack has disadvantage
            
        Returns:
            Dict[str, Any]: The result of the spell attack
        """
        try:
            # Roll the dice based on advantage/disadvantage
            if advantage and not disadvantage:
                # Roll with advantage (take the higher of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)
                rolls = [roll]
                advantage_type = "normal"
            
            # Check for critical hit or miss
            is_critical_hit = roll == 20
            is_critical_miss = roll == 1
            
            # Calculate total
            total = roll + spell_attack_bonus
            
            # Determine if hit
            is_hit = is_critical_hit or (not is_critical_miss and total >= target_ac)
            
            return {
                "rolls": rolls,
                "spell_attack_bonus": spell_attack_bonus,
                "total": total,
                "target_ac": target_ac,
                "advantage_type": advantage_type,
                "is_hit": is_hit,
                "is_critical_hit": is_critical_hit,
                "is_critical_miss": is_critical_miss
            }
        except Exception as e:
            logger.error(f"Error resolving spell attack: {str(e)}")
            return {
                "error": f"Error resolving spell attack: {str(e)}"
            }

    @kernel_function(
        description="Calculate proficiency bonus based on character level.",
        name="calculate_proficiency_bonus"
    )
    def calculate_proficiency_bonus(self, level: int) -> Dict[str, Any]:
        """
        Calculate proficiency bonus based on character level.
        
        Args:
            level: The character's level (1-20)
            
        Returns:
            Dict[str, Any]: The proficiency bonus for the given level
        """
        try:
            # D&D 5e proficiency bonus progression
            if level < 1:
                proficiency_bonus = 0
            elif level <= 4:
                proficiency_bonus = 2
            elif level <= 8:
                proficiency_bonus = 3
            elif level <= 12:
                proficiency_bonus = 4
            elif level <= 16:
                proficiency_bonus = 5
            elif level <= 20:
                proficiency_bonus = 6
            else:
                proficiency_bonus = 6  # Cap at level 20
            
            return {
                "level": level,
                "proficiency_bonus": proficiency_bonus
            }
        except Exception as e:
            logger.error(f"Error calculating proficiency bonus: {str(e)}")
            return {
                "error": f"Error calculating proficiency bonus: {str(e)}"
            }

    @kernel_function(
        description="Roll initiative for combat ordering.",
        name="roll_initiative"
    )
    def roll_initiative(self, dexterity_modifier: int, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Roll initiative for combat ordering.
        
        Args:
            dexterity_modifier: The character's Dexterity modifier
            advantage: Whether the character has advantage on initiative
            disadvantage: Whether the character has disadvantage on initiative
            
        Returns:
            Dict[str, Any]: The initiative roll result
        """
        try:
            # Roll the dice based on advantage/disadvantage
            if advantage and not disadvantage:
                # Roll with advantage (take the higher of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)
                roll2 = random.randint(1, 20)
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)
                rolls = [roll]
                advantage_type = "normal"
            
            # Calculate total initiative
            initiative = roll + dexterity_modifier
            
            return {
                "rolls": rolls,
                "dexterity_modifier": dexterity_modifier,
                "advantage_type": advantage_type,
                "initiative": initiative
            }
        except Exception as e:
            logger.error(f"Error rolling initiative: {str(e)}")
            return {
                "error": f"Error rolling initiative: {str(e)}"
            }

    @kernel_function(
        description="Get information about a D&D 5e skill including its associated ability.",
        name="get_skill_info"
    )
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """
        Get information about a D&D 5e skill including its associated ability.
        
        Args:
            skill_name: The name of the skill (e.g., "athletics", "perception")
            
        Returns:
            Dict[str, Any]: Information about the skill
        """
        try:
            skill_key = skill_name.lower().replace(" ", "_")
            
            if skill_key in SKILLS:
                skill_info = SKILLS[skill_key]
                return {
                    "skill": skill_name,
                    "ability": skill_info["ability"],
                    "description": skill_info["description"],
                    "found": True
                }
            else:
                return {
                    "skill": skill_name,
                    "found": False,
                    "message": f"Skill '{skill_name}' not found in D&D 5e skill list"
                }
        except Exception as e:
            logger.error(f"Error getting skill info: {str(e)}")
            return {
                "error": f"Error getting skill info: {str(e)}"
            }

    @kernel_function(
        description="Get information about a D&D 5e condition and its effects.",
        name="get_condition_info"
    )
    def get_condition_info(self, condition_name: str) -> Dict[str, Any]:
        """
        Get information about a D&D 5e condition and its effects.
        
        Args:
            condition_name: The name of the condition (e.g., "blinded", "frightened")
            
        Returns:
            Dict[str, Any]: Information about the condition
        """
        try:
            condition_key = condition_name.lower().replace(" ", "_")
            
            if condition_key in CONDITIONS:
                condition_info = CONDITIONS[condition_key]
                return {
                    "condition": condition_name,
                    "description": condition_info["description"],
                    "effects": condition_info["effects"],
                    "found": True
                }
            else:
                return {
                    "condition": condition_name,
                    "found": False,
                    "message": f"Condition '{condition_name}' not found in D&D 5e condition list"
                }
        except Exception as e:
            logger.error(f"Error getting condition info: {str(e)}")
            return {
                "error": f"Error getting condition info: {str(e)}"
            }

    @kernel_function(
        description="Get information about a D&D 5e spell from the SRD.",
        name="get_spell_info"
    )
    def get_spell_info(self, spell_name: str) -> Dict[str, Any]:
        """
        Get information about a D&D 5e spell from the SRD.
        
        Args:
            spell_name: The name of the spell (e.g., "fireball", "cure wounds")
            
        Returns:
            Dict[str, Any]: Information about the spell
        """
        try:
            spell_key = spell_name.lower().replace(" ", "_")
            
            if spell_key in SRD_SPELLS:
                spell_info = SRD_SPELLS[spell_key]
                return {
                    "spell": spell_name,
                    "level": spell_info["level"],
                    "school": spell_info["school"],
                    "casting_time": spell_info["casting_time"],
                    "range": spell_info["range"],
                    "components": spell_info["components"],
                    "duration": spell_info["duration"],
                    "description": spell_info["description"],
                    "found": True
                }
            else:
                return {
                    "spell": spell_name,
                    "found": False,
                    "message": f"Spell '{spell_name}' not found in SRD spell list"
                }
        except Exception as e:
            logger.error(f"Error getting spell info: {str(e)}")
            return {
                "error": f"Error getting spell info: {str(e)}"
            }

    @kernel_function(
        description="Get suggested difficulty class for a given task difficulty.",
        name="get_difficulty_class"
    )
    def get_difficulty_class(self, difficulty: str) -> Dict[str, Any]:
        """
        Get suggested difficulty class for a given task difficulty.
        
        Args:
            difficulty: The difficulty level (very_easy, easy, medium, hard, very_hard, nearly_impossible)
            
        Returns:
            Dict[str, Any]: The suggested DC for the difficulty
        """
        try:
            difficulty_key = difficulty.lower().replace(" ", "_")
            
            if difficulty_key in DIFFICULTY_CLASSES:
                dc = DIFFICULTY_CLASSES[difficulty_key]
                return {
                    "difficulty": difficulty,
                    "dc": dc,
                    "found": True
                }
            else:
                # Return all available difficulties
                return {
                    "difficulty": difficulty,
                    "found": False,
                    "message": f"Difficulty '{difficulty}' not recognized",
                    "available_difficulties": list(DIFFICULTY_CLASSES.keys())
                }
        except Exception as e:
            logger.error(f"Error getting difficulty class: {str(e)}")
            return {
                "error": f"Error getting difficulty class: {str(e)}"
            }
