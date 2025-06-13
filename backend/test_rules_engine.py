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


class TestSpellcasting:
    """Test spell save DC and spell attack bonus calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_spell_save_dc_cleric(self):
        """Test spell save DC calculation for Cleric (Wisdom-based)."""
        # Cleric level 5 with 16 Wisdom (modifier +3) and proficiency +3
        result = self.plugin.calculate_spell_save_dc("Cleric", 16, 5)
        
        assert result["can_cast_spells"] is True
        assert result["character_class"] == "Cleric"
        assert result["level"] == 5
        assert result["spellcasting_ability"] == "wisdom"
        assert result["spellcasting_ability_score"] == 16
        assert result["ability_modifier"] == 3
        assert result["proficiency_bonus"] == 3
        assert result["spell_save_dc"] == 14  # 8 + 3 + 3
    
    def test_spell_save_dc_wizard(self):
        """Test spell save DC calculation for Wizard (Intelligence-based)."""
        # Wizard level 10 with 18 Intelligence (modifier +4) and proficiency +4  
        result = self.plugin.calculate_spell_save_dc("Wizard", 18, 10)
        
        assert result["can_cast_spells"] is True
        assert result["character_class"] == "Wizard"
        assert result["level"] == 10
        assert result["spellcasting_ability"] == "intelligence"
        assert result["spellcasting_ability_score"] == 18
        assert result["ability_modifier"] == 4
        assert result["proficiency_bonus"] == 4
        assert result["spell_save_dc"] == 16  # 8 + 4 + 4
    
    def test_spell_save_dc_sorcerer(self):
        """Test spell save DC calculation for Sorcerer (Charisma-based)."""
        # Sorcerer level 1 with 14 Charisma (modifier +2) and proficiency +2
        result = self.plugin.calculate_spell_save_dc("Sorcerer", 14, 1)
        
        assert result["can_cast_spells"] is True
        assert result["character_class"] == "Sorcerer"
        assert result["level"] == 1
        assert result["spellcasting_ability"] == "charisma"
        assert result["spellcasting_ability_score"] == 14
        assert result["ability_modifier"] == 2
        assert result["proficiency_bonus"] == 2
        assert result["spell_save_dc"] == 12  # 8 + 2 + 2
    
    def test_spell_save_dc_non_spellcaster(self):
        """Test spell save DC calculation for non-spellcasting class."""
        result = self.plugin.calculate_spell_save_dc("Fighter", 16, 5)
        
        assert result["can_cast_spells"] is False
        assert "error" in result
        assert "not a spellcasting class" in result["error"]
    
    def test_spell_attack_bonus_warlock(self):
        """Test spell attack bonus calculation for Warlock (Charisma-based)."""
        # Warlock level 8 with 18 Charisma (modifier +4) and proficiency +3
        result = self.plugin.calculate_spell_attack_bonus("Warlock", 18, 8)
        
        assert result["can_cast_spells"] is True
        assert result["character_class"] == "Warlock"
        assert result["level"] == 8
        assert result["spellcasting_ability"] == "charisma"
        assert result["spellcasting_ability_score"] == 18
        assert result["ability_modifier"] == 4
        assert result["proficiency_bonus"] == 3
        assert result["spell_attack_bonus"] == 7  # 4 + 3
    
    def test_spell_attack_bonus_druid(self):
        """Test spell attack bonus calculation for Druid (Wisdom-based)."""
        # Druid level 13 with 20 Wisdom (modifier +5) and proficiency +5
        result = self.plugin.calculate_spell_attack_bonus("Druid", 20, 13)
        
        assert result["can_cast_spells"] is True
        assert result["character_class"] == "Druid"
        assert result["level"] == 13
        assert result["spellcasting_ability"] == "wisdom"
        assert result["spellcasting_ability_score"] == 20
        assert result["ability_modifier"] == 5
        assert result["proficiency_bonus"] == 5
        assert result["spell_attack_bonus"] == 10  # 5 + 5
    
    def test_spell_attack_bonus_case_insensitive(self):
        """Test that class names are case-insensitive."""
        result = self.plugin.calculate_spell_attack_bonus("BARD", 16, 3)
        
        assert result["can_cast_spells"] is True
        assert result["spellcasting_ability"] == "charisma"
        assert result["ability_modifier"] == 3
        assert result["proficiency_bonus"] == 2
        assert result["spell_attack_bonus"] == 5  # 3 + 2
    
    def test_spell_attack_bonus_non_spellcaster(self):
        """Test spell attack bonus calculation for non-spellcasting class."""
        result = self.plugin.calculate_spell_attack_bonus("Barbarian", 16, 5)
        
        assert result["can_cast_spells"] is False
        assert "error" in result
        assert "not a spellcasting class" in result["error"]
    
    def test_spell_calculations_with_low_ability_score(self):
        """Test spell calculations with low ability scores (negative modifiers)."""
        # Wizard with 8 Intelligence (modifier -1)
        result = self.plugin.calculate_spell_save_dc("Wizard", 8, 1)
        
        assert result["ability_modifier"] == -1
        assert result["proficiency_bonus"] == 2
        assert result["spell_save_dc"] == 9  # 8 + (-1) + 2
        
        attack_result = self.plugin.calculate_spell_attack_bonus("Wizard", 8, 1)
        assert attack_result["spell_attack_bonus"] == 1  # -1 + 2