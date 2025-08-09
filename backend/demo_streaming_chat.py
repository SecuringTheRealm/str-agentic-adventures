#!/usr/bin/env python3
"""
Demonstration script showing the streaming chat functionality.
This simulates how the system works when a user sends a chat message.
"""

import asyncio
import json
import sys


class StreamingDemo:
    """Demonstrates the streaming chat flow."""

    def __init__(self) -> None:
        self.messages_sent = []

    async def simulate_websocket_send(self, message: str) -> None:
        """Simulate sending a message via WebSocket."""
        self.messages_sent.append(message)

        # Parse and display the message nicely
        try:
            msg_data = json.loads(message)
            msg_type = msg_data.get("type", "unknown")

            if msg_type == "chat_typing":
                print("🤔 DM is thinking...")
            elif msg_type == "chat_start_stream":
                print("📝 DM starts responding: ", end="", flush=True)
            elif msg_type == "chat_stream":
                chunk = msg_data.get("chunk", "")
                print(chunk, end="", flush=True)
                await asyncio.sleep(0.05)  # Simulate network delay
            elif msg_type == "chat_complete":
                print("\n✨ Response complete!")
            elif msg_type == "chat_error":
                print(f"\n❌ Error: {msg_data.get('message', 'Unknown error')}")

        except json.JSONDecodeError:
            print(f"Raw message: {message}")

    async def demonstrate_streaming_flow(self) -> bool:
        """Show how streaming chat works."""
        print("🎭 Streaming Chat Demonstration")
        print("=" * 60)
        print("This shows how messages stream from the AI to the user in real-time.\n")

        # Mock WebSocket for testing
        class MockWebSocket:
            def __init__(self, demo) -> None:
                self.demo = demo

            async def send_text(self, message) -> None:
                await self.demo.simulate_websocket_send(message)

        try:
            from app.agents.dungeon_master_agent import get_dungeon_master

            dm = get_dungeon_master()
            mock_ws = MockWebSocket(self)

            print("Player: 'I want to explore the mysterious ancient ruins'")
            print("=" * 60)

            context = {
                "character_id": "demo-character",
                "campaign_id": "demo-campaign",
                "websocket": mock_ws,
                "streaming": True,
            }

            # Process the input with streaming
            await dm.process_input_stream(
                "I want to explore the mysterious ancient ruins", context
            )

            print(f"\n📊 Total messages sent: {len(self.messages_sent)}")
            print(
                "\nThis demonstrates the real-time streaming experience users will see!"
            )

        except Exception as e:
            print(f"Error in demonstration: {e}")
            return False

        return True


async def main() -> int:
    """Run the streaming demonstration."""
    demo = StreamingDemo()

    print("🚀 Starting Streaming Chat Demonstration")
    print("This shows the new real-time chat experience!\n")

    success = await demo.demonstrate_streaming_flow()

    if success:
        print("\n🎉 Demonstration completed successfully!")
        print("\nKey improvements:")
        print("✅ Real-time streaming responses (no more waiting)")
        print("✅ Immediate feedback when DM is thinking")
        print("✅ Progressive text display with animated cursor")
        print("✅ Better error handling and connection management")
        print("✅ Separated chat from other game events")
        return 0
    print("\n❌ Demonstration failed")
    return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Demonstration interrupted")
        sys.exit(1)
