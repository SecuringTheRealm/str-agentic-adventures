"""
Rules Engine Plugin for the Semantic Kernel.
This plugin provides D&D 5e SRD ruleset functionality to the agents.
"""
import logging
from typing import Dict, Any
import random

from semantic_kernel.functions import kernel_function

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
    def roll_dice(self, dice_notation: str) -> str:
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
                
                result = f"Rolling {dice_notation}: "
                result += f"[{', '.join(map(str, rolls))}]"
                if modifier != 0:
                    result += f" + {modifier}" if modifier > 0 else f" - {abs(modifier)}"
                result += f" = {total}"
                return result
            else:
                # Just a static number
                total = int(parts) + modifier
                return f"Result: {total}"
        except Exception as e:
            logger.error(f"Error rolling dice: {str(e)}")
            return f"Invalid dice notation: {str(e)}"

    @kernel_function(
        description="Perform a skill check against a target difficulty class (DC).",
        name="skill_check"
    )
    def skill_check(self, ability_score: int, proficient: bool = False, proficiency_bonus: int = 2, advantage: bool = False, disadvantage: bool = False) -> str:
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
            
            result = f"Skill Check: "
            if advantage_type == "advantage":
                result += f"(advantage) {rolls[0]}, {rolls[1]} -> {roll}"
            elif advantage_type == "disadvantage":
                result += f"(disadvantage) {rolls[0]}, {rolls[1]} -> {roll}"
            else:
                result += f"{roll}"
            
            result += f" + {total_modifier} = {total}"
            return result
        except Exception as e:
            logger.error(f"Error performing skill check: {str(e)}")
            return f"Error performing skill check: {str(e)}"
    
    @kernel_function(
        description="Calculate whether an attack hits based on the attack roll and target's armor class.",
        name="resolve_attack"
    )
    def resolve_attack(self, attack_bonus: int, target_ac: int, advantage: bool = False, disadvantage: bool = False) -> str:
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
            
            result = f"Attack Roll: "
            if advantage_type == "advantage":
                result += f"(advantage) {rolls[0]}, {rolls[1]} -> {roll}"
            elif advantage_type == "disadvantage":
                result += f"(disadvantage) {rolls[0]}, {rolls[1]} -> {roll}"
            else:
                result += f"{roll}"
            
            result += f" + {attack_bonus} = {total} vs AC {target_ac}"
            
            if is_critical_hit:
                result += " - CRITICAL HIT!"
            elif is_critical_miss:
                result += " - Critical Miss!"
            elif is_hit:
                result += " - HIT!"
            else:
                result += " - Miss."
            
            return result
        except Exception as e:
            logger.error(f"Error resolving attack: {str(e)}")
            return f"Error resolving attack: {str(e)}"
    
    @kernel_function(
        description="Calculate damage for an attack based on the damage dice and modifiers.",
        name="calculate_damage"
    )
    def calculate_damage(self, damage_dice: str, is_critical: bool = False) -> str:
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
            damage_result = self.roll_dice(damage_dice)
            
            # If critical hit, add extra damage dice
            if is_critical:
                # Parse the dice notation to get the number of dice and type
                parts = damage_dice.lower().replace(" ", "")
                
                # Handle modifiers
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
                    extra_total = sum(extra_rolls)
                    
                    return f"CRITICAL DAMAGE: {damage_result} + {extra_total} extra = {extra_total + self._extract_total(damage_result)} total damage"
            
            return f"Damage: {damage_result}"
        except Exception as e:
            logger.error(f"Error calculating damage: {str(e)}")
            return f"Error calculating damage: {str(e)}"
    
    def _extract_total(self, damage_result: str) -> int:
        """Extract the total damage from a damage result string."""
        try:
            # Extract the number after the last '=' character
            if '=' in damage_result:
                return int(damage_result.split('=')[-1].strip())
            return 0
        except:
            return 0
