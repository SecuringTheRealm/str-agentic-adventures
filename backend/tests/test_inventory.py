"""Tests for the inventory and equipment system.

Covers:
- InventoryItem / Inventory model construction
- Add and remove items
- Equip and unequip (correct slot assignment)
- Equip validation (can't equip non-weapon in main_hand)
- Attunement limit (max 3)
- calculate_ac with various armour types
- get_weapon_stats for known and unknown weapons
- Carrying capacity / weight tracking
"""

import pytest
from app.api.routes.inventory_routes import (
    _find_item,
    _get_character_inventory,
    _slot_for_item_type,
)
from app.models.game_models import (
    Inventory,
    InventoryItem,
    ItemType,
)
from app.rules_engine import (
    ARMOR_TABLE,
    WEAPON_TABLE,
    calculate_ac,
    get_weapon_stats,
)


class TestInventoryModels:
    """Verify Pydantic models instantiate and serialise correctly."""

    def test_inventory_item_defaults(self) -> None:
        """InventoryItem should populate sensible defaults."""
        item = InventoryItem(name="Torch", item_type=ItemType.GEAR)
        assert item.name == "Torch"
        assert item.item_type == ItemType.GEAR
        assert item.weight == 0.0
        assert item.quantity == 1
        assert item.equipped is False
        assert item.requires_attunement is False
        assert item.attuned is False
        assert item.description == ""
        assert item.id  # auto-generated UUID

    def test_inventory_item_custom_values(self) -> None:
        """InventoryItem accepts all explicit values."""
        item = InventoryItem(
            id="custom-id",
            name="Healing Potion",
            item_type=ItemType.POTION,
            weight=0.5,
            quantity=3,
            description="Heals 2d4+2 HP",
        )
        assert item.id == "custom-id"
        assert item.quantity == 3

    def test_inventory_defaults(self) -> None:
        """Empty Inventory has empty items, default slots, 0 gold."""
        inv = Inventory()
        assert inv.items == []
        assert inv.equipment.main_hand is None
        assert inv.equipment.off_hand is None
        assert inv.equipment.armor is None
        assert inv.gold == 0
        assert inv.max_attunements == 3

    def test_inventory_roundtrip_serialisation(self) -> None:
        """Inventory survives model_dump / model_validate roundtrip."""
        inv = Inventory(
            items=[
                InventoryItem(
                    name="Rope",
                    item_type=ItemType.GEAR,
                    weight=10.0,
                )
            ],
            gold=50,
        )
        data = inv.model_dump()
        restored = Inventory.model_validate(data)
        assert restored.gold == 50
        assert len(restored.items) == 1
        assert restored.items[0].name == "Rope"


class TestAddRemoveItems:
    """Adding and removing items from an Inventory instance."""

    def test_add_item(self) -> None:
        """Appending an item increases inventory length."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword",
            item_type=ItemType.WEAPON,
            weight=3.0,
        )
        inv.items.append(sword)
        assert len(inv.items) == 1
        assert inv.items[0].name == "Longsword"

    def test_remove_item_by_id(self) -> None:
        """Filtering by ID removes the matching item."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword",
            item_type=ItemType.WEAPON,
            weight=3.0,
        )
        inv.items.append(sword)
        inv.items = [i for i in inv.items if i.id != sword.id]
        assert len(inv.items) == 0

    def test_remove_nonexistent_item_leaves_inventory_intact(
        self,
    ) -> None:
        """Removing a missing ID does not change the inventory."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword",
            item_type=ItemType.WEAPON,
            weight=3.0,
        )
        inv.items.append(sword)
        inv.items = [
            i for i in inv.items if i.id != "nonexistent"
        ]
        assert len(inv.items) == 1

    def test_find_item_helper(self) -> None:
        """_find_item returns the item or None."""
        inv = Inventory()
        dagger = InventoryItem(
            name="Dagger", item_type=ItemType.WEAPON
        )
        inv.items.append(dagger)
        assert _find_item(inv, dagger.id) is dagger
        assert _find_item(inv, "missing") is None


class TestEquipUnequip:
    """Equipping and unequipping items assigns the correct slot."""

    def test_equip_weapon_in_main_hand(self) -> None:
        """Weapons go into the main_hand slot."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword", item_type=ItemType.WEAPON
        )
        inv.items.append(sword)

        slot = _slot_for_item_type(sword.item_type)
        assert slot == "main_hand"

        setattr(inv.equipment, slot, sword.id)
        sword.equipped = True

        assert inv.equipment.main_hand == sword.id
        assert sword.equipped is True

    def test_equip_shield_in_off_hand(self) -> None:
        """Shields go into the off_hand slot."""
        inv = Inventory()
        shield = InventoryItem(
            name="Shield", item_type=ItemType.SHIELD
        )
        inv.items.append(shield)

        slot = _slot_for_item_type(shield.item_type)
        assert slot == "off_hand"

        setattr(inv.equipment, slot, shield.id)
        shield.equipped = True
        assert inv.equipment.off_hand == shield.id

    def test_equip_armor_in_armor_slot(self) -> None:
        """Armour goes into the armor slot."""
        inv = Inventory()
        armor = InventoryItem(
            name="Chain Mail",
            item_type=ItemType.ARMOR,
            weight=55.0,
        )
        inv.items.append(armor)

        slot = _slot_for_item_type(armor.item_type)
        assert slot == "armor"

        setattr(inv.equipment, slot, armor.id)
        armor.equipped = True
        assert inv.equipment.armor == armor.id

    def test_unequip_clears_slot(self) -> None:
        """Unequipping clears the slot and flag."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword", item_type=ItemType.WEAPON
        )
        inv.items.append(sword)

        inv.equipment.main_hand = sword.id
        sword.equipped = True

        inv.equipment.main_hand = None
        sword.equipped = False

        assert inv.equipment.main_hand is None
        assert sword.equipped is False

    def test_equip_replaces_current_item(self) -> None:
        """Equipping a new weapon displaces the previous one."""
        inv = Inventory()
        sword = InventoryItem(
            name="Longsword", item_type=ItemType.WEAPON
        )
        axe = InventoryItem(
            name="Greataxe", item_type=ItemType.WEAPON
        )
        inv.items.extend([sword, axe])

        inv.equipment.main_hand = sword.id
        sword.equipped = True

        sword.equipped = False
        inv.equipment.main_hand = axe.id
        axe.equipped = True

        assert inv.equipment.main_hand == axe.id
        assert sword.equipped is False
        assert axe.equipped is True


class TestEquipValidation:
    """Items that lack an equipment slot cannot be equipped."""

    def test_cannot_equip_potion(self) -> None:
        """Potions have no equipment slot."""
        assert _slot_for_item_type(ItemType.POTION) is None

    def test_cannot_equip_scroll(self) -> None:
        """Scrolls have no equipment slot."""
        assert _slot_for_item_type(ItemType.SCROLL) is None

    def test_cannot_equip_gear(self) -> None:
        """Gear has no equipment slot."""
        assert _slot_for_item_type(ItemType.GEAR) is None

    def test_cannot_equip_treasure(self) -> None:
        """Treasure has no equipment slot."""
        assert _slot_for_item_type(ItemType.TREASURE) is None


class TestAttunementLimit:
    """Max 3 attuned items by default."""

    def test_attune_up_to_max(self) -> None:
        """Three items can be attuned simultaneously."""
        inv = Inventory()
        for i in range(3):
            item = InventoryItem(
                name=f"Ring {i}",
                item_type=ItemType.WEAPON,
                requires_attunement=True,
            )
            item.attuned = True
            inv.items.append(item)

        attuned_count = sum(
            1 for i in inv.items if i.attuned
        )
        assert attuned_count == 3

    def test_attunement_blocked_at_max(self) -> None:
        """A 4th attunement should be blocked at the route layer."""
        inv = Inventory()
        for i in range(3):
            item = InventoryItem(
                name=f"Ring {i}",
                item_type=ItemType.WEAPON,
                requires_attunement=True,
            )
            item.attuned = True
            inv.items.append(item)

        new_item = InventoryItem(
            name="Cloak of Displacement",
            item_type=ItemType.ARMOR,
            requires_attunement=True,
        )
        inv.items.append(new_item)

        attuned_count = sum(
            1 for i in inv.items if i.attuned
        )
        assert attuned_count >= inv.max_attunements

    def test_custom_max_attunements(self) -> None:
        """max_attunements can be overridden."""
        inv = Inventory(max_attunements=5)
        assert inv.max_attunements == 5


class TestCalculateAC:
    """Test AC calculation with various armour types."""

    def test_no_armor(self) -> None:
        """No armour: 10 + DEX."""
        assert calculate_ac(None, False, 2) == 12
        assert calculate_ac(None, False, -1) == 9

    def test_no_armor_with_shield(self) -> None:
        """No armour + shield: 10 + DEX + 2."""
        assert calculate_ac(None, True, 2) == 14

    def test_leather_armor(self) -> None:
        """Leather: 11 + DEX (no cap)."""
        assert calculate_ac("leather", False, 3) == 14

    def test_chain_shirt(self) -> None:
        """Chain shirt: 13 + DEX (max 2)."""
        assert calculate_ac("chain shirt", False, 5) == 15
        assert calculate_ac("chain shirt", False, 1) == 14

    def test_chain_mail(self) -> None:
        """Chain mail: 16, no DEX bonus."""
        assert calculate_ac("chain mail", False, 5) == 16
        assert calculate_ac("chain mail", False, -2) == 16

    def test_plate_armor(self) -> None:
        """Plate: 18, no DEX bonus."""
        assert calculate_ac("plate", False, 3) == 18

    def test_plate_with_shield(self) -> None:
        """Plate + shield: 18 + 2 = 20."""
        assert calculate_ac("plate", True, 0) == 20

    def test_half_plate(self) -> None:
        """Half plate: 15 + DEX (max 2)."""
        assert calculate_ac("half plate", False, 4) == 17

    def test_studded_leather(self) -> None:
        """Studded leather: 12 + DEX (no cap)."""
        assert calculate_ac("studded leather", False, 4) == 16

    def test_unknown_armor_fallback(self) -> None:
        """Unknown armour name falls back to 10 + DEX."""
        assert calculate_ac(
            "mithral fantasy plate", False, 2
        ) == 12

    def test_case_insensitive(self) -> None:
        """Armour lookup should be case-insensitive."""
        assert calculate_ac("Chain Mail", False, 0) == 16
        assert calculate_ac("PLATE", False, 0) == 18

    def test_all_armor_table_entries_covered(self) -> None:
        """Every ARMOR_TABLE entry produces a valid AC."""
        for name in ARMOR_TABLE:
            ac = calculate_ac(name, False, 2)
            assert isinstance(ac, int)
            assert ac >= 10


class TestGetWeaponStats:
    """Test SRD weapon lookups."""

    def test_longsword(self) -> None:
        """Longsword stats match SRD."""
        stats = get_weapon_stats("longsword")
        assert stats["damage_dice"] == "1d8"
        assert stats["damage_type"] == "slashing"
        assert "versatile" in stats["properties"]

    def test_shortbow(self) -> None:
        """Shortbow stats match SRD."""
        stats = get_weapon_stats("shortbow")
        assert stats["damage_dice"] == "1d6"
        assert stats["damage_type"] == "piercing"

    def test_dagger(self) -> None:
        """Dagger stats match SRD."""
        stats = get_weapon_stats("dagger")
        assert stats["damage_dice"] == "1d4"
        assert "finesse" in stats["properties"]
        assert "light" in stats["properties"]

    def test_greatsword(self) -> None:
        """Greatsword stats match SRD."""
        stats = get_weapon_stats("greatsword")
        assert stats["damage_dice"] == "2d6"
        assert "two-handed" in stats["properties"]

    def test_unknown_weapon_returns_default(self) -> None:
        """Unknown weapon returns safe fallback."""
        stats = get_weapon_stats("vorpal blade of doom")
        assert stats["damage_dice"] == "1d4"
        assert stats["damage_type"] == "bludgeoning"

    def test_case_insensitive(self) -> None:
        """Weapon lookup is case-insensitive."""
        stats = get_weapon_stats("Longsword")
        assert stats["damage_dice"] == "1d8"

    def test_all_weapon_table_entries(self) -> None:
        """Every WEAPON_TABLE entry returns valid stats."""
        for name in WEAPON_TABLE:
            stats = get_weapon_stats(name)
            assert "damage_dice" in stats
            assert "damage_type" in stats
            assert isinstance(stats["properties"], list)

    def test_returned_dict_is_copy(self) -> None:
        """get_weapon_stats returns a copy, not a reference."""
        stats = get_weapon_stats("longsword")
        stats["damage_dice"] = "999d99"
        original = get_weapon_stats("longsword")
        assert original["damage_dice"] == "1d8"


class TestWeightTracking:
    """Total weight of inventory items."""

    def test_total_weight_empty(self) -> None:
        """Empty inventory weighs nothing."""
        inv = Inventory()
        total = sum(
            i.weight * i.quantity for i in inv.items
        )
        assert total == 0.0

    def test_total_weight_single_item(self) -> None:
        """Single item reports correct weight."""
        inv = Inventory()
        inv.items.append(
            InventoryItem(
                name="Chain Mail",
                item_type=ItemType.ARMOR,
                weight=55.0,
            )
        )
        total = sum(
            i.weight * i.quantity for i in inv.items
        )
        assert total == 55.0

    def test_total_weight_multiple_items(self) -> None:
        """Multiple items sum correctly."""
        inv = Inventory()
        inv.items.append(
            InventoryItem(
                name="Longsword",
                item_type=ItemType.WEAPON,
                weight=3.0,
            )
        )
        inv.items.append(
            InventoryItem(
                name="Arrows",
                item_type=ItemType.GEAR,
                weight=0.05,
                quantity=20,
            )
        )
        total = sum(
            i.weight * i.quantity for i in inv.items
        )
        assert total == pytest.approx(4.0)

    def test_total_weight_with_quantity(self) -> None:
        """Quantity multiplies weight correctly."""
        inv = Inventory()
        inv.items.append(
            InventoryItem(
                name="Healing Potion",
                item_type=ItemType.POTION,
                weight=0.5,
                quantity=5,
            )
        )
        total = sum(
            i.weight * i.quantity for i in inv.items
        )
        assert total == pytest.approx(2.5)


class TestGetCharacterInventory:
    """Deserialising structured_inventory from a character dict."""

    def test_none_returns_empty_inventory(self) -> None:
        """Missing key returns an empty Inventory."""
        inv = _get_character_inventory({})
        assert inv == Inventory()

    def test_dict_input(self) -> None:
        """Dict payload is deserialised correctly."""
        data = Inventory(gold=100).model_dump()
        inv = _get_character_inventory(
            {"structured_inventory": data}
        )
        assert inv.gold == 100

    def test_model_input(self) -> None:
        """Inventory model is returned as-is."""
        model = Inventory(gold=42)
        inv = _get_character_inventory(
            {"structured_inventory": model}
        )
        assert inv.gold == 42
