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
        """Return inventory management functions."""
        return {
            "get_character_inventory": self.get_character_inventory,
            "add_item": self.add_to_inventory,
            "remove_item": self.remove_from_inventory,
            "update_item_quantity": self.update_item_quantity,
            "calculate_encumbrance": self.calculate_encumbrance,
            "get_equipped_items": self.get_equipped_items,
            "equip_item": self.equip_item,
            "unequip_item": self.unequip_item,
        }

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
                "equipment": {},
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

    async def get_character_inventory(self, character_id: str) -> Dict[str, Any]:
        """
        Get a character's complete inventory.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: The character's inventory data
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                
                # Calculate total weight and encumbrance
                total_weight = sum(
                    item.get("weight", 0) * item.get("quantity", 1) 
                    for item in inventory
                )
                
                # Calculate carrying capacity (Strength score * 15)
                strength = character.get("abilities", {}).get("strength", 10)
                carrying_capacity = strength * 15
                
                return {
                    "character_id": character_id,
                    "items": inventory,
                    "total_weight": total_weight,
                    "carrying_capacity": carrying_capacity,
                    "encumbrance_level": self._calculate_encumbrance_level(total_weight, carrying_capacity),
                    "equipped_items": character.get("equipment", {}),
                }

        except Exception as e:
            logger.error(f"Error getting character inventory: {str(e)}")
            return {"error": "Failed to get character inventory"}

    async def remove_from_inventory(
        self, character_id: str, item_id: str, quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Remove an item from a character's inventory.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to remove
            quantity: The quantity to remove (default 1)

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
                
                # Find the item
                item_found = False
                for i, item in enumerate(inventory):
                    if item.get("id") == item_id:
                        current_quantity = item.get("quantity", 1)
                        if current_quantity <= quantity:
                            # Remove the item completely
                            inventory.pop(i)
                        else:
                            # Reduce quantity
                            item["quantity"] = current_quantity - quantity
                        item_found = True
                        break
                
                if not item_found:
                    return {"error": f"Item {item_id} not found in inventory"}
                
                character["inventory"] = inventory
                db_character.data = character
                db.commit()

                return {"inventory": inventory, "message": f"Removed {quantity} of item {item_id}"}

        except Exception as e:
            logger.error(f"Error removing from inventory: {str(e)}")
            return {"error": "Failed to remove item from inventory"}

    async def update_item_quantity(
        self, character_id: str, item_id: str, new_quantity: int
    ) -> Dict[str, Any]:
        """
        Update the quantity of an item in a character's inventory.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to update
            new_quantity: The new quantity

        Returns:
            Dict[str, Any]: The updated inventory
        """
        try:
            if new_quantity < 0:
                return {"error": "Quantity cannot be negative"}
            
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                
                # Find the item
                item_found = False
                for item in inventory:
                    if item.get("id") == item_id:
                        if new_quantity == 0:
                            # Remove the item if quantity is 0
                            inventory.remove(item)
                        else:
                            item["quantity"] = new_quantity
                        item_found = True
                        break
                
                if not item_found:
                    return {"error": f"Item {item_id} not found in inventory"}
                
                character["inventory"] = inventory
                db_character.data = character
                db.commit()

                return {"inventory": inventory, "message": f"Updated quantity of item {item_id} to {new_quantity}"}

        except Exception as e:
            logger.error(f"Error updating item quantity: {str(e)}")
            return {"error": "Failed to update item quantity"}

    async def calculate_encumbrance(self, character_id: str) -> Dict[str, Any]:
        """
        Calculate encumbrance and carrying capacity for a character.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: Encumbrance calculation results
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                
                # Calculate total weight
                total_weight = sum(
                    item.get("weight", 0) * item.get("quantity", 1) 
                    for item in inventory
                )
                
                # Calculate carrying capacity (Strength score * 15)
                strength = character.get("abilities", {}).get("strength", 10)
                carrying_capacity = strength * 15
                
                encumbrance_level = self._calculate_encumbrance_level(total_weight, carrying_capacity)
                
                return {
                    "character_id": character_id,
                    "total_weight": total_weight,
                    "carrying_capacity": carrying_capacity,
                    "encumbrance_level": encumbrance_level,
                    "weight_percentage": (total_weight / carrying_capacity) * 100 if carrying_capacity > 0 else 0,
                }

        except Exception as e:
            logger.error(f"Error calculating encumbrance: {str(e)}")
            return {"error": "Failed to calculate encumbrance"}

    async def get_equipped_items(self, character_id: str) -> Dict[str, Any]:
        """
        Get all equipped items for a character.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: The character's equipped items
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                
                return {
                    "character_id": character_id,
                    "equipment": character.get("equipment", {}),
                }

        except Exception as e:
            logger.error(f"Error getting equipped items: {str(e)}")
            return {"error": "Failed to get equipped items"}

    async def equip_item(
        self, character_id: str, item_id: str, slot: str
    ) -> Dict[str, Any]:
        """
        Equip an item from inventory to a specific slot.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to equip
            slot: The equipment slot (e.g., "main_hand", "armor", "accessory")

        Returns:
            Dict[str, Any]: The updated equipment and inventory
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                equipment = character.get("equipment", {})
                
                # Find the item in inventory
                item_to_equip = None
                for item in inventory:
                    if item.get("id") == item_id:
                        item_to_equip = item
                        break
                
                if not item_to_equip:
                    return {"error": f"Item {item_id} not found in inventory"}
                
                # Check if slot is already occupied
                if slot in equipment:
                    # Unequip current item first
                    current_item = equipment[slot]
                    inventory.append(current_item)
                
                # Equip the new item
                equipment[slot] = item_to_equip
                inventory.remove(item_to_equip)
                
                character["inventory"] = inventory
                character["equipment"] = equipment
                db_character.data = character
                db.commit()

                return {
                    "equipment": equipment,
                    "inventory": inventory,
                    "message": f"Equipped {item_to_equip.get('name', 'item')} to {slot}",
                }

        except Exception as e:
            logger.error(f"Error equipping item: {str(e)}")
            return {"error": "Failed to equip item"}

    async def unequip_item(self, character_id: str, slot: str) -> Dict[str, Any]:
        """
        Unequip an item from a specific slot back to inventory.

        Args:
            character_id: The ID of the character
            slot: The equipment slot to unequip from

        Returns:
            Dict[str, Any]: The updated equipment and inventory
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data
                inventory = character.get("inventory", [])
                equipment = character.get("equipment", {})
                
                if slot not in equipment:
                    return {"error": f"No item equipped in slot {slot}"}
                
                # Move item back to inventory
                unequipped_item = equipment.pop(slot)
                inventory.append(unequipped_item)
                
                character["inventory"] = inventory
                character["equipment"] = equipment
                db_character.data = character
                db.commit()

                return {
                    "equipment": equipment,
                    "inventory": inventory,
                    "message": f"Unequipped {unequipped_item.get('name', 'item')} from {slot}",
                }

        except Exception as e:
            logger.error(f"Error unequipping item: {str(e)}")
            return {"error": "Failed to unequip item"}

    def _calculate_encumbrance_level(self, total_weight: float, carrying_capacity: float) -> str:
        """
        Calculate the encumbrance level based on weight and capacity.

        Args:
            total_weight: Total weight carried
            carrying_capacity: Maximum carrying capacity

        Returns:
            str: Encumbrance level ("light", "medium", "heavy", "over_encumbered")
        """
        if carrying_capacity <= 0:
            return "unknown"
        
        percentage = (total_weight / carrying_capacity) * 100
        
        if percentage <= 33.3:
            return "light"
        elif percentage <= 66.6:
            return "medium"
        elif percentage <= 100:
            return "heavy"
        else:
            return "over_encumbered"

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
