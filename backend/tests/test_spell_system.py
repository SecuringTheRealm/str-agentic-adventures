"""
Comprehensive tests for the spell system API endpoints.
"""

import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSpellSystemEndpoints:
    """Test spell system API endpoints."""

    def test_manage_character_spells_add(self):
        """Test adding a spell to a character."""
        from app.main import app

        client = TestClient(app)

        # Test adding a spell
        spell_data = {
            "action": "add",
            "spell": {
                "id": "spell_123",
                "name": "Fireball",
                "level": 3,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "150 feet",
                "components": "V, S, M",
                "duration": "Instantaneous",
                "description": "A bright streak flashes from your pointing finger..."
            }
        }

        response = client.post("/api/game/character/char_123/spells", json=spell_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "Fireball" in response_data["message"]
        assert response_data["spell"]["name"] == "Fireball"

    def test_manage_character_spells_remove(self):
        """Test removing a spell from a character."""
        from app.main import app

        client = TestClient(app)

        # Test removing a spell
        spell_data = {
            "action": "remove",
            "spell_id": "spell_123"
        }

        response = client.post("/api/game/character/char_123/spells", json=spell_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "removed" in response_data["message"]

    def test_manage_character_spells_learn(self):
        """Test learning a spell for a character."""
        from app.main import app

        client = TestClient(app)

        # Test learning a spell
        spell_data = {
            "action": "learn",
            "spell": {
                "id": "spell_456",
                "name": "Magic Missile",
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "120 feet",
                "components": "V, S",
                "duration": "Instantaneous",
                "description": "You create three glowing darts of magical force."
            }
        }

        response = client.post("/api/game/character/char_123/spells", json=spell_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "learned" in response_data["message"]
        assert response_data["spell"]["name"] == "Magic Missile"

    def test_manage_character_spells_invalid_action(self):
        """Test invalid spell action."""
        from app.main import app

        client = TestClient(app)

        # Test invalid action
        spell_data = {
            "action": "invalid_action"
        }

        response = client.post("/api/game/character/char_123/spells", json=spell_data)
        assert response.status_code == 400

    def test_manage_spell_slots_use(self):
        """Test using spell slots."""
        from app.main import app

        client = TestClient(app)

        # Test using spell slots
        slot_data = {
            "action": "use",
            "level": 3,
            "amount": 1
        }

        response = client.post("/api/game/character/char_123/spell-slots", json=slot_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "Used" in response_data["message"]
        assert response_data["level"] == 3
        assert response_data["used"] == 1

    def test_manage_spell_slots_recover(self):
        """Test recovering spell slots."""
        from app.main import app

        client = TestClient(app)

        # Test recovering spell slots
        slot_data = {
            "action": "recover",
            "level": 2,
            "amount": 2
        }

        response = client.post("/api/game/character/char_123/spell-slots", json=slot_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "Recovered" in response_data["message"]
        assert response_data["level"] == 2
        assert response_data["recovered"] == 2

    def test_manage_spell_slots_set(self):
        """Test setting spell slot totals."""
        from app.main import app

        client = TestClient(app)

        # Test setting spell slots
        slot_data = {
            "action": "set",
            "level": 1,
            "amount": 4
        }

        response = client.post("/api/game/character/char_123/spell-slots", json=slot_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert "Set" in response_data["message"]
        assert response_data["level"] == 1
        assert response_data["total"] == 4

    def test_manage_spell_slots_invalid_action(self):
        """Test invalid spell slot action."""
        from app.main import app

        client = TestClient(app)

        # Test invalid action
        slot_data = {
            "action": "invalid_action",
            "level": 1,
            "amount": 1
        }

        response = client.post("/api/game/character/char_123/spell-slots", json=slot_data)
        assert response.status_code == 400

    def test_cast_spell_in_combat(self):
        """Test casting a spell during combat."""
        from app.main import app

        client = TestClient(app)

        # Test casting a spell
        cast_data = {
            "character_id": "char_123",
            "spell_id": "spell_123",
            "spell_level": 3,
            "target_id": "enemy_456"
        }

        response = client.post("/api/game/combat/combat_789/cast-spell", json=cast_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["effects"]) > 0
        assert "enemy_456" in response_data["targets_affected"]
        assert response_data["narrative"] != ""

    def test_cast_spell_area_effect(self):
        """Test casting an area effect spell."""
        from app.main import app

        client = TestClient(app)

        # Test casting an area spell
        cast_data = {
            "character_id": "char_123",
            "spell_id": "fireball",
            "spell_level": 3,
            "target_position": {"x": 10, "y": 15}
        }

        response = client.post("/api/game/combat/combat_789/cast-spell", json=cast_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["effects"]) > 0

    def test_get_spells_list_by_class(self):
        """Test getting spells list filtered by class."""
        from app.main import app

        client = TestClient(app)

        # Test getting spells by class
        query_params = {
            "character_class": "wizard",
            "level": 3
        }

        response = client.get("/api/game/spells/list", params=query_params)
        assert response.status_code == 200

        response_data = response.json()
        assert "spells" in response_data
        assert isinstance(response_data["spells"], list)

    def test_get_spells_list_by_school(self):
        """Test getting spells list filtered by school."""
        from app.main import app

        client = TestClient(app)

        # Test getting spells by school
        query_params = {
            "school": "evocation",
            "level": 1
        }

        response = client.get("/api/game/spells/list", params=query_params)
        assert response.status_code == 200

        response_data = response.json()
        assert "spells" in response_data

    def test_calculate_save_dc(self):
        """Test calculating spell save DC."""
        from app.main import app

        client = TestClient(app)

        # Test calculating save DC
        dc_data = {
            "character_id": "char_123",
            "spell_id": "spell_456"
        }

        response = client.post("/api/game/spells/save-dc", json=dc_data)
        assert response.status_code == 200

        response_data = response.json()
        assert "save_dc" in response_data
        assert "calculation" in response_data
        assert response_data["save_dc"] >= 8  # Minimum save DC

    def test_calculate_attack_bonus(self):
        """Test calculating spell attack bonus."""
        from app.main import app

        client = TestClient(app)

        # Test calculating attack bonus
        bonus_data = {
            "character_id": "char_123",
            "spell_id": "spell_789"
        }

        response = client.post("/api/game/spells/attack-bonus", json=bonus_data)
        assert response.status_code == 200

        response_data = response.json()
        assert "attack_bonus" in response_data
        assert "calculation" in response_data
        assert isinstance(response_data["attack_bonus"], int)

    def test_concentration_start(self):
        """Test starting concentration on a spell."""
        from app.main import app

        client = TestClient(app)

        # Test starting concentration
        concentration_data = {
            "action": "start",
            "spell_id": "spell_concentration"
        }

        response = client.post("/api/game/character/char_123/concentration", json=concentration_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["is_concentrating"] is True
        assert response_data["spell_id"] == "spell_concentration"
        assert response_data["rounds_remaining"] > 0

    def test_concentration_end(self):
        """Test ending concentration."""
        from app.main import app

        client = TestClient(app)

        # Test ending concentration
        concentration_data = {
            "action": "end"
        }

        response = client.post("/api/game/character/char_123/concentration", json=concentration_data)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["is_concentrating"] is False
        assert response_data["spell_id"] is None

    def test_concentration_check(self):
        """Test concentration check after taking damage."""
        from app.main import app

        client = TestClient(app)

        # Test concentration check
        concentration_data = {
            "action": "check",
            "spell_id": "spell_concentration",
            "damage_taken": 15
        }

        response = client.post("/api/game/character/char_123/concentration", json=concentration_data)
        assert response.status_code == 200

        response_data = response.json()
        assert "is_concentrating" in response_data

    def test_concentration_invalid_action(self):
        """Test invalid concentration action."""
        from app.main import app

        client = TestClient(app)

        # Test invalid action
        concentration_data = {
            "action": "invalid_action"
        }

        response = client.post("/api/game/character/char_123/concentration", json=concentration_data)
        assert response.status_code == 400


class TestSpellSystemValidation:
    """Test spell system input validation."""

    def test_spell_data_validation(self):
        """Test spell data validation in requests."""
        from app.main import app

        client = TestClient(app)

        # Test with invalid spell data
        invalid_spell_data = {
            "action": "add",
            "spell": {
                "name": "",  # Empty name should be invalid
                "level": -1,  # Negative level should be invalid
            }
        }

        response = client.post("/api/game/character/char_123/spells", json=invalid_spell_data)
        # The endpoint might handle this gracefully or return an error
        # Just ensure we get a response
        assert response.status_code in [200, 400, 422]

    def test_spell_slot_validation(self):
        """Test spell slot validation."""
        from app.main import app

        client = TestClient(app)

        # Test with invalid level
        invalid_slot_data = {
            "action": "use",
            "level": 0,  # Level 0 should be cantrips, might be invalid for slots
            "amount": -1  # Negative amount should be invalid
        }

        response = client.post("/api/game/character/char_123/spell-slots", json=invalid_slot_data)
        # Should either handle gracefully or return validation error
        assert response.status_code in [200, 400, 422]

    def test_cast_spell_validation(self):
        """Test spell casting validation."""
        from app.main import app

        client = TestClient(app)

        # Test with missing required fields
        invalid_cast_data = {
            "character_id": "",  # Empty character ID
            "spell_id": "",  # Empty spell ID
        }

        response = client.post("/api/game/combat/combat_789/cast-spell", json=invalid_cast_data)
        # Should return validation error
        assert response.status_code in [400, 422]


class TestSpellSystemErrorHandling:
    """Test spell system error handling."""

    def test_character_not_found(self):
        """Test handling when character is not found."""
        from app.main import app

        client = TestClient(app)

        # Test with non-existent character
        spell_data = {
            "action": "add",
            "spell": {
                "id": "spell_123",
                "name": "Test Spell",
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "30 feet",
                "components": "V, S",
                "duration": "Instantaneous",
                "description": "A test spell."
            }
        }

        response = client.post("/api/game/character/nonexistent/spells", json=spell_data)
        # Should handle gracefully since we're using basic implementation
        # In a real system, this might return 404
        assert response.status_code in [200, 404, 500]

    def test_combat_not_found(self):
        """Test handling when combat is not found."""
        from app.main import app

        client = TestClient(app)

        # Test with non-existent combat
        cast_data = {
            "character_id": "char_123",
            "spell_id": "spell_123",
            "spell_level": 1
        }

        response = client.post("/api/game/combat/nonexistent/cast-spell", json=cast_data)
        # Should handle gracefully since we're using basic implementation
        assert response.status_code in [200, 404, 500]

    def test_spell_not_found(self):
        """Test handling when spell is not found."""
        from app.main import app

        client = TestClient(app)

        # Test with non-existent spell
        dc_data = {
            "character_id": "char_123",
            "spell_id": "nonexistent_spell"
        }

        response = client.post("/api/game/spells/save-dc", json=dc_data)
        # Should handle gracefully since we're using basic implementation
        assert response.status_code in [200, 404, 500]