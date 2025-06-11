"""
Rules Engine Plugin for the Semantic Kernel.
This plugin provides D&D 5e SRD ruleset functionality to the agents.
"""
import logging
from typing import Dict, Any
import random

from semantic_kernel.functions.kernel_function_decorator import kernel_function

logger = logging.getLogger(__name__)

class RulesEnginePlugin:
    """
    Plugin that provides D&D 5e SRD rules functionality.
    This plugin handles dice rolling, skill checks, and other game mechanics.
    """

    def __init__(self):
        """Initialize the rules engine plugin."""
        # D&D 5e experience thresholds for leveling up
        self.experience_thresholds = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        
        # Levels where proficiency bonus increases
        self.proficiency_bonus_levels = {
            1: 2, 5: 3, 9: 4, 13: 5, 17: 6
        }
        
        # Levels where ASI/feats are available
        self.asi_levels = [4, 8, 12, 16, 19]
        
        # Class hit dice
        self.class_hit_dice = {
            "barbarian": "1d12", "fighter": "1d10", "paladin": "1d10", "ranger": "1d10",
            "bard": "1d8", "cleric": "1d8", "druid": "1d8", "monk": "1d8", "rogue": "1d8", "warlock": "1d8",
            "sorcerer": "1d6", "wizard": "1d6"
        }

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
                
                # Handle modifiers (for critical hit calculation, we ignore modifiers for extra dice)
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
        description="Calculate the level for a character based on their experience points.",
        name="calculate_level"
    )
    def calculate_level(self, experience: int) -> Dict[str, Any]:
        """
        Calculate the level for a character based on their experience points.
        
        Args:
            experience: The character's current experience points
            
        Returns:
            Dict[str, Any]: The character's level and experience information
        """
        try:
            current_level = 1
            for level in range(20, 0, -1):
                if experience >= self.experience_thresholds[level]:
                    current_level = level
                    break
            
            next_level = min(current_level + 1, 20)
            exp_for_next = self.experience_thresholds[next_level] if next_level <= 20 else None
            exp_needed = exp_for_next - experience if exp_for_next else 0
            
            return {
                "current_level": current_level,
                "experience": experience,
                "experience_for_next_level": exp_for_next,
                "experience_needed": max(exp_needed, 0),
                "can_level_up": experience >= exp_for_next if exp_for_next else False
            }
        except Exception as e:
            logger.error(f"Error calculating level: {str(e)}")
            return {
                "error": f"Error calculating level: {str(e)}"
            }
    
    @kernel_function(
        description="Calculate proficiency bonus for a given level.",
        name="calculate_proficiency_bonus"
    )
    def calculate_proficiency_bonus(self, level: int) -> Dict[str, Any]:
        """
        Calculate proficiency bonus for a given level.
        
        Args:
            level: The character's level
            
        Returns:
            Dict[str, Any]: The proficiency bonus information
        """
        try:
            proficiency_bonus = 2
            for check_level in sorted(self.proficiency_bonus_levels.keys(), reverse=True):
                if level >= check_level:
                    proficiency_bonus = self.proficiency_bonus_levels[check_level]
                    break
            
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
        description="Check if a character can gain ability score improvement at their level.",
        name="check_asi_eligibility"
    )
    def check_asi_eligibility(self, level: int, asi_used: int) -> Dict[str, Any]:
        """
        Check if a character can gain ability score improvement at their level.
        
        Args:
            level: The character's level
            asi_used: Number of ASI/feats already used
            
        Returns:
            Dict[str, Any]: ASI eligibility information
        """
        try:
            asi_levels_reached = [asi_level for asi_level in self.asi_levels if level >= asi_level]
            asi_available = len(asi_levels_reached)
            asi_remaining = max(asi_available - asi_used, 0)
            
            return {
                "level": level,
                "asi_levels_reached": asi_levels_reached,
                "asi_available": asi_available,
                "asi_used": asi_used,
                "asi_remaining": asi_remaining,
                "can_improve_abilities": asi_remaining > 0
            }
        except Exception as e:
            logger.error(f"Error checking ASI eligibility: {str(e)}")
            return {
                "error": f"Error checking ASI eligibility: {str(e)}"
            }
    
    @kernel_function(
        description="Calculate hit points gained on level up.",
        name="calculate_level_up_hp"
    )
    def calculate_level_up_hp(self, character_class: str, constitution_modifier: int, use_average: bool = True) -> Dict[str, Any]:
        """
        Calculate hit points gained on level up.
        
        Args:
            character_class: The character's class
            constitution_modifier: The character's Constitution modifier
            use_average: Whether to use average hit points (True) or roll dice (False)
            
        Returns:
            Dict[str, Any]: Hit points calculation result
        """
        try:
            hit_dice = self.class_hit_dice.get(character_class.lower(), "1d8")
            
            if use_average:
                # Use average hit points (rounded up)
                if "d12" in hit_dice:
                    hp_gain = 7  # (12+1)/2 rounded up
                elif "d10" in hit_dice:
                    hp_gain = 6  # (10+1)/2 rounded up
                elif "d8" in hit_dice:
                    hp_gain = 5  # (8+1)/2 rounded up
                elif "d6" in hit_dice:
                    hp_gain = 4  # (6+1)/2 rounded up
                else:
                    hp_gain = 5  # Default
                    
                total_hp_gain = hp_gain + constitution_modifier
                
                return {
                    "hit_dice": hit_dice,
                    "base_hp": hp_gain,
                    "constitution_modifier": constitution_modifier,
                    "total_hp_gain": max(total_hp_gain, 1),  # Minimum 1 HP per level
                    "method": "average"
                }
            else:
                # Roll for hit points
                roll_result = self.roll_dice(hit_dice)
                base_hp = roll_result.get("total", 1)
                total_hp_gain = base_hp + constitution_modifier
                
                return {
                    "hit_dice": hit_dice,
                    "roll": roll_result,
                    "base_hp": base_hp,
                    "constitution_modifier": constitution_modifier,
                    "total_hp_gain": max(total_hp_gain, 1),  # Minimum 1 HP per level
                    "method": "rolled"
                }
        except Exception as e:
            logger.error(f"Error calculating level up HP: {str(e)}")
            return {
                "error": f"Error calculating level up HP: {str(e)}"
            }
