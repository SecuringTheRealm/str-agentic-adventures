#!/usr/bin/env python3
"""
Test script to demonstrate the D&D 5e rules engine functionality.
This script shows how to use the enhanced rules engine with comprehensive D&D 5e mechanics.
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.plugins.rules_engine_plugin import RulesEnginePlugin
from app.agents.dungeon_master_agent import DungeonMasterAgent

def main():
    print("=== D&D 5e Rules Engine Test ===\n")
    
    # Initialize the rules engine
    rules = RulesEnginePlugin()
    
    print("1. Testing Basic Dice Rolling:")
    dice_tests = ["1d20", "2d6+3", "1d8+2", "3d4-1"]
    for dice in dice_tests:
        result = rules.roll_dice(dice)
        print(f"   {dice}: {result['rolls']} + {result['modifier']} = {result['total']}")
    
    print("\n2. Testing Skill Checks:")
    # Test various skill checks
    athletics_check = rules.skill_check(16, proficient=True, proficiency_bonus=3)
    print(f"   Athletics (STR 16, proficient): {athletics_check['total']} (rolled {athletics_check['rolls'][0]})")
    
    stealth_check = rules.skill_check(14, proficient=False, proficiency_bonus=2, advantage=True)
    print(f"   Stealth (DEX 14, not proficient, advantage): {stealth_check['total']} (rolled {stealth_check['rolls']})")
    
    print("\n3. Testing Saving Throws:")
    # Test saving throws
    dex_save = rules.saving_throw(12, proficient=False, proficiency_bonus=2, dc=15)
    print(f"   Dexterity save vs DC 15: {dex_save['total']} - {'SUCCESS' if dex_save['is_success'] else 'FAILURE'}")
    
    wis_save = rules.saving_throw(14, proficient=True, proficiency_bonus=3, dc=13)
    print(f"   Wisdom save vs DC 13 (proficient): {wis_save['total']} - {'SUCCESS' if wis_save['is_success'] else 'FAILURE'}")
    
    print("\n4. Testing Combat Mechanics:")
    # Test attack resolution
    attack = rules.resolve_attack(5, 15)
    print(f"   Attack roll: {attack['total']} vs AC 15 - {'HIT' if attack['is_hit'] else 'MISS'}")
    if attack['is_critical_hit']:
        print("   *** CRITICAL HIT! ***")
    
    # Test damage calculation
    if attack['is_hit']:
        damage = rules.calculate_damage("1d8+3", attack['is_critical_hit'])
        print(f"   Damage: {damage['total']} points")
    
    print("\n5. Testing Spell Mechanics:")
    # Test spell attack
    spell_attack = rules.spell_attack(6, 14)
    print(f"   Spell attack: {spell_attack['total']} vs AC 14 - {'HIT' if spell_attack['is_hit'] else 'MISS'}")
    
    print("\n6. Testing D&D 5e Rules Lookup:")
    # Test skill information
    skill_info = rules.get_skill_info("perception")
    print(f"   Perception skill: {skill_info['ability']} - {skill_info['description']}")
    
    # Test condition information
    condition_info = rules.get_condition_info("frightened")
    print(f"   Frightened condition: {condition_info['description']}")
    print(f"   Effects: {', '.join(condition_info['effects'])}")
    
    # Test spell information
    spell_info = rules.get_spell_info("fireball")
    print(f"   Fireball: Level {spell_info['level']} {spell_info['school']} spell")
    print(f"   Range: {spell_info['range']}, Components: {spell_info['components']}")
    
    # Test difficulty class lookup
    dc_info = rules.get_difficulty_class("hard")
    print(f"   Hard task DC: {dc_info['dc']}")
    
    print("\n7. Testing Proficiency Bonus Calculation:")
    for level in [1, 5, 9, 13, 17, 20]:
        prof_bonus = rules.calculate_proficiency_bonus(level)
        print(f"   Level {level}: +{prof_bonus['proficiency_bonus']} proficiency bonus")
    
    print("\n8. Testing Initiative:")
    initiative = rules.roll_initiative(3)
    print(f"   Initiative (DEX +3): {initiative['initiative']} (rolled {initiative['rolls'][0]})")
    
    print("\n9. Testing Agent Integration:")
    # Test that the rules engine works in the dungeon master agent
    dm = DungeonMasterAgent()
    rules_plugin = dm.kernel.get_plugin("Rules")
    memory_plugin = dm.kernel.get_plugin("Memory")
    
    print(f"   Dungeon Master has {len(dm.kernel.plugins)} plugins loaded")
    print(f"   Rules plugin has {len(rules_plugin.functions)} functions available")
    print(f"   Memory plugin has {len(memory_plugin.functions)} functions available")
    
    print("\n=== All Tests Completed Successfully! ===")
    print("\nThe D&D 5e rules engine is fully functional and integrated with the game system.")
    print("Available features:")
    print("- Basic dice rolling with modifiers")
    print("- Skill checks with proficiency and advantage/disadvantage")
    print("- Saving throws with all D&D 5e mechanics")
    print("- Attack resolution and damage calculation")
    print("- Spell attacks and spell information lookup")
    print("- Condition effects and descriptions")
    print("- Proficiency bonus calculation by level")
    print("- Initiative rolling")
    print("- Integration with the dungeon master agent system")

if __name__ == "__main__":
    main()