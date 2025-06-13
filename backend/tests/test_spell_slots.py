"""
Test spell slot management functionality.
"""

import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSpellSlotEndpoint:
    """Test the spell slot management endpoint."""

    def test_spell_slot_usage_wizard(self):
        """Test using spell slots for a wizard character."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock a wizard character
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_wizard",
                    "name": "Gandalf",
                    "character_class": "wizard",
                    "level": 3,
                    "spell_slots": {
                        "level_1_current": 4,
                        "level_1_max": 4,
                        "level_2_current": 2,
                        "level_2_max": 2,
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test using a level 1 spell slot
            response = client.post(
                "/api/game/character/char_wizard/spell-slots",
                json={
                    "action": "use",
                    "spell_level": 1,
                    "slot_count": 1
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Used 1 level 1 spell slot" in data["message"]
            assert data["slots_affected"]["level_1"] == -1

    def test_spell_slot_recovery(self):
        """Test recovering spell slots."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock a character with used spell slots
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_cleric",
                    "name": "Healer",
                    "character_class": "cleric",
                    "level": 2,
                    "spell_slots": {
                        "level_1_current": 1,  # Used 2 out of 3
                        "level_1_max": 3,
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test recovering spell slots
            response = client.post(
                "/api/game/character/char_cleric/spell-slots",
                json={
                    "action": "recover",
                    "spell_level": 1,
                    "slot_count": 2
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Recovered 2 level 1 spell slot" in data["message"]

    def test_spell_slot_long_rest(self):
        """Test long rest recovery."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_sorcerer",
                    "name": "Firebolt",
                    "character_class": "sorcerer",
                    "level": 5,
                    "spell_slots": {
                        "level_1_current": 2,
                        "level_1_max": 4,
                        "level_2_current": 1,
                        "level_2_max": 3,
                        "level_3_current": 0,
                        "level_3_max": 2,
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test long rest
            response = client.post(
                "/api/game/character/char_sorcerer/spell-slots",
                json={"action": "long_rest"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Long rest completed" in data["message"]

    def test_warlock_short_rest(self):
        """Test warlock short rest recovery."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_warlock",
                    "name": "Fiend Patron",
                    "character_class": "warlock",
                    "level": 3,
                    "spell_slots": {
                        "level_2_current": 0,  # Used both slots
                        "level_2_max": 2,
                    }
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test short rest for warlock
            response = client.post(
                "/api/game/character/char_warlock/spell-slots",
                json={"action": "short_rest"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Warlock spell slots recovered" in data["message"]

    def test_non_caster_spell_slots(self):
        """Test spell slot management for non-caster class."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_fighter",
                    "name": "Sword Guy",
                    "character_class": "fighter",
                    "level": 2,  # Below Eldritch Knight threshold
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test using spell slot on non-caster
            response = client.post(
                "/api/game/character/char_fighter/spell-slots",
                json={
                    "action": "use",
                    "spell_level": 1,
                    "slot_count": 1
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Not enough level 1 spell slots" in data["message"]

    def test_invalid_requests(self):
        """Test error handling for invalid requests."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_test",
                    "name": "Test Character",
                    "character_class": "wizard",
                    "level": 1,
                }
            )
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            # Test missing spell_level for 'use' action
            response = client.post(
                "/api/game/character/char_test/spell-slots",
                json={"action": "use"}
            )
            assert response.status_code == 400
            assert "spell_level is required" in response.json()["detail"]

            # Test invalid spell level
            response = client.post(
                "/api/game/character/char_test/spell-slots",
                json={
                    "action": "use",
                    "spell_level": 10  # Invalid level
                }
            )
            assert response.status_code == 400
            assert "spell_level must be between 1 and 9" in response.json()["detail"]

            # Test invalid slot count
            response = client.post(
                "/api/game/character/char_test/spell-slots",
                json={
                    "action": "use",
                    "spell_level": 1,
                    "slot_count": 0  # Invalid count
                }
            )
            assert response.status_code == 400
            assert "slot_count must be at least 1" in response.json()["detail"]

    def test_character_not_found(self):
        """Test handling of non-existent character."""
        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value=None)
            mock_get_scribe.return_value = mock_scribe

            from app.main import app
            client = TestClient(app)

            response = client.post(
                "/api/game/character/nonexistent/spell-slots",
                json={"action": "long_rest"}
            )

            assert response.status_code == 404
            assert "Character nonexistent not found" in response.json()["detail"]


class TestRulesEngineSpellSlots:
    """Test the spell slot calculation logic in RulesEnginePlugin."""

    def test_spell_slot_calculation(self):
        """Test spell slot calculation for different classes and levels."""
        from app.plugins.rules_engine_plugin import RulesEnginePlugin
        
        rules_engine = RulesEnginePlugin()

        # Test full caster (wizard) at level 5
        result = rules_engine.calculate_spell_slots("wizard", 5)
        assert result["caster_type"] == "full_caster"
        assert result["spell_slots"] == [4, 3, 2, 0, 0, 0, 0, 0, 0]
        assert result["total_slots"] == 9

        # Test half caster (paladin) at level 6
        result = rules_engine.calculate_spell_slots("paladin", 6)
        assert result["caster_type"] == "half_caster"
        assert result["spell_slots"] == [4, 2, 0, 0, 0, 0, 0, 0, 0]

        # Test non-caster (barbarian)
        result = rules_engine.calculate_spell_slots("barbarian", 10)
        assert result["caster_type"] == "non_caster"
        assert result["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert result["total_slots"] == 0

        # Test warlock at level 5
        result = rules_engine.calculate_spell_slots("warlock", 5)
        assert result["caster_type"] == "warlock"
        assert result["spell_slots"] == [0, 0, 2, 0, 0, 0, 0, 0, 0]

    def test_spell_slot_management_logic(self):
        """Test the spell slot management logic."""
        from app.plugins.rules_engine_plugin import RulesEnginePlugin
        
        rules_engine = RulesEnginePlugin()

        # Mock character data
        character_data = {
            "character_class": "wizard",
            "level": 3,
            "spell_slots": {
                "level_1_current": 4,
                "level_1_max": 4,
                "level_2_current": 2,
                "level_2_max": 2,
            }
        }

        # Test using a spell slot
        result = rules_engine.manage_spell_slots(character_data, "use", 1, 1)
        assert result["success"] is True
        assert result["spell_slots"]["level_1_current"] == 3

        # Test using more slots than available
        result = rules_engine.manage_spell_slots(character_data, "use", 2, 5)
        assert result["success"] is False
        assert "Not enough level 2 spell slots" in result["message"]

        # Test long rest
        character_data["spell_slots"]["level_1_current"] = 0
        character_data["spell_slots"]["level_2_current"] = 0
        result = rules_engine.manage_spell_slots(character_data, "long_rest")
        assert result["success"] is True
        assert result["spell_slots"]["level_1_current"] == 4
        assert result["spell_slots"]["level_2_current"] == 2