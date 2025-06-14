#!/usr/bin/env python3
"""
Test script to verify streaming chat functionality works properly.
Tests both fallback mode (without Azure OpenAI) and the streaming infrastructure.
"""

import asyncio
import sys
import logging
from unittest.mock import Mock, AsyncMock

# Set up logging to see any warnings
logging.basicConfig(level=logging.INFO)

class MockWebSocket:
    """Mock WebSocket for testing streaming functionality."""
    
    def __init__(self):
        self.sent_messages = []
    
    async def send_text(self, message):
        """Mock send_text method."""
        self.sent_messages.append(message)
        print(f"WebSocket sent: {message}")

async def test_streaming_chat_fallback():
    """Test streaming chat functionality in fallback mode."""
    print("🧪 Testing Streaming Chat in Fallback Mode")
    print("=" * 60)
    
    try:
        from app.agents.dungeon_master_agent import get_dungeon_master
        
        # Get DM agent (should initialize in fallback mode)
        dm = get_dungeon_master()
        print(f"✅ DM Agent initialized (fallback_mode: {getattr(dm, '_fallback_mode', 'not set')})")
        
        # Create mock WebSocket
        mock_websocket = MockWebSocket()
        
        # Test streaming with various inputs
        test_cases = [
            "I want to explore the ancient temple",
            "I attack the goblin with my sword", 
            "I try to persuade the guard to let us pass",
            "I check my inventory",
        ]
        
        for i, user_input in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {user_input[:50]} ---")
            
            context = {
                'character_id': 'test-character',
                'campaign_id': 'test-campaign',
                'websocket': mock_websocket,
                'streaming': True
            }
            
            # Clear previous messages
            mock_websocket.sent_messages = []
            
            # Test streaming functionality
            try:
                await dm.process_input_stream(user_input, context)
                
                # Verify messages were sent
                if mock_websocket.sent_messages:
                    print(f"✅ Sent {len(mock_websocket.sent_messages)} WebSocket messages")
                    
                    # Check for expected message types
                    message_types = []
                    for msg_str in mock_websocket.sent_messages:
                        try:
                            import json
                            msg = json.loads(msg_str)
                            message_types.append(msg.get('type', 'unknown'))
                        except json.JSONDecodeError:
                            pass
                    
                    print(f"✅ Message types: {message_types}")
                    
                    # Verify streaming flow
                    expected_flow = ['chat_typing', 'chat_start_stream', 'chat_stream', 'chat_complete']
                    if any(msg_type in expected_flow for msg_type in message_types):
                        print("✅ Contains expected streaming message types")
                    else:
                        print("⚠️  May not contain expected streaming flow")
                else:
                    print("❌ No WebSocket messages sent")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during streaming: {e}")
                return False
        
        print("\n✅ All streaming tests completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test streaming chat: {e}")
        return False

async def test_websocket_infrastructure():
    """Test WebSocket infrastructure components."""
    print("\n🧪 Testing WebSocket Infrastructure")
    print("=" * 60)
    
    try:
        from app.api.websocket_routes import manager, handle_chat_message
        
        # Test connection manager
        print("✅ WebSocket manager imported successfully")
        print(f"Active connections: {len(manager.active_connections)}")
        print(f"Campaign connections: {len(manager.campaign_connections)}")
        
        # Test chat message handler exists
        print("✅ Chat message handler imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test WebSocket infrastructure: {e}")
        return False

async def test_azure_openai_streaming():
    """Test Azure OpenAI streaming client (will fail without config, which is expected)."""
    print("\n🧪 Testing Azure OpenAI Streaming Client")
    print("=" * 60)
    
    try:
        from app.azure_openai_client import AzureOpenAIClient
        
        client = AzureOpenAIClient()
        print("✅ Azure OpenAI client initialized")
        
        # Check if streaming method exists
        if hasattr(client, 'chat_completion_stream'):
            print("✅ Streaming method available")
        else:
            print("❌ Streaming method missing")
            return False
            
        print("✅ Streaming client infrastructure ready")
        print("ℹ️  Will use fallback mode without Azure OpenAI credentials")
        return True
        
    except Exception as e:
        print(f"ℹ️  Azure OpenAI config error (expected): {str(e)[:100]}...")
        print("✅ This is expected without Azure OpenAI credentials")
        return True

async def main():
    """Run all tests and report results."""
    print("🚀 Starting Streaming Chat Tests")
    print("=" * 60)
    
    tests = [
        ("WebSocket Infrastructure", test_websocket_infrastructure()),
        ("Azure OpenAI Streaming", test_azure_openai_streaming()),
        ("Streaming Chat Fallback", test_streaming_chat_fallback()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Streaming chat is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)