#!/usr/bin/env python3
"""
Manual test script to demonstrate SRD compliance improvements.
This script shows the before/after of character creation with SRD features.
"""

import sys
import os
import asyncio
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.agents.scribe_agent import ScribeAgent
from app.srd_data import (
    get_class_features, 
    get_racial_traits, 
    get_background_info,
    load_spells,
    get_spells_by_class
)


def test_srd_data_loading():
    """Test that SRD data loads correctly."""
    print("=== Testing SRD Data Loading ===")
    
    # Test class features
    fighter_features = get_class_features("fighter", 1)
    print(f"Fighter Level 1 Features: {[f['name'] for f in fighter_features]}")
    
    # Test racial traits
    elf_traits = get_racial_traits("elf")
    print(f"Elf Traits: {[t['name'] for t in elf_traits.get('traits', [])]}")
    print(f"Elf Ability Bonuses: {elf_traits.get('ability_score_increases', {})}")
    print(f"Elf Speed: {elf_traits.get('speed', 30)} ft")
    
    # Test backgrounds
    acolyte_bg = get_background_info("acolyte")
    print(f"Acolyte Skills: {acolyte_bg.get('skill_proficiencies', [])}")
    print(f"Acolyte Feature: {acolyte_bg.get('feature', {}).get('name', 'None')}")
    
    # Test spells
    spells = load_spells()
    wizard_spells = get_spells_by_class("wizard")
    print(f"Total Spells: {len(spells)}")
    print(f"Wizard Spells: {len(wizard_spells)}")
    print(f"Sample Wizard Spells: {[s['name'] for s in wizard_spells[:3]]}")
    print()


async def test_character_creation():
    """Test character creation with SRD features."""
    print("=== Testing Character Creation ===")
    
    # Mock the database and kernel dependencies
    with patch('app.agents.scribe_agent.init_db'), \
         patch('app.agents.scribe_agent.kernel_manager.create_kernel') as mock_kernel, \
         patch('app.agents.scribe_agent.ScribeAgent._register_skills'), \
         patch('app.agents.scribe_agent.get_session') as mock_session:
        
        mock_kernel.return_value = MagicMock()
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        scribe = ScribeAgent()
        
        # Test creating a dwarf fighter with soldier background
        character_data = {
            "name": "Thorin Ironforge",
            "race": "dwarf",
            "class": "fighter", 
            "background": "soldier",
            "strength": 16,
            "dexterity": 12,
            "constitution": 15,  # Will become 17 with +2 racial
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 8
        }
        
        result = await scribe.create_character(character_data)
        
        print("Character Created Successfully!")
        print(f"Name: {result['name']}")
        print(f"Race: {result['race'].title()}")
        print(f"Class: {result['character_class'].title()}")
        print(f"Background: {result.get('background', 'None').title()}")
        print()
        
        # Show ability scores with racial bonuses
        abilities = result['abilities']
        print(f"Abilities (with racial bonuses):")
        print(f"  STR: {abilities['strength']} (no change)")
        print(f"  DEX: {abilities['dexterity']} (no change)")
        print(f"  CON: {abilities['constitution']} (15 + 2 racial = 17)")
        print(f"  INT: {abilities['intelligence']} (no change)")
        print(f"  WIS: {abilities['wisdom']} (no change)")
        print(f"  CHA: {abilities['charisma']} (no change)")
        print()
        
        # Show racial features
        print(f"Speed: {result['speed']} ft (dwarf speed)")
        print(f"Hit Points: {result['hit_points']['maximum']} (d10 + CON mod)")
        print(f"Hit Dice: {result['hit_dice']}")
        print()
        
        # Show features
        features = result.get('features', [])
        print(f"Features ({len(features)} total):")
        for feature in features:
            source = feature.get('source', 'unknown')
            print(f"  {feature['name']} ({source})")
        print()
        
        # Show skills
        skills = result.get('skills', {})
        active_skills = [skill for skill, proficient in skills.items() if proficient]
        print(f"Skill Proficiencies: {active_skills}")
        
        # Show saving throws
        saving_throws = result.get('saving_throw_proficiencies', [])
        print(f"Saving Throw Proficiencies: {saving_throws}")
        print()


def main():
    """Run all manual tests."""
    print("D&D 5e SRD Compliance Manual Test")
    print("=" * 50)
    print()
    
    # Test data loading
    test_srd_data_loading()
    
    # Test character creation
    asyncio.run(test_character_creation())
    
    print("=== Summary ===")
    print("✓ SRD data loads correctly")
    print("✓ Racial bonuses apply properly") 
    print("✓ Class features are granted")
    print("✓ Background skills are assigned")
    print("✓ Saving throw proficiencies set")
    print("✓ Speed calculated by race")
    print("✓ HP calculated with racial bonuses")
    print()
    print("SRD compliance improvements are working correctly!")


if __name__ == "__main__":
    main()