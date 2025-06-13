"""
Integration tests for spell slot tracking with character progression.
Tests the complete workflow from character creation to spell slot management.
"""

import pytest
from app.models.game_models import CharacterSheet, CharacterClass, Race, Abilities, HitPoints
from app.plugins.rules_engine_plugin import RulesEnginePlugin


class TestSpellSlotIntegration:
    """Test complete integration of spell slot system with character progression."""
    
    def test_complete_wizard_progression(self):
        """Test complete wizard progression from level 1 to 5 with spell slots."""
        plugin = RulesEnginePlugin()
        
        # Create a level 1 wizard
        abilities = Abilities(strength=8, dexterity=14, constitution=13, 
                            intelligence=16, wisdom=12, charisma=10)
        hit_points = HitPoints(current=8, maximum=8)
        
        wizard = CharacterSheet(
            name="Gandalf the Grey",
            race=Race.HUMAN,
            character_class=CharacterClass.WIZARD,
            level=1,
            abilities=abilities,
            hit_points=hit_points
        )
        
        # Initialize spell slots for level 1
        level_1_slots = plugin.calculate_spell_slots("wizard", 1)
        wizard.max_spell_slots = level_1_slots["spell_slots"]
        wizard.current_spell_slots = level_1_slots["spell_slots"].copy()
        
        # Verify level 1 wizard spell slots
        assert wizard.max_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        assert wizard.current_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Cast a spell (expend a 1st level slot)
        expend_result = plugin.expend_spell_slot(wizard.current_spell_slots, 1)
        wizard.current_spell_slots = expend_result["current_slots"]
        assert wizard.current_spell_slots == [1, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level up to 2
        wizard.level = 2
        level_2_slots = plugin.calculate_spell_slots("wizard", 2)
        old_max = wizard.max_spell_slots.copy()
        wizard.max_spell_slots = level_2_slots["spell_slots"]
        
        # Update current slots (simulate level-up logic)
        new_current_slots = []
        for i in range(9):
            current_slots = min(wizard.current_spell_slots[i], wizard.max_spell_slots[i])
            if wizard.max_spell_slots[i] > old_max[i]:
                current_slots += (wizard.max_spell_slots[i] - old_max[i])
            new_current_slots.append(current_slots)
        wizard.current_spell_slots = new_current_slots
        
        # Verify level 2 wizard gets one more 1st level slot
        assert wizard.max_spell_slots == [3, 0, 0, 0, 0, 0, 0, 0, 0]
        assert wizard.current_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]  # 1 used + 1 new = 2
        
        # Level up to 3 (gains 2nd level spells)
        wizard.level = 3
        level_3_slots = plugin.calculate_spell_slots("wizard", 3)
        old_max = wizard.max_spell_slots.copy()
        wizard.max_spell_slots = level_3_slots["spell_slots"]
        
        # Update current slots
        new_current_slots = []
        for i in range(9):
            current_slots = min(wizard.current_spell_slots[i], wizard.max_spell_slots[i])
            if wizard.max_spell_slots[i] > old_max[i]:
                current_slots += (wizard.max_spell_slots[i] - old_max[i])
            new_current_slots.append(current_slots)
        wizard.current_spell_slots = new_current_slots
        
        # Verify level 3 wizard gets 2nd level spells and more 1st level slots
        assert wizard.max_spell_slots == [4, 2, 0, 0, 0, 0, 0, 0, 0]
        assert wizard.current_spell_slots == [3, 2, 0, 0, 0, 0, 0, 0, 0]
        
        # Cast a 2nd level spell
        expend_result = plugin.expend_spell_slot(wizard.current_spell_slots, 2)
        wizard.current_spell_slots = expend_result["current_slots"]
        assert wizard.current_spell_slots == [3, 1, 0, 0, 0, 0, 0, 0, 0]
        
        # Take a long rest (restore all spell slots)
        restore_result = plugin.restore_spell_slots(wizard.max_spell_slots)
        wizard.current_spell_slots = restore_result["current_slots"]
        assert wizard.current_spell_slots == wizard.max_spell_slots

    def test_paladin_spell_progression(self):
        """Test paladin spell progression (half-caster)."""
        plugin = RulesEnginePlugin()
        
        # Create a level 1 paladin (no spells yet)
        abilities = Abilities(strength=16, dexterity=10, constitution=14, 
                            intelligence=8, wisdom=12, charisma=13)
        hit_points = HitPoints(current=12, maximum=12)
        
        paladin = CharacterSheet(
            name="Sir Lancelot",
            race=Race.HUMAN,
            character_class=CharacterClass.PALADIN,
            level=1,
            abilities=abilities,
            hit_points=hit_points
        )
        
        # Level 1 paladin has no spells
        level_1_slots = plugin.calculate_spell_slots("paladin", 1)
        paladin.max_spell_slots = level_1_slots["spell_slots"]
        paladin.current_spell_slots = level_1_slots["spell_slots"].copy()
        
        assert paladin.max_spell_slots == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert paladin.current_spell_slots == [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level up to 2 (gains spells)
        paladin.level = 2
        level_2_slots = plugin.calculate_spell_slots("paladin", 2)
        paladin.max_spell_slots = level_2_slots["spell_slots"]
        paladin.current_spell_slots = level_2_slots["spell_slots"].copy()
        
        # Level 2 paladin gets 1st level spells
        assert paladin.max_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        assert paladin.current_spell_slots == [2, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level up to 5 (gains 2nd level spells)
        paladin.level = 5
        level_5_slots = plugin.calculate_spell_slots("paladin", 5)
        old_max = paladin.max_spell_slots.copy()
        paladin.max_spell_slots = level_5_slots["spell_slots"]
        
        # Update current slots
        new_current_slots = []
        for i in range(9):
            current_slots = min(paladin.current_spell_slots[i], paladin.max_spell_slots[i])
            if paladin.max_spell_slots[i] > old_max[i]:
                current_slots += (paladin.max_spell_slots[i] - old_max[i])
            new_current_slots.append(current_slots)
        paladin.current_spell_slots = new_current_slots
        
        # Level 5 paladin gets 2nd level spells
        assert paladin.max_spell_slots == [4, 2, 0, 0, 0, 0, 0, 0, 0]
        assert paladin.current_spell_slots == [4, 2, 0, 0, 0, 0, 0, 0, 0]

    def test_non_spellcaster_progression(self):
        """Test that non-spellcasters don't get spell slots."""
        plugin = RulesEnginePlugin()
        
        # Create a fighter
        abilities = Abilities(strength=16, dexterity=14, constitution=15, 
                            intelligence=10, wisdom=12, charisma=8)
        hit_points = HitPoints(current=12, maximum=12)
        
        fighter = CharacterSheet(
            name="Conan the Barbarian",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            level=1,
            abilities=abilities,
            hit_points=hit_points
        )
        
        # Test spell slots from level 1 to 10
        for level in range(1, 11):
            fighter.level = level
            slots = plugin.calculate_spell_slots("fighter", level)
            assert slots["spellcasting_type"] == "none"
            assert slots["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_warlock_pact_magic(self):
        """Test warlock pact magic progression."""
        plugin = RulesEnginePlugin()
        
        # Create a warlock
        abilities = Abilities(strength=8, dexterity=14, constitution=13, 
                            intelligence=12, wisdom=10, charisma=16)
        hit_points = HitPoints(current=8, maximum=8)
        
        warlock = CharacterSheet(
            name="Faust",
            race=Race.HUMAN,
            character_class=CharacterClass.WARLOCK,
            level=1,
            abilities=abilities,
            hit_points=hit_points
        )
        
        # Level 1 warlock gets 1 first-level slot
        level_1_slots = plugin.calculate_spell_slots("warlock", 1)
        warlock.max_spell_slots = level_1_slots["spell_slots"]
        warlock.current_spell_slots = level_1_slots["spell_slots"].copy()
        
        assert warlock.max_spell_slots == [1, 0, 0, 0, 0, 0, 0, 0, 0]
        assert warlock.current_spell_slots == [1, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Level 3 warlock gets 2nd level pact magic
        warlock.level = 3
        level_3_slots = plugin.calculate_spell_slots("warlock", 3)
        warlock.max_spell_slots = level_3_slots["spell_slots"]
        warlock.current_spell_slots = level_3_slots["spell_slots"].copy()
        
        # Warlock pact magic: all slots are at the highest level
        assert warlock.max_spell_slots == [0, 2, 0, 0, 0, 0, 0, 0, 0]
        assert warlock.current_spell_slots == [0, 2, 0, 0, 0, 0, 0, 0, 0]

    def test_multiclass_consideration(self):
        """Test that the system handles basic class identification correctly."""
        plugin = RulesEnginePlugin()
        
        # Test that different classes are recognized correctly
        classes_to_test = [
            ("wizard", "full"),
            ("cleric", "full"),
            ("sorcerer", "full"),
            ("bard", "full"),
            ("druid", "full"),
            ("paladin", "half"),
            ("ranger", "half"),
            ("warlock", "pact"),
            ("fighter", "none"),
            ("barbarian", "none"),
            ("rogue", "none"),
            ("monk", "none"),
        ]
        
        for class_name, expected_type in classes_to_test:
            result = plugin.calculate_spell_slots(class_name, 5)
            assert result["spellcasting_type"] == expected_type, f"Failed for {class_name}"
            
            if expected_type == "none":
                assert result["spell_slots"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
            else:
                # Should have some spell slots at level 5
                assert sum(result["spell_slots"]) > 0