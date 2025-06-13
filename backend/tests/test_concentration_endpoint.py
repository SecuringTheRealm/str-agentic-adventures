"""
Tests for the concentration management endpoint.
"""

import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConcentrationEndpoint:
    """Test the concentration management endpoint."""

    def test_concentration_endpoint_start_concentration(self):
        """Test starting concentration on a spell."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock character exists
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test Wizard",
                    "character_class": "wizard",
                    "concentration": None,
                }
            )
            # Mock successful concentration start
            mock_scribe.manage_concentration = AsyncMock(
                return_value={
                    "success": True,
                    "action_performed": "start",
                    "concentration_status": {
                        "spell_name": "Fireball",
                        "spell_level": 3,
                        "duration_remaining": None,
                        "save_dc": None,
                    },
                    "message": "Started concentrating on Fireball",
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/character/char_123/concentration",
                json={
                    "action": "start",
                    "spell_name": "Fireball",
                    "spell_level": 3,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["action_performed"] == "start"
            assert data["concentration_status"]["spell_name"] == "Fireball"
            assert data["concentration_status"]["spell_level"] == 3

    def test_concentration_endpoint_end_concentration(self):
        """Test ending concentration."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock character exists with active concentration
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test Wizard",
                    "character_class": "wizard",
                    "concentration": {
                        "spell_name": "Fireball",
                        "spell_level": 3,
                        "duration_remaining": None,
                        "save_dc": None,
                    },
                }
            )
            # Mock successful concentration end
            mock_scribe.manage_concentration = AsyncMock(
                return_value={
                    "success": True,
                    "action_performed": "end",
                    "concentration_status": None,
                    "message": "Ended concentration on Fireball",
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/character/char_123/concentration",
                json={"action": "end"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["action_performed"] == "end"
            assert data["concentration_status"] is None

    def test_concentration_endpoint_check_concentration(self):
        """Test concentration check due to damage."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock character exists with active concentration
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test Wizard",
                    "character_class": "wizard",
                    "concentration": {
                        "spell_name": "Fireball",
                        "spell_level": 3,
                        "duration_remaining": None,
                        "save_dc": None,
                    },
                }
            )
            # Mock successful concentration check
            mock_scribe.manage_concentration = AsyncMock(
                return_value={
                    "success": True,
                    "action_performed": "check",
                    "concentration_status": {
                        "spell_name": "Fireball",
                        "spell_level": 3,
                        "duration_remaining": None,
                        "save_dc": None,
                    },
                    "check_result": {
                        "dice_roll": 15,
                        "constitution_modifier": 2,
                        "proficiency_bonus": 2,
                        "total_save": 19,
                        "save_dc": 12,
                        "success": True,
                        "damage_taken": 24,
                    },
                    "message": "Concentration check succeeded! Still concentrating on Fireball.",
                }
            )
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/character/char_123/concentration",
                json={"action": "check", "damage_taken": 24},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["action_performed"] == "check"
            assert data["check_result"]["total_save"] == 19
            assert data["check_result"]["save_dc"] == 12
            assert data["check_result"]["success"] is True

    def test_concentration_endpoint_character_not_found(self):
        """Test concentration endpoint with non-existent character."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock character not found
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(return_value=None)
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/character/nonexistent/concentration",
                json={"action": "start", "spell_name": "Fireball"},
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_concentration_endpoint_invalid_action(self):
        """Test concentration endpoint with invalid action."""
        from app.main import app

        client = TestClient(app)

        with patch("app.agents.scribe_agent.get_scribe") as mock_get_scribe:
            # Mock character exists
            mock_scribe = Mock()
            mock_scribe.get_character = AsyncMock(
                return_value={
                    "id": "char_123",
                    "name": "Test Wizard",
                    "character_class": "wizard",
                    "concentration": None,
                }
            )
            # Mock agent error for invalid action
            mock_scribe.manage_concentration = AsyncMock(
                return_value={"error": "Unknown concentration action: invalid"}
            )
            mock_get_scribe.return_value = mock_scribe

            response = client.post(
                "/api/game/character/char_123/concentration",
                json={"action": "invalid"},
            )

            assert response.status_code == 400
            assert "Unknown concentration action" in response.json()["detail"]

    def test_concentration_endpoint_validation_errors(self):
        """Test concentration endpoint input validation."""
        from app.main import app

        client = TestClient(app)

        # Test missing action field
        response = client.post(
            "/api/game/character/char_123/concentration",
            json={},
        )
        assert response.status_code == 422

        # Test invalid action type
        response = client.post(
            "/api/game/character/char_123/concentration",
            json={"action": 123},  # Should be string
        )
        assert response.status_code == 422


class TestConcentrationAgentMethods:
    """Test the concentration management methods in the scribe agent."""

    @pytest.mark.asyncio
    async def test_start_concentration_new_spell(self):
        """Test starting concentration on a new spell."""
        with patch("app.agents.scribe_agent.next") as mock_next, \
             patch("app.agents.scribe_agent.get_session") as mock_get_session:
            
            # Mock database
            mock_db = Mock()
            mock_db_character = Mock()
            mock_db_character.data = {
                "id": "char_123",
                "name": "Test Wizard",
                "concentration": None,
            }
            mock_db.get.return_value = mock_db_character
            mock_get_session.return_value = mock_db
            mock_next.return_value = mock_db

            from app.agents.scribe_agent import ScribeAgent
            scribe = ScribeAgent()

            result = await scribe.manage_concentration(
                "char_123", "start", spell_name="Fireball", spell_level=3
            )

            assert result["success"] is True
            assert result["action_performed"] == "start"
            assert result["concentration_status"]["spell_name"] == "Fireball"
            assert result["concentration_status"]["spell_level"] == 3

    @pytest.mark.asyncio
    async def test_end_concentration_no_active(self):
        """Test ending concentration when no spell is active."""
        with patch("app.agents.scribe_agent.next") as mock_next, \
             patch("app.agents.scribe_agent.get_session") as mock_get_session:
            
            # Mock database
            mock_db = Mock()
            mock_db_character = Mock()
            mock_db_character.data = {
                "id": "char_123",
                "name": "Test Wizard",
                "concentration": None,  # No active concentration
            }
            mock_db.get.return_value = mock_db_character
            mock_get_session.return_value = mock_db
            mock_next.return_value = mock_db

            from app.agents.scribe_agent import ScribeAgent
            scribe = ScribeAgent()

            result = await scribe.manage_concentration("char_123", "end")

            assert result["success"] is False
            assert "not currently concentrating" in result["message"]

    @pytest.mark.asyncio
    async def test_concentration_check_success(self):
        """Test successful concentration check."""
        with patch("app.agents.scribe_agent.next") as mock_next, \
             patch("app.agents.scribe_agent.get_session") as mock_get_session, \
             patch("app.plugins.rules_engine_plugin.RulesEnginePlugin") as mock_rules:
            
            # Mock database
            mock_db = Mock()
            mock_db_character = Mock()
            mock_db_character.data = {
                "id": "char_123",
                "name": "Test Wizard",
                "concentration": {"spell_name": "Fireball", "spell_level": 3},
                "abilities": {"constitution": 14},  # +2 modifier
                "proficiency_bonus": 2,
            }
            mock_db.get.return_value = mock_db_character
            mock_get_session.return_value = mock_db
            mock_next.return_value = mock_db

            # Mock dice roll - high roll to ensure success
            mock_rules_instance = Mock()
            mock_rules_instance.roll_dice.return_value = {"total": 18}
            mock_rules.return_value = mock_rules_instance

            from app.agents.scribe_agent import ScribeAgent
            scribe = ScribeAgent()

            result = await scribe.manage_concentration(
                "char_123", "check", damage_taken=20  # DC 10 (max of 10 or 20/2)
            )

            assert result["success"] is True
            assert result["check_result"]["success"] is True
            assert result["check_result"]["save_dc"] == 10
            assert result["check_result"]["total_save"] == 22  # 18 + 2 + 2
            assert result["concentration_status"] is not None  # Still concentrating

    @pytest.mark.asyncio
    async def test_concentration_check_failure(self):
        """Test failed concentration check."""
        with patch("app.agents.scribe_agent.next") as mock_next, \
             patch("app.agents.scribe_agent.get_session") as mock_get_session, \
             patch("app.plugins.rules_engine_plugin.RulesEnginePlugin") as mock_rules:
            
            # Mock database
            mock_db = Mock()
            mock_db_character = Mock()
            mock_db_character.data = {
                "id": "char_123",
                "name": "Test Wizard",
                "concentration": {"spell_name": "Fireball", "spell_level": 3},
                "abilities": {"constitution": 10},  # +0 modifier
                "proficiency_bonus": 2,
            }
            mock_db.get.return_value = mock_db_character
            mock_get_session.return_value = mock_db
            mock_next.return_value = mock_db

            # Mock dice roll - low roll to ensure failure
            mock_rules_instance = Mock()
            mock_rules_instance.roll_dice.return_value = {"total": 1}
            mock_rules.return_value = mock_rules_instance

            from app.agents.scribe_agent import ScribeAgent
            scribe = ScribeAgent()

            result = await scribe.manage_concentration(
                "char_123", "check", damage_taken = 40  # DC 20 (40/2)
            )

            assert result["success"] is True  # Action succeeded
            assert result["check_result"]["success"] is False  # But check failed
            assert result["check_result"]["save_dc"] == 20
            assert result["check_result"]["total_save"] == 3  # 1 + 0 + 2
            assert result["concentration_status"] is None  # No longer concentrating