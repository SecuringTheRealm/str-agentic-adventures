"""
Integration tests for the equipment system.
"""
import pytest
import asyncio
from app.agents.scribe_agent import ScribeAgent
from app.models.game_models import Item


class TestEquipmentIntegration:
    """Test equipment system integration."""
    
    @pytest.fixture
    async def scribe_agent(self):
        """Create a test ScribeAgent instance."""
        return ScribeAgent()
    
    @pytest.fixture
    async def test_character(self, scribe_agent):
        """Create a test character."""
        character_data = {
            "name": "Test Warrior",
            "race": "human",
            "class": "fighter",
            "strength": 15,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 8,
            "hitPoints": 12
        }
        character = await scribe_agent.create_character(character_data)
        return character

    @pytest.fixture
    async def magic_sword(self, scribe_agent, test_character):
        """Add a magic sword to character inventory."""
        sword = {
            "id": "magic-sword-123",
            "name": "Magic Longsword",
            "description": "A sword that enhances the wielder's strength and protection",
            "equipment_type": "weapon",
            "stat_effects": {
                "strength": 2,
                "armor_class": 1
            }
        }
        await scribe_agent.add_to_inventory(test_character["id"], sword)
        return sword

    @pytest.mark.asyncio
    async def test_equip_item_success(self, scribe_agent, test_character, magic_sword):
        """Test successfully equipping an item."""
        result = await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "equip",
            "main_hand"
        )
        
        assert result["success"] is True
        assert "Equipped Magic Longsword" in result["message"]
        assert "main_hand" in result["equipped_items"]
        assert result["equipped_items"]["main_hand"]["name"] == "Magic Longsword"
        
        # Check stat effects were applied
        assert result["character_stats"]["armor_class"] == 11  # 10 base + 1 from sword
        assert result["character_stats"]["abilities"]["strength"] == 17  # 15 base + 2 from sword

    @pytest.mark.asyncio
    async def test_unequip_item_success(self, scribe_agent, test_character, magic_sword):
        """Test successfully unequipping an item."""
        # First equip the item
        await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "equip",
            "main_hand"
        )
        
        # Then unequip it
        result = await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "unequip"
        )
        
        assert result["success"] is True
        assert "Unequipped Magic Longsword" in result["message"]
        assert len(result["equipped_items"]) == 0
        
        # Check stat effects were removed
        assert result["character_stats"]["armor_class"] == 10  # Back to base 10
        assert result["character_stats"]["abilities"]["strength"] == 15  # Back to base 15

    @pytest.mark.asyncio
    async def test_equip_nonexistent_item(self, scribe_agent, test_character):
        """Test trying to equip an item that doesn't exist."""
        result = await scribe_agent.equip_item(
            test_character["id"],
            "nonexistent-item",
            "equip",
            "main_hand"
        )
        
        assert "error" in result
        assert "not found in inventory" in result["error"]

    @pytest.mark.asyncio
    async def test_equip_item_slot_occupied(self, scribe_agent, test_character, magic_sword):
        """Test trying to equip an item to an occupied slot."""
        # First equip the sword
        await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "equip",
            "main_hand"
        )
        
        # Add another weapon to inventory
        another_sword = {
            "id": "another-sword-456",
            "name": "Iron Sword",
            "equipment_type": "weapon",
            "stat_effects": {"strength": 1}
        }
        await scribe_agent.add_to_inventory(test_character["id"], another_sword)
        
        # Try to equip to the same slot
        result = await scribe_agent.equip_item(
            test_character["id"],
            another_sword["id"],
            "equip",
            "main_hand"
        )
        
        assert "error" in result
        assert "already occupied" in result["error"]

    @pytest.mark.asyncio
    async def test_unequip_not_equipped_item(self, scribe_agent, test_character, magic_sword):
        """Test trying to unequip an item that's not equipped."""
        result = await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "unequip"
        )
        
        assert "error" in result
        assert "not currently equipped" in result["error"]

    @pytest.mark.asyncio
    async def test_auto_detect_equipment_slot(self, scribe_agent, test_character, magic_sword):
        """Test auto-detection of equipment slot based on item type."""
        result = await scribe_agent.equip_item(
            test_character["id"],
            magic_sword["id"],
            "equip"  # No equipment_slot provided
        )
        
        assert result["success"] is True
        assert "weapon" in result["equipped_items"]  # Should auto-detect as weapon type

    @pytest.mark.asyncio
    async def test_equip_non_equipment_item(self, scribe_agent, test_character):
        """Test trying to equip a non-equipment item."""
        # Add a regular item (not equipment)
        potion = {
            "id": "health-potion-789",
            "name": "Health Potion",
            "description": "Restores health"
            # No equipment_type or stat_effects
        }
        await scribe_agent.add_to_inventory(test_character["id"], potion)
        
        result = await scribe_agent.equip_item(
            test_character["id"],
            potion["id"],
            "equip"
        )
        
        assert "error" in result
        assert "not equippable" in result["error"]