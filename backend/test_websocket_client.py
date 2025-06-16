#!/usr/bin/env python3
"""
Simple WebSocket test client for STR Agentic Adventures
Run this to test WebSocket connections directly.

Usage:
    python test_websocket_client.py
"""

import asyncio
import json
import websockets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketTester:
    def __init__(self, base_url="ws://localhost:8000"):
        self.base_url = base_url
        self.campaign_id = "test-campaign-123"
        self.character_id = "test-character-456"
    
    async def test_chat_websocket(self):
        """Test the chat WebSocket endpoint"""
        chat_url = f"{self.base_url}/api/ws/chat/{self.campaign_id}"
        
        print(f"\n🔗 Testing Chat WebSocket: {chat_url}")
        
        try:
            async with websockets.connect(chat_url) as websocket:
                print("✅ Successfully connected to chat WebSocket!")
                
                # Send a test chat message
                test_message = {
                    "type": "chat_input",
                    "message": "Hello, AI Dungeon Master! This is a test message.",
                    "character_id": self.character_id,
                    "campaign_id": self.campaign_id
                }
                
                print(f"📤 Sending message: {test_message}")
                await websocket.send(json.dumps(test_message))
                
                # Listen for responses (with timeout)
                try:
                    response_count = 0
                    while response_count < 5:  # Limit responses to avoid infinite loop
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        
                        print(f"📥 Received: {response_data}")
                        response_count += 1
                        
                        # Break on complete message
                        if response_data.get('type') == 'chat_complete':
                            break
                        elif response_data.get('type') == 'chat_error':
                            print(f"❌ Chat error: {response_data.get('message')}")
                            break
                            
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                
                print("✅ Chat WebSocket test completed")
                
        except Exception as e:
            print(f"❌ Chat WebSocket connection failed: {e}")
            return False
        
        return True
    
    async def test_campaign_websocket(self):
        """Test the campaign WebSocket endpoint"""
        campaign_url = f"{self.base_url}/api/ws/{self.campaign_id}"
        
        print(f"\n🔗 Testing Campaign WebSocket: {campaign_url}")
        
        try:
            async with websockets.connect(campaign_url) as websocket:
                print("✅ Successfully connected to campaign WebSocket!")
                
                # Send a test ping
                ping_message = {
                    "type": "ping",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                
                print(f"📤 Sending ping: {ping_message}")
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    print(f"📥 Received: {response_data}")
                    
                    if response_data.get('type') == 'pong':
                        print("✅ Ping/Pong successful!")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for pong")
                
                print("✅ Campaign WebSocket test completed")
                
        except Exception as e:
            print(f"❌ Campaign WebSocket connection failed: {e}")
            return False
        
        return True
    
    async def test_dice_roll_websocket(self):
        """Test dice rolling via campaign WebSocket"""
        campaign_url = f"{self.base_url}/api/ws/{self.campaign_id}"
        
        print(f"\n🎲 Testing Dice Roll via WebSocket: {campaign_url}")
        
        try:
            async with websockets.connect(campaign_url) as websocket:
                print("✅ Connected for dice roll test")
                
                # Send a dice roll message
                dice_message = {
                    "type": "dice_roll",
                    "notation": "1d20+3",
                    "character_id": self.character_id,
                    "player_name": "Test Player"
                }
                
                print(f"📤 Rolling dice: {dice_message}")
                await websocket.send(json.dumps(dice_message))
                
                # Wait for dice result
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    print(f"🎲 Dice result: {response_data}")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for dice result")
                
        except Exception as e:
            print(f"❌ Dice roll WebSocket test failed: {e}")
            return False
        
        return True

async def main():
    """Run all WebSocket tests"""
    print("🧪 STR Agentic Adventures WebSocket Test Suite")
    print("=" * 50)
    
    tester = WebSocketTester()
    
    results = []
    
    # Test 1: Chat WebSocket
    results.append(await tester.test_chat_websocket())
    
    # Test 2: Campaign WebSocket  
    results.append(await tester.test_campaign_websocket())
    
    # Test 3: Dice Roll via WebSocket
    results.append(await tester.test_dice_roll_websocket())
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All WebSocket tests passed!")
    else:
        print("⚠️  Some WebSocket tests failed. Check your backend configuration.")
        print("\n💡 Common issues:")
        print("   - Backend server not running on localhost:8000")
        print("   - WebSocket routes not properly registered")
        print("   - Azure OpenAI configuration missing/incorrect")
        print("   - Network connectivity issues")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
