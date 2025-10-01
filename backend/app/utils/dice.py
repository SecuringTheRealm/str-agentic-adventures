"""
Shared dice rolling utilities for D&D 5e mechanics.

This module consolidates dice rolling logic to eliminate duplication
between DungeonMasterAgent and CombatMCAgent.
"""

import random
import re
from typing import Any


class DiceRoller:
    """Utility class for rolling dice using standard D&D notation."""

    @staticmethod
    def roll_d20(
        modifier: int = 0, advantage: bool = False, disadvantage: bool = False
    ) -> dict[str, Any]:
        """
        Roll a d20 with optional advantage/disadvantage and modifier.

        Args:
            modifier: Modifier to add to the roll
            advantage: Roll with advantage (take higher of two rolls)
            disadvantage: Roll with disadvantage (take lower of two rolls)

        Returns:
            Dict containing rolls, modifier, total, and advantage type
        """
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
            "advantage_type": advantage_type,
        }

    @staticmethod
    def roll_dice(notation: str) -> dict[str, Any]:
        """
        Roll dice based on standard notation like '2d6+3' or '1d20-1'.

        Args:
            notation: Dice notation string (e.g., '2d6', '1d20+5', '3d8-2')

        Returns:
            Dict containing notation, rolls, modifier, and total

        Raises:
            ValueError: If notation is invalid
        """
        # Parse dice notation: NdM+X or NdM-X or NdM
        match = re.match(r"(\d+)d(\d+)([+-]\d+)?", notation.lower().strip())
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier_str = match.group(3) or "+0"

        # Parse modifier
        modifier = int(modifier_str)

        # Roll the dice
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        return {
            "notation": notation,
            "rolls": rolls,
            "modifier": modifier,
            "total": max(total, 1),  # Minimum 1 for damage rolls
        }

    @staticmethod
    def roll_damage(dice_notation: str) -> dict[str, Any]:
        """
        Roll damage dice based on notation.

        This is an alias for roll_dice() but ensures minimum 1 damage.

        Args:
            dice_notation: Damage dice notation (e.g., '1d8+3')

        Returns:
            Dict containing notation, rolls, modifier, and total (minimum 1)
        """
        result = DiceRoller.roll_dice(dice_notation)
        # Ensure minimum 1 damage
        result["total"] = max(result["total"], 1)
        return result

    @staticmethod
    def parse_dice_from_text(text: str) -> dict[str, Any] | None:
        """
        Extract and roll dice notation from natural language text.

        Args:
            text: Text containing dice notation (e.g., "roll 2d6+1" or "roll a d20")

        Returns:
            Roll result dict if valid notation found, None otherwise
        """
        # Look for dice notation in text, handling both "2d6" and "d20" patterns
        match = re.search(r"(\d*d\d+(?:[+-]\d+)?)", text.lower())
        if not match:
            return None

        notation = match.group(1)
        # Handle "d20" -> "1d20" conversion
        if notation.startswith("d"):
            notation = "1" + notation

        try:
            return DiceRoller.roll_dice(notation)
        except ValueError:
            return None

    @staticmethod
    def is_critical_hit(roll: int) -> bool:
        """
        Check if a d20 roll is a critical hit (natural 20).

        Args:
            roll: The d20 roll value

        Returns:
            True if roll is 20, False otherwise
        """
        return roll == 20

    @staticmethod
    def is_critical_miss(roll: int) -> bool:
        """
        Check if a d20 roll is a critical miss (natural 1).

        Args:
            roll: The d20 roll value

        Returns:
            True if roll is 1, False otherwise
        """
        return roll == 1
