"""
Rules Engine Plugin - Converted from Semantic Kernel plugin to direct function calls.
This plugin provides D&D 5e SRD ruleset functionality to the agents.
"""

import logging
import random
from datetime import datetime
from typing import Any

# Note: Converted from Semantic Kernel plugin to direct function calls

logger = logging.getLogger(__name__)


# D&D 5e spell slot progression tables by class and level
SPELL_SLOTS_BY_CLASS_LEVEL = {
    "wizard": {
        1: [2],
        2: [3],
        3: [4, 2],
        4: [4, 3],
        5: [4, 3, 2],
        6: [4, 3, 3],
        7: [4, 3, 3, 1],
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
    },
    "sorcerer": {
        1: [2],
        2: [3],
        3: [4, 2],
        4: [4, 3],
        5: [4, 3, 2],
        6: [4, 3, 3],
        7: [4, 3, 3, 1],
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
    },
    "cleric": {
        1: [2],
        2: [3],
        3: [4, 2],
        4: [4, 3],
        5: [4, 3, 2],
        6: [4, 3, 3],
        7: [4, 3, 3, 1],
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
    },
    "druid": {
        1: [2],
        2: [3],
        3: [4, 2],
        4: [4, 3],
        5: [4, 3, 2],
        6: [4, 3, 3],
        7: [4, 3, 3, 1],
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
    },
    "bard": {
        1: [2],
        2: [3],
        3: [4, 2],
        4: [4, 3],
        5: [4, 3, 2],
        6: [4, 3, 3],
        7: [4, 3, 3, 1],
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
    },
    "warlock": {
        1: [1],
        2: [2],
        3: [2],
        4: [2],
        5: [2],
        6: [2],
        7: [2],
        8: [2],
        9: [2],
        10: [2],
        11: [3],
        12: [3],
        13: [3],
        14: [3],
        15: [3],
        16: [3],
        17: [4],
        18: [4],
        19: [4],
        20: [4],
    },
    "paladin": {
        2: [2],
        3: [3],
        4: [3],
        5: [4, 2],
        6: [4, 2],
        7: [4, 3],
        8: [4, 3],
        9: [4, 3, 2],
        10: [4, 3, 2],
        11: [4, 3, 3],
        12: [4, 3, 3],
        13: [4, 3, 3, 1],
        14: [4, 3, 3, 1],
        15: [4, 3, 3, 2],
        16: [4, 3, 3, 2],
        17: [4, 3, 3, 3, 1],
        18: [4, 3, 3, 3, 1],
        19: [4, 3, 3, 3, 2],
        20: [4, 3, 3, 3, 2],
    },
    "ranger": {
        2: [2],
        3: [3],
        4: [3],
        5: [4, 2],
        6: [4, 2],
        7: [4, 3],
        8: [4, 3],
        9: [4, 3, 2],
        10: [4, 3, 2],
        11: [4, 3, 3],
        12: [4, 3, 3],
        13: [4, 3, 3, 1],
        14: [4, 3, 3, 1],
        15: [4, 3, 3, 2],
        16: [4, 3, 3, 2],
        17: [4, 3, 3, 3, 1],
        18: [4, 3, 3, 3, 1],
        19: [4, 3, 3, 3, 2],
        20: [4, 3, 3, 3, 2],
    },
}


class RulesEnginePlugin:
    """
    Plugin that provides D&D 5e SRD rules functionality.
    This plugin handles dice rolling, skill checks, and other game mechanics.
    """

    def __init__(self) -> None:
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

        # Concentration tracking for ongoing spells
        # Maps character_id to spell information for concentration spells
        self.concentration_spells = {}  # {character_id: {"spell": spell_dict, "duration_remaining": int, "started_at": timestamp}}

        # Spell slot tracking by character level and class
        self.spell_slots_by_class_level = SPELL_SLOTS_BY_CLASS_LEVEL

    def _initialize_spell_slots(self):
        """Initialize spell slot progression tables for each spellcasting class."""
        # This method is no longer needed as the data is now a module-level constant
        # Kept for backward compatibility
        return SPELL_SLOTS_BY_CLASS_LEVEL

#     # @kernel_function(
#     #     description="Get spell slots for a character by class and level.",
#     #     name="get_spell_slots_for_level",
#     # )
    def get_spell_slots_for_level(
        self, character_class: str, level: int
    ) -> dict[str, Any]:
        """
        Get the spell slots available for a character at a given level.

        Args:
            character_class: The character's class
            level: The character's level

        Returns:
            Dict[str, Any]: Spell slot information by level
        """
        try:
            class_lower = character_class.lower()
            if class_lower not in self.spell_slots_by_class_level:
                return {"error": f"Class {character_class} is not a spellcasting class"}

            if level not in self.spell_slots_by_class_level[class_lower]:
                return {"error": f"Level {level} not found for class {character_class}"}

            slots = self.spell_slots_by_class_level[class_lower][level]

            # Convert to dictionary format
            spell_slots = {}
            for slot_level, count in enumerate(slots, 1):
                spell_slots[str(slot_level)] = count

            return {
                "character_class": character_class,
                "level": level,
                "spell_slots": spell_slots,
                "total_slots": sum(slots),
            }
        except Exception as e:
            logger.error(f"Error getting spell slots: {str(e)}")
            return {"error": f"Error getting spell slots: {str(e)}"}

#     # @kernel_function(
#         description="Calculate spell attack bonus for a character.",
#         name="calculate_spell_attack_bonus",
#     )
    def calculate_spell_attack_bonus(
        self,
        spellcasting_ability_modifier: int,
        proficiency_bonus: int,
        character_level: int = None,
    ) -> dict[str, Any]:
        """
        Calculate spell attack bonus using D&D 5e rules.

        Formula: proficiency bonus + spellcasting ability modifier

        Args:
            spellcasting_ability_modifier: The modifier for the character's spellcasting ability
            proficiency_bonus: The character's proficiency bonus
            character_level: Optional character level (for information)

        Returns:
            Dict[str, Any]: Spell attack bonus information
        """
        try:
            attack_bonus = proficiency_bonus + spellcasting_ability_modifier

            return {
                "spell_attack_bonus": attack_bonus,
                "spellcasting_modifier": spellcasting_ability_modifier,
                "proficiency_bonus": proficiency_bonus,
                "character_level": character_level,
                "formula": "proficiency_bonus + spellcasting_ability_modifier",
            }
        except Exception as e:
            logger.error(f"Error calculating spell attack bonus: {str(e)}")
            return {"error": f"Error calculating spell attack bonus: {str(e)}"}

#     # @kernel_function(
#         description="Process spell effect resolution.",
#         name="resolve_spell_effect",
#     )
    def resolve_spell_effect(
        self,
        spell_name: str,
        spell_level: int,
        target_count: int = 1,
        slot_level: int = None,
    ) -> dict[str, Any]:
        """
        Resolve the effects of a spell being cast.

        Args:
            spell_name: Name of the spell being cast
            spell_level: Base level of the spell
            target_count: Number of targets
            slot_level: Level of spell slot used (for upcast effects)

        Returns:
            Dict[str, Any]: Spell effect information
        """
        try:
            slot_level = slot_level or spell_level
            upcast_levels = max(0, slot_level - spell_level)

            # Basic spell effect template
            effect = {
                "spell_name": spell_name,
                "spell_level": spell_level,
                "slot_level": slot_level,
                "upcast_levels": upcast_levels,
                "target_count": target_count,
                "effects": [],
                "damage": None,
                "healing": None,
                "duration": None,
                "save_required": False,
                "attack_required": False,
            }

            # Add basic effect processing - this would be expanded with actual spell data
            if upcast_levels > 0:
                effect["effects"].append(
                    f"Spell cast at {slot_level} level (+{upcast_levels} levels)"
                )

            return effect
        except Exception as e:
            logger.error(f"Error resolving spell effect: {str(e)}")
            return {"error": f"Error resolving spell effect: {str(e)}"}

#     # @kernel_function(
#         description="Calculate spell save DC for a character.",
#         name="calculate_spell_save_dc",
#     )
    def calculate_spell_save_dc(
        self,
        spellcasting_ability_modifier: int,
        proficiency_bonus: int,
        character_level: int = None,
    ) -> dict[str, Any]:
        """
        Calculate spell save DC using D&D 5e rules.

        Formula: 8 + proficiency bonus + spellcasting ability modifier

        Args:
            spellcasting_ability_modifier: The modifier for the character's spellcasting ability
            proficiency_bonus: The character's proficiency bonus
            character_level: Optional character level (for information)

        Returns:
            Dict[str, Any]: Spell save DC information
        """
        try:
            save_dc = 8 + proficiency_bonus + spellcasting_ability_modifier

            return {
                "save_dc": save_dc,
                "spellcasting_modifier": spellcasting_ability_modifier,
                "proficiency_bonus": proficiency_bonus,
                "character_level": character_level,
                "formula": "8 + proficiency_bonus + spellcasting_ability_modifier",
            }
        except Exception as e:
            logger.error(f"Error calculating spell save DC: {str(e)}")
            return {"error": f"Error calculating spell save DC: {str(e)}"}

#     # @kernel_function(
#         description="Resolve spell damage effects.",
#         name="resolve_spell_damage",
#     )
    def resolve_spell_damage(
        self, dice_notation: str, damage_type: str, target_count: int = 1
    ) -> dict[str, Any]:
        """
        Resolve spell damage using dice rolls.

        Args:
            dice_notation: Damage dice notation (e.g., "3d6", "1d4+3")
            damage_type: Type of damage (e.g., "fire", "force", "cold")
            target_count: Number of targets (for information)

        Returns:
            Dict[str, Any]: Damage resolution results
        """
        try:
            # Use existing dice rolling system
            roll_result = self.roll_dice(dice_notation)

            if "error" in roll_result:
                return roll_result

            return {
                "total_damage": roll_result["total"],
                "damage_type": damage_type,
                "dice_notation": dice_notation,
                "dice_rolls": roll_result.get("rolls", []),
                "modifier": roll_result.get("modifier", 0),
                "target_count": target_count,
                "roll_details": roll_result,
            }
        except Exception as e:
            logger.error(f"Error resolving spell damage: {str(e)}")
            return {"error": f"Error resolving spell damage: {str(e)}"}

#     # @kernel_function(
#         description="Resolve spell healing effects.",
#         name="resolve_spell_healing",
#     )
    def resolve_spell_healing(
        self, dice_notation: str, spellcasting_modifier: int = None
    ) -> dict[str, Any]:
        """
        Resolve spell healing using dice rolls.

        Args:
            dice_notation: Healing dice notation (e.g., "1d8+3", "2d4+2")
            spellcasting_modifier: Optional additional modifier (if not in dice notation)

        Returns:
            Dict[str, Any]: Healing resolution results
        """
        try:
            # Use existing dice rolling system
            roll_result = self.roll_dice(dice_notation)

            if "error" in roll_result:
                return roll_result

            healing_amount = roll_result["total"]

            # Add additional modifier if provided and not already in dice notation
            if (
                spellcasting_modifier is not None
                and roll_result.get("modifier", 0) == 0
            ):
                healing_amount += spellcasting_modifier

            return {
                "healing_amount": healing_amount,
                "dice_notation": dice_notation,
                "dice_rolls": roll_result.get("rolls", []),
                "base_modifier": roll_result.get("modifier", 0),
                "spellcasting_modifier": spellcasting_modifier,
                "roll_details": roll_result,
            }
        except Exception as e:
            logger.error(f"Error resolving spell healing: {str(e)}")
            return {"error": f"Error resolving spell healing: {str(e)}"}

#     # @kernel_function(
#         description="Resolve saving throw against spell effects.",
#         name="resolve_saving_throw",
#     )
    def resolve_saving_throw(
        self,
        save_dc: int,
        ability_modifier: int,
        proficiency_bonus: int = 0,
        is_proficient: bool = False,
        roll_result: int = None,
    ) -> dict[str, Any]:
        """
        Resolve a saving throw against a spell effect.

        Args:
            save_dc: The DC to beat
            ability_modifier: The relevant ability modifier
            proficiency_bonus: Character's proficiency bonus
            is_proficient: Whether the character is proficient in this save
            roll_result: Optional manual roll result (if not provided, will roll d20)

        Returns:
            Dict[str, Any]: Saving throw results
        """
        try:
            # Roll d20 if no manual result provided
            if roll_result is None:
                roll_data = self.roll_dice("1d20")
                if "error" in roll_data:
                    return roll_data
                roll_result = roll_data["total"]

            # Calculate total roll
            total_roll = roll_result + ability_modifier
            if is_proficient:
                total_roll += proficiency_bonus

            save_successful = total_roll >= save_dc

            return {
                "save_successful": save_successful,
                "total_roll": total_roll,
                "d20_roll": roll_result,
                "ability_modifier": ability_modifier,
                "proficiency_bonus": proficiency_bonus if is_proficient else 0,
                "is_proficient": is_proficient,
                "save_dc": save_dc,
                "margin": total_roll - save_dc,
            }
        except Exception as e:
            logger.error(f"Error resolving saving throw: {str(e)}")
            return {"error": f"Error resolving saving throw: {str(e)}"}

#     # @kernel_function(
#         description="Roll dice using standard D&D notation with advanced features (e.g., '1d20', '2d6+3', '4d6dl1', '2d20kh1').",
#         name="roll_dice",
#     )
    def roll_dice(self, dice_notation: str) -> dict[str, Any]:
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

    def _parse_and_roll_dice(self, dice_notation: str) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]  # noqa: S311

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
                    new_roll = random.randint(1, dice_type)  # noqa: S311
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

    def _extract_advanced_modifiers(self, dice_notation: str) -> dict[str, Any]:
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

#     # @kernel_function(
#         description="Perform a skill check against a target difficulty class (DC).",
#         name="skill_check",
#     )
    def skill_check(
        self,
        ability_score: int,
        proficient: bool = False,
        proficiency_bonus: int = 2,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> dict[str, Any]:
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
                roll1 = random.randint(1, 20)  # noqa: S311
                roll2 = random.randint(1, 20)  # noqa: S311
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)  # noqa: S311
                roll2 = random.randint(1, 20)  # noqa: S311
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)  # noqa: S311
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

#     # @kernel_function(
#         description="Calculate whether an attack hits based on the attack roll and target's armor class.",
#         name="resolve_attack",
#     )
    def resolve_attack(
        self,
        attack_bonus: int,
        target_ac: int,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> dict[str, Any]:
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
                roll1 = random.randint(1, 20)  # noqa: S311
                roll2 = random.randint(1, 20)  # noqa: S311
                roll = max(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "advantage"
            elif disadvantage and not advantage:
                # Roll with disadvantage (take the lower of two d20 rolls)
                roll1 = random.randint(1, 20)  # noqa: S311
                roll2 = random.randint(1, 20)  # noqa: S311
                roll = min(roll1, roll2)
                rolls = [roll1, roll2]
                advantage_type = "disadvantage"
            else:
                # Normal roll
                roll = random.randint(1, 20)  # noqa: S311
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

#     # @kernel_function(
#         description="Calculate damage for an attack based on the damage dice and modifiers.",
#         name="calculate_damage",
#     )
    def calculate_damage(
        self, damage_dice: str, is_critical: bool = False
    ) -> dict[str, Any]:
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
                        random.randint(1, dice_type)  # noqa: S311
                        for _ in range(num_dice)
                    ]
                    damage_roll["critical_rolls"] = extra_rolls
                    damage_roll["total"] += sum(extra_rolls)

            return damage_roll
        except Exception as e:
            logger.error(f"Error calculating damage: {str(e)}")
            return {"error": f"Error calculating damage: {str(e)}"}

#     # @kernel_function(
#         description="Calculate the level for a character based on their experience points.",
#         name="calculate_level",
#     )
    def calculate_level(self, experience: int) -> dict[str, Any]:
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

#     # @kernel_function(
#         description="Calculate proficiency bonus for a given level.",
#         name="calculate_proficiency_bonus",
#     )
    def calculate_proficiency_bonus(self, level: int) -> dict[str, Any]:
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

#     # @kernel_function(
#         description="Check if a character can gain ability score improvement at their level.",
#         name="check_asi_eligibility",
#     )
    def check_asi_eligibility(self, level: int, asi_used: int) -> dict[str, Any]:
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

#     # @kernel_function(
#         description="Calculate hit points gained on level up.",
#         name="calculate_level_up_hp",
#     )
    def calculate_level_up_hp(
        self, character_class: str, constitution_modifier: int, use_average: bool = True
    ) -> dict[str, Any]:
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
        self, dice_notation: str, character: dict[str, Any], skill: str = None
    ) -> dict[str, Any]:
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

    def input_manual_roll(self, dice_notation: str, result: int) -> dict[str, Any]:
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

    def clear_roll_history(self) -> None:
        """Clear the roll history."""
        self.roll_history = []

    def get_roll_history(self, limit: int = None) -> list[dict[str, Any]]:
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

    def _add_to_history(self, roll_result: dict[str, Any]) -> None:
        """Add a roll result to the history."""
        # Add timestamp
        import datetime

        roll_result["timestamp"] = datetime.datetime.now().isoformat()

        # Add to history
        self.roll_history.append(roll_result)

        # Limit history size
        if len(self.roll_history) > self.max_history:
            self.roll_history = self.roll_history[-self.max_history :]

#     # @kernel_function(
#         description="Start concentration on a spell for a character.",
#         name="start_concentration",
#     )
    def start_concentration(
        self, character_id: str, spell_data: dict[str, Any], duration_rounds: int = 10
    ) -> dict[str, Any]:
        """
        Start concentration on a spell for a character.

        Args:
            character_id: The character's unique identifier
            spell_data: Dictionary containing spell information (name, level, etc.)
            duration_rounds: Duration of the spell in combat rounds (default 10 for 1 minute)

        Returns:
            Dict[str, Any]: Result of starting concentration
        """
        try:
            # Check if spell requires concentration
            if not spell_data.get("requires_concentration", False):
                return {
                    "success": False,
                    "error": "Spell does not require concentration",
                    "spell": spell_data.get("name", "Unknown"),
                }

            # End any existing concentration
            if character_id in self.concentration_spells:
                old_spell = self.concentration_spells[character_id]["spell"]
                logger.info(
                    f"Character {character_id} lost concentration on {old_spell.get('name', 'Unknown')}"
                )

            # Start new concentration
            self.concentration_spells[character_id] = {
                "spell": spell_data,
                "duration_remaining": duration_rounds,
                "started_at": datetime.now().isoformat(),
            }

            return {
                "success": True,
                "character_id": character_id,
                "spell": spell_data.get("name", "Unknown"),
                "duration_rounds": duration_rounds,
                "message": f"Concentration started on {spell_data.get('name', 'Unknown')}",
            }

        except Exception as e:
            logger.error(f"Error starting concentration: {str(e)}")
            return {
                "success": False,
                "error": f"Error starting concentration: {str(e)}",
            }

#     # @kernel_function(
#         description="End concentration on a spell for a character.",
#         name="end_concentration",
#     )
    def end_concentration(self, character_id: str) -> dict[str, Any]:
        """
        End concentration on a spell for a character.

        Args:
            character_id: The character's unique identifier

        Returns:
            Dict[str, Any]: Result of ending concentration
        """
        try:
            if character_id not in self.concentration_spells:
                return {
                    "success": False,
                    "error": "Character is not concentrating on any spell",
                    "character_id": character_id,
                }

            spell_data = self.concentration_spells[character_id]["spell"]
            spell_name = spell_data.get("name", "Unknown")

            # Remove concentration
            del self.concentration_spells[character_id]

            return {
                "success": True,
                "character_id": character_id,
                "spell": spell_name,
                "message": f"Concentration ended on {spell_name}",
            }

        except Exception as e:
            logger.error(f"Error ending concentration: {str(e)}")
            return {"success": False, "error": f"Error ending concentration: {str(e)}"}

#     # @kernel_function(
#         description="Check current concentration status for a character.",
#         name="check_concentration",
#     )
    def check_concentration(self, character_id: str) -> dict[str, Any]:
        """
        Check current concentration status for a character.

        Args:
            character_id: The character's unique identifier

        Returns:
            Dict[str, Any]: Current concentration status
        """
        try:
            if character_id not in self.concentration_spells:
                return {
                    "is_concentrating": False,
                    "character_id": character_id,
                    "spell": None,
                    "duration_remaining": 0,
                }

            concentration_data = self.concentration_spells[character_id]

            return {
                "is_concentrating": True,
                "character_id": character_id,
                "spell": concentration_data["spell"],
                "duration_remaining": concentration_data["duration_remaining"],
                "started_at": concentration_data["started_at"],
            }

        except Exception as e:
            logger.error(f"Error checking concentration: {str(e)}")
            return {"error": f"Error checking concentration: {str(e)}"}

#     # @kernel_function(
#         description="Perform a concentration saving throw when character takes damage.",
#         name="concentration_saving_throw",
#     )
    def concentration_saving_throw(
        self, character_id: str, damage_taken: int, constitution_modifier: int = 0
    ) -> dict[str, Any]:
        """
        Perform a concentration saving throw when character takes damage.

        Args:
            character_id: The character's unique identifier
            damage_taken: Amount of damage taken
            constitution_modifier: Character's Constitution modifier

        Returns:
            Dict[str, Any]: Result of the concentration save
        """
        try:
            if character_id not in self.concentration_spells:
                return {
                    "success": False,
                    "error": "Character is not concentrating on any spell",
                    "character_id": character_id,
                }

            # Calculate DC: 10 or half the damage taken, whichever is higher
            dc = max(10, damage_taken // 2)

            # Roll d20 + Constitution modifier
            roll_result = self.roll_dice("1d20")
            if "error" in roll_result:
                return roll_result

            total = roll_result["total"] + constitution_modifier
            success = total >= dc

            concentration_data = self.concentration_spells[character_id]
            spell_name = concentration_data["spell"].get("name", "Unknown")

            result = {
                "character_id": character_id,
                "spell": spell_name,
                "damage_taken": damage_taken,
                "dc": dc,
                "roll": roll_result["total"],
                "constitution_modifier": constitution_modifier,
                "total": total,
                "success": success,
                "concentration_maintained": success,
            }

            if not success:
                # Concentration is lost
                del self.concentration_spells[character_id]
                result["message"] = (
                    f"Concentration lost on {spell_name}! (Rolled {total} vs DC {dc})"
                )
            else:
                result["message"] = (
                    f"Concentration maintained on {spell_name}! (Rolled {total} vs DC {dc})"
                )

            return result

        except Exception as e:
            logger.error(f"Error with concentration saving throw: {str(e)}")
            return {
                "success": False,
                "error": f"Error with concentration saving throw: {str(e)}",
            }

#     # @kernel_function(
#         description="Reduce spell duration for all concentrating characters (call each round).",
#         name="advance_concentration_round",
#     )
    def advance_concentration_round(self) -> dict[str, Any]:
        """
        Reduce spell duration for all concentrating characters by one round.
        Should be called at the end of each combat round.

        Returns:
            Dict[str, Any]: Summary of concentration changes
        """
        try:
            expired_spells = []
            continuing_spells = []

            for character_id, concentration_data in list(
                self.concentration_spells.items()
            ):
                concentration_data["duration_remaining"] -= 1

                if concentration_data["duration_remaining"] <= 0:
                    # Spell duration expired
                    spell_name = concentration_data["spell"].get("name", "Unknown")
                    expired_spells.append(
                        {"character_id": character_id, "spell": spell_name}
                    )
                    del self.concentration_spells[character_id]
                else:
                    # Spell continues
                    continuing_spells.append(
                        {
                            "character_id": character_id,
                            "spell": concentration_data["spell"].get("name", "Unknown"),
                            "duration_remaining": concentration_data[
                                "duration_remaining"
                            ],
                        }
                    )

            return {
                "success": True,
                "expired_spells": expired_spells,
                "continuing_spells": continuing_spells,
                "total_concentrating": len(self.concentration_spells),
            }

        except Exception as e:
            logger.error(f"Error advancing concentration round: {str(e)}")
            return {
                "success": False,
                "error": f"Error advancing concentration round: {str(e)}",
            }
