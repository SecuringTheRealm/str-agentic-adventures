"""
Dungeon Master Agent - Rebuilt with minimal, barebones functionality.

This is a ground-up rebuild focusing on a simple AI approach using system prompts
to meet PRD requirements, replacing the complex multi-agent orchestration.
"""

import logging
import random
import json
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class DungeonMasterAgent:
    """
    Simplified Dungeon Master Agent using system prompts to fulfill the role
    of orchestrating the D&D experience through AI guidance rather than 
    complex agent coordination.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent."""
        self._fallback_mode = False
        self.openai_client = None
        
        try:
            # Try to initialize Azure OpenAI client
            from app.azure_openai_client import AzureOpenAIClient
            self.openai_client = AzureOpenAIClient()
            logger.info("DM Agent initialized with Azure OpenAI support")
            
        except Exception as e:
            # Fall back to basic mode if Azure OpenAI is not configured
            error_msg = str(e)
            if (("validation errors for Settings" in error_msg and (
                "azure_openai" in error_msg or "openai" in error_msg
            )) or "Azure OpenAI configuration is missing or invalid" in error_msg):
                logger.warning(
                    "Azure OpenAI configuration is missing or invalid. "
                    "DM Agent operating in fallback mode with basic functionality."
                )
                self._fallback_mode = True
            else:
                # Re-raise other errors
                raise

    def _get_dm_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate a comprehensive system prompt that embodies the Dungeon Master role
        as specified in the PRD, replacing complex agent coordination.
        """
        character_info = ""
        if context.get("character_name"):
            character_info = f"The player character is {context.get('character_name', 'an adventurer')}, "
            character_info += f"a level {context.get('character_level', '1')} {context.get('character_class', 'fighter')}. "

        system_prompt = f"""You are an expert Dungeon Master for D&D 5e. You are the primary orchestrator of the tabletop RPG experience, responsible for:

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

        return system_prompt

    async def process_input(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user input using a simple AI approach with system prompts.
        
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
            return self._process_input_fallback(user_input, context)
        
        try:
            # Create system prompt
            system_prompt = self._get_dm_system_prompt(context)
            
            # Create user message with context
            user_message = user_input
            if context.get("character_name"):
                user_message = f"Player ({context['character_name']}): {user_input}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Get AI response
            ai_response = await self.openai_client.chat_completion(
                messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Structure the response in the expected format
            response = {
                "message": ai_response.strip() if ai_response else "The adventure continues...",
                "visuals": [],  # Simple implementation - no visual generation
                "state_updates": {"last_action": user_input},
                "combat_updates": None
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in DM processing: {str(e)}")
            # Fall back to using the full fallback processing which handles dice, etc.
            return self._process_input_fallback(user_input, context)

    async def process_input_stream(
        self, user_input: str, context: Dict[str, Any] = None
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
            await self._send_chat_message(websocket, {
                "type": "chat_typing",
                "message": "The Dungeon Master considers your action..."
            })
            
            # Create system prompt
            system_prompt = self._get_dm_system_prompt(context)
            
            # Create user message
            user_message = user_input
            if context.get("character_name"):
                user_message = f"Player ({context['character_name']}): {user_input}"
                
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Stream the AI response
            await self._stream_ai_response(messages, websocket)
            
        except Exception as e:
            logger.error(f"Error in streaming processing: {str(e)}")
            await self._send_chat_message(websocket, {
                "type": "chat_error",
                "message": "I encountered an issue processing your request. Please try again."
            })

    async def _stream_ai_response(self, messages: List[Dict[str, str]], websocket) -> None:
        """Stream AI response using Azure OpenAI."""
        try:
            # Send start streaming message
            await self._send_chat_message(websocket, {
                "type": "chat_start_stream",
                "message": ""
            })

            full_response = ""
            async for chunk in self.openai_client.chat_completion_stream(
                messages, 
                temperature=0.7, 
                max_tokens=500
            ):
                if chunk:
                    full_response += chunk
                    await self._send_chat_message(websocket, {
                        "type": "chat_stream",
                        "chunk": chunk,
                        "full_text": full_response
                    })

            # Send completion message
            await self._send_chat_message(websocket, {
                "type": "chat_complete",
                "message": full_response
            })
            
        except Exception as e:
            logger.error(f"Error streaming AI response: {str(e)}")
            await self._send_chat_message(websocket, {
                "type": "chat_error",
                "message": f"Failed to generate response: {str(e)}"
            })

    def _process_input_fallback(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input in fallback mode with basic responses."""
        logger.info("DM processing input in fallback mode")
        
        try:
            # Simple keyword-based responses
            input_lower = user_input.lower()
            
            # Handle dice rolls
            if any(dice in input_lower for dice in ["roll", "d4", "d6", "d8", "d10", "d12", "d20", "d100"]):
                dice_result = self._handle_fallback_dice_roll(user_input)
                return {
                    "message": f"You roll the dice: {dice_result.get('details', 'Dice rolled')}",
                    "dice_result": dice_result,
                    "visuals": [],
                    "state_updates": {"last_action": user_input},
                    "combat_updates": None
                }
            
            # Basic response patterns
            if any(word in input_lower for word in self.COMBAT_KEYWORDS):
                message = "You engage in combat! Your weapon gleams as you prepare to strike. Roll for your attack!"
            elif any(word in input_lower for word in self.EXPLORE_KEYWORDS):
                message = "You carefully explore the area, taking note of interesting details and potential secrets."
            elif any(word in input_lower for word in self.TALK_KEYWORDS):
                message = "Your words carry weight in this moment. The conversation develops based on your approach."
            elif any(word in input_lower for word in self.INVENTORY_KEYWORDS):
                message = "You check your belongings and assess your available resources."
            else:
                message = f"You {user_input.lower()}. The world responds to your actions, and the adventure continues."
            
            return {
                "message": message,
                "visuals": [],
                "state_updates": {"last_action": user_input},
                "combat_updates": None,
                "fallback_mode": True
            }
            
        except Exception as e:
            logger.error(f"Error in fallback processing: {str(e)}")
            return {
                "message": "The adventure continues, though the path ahead is uncertain.",
                "visuals": [],
                "state_updates": {},
                "combat_updates": None,
                "fallback_mode": True,
                "error": str(e)
            }

    async def _process_input_stream_fallback(
        self, user_input: str, context: Dict[str, Any]
    ) -> None:
        """Process input in fallback mode with streaming simulation."""
        websocket = context.get("websocket")
        if not websocket:
            return
            
        logger.info("DM processing streaming input in fallback mode")
        
        try:
            # Simulate typing
            await self._send_chat_message(websocket, {
                "type": "chat_typing",
                "message": "Preparing response..."
            })
            
            # Get basic response
            result = self._process_input_fallback(user_input, context)
            response_text = result.get("message", "The adventure continues...")
            
            # Stream the response word by word
            await self._simulate_streaming_response(response_text, websocket)
            
        except Exception as e:
            logger.error(f"Error in fallback streaming: {str(e)}")
            await self._send_chat_message(websocket, {
                "type": "chat_error",
                "message": "The adventure continues, though the path is unclear."
            })

    async def _simulate_streaming_response(self, response_text: str, websocket) -> None:
        """Simulate streaming by sending text word by word."""
        import asyncio
        
        await self._send_chat_message(websocket, {
            "type": "chat_start_stream",
            "message": ""
        })

        words = response_text.split()
        full_response = ""
        
        for i, word in enumerate(words):
            if i > 0:
                full_response += " "
            full_response += word
            
            await self._send_chat_message(websocket, {
                "type": "chat_stream", 
                "chunk": f"{' ' if i > 0 else ''}{word}",
                "full_text": full_response
            })
            
            # Small delay to simulate real streaming
            await asyncio.sleep(0.1)

        await self._send_chat_message(websocket, {
            "type": "chat_complete",
            "message": full_response
        })

    async def _send_chat_message(self, websocket, message: Dict[str, Any]) -> None:
        """Send a message via WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")

    def _handle_fallback_dice_roll(self, user_input: str) -> Dict[str, Any]:
        """Handle dice rolling in fallback mode."""
        import re
        
        # Extract dice notation from input
        dice_patterns = [
            r"(\d*d\d+(?:[+-]\d+)?)",  # Standard notation like 2d6+3
            r"roll\s+(\d*d\d+)",       # "roll 2d6"
            r"(\d+)d(\d+)",            # Simple XdY format
        ]
        
        for pattern in dice_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                if len(match.groups()) == 1:
                    dice_notation = match.group(1)
                else:
                    # Handle XdY format
                    num_dice = match.group(1) or "1"
                    die_size = match.group(2)
                    dice_notation = f"{num_dice}d{die_size}"
                
                return self._fallback_dice_roll(dice_notation)
        
        # Default to d20 if no specific dice found
        return self._fallback_dice_roll("1d20")

    def _fallback_dice_roll(self, dice_notation: str) -> Dict[str, Any]:
        """Simple dice rolling for fallback mode."""
        import re
        
        try:
            # Parse dice notation (e.g., "2d6+3", "1d20")
            match = re.match(r"(\d+)?d(\d+)([+-]\d+)?", dice_notation.lower())
            if not match:
                return {"error": f"Invalid dice notation: {dice_notation}"}
            
            num_dice = int(match.group(1)) if match.group(1) else 1
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            # Roll the dice
            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            return {
                "notation": dice_notation,
                "rolls": rolls,
                "modifier": modifier,
                "total": total,
                "details": f"Rolled {rolls} + {modifier} = {total}"
            }
            
        except Exception as e:
            return {"error": f"Error rolling dice: {str(e)}"}

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
