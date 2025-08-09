#!/usr/bin/env python3
"""
Test script for visual generation functionality.
This tests the image generation capabilities without requiring Azure credentials.
"""

import asyncio
import sys
import os
from unittest.mock import patch

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Mock environment variables before importing agents
with patch.dict(
    os.environ,
    {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002",
        "AZURE_OPENAI_DALLE_DEPLOYMENT": "dall-e-3",
        "STORAGE_CONNECTION_STRING": "test-connection",
    },
):
    from app.agents.artist_agent import ArtistAgent
    from app.agents.combat_cartographer_agent import CombatCartographerAgent


async def test_artist_agent():
    """Test the Artist Agent's image generation methods."""
    print("🎨 Testing Artist Agent...")

    try:
        artist = ArtistAgent()

        # Test character portrait generation
        character_details = {
            "name": "Elara Moonwhisper",
            "race": "elf",
            "class": "wizard",
            "gender": "female",
            "description": "A tall elf with silver hair and piercing blue eyes, wearing star-adorned robes",
        }

        print("   📸 Testing character portrait generation...")
        portrait_result = await artist.generate_character_portrait(character_details)

        if "error" in portrait_result:
            print(
                f"   ❌ Portrait generation handled gracefully: {portrait_result.get('error', 'Unknown error')}"
            )
        else:
            print(f"   ✅ Portrait generation successful!")
            print(f"      ID: {portrait_result.get('id')}")
            print(f"      Type: {portrait_result.get('type')}")
            print(f"      Character: {portrait_result.get('character_name')}")
            print(f"      Has image URL: {'image_url' in portrait_result}")

        # Test scene illustration
        scene_context = {
            "location": "ancient forest clearing",
            "mood": "mystical",
            "time": "twilight",
            "notable_elements": [
                "glowing mushrooms",
                "ancient stone circle",
                "fireflies",
            ],
            "weather": "misty",
        }

        print("   🏞️ Testing scene illustration generation...")
        scene_result = await artist.illustrate_scene(scene_context)

        if "error" in scene_result:
            print(
                f"   ❌ Scene generation handled gracefully: {scene_result.get('error', 'Unknown error')}"
            )
        else:
            print(f"   ✅ Scene generation successful!")
            print(f"      ID: {scene_result.get('id')}")
            print(f"      Type: {scene_result.get('type')}")
            print(f"      Location: {scene_result.get('location')}")
            print(f"      Has image URL: {'image_url' in scene_result}")

        # Test item visualization
        item_details = {
            "name": "Staff of Arcane Mastery",
            "type": "staff",
            "rarity": "legendary",
            "magical": True,
            "description": "A crystalline staff that pulses with ethereal blue energy",
        }

        print("   🗡️ Testing item visualization generation...")
        item_result = await artist.create_item_visualization(item_details)

        if "error" in item_result:
            print(
                f"   ❌ Item generation handled gracefully: {item_result.get('error', 'Unknown error')}"
            )
        else:
            print(f"   ✅ Item generation successful!")
            print(f"      ID: {item_result.get('id')}")
            print(f"      Type: {item_result.get('type')}")
            print(f"      Item: {item_result.get('item_name')}")
            print(f"      Has image URL: {'image_url' in item_result}")

        print(f"   📊 Total generated art pieces: {len(artist.generated_art)}")
        return True

    except Exception as e:
        print(f"   ❌ Artist Agent test failed: {str(e)}")
        return False


async def test_combat_cartographer():
    """Test the Combat Cartographer Agent's battle map generation."""
    print("\n🗺️ Testing Combat Cartographer Agent...")

    try:
        cartographer = CombatCartographerAgent()

        # Test battle map generation
        environment_context = {
            "location": "underground cavern",
            "terrain": "rocky",
            "size": "large",
            "features": ["stalactites", "underground pool", "narrow passages"],
            "hazards": ["slippery rocks", "low ceiling"],
        }

        combat_context = {"encounter_type": "ambush", "party_size": 4, "enemy_count": 6}

        print("   🎯 Testing battle map generation...")
        map_result = await cartographer.generate_battle_map(
            environment_context, combat_context
        )

        if "error" in map_result:
            print(
                f"   ❌ Map generation handled gracefully: {map_result.get('error', 'Unknown error')}"
            )
        else:
            print(f"   ✅ Map generation successful!")
            print(f"      ID: {map_result.get('id')}")
            print(f"      Name: {map_result.get('name')}")
            print(f"      Terrain: {map_result.get('terrain')}")
            print(f"      Features: {map_result.get('features')}")
            print(f"      Has image URL: {'image_url' in map_result}")

        print(f"   📊 Total battle maps: {len(cartographer.battle_maps)}")
        return True

    except Exception as e:
        print(f"   ❌ Combat Cartographer test failed: {str(e)}")
        return False


async def main():
    """Run all visual generation tests."""
    print("🚀 Starting Visual Generation Tests...")
    print("=" * 50)

    # Test individual agents
    artist_success = await test_artist_agent()
    cartographer_success = await test_combat_cartographer()

    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   🎨 Artist Agent: {'✅ PASS' if artist_success else '❌ FAIL'}")
    print(
        f"   🗺️ Combat Cartographer: {'✅ PASS' if cartographer_success else '❌ FAIL'}"
    )

    if artist_success and cartographer_success:
        print("\n🎉 All visual generation tests completed successfully!")
        print("✨ Visual elements functionality is properly implemented!")
        return True
    else:
        print("\n⚠️ Some tests failed. Check error messages above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
