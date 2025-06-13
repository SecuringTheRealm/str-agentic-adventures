"""
Tests for inventory system API endpoints.
"""

import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestInventoryAPIEndpoints:
    """Test inventory system API endpoints."""

    def setup_method(self):
        """Set up test client."""
        from app.main import app
        self.client = TestClient(app)

    def test_manage_equipment_valid_request(self):
        """Test equipment management with valid request."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            # Mock successful equipment management
            mock_scribe = Mock()
            mock_scribe.manage_equipment = AsyncMock(
                return_value={
                    "character_id": "char_123",
                    "action": "equipped",
                    "item": {"id": "item_123", "name": "Sword"},
                    "slot": "weapon",
                    "equipped_items": {"weapon": "item_123"}
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.post(
                "/api/game/character/char_123/equipment",
                json={"action": "equip", "item_id": "item_123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["character_id"] == "char_123"
            assert data["action"] == "equipped"
            assert data["item"]["id"] == "item_123"

    def test_manage_equipment_missing_fields(self):
        """Test equipment management with missing required fields."""
        # Test missing action
        response = self.client.post(
            "/api/game/character/char_123/equipment",
            json={"item_id": "item_123"}
        )
        assert response.status_code == 400

        # Test missing item_id
        response = self.client.post(
            "/api/game/character/char_123/equipment",
            json={"action": "equip"}
        )
        assert response.status_code == 400

        # Test empty request
        response = self.client.post(
            "/api/game/character/char_123/equipment",
            json={}
        )
        assert response.status_code == 400

    def test_manage_equipment_character_not_found(self):
        """Test equipment management when character is not found."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.manage_equipment = AsyncMock(
                return_value={"error": "Character char_123 not found"}
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.post(
                "/api/game/character/char_123/equipment",
                json={"action": "equip", "item_id": "item_123"}
            )

            assert response.status_code == 400
            assert "not found" in response.json()["detail"]

    def test_get_encumbrance_valid_request(self):
        """Test encumbrance calculation with valid character."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.calculate_encumbrance = AsyncMock(
                return_value={
                    "character_id": "char_123",
                    "current_weight": 25.5,
                    "carrying_capacity": 150,
                    "push_drag_lift": 300,
                    "encumbrance_level": "normal",
                    "weight_remaining": 124.5
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.get("/api/game/character/char_123/encumbrance")

            assert response.status_code == 200
            data = response.json()
            assert data["character_id"] == "char_123"
            assert data["current_weight"] == 25.5
            assert data["carrying_capacity"] == 150
            assert data["encumbrance_level"] == "normal"

    def test_get_encumbrance_character_not_found(self):
        """Test encumbrance calculation when character is not found."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.calculate_encumbrance = AsyncMock(
                return_value={"error": "Character char_123 not found"}
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.get("/api/game/character/char_123/encumbrance")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_apply_magical_effects_valid_request(self):
        """Test applying magical effects with valid request."""
        with patch("app.api.game_routes.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.apply_magical_effects = AsyncMock(
                return_value={
                    "character_id": "char_123",
                    "item_id": "magic_item_123",
                    "effects_applied": {"strength": 2, "armor_class": 1},
                    "magical_effects": {"magic_item_123": {"strength": 2, "armor_class": 1}},
                    "temp_stat_modifications": {"strength": 2, "armor_class": 1}
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.post(
                "/api/game/items/magical-effects",
                json={
                    "character_id": "char_123",
                    "item_id": "magic_item_123",
                    "effects": {"strength": 2, "armor_class": 1}
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["character_id"] == "char_123"
            assert data["item_id"] == "magic_item_123"
            assert data["effects_applied"]["strength"] == 2

    def test_apply_magical_effects_missing_fields(self):
        """Test applying magical effects with missing required fields."""
        # Test missing character_id
        response = self.client.post(
            "/api/game/items/magical-effects",
            json={"item_id": "magic_item_123", "effects": {"strength": 2}}
        )
        assert response.status_code == 400

        # Test missing item_id
        response = self.client.post(
            "/api/game/items/magical-effects",
            json={"character_id": "char_123", "effects": {"strength": 2}}
        )
        assert response.status_code == 400

    def test_get_items_catalog_no_filters(self):
        """Test getting items catalog without filters."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_items_catalog = AsyncMock(
                return_value={
                    "items": [
                        {
                            "id": "sword_longsword",
                            "name": "Longsword",
                            "description": "A versatile martial weapon",
                            "weight": 3.0,
                            "value": 15,
                            "rarity": "common",
                            "properties": {"type": "weapon", "damage": "1d8"}
                        }
                    ],
                    "total_count": 1,
                    "filters_applied": {"rarity": None, "item_type": None}
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.get("/api/game/items/catalog")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert data["total_count"] == 1
            assert len(data["items"]) == 1

    def test_get_items_catalog_with_filters(self):
        """Test getting items catalog with filters."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_items_catalog = AsyncMock(
                return_value={
                    "items": [
                        {
                            "id": "sword_flame_tongue",
                            "name": "Flame Tongue Sword",
                            "rarity": "rare",
                            "properties": {"type": "weapon"}
                        }
                    ],
                    "total_count": 1,
                    "filters_applied": {"rarity": "rare", "item_type": "weapon"}
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = self.client.get(
                "/api/game/items/catalog?rarity=rare&item_type=weapon"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 1
            assert data["filters_applied"]["rarity"] == "rare"
            assert data["filters_applied"]["item_type"] == "weapon"


class TestScribeAgentInventoryMethods:
    """Test ScribeAgent inventory management methods directly."""

    def setup_method(self):
        """Set up mock database and character."""
        self.character_id = "test_char_123"
        self.mock_character_data = {
            "id": self.character_id,
            "name": "Test Character",
            "inventory": [
                {
                    "id": "item_1",
                    "name": "Sword",
                    "weight": 3.0,
                    "quantity": 1,
                    "properties": {"type": "weapon"}
                },
                {
                    "id": "item_2",
                    "name": "Shield",
                    "weight": 6.0,
                    "quantity": 1,
                    "properties": {"type": "armor"}
                }
            ],
            "abilities": {"strength": 10},
            "equipped_items": {}
        }

    @patch("app.agents.scribe_agent.get_session")
    @patch("app.agents.scribe_agent.kernel_manager")
    @patch("app.agents.scribe_agent.init_db")
    def test_manage_equipment_equip_item(self, mock_init_db, mock_kernel_manager, mock_get_session):
        """Test equipping an item."""
        from app.agents.scribe_agent import ScribeAgent

        # Mock kernel manager
        mock_kernel_manager.create_kernel.return_value = Mock()

        # Mock database session
        mock_db = Mock()
        mock_character = Mock()
        mock_character.data = self.mock_character_data.copy()
        mock_db.get.return_value = mock_character
        mock_get_session.return_value.__next__.return_value = mock_db

        scribe = ScribeAgent()
        
        # Test equipping an item
        import asyncio
        result = asyncio.run(scribe.manage_equipment(self.character_id, "equip", "item_1"))

        assert "error" not in result
        assert result["action"] == "equipped"
        assert result["item"]["id"] == "item_1"
        assert "weapon" in result["equipped_items"]

    @patch("app.agents.scribe_agent.get_session")
    @patch("app.agents.scribe_agent.kernel_manager")
    @patch("app.agents.scribe_agent.init_db")
    def test_calculate_encumbrance(self, mock_init_db, mock_kernel_manager, mock_get_session):
        """Test encumbrance calculation."""
        from app.agents.scribe_agent import ScribeAgent

        # Mock kernel manager
        mock_kernel_manager.create_kernel.return_value = Mock()

        # Mock database session
        mock_db = Mock()
        mock_character = Mock()
        mock_character.data = self.mock_character_data.copy()
        mock_db.get.return_value = mock_character
        mock_get_session.return_value.__next__.return_value = mock_db

        scribe = ScribeAgent()
        
        # Test encumbrance calculation
        import asyncio
        result = asyncio.run(scribe.calculate_encumbrance(self.character_id))

        assert "error" not in result
        assert result["character_id"] == self.character_id
        assert result["current_weight"] == 9.0  # 3.0 + 6.0
        assert result["carrying_capacity"] == 150  # 10 * 15
        assert result["encumbrance_level"] == "normal"

    @patch("app.agents.scribe_agent.kernel_manager")
    @patch("app.agents.scribe_agent.init_db")
    def test_get_items_catalog_no_filters(self, mock_init_db, mock_kernel_manager):
        """Test getting items catalog without filters."""
        from app.agents.scribe_agent import ScribeAgent

        # Mock kernel manager
        mock_kernel_manager.create_kernel.return_value = Mock()

        scribe = ScribeAgent()
        
        # Test catalog retrieval
        import asyncio
        result = asyncio.run(scribe.get_items_catalog())

        assert "error" not in result
        assert "items" in result
        assert result["total_count"] > 0
        assert len(result["items"]) == result["total_count"]

    @patch("app.agents.scribe_agent.kernel_manager")
    @patch("app.agents.scribe_agent.init_db")
    def test_get_items_catalog_with_rarity_filter(self, mock_init_db, mock_kernel_manager):
        """Test getting items catalog with rarity filter."""
        from app.agents.scribe_agent import ScribeAgent

        # Mock kernel manager
        mock_kernel_manager.create_kernel.return_value = Mock()

        scribe = ScribeAgent()
        
        # Test catalog retrieval with filter
        import asyncio
        result = asyncio.run(scribe.get_items_catalog(rarity="rare"))

        assert "error" not in result
        assert "items" in result
        assert result["filters_applied"]["rarity"] == "rare"
        # All returned items should have "rare" rarity
        for item in result["items"]:
            assert item["rarity"] == "rare"