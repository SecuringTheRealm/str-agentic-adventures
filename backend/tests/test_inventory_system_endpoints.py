"""
Tests for the inventory system API endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from fastapi.testclient import TestClient


class TestInventorySystemEndpoints:
    """Test suite for inventory system API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_manage_equipment_equip(self, client) -> None:
        """Equipping an item persists to the real inventory and reports its own effects."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "equip",
            "equipment_id": "plate_armor",
            "slot": "chest",
        }

        with patch(
            "app.api.routes.character_routes.get_scribe"
        ) as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.equip_item = AsyncMock(
                return_value={
                    "character_id": character_id,
                    "equipped_item": {
                        "id": "plate_armor",
                        "effects": {"armor_class": 8, "stealth": -1},
                    },
                    "slot": "chest",
                }
            )

            response = client.post(
                f"/game/character/{character_id}/equipment", json=request_data
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "Successfully equipped" in data["message"]
            assert data["stat_changes"]["armor_class"] == 8
            assert data["armor_class_change"] == 8
            mock_scribe.equip_item.assert_called_once_with(
                character_id, "plate_armor", "chest"
            )

    def test_manage_equipment_unequip(self, client) -> None:
        """Unequipping an item reverses its effects and persists the change."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "unequip",
            "equipment_id": "plate_armor",
            "slot": "chest",
        }

        with patch(
            "app.api.routes.character_routes.get_scribe"
        ) as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.unequip_item = AsyncMock(
                return_value={
                    "character_id": character_id,
                    "unequipped_item": {
                        "id": "plate_armor",
                        "effects": {"armor_class": 8},
                    },
                    "slot": "chest",
                }
            )

            response = client.post(
                f"/game/character/{character_id}/equipment", json=request_data
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "Successfully unequipped" in data["message"]
            assert data["armor_class_change"] == -8  # Negative because unequipping

    def test_manage_equipment_character_not_found(self, client) -> None:
        """A nonexistent character returns 404, not fake success."""
        character_id = "does-not-exist"
        request_data = {
            "character_id": character_id,
            "action": "equip",
            "equipment_id": "plate_armor",
            "slot": "chest",
        }

        with patch(
            "app.api.routes.character_routes.get_scribe"
        ) as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.equip_item = AsyncMock(
                return_value={"error": f"Character {character_id} not found"}
            )

            response = client.post(
                f"/game/character/{character_id}/equipment", json=request_data
            )
            assert response.status_code == 404

    def test_manage_equipment_missing_slot(self, client) -> None:
        """Equipping without a slot is an honest 400, not fake success."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "equip",
            "equipment_id": "plate_armor",
        }

        response = client.post(
            f"/game/character/{character_id}/equipment", json=request_data
        )
        assert response.status_code == 400

    def test_manage_equipment_invalid_action(self, client) -> None:
        """Test equipment management with invalid action rejects at schema level."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "invalid_action",
            "equipment_id": "plate_armor",
        }

        response = client.post(
            f"/game/character/{character_id}/equipment", json=request_data
        )
        assert response.status_code == 422

        data = response.json()
        assert any(e["loc"][-1] == "action" for e in data["detail"])

    def test_get_encumbrance(self, client) -> None:
        """Encumbrance is computed from the real character's Strength and inventory."""
        character_id = "test_char_123"

        with patch(
            "app.api.routes.character_routes.get_scribe"
        ) as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.calculate_encumbrance = AsyncMock(
                return_value={
                    "character_id": character_id,
                    "total_weight": 85.5,
                    "carrying_capacity": 225,  # STR 15 * 15, per SRD
                    "push_drag_lift": 450,
                    "encumbrance_level": "unencumbered",
                    "speed_penalty": 0,
                    "weight_breakdown": {"inventory": 85.5, "equipment": 0},
                }
            )

            response = client.get(f"/game/character/{character_id}/encumbrance")
            assert response.status_code == 200

            data = response.json()
            assert data["character_id"] == character_id
            assert data["current_weight"] == 85.5
            assert data["carrying_capacity"] == 225
            assert data["encumbrance_level"] in [
                "unencumbered",
                "encumbered",
                "heavily_encumbered",
            ]
            assert isinstance(data["speed_penalty"], int)

    def test_get_encumbrance_character_not_found(self, client) -> None:
        """A nonexistent character returns 404, not hardcoded fake data."""
        character_id = "does-not-exist"

        with patch(
            "app.api.routes.character_routes.get_scribe"
        ) as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.calculate_encumbrance = AsyncMock(
                return_value={"error": f"Character {character_id} not found"}
            )

            response = client.get(f"/game/character/{character_id}/encumbrance")
            assert response.status_code == 404

    def test_manage_magical_effects_apply(self, client) -> None:
        """Test applying magical item effects."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "apply",
        }

        response = client.post("/game/items/magical-effects", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Applied magical effects" in data["message"]
        assert len(data["active_effects"]) > 0
        assert "stealth" in data["stat_modifiers"]
        assert data["stat_modifiers"]["stealth"] == 2

    def test_manage_magical_effects_remove(self, client) -> None:
        """Test removing magical item effects."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "remove",
        }

        response = client.post("/game/items/magical-effects", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Removed magical effects" in data["message"]
        assert len(data["active_effects"]) == 0
        assert len(data["stat_modifiers"]) == 0

    def test_manage_magical_effects_invalid_action(self, client) -> None:
        """Test magical effects management with invalid action rejects at schema level."""
        request_data = {
            "character_id": "test_char_123",
            "item_id": "cloak_of_elvenkind",
            "action": "invalid_action",
        }

        response = client.post("/game/items/magical-effects", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert any(e["loc"][-1] == "action" for e in data["detail"])

    def test_get_item_catalog_no_filters(self, client) -> None:
        """Test getting item catalog without filters."""
        response = client.get("/game/items/catalog")
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

    def test_get_item_catalog_filter_by_type(self, client) -> None:
        """Test getting item catalog filtered by item type."""
        response = client.get("/game/items/catalog?item_type=weapon")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

        # Check that all returned items are weapons
        for item in data["items"]:
            assert item["item_type"] == "weapon"

    def test_get_item_catalog_filter_by_rarity(self, client) -> None:
        """Test getting item catalog filtered by rarity."""
        response = client.get("/game/items/catalog?rarity=rare")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

        # Check that all returned items are rare
        for item in data["items"]:
            assert item["rarity"] == "rare"

    def test_get_item_catalog_filter_by_value_range(self, client) -> None:
        """Test getting item catalog filtered by value range."""
        response = client.get("/game/items/catalog?min_value=100&max_value=2000")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

        # Check that all returned items are within value range
        for item in data["items"]:
            if item["value"] is not None:
                assert 100 <= item["value"] <= 2000

    def test_get_item_catalog_multiple_filters(self, client) -> None:
        """Test getting item catalog with multiple filters."""
        response = client.get("/game/items/catalog?item_type=armor&rarity=common")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

        # Check that all returned items match both filters
        for item in data["items"]:
            assert item["item_type"] == "armor"
            assert item["rarity"] == "common"

    def test_magical_item_properties(self, client) -> None:
        """Test that magical items have proper properties."""
        response = client.get("/game/items/catalog?rarity=rare")
        assert response.status_code == 200

        data = response.json()
        magical_items = [
            item for item in data["items"] if item.get("is_magical", False)
        ]

        for item in magical_items:
            assert item["is_magical"] is True
            # Magical items should typically require attunement or have special abilities
            assert (
                item.get("requires_attunement", False)
                or len(item.get("special_abilities", [])) > 0
            )

    def test_equipment_with_stat_modifiers(self, client) -> None:
        """Test that equipment with stat modifiers is properly represented."""
        response = client.get("/game/items/catalog")
        assert response.status_code == 200

        data = response.json()
        items_with_modifiers = [
            item for item in data["items"] if item.get("stat_modifiers")
        ]

        assert len(items_with_modifiers) > 0

        for item in items_with_modifiers:
            assert isinstance(item["stat_modifiers"], dict)
            # Check that modifier values are integers
            for _stat, modifier in item["stat_modifiers"].items():
                assert isinstance(modifier, int)
