"""Base class for all AI agents: shared client setup and fallback logic."""

from __future__ import annotations

import logging

from app.agent_client_setup import agent_client_manager
from app.azure_openai_client import (
    AzureOpenAIClient,
    azure_circuit_breaker,  # noqa: F401 - re-exported for main.py /health
    azure_openai_client,
)
from app.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for AI agents providing shared client setup and fallback logic.

    Chat-driven agents point ``self.azure_client`` at ``agent_client_manager``
    (the Foundry chat runtime); image agents call ``_init_azure_client()`` to
    attach the images-only Azure OpenAI helper.  Subclasses set ``agent_name``
    and optionally ``deployment_setting`` (per-agent chat model, F03).
    """

    agent_name: str = "Base"  # Override in subclasses
    # Settings attribute naming this agent's chat deployment override (F03).
    deployment_setting: str = "azure_openai_chat_deployment"

    def __init__(self) -> None:
        """Initialise shared client setup and fallback detection."""
        self.azure_client: AzureOpenAIClient | None = None

        # Availability sentinel: None => Foundry chat unavailable => fallback.
        self.chat_client = agent_client_manager.get_chat_client()
        self._fallback_mode = self.chat_client is None
        if self._fallback_mode:
            logger.warning(
                "%s agent operating in fallback mode - Foundry chat not configured",
                self.agent_name,
            )
        else:
            logger.info("%s agent initialised with Agent Framework chat", self.agent_name)

        self._post_init()

    def _post_init(self) -> None:
        """Hook for subclass-specific initialisation after client setup."""

    def _init_azure_client(self) -> None:
        """Attach the images-only Azure OpenAI helper (image agents only).

        Fallback for image agents is gated on image configuration, independent
        of the Foundry chat path.
        """
        if azure_openai_client.is_configured():
            self.azure_client = azure_openai_client
            self._fallback_mode = False
        else:
            self._fallback_mode = True

    @property
    def _deployment(self) -> str:
        """Resolve this agent's chat deployment (per-agent override, F03)."""
        return settings.deployment_for(self.deployment_setting)
