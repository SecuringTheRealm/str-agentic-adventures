"""
Tests for the enhanced Rules Engine Plugin.
"""

import pytest
from app.plugins.rules_engine_plugin import RulesEnginePlugin


class TestDiceRolling:
    """Test enhanced dice rolling functionality."""

    @pytest.mark.unit
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_basic_dice_notation(self) -> None:
        """Test basic dice notation still works."""
        result = self.plugin.roll_dice("1d20")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 1
        assert 1 <= result["rolls"][0] <= 20
        assert result["total"] == result["rolls"][0]

    def test_dice_with_modifier(self) -> None:
        """Test dice with positive and negative modifiers."""
        result = self.plugin.roll_dice("1d20+5")
        assert result["modifier"] == 5
        assert result["total"] == result["rolls"][0] + 5

        result = self.plugin.roll_dice("2d6-2")
        assert result["modifier"] == -2
        assert result["total"] == sum(result["rolls"]) - 2

    def test_drop_lowest_notation(self) -> None:
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

    def test_keep_highest_notation(self) -> None:
        """Test advanced notation: keep highest (advantage)."""
        result = self.plugin.roll_dice("2d20kh1")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 2
        assert "dropped" in result
        assert len(result["dropped"]) == 1
        # Total should be the highest roll
        assert result["total"] == max(result["rolls"])

    def test_keep_lowest_notation(self) -> None:
        """Test advanced notation: keep lowest (disadvantage)."""
        result = self.plugin.roll_dice("2d20kl1")
        assert "total" in result
        assert "rolls" in result
        assert len(result["rolls"]) == 2
        assert "dropped" in result
        assert len(result["dropped"]) == 1
        # Total should be the lowest roll
        assert result["total"] == min(result["rolls"])

    def test_reroll_notation(self) -> None:
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
        reroll_results = [
            r for r in results if "rerolls" in r and len(r["rerolls"]) > 0
        ]
        assert len(reroll_results) > 0  # Should have some rerolls in 100 attempts

    def test_multiple_dice_pools(self) -> None:
        """Test multiple dice pools in one expression."""
        result = self.plugin.roll_dice("2d6+1d4+3")
        assert "total" in result
        assert "pools" in result
        assert len(result["pools"]) == 3  # 2d6, 1d4, and +3

        # Verify the total is correct
        expected_total = (
            sum(result["pools"][0]["rolls"])
            + sum(result["pools"][1]["rolls"])
            + result["pools"][2]["value"]
        )
        assert result["total"] == expected_total


class TestCharacterIntegration:
    """Test character sheet integration features."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_roll_with_character_context(self) -> None:
        """Test rolling with character context for automatic modifiers."""
        character = {
            "abilities": {"strength": 16, "dexterity": 14},
            "proficiency_bonus": 3,
            "proficiencies": ["athletics", "stealth"],
        }

        result = self.plugin.roll_with_character("1d20", character, "athletics")
        assert "character_bonus" in result
        assert "total" in result
        # Should include STR modifier (3) + proficiency (3) = 6
        expected_bonus = 3 + 3  # STR mod + prof
        assert result["character_bonus"] == expected_bonus

    def test_manual_roll_input(self) -> None:
        """Test manual roll input functionality."""
        result = self.plugin.input_manual_roll("1d20", 18)
        assert result["notation"] == "1d20"
        assert result["manual_result"] == 18
        assert result["total"] == 18
        assert result["is_manual"] is True


class TestRollHistory:
    """Test roll history functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    def test_roll_history_tracking(self) -> None:
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

    def test_roll_history_limit(self) -> None:
        """Test roll history has a reasonable limit."""
        self.plugin.clear_roll_history()

        # Make many rolls
        for _i in range(150):
            self.plugin.roll_dice("1d6")

        history = self.plugin.get_roll_history()
        # Should be limited to 100 entries
        assert len(history) <= 100


class TestConcentrationTracking:
    """Test concentration tracking functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

        # Sample spell data
        self.concentration_spell = {
            "name": "Hold Person",
            "level": 2,
            "school": "enchantment",
            "requires_concentration": True,
        }

        self.non_concentration_spell = {
            "name": "Magic Missile",
            "level": 1,
            "school": "evocation",
            "requires_concentration": False,
        }

    def test_start_concentration_success(self) -> None:
        """Test successfully starting concentration on a spell."""
        result = self.plugin.start_concentration("char1", self.concentration_spell, 10)

        assert result["success"] is True
        assert result["character_id"] == "char1"
        assert result["spell"] == "Hold Person"
        assert result["duration_rounds"] == 10
        assert "message" in result

    def test_start_concentration_non_concentration_spell(self) -> None:
        """Test starting concentration on a spell that doesn't require it."""
        result = self.plugin.start_concentration("char1", self.non_concentration_spell)

        assert result["success"] is False
        assert "does not require concentration" in result["error"]

    def test_start_concentration_replaces_existing(self) -> None:
        """Test that starting new concentration ends existing concentration."""
        # Start first concentration
        self.plugin.start_concentration("char1", self.concentration_spell)

        # Start second concentration
        second_spell = {"name": "Blur", "level": 2, "requires_concentration": True}
        result = self.plugin.start_concentration("char1", second_spell)

        assert result["success"] is True
        assert result["spell"] == "Blur"

        # Check that only the new spell is active
        status = self.plugin.check_concentration("char1")
        assert status["spell"]["name"] == "Blur"

    def test_check_concentration_active(self) -> None:
        """Test checking concentration when character is concentrating."""
        self.plugin.start_concentration("char1", self.concentration_spell, 5)

        result = self.plugin.check_concentration("char1")

        assert result["is_concentrating"] is True
        assert result["character_id"] == "char1"
        assert result["spell"]["name"] == "Hold Person"
        assert result["duration_remaining"] == 5
        assert "started_at" in result

    def test_check_concentration_inactive(self) -> None:
        """Test checking concentration when character is not concentrating."""
        result = self.plugin.check_concentration("char1")

        assert result["is_concentrating"] is False
        assert result["character_id"] == "char1"
        assert result["spell"] is None
        assert result["duration_remaining"] == 0

    def test_end_concentration_success(self) -> None:
        """Test successfully ending concentration."""
        self.plugin.start_concentration("char1", self.concentration_spell)

        result = self.plugin.end_concentration("char1")

        assert result["success"] is True
        assert result["character_id"] == "char1"
        assert result["spell"] == "Hold Person"
        assert "ended" in result["message"]

        # Verify concentration is actually ended
        status = self.plugin.check_concentration("char1")
        assert status["is_concentrating"] is False

    def test_end_concentration_not_concentrating(self) -> None:
        """Test ending concentration when not concentrating."""
        result = self.plugin.end_concentration("char1")

        assert result["success"] is False
        assert "not concentrating" in result["error"]

    def test_concentration_saving_throw_success(self) -> None:
        """Test successful concentration saving throw."""
        self.plugin.start_concentration("char1", self.concentration_spell)

        # Mock a high roll by testing multiple times (probabilistic)
        # We'll test the mechanics directly
        damage = 10  # should be max(10, 10//2) = 10
        constitution_mod = 3

        result = self.plugin.concentration_saving_throw(
            "char1", damage, constitution_mod
        )

        assert "character_id" in result
        assert result["spell"] == "Hold Person"
        assert result["damage_taken"] == 10
        assert result["dc"] == 10
        assert result["constitution_modifier"] == 3
        assert "roll" in result
        assert "total" in result
        assert "success" in result
        assert "concentration_maintained" in result

    def test_concentration_saving_throw_dc_calculation(self) -> None:
        """Test concentration saving throw DC calculation."""
        self.plugin.start_concentration("char1", self.concentration_spell)

        # Test low damage (DC should be 10)
        result1 = self.plugin.concentration_saving_throw("char1", 5, 0)
        assert result1["dc"] == 10

        # Reset concentration
        self.plugin.start_concentration("char1", self.concentration_spell)

        # Test high damage (DC should be half damage)
        result2 = self.plugin.concentration_saving_throw("char1", 30, 0)
        assert result2["dc"] == 15  # 30 // 2

    def test_concentration_saving_throw_not_concentrating(self) -> None:
        """Test concentration saving throw when not concentrating."""
        result = self.plugin.concentration_saving_throw("char1", 10, 0)

        assert result["success"] is False
        assert "not concentrating" in result["error"]

    def test_advance_concentration_round(self) -> None:
        """Test advancing concentration rounds."""
        # Set up multiple characters with concentration
        self.plugin.start_concentration("char1", self.concentration_spell, 3)
        self.plugin.start_concentration(
            "char2", {"name": "Bless", "requires_concentration": True}, 2
        )  # Changed from 1 to 2 to avoid immediate expiration

        result = self.plugin.advance_concentration_round()

        assert result["success"] is True
        assert len(result["continuing_spells"]) == 2
        assert len(result["expired_spells"]) == 0
        assert result["total_concentrating"] == 2

        # Check that durations were reduced
        char1_status = self.plugin.check_concentration("char1")
        assert char1_status["duration_remaining"] == 2

        char2_status = self.plugin.check_concentration("char2")
        assert char2_status["duration_remaining"] == 1

        # Advance one more round to expire char2's spell
        result2 = self.plugin.advance_concentration_round()
        assert len(result2["expired_spells"]) == 1
        assert result2["expired_spells"][0]["character_id"] == "char2"
        assert len(result2["continuing_spells"]) == 1

        # Verify char2 is no longer concentrating
        char2_status_after = self.plugin.check_concentration("char2")
        assert char2_status_after["is_concentrating"] is False


class TestSpellEffectResolution:
    """Test spell effect resolution system."""

    @pytest.mark.integration
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    @pytest.mark.integration
    def test_calculate_spell_save_dc(self) -> None:
        """Test spell save DC calculation."""
        # Test with standard spellcaster stats
        result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=3,  # 16 ability score
            proficiency_bonus=2,  # Level 1-4
            character_level=3,
        )
        assert result["save_dc"] == 13  # 8 + 3 + 2 = 13
        assert result["spellcasting_modifier"] == 3
        assert result["proficiency_bonus"] == 2

        # Test with higher level character
        result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=4,  # 18 ability score
            proficiency_bonus=3,  # Level 5-8
            character_level=6,
        )
        assert result["save_dc"] == 15  # 8 + 4 + 3 = 15

    def test_calculate_spell_attack_bonus(self) -> None:
        """Test spell attack bonus calculation."""
        result = self.plugin.calculate_spell_attack_bonus(
            spellcasting_ability_modifier=3, proficiency_bonus=2
        )
        assert result["attack_bonus"] == 5  # 3 + 2 = 5
        assert result["spellcasting_modifier"] == 3
        assert result["proficiency_bonus"] == 2

    def test_resolve_spell_damage(self) -> None:
        """Test spell damage resolution."""
        # Test basic damage spell
        result = self.plugin.resolve_spell_damage(
            dice_notation="3d6",  # Fireball at 3rd level
            damage_type="fire",
        )
        assert "total_damage" in result
        assert result["damage_type"] == "fire"
        assert "dice_rolls" in result
        assert 3 <= result["total_damage"] <= 18  # 3d6 range

        # Test damage with modifier
        result = self.plugin.resolve_spell_damage(
            dice_notation="1d4+3",  # Magic Missile
            damage_type="force",
        )
        assert result["damage_type"] == "force"
        assert 4 <= result["total_damage"] <= 7  # 1d4+3 range

    def test_resolve_spell_healing(self) -> None:
        """Test spell healing resolution."""
        result = self.plugin.resolve_spell_healing(
            dice_notation="1d8+3",  # Cure Wounds
            spellcasting_modifier=3,
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

    def test_resolve_saving_throw(self) -> None:
        """Test saving throw resolution."""
        # Test successful save
        result = self.plugin.resolve_saving_throw(
            save_dc=13,
            ability_modifier=2,  # Dex modifier
            proficiency_bonus=2,  # Proficient in save
            is_proficient=True,
            roll_result=15,  # Manual roll for consistency
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
            roll_result=8,
        )
        assert result["save_successful"] is False
        assert result["total_roll"] == 9  # 8 + 1 (no proficiency)
        assert result["save_dc"] == 15

    def test_spell_effect_integration(self) -> None:
        """Test integration between different spell effect methods."""
        # Create a scenario: Level 5 wizard casting fireball
        wizard_int_mod = 4  # 18 Intelligence
        proficiency = 3  # Level 5

        # Calculate save DC
        save_dc_result = self.plugin.calculate_spell_save_dc(
            spellcasting_ability_modifier=wizard_int_mod,
            proficiency_bonus=proficiency,
            character_level=5,
        )
        save_dc = save_dc_result["save_dc"]
        assert save_dc == 15  # 8 + 4 + 3

        # Resolve damage (5th level fireball)
        damage_result = self.plugin.resolve_spell_damage(
            dice_notation="8d6",  # 5th level fireball
            damage_type="fire",
        )
        assert "total_damage" in damage_result
        assert 8 <= damage_result["total_damage"] <= 48  # 8d6 range

        # Test saving throw against this DC
        save_result = self.plugin.resolve_saving_throw(
            save_dc=save_dc,
            ability_modifier=2,  # Dex save
            proficiency_bonus=proficiency,
            is_proficient=True,
            roll_result=10,  # Manual roll
        )
        # 10 + 2 + 3 = 15, exactly meets DC
        assert save_result["save_successful"] is True
        assert save_result["total_roll"] == 15

    def test_spell_attack_integration(self) -> None:
        """Test spell attack integration."""
        # Test spell attack calculation
        attack_result = self.plugin.calculate_spell_attack_bonus(
            spellcasting_ability_modifier=3, proficiency_bonus=2
        )
        assert attack_result["attack_bonus"] == 5

        # Could simulate spell attack by rolling d20 + attack bonus
        # This would be done by calling roll_dice("1d20+5") in practice
