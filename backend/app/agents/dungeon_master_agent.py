"""
Dungeon Master Agent - The orchestrator agent that coordinates all other agents.
"""
import logging
from typing import Dict, Any, List

import semantic_kernel as sk
from semantic_kernel.orchestration.context_variables import ContextVariables
from semantic_kernel.tools.tool_manager import ToolManager

from app.kernel_setup import kernel_manager

logger = logging.getLogger(__name__)

class DungeonMasterAgent:
    """
    Dungeon Master Agent that acts as the orchestrator for all other agents.
    This is the primary user-facing agent that manages player interactions and conversation flow.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent with its own kernel instance."""
        self.kernel = kernel_manager.create_kernel()
        self.tool_manager = ToolManager(self.kernel)
        self._register_plugins()

    def _register_plugins(self):
        """Register necessary plugins for the Dungeon Master agent."""
        # Will register plugins once implemented
        pass

    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Process user input and coordinate responses from specialized agents.

        Args:
            user_input: The player's input text
            context: Additional context information (game state, etc.)

        Returns:
            str: The response to the player
        """
        if not context:
            context = {}

        logger.info(f"Processing player input: {user_input}")

        try:
            # Create context variables
            variables = ContextVariables()
            variables["input"] = user_input

            # Add game context variables
            for key, value in context.items():
                if isinstance(value, str):
                    variables[key] = value

            # TODO: Add logic to determine which specialized agent(s) to invoke

            # For now, return a placeholder response
            return f"Dungeon Master: I understand your request '{user_input}'. We're still setting up the adventure. Please try again soon!"

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return "I'm sorry, I encountered an issue processing your request. Please try again."

# Singleton instance
dungeon_master = DungeonMasterAgent()
