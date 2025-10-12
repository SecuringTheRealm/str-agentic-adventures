"""
Dungeon Master Agent - Migrated to Azure AI Agents SDK.

This agent uses Azure AI Agents SDK for production-grade orchestration of the
D&D experience through AI guidance.
"""

import json
import logging
import random
import re
from typing import Any

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    AssistantMessage,
    ChatCompletions,
    ChatRequestMessage,
    SystemMessage,
    UserMessage,
)

from app.agent_client_setup import agent_client_manager
from app.utils.dice import DiceRoller

logger = logging.getLogger(__name__)


class DungeonMasterAgent:
    """
    Dungeon Master Agent using Azure AI Agents SDK to fulfill the role
    of orchestrating the D&D experience through AI guidance.
    """

    def __init__(self) -> None:
        """Initialize the Dungeon Master agent."""
        self._fallback_mode = False
        self.chat_client: ChatCompletionsClient | None = None

        # Try to get the shared chat client from agent client manager
        try:
            self.chat_client = agent_client_manager.get_chat_client()
            if self.chat_client is None:
                # Agent client manager is in fallback mode
                self._fallback_mode = True
                logger.warning(
                    "DM Agent operating in fallback mode - Azure OpenAI not configured"
                )
            else:
                logger.info("DM Agent initialized with Azure AI Agents SDK")

        except Exception as e:
            logger.warning(
                f"Failed to initialize DM Agent with Azure AI SDK: {e}. "
                "Operating in fallback mode."
            )
            self._fallback_mode = True

        # Fallback components are initialized lazily
        self._fallback_initialized = False

    def _get_dm_system_prompt(self, context: dict[str, Any]) -> str:
        """
        Generate a comprehensive system prompt that embodies the Dungeon Master role
        as specified in the PRD, replacing complex agent coordination.
        """
        character_info = ""
        if context.get("character_name"):
            character_info = f"The player character is {context.get('character_name', 'an adventurer')}, "
            character_info += f"a level {context.get('character_level', '1')} {context.get('character_class', 'fighter')}. "

        return f"""You are an expert Dungeon Master for D&D 5e. You are the primary orchestrator of the tabletop RPG experience, responsible for:

- Managing player interactions and conversation flow
- Coordinating narrative, combat, and character management aspects
- Maintaining cohesion across the gameplay experience  
- Ensuring continuity of game rules and narrative
- Creating immersive storytelling and descriptions
- Adjudicating player actions and their consequences

{character_info}

Your responses should:
- Be engaging and immersive
- Respect player agency and choices
- Follow D&D 5e rules when applicable
- Advance the story meaningfully
- Describe outcomes clearly
- Suggest or prompt for dice rolls when appropriate (but don't roll for the player)
- Maintain the fantasy adventure atmosphere

Always respond as a helpful, creative DM who wants players to have an exciting adventure. Keep responses focused and not overly long. You are the single point of coordination for the entire game experience."""

    async def process_input(
        self, user_input: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Process user input using Azure AI Agents SDK.

        Args:
            user_input: The player's input text
            context: Additional context information

        Returns:
            Dict with required fields: message, visuals, state_updates, combat_updates
        """
        if not context:
            context = {}

        logger.info(f"DM processing player input: {user_input}")

        # Use fallback mode if needed
        if self._fallback_mode:
            return await self._process_input_fallback(user_input, context)

        try:
            # Create system prompt
            system_prompt = self._get_dm_system_prompt(context)

            # Create user message with context
            user_message = user_input
            if context.get("character_name"):
                user_message = f"Player ({context['character_name']}): {user_input}"

            # Create messages for Azure AI SDK
            messages: list[ChatRequestMessage] = [
                SystemMessage(content=system_prompt),
                UserMessage(content=user_message),
            ]

            # Get AI response using Azure AI Inference SDK
            from app.config import settings
            
            response: ChatCompletions = await self.chat_client.complete(
                messages=messages,
                model=settings.azure_openai_chat_deployment,
                temperature=0.7,
                max_tokens=500,
            )

            # Extract the response text
            ai_response = (
                response.choices[0].message.content
                if response.choices
                else "The adventure continues..."
            )

            # Structure the response in the expected format
            return {
                "message": ai_response.strip(),
                "visuals": [],  # Simple implementation - no visual generation
                "state_updates": {"last_action": user_input},
                "combat_updates": None,
            }

        except Exception as e:
            logger.error(f"Error in DM processing: {str(e)}")
            # Fall back to using the full fallback processing which handles dice, etc.
            return await self._process_input_fallback(user_input, context)

    async def process_input_stream(
        self, user_input: str, context: dict[str, Any] = None
    ) -> None:
        """
        Process user input with streaming responses via WebSocket.

        Args:
            user_input: The player's input text
            context: Context including WebSocket for streaming
        """
        if not context:
            context = {}

        websocket = context.get("websocket")
        if not websocket:
            logger.error("No WebSocket provided for streaming")
            return

        logger.info(f"DM processing streaming input: {user_input}")

        # Use fallback streaming if needed
        if self._fallback_mode:
            await self._process_input_stream_fallback(user_input, context)
            return

        try:
            # Send typing indicator
            await self._send_chat_message(
                websocket,
                {
                    "type": "chat_typing",
                    "message": "The Dungeon Master considers your action...",
                },
            )

            # Create system prompt
            system_prompt = self._get_dm_system_prompt(context)

            # Create user message
            user_message = user_input
            if context.get("character_name"):
                user_message = f"Player ({context['character_name']}): {user_input}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            # Stream the AI response
            await self._stream_ai_response(messages, websocket)

        except Exception as e:
            logger.error(f"Error in streaming processing: {str(e)}")
            await self._send_chat_message(
                websocket,
                {
                    "type": "chat_error",
                    "message": "I encountered an issue processing your request. Please try again.",
                },
            )

    async def _stream_ai_response(
        self, messages: list[dict[str, str]], websocket
    ) -> None:
        """Stream AI response using Azure AI Inference SDK."""
        try:
            # Send start streaming message
            await self._send_chat_message(
                websocket, {"type": "chat_start_stream", "message": ""}
            )

            # Convert message dicts to ChatRequestMessage objects
            chat_messages: list[ChatRequestMessage] = []
            for msg in messages:
                if msg["role"] == "system":
                    chat_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    chat_messages.append(UserMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_messages.append(AssistantMessage(content=msg["content"]))

            # Get model deployment name from settings
            from app.config import settings

            # Stream response using Azure AI Inference SDK
            full_response = ""
            response = await self.chat_client.complete(
                messages=chat_messages,
                model=settings.azure_openai_chat_deployment,
                temperature=0.7,
                max_tokens=500,
                stream=True,
            )

            async for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        chunk_text = delta.content
                        full_response += chunk_text
                        await self._send_chat_message(
                            websocket,
                            {
                                "type": "chat_stream",
                                "chunk": chunk_text,
                                "full_text": full_response,
                            },
                        )

            # Send completion message
            await self._send_chat_message(
                websocket, {"type": "chat_complete", "message": full_response}
            )

        except Exception as e:
            logger.error(f"Error streaming AI response: {str(e)}")
            await self._send_chat_message(
                websocket,
                {
                    "type": "chat_error",
                    "message": f"Failed to generate response: {str(e)}",
                },
            )

    def _initialize_fallback_components(self) -> None:
        """Set up minimal components used in fallback mode."""
        if getattr(self, "_fallback_initialized", False):
            return

        self._fallback_mode = True

        self._fallback_dice = {
            "d4": lambda: random.randint(1, 4),  # noqa: S311
            "d6": lambda: random.randint(1, 6),  # noqa: S311
            "d8": lambda: random.randint(1, 8),  # noqa: S311
            "d10": lambda: random.randint(1, 10),  # noqa: S311
            "d12": lambda: random.randint(1, 12),  # noqa: S311
            "d20": lambda: random.randint(1, 20),  # noqa: S311
        }

        self._fallback_responses = {
            "combat": "You brace for combat, weapons ready.",
            "exploration": "You look around, taking in your surroundings.",
            "default": "The story continues...",
        }

        self._fallback_campaign_templates = {
            "fantasy": {
                "setting": "A classic fantasy realm",
                "themes": ["heroism", "magic"],
                "locations": ["village", "forest"],
                "npcs": ["innkeeper", "guard"],
            },
            "modern": {
                "setting": "A bustling modern city",
                "themes": ["mystery", "action"],
                "locations": ["downtown", "subway"],
                "npcs": ["detective", "shopkeeper"],
            },
            "sci-fi": {
                "setting": "A distant space colony",
                "themes": ["exploration", "technology"],
                "locations": ["spaceport", "alien ruins"],
                "npcs": ["android", "alien"],
            },
        }

        self._fallback_initialized = True

    def _fallback_dice_roll(self, notation: str) -> dict[str, Any]:
        """Roll dice based on notation like '2d6+1'."""
        match = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", notation.strip())
        if not match:
            return {"error": "Invalid dice notation"}

        num = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        rolls = [random.randint(1, sides) for _ in range(num)]  # noqa: S311
        total = sum(rolls) + modifier
        return {
            "notation": notation,
            "rolls": rolls,
            "total": total,
            "modifier": modifier,
        }

    def _fallback_generate_response(self, context: str) -> str:
        """Return canned response for a context."""
        self._initialize_fallback_components()
        return self._fallback_responses.get(
            context, self._fallback_responses["default"]
        )

    def _handle_fallback_dice_roll(self, text: str) -> dict[str, Any]:
        """Extract dice notation from text and roll."""
        self._initialize_fallback_components()
        result = DiceRoller.parse_dice_from_text(text)
        if result is None:
            return {"error": "Invalid dice notation"}
        return result

    async def _process_input_fallback(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process player input without external services."""
        self._initialize_fallback_components()

        # Add AI model not configured warning prefix
        ai_warning = "[AI model not configured] "

        response = {
            "message": "",
            "narration": "",
            "state_updates": {},
            "visuals": [],
            "combat_updates": None,
            "fallback_mode": True,
        }

        if not user_input:
            response["message"] = f"{ai_warning}No action taken."
            response["narration"] = "Silence hangs in the air."
            return response

        lower = user_input.lower()
        if "roll" in lower:
            dice_result = self._handle_fallback_dice_roll(user_input)
            response["dice_result"] = dice_result
            response["message"] = dice_result.get(
                "error", f"{ai_warning}You rolled {dice_result['total']}"
            )
            response["narration"] = "The dice clatter across the table."
            return response

        if "attack" in lower:
            response["message"] = f"{ai_warning}You attack your foe."
            response["narration"] = "You lunge forward in a swift strike."
            return response

        response["message"] = f"{ai_warning}You continue your journey."
        response["narration"] = self._fallback_generate_response("exploration")
        return response

    async def _process_input_stream_fallback(
        self, user_input: str, context: dict[str, Any]
    ) -> None:
        """Stream fallback response over WebSocket."""
        websocket = context.get("websocket")
        if not websocket:
            return

        # Send initial warning about AI model not being configured
        await websocket.send_text(
            json.dumps(
                {"type": "chat_start_stream", "message": "[AI model not configured] "}
            )
        )

        result = await self._process_input_fallback(user_input, context)
        await websocket.send_text(
            json.dumps({"type": "chat_complete", "message": result["message"]})
        )

    async def _send_chat_message(self, websocket, message: dict[str, Any]) -> None:
        """Send a message through the WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as exc:
            logger.error(f"Error sending chat message: {exc}")


# Lazy singleton instance
_dungeon_master = None


def get_dungeon_master():
    """Get the dungeon master instance, creating it if necessary."""
    global _dungeon_master
    if _dungeon_master is None:
        _dungeon_master = DungeonMasterAgent()
    return _dungeon_master


# For backward compatibility during import-time checks
dungeon_master = None
