#!/usr/bin/env python3
"""
Simple test script for character progression system.
"""
import sys
import os
import asyncio

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.plugins.rules_engine_plugin import RulesEnginePlugin
from app.agents.scribe_agent import ScribeAgent

async def test_progression_system():
    """Test the character progression system."""
    print("Testing D&D 5e Character Progression System")
    print("=" * 50)
    
    # Initialize components
    rules_engine = RulesEnginePlugin()
    scribe = ScribeAgent()
    
    # Test 1: Experience to level calculation
    print("\n1. Testing Experience to Level Calculation:")
    test_experiences = [0, 300, 900, 2700, 6500]
    for exp in test_experiences:
        result = rules_engine.calculate_level(exp)
        print(f"   Experience {exp}: Level {result['current_level']}")
    
    # Test 2: Proficiency bonus calculation
    print("\n2. Testing Proficiency Bonus Calculation:")
    test_levels = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]
    for level in test_levels:
        result = rules_engine.calculate_proficiency_bonus(level)
        print(f"   Level {level}: Proficiency Bonus +{result['proficiency_bonus']}")
    
    # Test 3: ASI eligibility
    print("\n3. Testing ASI Eligibility:")
    test_data = [(4, 0), (4, 1), (8, 0), (8, 1), (12, 2), (16, 3), (19, 4)]
    for level, asi_used in test_data:
        result = rules_engine.check_asi_eligibility(level, asi_used)
        print(f"   Level {level}, ASI Used {asi_used}: Can improve = {result['can_improve_abilities']}, Remaining = {result['asi_remaining']}")
    
    # Test 4: HP calculation
    print("\n4. Testing HP Calculation:")
    test_classes = ["fighter", "wizard", "barbarian", "rogue"]
    for char_class in test_classes:
        result = rules_engine.calculate_level_up_hp(char_class, 2, use_average=True)  # +2 Con modifier
        print(f"   {char_class.title()} (Con +2): {result['total_hp_gain']} HP ({result['hit_dice']})")
    
    # Test 5: Character creation and level up
    print("\n5. Testing Character Creation and Level Up:")
    
    # Create a test character
    character_data = {
        "name": "Test Hero",
        "race": "human",
        "class": "fighter",
        "level": 1,
        "experience": 0,
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,  # +2 modifier
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 8,
        "hitPoints": 12  # Fighter with +2 Con
    }
    
    character = await scribe.create_character(character_data)
    character_id = character["id"]
    print(f"   Created character: {character['name']} (Level {character['level']})")
    
    # Award enough experience to reach level 4 (ASI level)
    exp_result = await scribe.award_experience(character_id, 2700)
    print(f"   Awarded 2700 XP: Level {exp_result['level_info']['current_level']}, Can level up: {exp_result['can_level_up']}")
    
    # Level up to level 2
    level_up_result = await scribe.level_up_character(character_id)
    print(f"   Level up to {level_up_result['new_level']}: +{level_up_result['hit_points_gained']} HP")
    
    # Level up to level 3
    level_up_result = await scribe.level_up_character(character_id)
    print(f"   Level up to {level_up_result['new_level']}: +{level_up_result['hit_points_gained']} HP")
    
    # Level up to level 4 with ASI
    ability_improvements = {"strength": 1, "constitution": 1}  # +1 to Str and Con
    level_up_result = await scribe.level_up_character(character_id, ability_improvements)
    print(f"   Level up to {level_up_result['new_level']}: +{level_up_result['hit_points_gained']} HP")
    print(f"   Ability improvements: {level_up_result['ability_improvements']}")
    print(f"   Features gained: {level_up_result['features_gained']}")
    
    # Get final character state
    final_character = await scribe.get_character(character_id)
    print(f"\n   Final character state:")
    print(f"   Name: {final_character['name']}")
    print(f"   Level: {final_character['level']}")
    print(f"   Experience: {final_character['experience']}")
    print(f"   HP: {final_character['hitPoints']['current']}/{final_character['hitPoints']['maximum']}")
    print(f"   Abilities: {final_character['abilities']}")
    print(f"   Proficiency Bonus: +{final_character['proficiency_bonus']}")
    print(f"   ASI Used: {final_character['ability_score_improvements_used']}")
    
    print("\n" + "=" * 50)
    print("Character Progression System Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_progression_system())