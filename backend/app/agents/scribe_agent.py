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

    async def manage_equipment(
        self, character_id: str, action: str, item_id: str
    ) -> Dict[str, Any]:
        """
        Equip or unequip items for a character.

        Args:
            character_id: The ID of the character
            action: "equip" or "unequip"
            item_id: The ID of the item to equip/unequip

        Returns:
            Dict[str, Any]: Updated character data with equipment changes
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                
                character = db_character.data
                inventory = character.get("inventory", [])
                equipped_items = character.get("equipped_items", {})
                
                # Find item in inventory
                item = next((i for i in inventory if i.get("id") == item_id), None)
                if not item:
                    return {"error": f"Item {item_id} not found in inventory"}
                
                if action == "equip":
                    # Simple equipment logic - store item ID in equipped_items
                    item_type = item.get("properties", {}).get("type", "misc")
                    equipped_items[item_type] = item_id
                    result = {"action": "equipped", "item": item, "slot": item_type}
                elif action == "unequip":
                    # Remove from equipped items
                    for slot, equipped_id in list(equipped_items.items()):
                        if equipped_id == item_id:
                            del equipped_items[slot]
                            break
                    result = {"action": "unequipped", "item": item}
                else:
                    return {"error": f"Invalid action: {action}. Use 'equip' or 'unequip'"}
                
                character["equipped_items"] = equipped_items
                db_character.data = character
                db.commit()
                
                return {
                    "character_id": character_id,
                    "equipped_items": equipped_items,
                    **result
                }

        except Exception as e:
            logger.error(f"Error managing equipment: {str(e)}")
            return {"error": "Failed to manage equipment"}

    async def calculate_encumbrance(self, character_id: str) -> Dict[str, Any]:
        """
        Calculate carrying capacity and current weight for a character.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: Encumbrance information
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                
                character = db_character.data
                inventory = character.get("inventory", [])
                abilities = character.get("abilities", {})
                
                # Calculate current weight from inventory
                current_weight = 0.0
                for item in inventory:
                    weight = item.get("weight", 0.0) or 0.0
                    quantity = item.get("quantity", 1)
                    current_weight += weight * quantity
                
                # Calculate carrying capacity based on Strength (D&D 5e rules)
                strength = abilities.get("strength", 10)
                carrying_capacity = strength * 15  # Basic carrying capacity
                push_drag_lift = carrying_capacity * 2
                
                # Calculate encumbrance levels
                encumbrance_level = "normal"
                if current_weight > carrying_capacity:
                    encumbrance_level = "heavily_encumbered"
                elif current_weight > carrying_capacity * 0.66:
                    encumbrance_level = "encumbered"
                
                return {
                    "character_id": character_id,
                    "current_weight": current_weight,
                    "carrying_capacity": carrying_capacity,
                    "push_drag_lift": push_drag_lift,
                    "encumbrance_level": encumbrance_level,
                    "weight_remaining": max(0, carrying_capacity - current_weight)
                }

        except Exception as e:
            logger.error(f"Error calculating encumbrance: {str(e)}")
            return {"error": "Failed to calculate encumbrance"}

    async def apply_magical_effects(
        self, character_id: str, item_id: str, effects: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply magical item effects to character stats.

        Args:
            character_id: The ID of the character
            item_id: The ID of the magical item
            effects: Dictionary of effects to apply

        Returns:
            Dict[str, Any]: Updated character data with applied effects
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                
                character = db_character.data
                
                # Store magical effects in character data
                magical_effects = character.get("magical_effects", {})
                magical_effects[item_id] = effects
                character["magical_effects"] = magical_effects
                
                # Apply temporary stat modifications
                temp_stats = character.get("temp_stat_modifications", {})
                for stat, value in effects.items():
                    if stat in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                        temp_stats[stat] = temp_stats.get(stat, 0) + value
                    elif stat == "armor_class":
                        temp_stats["armor_class"] = temp_stats.get("armor_class", 0) + value
                
                character["temp_stat_modifications"] = temp_stats
                db_character.data = character
                db.commit()
                
                return {
                    "character_id": character_id,
                    "item_id": item_id,
                    "effects_applied": effects,
                    "magical_effects": magical_effects,
                    "temp_stat_modifications": temp_stats
                }

        except Exception as e:
            logger.error(f"Error applying magical effects: {str(e)}")
            return {"error": "Failed to apply magical effects"}

    async def get_items_catalog(
        self, rarity: Optional[str] = None, item_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get catalog of available items with filtering options.

        Args:
            rarity: Filter by item rarity (common, uncommon, rare, very_rare, legendary)
            item_type: Filter by item type (weapon, armor, tool, etc.)

        Returns:
            Dict[str, Any]: Catalog of available items
        """
        try:
            # Basic item catalog - in a real implementation this would come from a database
            catalog_items = [
                {
                    "id": "sword_longsword",
                    "name": "Longsword",
                    "description": "A versatile martial weapon",
                    "weight": 3.0,
                    "value": 15,
                    "rarity": "common",
                    "properties": {
                        "type": "weapon",
                        "damage": "1d8",
                        "damage_type": "slashing",
                        "versatile": "1d10"
                    }
                },
                {
                    "id": "armor_leather",
                    "name": "Leather Armor",
                    "description": "Light armor made from supple leather",
                    "weight": 10.0,
                    "value": 10,
                    "rarity": "common",
                    "properties": {
                        "type": "armor",
                        "armor_class": 11,
                        "armor_type": "light"
                    }
                },
                {
                    "id": "potion_healing",
                    "name": "Potion of Healing",
                    "description": "A magical red potion that restores health",
                    "weight": 0.5,
                    "value": 50,
                    "rarity": "common",
                    "properties": {
                        "type": "consumable",
                        "healing": "2d4+2",
                        "magical": True
                    }
                },
                {
                    "id": "sword_flame_tongue",
                    "name": "Flame Tongue Sword",
                    "description": "A magical sword wreathed in flames",
                    "weight": 3.0,
                    "value": 5000,
                    "rarity": "rare",
                    "properties": {
                        "type": "weapon",
                        "damage": "1d8",
                        "damage_type": "slashing",
                        "fire_damage": "2d6",
                        "magical": True
                    }
                }
            ]
            
            # Apply filters
            filtered_items = catalog_items
            if rarity:
                filtered_items = [item for item in filtered_items if item.get("rarity") == rarity]
            if item_type:
                filtered_items = [item for item in filtered_items if item.get("properties", {}).get("type") == item_type]
            
            return {
                "items": filtered_items,
                "total_count": len(filtered_items),
                "filters_applied": {
                    "rarity": rarity,
                    "item_type": item_type
                }
            }

        except Exception as e:
            logger.error(f"Error getting items catalog: {str(e)}")
            return {"error": "Failed to get items catalog"}

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
