#!/usr/bin/env python3
"""
Unit tests for the inventory management system functionality.
"""

import asyncio
import sys
import os
import tempfile
from unittest.mock import Mock, patch

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up test database
test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
test_db_file.close()
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_file.name}'

# Mock the kernel manager and Azure OpenAI dependencies
class MockKernelManager:
    def create_kernel(self):
        return Mock()

# Mock the get_session function
class MockSession:
    def __init__(self):
        self.characters = {}

    def get(self, model, id):
        if id in self.characters:
            mock_char = Mock()
            mock_char.data = self.characters[id]
            return mock_char
        return None
    
    def add(self, obj):
        self.characters[obj.id] = obj.data
    
    def commit(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

mock_session = MockSession()

def mock_get_session():
    yield mock_session

# Apply mocks before importing the ScribeAgent
with patch('app.kernel_setup.kernel_manager', MockKernelManager()):
    with patch('app.database.get_session', mock_get_session):
        with patch('app.database.init_db'):
            from app.agents.scribe_agent import ScribeAgent


async def test_inventory_system():
    """Test the inventory management system functionality."""
    print("Testing inventory management system with mocked dependencies...")
    
    # Initialize the scribe agent
    scribe = ScribeAgent()
    
    # Create a test character manually in the mock session
    character_data = {
        "id": "test_character_123",
        "name": "Test Adventurer",
        "race": "human",
        "character_class": "fighter",
        "level": 1,
        "experience": 0,
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 10,
        },
        "hit_points": {"current": 10, "maximum": 10},
        "proficiency_bonus": 2,
        "ability_score_improvements_used": 0,
        "inventory": [],
        "equipment": {},
        "hit_dice": "1d10",
    }
    
    # Add to mock session
    mock_session.characters["test_character_123"] = character_data
    character_id = "test_character_123"
    
    print(f"✅ Set up test character: {character_id}")
    
    # Test 1: Get empty inventory
    print("\n1. Testing empty inventory...")
    inventory_result = await scribe.get_character_inventory(character_id)
    if "error" in inventory_result:
        print(f"❌ Failed to get inventory: {inventory_result['error']}")
        return False
    
    if inventory_result["items"] != []:
        print(f"❌ Expected empty inventory, got: {inventory_result['items']}")
        return False
    
    print("✅ Empty inventory retrieved successfully")
    print(f"   Total weight: {inventory_result['total_weight']}")
    print(f"   Carrying capacity: {inventory_result['carrying_capacity']}")
    print(f"   Encumbrance level: {inventory_result['encumbrance_level']}")
    
    # Test 2: Add items to inventory
    print("\n2. Testing adding items to inventory...")
    
    # Add a sword
    sword = {
        "id": "sword_001",
        "name": "Iron Sword",
        "description": "A sturdy iron sword",
        "quantity": 1,
        "weight": 3.0,
        "value": 15,
        "properties": {
            "damage": "1d8",
            "damage_type": "slashing",
            "weapon_type": "martial",
        }
    }
    
    add_result = await scribe.add_to_inventory(character_id, sword)
    if "error" in add_result:
        print(f"❌ Failed to add sword: {add_result['error']}")
        return False
    
    print("✅ Added sword to inventory")
    
    # Add some potions
    potion = {
        "id": "potion_001",
        "name": "Healing Potion",
        "description": "Restores 2d4+2 hit points",
        "quantity": 3,
        "weight": 0.5,
        "value": 50,
        "properties": {
            "healing": "2d4+2",
            "consumable": True,
        }
    }
    
    add_result = await scribe.add_to_inventory(character_id, potion)
    if "error" in add_result:
        print(f"❌ Failed to add potions: {add_result['error']}")
        return False
    
    print("✅ Added healing potions to inventory")
    
    # Test 3: Check updated inventory
    print("\n3. Testing updated inventory...")
    inventory_result = await scribe.get_character_inventory(character_id)
    if "error" in inventory_result:
        print(f"❌ Failed to get updated inventory: {inventory_result['error']}")
        return False
    
    items = inventory_result["items"]
    if len(items) != 2:
        print(f"❌ Expected 2 items, got: {len(items)}")
        return False
    
    total_weight = inventory_result["total_weight"]
    expected_weight = (3.0 * 1) + (0.5 * 3)  # sword + potions
    if abs(total_weight - expected_weight) > 0.01:
        print(f"❌ Expected weight {expected_weight}, got: {total_weight}")
        return False
    
    print("✅ Inventory updated correctly")
    print(f"   Items: {len(items)}")
    print(f"   Total weight: {total_weight}")
    print(f"   Encumbrance level: {inventory_result['encumbrance_level']}")
    
    # Test 4: Equipment system
    print("\n4. Testing equipment system...")
    
    # Equip the sword
    equip_result = await scribe.equip_item(character_id, "sword_001", "main_hand")
    if "error" in equip_result:
        print(f"❌ Failed to equip sword: {equip_result['error']}")
        return False
    
    print("✅ Equipped sword to main hand")
    
    # Check equipment
    equipment_result = await scribe.get_equipped_items(character_id)
    if "error" in equipment_result:
        print(f"❌ Failed to get equipment: {equipment_result['error']}")
        return False
    
    equipment = equipment_result["equipment"]
    if "main_hand" not in equipment:
        print("❌ Sword not found in main_hand slot")
        return False
    
    if equipment["main_hand"]["id"] != "sword_001":
        print("❌ Wrong item in main_hand slot")
        return False
    
    print("✅ Equipment system working correctly")
    
    # Test 5: Remove items
    print("\n5. Testing item removal...")
    
    # Remove 1 potion
    remove_result = await scribe.remove_from_inventory(character_id, "potion_001", 1)
    if "error" in remove_result:
        print(f"❌ Failed to remove potion: {remove_result['error']}")
        return False
    
    print("✅ Removed 1 potion from inventory")
    
    # Check inventory
    inventory_result = await scribe.get_character_inventory(character_id)
    if "error" in inventory_result:
        print(f"❌ Failed to get inventory after removal: {inventory_result['error']}")
        return False
    
    # Should have 1 item (potions with quantity 2) since sword is equipped
    items = inventory_result["items"]
    if len(items) != 1:
        print(f"❌ Expected 1 item after removal, got: {len(items)}")
        return False
    
    potion_item = items[0]
    if potion_item["id"] != "potion_001" or potion_item["quantity"] != 2:
        print(f"❌ Potion quantity not updated correctly: {potion_item}")
        return False
    
    print("✅ Item removal working correctly")
    
    # Test 6: Encumbrance calculation
    print("\n6. Testing encumbrance calculation...")
    
    encumbrance_result = await scribe.calculate_encumbrance(character_id)
    if "error" in encumbrance_result:
        print(f"❌ Failed to calculate encumbrance: {encumbrance_result['error']}")
        return False
    
    print("✅ Encumbrance calculation working correctly")
    print(f"   Weight percentage: {encumbrance_result['weight_percentage']:.1f}%")
    print(f"   Encumbrance level: {encumbrance_result['encumbrance_level']}")
    
    # Test 7: Unequip item
    print("\n7. Testing unequipping items...")
    
    unequip_result = await scribe.unequip_item(character_id, "main_hand")
    if "error" in unequip_result:
        print(f"❌ Failed to unequip sword: {unequip_result['error']}")
        return False
    
    print("✅ Unequipped sword from main hand")
    
    # Verify sword is back in inventory
    inventory_result = await scribe.get_character_inventory(character_id)
    if "error" in inventory_result:
        print(f"❌ Failed to get inventory after unequipping: {inventory_result['error']}")
        return False
    
    items = inventory_result["items"]
    sword_in_inventory = any(item["id"] == "sword_001" for item in items)
    if not sword_in_inventory:
        print("❌ Sword not found in inventory after unequipping")
        return False
    
    print("✅ Unequipping working correctly")
    
    # Test 8: Test inventory property
    print("\n8. Testing inventory property interface...")
    inventory_functions = scribe.inventory
    if not isinstance(inventory_functions, dict):
        print(f"❌ Inventory property should return a dict, got: {type(inventory_functions)}")
        return False
    
    expected_functions = [
        "get_character_inventory",
        "add_item", 
        "remove_item",
        "update_item_quantity",
        "calculate_encumbrance",
        "get_equipped_items",
        "equip_item",
        "unequip_item",
    ]
    
    for func_name in expected_functions:
        if func_name not in inventory_functions:
            print(f"❌ Missing function in inventory property: {func_name}")
            return False
        if not callable(inventory_functions[func_name]):
            print(f"❌ {func_name} should be callable")
            return False
    
    print("✅ Inventory property interface working correctly")
    
    print("\n🎉 All inventory management tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_inventory_system())
    
    # Clean up test database
    try:
        os.unlink(test_db_file.name)
    except OSError:
        pass
    
    if not success:
        sys.exit(1)
    
    print("\n✅ Inventory management system is working correctly!")