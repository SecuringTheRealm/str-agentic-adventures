"""
Azure AI Agent client setup and initialization for the AI Dungeon Master.

This module replaces the previous Semantic Kernel implementation with
Azure AI Agents SDK for production-grade agent orchestration.
"""

from __future__ import annotations

import logging

from azure.ai.agents import AgentsClient
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.config import settings

logger = logging.getLogger(__name__)


class AgentClientManager:
    """Manager class for creating and configuring Azure AI Agent clients."""

    def __init__(self) -> None:
        """Initialize the agent client manager."""
        self._chat_client = None
        self._agents_client = None
        self._is_configured = False
        self._fallback_mode = False
        self._tracer = None

    def get_chat_client(self) -> ChatCompletionsClient | None:
        """
        Get the Azure OpenAI chat client, creating it if necessary.

        Returns:
            Optional[ChatCompletionsClient]: Chat client, or None in fallback mode
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
                logger.info("Azure AI Agents client initialized successfully")
            except ValueError as e:
                logger.warning(
                    "Azure AI not configured, entering fallback mode: %s", e
                )
                self._fallback_mode = True
                return None
            except Exception as e:
                logger.error("Failed to initialize agents client: %s", e)
                self._fallback_mode = True
                return None

        return self._agents_client

    def _create_chat_client(self) -> ChatCompletionsClient:
        """
        Create and configure Azure OpenAI chat client.

        Returns:
            ChatCompletionsClient: Configured chat client
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
            # Use DefaultAzureCredential for managed identity / local dev auth
            credential = DefaultAzureCredential()

            chat_client = ChatCompletionsClient(
                endpoint=settings.azure_openai_endpoint,
                credential=credential,
                api_version=settings.azure_openai_api_version,
            )

            logger.info(
                "Azure OpenAI chat client configured successfully"
            )
            return chat_client

        except Exception as e:
            logger.error("Failed to configure chat client: %s", str(e))
            raise

    def _create_agents_client(self) -> AgentsClient:
        """
        Create and configure Azure AI Agents client.

        Returns:
            AgentsClient: Configured agents client

        Raises:
            ValueError: If Azure AI project endpoint is not configured
        """
        if not settings.azure_ai_project_endpoint:
            raise ValueError(
                "Azure AI project endpoint is not configured. "
                "Set AZURE_AI_PROJECT_ENDPOINT to your Foundry project endpoint "
                "(format: https://<account>.services.ai.azure.com/api/projects/<project>)."
            )

        try:
            # Use DefaultAzureCredential for managed identity / local dev auth
            credential = DefaultAzureCredential()

            agents_client = AgentsClient(
                endpoint=settings.azure_ai_project_endpoint,
                credential=credential,
            )

            logger.info(
                "Azure AI Agents client configured successfully"
            )
            return agents_client

        except Exception as e:
            logger.error("Failed to configure agents client: %s", str(e))
            raise

    def setup_observability(self) -> None:
        """Setup OpenTelemetry for agent observability."""
        try:
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
