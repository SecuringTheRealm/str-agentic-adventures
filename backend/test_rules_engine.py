"""
Tests for the enhanced Rules Engine Plugin.
"""
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
        """Test advanced notation: drop lowest."""
        result = self.plugin.roll_dice("4d6dl1")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 4
        assert "dropped" in result
        assert len(result["dropped"]) == 1
        # Total should be sum of 3 highest rolls
        sorted_rolls = sorted(result["rolls"], reverse=True)
        expected_total = sum(sorted_rolls[:3])
        assert result["total"] == expected_total
    
    def test_keep_highest_notation(self):
        """Test advanced notation: keep highest (advantage)."""
        result = self.plugin.roll_dice("2d20kh1")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 2
        assert "dropped" in result
        assert len(result["dropped"]) == 1
        # Total should be the highest roll
        assert result["total"] == max(result["rolls"])
    
    def test_keep_lowest_notation(self):
        """Test advanced notation: keep lowest (disadvantage)."""
        result = self.plugin.roll_dice("2d20kl1")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 2
        assert "dropped" in result
        assert len(result["dropped"]) == 1
        # Total should be the lowest roll
        assert result["total"] == min(result["rolls"])
    
    def test_reroll_notation(self):
        """Test reroll notation."""
        # This test is probabilistic, so we'll run it multiple times
        # to ensure the reroll functionality works
        results = []
        for _ in range(100):
            result = self.plugin.roll_dice("1d6r1")
            results.append(result)
        
        # Check that we never have a final result of 1 (should be rerolled)
        final_rolls = [r["total"] for r in results]
        assert 1 not in final_rolls
        
        # Check that some results have reroll information
        reroll_results = [r for r in results if "rerolls" in r and len(r["rerolls"]) > 0]
        assert len(reroll_results) > 0  # Should have some rerolls in 100 attempts
    
    def test_multiple_dice_pools(self):
        """Test multiple dice pools in one expression."""
        result = self.plugin.roll_dice("2d6+1d4+3")
        assert "total" in result
        assert "pools" in result
        assert len(result["pools"]) == 3  # 2d6, 1d4, and +3
        
        # Verify the total is correct
        expected_total = (sum(result["pools"][0]["rolls"]) + 
                         sum(result["pools"][1]["rolls"]) + 
                         result["pools"][2]["value"])
        assert result["total"] == expected_total


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
            "proficiencies": ["athletics", "stealth"]
        }
        
        result = self.plugin.roll_with_character("1d20", character, "athletics")
        assert "character_bonus" in result
        assert "total" in result
        # Should include STR modifier (3) + proficiency (3) = 6
        expected_bonus = 3 + 3  # STR mod + prof
        assert result["character_bonus"] == expected_bonus
    
    def test_manual_roll_input(self):
        """Test manual roll input functionality."""
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
        # Clear any existing history
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
        self.plugin.clear_roll_history()
        
        # Make many rolls
        for i in range(150):
            self.plugin.roll_dice("1d6")
        
        history = self.plugin.get_roll_history()
        # Should be limited to 100 entries
        assert len(history) <= 100


class TestSpellSaveDC:
    """Test spell save DC calculation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_wizard_spell_save_dc(self):
        """Test spell save DC calculation for a wizard."""
        abilities = {
            "strength": 10,
            "dexterity": 14,
            "constitution": 16,
            "intelligence": 18,  # Primary spellcasting ability
            "wisdom": 12,
            "charisma": 8
        }
        
        result = self.plugin.calculate_spell_save_dc("wizard", 5, abilities)
        
        assert "error" not in result
        assert result["spellcasting_ability"] == "intelligence"
        assert result["ability_score"] == 18
        assert result["ability_modifier"] == 4  # (18-10)//2 = 4
        assert result["proficiency_bonus"] == 3  # Level 5 = +3
        assert result["spell_save_dc"] == 15  # 8 + 3 + 4 = 15
        assert result["level"] == 5
        assert result["character_class"] == "wizard"
    
    def test_cleric_spell_save_dc(self):
        """Test spell save DC calculation for a cleric."""
        abilities = {
            "strength": 14,
            "dexterity": 10,
            "constitution": 16,
            "intelligence": 12,
            "wisdom": 16,  # Primary spellcasting ability
            "charisma": 13
        }
        
        result = self.plugin.calculate_spell_save_dc("cleric", 1, abilities)
        
        assert "error" not in result
        assert result["spellcasting_ability"] == "wisdom"
        assert result["ability_score"] == 16
        assert result["ability_modifier"] == 3  # (16-10)//2 = 3
        assert result["proficiency_bonus"] == 2  # Level 1 = +2
        assert result["spell_save_dc"] == 13  # 8 + 2 + 3 = 13
    
    def test_sorcerer_spell_save_dc(self):
        """Test spell save DC calculation for a sorcerer."""
        abilities = {
            "strength": 8,
            "dexterity": 15,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 17  # Primary spellcasting ability
        }
        
        result = self.plugin.calculate_spell_save_dc("sorcerer", 9, abilities)
        
        assert "error" not in result
        assert result["spellcasting_ability"] == "charisma"
        assert result["ability_score"] == 17
        assert result["ability_modifier"] == 3  # (17-10)//2 = 3
        assert result["proficiency_bonus"] == 4  # Level 9 = +4
        assert result["spell_save_dc"] == 15  # 8 + 4 + 3 = 15
    
    def test_non_spellcaster_class(self):
        """Test spell save DC calculation for non-spellcasting classes."""
        abilities = {
            "strength": 18,
            "dexterity": 14,
            "constitution": 16,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8
        }
        
        result = self.plugin.calculate_spell_save_dc("barbarian", 5, abilities)
        
        assert "error" in result
        assert result["spell_save_dc"] is None
        assert result["spellcasting_ability"] is None
        assert "does not have innate spellcasting ability" in result["error"]
    
    def test_missing_ability_score(self):
        """Test spell save DC calculation with missing ability score."""
        abilities = {
            "strength": 16,
            "dexterity": 14,
            "constitution": 16,
            # Missing intelligence
            "wisdom": 12,
            "charisma": 8
        }
        
        result = self.plugin.calculate_spell_save_dc("wizard", 3, abilities)
        
        assert "error" in result
        assert result["spell_save_dc"] is None
        assert "Missing ability score for intelligence" in result["error"]
    
    def test_edge_case_low_ability_score(self):
        """Test spell save DC calculation with very low spellcasting ability."""
        abilities = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 6,  # Very low intelligence
            "wisdom": 10,
            "charisma": 10
        }
        
        result = self.plugin.calculate_spell_save_dc("wizard", 1, abilities)
        
        assert "error" not in result
        assert result["ability_modifier"] == -2  # (6-10)//2 = -2
        assert result["spell_save_dc"] == 8  # 8 + 2 + (-2) = 8
    
    def test_high_level_character(self):
        """Test spell save DC calculation for high-level character."""
        abilities = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 20,  # Maxed intelligence
            "wisdom": 10,
            "charisma": 10
        }
        
        result = self.plugin.calculate_spell_save_dc("wizard", 17, abilities)
        
        assert "error" not in result
        assert result["ability_modifier"] == 5  # (20-10)//2 = 5
        assert result["proficiency_bonus"] == 6  # Level 17 = +6
        assert result["spell_save_dc"] == 19  # 8 + 6 + 5 = 19