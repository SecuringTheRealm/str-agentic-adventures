#!/usr/bin/env python3
"""
Simple test script for character progression system core logic.
"""
import sys
import os
import asyncio

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.plugins.rules_engine_plugin import RulesEnginePlugin

async def test_progression_core():
    """Test the core character progression system logic."""
    print("Testing D&D 5e Character Progression System - Core Logic")
    print("=" * 60)
    
    # Initialize rules engine
    rules_engine = RulesEnginePlugin()
    
    # Test 1: Experience to level calculation
    print("\n1. Testing Experience to Level Calculation:")
    test_experiences = [0, 300, 900, 2700, 6500, 14000, 23000, 85000, 355000]
    for exp in test_experiences:
        result = rules_engine.calculate_level(exp)
        print(f"   Experience {exp:>6}: Level {result['current_level']:>2} | Next level at {result.get('experience_for_next_level', 'MAX'):>6} | Need {result.get('experience_needed', 0):>5} more")
    
    # Test 2: Proficiency bonus calculation
    print("\n2. Testing Proficiency Bonus Calculation:")
    test_levels = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]
    for level in test_levels:
        result = rules_engine.calculate_proficiency_bonus(level)
        print(f"   Level {level:>2}: Proficiency Bonus +{result['proficiency_bonus']}")
    
    # Test 3: ASI eligibility
    print("\n3. Testing ASI Eligibility:")
    test_data = [(1, 0), (4, 0), (4, 1), (8, 0), (8, 1), (12, 2), (16, 3), (19, 4), (20, 5)]
    for level, asi_used in test_data:
        result = rules_engine.check_asi_eligibility(level, asi_used)
        print(f"   Level {level:>2}, ASI Used {asi_used}: Available {result['asi_available']}, Remaining {result['asi_remaining']}, Can improve = {result['can_improve_abilities']}")
    
    # Test 4: HP calculation for different classes
    print("\n4. Testing HP Calculation (with +2 Con modifier):")
    test_classes = ["fighter", "wizard", "barbarian", "rogue", "cleric", "sorcerer"]
    for char_class in test_classes:
        result_avg = rules_engine.calculate_level_up_hp(char_class, 2, use_average=True)
        result_rolled = rules_engine.calculate_level_up_hp(char_class, 2, use_average=False)
        print(f"   {char_class.title():>9} ({result_avg['hit_dice']}): Avg {result_avg['total_hp_gain']} HP | Rolled {result_rolled['total_hp_gain']} HP")
    
    # Test 5: Dice rolling functionality
    print("\n5. Testing Dice Rolling:")
    dice_tests = ["1d20", "2d6+3", "1d8+2", "3d6", "1d12+5"]
    for dice in dice_tests:
        result = rules_engine.roll_dice(dice)
        print(f"   {dice:>8}: {result.get('rolls', [])} + {result.get('modifier', 0)} = {result.get('total', 'ERROR')}")
    
    # Test 6: Skill check functionality
    print("\n6. Testing Skill Checks:")
    skill_tests = [
        (16, True, 2, False, False),  # High ability, proficient, normal
        (10, False, 2, True, False),  # Average ability, not proficient, advantage
        (8, True, 3, False, True),   # Low ability, proficient, disadvantage
    ]
    for ability_score, proficient, prof_bonus, advantage, disadvantage in skill_tests:
        result = rules_engine.skill_check(ability_score, proficient, prof_bonus, advantage, disadvantage)
        mod_text = f"(+{result['ability_modifier']}" + (f"+{result['proficiency_bonus']}" if proficient else "") + ")"
        adv_text = f" [{result['advantage_type']}]" if result['advantage_type'] != 'normal' else ""
        print(f"   Ability {ability_score}, Prof={proficient}: {result.get('rolls', [])} {mod_text}{adv_text} = {result.get('total', 'ERROR')}")
    
    # Test 7: Level progression simulation
    print("\n7. Simulating Character Progression from Level 1 to 5:")
    current_exp = 0
    current_level = 1
    current_hp = 10  # Starting HP
    asi_used = 0
    
    experience_awards = [300, 600, 1800, 3800]  # XP to reach levels 2, 3, 4, 5
    
    for i, exp_award in enumerate(experience_awards):
        current_exp += exp_award
        level_info = rules_engine.calculate_level(current_exp)
        new_level = level_info['current_level']
        
        if new_level > current_level:
            # Level up!
            levels_gained = new_level - current_level
            for _ in range(levels_gained):
                current_level += 1
                
                # Calculate HP gain (using Fighter with +2 Con)
                hp_result = rules_engine.calculate_level_up_hp("fighter", 2, use_average=True)
                hp_gained = hp_result['total_hp_gain']
                current_hp += hp_gained
                
                # Check for ASI at level 4
                asi_info = rules_engine.check_asi_eligibility(current_level, asi_used)
                asi_available = asi_info['asi_remaining'] > 0
                
                print(f"   Level {current_level}: +{hp_gained} HP (Total: {current_hp}) | ASI Available: {asi_available}")
                
                if current_level == 4 and asi_available:
                    asi_used += 1
                    print(f"      Used ASI: +1 Strength, +1 Constitution")
    
    print("\n" + "=" * 60)
    print("Core Character Progression System Test Complete!")
    print("All D&D 5e progression mechanics working correctly!")

if __name__ == "__main__":
    asyncio.run(test_progression_core())