"""
Scribe Agent - Manages character sheets and game data.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

from app.kernel_setup import kernel_manager

logger = logging.getLogger(__name__)


class ScribeAgent:
    """
    Scribe Agent that manages character sheets, inventory, equipment, and game data.
    This agent is responsible for tracking and updating structured game data.
    """

    def __init__(self):
        """Initialize the Scribe agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self._register_skills()

        # In-memory storage with simple JSON persistence
        self.DATA_FILE = (
            Path(__file__).resolve().parent.parent / "data" / "characters.json"
        )
        self.characters: Dict[str, Any] = {}
        self.npcs: Dict[str, Any] = {}
        self.inventory: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load character data from disk."""
        if self.DATA_FILE.exists():
            try:
                with self.DATA_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.characters = data.get("characters", {})
                    self.npcs = data.get("npcs", {})
                    self.inventory = data.get("inventory", {})
            except Exception as exc:  # pragma: no cover - load failure
                logger.error("Failed to load character data: %s", exc)

    def _save_data(self) -> None:
        """Persist character data to disk."""
        try:
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with self.DATA_FILE.open("w", encoding="utf-8") as f:
                json.dump(
                    {
                        "characters": self.characters,
                        "npcs": self.npcs,
                        "inventory": self.inventory,
                    },
                    f,
                )
        except Exception as exc:  # pragma: no cover - save failure
            logger.error("Failed to save character data: %s", exc)

    def _register_skills(self):
        """Register necessary skills for the Scribe agent."""
        # Will register skills once implemented
        pass

    async def create_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new character sheet based on provided data.

        Args:
            character_data: Dictionary containing character creation details

        Returns:
            Dict[str, Any]: The created character sheet
        """
        try:
            character_id = character_data.get(
                "id", f"character_{len(self.characters) + 1}"
            )

            # Validation does not require rule calculations yet

            # Validate ability scores and clamp between 1 and 20
            abilities = {
                "strength": min(max(int(character_data.get("strength", 10)), 1), 20),
                "dexterity": min(max(int(character_data.get("dexterity", 10)), 1), 20),
                "constitution": min(
                    max(int(character_data.get("constitution", 10)), 1), 20
                ),
                "intelligence": min(
                    max(int(character_data.get("intelligence", 10)), 1), 20
                ),
                "wisdom": min(max(int(character_data.get("wisdom", 10)), 1), 20),
                "charisma": min(max(int(character_data.get("charisma", 10)), 1), 20),
            }

            # Calculate starting hit points using rules engine
            from app.plugins.rules_engine_plugin import RulesEnginePlugin
            rules_engine = RulesEnginePlugin()

            con_mod = (abilities["constitution"] - 10) // 2
            class_name = character_data.get("class", "fighter")
            hp_result = rules_engine.calculate_level_up_hp(
                class_name, con_mod, use_average=True
            )
            starting_hp = hp_result.get("total_hp_gain", 10)

            # Calculate proficiency bonus
            prof_result = rules_engine.calculate_proficiency_bonus(
                int(character_data.get("level", 1))
            )
            proficiency_bonus = prof_result.get("proficiency_bonus", 2)

            character_sheet = {
                "id": character_id,
                "name": character_data.get("name", "Unnamed Adventurer"),
                "race": character_data.get("race", "Human"),
                "class": class_name,
                "level": int(character_data.get("level", 1)),
                "experience": int(character_data.get("experience", 0)),
                "abilities": abilities,
                "hitPoints": {
                    "current": starting_hp,
                    "maximum": starting_hp,
                },
                "proficiency_bonus": proficiency_bonus,
                "ability_score_improvements_used": 0,
                "inventory": [],
            }

            # Set hit dice based on class
            class_hit_dice = {
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
            character_sheet["hit_dice"] = class_hit_dice.get(
                character_sheet["class"].lower(), "1d8"
            )

            # Store character
            self.characters[character_id] = character_sheet
            self._save_data()

            return character_sheet

        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            return {"error": "Failed to create character"}

    async def update_character(
        self, character_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing character sheet.

        Args:
            character_id: The ID of the character to update
            updates: Dictionary containing fields to update

        Returns:
            Dict[str, Any]: The updated character sheet
        """
        try:
            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]



            # Apply updates with basic validation
            for key, value in updates.items():
                if key == "abilities" and isinstance(value, dict):
                    for ability, score in value.items():
                        if ability in character["abilities"]:
                            new_score = int(score)
                            if not 1 <= new_score <= 20:
                                return {"error": f"Invalid score for {ability}"}
                            character["abilities"][ability] = new_score
                elif key in character and key != "id":
                    character[key] = value

            self._save_data()

            return character

        except Exception as e:
            logger.error(f"Error updating character: {str(e)}")
            return {"error": "Failed to update character"}

    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a character sheet by ID.

        Args:
            character_id: The ID of the character to retrieve

        Returns:
            Optional[Dict[str, Any]]: The character sheet if found, None otherwise
        """
        return self.characters.get(character_id)

    async def add_to_inventory(
        self, character_id: str, item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add an item to a character's inventory.

        Args:
            character_id: The ID of the character
            item: Dictionary containing item details

        Returns:
            Dict[str, Any]: The updated inventory
        """
        try:
            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]
            inventory = character.get("inventory", [])
            inventory.append(item)
            character["inventory"] = inventory

            self._save_data()

            return {"inventory": inventory}

        except Exception as e:
            logger.error(f"Error adding to inventory: {str(e)}")
            return {"error": "Failed to add item to inventory"}

    async def level_up_character(
        self,
        character_id: str,
        ability_improvements: Dict[str, int] = None,
        use_average_hp: bool = True,
    ) -> Dict[str, Any]:
        """
        Level up a character if they have enough experience.

        Args:
            character_id: The ID of the character to level up
            ability_improvements: Dictionary of ability score improvements (max 2 points total)
            use_average_hp: Whether to use average HP gain or roll for it

        Returns:
            Dict[str, Any]: The level up result
        """
        try:
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            rules_engine = RulesEnginePlugin()

            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]
            current_experience = character.get("experience", 0)
            current_level = character.get("level", 1)

            # Check if character can level up
            level_info = rules_engine.calculate_level(current_experience)
            if level_info.get("error"):
                return level_info

            calculated_level = level_info["current_level"]
            if calculated_level <= current_level:
                return {
                    "error": "Character does not have enough experience to level up",
                    "current_level": current_level,
                    "calculated_level": calculated_level,
                    "experience": current_experience,
                    "experience_needed": level_info.get("experience_needed", 0),
                }

            new_level = current_level + 1

            # Calculate ability modifier for Constitution (needed for HP calculation)
            constitution = character.get("abilities", {}).get("constitution", 10)
            constitution_modifier = (constitution - 10) // 2

            # Calculate HP gain
            character_class = character.get("class", "fighter")
            hp_result = rules_engine.calculate_level_up_hp(
                character_class, constitution_modifier, use_average_hp
            )
            if hp_result.get("error"):
                return hp_result

            hp_gained = hp_result["total_hp_gain"]

            # Calculate new proficiency bonus
            prof_result = rules_engine.calculate_proficiency_bonus(new_level)
            if prof_result.get("error"):
                return prof_result

            new_proficiency_bonus = prof_result["proficiency_bonus"]

            # Handle ability score improvements
            asi_used = character.get("ability_score_improvements_used", 0)
            asi_info = rules_engine.check_asi_eligibility(new_level, asi_used)

            ability_changes = {}
            features_gained = []

            # Check if this level grants ASI and if improvements were provided
            if (
                new_level in rules_engine.asi_levels
                and asi_info.get("asi_remaining", 0) > 0
            ):
                if ability_improvements:
                    # Validate ability improvements
                    total_improvements = sum(ability_improvements.values())
                    if total_improvements > 2:
                        return {
                            "error": "Cannot improve ability scores by more than 2 points total"
                        }

                    # Apply ability improvements
                    abilities = character.get("abilities", {})
                    for ability, improvement in ability_improvements.items():
                        if ability in abilities:
                            current_score = abilities[ability]
                            new_score = min(
                                current_score + improvement, 20
                            )  # Max ability score is 20
                            abilities[ability] = new_score
                            ability_changes[ability] = new_score - current_score

                    character["abilities"] = abilities
                    character["ability_score_improvements_used"] = asi_used + 1
                    features_gained.append(
                        f"Ability Score Improvement: {', '.join(f'{ability.title()} +{change}' for ability, change in ability_changes.items())}"
                    )
                else:
                    features_gained.append(
                        "Ability Score Improvement Available (not used)"
                    )

            # Update character
            character["level"] = new_level
            character["hitPoints"]["maximum"] += hp_gained
            character["hitPoints"]["current"] += (
                hp_gained  # Assume full heal on level up
            )
            character["proficiency_bonus"] = new_proficiency_bonus

            # Add level-specific features
            if new_level == 5:
                features_gained.append("Proficiency Bonus increased to +3")
            elif new_level == 9:
                features_gained.append("Proficiency Bonus increased to +4")
            elif new_level == 13:
                features_gained.append("Proficiency Bonus increased to +5")
            elif new_level == 17:
                features_gained.append("Proficiency Bonus increased to +6")

            self._save_data()

            return {
                "success": True,
                "character_id": character_id,
                "old_level": current_level,
                "new_level": new_level,
                "hit_points_gained": hp_gained,
                "ability_improvements": ability_changes,
                "new_proficiency_bonus": new_proficiency_bonus,
                "features_gained": features_gained,
                "hp_calculation": hp_result,
                "updated_character": character,
            }

        except Exception as e:
            logger.error(f"Error leveling up character: {str(e)}")
            return {"error": f"Failed to level up character: {str(e)}"}

    async def award_experience(
        self, character_id: str, experience_points: int
    ) -> Dict[str, Any]:
        """
        Award experience points to a character.

        Args:
            character_id: The ID of the character
            experience_points: The amount of experience to award

        Returns:
            Dict[str, Any]: The result of awarding experience
        """
        try:
            if character_id not in self.characters:
                return {"error": f"Character {character_id} not found"}

            character = self.characters[character_id]
            old_experience = character.get("experience", 0)
            new_experience = old_experience + experience_points
            character["experience"] = new_experience

            self._save_data()

            # Check if character can now level up
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            rules_engine = RulesEnginePlugin()
            level_info = rules_engine.calculate_level(new_experience)

            return {
                "character_id": character_id,
                "experience_awarded": experience_points,
                "old_experience": old_experience,
                "new_experience": new_experience,
                "level_info": level_info,
                "can_level_up": level_info.get("can_level_up", False),
            }

        except Exception as e:
            logger.error(f"Error awarding experience: {str(e)}")
            return {"error": f"Failed to award experience: {str(e)}"}


# Singleton instance
scribe = ScribeAgent()
