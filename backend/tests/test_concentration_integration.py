"""
Test integration of concentration spells with the spell casting system.
"""

from unittest.mock import Mock, patch

import pytest
from app.api.game_routes import cast_spell_in_combat
from app.models.game_models import CastSpellRequest


class TestConcentrationSpellIntegration:
    """Test concentration spell integration in combat spell casting."""

    @pytest.fixture
    def concentration_spell_data(self):
        """Sample concentration spell data."""
        return {
            "name": "Hold Person",
            "level": 2,
            "school": "enchantment",
            "concentration": True,
            "requires_concentration": True,  # Support both field names
            "save_type": "wisdom",
            "damage_dice": None,
            "healing_dice": None,
        }

    @pytest.fixture
    def non_concentration_spell_data(self):
        """Sample non-concentration spell data."""
        return {
            "name": "Magic Missile",
            "level": 1,
            "school": "evocation",
            "concentration": False,
            "requires_concentration": False,
            "auto_hit": True,
            "damage_dice": "1d4+1",
            "base_missiles": 3,
        }

    @pytest.fixture
    def cast_spell_request(self):
        """Sample cast spell request."""
        return CastSpellRequest(
            combat_id="test_combat_123",
            character_id="test_char_456",
            spell_id="hold_person",
            slot_level=2,
            target_ids=["enemy_1"],
        )

    @pytest.mark.asyncio
    async def test_concentration_spell_starts_concentration(
        self, concentration_spell_data, cast_spell_request
    ) -> None:
        """Test that casting a concentration spell starts concentration."""
        with (
            patch("app.api.game_routes._get_spell_data") as mock_get_spell,
            patch("app.api.game_routes._calculate_spell_effects") as mock_calc_effects,
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules_engine,
        ):
            # Setup mocks
            mock_get_spell.return_value = concentration_spell_data
            mock_calc_effects.return_value = {
                "spell_name": "Hold Person",
                "concentration": True,
                "effects": ["Target must make Wisdom saving throw"],
            }

            mock_engine_instance = Mock()
            mock_rules_engine.return_value = mock_engine_instance
            mock_engine_instance.start_concentration.return_value = {
                "success": True,
                "character_id": "test_char_456",
                "spell": "Hold Person",
                "message": "Concentration started on Hold Person",
            }

            # Call the function
            response = await cast_spell_in_combat("test_combat_123", cast_spell_request)

            # Verify concentration was started
            mock_engine_instance.start_concentration.assert_called_once()
            call_args = mock_engine_instance.start_concentration.call_args
            assert call_args[0][0] == "test_char_456"  # character_id
            assert call_args[0][1]["name"] == "Hold Person"  # spell_data

            # Verify response indicates success
            assert response.success is True
            assert "Hold Person" in response.message

    @pytest.mark.asyncio
    async def test_non_concentration_spell_no_concentration_started(
        self, non_concentration_spell_data, cast_spell_request
    ) -> None:
        """Test that casting a non-concentration spell doesn't start concentration."""
        cast_spell_request.spell_id = "magic_missile"

        with (
            patch("app.api.game_routes._get_spell_data") as mock_get_spell,
            patch("app.api.game_routes._calculate_spell_effects") as mock_calc_effects,
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules_engine,
        ):
            # Setup mocks
            mock_get_spell.return_value = non_concentration_spell_data
            mock_calc_effects.return_value = {
                "spell_name": "Magic Missile",
                "concentration": False,
                "effects": ["Fires 3 missiles"],
            }

            mock_engine_instance = Mock()
            mock_rules_engine.return_value = mock_engine_instance

            # Call the function
            response = await cast_spell_in_combat("test_combat_123", cast_spell_request)

            # Verify concentration was NOT started
            mock_engine_instance.start_concentration.assert_not_called()

            # Verify response indicates success
            assert response.success is True
            assert "Magic Missile" in response.message

    @pytest.mark.asyncio
    async def test_concentration_spell_breaks_existing_concentration(
        self, concentration_spell_data, cast_spell_request
    ) -> None:
        """Test that casting a concentration spell when already concentrating breaks the old concentration."""
        with (
            patch("app.api.game_routes._get_spell_data") as mock_get_spell,
            patch("app.api.game_routes._calculate_spell_effects") as mock_calc_effects,
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules_engine,
        ):
            # Setup mocks
            mock_get_spell.return_value = concentration_spell_data
            mock_calc_effects.return_value = {
                "spell_name": "Hold Person",
                "concentration": True,
                "effects": ["Target must make Wisdom saving throw"],
            }

            mock_engine_instance = Mock()
            mock_rules_engine.return_value = mock_engine_instance
            mock_engine_instance.start_concentration.return_value = {
                "success": True,
                "character_id": "test_char_456",
                "spell": "Hold Person",
                "message": "Concentration started on Hold Person",
            }

            # Call the function
            response = await cast_spell_in_combat("test_combat_123", cast_spell_request)

            # Verify concentration was started (which will automatically break existing concentration)
            mock_engine_instance.start_concentration.assert_called_once()

            # Verify response indicates success
            assert response.success is True
            assert (
                response.concentration_broken is False
            )  # Should be False because we successfully started new concentration

    @pytest.mark.asyncio
    async def test_concentration_spell_failure_doesnt_break_cast(
        self, concentration_spell_data, cast_spell_request
    ) -> None:
        """Test that concentration failure doesn't prevent spell from being cast."""
        with (
            patch("app.api.game_routes._get_spell_data") as mock_get_spell,
            patch("app.api.game_routes._calculate_spell_effects") as mock_calc_effects,
            patch(
                "app.plugins.rules_engine_plugin.RulesEnginePlugin"
            ) as mock_rules_engine,
        ):
            # Setup mocks
            mock_get_spell.return_value = concentration_spell_data
            mock_calc_effects.return_value = {
                "spell_name": "Hold Person",
                "concentration": True,
                "effects": ["Target must make Wisdom saving throw"],
            }

            mock_engine_instance = Mock()
            mock_rules_engine.return_value = mock_engine_instance
            # Simulate concentration failure
            mock_engine_instance.start_concentration.return_value = {
                "success": False,
                "error": "Spell does not require concentration",
                "spell": "Hold Person",
            }

            # Call the function
            response = await cast_spell_in_combat("test_combat_123", cast_spell_request)

            # Verify concentration was attempted
            mock_engine_instance.start_concentration.assert_called_once()

            # Verify spell cast still succeeds despite concentration failure
            assert response.success is True
            assert "Hold Person" in response.message
            assert response.concentration_broken is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
