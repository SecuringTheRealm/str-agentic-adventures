"""
Rules Engine Plugin for the Semantic Kernel.
This plugin provides D&D 5e SRD ruleset functionality to the agents.
"""

import logging
from typing import Dict, Any, List
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
        # Roll history for tracking dice rolls
        self.roll_history = []
        self.max_history = 100

        # D&D 5e experience thresholds for leveling up
        self.experience_thresholds = {
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500,
            6: 14000,
            7: 23000,
            8: 34000,
            9: 48000,
            10: 64000,
            11: 85000,
            12: 100000,
            13: 120000,
            14: 140000,
            15: 165000,
            16: 195000,
            17: 225000,
            18: 265000,
            19: 305000,
            20: 355000,
        }

        # Levels where proficiency bonus increases
        self.proficiency_bonus_levels = {1: 2, 5: 3, 9: 4, 13: 5, 17: 6}

        # Levels where ASI/feats are available
        self.asi_levels = [4, 8, 12, 16, 19]

        # Class hit dice
        self.class_hit_dice = {
            "barbarian": "1d12",
            "fighter": "1d10",
            "paladin": "1d10",
            "ranger": "1d10",
            "bard": "1d8",
            "cleric": "1d8",
            "druid": "1d8",
            "monk": "1d8",
            "rogue": "1d8",
            "warlock": "1d8",
            "sorcerer": "1d6",
            "wizard": "1d6",
        }

        # TODO: Implement spell system components
        # TODO: Add spell slot tracking by level and class
        # TODO: Add spell save DC calculation
        # TODO: Add spell attack bonus calculation
        # TODO: Add spell effect resolution system
        # TODO: Add concentration tracking for ongoing spells

        # D&D 5e spell slot progression tables
        self.spell_slot_tables = {
            # Full casters (Wizard, Sorcerer, Cleric, Druid, Bard)
            "full_caster": {
                1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
                2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
                8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
                9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
                10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
                11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
                12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
                13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
                14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
                15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
                16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
                17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
                18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
                19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
                20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
            },
            # Half casters (Paladin, Ranger)
            "half_caster": {
                1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
                2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
                3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
                14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
                15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
                16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
                17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
                18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
                19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
                20: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            },
            # Third casters (Eldritch Knight Fighter, Arcane Trickster Rogue)
            "third_caster": {
                1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
                2: [0, 0, 0, 0, 0, 0, 0, 0, 0],
                3: [2, 0, 0, 0, 0, 0, 0, 0, 0],
                4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                5: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                6: [3, 0, 0, 0, 0, 0, 0, 0, 0],
                7: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                8: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                9: [4, 2, 0, 0, 0, 0, 0, 0, 0],
                10: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                11: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                12: [4, 3, 0, 0, 0, 0, 0, 0, 0],
                13: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                14: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                15: [4, 3, 2, 0, 0, 0, 0, 0, 0],
                16: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                17: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                18: [4, 3, 3, 0, 0, 0, 0, 0, 0],
                19: [4, 3, 3, 1, 0, 0, 0, 0, 0],
                20: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            },
            # Warlock (unique pact magic system)
            "warlock": {
                1: [1, 0, 0, 0, 0, 0, 0, 0, 0],
                2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
                3: [0, 2, 0, 0, 0, 0, 0, 0, 0],
                4: [0, 2, 0, 0, 0, 0, 0, 0, 0],
                5: [0, 0, 2, 0, 0, 0, 0, 0, 0],
                6: [0, 0, 2, 0, 0, 0, 0, 0, 0],
                7: [0, 0, 0, 2, 0, 0, 0, 0, 0],
                8: [0, 0, 0, 2, 0, 0, 0, 0, 0],
                9: [0, 0, 0, 0, 2, 0, 0, 0, 0],
                10: [0, 0, 0, 0, 2, 0, 0, 0, 0],
                11: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                12: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                13: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                14: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                15: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                16: [0, 0, 0, 0, 3, 0, 0, 0, 0],
                17: [0, 0, 0, 0, 4, 0, 0, 0, 0],
                18: [0, 0, 0, 0, 4, 0, 0, 0, 0],
                19: [0, 0, 0, 0, 4, 0, 0, 0, 0],
                20: [0, 0, 0, 0, 4, 0, 0, 0, 0],
            },
        }

        # Map character classes to caster types
        self.class_caster_types = {
            "wizard": "full_caster",
            "sorcerer": "full_caster",
            "cleric": "full_caster",
            "druid": "full_caster",
            "bard": "full_caster",
            "paladin": "half_caster",
            "ranger": "half_caster",
            "warlock": "warlock",
            "fighter": "third_caster",  # Eldritch Knight subclass
            "rogue": "third_caster",   # Arcane Trickster subclass
            # Non-casters return no spell slots
            "barbarian": None,
            "monk": None,
        }

    @kernel_function(
        description="Roll dice using standard D&D notation with advanced features (e.g., '1d20', '2d6+3', '4d6dl1', '2d20kh1').",
        name="roll_dice",
    )
    def roll_dice(self, dice_notation: str) -> Dict[str, Any]:
        """
        Roll dice based on the given notation with support for advanced D&D features.

        Supported notation:
        - Basic: 1d20, 2d6+3, 3d8-1
        - Drop lowest: 4d6dl1 (drop 1 lowest)
        - Keep highest: 2d20kh1 (advantage)
        - Keep lowest: 2d20kl1 (disadvantage)
        - Reroll: 1d6r1 (reroll 1s)
        - Multiple pools: 2d6+1d4+3

        Args:
            dice_notation: Advanced dice notation string

        Returns:
            Dict[str, Any]: Roll results with individual rolls, modifiers, and total
        """
        try:
            result = self._parse_and_roll_dice(dice_notation)

            # Add to roll history
            self._add_to_history(result)

            return result

        except Exception as e:
            logger.error(f"Error rolling dice: {str(e)}")
            return {
                "notation": dice_notation,
                "error": f"Invalid dice notation: {str(e)}",
            }

    def _parse_and_roll_dice(self, dice_notation: str) -> Dict[str, Any]:
        """Parse and execute dice roll notation."""
        original_notation = dice_notation
        dice_notation = dice_notation.lower().replace(" ", "")

        # Check if this is actually multiple pools (more than one 'd')
        d_count = dice_notation.count("d")

        # If only one 'd', treat as single pool even with modifiers
        if d_count <= 1:
            return self._roll_single_pool(original_notation, dice_notation)

        # Multiple dice pools (e.g., "2d6+1d4+3")
        if "+" in dice_notation or "-" in dice_notation:
            return self._handle_multiple_pools(original_notation, dice_notation)

        # Single dice pool with potential advanced notation
        return self._roll_single_pool(original_notation, dice_notation)

    def _handle_multiple_pools(
        self, original_notation: str, dice_notation: str
    ) -> Dict[str, Any]:
        """Handle multiple dice pools in one expression."""
        import re

        # Split by + and - while preserving the operators
        parts = re.split(r"(\+|\-)", dice_notation)
        pools = []
        total = 0
        overall_modifier = 0

        current_sign = 1
        for part in parts:
            if part == "+":
                current_sign = 1
            elif part == "-":
                current_sign = -1
            elif part.strip():
                if "d" in part:
                    # It's a dice pool
                    pool_result = self._roll_single_pool(part, part)
                    pool_result["modifier"] = current_sign
                    pools.append(pool_result)
                    total += pool_result["total"] * current_sign
                else:
                    # It's a static modifier
                    value = int(part) * current_sign
                    overall_modifier += value
                    pools.append(
                        {
                            "type": "modifier",
                            "value": value,
                            "notation": f"{'+' if current_sign > 0 else ''}{value}",
                        }
                    )
                    total += value

        return {
            "notation": original_notation,
            "pools": pools,
            "modifier": overall_modifier,
            "total": total,
        }

    def _roll_single_pool(
        self, original_notation: str, dice_notation: str
    ) -> Dict[str, Any]:
        """Roll a single dice pool with potential advanced notation."""
        # Parse basic dice notation (XdY)
        if "d" not in dice_notation:
            # Just a number
            return {
                "notation": original_notation,
                "total": int(dice_notation),
                "rolls": [],
                "modifier": int(dice_notation),
            }

        # Extract modifiers first
        modifier = 0
        base_notation = dice_notation

        # Handle simple +/- modifiers (for single pools only)
        if "+" in dice_notation and not any(
            x in dice_notation for x in ["dl", "dh", "kh", "kl", "r"]
        ):
            base_notation, mod_str = dice_notation.split("+", 1)
            modifier = int(mod_str)
        elif "-" in dice_notation and not any(
            x in dice_notation for x in ["dl", "dh", "kh", "kl", "r"]
        ):
            base_notation, mod_str = dice_notation.split("-", 1)
            modifier = -int(mod_str)

        # Extract advanced notation modifiers
        modifiers = self._extract_advanced_modifiers(base_notation)
        base_dice = modifiers["base_dice"]

        # Parse basic XdY
        num_dice, dice_type = base_dice.split("d")
        num_dice = int(num_dice) if num_dice else 1
        dice_type = int(dice_type)

        # Roll initial dice
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]

        # Apply advanced modifiers
        result = {
            "notation": original_notation,
            "rolls": rolls.copy(),
            "modifier": modifier,
            "total": 0,
        }

        # Handle rerolls
        if modifiers["reroll"]:
            reroll_value = modifiers["reroll"]
            rerolls = []

            # Keep rerolling until no more reroll values
            for i, roll in enumerate(rolls):
                while roll == reroll_value:
                    new_roll = random.randint(1, dice_type)
                    rerolls.append({"original": roll, "new": new_roll, "index": i})
                    roll = new_roll
                    rolls[i] = roll  # Update the roll

            if rerolls:
                result["rerolls"] = rerolls
                # Update the rolls in the result
                result["rolls"] = rolls.copy()

        # Handle drop/keep modifiers
        final_rolls = rolls.copy()
        dropped = []

        if modifiers["drop_lowest"]:
            count = modifiers["drop_lowest"]
            sorted_indices = sorted(range(len(rolls)), key=lambda i: rolls[i])
            for i in range(min(count, len(rolls))):
                idx = sorted_indices[i]
                dropped.append(rolls[idx])
                final_rolls[idx] = 0  # Mark as dropped
            result["dropped"] = dropped

        elif modifiers["drop_highest"]:
            count = modifiers["drop_highest"]
            sorted_indices = sorted(
                range(len(rolls)), key=lambda i: rolls[i], reverse=True
            )
            for i in range(min(count, len(rolls))):
                idx = sorted_indices[i]
                dropped.append(rolls[idx])
                final_rolls[idx] = 0  # Mark as dropped
            result["dropped"] = dropped

        elif modifiers["keep_highest"]:
            count = modifiers["keep_highest"]
            sorted_indices = sorted(
                range(len(rolls)), key=lambda i: rolls[i], reverse=True
            )
            for i in range(count, len(rolls)):
                idx = sorted_indices[i]
                dropped.append(rolls[idx])
                final_rolls[idx] = 0  # Mark as dropped
            result["dropped"] = dropped

        elif modifiers["keep_lowest"]:
            count = modifiers["keep_lowest"]
            sorted_indices = sorted(range(len(rolls)), key=lambda i: rolls[i])
            for i in range(count, len(rolls)):
                idx = sorted_indices[i]
                dropped.append(rolls[idx])
                final_rolls[idx] = 0  # Mark as dropped
            result["dropped"] = dropped

        # Calculate total from non-dropped rolls plus modifier
        dice_total = sum(roll for roll in final_rolls if roll > 0)
        result["total"] = dice_total + modifier

        return result

    def _extract_advanced_modifiers(self, dice_notation: str) -> Dict[str, Any]:
        """Extract advanced notation modifiers from dice string."""
        import re

        modifiers = {
            "base_dice": dice_notation,
            "drop_lowest": None,
            "drop_highest": None,
            "keep_highest": None,
            "keep_lowest": None,
            "reroll": None,
        }

        # Extract drop lowest (dl)
        dl_match = re.search(r"dl(\d+)", dice_notation)
        if dl_match:
            modifiers["drop_lowest"] = int(dl_match.group(1))
            modifiers["base_dice"] = dice_notation.replace(dl_match.group(0), "")

        # Extract drop highest (dh)
        dh_match = re.search(r"dh(\d+)", dice_notation)
        if dh_match:
            modifiers["drop_highest"] = int(dh_match.group(1))
            modifiers["base_dice"] = dice_notation.replace(dh_match.group(0), "")

        # Extract keep highest (kh)
        kh_match = re.search(r"kh(\d+)", dice_notation)
        if kh_match:
            modifiers["keep_highest"] = int(kh_match.group(1))
            modifiers["base_dice"] = dice_notation.replace(kh_match.group(0), "")

        # Extract keep lowest (kl)
        kl_match = re.search(r"kl(\d+)", dice_notation)
        if kl_match:
            modifiers["keep_lowest"] = int(kl_match.group(1))
            modifiers["base_dice"] = dice_notation.replace(kl_match.group(0), "")

        # Extract reroll (r)
        r_match = re.search(r"r(\d+)", dice_notation)
        if r_match:
            modifiers["reroll"] = int(r_match.group(1))
            modifiers["base_dice"] = dice_notation.replace(r_match.group(0), "")

        return modifiers

    @kernel_function(
        description="Perform a skill check against a target difficulty class (DC).",
        name="skill_check",
    )
    def skill_check(
        self,
        ability_score: int,
        proficient: bool = False,
        proficiency_bonus: int = 2,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> Dict[str, Any]:
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
                "total": total,
            }
        except Exception as e:
            logger.error(f"Error performing skill check: {str(e)}")
            return {"error": f"Error performing skill check: {str(e)}"}

    @kernel_function(
        description="Calculate whether an attack hits based on the attack roll and target's armor class.",
        name="resolve_attack",
    )
    def resolve_attack(
        self,
        attack_bonus: int,
        target_ac: int,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> Dict[str, Any]:
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
                "is_critical_miss": is_critical_miss,
            }
        except Exception as e:
            logger.error(f"Error resolving attack: {str(e)}")
            return {"error": f"Error resolving attack: {str(e)}"}

    @kernel_function(
        description="Calculate damage for an attack based on the damage dice and modifiers.",
        name="calculate_damage",
    )
    def calculate_damage(
        self, damage_dice: str, is_critical: bool = False
    ) -> Dict[str, Any]:
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
                    extra_rolls = [
                        random.randint(1, dice_type) for _ in range(num_dice)
                    ]
                    damage_roll["critical_rolls"] = extra_rolls
                    damage_roll["total"] += sum(extra_rolls)

            return damage_roll
        except Exception as e:
            logger.error(f"Error calculating damage: {str(e)}")
            return {"error": f"Error calculating damage: {str(e)}"}

    @kernel_function(
        description="Calculate the level for a character based on their experience points.",
        name="calculate_level",
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
            exp_for_next = (
                self.experience_thresholds[next_level] if next_level <= 20 else None
            )
            exp_needed = exp_for_next - experience if exp_for_next else 0

            return {
                "current_level": current_level,
                "experience": experience,
                "experience_for_next_level": exp_for_next,
                "experience_needed": max(exp_needed, 0),
                "can_level_up": experience >= exp_for_next if exp_for_next else False,
            }
        except Exception as e:
            logger.error(f"Error calculating level: {str(e)}")
            return {"error": f"Error calculating level: {str(e)}"}

    @kernel_function(
        description="Calculate proficiency bonus for a given level.",
        name="calculate_proficiency_bonus",
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
            for check_level in sorted(
                self.proficiency_bonus_levels.keys(), reverse=True
            ):
                if level >= check_level:
                    proficiency_bonus = self.proficiency_bonus_levels[check_level]
                    break

            return {"level": level, "proficiency_bonus": proficiency_bonus}
        except Exception as e:
            logger.error(f"Error calculating proficiency bonus: {str(e)}")
            return {"error": f"Error calculating proficiency bonus: {str(e)}"}

    @kernel_function(
        description="Check if a character can gain ability score improvement at their level.",
        name="check_asi_eligibility",
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
            asi_levels_reached = [
                asi_level for asi_level in self.asi_levels if level >= asi_level
            ]
            asi_available = len(asi_levels_reached)
            asi_remaining = max(asi_available - asi_used, 0)

            return {
                "level": level,
                "asi_levels_reached": asi_levels_reached,
                "asi_available": asi_available,
                "asi_used": asi_used,
                "asi_remaining": asi_remaining,
                "can_improve_abilities": asi_remaining > 0,
            }
        except Exception as e:
            logger.error(f"Error checking ASI eligibility: {str(e)}")
            return {"error": f"Error checking ASI eligibility: {str(e)}"}

    @kernel_function(
        description="Calculate hit points gained on level up.",
        name="calculate_level_up_hp",
    )
    def calculate_level_up_hp(
        self, character_class: str, constitution_modifier: int, use_average: bool = True
    ) -> Dict[str, Any]:
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
                    "method": "average",
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
                    "method": "rolled",
                }
        except Exception as e:
            logger.error(f"Error calculating level up HP: {str(e)}")
            return {"error": f"Error calculating level up HP: {str(e)}"}

    def roll_with_character(
        self, dice_notation: str, character: Dict[str, Any], skill: str = None
    ) -> Dict[str, Any]:
        """
        Roll dice with character context for automatic modifiers.

        Args:
            dice_notation: Dice notation to roll
            character: Character data with abilities and proficiencies
            skill: Skill name to apply modifiers for

        Returns:
            Dict[str, Any]: Roll result with character bonuses applied
        """
        base_result = self.roll_dice(dice_notation)

        if "error" in base_result:
            return base_result

        # Calculate character bonus
        character_bonus = 0

        if skill and "abilities" in character:
            # Map skills to abilities (simplified mapping)
            skill_ability_map = {
                "athletics": "strength",
                "stealth": "dexterity",
                "perception": "wisdom",
                "investigation": "intelligence",
                "persuasion": "charisma",
                "intimidation": "charisma",
            }

            ability = skill_ability_map.get(skill.lower())
            if ability and ability in character["abilities"]:
                ability_score = character["abilities"][ability]
                ability_modifier = (ability_score - 10) // 2
                character_bonus += ability_modifier

                # Add proficiency bonus if proficient
                if "proficiencies" in character and skill in character["proficiencies"]:
                    proficiency_bonus = character.get("proficiency_bonus", 2)
                    character_bonus += proficiency_bonus

        # Apply character bonus to total
        base_result["character_bonus"] = character_bonus
        base_result["total"] += character_bonus

        return base_result

    def input_manual_roll(self, dice_notation: str, result: int) -> Dict[str, Any]:
        """
        Input a manual roll result (for when dice are rolled physically).

        Args:
            dice_notation: The dice notation that was supposed to be rolled
            result: The actual result from physical dice

        Returns:
            Dict[str, Any]: Manual roll record
        """
        manual_result = {
            "notation": dice_notation,
            "manual_result": result,
            "total": result,
            "type": "manual",
            "is_manual": True,
        }

        self._add_to_history(manual_result)
        return manual_result

    def clear_roll_history(self):
        """Clear the roll history."""
        self.roll_history = []

    def get_roll_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get the roll history.

        Args:
            limit: Maximum number of rolls to return

        Returns:
            List[Dict[str, Any]]: List of recent rolls
        """
        if limit:
            return self.roll_history[-limit:]
        return self.roll_history.copy()

    def _add_to_history(self, roll_result: Dict[str, Any]):
        """Add a roll result to the history."""
        # Add timestamp
        import datetime

        roll_result["timestamp"] = datetime.datetime.now().isoformat()

        # Add to history
        self.roll_history.append(roll_result)

        # Limit history size
        if len(self.roll_history) > self.max_history:
            self.roll_history = self.roll_history[-self.max_history :]

    @kernel_function(
        description="Calculate spell slots for a character based on class and level.",
        name="calculate_spell_slots",
    )
    def calculate_spell_slots(self, character_class: str, level: int) -> Dict[str, Any]:
        """
        Calculate spell slots for a character based on class and level.

        Args:
            character_class: The character's class
            level: The character's level

        Returns:
            Dict[str, Any]: Spell slot information by level
        """
        try:
            caster_type = self.class_caster_types.get(character_class.lower())
            
            if not caster_type:
                # Non-spellcasting class
                return {
                    "caster_type": "non_caster",
                    "spell_slots": [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "total_slots": 0,
                }

            spell_slots = self.spell_slot_tables[caster_type].get(level, [0, 0, 0, 0, 0, 0, 0, 0, 0])
            
            return {
                "caster_type": caster_type,
                "level": level,
                "spell_slots": spell_slots,
                "total_slots": sum(spell_slots),
                "spell_slots_by_level": {
                    f"level_{i+1}": slots for i, slots in enumerate(spell_slots)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating spell slots: {str(e)}")
            return {"error": f"Error calculating spell slots: {str(e)}"}

    def manage_spell_slots(self, character_data: Dict[str, Any], action: str, spell_level: int = None, slot_count: int = 1) -> Dict[str, Any]:
        """
        Manage spell slot usage and recovery for a character.

        Args:
            character_data: Character data including current spell slots
            action: Action to perform ('use', 'recover', 'long_rest', 'short_rest')
            spell_level: Spell level (1-9) for 'use' and 'recover' actions
            slot_count: Number of slots to use/recover

        Returns:
            Dict[str, Any]: Result of the spell slot management
        """
        try:
            character_class = character_data.get("character_class") or character_data.get("class", "")
            level = character_data.get("level", 1)
            current_spell_slots = character_data.get("spell_slots", {})

            # Calculate maximum spell slots for this character
            max_slots_info = self.calculate_spell_slots(character_class, level)
            if "error" in max_slots_info:
                return max_slots_info

            max_spell_slots = max_slots_info["spell_slots"]

            # Initialize current spell slots if not present
            if not current_spell_slots:
                current_spell_slots = {
                    f"level_{i+1}_current": max_spell_slots[i]
                    for i in range(9)
                }
                current_spell_slots.update({
                    f"level_{i+1}_max": max_spell_slots[i]
                    for i in range(9)
                })

            result = {
                "success": False,
                "message": "",
                "spell_slots": current_spell_slots,
                "action_performed": action,
                "slots_affected": {}
            }

            if action == "use":
                if spell_level is None or spell_level < 1 or spell_level > 9:
                    return {
                        "success": False,
                        "message": "Invalid spell level. Must be between 1 and 9.",
                        "spell_slots": current_spell_slots,
                        "action_performed": action
                    }

                current_key = f"level_{spell_level}_current"
                current_slots = current_spell_slots.get(current_key, 0)

                if current_slots < slot_count:
                    return {
                        "success": False,
                        "message": f"Not enough level {spell_level} spell slots. Current: {current_slots}, Requested: {slot_count}",
                        "spell_slots": current_spell_slots,
                        "action_performed": action
                    }

                current_spell_slots[current_key] = current_slots - slot_count
                result["success"] = True
                result["message"] = f"Used {slot_count} level {spell_level} spell slot(s)."
                result["slots_affected"] = {f"level_{spell_level}": -slot_count}

            elif action == "recover":
                if spell_level is None or spell_level < 1 or spell_level > 9:
                    return {
                        "success": False,
                        "message": "Invalid spell level. Must be between 1 and 9.",
                        "spell_slots": current_spell_slots,
                        "action_performed": action
                    }

                current_key = f"level_{spell_level}_current"
                max_key = f"level_{spell_level}_max"
                current_slots = current_spell_slots.get(current_key, 0)
                max_slots = current_spell_slots.get(max_key, max_spell_slots[spell_level - 1])

                slots_to_recover = min(slot_count, max_slots - current_slots)
                if slots_to_recover <= 0:
                    return {
                        "success": False,
                        "message": f"Level {spell_level} spell slots are already at maximum ({max_slots}).",
                        "spell_slots": current_spell_slots,
                        "action_performed": action
                    }

                current_spell_slots[current_key] = current_slots + slots_to_recover
                result["success"] = True
                result["message"] = f"Recovered {slots_to_recover} level {spell_level} spell slot(s)."
                result["slots_affected"] = {f"level_{spell_level}": slots_to_recover}

            elif action == "long_rest":
                # Long rest recovers all spell slots
                slots_recovered = {}
                for i in range(9):
                    current_key = f"level_{i+1}_current"
                    max_key = f"level_{i+1}_max"
                    max_slots = max_spell_slots[i]
                    current_slots = current_spell_slots.get(current_key, 0)
                    
                    if max_slots > 0:
                        slots_recovered_for_level = max_slots - current_slots
                        current_spell_slots[current_key] = max_slots
                        current_spell_slots[max_key] = max_slots
                        if slots_recovered_for_level > 0:
                            slots_recovered[f"level_{i+1}"] = slots_recovered_for_level

                result["success"] = True
                result["message"] = "Long rest completed. All spell slots recovered."
                result["slots_affected"] = slots_recovered

            elif action == "short_rest":
                # Short rest only affects Warlocks (they recover all spell slots)
                caster_type = max_slots_info.get("caster_type")
                if caster_type == "warlock":
                    slots_recovered = {}
                    for i in range(9):
                        current_key = f"level_{i+1}_current"
                        max_key = f"level_{i+1}_max"
                        max_slots = max_spell_slots[i]
                        current_slots = current_spell_slots.get(current_key, 0)
                        
                        if max_slots > 0:
                            slots_recovered_for_level = max_slots - current_slots
                            current_spell_slots[current_key] = max_slots
                            current_spell_slots[max_key] = max_slots
                            if slots_recovered_for_level > 0:
                                slots_recovered[f"level_{i+1}"] = slots_recovered_for_level

                    result["success"] = True
                    result["message"] = "Short rest completed. Warlock spell slots recovered."
                    result["slots_affected"] = slots_recovered
                else:
                    result["success"] = True
                    result["message"] = "Short rest completed. No spell slots recovered (not a Warlock)."
                    result["slots_affected"] = {}

            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}",
                    "spell_slots": current_spell_slots,
                    "action_performed": action
                }

            result["spell_slots"] = current_spell_slots
            return result

        except Exception as e:
            logger.error(f"Error managing spell slots: {str(e)}")
            return {"error": f"Error managing spell slots: {str(e)}"}
