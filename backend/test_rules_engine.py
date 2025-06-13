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


class TestConcentrationChecks:
    """Test concentration check functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_concentration_check_basic_dc_calculation(self):
        """Test basic concentration check DC calculation."""
        # Test with low damage (DC should be 10)
        result = self.plugin.concentration_check(
            damage_taken=5,
            constitution_score=14,  # +2 modifier
            proficient_in_constitution=False,
            proficiency_bonus=2
        )
        
        assert result["dc"] == 10  # max(10, 5//2) = max(10, 2) = 10
        assert result["constitution_modifier"] == 2
        assert result["total_modifier"] == 2  # Only CON modifier, no proficiency
        assert "success" in result
        assert "concentration_maintained" in result
        assert result["concentration_maintained"] == result["success"]
    
    def test_concentration_check_high_damage_dc(self):
        """Test concentration check with high damage affecting DC."""
        # Test with high damage (DC should be half damage)
        result = self.plugin.concentration_check(
            damage_taken=30,
            constitution_score=16,  # +3 modifier
            proficient_in_constitution=True,
            proficiency_bonus=3
        )
        
        assert result["dc"] == 15  # max(10, 30//2) = max(10, 15) = 15
        assert result["constitution_modifier"] == 3
        assert result["total_modifier"] == 6  # CON modifier + proficiency
        assert result["proficiency_bonus"] == 3
    
    def test_concentration_check_war_caster_advantage(self):
        """Test concentration check with War Caster feat granting advantage."""
        result = self.plugin.concentration_check(
            damage_taken=20,
            constitution_score=12,  # +1 modifier
            proficient_in_constitution=True,
            proficiency_bonus=2,
            war_caster_feat=True
        )
        
        assert result["war_caster_feat"] is True
        assert result["advantage_type"] == "advantage"
        assert len(result["rolls"]) == 2  # Should roll two dice for advantage
        assert result["total"] == max(result["rolls"]) + result["total_modifier"]
    
    def test_concentration_check_advantage_disadvantage_mechanics(self):
        """Test advantage and disadvantage mechanics in concentration checks."""
        # Test with explicit advantage
        result_adv = self.plugin.concentration_check(
            damage_taken=10,
            constitution_score=14,
            advantage=True
        )
        assert result_adv["advantage_type"] == "advantage"
        assert len(result_adv["rolls"]) == 2
        
        # Test with disadvantage
        result_dis = self.plugin.concentration_check(
            damage_taken=10,
            constitution_score=14,
            disadvantage=True
        )
        assert result_dis["advantage_type"] == "disadvantage"
        assert len(result_dis["rolls"]) == 2
        
        # Test that War Caster overrides disadvantage
        result_war_caster = self.plugin.concentration_check(
            damage_taken=10,
            constitution_score=14,
            war_caster_feat=True,
            disadvantage=True
        )
        assert result_war_caster["advantage_type"] == "advantage"