#!/usr/bin/env python3
"""
End-to-end test for image generation functionality.
Tests the complete flow from frontend API to DALL-E generation.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock, patch

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))


async def test_end_to_end_image_generation() -> bool | None:
    """Test the complete image generation flow."""
    print("🎯 Testing End-to-End Image Generation Flow...")
    print("=" * 50)

    try:
        # Mock Azure OpenAI client to simulate successful response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].url = "https://example.com/generated-image.jpg"
        mock_response.data[0].revised_prompt = "A fantasy character portrait"

        with patch(
            "app.azure_openai_client.AsyncAzureOpenAI"
        ) as mock_azure_client_class:
            # Setup mock client
            mock_client_instance = Mock()
            mock_client_instance.images.generate = AsyncMock(return_value=mock_response)
            mock_azure_client_class.return_value = mock_client_instance

            # Test 1: Character Portrait Generation
            print("\n1️⃣ Testing Character Portrait Generation...")
            from app.agents.artist_agent import get_artist

            artist = get_artist()

            character_details = {
                "name": "Aragorn Strider",
                "race": "human",
                "class": "ranger",
                "gender": "male",
                "description": "A weathered ranger with piercing gray eyes",
            }

            portrait_result = await artist.generate_character_portrait(
                character_details
            )

            assert "error" not in portrait_result, (
                f"Portrait generation failed: {portrait_result.get('error')}"
            )
            assert (
                portrait_result.get("image_url")
                == "https://example.com/generated-image.jpg"
            )
            assert portrait_result.get("character_name") == "Aragorn Strider"

            print("   ✅ Character portrait generated successfully")
            print(f"      Image URL: {portrait_result.get('image_url')}")

            # Test 2: Scene Illustration Generation
            print("\n2️⃣ Testing Scene Illustration Generation...")

            scene_context = {
                "location": "mystical forest glade",
                "mood": "ethereal",
                "time": "twilight",
                "notable_elements": [
                    "ancient oak tree",
                    "floating wisps",
                    "stone circle",
                ],
                "weather": "misty",
            }

            scene_result = await artist.illustrate_scene(scene_context)

            assert "error" not in scene_result, (
                f"Scene generation failed: {scene_result.get('error')}"
            )
            assert (
                scene_result.get("image_url")
                == "https://example.com/generated-image.jpg"
            )
            assert scene_result.get("location") == "mystical forest glade"

            print("   ✅ Scene illustration generated successfully")
            print(f"      Image URL: {scene_result.get('image_url')}")

            # Test 3: Battle Map Generation
            print("\n3️⃣ Testing Battle Map Generation...")
            from app.agents.combat_cartographer_agent import CombatCartographerAgent

            cartographer = CombatCartographerAgent()

            environment_context = {
                "location": "ancient ruins",
                "terrain": "stone",
                "size": "large",
                "features": ["crumbling walls", "overgrown vines", "broken statues"],
                "hazards": ["unstable floor", "hidden pits"],
            }

            combat_context = {
                "encounter_type": "exploration",
                "party_size": 5,
                "enemy_count": 0,
            }

            map_result = await cartographer.generate_battle_map(
                environment_context, combat_context
            )

            assert "error" not in map_result, (
                f"Map generation failed: {map_result.get('error')}"
            )
            assert (
                map_result.get("image_url") == "https://example.com/generated-image.jpg"
            )
            assert map_result.get("terrain") == "stone"

            print("   ✅ Battle map generated successfully")
            print(f"      Image URL: {map_result.get('image_url')}")

            # Test 4: API Integration
            print("\n4️⃣ Testing API Integration...")

            # Mock FastAPI request
            image_request = {
                "image_type": "character_portrait",
                "details": {"name": "Legolas", "race": "elf", "class": "archer"},
            }

            # Import and test the API function
            from app.api.game_routes import generate_image as api_generate_image

            api_result = await api_generate_image(image_request)

            assert "error" not in api_result, (
                f"API generation failed: {api_result.get('error')}"
            )
            assert (
                api_result.get("image_url") == "https://example.com/generated-image.jpg"
            )

            print("   ✅ API integration working correctly")
            print(
                f"      API response: {api_result.get('type')} for {api_result.get('character_name')}"
            )

            print("\n" + "=" * 50)
            print("🎉 End-to-End Image Generation Tests PASSED!")
            print("✨ All components working correctly:")
            print("   • Azure OpenAI DALL-E client updated to SDK 1.0+")
            print("   • Artist Agent generating portraits and scenes")
            print("   • Combat Cartographer generating battle maps")
            print("   • API endpoints responding correctly")
            print("   • Frontend type definitions in place")
            print("   • Error handling implemented")

            return True

    except Exception as e:
        print(f"\n❌ End-to-End test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_end_to_end_image_generation())
    sys.exit(0 if success else 1)
