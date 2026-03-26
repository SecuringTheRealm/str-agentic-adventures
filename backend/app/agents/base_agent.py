"""Base class for all AI agents with shared client initialization and SDK lifecycle."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pybreaker

from app.agent_client_setup import agent_client_manager
from app.azure_openai_client import AzureOpenAIClient, azure_openai_client

if TYPE_CHECKING:
    from azure.ai.agents.models import FunctionToolDefinition
    from azure.ai.inference import ChatCompletionsClient

logger = logging.getLogger(__name__)

# Module-level circuit breaker for Azure OpenAI calls.
# Opens after 3 consecutive failures, auto-resets after 60 seconds.
azure_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=60,
    name="azure_openai",
)


class BaseAgent:
    """Base class for AI agents providing shared client setup, SDK lifecycle, and fallback logic.

    Subclasses should set ``agent_name`` and optionally override ``_post_init()``
    and ``_get_sdk_tools()`` to participate in the Microsoft Agent Framework lifecycle.
    """

    agent_name: str = "Base"  # Override in subclasses

    def __init__(self) -> None:
        """Initialize shared client setup and fallback detection."""
        self._fallback_mode = False
        self.chat_client: ChatCompletionsClient | None = None
        self.azure_client: AzureOpenAIClient | None = None

        # Microsoft Agent Framework SDK state
        self._agent_id: str | None = None
        self._sdk_thread_ids: dict[str, str] = {}

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

    # -----------------------------------------------------------------
    # Microsoft Agent Framework SDK helpers
    # -----------------------------------------------------------------

    @property
    def _sdk_available(self) -> bool:
        """Return True if the Microsoft Agent Framework SDK client is available."""
        return agent_client_manager.get_agents_client() is not None

    def _get_sdk_tools(self) -> list[FunctionToolDefinition]:
        """Return tool definitions to register with the SDK agent.

        Override in subclasses to register game-mechanics tools (dice, combat, etc.).
        """
        return []

    def _get_sdk_instructions(self) -> str:
        """Return system instructions for the SDK agent.

        Override in subclasses to supply agent-specific instructions.
        """
        return f"You are the {self.agent_name} agent."

    async def _ensure_agent_created(self) -> str | None:
        """Lazily create the SDK agent and cache the agent ID.

        Returns:
            The SDK agent ID, or None if the SDK is unavailable or creation fails.
        """
        if self._agent_id is not None:
            return self._agent_id

        if not self._sdk_available:
            return None

        result = await agent_client_manager.create_agent(
            name=self.agent_name,
            instructions=self._get_sdk_instructions(),
            tools=self._get_sdk_tools(),
        )
        if result is not None:
            self._agent_id = result["id"]
            logger.info(
                "%s SDK agent created (id=%s)", self.agent_name, self._agent_id
            )
        return self._agent_id

    async def _get_or_create_sdk_thread(self, session_id: str) -> str | None:
        """Get an existing SDK thread for a session, or create a new one.

        Args:
            session_id: Game session identifier used as the mapping key.

        Returns:
            The SDK thread ID, or None if the SDK is unavailable.
        """
        if session_id in self._sdk_thread_ids:
            return self._sdk_thread_ids[session_id]

        thread_id = await agent_client_manager.create_thread()
        if thread_id is not None:
            self._sdk_thread_ids[session_id] = thread_id
        return thread_id

    @property
    def _circuit_open(self) -> bool:
        """Return True if the circuit breaker is open (Azure deemed unavailable)."""
        return azure_circuit_breaker.current_state == pybreaker.STATE_OPEN

    async def _sdk_chat(
        self, session_id: str, user_message: str
    ) -> str | None:
        """Send a user message through the SDK agent and return the response.

        The call is guarded by the module-level circuit breaker.  When the
        breaker is open, we skip the Azure call entirely and return ``None``
        so that callers fall back to deterministic logic.

        Note: pybreaker's ``call_async`` relies on Tornado, which is not
        available in this project.  Instead we check ``_circuit_open`` before
        calling and drive ``_handle_success`` / ``_handle_error`` manually
        for pure-asyncio compatibility.

        Args:
            session_id: Game session identifier.
            user_message: The player's message.

        Returns:
            The agent's response text, or None if any step fails (caller
            should fall back to direct AzureOpenAIClient).
        """
        if self._circuit_open:
            logger.warning(
                "%s: circuit breaker open — returning fallback", self.agent_name
            )
            return None

        try:
            result = await self._sdk_chat_inner(session_id, user_message)
            # Record success so half-open transitions back to closed
            azure_circuit_breaker.state._handle_success()  # noqa: SLF001
            return result
        except Exception as exc:
            # Record failure; pybreaker will trip the breaker after fail_max
            azure_circuit_breaker.state._handle_error(exc, reraise=False)  # noqa: SLF001
            logger.warning(
                "%s: Azure call failed, circuit breaker recorded failure: %s",
                self.agent_name,
                exc,
            )
            return None

    async def _sdk_chat_inner(
        self, session_id: str, user_message: str
    ) -> str | None:
        """Inner SDK chat logic executed inside the circuit breaker."""
        agent_id = await self._ensure_agent_created()
        if agent_id is None:
            return None

        thread_id = await self._get_or_create_sdk_thread(session_id)
        if thread_id is None:
            return None

        added = await agent_client_manager.add_message(
            thread_id=thread_id, role="user", content=user_message
        )
        if not added:
            return None

        return await agent_client_manager.create_and_process_run(
            thread_id=thread_id, agent_id=agent_id
        )
