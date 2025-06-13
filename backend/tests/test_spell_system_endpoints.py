"""
Tests for the spell system API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.game_models import CharacterClass


class TestSpellSystemEndpoints:
    """Test suite for spell system API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_manage_character_spells(self, client):
        """Test managing character spells endpoint."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "learn",
            "spell_ids": ["magic_missile", "fireball"]
        }
        
        response = client.post(f"/api/game/character/{character_id}/spells", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["character_id"] == character_id
        assert data["action"] == "learn"
        assert data["spell_ids"] == ["magic_missile", "fireball"]
        assert data["success"] is True

    def test_manage_spell_slots(self, client):
        """Test managing spell slots endpoint."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "use",
            "slot_level": 1,
            "count": 1
        }
        
        response = client.post(f"/api/game/character/{character_id}/spell-slots", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["character_id"] == character_id
        assert data["action"] == "use"
        assert data["slot_level"] == 1
        assert data["success"] is True

    def test_cast_spell_in_combat(self, client):
        """Test casting spell in combat endpoint."""
        combat_id = "test_combat_123"
        request_data = {
            "combat_id": combat_id,
            "character_id": "test_char_123",
            "spell_id": "magic_missile",
            "slot_level": 1,
            "target_ids": ["enemy_1"]
        }
        
        response = client.post(f"/api/game/combat/{combat_id}/cast-spell", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "spell_effects" in data
        assert data["slot_used"] is True

    def test_get_spell_list(self, client):
        """Test getting spell list endpoint."""
        response = client.get("/api/game/spells/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "spells" in data
        assert "total_count" in data
        assert len(data["spells"]) == data["total_count"]

    def test_get_spell_list_filtered_by_class(self, client):
        """Test getting spell list filtered by character class."""
        response = client.get("/api/game/spells/list?character_class=wizard")
        assert response.status_code == 200
        
        data = response.json()
        assert "spells" in data
        assert "total_count" in data
        
        # Check that all returned spells are available to wizards
        for spell in data["spells"]:
            assert "wizard" in spell["classes"]

    def test_get_spell_list_filtered_by_level(self, client):
        """Test getting spell list filtered by spell level."""
        response = client.get("/api/game/spells/list?spell_level=1")
        assert response.status_code == 200
        
        data = response.json()
        assert "spells" in data
        
        # Check that all returned spells are level 1
        for spell in data["spells"]:
            assert spell["level"] == 1

    def test_calculate_spell_save_dc(self, client):
        """Test calculating spell save DC endpoint."""
        params = {
            "character_class": "wizard",
            "level": 5,
            "spellcasting_ability_score": 16
        }
        
        response = client.post("/api/game/spells/save-dc", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "save_dc" in data
        assert data["character_class"] == "wizard"
        assert data["level"] == 5
        assert data["spellcasting_ability_score"] == 16
        
        # Verify calculation: 8 + proficiency_bonus + ability_modifier
        # Level 5 = +3 proficiency, 16 ability = +3 modifier
        # Expected: 8 + 3 + 3 = 14
        assert data["save_dc"] == 14

    def test_manage_concentration_start(self, client):
        """Test starting concentration on a spell."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "start",
            "spell_id": "concentration_spell"
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["concentration_maintained"] is True
        assert data["spell_ended"] is False

    def test_manage_concentration_end(self, client):
        """Test ending concentration on a spell."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "end"
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["concentration_maintained"] is False
        assert data["spell_ended"] is True

    def test_manage_concentration_check(self, client):
        """Test concentration check with damage."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "check",
            "damage_taken": 20
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "concentration_maintained" in data
        assert data["dc"] == 10  # max(10, 20//2) = 10
        assert "roll_result" in data

    def test_manage_concentration_invalid_action(self, client):
        """Test concentration management with invalid action."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "invalid_action"
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 400

    def test_manage_concentration_start_without_spell_id(self, client):
        """Test starting concentration without spell_id."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "start"
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 400

    def test_manage_concentration_check_without_damage(self, client):
        """Test concentration check without damage_taken."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "check"
        }
        
        response = client.post(f"/api/game/character/{character_id}/concentration", json=request_data)
        assert response.status_code == 400