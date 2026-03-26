"""
Microsoft Agent Framework client setup and initialization for the AI Dungeon Master.

This module provides the AgentClientManager which manages the lifecycle of
Microsoft Agent Framework SDK clients (create agent, thread, message, run)
with automatic fallback to direct AzureOpenAIClient when the SDK is unavailable.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    FunctionToolDefinition,
    MessageRole,
    ThreadMessageOptions,
)
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.config import settings

if TYPE_CHECKING:
    from azure.ai.agents.models import Agent

logger = logging.getLogger(__name__)


class AgentClientManager:
    """Manager for Microsoft Agent Framework SDK clients and lifecycle operations.

    Provides methods to create agents, threads, messages, and runs via the SDK.
    All lifecycle methods return None on failure, enabling callers to fall back
    to the direct AzureOpenAIClient wrapper.
    """

    def __init__(self) -> None:
        """Initialize the agent client manager."""
        self._chat_client = None
        self._agents_client: AgentsClient | None = None
        self._is_configured = False
        self._fallback_mode = False
        self._tracer = None

    def get_chat_client(self) -> ChatCompletionsClient | None:
        """Get the Azure OpenAI chat client, creating it if necessary.

        Returns:
            Chat client, or None in fallback mode.
        """
        if self._chat_client is not None:
            return self._chat_client

        if self._fallback_mode:
            return None

        if not self._is_configured:
            try:
                self._chat_client = self._create_chat_client()
                self._is_configured = True
                logger.info("Azure OpenAI chat client initialized successfully")
            except ValueError as e:
                logger.warning(
                    "Azure OpenAI not configured, entering fallback mode: %s", e
                )
                self._fallback_mode = True
                return None
            except Exception as e:
                logger.error("Failed to initialize chat client: %s", e)
                self._fallback_mode = True
                return None

        return self._chat_client

    def get_agents_client(self) -> AgentsClient | None:
        """Get the Microsoft Agent Framework client, creating it if necessary.

        The agents client has its own initialisation path, independent of the
        chat client.  Failure here does NOT set ``_fallback_mode`` — that flag
        only controls the chat-completions path.

        Returns:
            Agents client, or None when unavailable.
        """
        if self._agents_client is not None:
            return self._agents_client

        if self._fallback_mode:
            return None

        try:
            self._agents_client = self._create_agents_client()
            logger.info(
                "Microsoft Agent Framework client initialized successfully"
            )
        except ValueError as e:
            logger.warning("Azure AI not configured for agents: %s", e)
            return None
        except Exception as e:
            logger.error("Failed to initialize agents client: %s", e)
            return None

        return self._agents_client

    # -----------------------------------------------------------------
    # Agent lifecycle methods
    # -----------------------------------------------------------------

    async def create_agent(
        self,
        name: str,
        instructions: str,
        tools: list[FunctionToolDefinition] | None = None,
        model: str | None = None,
    ) -> dict[str, Any] | None:
        """Create an agent via the Microsoft Agent Framework SDK.

        Args:
            name: Human-readable agent name.
            instructions: System-level instructions for the agent.
            tools: Optional list of FunctionToolDefinition instances.
            model: Model deployment name (defaults to chat deployment).

        Returns:
            Dict with ``id`` and ``name`` on success, or None on failure.
        """
        client = self.get_agents_client()
        if client is None:
            return None
        try:
            model = model or settings.azure_openai_chat_deployment
            agent: Agent = await client.create_agent(
                model=model,
                name=name,
                instructions=instructions,
                tools=tools or [],
            )
            logger.info("Created SDK agent: %s (id=%s)", name, agent.id)
            return {"id": agent.id, "name": name}
        except Exception as e:
            logger.warning("Failed to create SDK agent %s: %s", name, e)
            return None

    async def create_thread(self) -> str | None:
        """Create a conversation thread via the SDK.

        Returns:
            Thread ID string on success, or None on failure.
        """
        client = self.get_agents_client()
        if client is None:
            return None
        try:
            thread = await client.threads.create()
            logger.info("Created SDK thread: %s", thread.id)
            return thread.id
        except Exception as e:
            logger.warning("Failed to create SDK thread: %s", e)
            return None

    async def add_message(
        self, thread_id: str, role: str, content: str
    ) -> bool:
        """Add a message to an existing thread.

        Args:
            thread_id: The SDK thread identifier.
            role: Message role — ``"user"`` or ``"assistant"``.
            content: Message text content.

        Returns:
            True on success, False on failure.
        """
        client = self.get_agents_client()
        if client is None:
            return False
        try:
            sdk_role = MessageRole.USER if role == "user" else MessageRole.AGENT
            await client.messages.create(
                thread_id=thread_id,
                role=sdk_role,
                content=content,
            )
            return True
        except Exception as e:
            logger.warning("Failed to add message to thread %s: %s", thread_id, e)
            return False

    async def create_and_process_run(
        self, thread_id: str, agent_id: str
    ) -> str | None:
        """Create a run on an existing thread and wait for completion.

        Args:
            thread_id: The SDK thread identifier.
            agent_id: The SDK agent identifier.

        Returns:
            The assistant's response text on success, or None on failure.
        """
        client = self.get_agents_client()
        if client is None:
            return None
        try:
            run = await client.runs.create_and_process(
                thread_id=thread_id,
                agent_id=agent_id,
            )
            if run.status == "failed":
                logger.warning("SDK run failed: %s", run.last_error)
                return None

            # Retrieve the last assistant message from the thread
            messages = await client.messages.list(thread_id=thread_id)
            for msg in reversed(messages.data):
                if msg.role == "assistant" and msg.content:
                    for part in msg.content:
                        if hasattr(part, "text") and hasattr(part.text, "value"):
                            return part.text.value
            return None
        except Exception as e:
            logger.warning(
                "Failed to process run for agent %s: %s", agent_id, e
            )
            return None

    async def create_thread_and_process_run(
        self,
        agent_id: str,
        user_message: str,
        *,
        instructions: str | None = None,
    ) -> tuple[str | None, str | None]:
        """Create a new thread with a user message and run the agent in one call.

        This is a convenience wrapper around the SDK's combined operation.

        Args:
            agent_id: The SDK agent identifier.
            user_message: The initial user message.
            instructions: Optional instruction override for this run.

        Returns:
            Tuple of (thread_id, response_text), or (None, None) on failure.
        """
        client = self.get_agents_client()
        if client is None:
            return None, None
        try:
            thread_options = AgentThreadCreationOptions(
                messages=[
                    ThreadMessageOptions(role=MessageRole.USER, content=user_message)
                ]
            )
            run = await client.create_thread_and_process_run(
                agent_id=agent_id,
                thread=thread_options,
                instructions=instructions,
            )
            if run.status == "failed":
                logger.warning("SDK run failed: %s", run.last_error)
                return None, None

            thread_id = run.thread_id
            messages = await client.messages.list(thread_id=thread_id)
            response_text = None
            for msg in reversed(messages.data):
                if msg.role == "assistant" and msg.content:
                    for part in msg.content:
                        if hasattr(part, "text") and hasattr(part.text, "value"):
                            response_text = part.text.value
                            break
                    if response_text:
                        break
            return thread_id, response_text
        except Exception as e:
            logger.warning(
                "Failed to create thread and process run for agent %s: %s",
                agent_id,
                e,
            )
            return None, None

    # -----------------------------------------------------------------
    # Client creation helpers
    # -----------------------------------------------------------------

    def _create_chat_client(self) -> ChatCompletionsClient:
        """Create and configure Azure OpenAI chat client.

        Returns:
            Configured chat client.

        Raises:
            ValueError: If Azure OpenAI is not configured.
        """
        if not settings.is_azure_openai_configured():
            raise ValueError(
                "Azure OpenAI configuration is missing or invalid. "
                "This agentic demo requires proper Azure OpenAI setup. "
                "Please ensure the following environment variables are set: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            )

        try:
            credential = DefaultAzureCredential()

            chat_client = ChatCompletionsClient(
                endpoint=settings.azure_openai_endpoint,
                credential=credential,
                api_version=settings.azure_openai_api_version,
            )

            logger.info("Azure OpenAI chat client configured successfully")
            return chat_client

        except Exception as e:
            logger.error("Failed to configure chat client: %s", str(e))
            raise

    def _create_agents_client(self) -> AgentsClient:
        """Create and configure the Microsoft Agent Framework client.

        Uses the async DefaultAzureCredential since the AgentsClient from
        ``azure.ai.agents.aio`` requires an async token credential.

        Returns:
            Configured agents client.

        Raises:
            ValueError: If Azure AI project endpoint is not configured.
        """
        if not settings.azure_ai_project_endpoint:
            raise ValueError(
                "Azure AI project endpoint is not configured. "
                "Set AZURE_AI_PROJECT_ENDPOINT to your Foundry project endpoint "
                "(format: https://<account>.services.ai.azure.com/api/projects/<project>)."
            )

        try:
            # Async credential for the async AgentsClient
            credential = AsyncDefaultAzureCredential()

            agents_client = AgentsClient(
                endpoint=settings.azure_ai_project_endpoint,
                credential=credential,
            )

            logger.info(
                "Microsoft Agent Framework client configured successfully"
            )
            return agents_client

        except Exception as e:
            logger.error("Failed to configure agents client: %s", str(e))
            raise

    # -----------------------------------------------------------------
    # Observability
    # -----------------------------------------------------------------

    def setup_observability(self) -> None:
        """Setup OpenTelemetry for agent observability."""
        try:
            provider = TracerProvider()
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(__name__)
            logger.info("OpenTelemetry observability configured")
        except Exception as e:
            logger.warning("Failed to setup observability: %s", e)

    def get_tracer(self) -> trace.Tracer | None:
        """Get the OpenTelemetry tracer for agent operations."""
        if self._tracer is None:
            self.setup_observability()
        return self._tracer

    def is_fallback_mode(self) -> bool:
        """Check if agent client manager is in fallback mode."""
        # Trigger initialization if not yet done
        self.get_chat_client()
        return self._fallback_mode


# Singleton instance for global access
agent_client_manager = AgentClientManager()
