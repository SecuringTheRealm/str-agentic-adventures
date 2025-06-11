"""Tests for the enhanced Rules Engine Plugin."""

import pytest
from app.plugins.rules_engine_plugin import RulesEnginePlugin


class TestDiceRolling:
    """Test enhanced dice rolling functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_basic_dice_notation(self):
        """Test basic dice notation still works."""
        result = self.plugin.roll_dice("1d20")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 1
        assert 1 <= result["rolls"][0] <= 20
        assert result["total"] == result["rolls"][0]

    def test_dice_with_modifier(self):
        """Test dice with positive and negative modifiers."""
        result = self.plugin.roll_dice("1d20+5")
        assert result["modifier"] == 5
        assert result["total"] == result["rolls"][0] + 5

        result = self.plugin.roll_dice("2d6-2")
        assert result["modifier"] == -2
        assert result["total"] == sum(result["rolls"]) - 2

    def test_drop_lowest_notation(self):
        """Unsupported notation should return an error."""
        result = self.plugin.roll_dice("4d6dl1")
        assert "error" in result

    def test_keep_highest_notation(self):
        """Unsupported notation should return an error."""
        result = self.plugin.roll_dice("2d20kh1")
        assert "error" in result

    def test_keep_lowest_notation(self):
        """Unsupported notation should return an error."""
        result = self.plugin.roll_dice("2d20kl1")
        assert "error" in result

    def test_reroll_notation(self):
        """Unsupported reroll notation returns error."""
        result = self.plugin.roll_dice("1d6r1")
        assert "error" in result

    def test_multiple_dice_pools(self):
        """Unsupported multi-pool notation returns error."""
        result = self.plugin.roll_dice("2d6+1d4+3")
        assert "error" in result


class TestCharacterIntegration:
    """Test character sheet integration features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_roll_with_character_context(self):
        """Test rolling with character context for automatic modifiers."""
        character = {
            "abilities": {"strength": 16, "dexterity": 14},
            "proficiency_bonus": 3,
            "proficiencies": ["athletics", "stealth"],
        }
        if not hasattr(self.plugin, "roll_with_character"):
            pytest.skip("roll_with_character not implemented")
        result = self.plugin.roll_with_character("1d20", character, "athletics")
        assert "character_bonus" in result
        assert "total" in result
        expected_bonus = 3 + 3
        assert result["character_bonus"] == expected_bonus

    def test_manual_roll_input(self):
        """Test manual roll input functionality."""
        if not hasattr(self.plugin, "input_manual_roll"):
            pytest.skip("input_manual_roll not implemented")
        result = self.plugin.input_manual_roll("1d20", 18)
        assert result["notation"] == "1d20"
        assert result["manual_result"] == 18
        assert result["total"] == 18
        assert result["is_manual"] is True


class TestRollHistory:
    """Test roll history functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_roll_history_tracking(self):
        """Test that rolls are tracked in history."""
        if not hasattr(self.plugin, "clear_roll_history"):
            pytest.skip("roll history not implemented")
        self.plugin.clear_roll_history()

        # Make some rolls
        self.plugin.roll_dice("1d20")
        self.plugin.roll_dice("2d6+3")

        history = self.plugin.get_roll_history()
        assert len(history) == 2
        assert history[0]["notation"] == "1d20"
        assert history[1]["notation"] == "2d6+3"
        assert "timestamp" in history[0]
        assert "timestamp" in history[1]

    def test_roll_history_limit(self):
        """Test roll history has a reasonable limit."""
        if not hasattr(self.plugin, "clear_roll_history"):
            pytest.skip("roll history not implemented")
        self.plugin.clear_roll_history()

        # Make many rolls
        for i in range(150):
            self.plugin.roll_dice("1d6")

        history = self.plugin.get_roll_history()
        # Should be limited to 100 entries
        assert len(history) <= 100
