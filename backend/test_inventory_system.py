#!/usr/bin/env python3
"""
Test script for the inventory management system.
"""

import asyncio
import sys
import os
import tempfile
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up test database
test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
test_db_file.close()
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_file.name}'

from app.agents.scribe_agent import ScribeAgent


async def test_inventory_system():
    """Test the inventory management system functionality."""
    print("Testing inventory management system...")
    
    # Initialize the scribe agent
    scribe = ScribeAgent()
    
    # Create a test character
    character_data = {
        "name": "Test Adventurer",
        "race": "human",
        "class": "fighter",
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 10,
        },
    }
    
    print("\n1. Creating test character...")
    character = await scribe.create_character(character_data)
    if "error" in character:
        print(f"❌ Failed to create character: {character['error']}")
        return False
    
    character_id = character["id"]
    print(f"✅ Created character: {character_id}")
    
    # Test 1: Get empty inventory
    print("\n2. Testing empty inventory...")
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
    print("\n3. Testing adding items to inventory...")
    
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
    print("\n4. Testing updated inventory...")
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
    print("\n5. Testing equipment system...")
    
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
        print(f"❌ Sword not found in main_hand slot")
        return False
    
    if equipment["main_hand"]["id"] != "sword_001":
        print(f"❌ Wrong item in main_hand slot")
        return False
    
    print("✅ Equipment system working correctly")
    
    # Test 5: Remove items
    print("\n6. Testing item removal...")
    
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
    print("\n7. Testing encumbrance calculation...")
    
    encumbrance_result = await scribe.calculate_encumbrance(character_id)
    if "error" in encumbrance_result:
        print(f"❌ Failed to calculate encumbrance: {encumbrance_result['error']}")
        return False
    
    print("✅ Encumbrance calculation working correctly")
    print(f"   Weight percentage: {encumbrance_result['weight_percentage']:.1f}%")
    print(f"   Encumbrance level: {encumbrance_result['encumbrance_level']}")
    
    # Test 7: Unequip item
    print("\n8. Testing unequipping items...")
    
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
        print(f"❌ Sword not found in inventory after unequipping")
        return False
    
    print("✅ Unequipping working correctly")
    
    print("\n🎉 All inventory management tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_inventory_system())
    
    # Clean up test database
    try:
        os.unlink(test_db_file.name)
    except:
        pass
    
    if not success:
        sys.exit(1)
    
    print("\n✅ Inventory management system is working correctly!")