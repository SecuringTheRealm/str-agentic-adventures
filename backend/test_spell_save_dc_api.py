"""
Tests for the spell save DC API endpoint.
"""
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestSpellSaveDCAPI:
    """Test spell save DC API endpoint."""

    def test_spell_save_dc_valid_wizard(self):
        """Test spell save DC calculation for a valid wizard character."""
        from app.main import app

        client = TestClient(app)

        # Mock character data returned by scribe agent
        mock_character = {
            "id": "char_123",
            "name": "Gandalf",
            "character_class": "wizard",
            "level": 5,
            "abilities": {
                "strength": 10,
                "dexterity": 14,
                "constitution": 16,
                "intelligence": 18,
                "wisdom": 12,
                "charisma": 8
            }
        }

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value=mock_character)
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/spells/save-dc", 
                json={"character_id": "char_123"}
            )

            assert response.status_code == 200
            data = response.json()
            
            assert data["spell_save_dc"] == 15  # 8 + 3 + 4
            assert data["spellcasting_ability"] == "intelligence"
            assert data["ability_score"] == 18
            assert data["ability_modifier"] == 4
            assert data["proficiency_bonus"] == 3
            assert data["level"] == 5
            assert data["character_class"] == "wizard"
            assert data["error"] is None

    def test_spell_save_dc_non_spellcaster(self):
        """Test spell save DC calculation for non-spellcasting class."""
        from app.main import app

        client = TestClient(app)

        # Mock barbarian character
        mock_character = {
            "id": "char_456",
            "name": "Conan",
            "character_class": "barbarian",
            "level": 3,
            "abilities": {
                "strength": 18,
                "dexterity": 14,
                "constitution": 16,
                "intelligence": 10,
                "wisdom": 12,
                "charisma": 8
            }
        }

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value=mock_character)
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/spells/save-dc", 
                json={"character_id": "char_456"}
            )

            assert response.status_code == 200
            data = response.json()
            
            assert data["spell_save_dc"] is None
            assert data["spellcasting_ability"] is None
            assert data["error"] is not None
            assert "does not have innate spellcasting ability" in data["error"]

    def test_spell_save_dc_character_not_found(self):
        """Test spell save DC calculation when character is not found."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value={"error": "Character not found"})
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/spells/save-dc", 
                json={"character_id": "nonexistent"}
            )

            assert response.status_code == 404
            assert "Character not found" in response.json()["detail"]

    def test_spell_save_dc_invalid_request(self):
        """Test spell save DC calculation with invalid request."""
        from app.main import app

        client = TestClient(app)

        # Test missing character_id
        response = client.post("/api/game/spells/save-dc", json={})
        assert response.status_code == 422

        # Test invalid JSON
        response = client.post("/api/game/spells/save-dc", json={"invalid": "data"})
        assert response.status_code == 422

    def test_spell_save_dc_missing_character_data(self):
        """Test spell save DC calculation when character is missing required data."""
        from app.main import app

        client = TestClient(app)

        # Mock character missing abilities
        mock_character = {
            "id": "char_789",
            "name": "Incomplete",
            "character_class": "wizard",
            "level": 1,
            # Missing abilities
        }

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value=mock_character)
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/spells/save-dc", 
                json={"character_id": "char_789"}
            )

            assert response.status_code == 400
            assert "missing ability scores" in response.json()["detail"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])