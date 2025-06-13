"""
Test equipment system functionality.
"""
import pytest
from app.models.game_models import Item, CharacterSheet, EquipmentRequest, Abilities, HitPoints


class TestEquipmentModels:
    """Test equipment-related models."""

    def test_item_with_equipment_type(self):
        """Test Item model with equipment type and stat effects."""
        item = Item(
            name="Magic Sword",
            description="A sword that grants strength",
            equipment_type="weapon",
            stat_effects={"strength": 2, "armor_class": 1}
        )
        
        assert item.name == "Magic Sword"
        assert item.equipment_type == "weapon"
        assert item.stat_effects == {"strength": 2, "armor_class": 1}

    def test_item_without_equipment_type(self):
        """Test Item model without equipment type (regular item)."""
        item = Item(name="Health Potion")
        
        assert item.name == "Health Potion"
        assert item.equipment_type is None
        assert item.stat_effects is None

    def test_character_sheet_with_equipped_items(self):
        """Test CharacterSheet with equipped items."""
        sword = Item(
            name="Magic Sword",
            equipment_type="weapon",
            stat_effects={"strength": 2}
        )
        
        character = CharacterSheet(
            name="Test Hero",
            race="human",
            character_class="fighter",
            abilities=Abilities(),
            hit_points=HitPoints(current=10, maximum=10),
            equipped_items={"main_hand": sword}
        )
        
        assert character.name == "Test Hero"
        assert "main_hand" in character.equipped_items
        assert character.equipped_items["main_hand"].name == "Magic Sword"

    def test_equipment_request_equip(self):
        """Test EquipmentRequest for equipping items."""
        request = EquipmentRequest(
            item_id="sword-123",
            action="equip",
            equipment_slot="main_hand"
        )
        
        assert request.item_id == "sword-123"
        assert request.action == "equip"
        assert request.equipment_slot == "main_hand"

    def test_equipment_request_unequip(self):
        """Test EquipmentRequest for unequipping items."""
        request = EquipmentRequest(
            item_id="armor-456",
            action="unequip"
        )
        
        assert request.item_id == "armor-456"
        assert request.action == "unequip"
        assert request.equipment_slot is None


class TestEquipmentFunctionality:
    """Test equipment system functionality."""

    def test_stat_effects_application(self):
        """Test that stat effects are properly applied to character stats."""
        # This would test the actual functionality when integrated
        # For now, just verify the data structures support the functionality
        
        sword = Item(
            name="Strength Sword",
            equipment_type="weapon",
            stat_effects={"strength": 3, "armor_class": 1}
        )
        
        armor = Item(
            name="Plate Armor",
            equipment_type="armor",
            stat_effects={"armor_class": 5, "dexterity": -1}
        )
        
        # Test that items have proper stat effects
        assert sword.stat_effects["strength"] == 3
        assert sword.stat_effects["armor_class"] == 1
        assert armor.stat_effects["armor_class"] == 5
        assert armor.stat_effects["dexterity"] == -1

    def test_equipment_slot_mapping(self):
        """Test equipment slot mapping functionality."""
        equipped_items = {
            "main_hand": Item(name="Sword", equipment_type="weapon"),
            "armor": Item(name="Plate Mail", equipment_type="armor"),
            "off_hand": Item(name="Shield", equipment_type="shield")
        }
        
        character = CharacterSheet(
            name="Warrior",
            race="human",
            character_class="fighter",
            abilities=Abilities(),
            hit_points=HitPoints(current=20, maximum=20),
            equipped_items=equipped_items
        )
        
        assert len(character.equipped_items) == 3
        assert character.equipped_items["main_hand"].name == "Sword"
        assert character.equipped_items["armor"].name == "Plate Mail"
        assert character.equipped_items["off_hand"].name == "Shield"