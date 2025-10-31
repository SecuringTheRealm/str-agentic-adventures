"""
Microsoft Agent Framework base infrastructure for AI Dungeon Master.

This module provides the foundation for all agents using Azure AI Agents SDK,
following Microsoft Agent Framework patterns for production-grade agent orchestration.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    AsyncFunctionTool,
    FunctionTool,
)
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from opentelemetry import trace

from app.config import settings

logger = logging.getLogger(__name__)


class AgentFrameworkManager:
    """
    Manager for Microsoft Agent Framework integration with Azure AI Agents SDK.

    Provides centralized agent creation, thread management, and orchestration
    following ADR-0018 guidelines for Azure AI Agents SDK adoption.
    """

    def __init__(self) -> None:
        """Initialize the Agent Framework manager."""
        self._agents_client: AgentsClient | None = None
        self._chat_client: ChatCompletionsClient | None = None
        self._is_configured = False
        self._fallback_mode = False
        self._tracer: trace.Tracer | None = None
        self._registered_agents: dict[str, Agent] = {}

    def get_agents_client(self) -> AgentsClient | None:
        """
        Get the Azure AI Agents client, creating it if necessary.

        Returns:
            Optional[AgentsClient]: Agents client, or None in fallback mode
        """
        if self._agents_client is not None:
            return self._agents_client

        if self._fallback_mode:
            return None

        if not self._is_configured:
            try:
                self._agents_client = self._create_agents_client()
                self._is_configured = True
                logger.info("Azure AI Agents client initialized successfully")
            except ValueError as e:
                logger.warning(
                    f"Azure OpenAI not configured, entering fallback mode: {e}"
                )
                self._fallback_mode = True
                return None
            except Exception as e:
                logger.error(f"Failed to initialize agents client: {e}")
                self._fallback_mode = True
                return None

        return self._agents_client

    def get_chat_client(self) -> ChatCompletionsClient | None:
        """
        Get the Azure OpenAI chat client for direct completions.

        Returns:
            Optional[ChatCompletionsClient]: Chat client, or None in fallback mode
        """
        if self._chat_client is not None:
            return self._chat_client

        if self._fallback_mode:
            return None

        try:
            self._chat_client = self._create_chat_client()
            logger.info("Azure OpenAI chat client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat client: {e}")
            return None

        return self._chat_client

    def _create_agents_client(self) -> AgentsClient:
        """
        Create and configure Azure AI Agents client.

        Returns:
            AgentsClient: Configured agents client

        Raises:
            ValueError: If Azure OpenAI configuration is missing
        """
        if not settings.is_azure_openai_configured():
            raise ValueError(
                "Azure OpenAI configuration is missing or invalid. "
                "This agentic demo requires proper Azure OpenAI setup."
            )

        try:
            # Try managed identity first, fall back to API key
            try:
                credential = DefaultAzureCredential()
            except Exception:
                credential = AzureKeyCredential(settings.azure_openai_api_key)

            # Azure AI Agents SDK requires project endpoint
            # For now, use the OpenAI endpoint directly
            agents_client = AgentsClient(
                endpoint=settings.azure_openai_endpoint,
                credential=credential,
            )

            logger.info("Azure AI Agents client configured successfully")
            return agents_client

        except Exception as e:
            logger.error(f"Failed to configure agents client: {str(e)}")
            raise

    def _create_chat_client(self) -> ChatCompletionsClient:
        """
        Create and configure Azure OpenAI chat client for direct completions.

        Returns:
            ChatCompletionsClient: Configured chat client
        """
        if not settings.is_azure_openai_configured():
            raise ValueError("Azure OpenAI configuration is missing or invalid.")

        try:
            credential = AzureKeyCredential(settings.azure_openai_api_key)

            chat_client = ChatCompletionsClient(
                endpoint=settings.azure_openai_endpoint,
                credential=credential,
                api_version=settings.azure_openai_api_version,
            )

            logger.info("Azure OpenAI chat client configured successfully")
            return chat_client

        except Exception as e:
            logger.error(f"Failed to configure chat client: {str(e)}")
            raise

    def create_agent(
        self,
        name: str,
        instructions: str,
        model: str | None = None,
        tools: list[FunctionTool | AsyncFunctionTool] | None = None,
        temperature: float = 0.7,
        description: str | None = None,
    ) -> Agent | None:
        """
        Create an agent using Azure AI Agents SDK.

        Args:
            name: Agent name
            instructions: System instructions for the agent
            model: Model deployment name (defaults to settings)
            tools: List of function tools the agent can use
            temperature: Sampling temperature (0-2)
            description: Agent description

        Returns:
            Optional[Agent]: Created agent, or None in fallback mode
        """
        client = self.get_agents_client()
        if client is None:
            logger.warning(f"Cannot create agent '{name}' in fallback mode")
            return None

        try:
            model_deployment = model or settings.azure_openai_chat_deployment

            agent = client.create_agent(
                model=model_deployment,
                name=name,
                instructions=instructions,
                tools=tools or [],
                temperature=temperature,
                description=description or f"{name} agent for AI Dungeon Master",
            )

            self._registered_agents[name] = agent
            logger.info(f"Agent '{name}' created successfully with ID: {agent.id}")
            return agent

        except Exception as e:
            logger.error(f"Failed to create agent '{name}': {str(e)}")
            return None

    def create_thread(self) -> AgentThread | None:
        """
        Create a new conversation thread for agent interactions.

        Returns:
            Optional[AgentThread]: Created thread, or None in fallback mode
        """
        client = self.get_agents_client()
        if client is None:
            logger.warning("Cannot create thread in fallback mode")
            return None

        try:
            thread = client.threads.create()
            logger.info(f"Thread created successfully with ID: {thread.id}")
            return thread

        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            return None

    def create_function_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        function: Callable,
    ) -> FunctionTool:
        """
        Create a function tool that agents can use.

        Args:
            name: Tool name
            description: Tool description for the agent
            parameters: JSON schema for tool parameters
            function: Python function to execute

        Returns:
            FunctionTool: Created function tool
        """
        return FunctionTool(
            name=name,
            description=description,
            parameters=parameters,
            function=function,
        )

    def setup_observability(self) -> None:
        """Setup OpenTelemetry for agent observability."""
        try:
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import (
                ConsoleSpanExporter,
                SimpleSpanProcessor,
            )

            # Setup tracer provider
            provider = TracerProvider()

            # Add console exporter for development
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)

            # Set the global tracer provider
            trace.set_tracer_provider(provider)

            # Get a tracer for this module
            self._tracer = trace.get_tracer(__name__)

            logger.info("OpenTelemetry observability configured")
        except Exception as e:
            logger.warning(f"Failed to setup observability: {e}")

    def get_tracer(self) -> trace.Tracer | None:
        """Get the OpenTelemetry tracer for agent operations."""
        if self._tracer is None:
            self.setup_observability()
        return self._tracer

    def is_fallback_mode(self) -> bool:
        """Check if framework manager is in fallback mode."""
        # Trigger initialization if not yet done
        self.get_agents_client()
        return self._fallback_mode

    def get_registered_agent(self, name: str) -> Agent | None:
        """
        Get a previously registered agent by name.

        Args:
            name: Agent name

        Returns:
            Optional[Agent]: Agent if found, None otherwise
        """
        return self._registered_agents.get(name)


# Singleton instance for global access
agent_framework_manager = AgentFrameworkManager()
