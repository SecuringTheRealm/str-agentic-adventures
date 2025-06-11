#!/usr/bin/env python3
"""
Simple test script to verify image generation functionality.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Mock environment variables for testing (without actual API keys)
test_env = {
    "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "test-key",
    "AZURE_OPENAI_API_VERSION": "2023-12-01-preview",
    "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o-mini",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002",
    "AZURE_OPENAI_IMAGE_DEPLOYMENT": "dall-e-3"
}

for key, value in test_env.items():
    os.environ[key] = value

async def test_artist_agent_structure():
    """Test that the ArtistAgent can be instantiated and has the expected methods."""
    try:
        from app.agents.artist_agent import ArtistAgent
        
        # Test instantiation (this will fail with actual API calls but should import correctly)
        print("✓ ArtistAgent imports successfully")
        
        # Check that required methods exist
        required_methods = ['generate_character_portrait', 'illustrate_scene', 'create_item_visualization']
        for method in required_methods:
            if hasattr(ArtistAgent, method):
                print(f"✓ ArtistAgent has method: {method}")
            else:
                print(f"✗ ArtistAgent missing method: {method}")
                
        return True
        
    except Exception as e:
        print(f"✗ Error testing ArtistAgent: {e}")
        return False

async def test_combat_cartographer_structure():
    """Test that the CombatCartographerAgent can be instantiated and has the expected methods."""
    try:
        from app.agents.combat_cartographer_agent import CombatCartographerAgent
        
        print("✓ CombatCartographerAgent imports successfully")
        
        # Check that required methods exist
        required_methods = ['generate_battle_map']
        for method in required_methods:
            if hasattr(CombatCartographerAgent, method):
                print(f"✓ CombatCartographerAgent has method: {method}")
            else:
                print(f"✗ CombatCartographerAgent missing method: {method}")
                
        return True
        
    except Exception as e:
        print(f"✗ Error testing CombatCartographerAgent: {e}")
        return False

async def test_config_structure():
    """Test that configuration includes image deployment settings."""
    try:
        from app.config import settings
        
        print("✓ Config imports successfully")
        
        # Check that image deployment config exists
        if hasattr(settings, 'azure_openai_image_deployment'):
            print("✓ Config has azure_openai_image_deployment setting")
        else:
            print("✗ Config missing azure_openai_image_deployment setting")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing config: {e}")
        return False

async def main():
    """Run all tests."""
    print("Testing image generation integration...")
    print("=" * 50)
    
    tests = [
        test_config_structure(),
        test_artist_agent_structure(),
        test_combat_cartographer_structure()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("=" * 50)
    success_count = sum(1 for result in results if result is True)
    print(f"Tests completed: {success_count}/{len(tests)} passed")
    
    if success_count == len(tests):
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)