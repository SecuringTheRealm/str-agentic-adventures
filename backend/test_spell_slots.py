"""
Tests for spell slot tracking functionality.
"""
from app.plugins.rules_engine_plugin import RulesEnginePlugin
from app.models.game_models import CharacterSheet, CharacterClass, Race, Abilities, HitPoints


class TestSpellSlotCalculation:
    """Test spell slot calculation for different classes and levels."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_wizard_spell_slots(self):
        """Test wizard spell slot calculation (full caster)."""
        # Level 1 wizard
        result = self.plugin.calculate_spell_slots("wizard", 1)
        assert "error" not in result
        assert result["character_class"] == "wizard"
        assert result["level"] == 1
        assert result["spellcasting_type"] == "full"
        assert result["spell_slots"] == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 5 wizard
        result = self.plugin.calculate_spell_slots("wizard", 5)
        assert result["spell_slots"] == [4, 3, 2, 0, 0, 0, 0, 0, 0]
        
        # Level 20 wizard
        result = self.plugin.calculate_spell_slots("wizard", 20)
        assert result["spell_slots"] == [4, 3, 3, 3, 3, 2, 2, 1, 1]

    def test_paladin_spell_slots(self):
        """Test paladin spell slot calculation (half caster)."""
        # Level 1 paladin (no spells yet)
        result = self.plugin.calculate_spell_slots("paladin", 1)
        assert result["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 2 paladin (first spells)
        result = self.plugin.calculate_spell_slots("paladin", 2)
        assert result["spellcasting_type"] == "half"
        assert result["spell_slots"] == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 20 paladin
        result = self.plugin.calculate_spell_slots("paladin", 20)
        assert result["spell_slots"] == [4, 3, 3, 3, 2, 0, 0, 0, 0]

    def test_warlock_spell_slots(self):
        """Test warlock spell slot calculation (pact magic)."""
        # Level 1 warlock
        result = self.plugin.calculate_spell_slots("warlock", 1)
        assert result["spellcasting_type"] == "pact"
        assert result["spell_slots"] == [1, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 3 warlock (2nd level slots)
        result = self.plugin.calculate_spell_slots("warlock", 3)
        assert result["spell_slots"] == [0, 2, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 11 warlock (3 5th level slots)
        result = self.plugin.calculate_spell_slots("warlock", 11)
        assert result["spell_slots"] == [0, 0, 0, 0, 3, 0, 0, 0, 0]

    def test_non_spellcaster(self):
        """Test non-spellcasting classes."""
        result = self.plugin.calculate_spell_slots("fighter", 10)
        assert result["spellcasting_type"] == "none"
        assert result["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        # Invalid class
        result = self.plugin.calculate_spell_slots("invalid", 5)
        assert "error" in result
        
        # Invalid level
        result = self.plugin.calculate_spell_slots("wizard", 25)
        assert "error" in result
        
        result = self.plugin.calculate_spell_slots("wizard", 0)
        assert "error" in result


class TestSpellSlotExpenditure:
    """Test spell slot expenditure and restoration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()
    
    def test_expend_spell_slot_success(self):
        """Test successful spell slot expenditure."""
        current_slots = [4, 3, 2, 0, 0, 0, 0, 0, 0]
        
        # Expend a 1st level slot
        result = self.plugin.expend_spell_slot(current_slots, 1)
        assert result["success"] == True
        assert result["slot_level"] == 1
        assert result["current_slots"] == [3, 3, 2, 0, 0, 0, 0, 0, 0]
        assert result["slots_remaining"] == 3
        
        # Expend a 2nd level slot
        result = self.plugin.expend_spell_slot(current_slots, 2)
        assert result["success"] == True
        assert result["current_slots"] == [4, 2, 2, 0, 0, 0, 0, 0, 0]

    def test_expend_spell_slot_failure(self):
        """Test spell slot expenditure when no slots available."""
        current_slots = [0, 0, 1, 0, 0, 0, 0, 0, 0]
        
        # Try to expend 1st level slot (none available)
        result = self.plugin.expend_spell_slot(current_slots, 1)
        assert result["success"] == False
        assert "error" in result
        assert result["current_slots"] == [0, 0, 1, 0, 0, 0, 0, 0, 0]

    def test_expend_invalid_slot_level(self):
        """Test expenditure with invalid slot level."""
        current_slots = [2, 1, 0, 0, 0, 0, 0, 0, 0]
        
        # Invalid slot level
        result = self.plugin.expend_spell_slot(current_slots, 10)
        assert result["success"] == False
        assert "error" in result

    def test_restore_spell_slots(self):
        """Test spell slot restoration after long rest."""
        max_slots = [4, 3, 3, 1, 0, 0, 0, 0, 0]
        
        result = self.plugin.restore_spell_slots(max_slots)
        assert result["success"] == True
        assert result["current_slots"] == [4, 3, 3, 1, 0, 0, 0, 0, 0]
        assert result["total_slots_restored"] == 11


class TestCharacterSheetSpellSlots:
    """Test spell slot integration with CharacterSheet model."""
    
    def test_character_sheet_spell_slot_fields(self):
        """Test that CharacterSheet includes spell slot fields."""
        abilities = Abilities(strength=10, dexterity=14, constitution=12, 
                            intelligence=16, wisdom=13, charisma=8)
        hit_points = HitPoints(current=8, maximum=8)
        
        character = CharacterSheet(
            name="Test Wizard",
            race=Race.HUMAN,
            character_class=CharacterClass.WIZARD,
            level=1,
            abilities=abilities,
            hit_points=hit_points
        )
        
        # Check that spell slot fields exist and have defaults
        assert hasattr(character, 'max_spell_slots')
        assert hasattr(character, 'current_spell_slots')
        assert character.max_spell_slots == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert character.current_spell_slots == [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_character_spell_slot_integration(self):
        """Test integration between spell slot calculation and character sheet."""
        abilities = Abilities(strength=10, dexterity=14, constitution=12, 
                            intelligence=16, wisdom=13, charisma=8)
        hit_points = HitPoints(current=20, maximum=20)
        
        character = CharacterSheet(
            name="Test Wizard",
            race=Race.HUMAN,
            character_class=CharacterClass.WIZARD,
            level=5,
            abilities=abilities,
            hit_points=hit_points
        )
        
        plugin = RulesEnginePlugin()
        
        # Calculate spell slots for the character
        spell_slot_result = plugin.calculate_spell_slots(
            character.character_class.value, 
            character.level
        )
        
        # Update character's spell slots
        character.max_spell_slots = spell_slot_result["spell_slots"]
        character.current_spell_slots = spell_slot_result["spell_slots"].copy()
        
        # Verify the slots are correct for a 5th level wizard
        assert character.max_spell_slots == [4, 3, 2, 0, 0, 0, 0, 0, 0]
        assert character.current_spell_slots == [4, 3, 2, 0, 0, 0, 0, 0, 0]
        
        # Test expending a slot
        expend_result = plugin.expend_spell_slot(character.current_spell_slots, 1)
        character.current_spell_slots = expend_result["current_slots"]
        
        assert character.current_spell_slots == [3, 3, 2, 0, 0, 0, 0, 0, 0]
        
        # Test restoration
        restore_result = plugin.restore_spell_slots(character.max_spell_slots)
        character.current_spell_slots = restore_result["current_slots"]
        
        assert character.current_spell_slots == character.max_spell_slots


class TestLevelUpSpellSlotIntegration:
    """Test spell slot integration with character level-up process."""
    
    def test_level_up_spell_slot_update_wizard(self):
        """Test that spell slots are properly updated when a wizard levels up."""
        plugin = RulesEnginePlugin()
        
        # Simulate level 1 wizard data
        character_data = {
            "character_class": "wizard",
            "level": 1,
            "max_spell_slots": [2, 0, 0, 0, 0, 0, 0, 0, 0],
            "current_spell_slots": [1, 0, 0, 0, 0, 0, 0, 0, 0],  # Used 1 slot
        }
        
        # Calculate new spell slots for level 3 (gains 2nd level spells)
        new_level = 3
        spell_slot_result = plugin.calculate_spell_slots("wizard", new_level)
        
        assert "error" not in spell_slot_result
        new_spell_slots = spell_slot_result["spell_slots"]
        assert new_spell_slots == [4, 2, 0, 0, 0, 0, 0, 0, 0]
        
        # Simulate level-up spell slot update logic
        old_max_spell_slots = character_data["max_spell_slots"]
        old_current_spell_slots = character_data["current_spell_slots"]
        
        new_current_spell_slots = []
        for i in range(9):
            # Keep existing current slots up to the new maximum
            current_slots = min(old_current_spell_slots[i], new_spell_slots[i])
            # Add any new spell slots gained at this level
            if new_spell_slots[i] > old_max_spell_slots[i]:
                current_slots += (new_spell_slots[i] - old_max_spell_slots[i])
            new_current_spell_slots.append(current_slots)
        
        # Verify the update logic
        assert new_current_spell_slots == [3, 2, 0, 0, 0, 0, 0, 0, 0]  # 1+2 level 1 slots, 2 new level 2 slots

    def test_level_up_spell_slot_update_paladin(self):
        """Test that spell slots are properly updated when a paladin levels up."""
        plugin = RulesEnginePlugin()
        
        # Simulate level 1 paladin data (no spells yet)
        character_data = {
            "character_class": "paladin",
            "level": 1,
            "max_spell_slots": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "current_spell_slots": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        
        # Calculate new spell slots for level 2 (gains first spells)
        new_level = 2
        spell_slot_result = plugin.calculate_spell_slots("paladin", new_level)
        
        assert "error" not in spell_slot_result
        new_spell_slots = spell_slot_result["spell_slots"]
        assert new_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]  # Half-caster table, padded to 9
        
        # Simulate level-up spell slot update logic
        old_max_spell_slots = character_data["max_spell_slots"]
        old_current_spell_slots = character_data["current_spell_slots"]
        
        new_current_spell_slots = []
        for i in range(9):
            # Keep existing current slots up to the new maximum
            current_slots = min(old_current_spell_slots[i], new_spell_slots[i])
            # Add any new spell slots gained at this level
            if new_spell_slots[i] > old_max_spell_slots[i]:
                current_slots += (new_spell_slots[i] - old_max_spell_slots[i])
            new_current_spell_slots.append(current_slots)
        
        # Verify the update logic - should gain 2 first level slots
        assert new_current_spell_slots[:5] == [2, 0, 0, 0, 0]

    def test_level_up_non_spellcaster(self):
        """Test that non-spellcasters don't get spell slots."""
        plugin = RulesEnginePlugin()
        
        # Test with fighter (non-spellcaster)
        spell_slot_result = plugin.calculate_spell_slots("fighter", 5)
        
        assert "error" not in spell_slot_result
        assert spell_slot_result["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert spell_slot_result["spellcasting_type"] == "none"