"""Base class for all AI agents with shared client initialization."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.agent_client_setup import agent_client_manager
from app.azure_openai_client import AzureOpenAIClient, azure_openai_client

if TYPE_CHECKING:
    from azure.ai.inference import ChatCompletionsClient

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for AI agents providing shared client setup and fallback logic."""

    agent_name: str = "Base"  # Override in subclasses

    def __init__(self) -> None:
        """Initialize shared client setup and fallback detection."""
        self._fallback_mode = False
        self.chat_client: ChatCompletionsClient | None = None
        self.azure_client: AzureOpenAIClient | None = None

        try:
            self.chat_client = agent_client_manager.get_chat_client()
            if self.chat_client is None:
                self._fallback_mode = True
                logger.warning(
                    "%s agent operating in fallback mode - Azure OpenAI not configured",
                    self.agent_name,
                )
            else:
                logger.info("%s agent initialized with Azure AI SDK", self.agent_name)
        except Exception as e:
            logger.warning(
                "Failed to initialize %s agent with Azure AI SDK: %s. "
                "Operating in fallback mode.",
                self.agent_name,
                e,
            )
            self._fallback_mode = True

        self._post_init()

    def _post_init(self) -> None:
        """Hook for subclass-specific initialization after client setup.

        Override this instead of __init__ to add custom setup logic.
        """

    def _init_azure_client(self) -> None:
        """Initialize the Azure OpenAI client for image generation.

        Call this in _post_init() for agents that need image generation.
        """
        if not self._fallback_mode:
            try:
                self.azure_client = azure_openai_client
            except Exception as e:
                logger.warning(
                    "Failed to initialize Azure OpenAI client for %s: %s",
                    self.agent_name,
                    e,
                )
                self._fallback_mode = True
