#!/usr/bin/env python3
"""
Simple test script for the enhanced battle map system.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.combat_cartographer_agent import CombatCartographerAgent

async def test_battle_map_generation():
    """Test basic battle map generation functionality."""
    
    print("Testing Enhanced Battle Map System")
    print("=" * 50)
    
    # Initialize the agent
    cartographer = CombatCartographerAgent()
    
    # Test 1: Basic map generation
    print("\n1. Testing basic map generation...")
    environment_context = {
        "location": "abandoned castle courtyard",
        "terrain": "urban",
        "size": "medium",
        "features": ["broken fountain", "stone walls", "iron gates"],
        "lighting": "dim",
        "weather": "fog"
    }
    
    combat_context = {
        "participants": ["player1", "player2", "goblin1", "goblin2"]
    }
    
    result = await cartographer.generate_battle_map(environment_context, combat_context)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Map generated successfully!")
        print(f"   Map ID: {result['id']}")
        print(f"   Name: {result['name']}")
        print(f"   Description: {result['description']}")
        print(f"   Grid Size: {result['tactical_info']['grid_size']}")
        print(f"   Recommended Participants: {result['tactical_info']['recommended_participants']}")
    
    # Test 2: Template-based generation
    print("\n2. Testing template-based generation...")
    template_environment = {
        "location": "mysterious chamber",
        "template": "dungeon_room",
        "size": "large"
    }
    
    template_result = await cartographer.generate_battle_map(template_environment)
    
    if "error" in template_result:
        print(f"❌ Error: {template_result['error']}")
    else:
        print("✅ Template map generated successfully!")
        print(f"   Template: {template_result['template']}")
        print(f"   Features: {template_result['features']}")
    
    # Test 3: Get available templates
    print("\n3. Testing template retrieval...")
    templates = await cartographer.get_map_templates()
    print(f"✅ Available templates: {list(templates['templates'].keys())}")
    
    # Test 4: Combat state update
    if "error" not in result:
        print("\n4. Testing combat state update...")
        combat_state = {
            "positions": {
                "player1": {"x": 5, "y": 5},
                "player2": {"x": 7, "y": 5},
                "goblin1": {"x": 15, "y": 10},
                "goblin2": {"x": 17, "y": 12}
            },
            "active_character": "player1",
            "character_types": {
                "player1": "ally",
                "player2": "ally", 
                "goblin1": "enemy",
                "goblin2": "enemy"
            },
            "round": 1,
            "current_turn": 0
        }
        
        updated_map = await cartographer.update_map_with_combat_state(result['id'], combat_state)
        
        if "error" in updated_map:
            print(f"❌ Error: {updated_map['error']}")
        else:
            print("✅ Combat state updated successfully!")
            if "tactical_analysis" in updated_map:
                analysis = updated_map["tactical_analysis"]
                print(f"   Active Character: {analysis['active_character']}")
                print(f"   Nearby Enemies: {len(analysis['nearby_enemies'])}")
                print(f"   Recommendations: {analysis['tactical_recommendations']}")
    
    # Test 5: Map variation generation
    if "error" not in result:
        print("\n5. Testing map variation generation...")
        variation = await cartographer.generate_map_variation(result['id'], "lighting")
        
        if "error" in variation:
            print(f"❌ Error: {variation['error']}")
        else:
            print("✅ Map variation generated successfully!")
            print(f"   Base Map: {result['lighting']}")
            print(f"   Variation: {variation['lighting']}")
    
    print("\n" + "=" * 50)
    print("Battle Map System Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_battle_map_generation())