#!/usr/bin/env python3
"""
Test script to verify the fix for GitHub issue #283:
"Unexpected behaviour (error) occuring when trying to chat with dungeon master agent"

This script tests that the DM agent properly handles input and returns responses
even when Azure OpenAI is not configured.
"""

import asyncio
import sys
import logging

# Set up logging to see any warnings
logging.basicConfig(level=logging.INFO)

async def test_dm_agent_responses():
    """Test that the DM agent returns proper responses for various inputs."""
    
    print("🧪 Testing DM Agent Response Generation (Issue #283)")
    print("=" * 60)
    
    try:
        from app.agents.dungeon_master_agent import get_dungeon_master
        
        # Get DM agent (should initialize in fallback mode)
        dm = get_dungeon_master()
        print(f"✅ DM Agent initialized (fallback_mode: {getattr(dm, '_fallback_mode', 'not set')})")
        
        # Test various input types that users might send
        test_cases = [
            ("Hello, I want to explore the area", "narrative"),
            ("I attack the goblin with my sword", "combat"),
            ("I check my inventory", "character"), 
            ("I want to talk to the NPC", "social"),
            ("I roll a d20", "dice"),
            ("", "empty input"),
            ("What should I do?", "general question"),
        ]
        
        all_passed = True
        
        for user_input, expected_type in test_cases:
            try:
                context = {
                    'character_id': 'test-character',
                    'campaign_id': 'test-campaign'
                }
                
                result = await dm.process_input(user_input, context)
                
                # Check that result has required fields
                required_fields = ['message', 'visuals', 'state_updates', 'combat_updates']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"❌ {expected_type}: Missing fields {missing_fields}")
                    all_passed = False
                elif not result.get('message'):
                    print(f"❌ {expected_type}: Empty message field")
                    all_passed = False
                else:
                    print(f"✅ {expected_type}: '{result['message'][:50]}{'...' if len(result['message']) > 50 else ''}'")
                    
            except Exception as e:
                print(f"❌ {expected_type}: Exception occurred: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Failed to initialize DM agent: {e}")
        return False

async def test_api_endpoint():
    """Test the API endpoint to ensure it works end-to-end."""
    
    print(f"\n🌐 Testing API Endpoint")
    print("=" * 30)
    
    try:
        import httpx
        
        # Test the API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/game/input",
                json={
                    "message": "Hello, I want to explore the mysterious cave",
                    "character_id": "test-character",
                    "campaign_id": "test-campaign"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and data['message']:
                    print(f"✅ API Response: {data['message'][:50]}{'...' if len(data['message']) > 50 else ''}")
                    return True
                else:
                    print(f"❌ API returned empty message: {data}")
                    return False
            else:
                print(f"❌ API returned status {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def main():
    """Run all tests and report results."""
    
    print("🔍 Testing GitHub Issue #283 Fix")
    print("Issue: 'Unexpected behaviour (error) occuring when trying to chat with dungeon master agent'")
    print()
    
    # Test 1: DM Agent Direct Testing
    dm_test_passed = await test_dm_agent_responses()
    
    # Test 2: API Endpoint Testing
    api_test_passed = await test_api_endpoint()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"DM Agent Direct Tests: {'✅ PASSED' if dm_test_passed else '❌ FAILED'}")
    print(f"API Endpoint Tests: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    
    if dm_test_passed and api_test_passed:
        print(f"\n🎉 Issue #283 FIX VERIFIED: All tests passed!")
        print("Users should now be able to chat with the dungeon master agent successfully.")
        return 0
    else:
        print(f"\n⚠️  Issue #283 FIX INCOMPLETE: Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)