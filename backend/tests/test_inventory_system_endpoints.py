"""
Tests for the inventory system API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.game_models import ItemType, ItemRarity, EquipmentSlot


class TestInventorySystemEndpoints:
    """Test suite for inventory system API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_manage_equipment_equip(self, client):
        """Test equipping equipment endpoint."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "equip",
            "equipment_id": "plate_armor",
            "slot": "chest"
        }
        
        response = client.post(f"/api/game/character/{character_id}/equipment", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Successfully equipped" in data["message"]
        assert "armor_class" in data["stat_changes"]
        assert data["armor_class_change"] == 8

    def test_manage_equipment_unequip(self, client):
        """Test unequipping equipment endpoint."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "unequip",
            "equipment_id": "plate_armor",
            "slot": "chest"
        }
        
        response = client.post(f"/api/game/character/{character_id}/equipment", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Successfully unequipped" in data["message"]
        assert "armor_class" in data["stat_changes"]
        assert data["armor_class_change"] == -8  # Negative because unequipping

    def test_manage_equipment_invalid_action(self, client):
        """Test equipment management with invalid action."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "invalid_action",
            "equipment_id": "plate_armor"
        }
        
        response = client.post(f"/api/game/character/{character_id}/equipment", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Invalid action" in data["message"]

    def test_get_encumbrance(self, client):
        """Test getting character encumbrance."""
        character_id = "test_char_123"
        
        response = client.get(f"/api/game/character/{character_id}/encumbrance")
        assert response.status_code == 200
        
        data = response.json()
        assert data["character_id"] == character_id
        assert "current_weight" in data
        assert "carrying_capacity" in data
        assert data["encumbrance_level"] in ["unencumbered", "encumbered", "heavily_encumbered"]
        assert "speed_penalty" in data
        assert isinstance(data["speed_penalty"], int)

    def test_manage_magical_effects_apply(self, client):
        """Test applying magical item effects."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "apply"
        }
        
        response = client.post("/api/game/items/magical-effects", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Applied magical effects" in data["message"]
        assert len(data["active_effects"]) > 0
        assert "stealth" in data["stat_modifiers"]
        assert data["stat_modifiers"]["stealth"] == 2

    def test_manage_magical_effects_remove(self, client):
        """Test removing magical item effects."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "remove"
        }
        
        response = client.post("/api/game/items/magical-effects", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Removed magical effects" in data["message"]
        assert len(data["active_effects"]) == 0
        assert len(data["stat_modifiers"]) == 0

    def test_manage_magical_effects_invalid_action(self, client):
        """Test magical effects management with invalid action."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "invalid_action"
        }
        
        response = client.post("/api/game/items/magical-effects", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Invalid action" in data["message"]

    def test_get_item_catalog_no_filters(self, client):
        """Test getting item catalog without filters."""
        response = client.get("/api/game/items/catalog")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total_count" in data
        assert len(data["items"]) == data["total_count"]
        assert data["total_count"] > 0
        
        # Check that all items have required fields
        for item in data["items"]:
            assert "name" in item
            assert "item_type" in item
            assert "rarity" in item

    def test_get_item_catalog_filter_by_type(self, client):
        """Test getting item catalog filtered by item type."""
        response = client.get("/api/game/items/catalog?item_type=weapon")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        
        # Check that all returned items are weapons
        for item in data["items"]:
            assert item["item_type"] == "weapon"

    def test_get_item_catalog_filter_by_rarity(self, client):
        """Test getting item catalog filtered by rarity."""
        response = client.get("/api/game/items/catalog?rarity=rare")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        
        # Check that all returned items are rare
        for item in data["items"]:
            assert item["rarity"] == "rare"

    def test_get_item_catalog_filter_by_value_range(self, client):
        """Test getting item catalog filtered by value range."""
        response = client.get("/api/game/items/catalog?min_value=100&max_value=2000")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        
        # Check that all returned items are within value range
        for item in data["items"]:
            if item["value"] is not None:
                assert 100 <= item["value"] <= 2000

    def test_get_item_catalog_multiple_filters(self, client):
        """Test getting item catalog with multiple filters."""
        response = client.get("/api/game/items/catalog?item_type=armor&rarity=common")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        
        # Check that all returned items match both filters
        for item in data["items"]:
            assert item["item_type"] == "armor"
            assert item["rarity"] == "common"

    def test_magical_item_properties(self, client):
        """Test that magical items have proper properties."""
        response = client.get("/api/game/items/catalog?rarity=rare")
        assert response.status_code == 200
        
        data = response.json()
        magical_items = [item for item in data["items"] if item.get("is_magical", False)]
        
        for item in magical_items:
            assert item["is_magical"] is True
            # Magical items should typically require attunement or have special abilities
            assert item.get("requires_attunement", False) or len(item.get("special_abilities", [])) > 0

    def test_equipment_with_stat_modifiers(self, client):
        """Test that equipment with stat modifiers is properly represented."""
        response = client.get("/api/game/items/catalog")
        assert response.status_code == 200
        
        data = response.json()
        items_with_modifiers = [item for item in data["items"] if item.get("stat_modifiers")]
        
        assert len(items_with_modifiers) > 0
        
        for item in items_with_modifiers:
            assert isinstance(item["stat_modifiers"], dict)
            # Check that modifier values are integers
            for stat, modifier in item["stat_modifiers"].items():
                assert isinstance(modifier, int)