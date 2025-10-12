"""
Scribe Agent - Manages character sheets and game data.
"""

import logging
from typing import Any

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from app.database import get_session, init_db
from app.kernel_setup import kernel_manager
from app.models.db_models import NPC, Character, NPCInteraction

logger = logging.getLogger(__name__)


class ScribeAgent:
    """
    Scribe Agent that manages character sheets, inventory, equipment, and game data.
    This agent is responsible for tracking and updating structured game data.
    """

    def __init__(self) -> None:
        """Initialize the Scribe agent with its own kernel instance."""
        self.kernel: Kernel | None = None
        self.chat_service: AzureChatCompletion | None = None
        self._fallback_mode = False

        # Try to get the shared kernel from kernel manager
        try:
            self.kernel = kernel_manager.get_kernel()
            if self.kernel is None:
                self._fallback_mode = True
                logger.warning(
                    "Scribe agent operating in fallback mode - Azure OpenAI not configured"
                )
            else:
                self.chat_service = self.kernel.get_service(type=AzureChatCompletion)
                logger.info("Scribe agent initialized with Semantic Kernel")
        except Exception as e:
            logger.warning(
                f"Failed to initialize Scribe agent with Semantic Kernel: {e}. "
                "Operating in fallback mode."
            )
            self._fallback_mode = True

        init_db()
        self._register_skills()

    @property
    def characters(self) -> dict[str, Any]:
        """Return all characters from the database."""
        with next(get_session()) as db:
            return {c.id: c.data for c in db.query(Character).all()}

    @property
    def npcs(self) -> dict[str, Any]:
        """Return NPCs from the database."""
        with next(get_session()) as db:
            npcs = db.query(NPC).all()
            return {npc.id: npc.data for npc in npcs}

    def create_npc(self, npc_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new NPC with personality generation."""
        import random
        import uuid

        # Generate personality if not provided
        if "personality" not in npc_data:
            traits_pool = [
                "Honest",
                "Deceitful",
                "Brave",
                "Cowardly",
                "Generous",
                "Greedy",
                "Kind",
                "Cruel",
                "Optimistic",
                "Pessimistic",
                "Curious",
                "Secretive",
                "Patient",
                "Impatient",
                "Loyal",
                "Fickle",
                "Calm",
                "Excitable",
            ]

            ideals_pool = [
                "Justice",
                "Freedom",
                "Order",
                "Chaos",
                "Knowledge",
                "Power",
                "Wealth",
                "Family",
                "Honor",
                "Beauty",
                "Nature",
                "Progress",
            ]

            npc_data["personality"] = {
                "traits": random.sample(traits_pool, 2),
                "ideals": random.sample(ideals_pool, 1),
                "bonds": [f"Loyal to {npc_data.get('location', 'their home')}"],
                "flaws": [
                    random.choice(
                        ["Quick to anger", "Overly trusting", "Greedy", "Secretive"]
                    )
                ],
                "mannerisms": [
                    random.choice(
                        [
                            "Speaks softly",
                            "Gestures wildly",
                            "Never makes eye contact",
                            "Constantly fidgets",
                            "Uses elaborate vocabulary",
                        ]
                    )
                ],
            }

        # Set default values
        npc_data.setdefault("id", str(uuid.uuid4()))
        npc_data.setdefault("relationships", {})
        npc_data.setdefault("interaction_history", [])
        npc_data.setdefault("current_mood", "neutral")
        npc_data.setdefault("importance", "minor")

        return npc_data

    def update_npc_relationship(
        self, npc_id: str, character_id: str, change: int
    ) -> dict[str, Any]:
        """Update relationship between NPC and character."""
        with next(get_session()) as db:
            # Get current NPC and relationship data
            npc = db.query(NPC).filter(NPC.id == npc_id).first()
            if not npc:
                raise ValueError(f"NPC {npc_id} not found")

            # Get current relationship level from NPC relationships
            relationships = npc.data.get("relationships", {})
            current_level = relationships.get(character_id, 0)
            new_level = max(-100, min(100, current_level + change))

            # Update the relationship in NPC data
            relationships[character_id] = new_level
            npc.data["relationships"] = relationships

            # Mark as modified and commit
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(npc, "data")
            db.commit()

            return {
                "npc_id": npc_id,
                "character_id": character_id,
                "old_level": current_level,
                "new_level": new_level,
                "change": change,
            }

    def log_npc_interaction(self, interaction_data: dict[str, Any]) -> str:
        """Log an interaction with an NPC."""
        import uuid
        from datetime import datetime

        interaction_id = str(uuid.uuid4())

        # Store interaction in database
        with next(get_session()) as db:
            interaction_record = NPCInteraction(
                id=interaction_id,
                npc_id=interaction_data.get("npc_id"),
                character_id=interaction_data.get("character_id"),
                interaction_type=interaction_data.get(
                    "interaction_type", "conversation"
                ),
                summary=interaction_data.get("summary", ""),
                outcome=interaction_data.get("outcome"),
                relationship_change=interaction_data.get("relationship_change", 0),
                timestamp=interaction_data.get("timestamp") or datetime.utcnow(),
                data=interaction_data,
            )
            db.add(interaction_record)
            db.commit()

        return interaction_id

    def generate_npc_stats(self, npc_id: str, level: int, role: str) -> dict[str, Any]:
        """Generate combat stats for an NPC."""
        import random

        # Base stats by role
        role_templates = {
            "civilian": {"hp_base": 4, "ac_base": 10, "str": 10, "dex": 10, "con": 10},
            "guard": {"hp_base": 8, "ac_base": 16, "str": 13, "dex": 12, "con": 12},
            "soldier": {"hp_base": 10, "ac_base": 18, "str": 15, "dex": 13, "con": 14},
            "spellcaster": {
                "hp_base": 6,
                "ac_base": 12,
                "str": 8,
                "dex": 12,
                "con": 10,
            },
            "rogue": {"hp_base": 8, "ac_base": 14, "str": 11, "dex": 16, "con": 12},
        }

        template = role_templates.get(role, role_templates["civilian"])

        # Generate stats
        hit_points = template["hp_base"] * level + random.randint(0, level)
        abilities = {
            "strength": template["str"] + random.randint(-2, 2),
            "dexterity": template["dex"] + random.randint(-2, 2),
            "constitution": template["con"] + random.randint(-2, 2),
            "intelligence": 10 + random.randint(-2, 2),
            "wisdom": 10 + random.randint(-2, 2),
            "charisma": 10 + random.randint(-2, 2),
        }

        return {
            "npc_id": npc_id,
            "level": level,
            "role": role,
            "hit_points": {"current": hit_points, "maximum": hit_points},
            "armor_class": template["ac_base"] + ((abilities["dexterity"] - 10) // 2),
            "abilities": abilities,
            "proficiency_bonus": 2 + ((level - 1) // 4),
        }

    @property
    def inventory(self) -> dict[str, Any]:
        """Return all inventories from all characters."""
        try:
            with next(get_session()) as db:
                characters = db.query(Character).all()
                return {c.id: c.data.get("inventory", []) for c in characters}
        except Exception as e:
            logger.error(f"Error retrieving inventory data: {str(e)}")
            return {}

    def _register_skills(self) -> None:
        """Register necessary skills for the Scribe agent."""
        # Skip plugin registration if in fallback mode
        if self._fallback_mode or self.kernel is None:
            logger.info("Scribe agent in fallback mode - skipping plugin registration")
            return

        from semantic_kernel.functions import kernel_function

        @kernel_function(
            description="Create a new NPC with generated personality and stats",
            name="create_npc",
        )
        def create_npc_skill(npc_data: str) -> str:
            """Create an NPC from JSON data."""
            import json

            try:
                npc_dict = json.loads(npc_data)
                result = self.create_npc(npc_dict)
                return json.dumps(result)
            except Exception as e:
                return f"Error creating NPC: {str(e)}"

        @kernel_function(
            description="Update relationship level between NPC and character",
            name="update_npc_relationship",
        )
        def update_relationship_skill(
            npc_id: str, character_id: str, change: str
        ) -> str:
            """Update NPC-character relationship."""
            try:
                change_amount = int(change)
                result = self.update_npc_relationship(
                    npc_id, character_id, change_amount
                )
                return json.dumps(result)
            except Exception as e:
                return f"Error updating relationship: {str(e)}"

        @kernel_function(
            description="Log an interaction between character and NPC",
            name="log_npc_interaction",
        )
        def log_interaction_skill(interaction_data: str) -> str:
            """Log NPC interaction."""
            import json

            try:
                interaction_dict = json.loads(interaction_data)
                interaction_id = self.log_npc_interaction(interaction_dict)
                return f"Interaction logged with ID: {interaction_id}"
            except Exception as e:
                return f"Error logging interaction: {str(e)}"

        @kernel_function(
            description="Generate combat stats for an NPC", name="generate_npc_stats"
        )
        def generate_stats_skill(npc_id: str, level: str, role: str) -> str:
            """Generate NPC combat statistics."""
            import json

            try:
                level_int = int(level)
                result = self.generate_npc_stats(npc_id, level_int, role)
                return json.dumps(result)
            except Exception as e:
                return f"Error generating stats: {str(e)}"

        # Register skills with the kernel (if available)
        try:
            if hasattr(self, "kernel") and self.kernel:
                self.kernel.add_function(
                    plugin_name="scribe_npc", function=create_npc_skill
                )
                self.kernel.add_function(
                    plugin_name="scribe_npc", function=update_relationship_skill
                )
                self.kernel.add_function(
                    plugin_name="scribe_npc", function=log_interaction_skill
                )
                self.kernel.add_function(
                    plugin_name="scribe_npc", function=generate_stats_skill
                )
                logger.info("Scribe NPC skills registered successfully")
        except Exception as e:
            logger.warning(f"Could not register Scribe NPC skills: {str(e)}")
            # Continue without skills registration - fallback behavior

    async def create_character(self, character_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new character sheet based on provided data.

        Args:
            character_data: Dictionary containing character creation details

        Returns:
            Dict[str, Any]: The created character sheet
        """
        try:
            import uuid

            from app.srd_data import (
                apply_racial_ability_bonuses,
                get_background_info,
                get_class_features,
                get_class_hit_die,
                get_class_saving_throws,
                get_racial_speed,
                get_racial_traits,
            )

            character_id = character_data.get(
                "id", f"character_{str(uuid.uuid4())[:8]}"
            )

            race = character_data.get("race", "human").lower()
            character_class = character_data.get("class", "fighter").lower()
            background = character_data.get("background", "").lower()
            level = character_data.get("level", 1)

            # Get base abilities from input
            base_abilities = {
                "strength": character_data.get("strength", 10),
                "dexterity": character_data.get("dexterity", 10),
                "constitution": character_data.get("constitution", 10),
                "intelligence": character_data.get("intelligence", 10),
                "wisdom": character_data.get("wisdom", 10),
                "charisma": character_data.get("charisma", 10),
            }

            # Apply racial ability bonuses
            final_abilities = apply_racial_ability_bonuses(base_abilities, race)

            # Get racial speed
            speed = get_racial_speed(race)

            # Get class hit die
            hit_die = get_class_hit_die(character_class)

            # Get class saving throw proficiencies
            saving_throw_proficiencies = get_class_saving_throws(character_class)

            # Calculate initial hit points (class hit die max + CON modifier)
            constitution_modifier = (final_abilities["constitution"] - 10) // 2
            hit_die_max = int(hit_die.split("d")[1])  # Extract max from "1d10" -> 10
            initial_hp = hit_die_max + constitution_modifier

            # Create basic character sheet structure
            character_sheet = {
                "id": character_id,
                "name": character_data.get("name", "Unnamed Adventurer"),
                "race": race,
                "character_class": character_class,
                "background": background if background else None,
                "level": level,
                "experience": character_data.get("experience", 0),
                "abilities": final_abilities,
                "hit_points": {
                    "current": initial_hp,
                    "maximum": initial_hp,
                },
                "armor_class": 10 + ((final_abilities["dexterity"] - 10) // 2),
                "speed": speed,
                "proficiency_bonus": 2,
                "ability_score_improvements_used": 0,
                "hit_dice": hit_die,
                "saving_throw_proficiencies": saving_throw_proficiencies,
                "skills": {},
                "features": [],
                "inventory": [],
                "equipment": {},
                "backstory": character_data.get("backstory", ""),
            }

            # Add background skill proficiencies if background is specified
            if background:
                background_info = get_background_info(background)
                if background_info:
                    # Add background skill proficiencies
                    skill_proficiencies = background_info.get("skill_proficiencies", [])
                    for skill in skill_proficiencies:
                        character_sheet["skills"][skill] = True

                    # Add background feature as a feature
                    feature = background_info.get("feature", {})
                    if feature:
                        character_sheet["features"].append(
                            {
                                "name": feature["name"],
                                "description": feature["description"],
                                "type": "background",
                                "source": "background",
                                "level_gained": 1,
                            }
                        )

            # Add level 1 class features
            level_1_features = get_class_features(character_class, 1)
            for feature in level_1_features:
                character_sheet["features"].append(
                    {
                        "name": feature["name"],
                        "description": feature["description"],
                        "type": feature["type"],
                        "source": "class",
                        "level_gained": 1,
                    }
                )

            # Add racial traits as features
            racial_data = get_racial_traits(race)
            racial_traits = racial_data.get("traits", [])
            for trait in racial_traits:
                character_sheet["features"].append(
                    {
                        "name": trait["name"],
                        "description": trait["description"],
                        "type": "racial",
                        "source": "race",
                        "level_gained": 1,
                    }
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
            return {"error": f"Failed to create character: {str(e)}"}

    async def update_character(
        self, character_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
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
                if key in character and key != "id":  # Don't allow changing the ID
                    character[key] = value

                db_character.data = character
                db.commit()
            return character

        except Exception as e:
            logger.error(f"Error updating character: {str(e)}")
            return {"error": "Failed to update character"}

    async def get_character(self, character_id: str) -> dict[str, Any] | None:
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
        self, character_id: str, item: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Add an item to a character's inventory.

        Args:
            character_id: The ID of the character
            item: Dictionary containing item details

        Returns:
            Dict[str, Any]: The updated inventory
        """
        try:
            import uuid

            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                inventory = character.get("inventory", [])

                # Ensure item has required structure
                if "id" not in item:
                    item["id"] = f"item_{str(uuid.uuid4())[:8]}"

                # Set default values for item properties
                item.setdefault("name", "Unknown Item")
                item.setdefault("type", "misc")
                item.setdefault("weight", 0)
                item.setdefault("value", 0)
                item.setdefault("quantity", 1)
                item.setdefault("rarity", "common")
                item.setdefault("description", "")
                item.setdefault("magical", False)
                item.setdefault("effects", {})

                # Check if item already exists in inventory (stack if possible)
                existing_item = None
                for inv_item in inventory:
                    if (
                        inv_item.get("name") == item["name"]
                        and inv_item.get("type") == item["type"]
                        and not item.get("magical", False)
                    ):  # Don't stack magical items
                        existing_item = inv_item
                        break

                if existing_item:
                    # Stack with existing item
                    existing_item["quantity"] = existing_item.get(
                        "quantity", 1
                    ) + item.get("quantity", 1)
                else:
                    # Add as new item
                    inventory.append(item)

                character["inventory"] = inventory
                db_character.data = character
                db.commit()

            return {"inventory": inventory, "added_item": item}

        except Exception as e:
            logger.error(f"Error adding to inventory: {str(e)}")
            return {"error": "Failed to add item to inventory"}

    async def get_inventory(self, character_id: str) -> dict[str, Any]:
        """
        Get a character's inventory.

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

                # Calculate total weight and count
                total_weight = sum(
                    item.get("weight", 0) * item.get("quantity", 1)
                    for item in inventory
                )
                total_items = sum(item.get("quantity", 1) for item in inventory)

                return {
                    "character_id": character_id,
                    "items": inventory,
                    "total_items": total_items,
                    "total_weight": total_weight,
                }

        except Exception as e:
            logger.error(f"Error getting inventory: {str(e)}")
            return {"error": "Failed to get inventory"}

    async def remove_from_inventory(
        self, character_id: str, item_id: str, quantity: int = 1
    ) -> dict[str, Any]:
        """
        Remove items from a character's inventory.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to remove
            quantity: The quantity to remove (default: 1)

        Returns:
            Dict[str, Any]: The result of the removal operation
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                inventory = character.get("inventory", [])

                # Find the item
                item_index = None
                for i, item in enumerate(inventory):
                    if item.get("id") == item_id:
                        item_index = i
                        break

                if item_index is None:
                    return {"error": f"Item {item_id} not found in inventory"}

                item = inventory[item_index]
                current_quantity = item.get("quantity", 1)

                if quantity >= current_quantity:
                    # Remove the entire item
                    removed_item = inventory.pop(item_index)
                    removed_quantity = current_quantity
                else:
                    # Reduce the quantity
                    item["quantity"] = current_quantity - quantity
                    removed_quantity = quantity
                    removed_item = item.copy()
                    removed_item["quantity"] = removed_quantity

                character["inventory"] = inventory
                db_character.data = character
                db.commit()

                return {
                    "character_id": character_id,
                    "removed_item": removed_item,
                    "removed_quantity": removed_quantity,
                    "inventory": inventory,
                }

        except Exception as e:
            logger.error(f"Error removing from inventory: {str(e)}")
            return {"error": "Failed to remove item from inventory"}

    async def update_inventory_item(
        self, character_id: str, item_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update an item in a character's inventory.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to update
            updates: Dictionary containing fields to update

        Returns:
            Dict[str, Any]: The result of the update operation
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                inventory = character.get("inventory", [])

                # Find and update the item
                item_found = False
                for item in inventory:
                    if item.get("id") == item_id:
                        # Don't allow changing the ID
                        update_data = {k: v for k, v in updates.items() if k != "id"}
                        item.update(update_data)
                        item_found = True
                        break

                if not item_found:
                    return {"error": f"Item {item_id} not found in inventory"}

                character["inventory"] = inventory
                db_character.data = character
                db.commit()

                return {
                    "character_id": character_id,
                    "updated_item": item,
                    "inventory": inventory,
                }

        except Exception as e:
            logger.error(f"Error updating inventory item: {str(e)}")
            return {"error": "Failed to update inventory item"}

    async def equip_item(
        self, character_id: str, item_id: str, slot: str
    ) -> dict[str, Any]:
        """
        Equip an item from inventory to an equipment slot.

        Args:
            character_id: The ID of the character
            item_id: The ID of the item to equip
            slot: The equipment slot (e.g., 'main_hand', 'armor', 'ring1')

        Returns:
            Dict[str, Any]: The result of the equip operation
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

                # Check if item can be equipped in this slot
                item_type = item_to_equip.get("type", "")
                valid_slots = self._get_valid_slots_for_item_type(item_type)

                if slot not in valid_slots:
                    return {
                        "error": f"Item type {item_type} cannot be equipped in slot {slot}"
                    }

                # Unequip current item in slot if any
                previously_equipped = equipment.get(slot)
                if previously_equipped:
                    # Move currently equipped item back to inventory
                    inventory.append(previously_equipped)

                # Equip the new item
                equipment[slot] = item_to_equip

                # Remove item from inventory
                inventory = [item for item in inventory if item.get("id") != item_id]

                character["inventory"] = inventory
                character["equipment"] = equipment
                db_character.data = character
                db.commit()

                return {
                    "character_id": character_id,
                    "equipped_item": item_to_equip,
                    "slot": slot,
                    "previously_equipped": previously_equipped,
                    "equipment": equipment,
                    "inventory": inventory,
                }

        except Exception as e:
            logger.error(f"Error equipping item: {str(e)}")
            return {"error": "Failed to equip item"}

    def _get_valid_slots_for_item_type(self, item_type: str) -> list[str]:
        """Get valid equipment slots for an item type."""
        slot_mapping = {
            "weapon": ["main_hand", "off_hand"],
            "sword": ["main_hand", "off_hand"],
            "dagger": ["main_hand", "off_hand"],
            "bow": ["main_hand"],
            "shield": ["off_hand"],
            "armor": ["armor"],
            "helmet": ["head"],
            "boots": ["feet"],
            "gloves": ["hands"],
            "ring": ["ring1", "ring2"],
            "amulet": ["neck"],
            "cloak": ["back"],
        }
        return slot_mapping.get(item_type.lower(), [])

    async def unequip_item(self, character_id: str, slot: str) -> dict[str, Any]:
        """
        Unequip an item from an equipment slot back to inventory.

        Args:
            character_id: The ID of the character
            slot: The equipment slot to unequip from

        Returns:
            Dict[str, Any]: The result of the unequip operation
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                inventory = character.get("inventory", [])
                equipment = character.get("equipment", {})

                # Check if there's an item in the slot
                item_to_unequip = equipment.get(slot)
                if not item_to_unequip:
                    return {"error": f"No item equipped in slot {slot}"}

                # Move item back to inventory
                inventory.append(item_to_unequip)

                # Remove from equipment
                del equipment[slot]

                character["inventory"] = inventory
                character["equipment"] = equipment
                db_character.data = character
                db.commit()

                return {
                    "character_id": character_id,
                    "unequipped_item": item_to_unequip,
                    "slot": slot,
                    "equipment": equipment,
                    "inventory": inventory,
                }

        except Exception as e:
            logger.error(f"Error unequipping item: {str(e)}")
            return {"error": "Failed to unequip item"}

    async def calculate_encumbrance(self, character_id: str) -> dict[str, Any]:
        """
        Calculate a character's current encumbrance.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: Encumbrance data including weight limits and penalties
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                abilities = character.get("abilities", {})
                strength = abilities.get("strength", 10)

                # Calculate carrying capacity based on Strength
                carrying_capacity = strength * 15  # Standard D&D 5e rule
                push_drag_lift = carrying_capacity * 2

                # Calculate current weight
                inventory = character.get("inventory", [])
                equipment = character.get("equipment", {})

                inventory_weight = sum(
                    item.get("weight", 0) * item.get("quantity", 1)
                    for item in inventory
                )
                equipment_weight = sum(
                    item.get("weight", 0) for item in equipment.values()
                )

                total_weight = inventory_weight + equipment_weight

                # Determine encumbrance level
                encumbrance_level = "unencumbered"
                speed_penalty = 0

                if total_weight > carrying_capacity:
                    encumbrance_level = "heavily_encumbered"
                    speed_penalty = 20  # -20 feet speed
                elif total_weight > carrying_capacity * 2 / 3:
                    encumbrance_level = "encumbered"
                    speed_penalty = 10  # -10 feet speed

                return {
                    "character_id": character_id,
                    "total_weight": total_weight,
                    "carrying_capacity": carrying_capacity,
                    "push_drag_lift": push_drag_lift,
                    "encumbrance_level": encumbrance_level,
                    "speed_penalty": speed_penalty,
                    "weight_breakdown": {
                        "inventory": inventory_weight,
                        "equipment": equipment_weight,
                    },
                }

        except Exception as e:
            logger.error(f"Error calculating encumbrance: {str(e)}")
            return {"error": "Failed to calculate encumbrance"}

    async def apply_item_effects(self, character_id: str) -> dict[str, Any]:
        """
        Calculate the total effects of all equipped items on character stats.

        Args:
            character_id: The ID of the character

        Returns:
            Dict[str, Any]: The total stat modifications from equipped items
        """
        try:
            with next(get_session()) as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}

                character = db_character.data
                equipment = character.get("equipment", {})

                # Initialize stat modifications
                stat_modifiers = {
                    "strength": 0,
                    "dexterity": 0,
                    "constitution": 0,
                    "intelligence": 0,
                    "wisdom": 0,
                    "charisma": 0,
                    "armor_class": 0,
                    "attack_bonus": 0,
                    "damage_bonus": 0,
                    "speed": 0,
                    "hit_points": 0,
                    "saving_throws": {},
                }

                # Apply effects from each equipped item
                for _slot, item in equipment.items():
                    effects = item.get("effects", {})

                    # Apply stat bonuses
                    for stat, bonus in effects.items():
                        if stat in stat_modifiers and isinstance(bonus, int | float):
                            stat_modifiers[stat] += bonus
                        elif stat == "saving_throws" and isinstance(bonus, dict):
                            for save_type, save_bonus in bonus.items():
                                if save_type not in stat_modifiers["saving_throws"]:
                                    stat_modifiers["saving_throws"][save_type] = 0
                                stat_modifiers["saving_throws"][save_type] += save_bonus

                return {
                    "character_id": character_id,
                    "stat_modifiers": stat_modifiers,
                    "equipped_items": list(equipment.keys()),
                }

        except Exception as e:
            logger.error(f"Error applying item effects: {str(e)}")
            return {"error": "Failed to apply item effects"}

    async def level_up_character(
        self,
        character_id: str,
        ability_improvements: dict[str, int] | None = None,
        use_average_hp: bool = True,
    ) -> dict[str, Any]:
        """
        Level up a character if they have enough experience.

        Args:
            character_id: The ID of the character to level up
            ability_improvements: Dictionary of ability score improvements
                (maximum of 2 points total)
            use_average_hp: Whether to use average HP gain or roll for it

        Returns:
            Dict[str, Any]: The level up result
        """
        try:
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            rules_engine = RulesEnginePlugin()

            with get_session() as db:
                db_character = db.get(Character, character_id)
                if not db_character:
                    return {"error": f"Character {character_id} not found"}
                character = db_character.data

            current_experience = character.get("experience", 0)
            current_level = character.get("level", 1)

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

            target_level = calculated_level
            character_class = character.get("character_class", "fighter")

            ability_changes: dict[str, int] = {}
            features_gained: list[str] = []
            hp_gain_details: list[dict[str, Any]] = []
            total_hp_gained = 0
            new_proficiency_bonus = character.get("proficiency_bonus", 2)
            asi_used = character.get("ability_score_improvements_used", 0)
            remaining_improvements = (
                ability_improvements.copy() if ability_improvements else None
            )

            from app.srd_data import get_class_features

            for next_level in range(current_level + 1, target_level + 1):
                constitution = character.get("abilities", {}).get("constitution", 10)
                constitution_modifier = (constitution - 10) // 2

                hp_result = rules_engine.calculate_level_up_hp(
                    character_class, constitution_modifier, use_average_hp
                )
                if hp_result.get("error"):
                    return hp_result

                hp_gain = hp_result["total_hp_gain"]
                total_hp_gained += hp_gain
                hp_gain_details.append({"level": next_level, **hp_result})

                prof_result = rules_engine.calculate_proficiency_bonus(next_level)
                if prof_result.get("error"):
                    return prof_result

                proficiency_bonus = prof_result["proficiency_bonus"]

                asi_info = rules_engine.check_asi_eligibility(next_level, asi_used)
                if asi_info.get("error"):
                    return asi_info

                if (
                    remaining_improvements
                    and next_level in getattr(rules_engine, "asi_levels", [])
                    and asi_info.get("asi_remaining", 0) > 0
                ):
                    total_improvements = sum(remaining_improvements.values())
                    if total_improvements > 2:
                        return {
                            "error": (
                                "Cannot improve ability scores by more than "
                                "2 points total"
                            )
                        }

                    applied_changes: list[str] = []
                    abilities = character.get("abilities", {})
                    for ability, improvement in remaining_improvements.items():
                        if ability in abilities and improvement:
                            current_score = abilities[ability]
                            new_score = min(current_score + improvement, 20)
                            change = new_score - current_score
                            if change:
                                abilities[ability] = new_score
                                ability_changes[ability] = (
                                    ability_changes.get(ability, 0) + change
                                )
                                applied_changes.append(f"{ability.title()} +{change}")

                    if applied_changes:
                        character["abilities"] = abilities
                        features_gained.append(
                            "Ability Score Improvement: " + ", ".join(applied_changes)
                        )
                        asi_used += 1
                        remaining_improvements = None

                level_features = get_class_features(character_class, next_level) or []
                character.setdefault("features", [])
                existing_features = {
                    (feature.get("name"), feature.get("level_gained"))
                    for feature in character["features"]
                }

                for feature in level_features:
                    feature_key = (feature["name"], next_level)
                    if feature_key in existing_features:
                        continue

                    character["features"].append(
                        {
                            "name": feature["name"],
                            "description": feature["description"],
                            "type": feature["type"],
                            "source": "class",
                            "level_gained": next_level,
                        }
                    )
                    features_gained.append(f"Class Feature: {feature['name']}")
                    existing_features.add(feature_key)

                hit_points = character.setdefault(
                    "hitPoints", {"current": 0, "maximum": 0}
                )
                hit_points["maximum"] += hp_gain
                hit_points["current"] = min(
                    hit_points["maximum"], hit_points.get("current", 0) + hp_gain
                )

                previous_proficiency = character.get(
                    "proficiency_bonus", new_proficiency_bonus
                )
                new_proficiency_bonus = proficiency_bonus
                character["proficiency_bonus"] = proficiency_bonus
                if proficiency_bonus > previous_proficiency:
                    features_gained.append(
                        f"Proficiency Bonus increased to +{proficiency_bonus}"
                    )

                character["level"] = next_level

            character["ability_score_improvements_used"] = asi_used

            with get_session() as db:
                db_character = db.get(Character, character_id)
                if db_character:
                    db_character.data = character
                    db.commit()

            hp_calculation: dict[str, Any] = {
                "total_hp_gain": total_hp_gained,
                "per_level": hp_gain_details,
            }
            if hp_gain_details:
                last_calc = hp_gain_details[-1].copy()
                level_specific_gain = last_calc.pop("total_hp_gain", None)
                hp_calculation.update(last_calc)
                if level_specific_gain is not None:
                    last_calc["total_hp_gain"] = level_specific_gain
                hp_calculation["last_level"] = last_calc

            return {
                "success": True,
                "character_id": character_id,
                "old_level": current_level,
                "new_level": target_level,
                "hit_points_gained": total_hp_gained,
                "ability_improvements": ability_changes,
                "new_proficiency_bonus": new_proficiency_bonus,
                "features_gained": features_gained,
                "hp_calculation": hp_calculation,
                "updated_character": character,
            }

        except Exception as e:
            logger.error(f"Error leveling up character: {str(e)}")
            return {"error": f"Failed to level up character: {str(e)}"}

    async def award_experience(
        self, character_id: str, experience_points: int
    ) -> dict[str, Any]:
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
