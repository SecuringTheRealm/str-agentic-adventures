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


class TestSpellEffectResolution:
    """Test spell effect resolution system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_calculate_spell_save_dc(self):
        """Test spell save DC calculation."""
        # Test with standard spellcaster stats
        result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=3,  # 16 ability score
            proficiency_bonus=2,  # Level 1-4
            character_level=3
        )
        assert result["save_dc"] == 13  # 8 + 3 + 2 = 13
        assert result["spellcasting_modifier"] == 3
        assert result["proficiency_bonus"] == 2
        
        # Test with higher level character
        result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=4,  # 18 ability score  
            proficiency_bonus=3,  # Level 5-8
            character_level=6
        )
        assert result["save_dc"] == 15  # 8 + 4 + 3 = 15
    
    def test_calculate_spell_attack_bonus(self):
        """Test spell attack bonus calculation."""
        result = self.plugin.calculate_spell_attack_bonus(
            spellcasting_ability_modifier=3,
            proficiency_bonus=2
        )
        assert result["attack_bonus"] == 5  # 3 + 2 = 5
        assert result["spellcasting_modifier"] == 3
        assert result["proficiency_bonus"] == 2
    
    def test_resolve_spell_damage(self):
        """Test spell damage resolution."""
        # Test basic damage spell
        result = self.plugin.resolve_spell_damage(
            dice_notation="3d6",  # Fireball at 3rd level
            damage_type="fire"
        )
        assert "total_damage" in result
        assert result["damage_type"] == "fire"
        assert "dice_rolls" in result
        assert 3 <= result["total_damage"] <= 18  # 3d6 range
        
        # Test damage with modifier
        result = self.plugin.resolve_spell_damage(
            dice_notation="1d4+3",  # Magic Missile
            damage_type="force"
        )
        assert result["damage_type"] == "force"
        assert 4 <= result["total_damage"] <= 7  # 1d4+3 range
    
    def test_resolve_spell_healing(self):
        """Test spell healing resolution."""
        result = self.plugin.resolve_spell_healing(
            dice_notation="1d8+3",  # Cure Wounds
            spellcasting_modifier=3
        )
        assert "healing_amount" in result
        assert result["spellcasting_modifier"] == 3
        assert 4 <= result["healing_amount"] <= 11  # 1d8+3 range
        
        # Test healing without explicit modifier (should use the one from dice notation)
        result = self.plugin.resolve_spell_healing(
            dice_notation="2d4+2"  # Healing Word
        )
        assert "healing_amount" in result
        assert 4 <= result["healing_amount"] <= 10  # 2d4+2 range
    
    def test_resolve_saving_throw(self):
        """Test saving throw resolution."""
        # Test successful save
        result = self.plugin.resolve_saving_throw(
            save_dc=13,
            ability_modifier=2,  # Dex modifier
            proficiency_bonus=2,  # Proficient in save
            is_proficient=True,
            roll_result=15  # Manual roll for consistency
        )
        assert result["save_successful"] is True
        assert result["total_roll"] == 19  # 15 + 2 + 2
        assert result["save_dc"] == 13
        
        # Test failed save
        result = self.plugin.resolve_saving_throw(
            save_dc=15,
            ability_modifier=1,
            proficiency_bonus=2,
            is_proficient=False,
            roll_result=8
        )
        assert result["save_successful"] is False
        assert result["total_roll"] == 9  # 8 + 1 (no proficiency)
        assert result["save_dc"] == 15
    
    def test_spell_effect_integration(self):
        """Test integration between different spell effect methods."""
        # Create a scenario: Level 5 wizard casting fireball
        wizard_int_mod = 4  # 18 Intelligence
        proficiency = 3     # Level 5
        
        # Calculate save DC
        save_dc_result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=wizard_int_mod,
            proficiency_bonus=proficiency,
            character_level=5
        )
        save_dc = save_dc_result["save_dc"]
        assert save_dc == 15  # 8 + 4 + 3
        
        # Resolve damage (5th level fireball)
        damage_result = self.plugin.resolve_spell_damage(
            dice_notation="8d6",  # 5th level fireball
            damage_type="fire"
        )
        assert "total_damage" in damage_result
        assert 8 <= damage_result["total_damage"] <= 48  # 8d6 range
        
        # Test saving throw against this DC
        save_result = self.plugin.resolve_saving_throw(
            save_dc=save_dc,
            ability_modifier=2,  # Dex save
            proficiency_bonus=proficiency,
            is_proficient=True,
            roll_result=10  # Manual roll
        )
        # 10 + 2 + 3 = 15, exactly meets DC
        assert save_result["save_successful"] is True
        assert save_result["total_roll"] == 15
    
    def test_spell_attack_integration(self):
        """Test spell attack integration."""
        # Test spell attack calculation
        attack_result = self.plugin.calculate_spell_attack_bonus(
            spellcasting_ability_modifier=3,
            proficiency_bonus=2
        )
        assert attack_result["attack_bonus"] == 5
        
        # Could simulate spell attack by rolling d20 + attack bonus
        # This would be done by calling roll_dice("1d20+5") in practice