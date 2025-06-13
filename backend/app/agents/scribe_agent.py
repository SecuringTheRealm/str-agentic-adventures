"""
Scribe Agent - Manages character sheets and game data.
"""

import logging
from typing import Any, Dict, Optional

from app.kernel_setup import kernel_manager
from app.database import get_session, init_db
from app.models.db_models import Character

logger = logging.getLogger(__name__)


class ScribeAgent:
    """
    Scribe Agent that manages character sheets, inventory, equipment, and game data.
    This agent is responsible for tracking and updating structured game data.
    """

    def __init__(self):
        """Initialize the Scribe agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        init_db()
        self._register_skills()

    @property
    def characters(self) -> Dict[str, Any]:
        """Return all characters from the database."""
        with next(get_session()) as db:
            return {c.id: c.data for c in db.query(Character).all()}

    @property
    def npcs(self) -> Dict[str, Any]:
        """Return NPCs placeholder."""
        # TODO: Implement NPC storage and retrieval system
        # TODO: Add NPC personality traits and behavior patterns
        # TODO: Add NPC relationship tracking with player characters
        # TODO: Add NPC conversation history and interaction logs
        # TODO: Add dynamic NPC stat generation and combat capabilities
        return {}

    @property
    def inventory(self) -> Dict[str, Any]:
        """Return inventory placeholder."""
        # TODO: Implement inventory management system
        # TODO: Add item CRUD operations (create, read, update, delete items)
        # TODO: Add equipment slot management (armor, weapons, accessories)
        # TODO: Add item weight and encumbrance calculations
        # TODO: Add magical item properties and effects on character stats
        # TODO: Add item rarity and value tracking
        # TODO: Add equipment effects on ability scores and combat modifiers
        return {}

    def _register_skills(self):
        """Register necessary skills for the Scribe agent."""
        # TODO: Implement Scribe agent skills registration
        # Skills needed: character_sheet_management, inventory_tracking,
        # experience_calculation, ability_score_improvement
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
            import uuid

            character_id = character_data.get(
                "id", f"character_{str(uuid.uuid4())[:8]}"
            )

            # Create basic character sheet structure
            character_sheet = {
                "id": character_id,
                "name": character_data.get("name", "Unnamed Adventurer"),
                "race": character_data.get("race", "Human"),
                "character_class": character_data.get("class", "Fighter"),
                "level": character_data.get("level", 1),
                "experience": character_data.get("experience", 0),
                "abilities": {
                    "strength": character_data.get("strength", 10),
                    "dexterity": character_data.get("dexterity", 10),
                    "constitution": character_data.get("constitution", 10),
                    "intelligence": character_data.get("intelligence", 10),
                    "wisdom": character_data.get("wisdom", 10),
                    "charisma": character_data.get("charisma", 10),
                },
                "hit_points": {
                    "current": character_data.get("hitPoints", 10),
                    "maximum": character_data.get("hitPoints", 10),
                },
                "proficiency_bonus": 2,
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
                character_sheet["character_class"].lower(), "1d8"
            )

            # Store character in database
            with next(get_session()) as db:
                db_character = Character(
                    id=character_id, name=character_sheet["name"], data=character_sheet
                )
                db.add(db_character)
                db.commit()

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
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data

            # Apply updates (simplified for now)
            for key, value in updates.items():
                if key in character and not key == "id":  # Don't allow changing the ID
                    character[key] = value

                db_character.data = character
                db.commit()
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
        with next(get_session()) as db:
            db_character = db.get(Character, character_id)
            return db_character.data if db_character else None

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
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                inventory.append(item)
                character["inventory"] = inventory
                db_character.data = character
                db.commit()

            return {"inventory": inventory}

        except Exception as e:
            logger.error(f"Error adding to inventory: {str(e)}")
            return {"error": "Failed to add item to inventory"}

    async def level_up_character(
        self,
        character_id: str,
        ability_improvements: Dict[str, int] | None = None,
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

            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
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
            character_class = character.get("character_class", "fighter")
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

            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if db_character:
                    db_character.data = character
                    db.commit()

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
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                old_experience = character.get("experience", 0)
                new_experience = old_experience + experience_points
                character["experience"] = new_experience
                db_character.data = character
                db.commit()

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

    async def manage_concentration(
        self, character_id: str, action: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Manage spell concentration for a character.

        Args:
            character_id: The ID of the character
            action: "start", "end", or "check"
            **kwargs: Additional parameters based on action

        Returns:
            Dict[str, Any]: The result of the concentration action
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data

            if action == "start":
                return await self._start_concentration(character, character_id, db_character, db, **kwargs)
            elif action == "end":
                return await self._end_concentration(character, character_id, db_character, db)
            elif action == "check":
                return await self._check_concentration(character, character_id, db_character, db, **kwargs)
            else:
                return {"error": f"Unknown concentration action: {action}"}

        except Exception as e:
            logger.error(f"Error managing concentration: {str(e)}")
            return {"error": f"Failed to manage concentration: {str(e)}"}

    async def _start_concentration(self, character, character_id, db_character, db, **kwargs):
        """Start concentrating on a spell."""
        spell_name = kwargs.get("spell_name")
        spell_level = kwargs.get("spell_level")
        
        if not spell_name:
            return {"error": "Spell name is required to start concentration"}

        # End any existing concentration
        if character.get("concentration"):
            old_spell = character["concentration"]["spell_name"]
            character["concentration"] = None
            db_character.data = character
            db.commit()
            logger.info(f"Ended concentration on {old_spell} to start new concentration")

        # Start new concentration
        concentration_info = {
            "spell_name": spell_name,
            "spell_level": spell_level,
            "duration_remaining": None,  # Can be set based on spell duration
            "save_dc": None
        }
        
        character["concentration"] = concentration_info
        db_character.data = character
        db.commit()

        return {
            "success": True,
            "action_performed": "start",
            "concentration_status": concentration_info,
            "message": f"Started concentrating on {spell_name}"
        }

    async def _end_concentration(self, character, character_id, db_character, db):
        """End concentration on current spell."""
        current_concentration = character.get("concentration")
        
        if not current_concentration:
            return {
                "success": False,
                "action_performed": "end",
                "message": "Character is not currently concentrating on any spell"
            }

        spell_name = current_concentration.get("spell_name", "unknown spell")
        character["concentration"] = None
        db_character.data = character
        db.commit()

        return {
            "success": True,
            "action_performed": "end",
            "concentration_status": None,
            "message": f"Ended concentration on {spell_name}"
        }

    async def _check_concentration(self, character, character_id, db_character, db, **kwargs):
        """Perform a concentration check."""
        current_concentration = character.get("concentration")
        
        if not current_concentration:
            return {
                "success": False,
                "action_performed": "check",
                "message": "Character is not currently concentrating on any spell"
            }

        damage_taken = kwargs.get("damage_taken", 0)
        
        # Calculate concentration save DC (minimum 10, or half damage taken, whichever is higher)
        save_dc = max(10, damage_taken // 2)
        
        # Get character's Constitution modifier for the save
        constitution = character.get("abilities", {}).get("constitution", 10)
        constitution_modifier = (constitution - 10) // 2
        proficiency_bonus = character.get("proficiency_bonus", 2)
        
        # Roll concentration save (d20 + Con modifier + proficiency bonus)
        from app.plugins.rules_engine_plugin import RulesEnginePlugin
        rules_engine = RulesEnginePlugin()
        roll_result = rules_engine.roll_dice("1d20")
        
        if "error" in roll_result:
            return {"error": f"Failed to roll concentration save: {roll_result['error']}"}
        
        total_save = roll_result["total"] + constitution_modifier + proficiency_bonus
        success = total_save >= save_dc
        
        check_result = {
            "dice_roll": roll_result["total"],
            "constitution_modifier": constitution_modifier,
            "proficiency_bonus": proficiency_bonus,
            "total_save": total_save,
            "save_dc": save_dc,
            "success": success,
            "damage_taken": damage_taken
        }

        spell_name = current_concentration.get("spell_name", "unknown spell")
        
        if not success:
            # Concentration is broken
            character["concentration"] = None
            db_character.data = character
            db.commit()
            
            return {
                "success": True,
                "action_performed": "check",
                "concentration_status": None,
                "check_result": check_result,
                "message": f"Concentration check failed! No longer concentrating on {spell_name}."
            }
        else:
            # Concentration maintained
            return {
                "success": True,
                "action_performed": "check",
                "concentration_status": current_concentration,
                "check_result": check_result,
                "message": f"Concentration check succeeded! Still concentrating on {spell_name}."
            }


# Lazy singleton instance
_scribe = None


def get_scribe():
    """Get the scribe instance, creating it if necessary."""
    global _scribe
    if _scribe is None:
        _scribe = ScribeAgent()
    return _scribe


# For backward compatibility during import-time checks
scribe = None
