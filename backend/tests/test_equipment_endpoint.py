"""
Test equipment endpoint functionality with mocked dependencies.
"""
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEquipmentEndpoint:
    """Test equipment endpoint with mocked ScribeAgent."""

    def test_equip_item_success(self):
        """Test successful equipment operation."""
        from app.main import app

        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            # Mock successful equipment operation
            mock_scribe = AsyncMock()
            mock_scribe.equip_item = AsyncMock(
                return_value={
                    "success": True,
                    "message": "Equipped Magic Longsword in main_hand slot",
                    "equipped_items": {
                        "main_hand": {
                            "id": "magic-sword-123",
                            "name": "Magic Longsword",
                            "equipment_type": "weapon",
                            "stat_effects": {"strength": 2, "armor_class": 1}
                        }
                    },
                    "character_stats": {
                        "armor_class": 11,
                        "abilities": {"strength": 17}
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            # Test equipment request
            equipment_request = {
                "item_id": "magic-sword-123",
                "action": "equip",
                "equipment_slot": "main_hand"
            }

            response = client.post(
                "/api/game/character/char_123/equipment",
                json=equipment_request
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert "Equipped Magic Longsword" in result["message"]
            assert "main_hand" in result["equipped_items"]
            assert result["character_stats"]["armor_class"] == 11

            # Verify the mock was called correctly
            mock_scribe.equip_item.assert_called_once_with(
                "char_123",
                "magic-sword-123",
                "equip",
                "main_hand"
            )

    def test_unequip_item_success(self):
        """Test successful unequip operation."""
        from app.main import app

        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = AsyncMock()
            mock_scribe.equip_item = AsyncMock(
                return_value={
                    "success": True,
                    "message": "Unequipped Magic Longsword from main_hand slot",
                    "equipped_items": {},
                    "character_stats": {
                        "armor_class": 10,
                        "abilities": {"strength": 15}
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            equipment_request = {
                "item_id": "magic-sword-123",
                "action": "unequip"
            }

            response = client.post(
                "/api/game/character/char_123/equipment",
                json=equipment_request
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert "Unequipped Magic Longsword" in result["message"]
            assert len(result["equipped_items"]) == 0

    def test_equip_item_validation_errors(self):
        """Test equipment request validation."""
        from app.main import app

        client = TestClient(app)

        # Test missing required fields
        invalid_requests = [
            {},  # Empty request
            {"item_id": ""},  # Empty item_id
            {"item_id": "test", "action": ""},  # Empty action
            {"item_id": "test", "action": "invalid"},  # Invalid action
        ]

        for invalid_request in invalid_requests:
            response = client.post(
                "/api/game/character/char_123/equipment",
                json=invalid_request
            )
            assert response.status_code == 422, (
                f"Should reject invalid request: {invalid_request}"
            )

    def test_equip_item_error_handling(self):
        """Test equipment endpoint error handling."""
        from app.main import app

        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            # Mock error response from ScribeAgent
            mock_scribe = AsyncMock()
            mock_scribe.equip_item = AsyncMock(
                return_value={"error": "Item not found in inventory"}
            )
            mock_get_scribe.return_value = mock_scribe

            equipment_request = {
                "item_id": "nonexistent-item",
                "action": "equip",
                "equipment_slot": "main_hand"
            }

            response = client.post(
                "/api/game/character/char_123/equipment",
                json=equipment_request
            )

            assert response.status_code == 400
            assert "Item not found in inventory" in response.json()["detail"]

    def test_equip_item_exception_handling(self):
        """Test equipment endpoint exception handling."""
        from app.main import app

        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            # Mock exception from ScribeAgent
            mock_scribe = AsyncMock()
            mock_scribe.equip_item = AsyncMock(
                side_effect=Exception("Database connection failed")
            )
            mock_get_scribe.return_value = mock_scribe

            equipment_request = {
                "item_id": "magic-sword-123",
                "action": "equip",
                "equipment_slot": "main_hand"
            }

            response = client.post(
                "/api/game/character/char_123/equipment",
                json=equipment_request
            )

            assert response.status_code == 500
            assert "Failed to manage equipment" in response.json()["detail"]

    def test_auto_detect_equipment_slot(self):
        """Test auto-detection of equipment slot."""
        from app.main import app

        client = TestClient(app)

        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = AsyncMock()
            mock_scribe.equip_item = AsyncMock(
                return_value={
                    "success": True,
                    "message": "Equipped Magic Longsword in weapon slot",
                    "equipped_items": {
                        "weapon": {
                            "id": "magic-sword-123",
                            "name": "Magic Longsword",
                            "equipment_type": "weapon"
                        }
                    },
                    "character_stats": {"armor_class": 11}
                }
            )
            mock_get_scribe.return_value = mock_scribe

            equipment_request = {
                "item_id": "magic-sword-123",
                "action": "equip"
                # No equipment_slot provided - should auto-detect
            }

            response = client.post(
                "/api/game/character/char_123/equipment",
                json=equipment_request
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True

            # Verify the mock was called with None for equipment_slot
            mock_scribe.equip_item.assert_called_once_with(
                "char_123",
                "magic-sword-123",
                "equip",
                None
            )