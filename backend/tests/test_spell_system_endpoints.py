"""
Tests for the spell system API endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from fastapi.testclient import TestClient


def _wizard_character_data(**overrides):
    """A minimal persisted wizard character dict, as returned by scribe.get_character."""
    data = {
        "id": "test_char_123",
        "name": "Test Wizard",
        "race": "human",
        "character_class": "wizard",
        "level": 3,
        "abilities": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 10,
            "charisma": 10,
        },
        "hit_points": {"current": 18, "maximum": 18},
        "spellcasting": None,
    }
    data.update(overrides)
    return data


class TestSpellSystemEndpoints:
    """Test suite for spell system API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_manage_character_spells(self, client) -> None:
        """Learning spells persists them to the character sheet."""
        character_id = "test_char_123"
        request_data = {
            "action": "learn",
            "spell_ids": ["magic_missile", "fireball"],
        }

        with patch("app.api.routes.spell_routes.get_scribe") as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.get_character = AsyncMock(
                return_value=_wizard_character_data()
            )
            mock_scribe.update_character = AsyncMock(return_value={})

            response = client.post(
                f"/game/character/{character_id}/spells", json=request_data
            )
            assert response.status_code == 200

            data = response.json()
            assert data["character_id"] == character_id
            assert data["action"] == "learn"
            assert data["spell_ids"] == ["magic_missile", "fireball"]
            assert data["success"] is True

            # The character sheet passed to persistence has the learned spells.
            updated = mock_scribe.update_character.call_args[0][1]
            assert set(updated["spellcasting"]["known_spells"]) == {
                "magic_missile",
                "fireball",
            }

    def test_manage_character_spells_prepare_requires_known(self, client) -> None:
        """Preparing a spell that hasn't been learned is an honest 400, not fake success."""
        character_id = "test_char_123"
        request_data = {"action": "prepare", "spell_ids": ["fireball"]}

        with patch("app.api.routes.spell_routes.get_scribe") as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.get_character = AsyncMock(
                return_value=_wizard_character_data()
            )

            response = client.post(
                f"/game/character/{character_id}/spells", json=request_data
            )
            assert response.status_code == 400

    def test_manage_character_spells_not_found(self, client) -> None:
        """A nonexistent character returns 404, not fake success."""
        with patch("app.api.routes.spell_routes.get_scribe") as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.get_character = AsyncMock(return_value=None)

            response = client.post(
                "/game/character/does-not-exist/spells",
                json={"action": "learn", "spell_ids": ["magic_missile"]},
            )
            assert response.status_code == 404

    def test_manage_spell_slots(self, client) -> None:
        """Using a spell slot persists the expenditure to the character sheet."""
        character_id = "test_char_123"
        request_data = {
            "action": "use",
            "slot_level": 1,
            "count": 1,
        }

        with patch("app.api.routes.spell_routes.get_scribe") as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.get_character = AsyncMock(
                return_value=_wizard_character_data()
            )
            mock_scribe.update_character = AsyncMock(return_value={})

            response = client.post(
                f"/game/character/{character_id}/spell-slots", json=request_data
            )
            assert response.status_code == 200

            data = response.json()
            assert data["character_id"] == character_id
            assert data["action"] == "use"
            assert data["slot_level"] == 1
            assert data["success"] is True

            # A level-3 wizard has 4 level-1 slots (SRD table); one was spent.
            updated = mock_scribe.update_character.call_args[0][1]
            slots = updated["spellcasting"]["spell_slots"]
            level_1_slot = next(s for s in slots if s["level"] == 1)
            assert level_1_slot["total"] == 4
            assert level_1_slot["used"] == 1

    def test_manage_spell_slots_cannot_exceed_total(self, client) -> None:
        """Using more slots than remain is an honest 400, not fake success."""
        character_id = "test_char_123"
        request_data = {"action": "use", "slot_level": 1, "count": 5}

        with patch("app.api.routes.spell_routes.get_scribe") as mock_get_scribe:
            mock_scribe = mock_get_scribe.return_value
            mock_scribe.get_character = AsyncMock(
                return_value=_wizard_character_data()
            )

            response = client.post(
                f"/game/character/{character_id}/spell-slots", json=request_data
            )
            assert response.status_code == 400

    def test_cast_spell_in_combat(self, client) -> None:
        """Test casting spell in combat endpoint."""
        combat_id = "test_combat_123"
        request_data = {
            "character_id": "test_char_123",
            "spell_id": "magic_missile",
            "slot_level": 1,
            "target_ids": ["enemy_1"],
        }

        response = client.post(
            f"/game/combat/{combat_id}/cast-spell", json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "spell_effects" in data
        assert data["slot_used"] is True

    def test_get_spell_list(self, client) -> None:
        """Test getting spell list endpoint."""
        response = client.get("/game/spells/list")
        assert response.status_code == 200

        data = response.json()
        assert "spells" in data
        assert "total_count" in data
        assert len(data["spells"]) == data["total_count"]

    def test_get_spell_list_filtered_by_class(self, client) -> None:
        """Test getting spell list filtered by character class."""
        response = client.get("/game/spells/list?character_class=wizard")
        assert response.status_code == 200

        data = response.json()
        assert "spells" in data
        assert "total_count" in data

        # Check that all returned spells are available to wizards
        for spell in data["spells"]:
            assert "wizard" in spell["available_classes"]

    def test_get_spell_list_filtered_by_level(self, client) -> None:
        """Test getting spell list filtered by spell level."""
        response = client.get("/game/spells/list?spell_level=1")
        assert response.status_code == 200

        data = response.json()
        assert "spells" in data

        # Check that all returned spells are level 1
        for spell in data["spells"]:
            assert spell["level"] == 1

    def test_calculate_spell_save_dc(self, client) -> None:
        """Test calculating spell save DC endpoint."""
        params = {
            "character_class": "wizard",
            "level": 5,
            "spellcasting_ability_score": 16,
        }

        response = client.post("/game/spells/save-dc", json=params)
        assert response.status_code == 200

        data = response.json()
        assert "save_dc" in data
        assert data["character_class"] == "wizard"
        assert data["level"] == 5
        assert data["spellcasting_ability_score"] == 16

        # Verify calculation: 8 + proficiency_bonus + ability_modifier
        # Level 5 = +3 proficiency, 16 ability = +3 modifier, Expected: 8 + 3 + 3 = 14
        assert data["save_dc"] == 14

    def test_manage_concentration_start(self, client) -> None:
        """Test starting concentration on a spell."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "start",
            "spell_id": "concentration_spell",
        }

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["concentration_maintained"] is True
        assert data["spell_ended"] is False

    def test_manage_concentration_end(self, client) -> None:
        """Test ending concentration on a spell."""
        character_id = "test_char_123"
        request_data = {"character_id": character_id, "action": "end"}

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["concentration_maintained"] is False
        assert data["spell_ended"] is True

    def test_manage_concentration_check(self, client) -> None:
        """Test concentration check with damage."""
        character_id = "test_char_123"
        request_data = {
            "character_id": character_id,
            "action": "check",
            "damage_taken": 20,
        }

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "concentration_maintained" in data
        assert data["dc"] == 10  # max(10, 20//2) = 10
        assert "roll_result" in data

    def test_manage_concentration_invalid_action(self, client) -> None:
        """Test concentration management with invalid action rejects at schema level."""
        character_id = "test_char_123"
        request_data = {"character_id": character_id, "action": "invalid_action"}

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 422

    def test_manage_concentration_start_without_spell_id(self, client) -> None:
        """Test starting concentration without spell_id."""
        character_id = "test_char_123"
        request_data = {"character_id": character_id, "action": "start"}

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 400

    def test_manage_concentration_check_without_damage(self, client) -> None:
        """Test concentration check without damage_taken."""
        character_id = "test_char_123"
        request_data = {"character_id": character_id, "action": "check"}

        response = client.post(
            f"/game/character/{character_id}/concentration", json=request_data
        )
        assert response.status_code == 400
