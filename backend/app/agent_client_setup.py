"""Microsoft Agent Framework chat runtime for the AI Dungeon Master.

The single LLM chat path: an ``agent-framework`` ``FoundryChatClient`` (GA
Microsoft Agent Framework, ``agent_framework.foundry``) targeting the Foundry
project endpoint with ``DefaultAzureCredential``.  Availability is config-based
(``settings.is_foundry_configured()``); when unconfigured, callers fall back to
deterministic logic.  Supersedes the classic azure-ai-agents Threads/Runs path
and the hand-rolled azure-ai-inference chat client (see ADR-0023).
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.azure_openai_client import guarded_azure_call
from app.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from agent_framework.foundry import FoundryChatClient

logger = logging.getLogger(__name__)


class AgentClientManager:
    """Manages the Foundry chat client and provides chat/streaming helpers.

    The chat methods mirror the message-list-in / text-out shape the agents
    expect, are guarded by the shared circuit breaker, and raise on failure so
    agents fall back deterministically.
    """

    def __init__(self) -> None:
        self._client: FoundryChatClient | None = None
        self._tracer: trace.Tracer | None = None

    # -----------------------------------------------------------------
    # Availability
    # -----------------------------------------------------------------

    def get_chat_client(self) -> AgentClientManager | None:
        """Return an availability sentinel: ``self`` when Foundry is configured.

        Agents treat a ``None`` return as "operate in fallback mode".
        """
        return self if settings.is_foundry_configured() else None

    def is_fallback_mode(self) -> bool:
        """True when the Foundry chat path is unavailable (config-based)."""
        return not settings.is_foundry_configured()

    def _get_client(self) -> FoundryChatClient:
        """Lazily build and cache the FoundryChatClient."""
        if self._client is not None:
            return self._client
        if not settings.azure_ai_project_endpoint:
            raise ValueError(
                "Microsoft Foundry project endpoint is not configured. "
                "Set AZURE_AI_PROJECT_ENDPOINT to your Foundry project endpoint "
                "(https://<account>.services.ai.azure.com/api/projects/<project>)."
            )
        from agent_framework.foundry import FoundryChatClient
        from azure.identity.aio import DefaultAzureCredential

        self._client = FoundryChatClient(
            project_endpoint=settings.azure_ai_project_endpoint,
            credential=DefaultAzureCredential(),
        )
        logger.info("FoundryChatClient initialised for Agent Framework chat")
        return self._client

    @staticmethod
    def _to_messages(messages: list[dict[str, str]]) -> list[Any]:
        from agent_framework import Message

        return [Message(m["role"], [m["content"]]) for m in messages]

    @staticmethod
    def _options(
        deployment: str | None, temperature: float | None, max_tokens: int | None
    ) -> dict[str, Any]:
        options: dict[str, Any] = {}
        if deployment:
            options["model"] = deployment
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["max_tokens"] = max_tokens
        return options

    # -----------------------------------------------------------------
    # Chat
    # -----------------------------------------------------------------

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        deployment: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **_kwargs: Any,  # noqa: ANN401 - accept/ignore legacy kwargs
    ) -> str:
        """Generate a chat completion via the Foundry chat client.

        Raises on any failure (breaker open, network, service) so the calling
        agent can fall back deterministically.
        """
        client = self._get_client()
        response = await guarded_azure_call(
            client.get_response(
                self._to_messages(messages),
                options=self._options(
                    deployment or settings.azure_openai_chat_deployment,
                    temperature,
                    max_tokens,
                ),
            )
        )
        return (response.text or "").strip()

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        deployment: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **_kwargs: Any,  # noqa: ANN401
    ) -> AsyncIterator[str]:
        """Stream a chat completion via the Foundry chat client."""
        import pybreaker

        from app.azure_openai_client import azure_circuit_breaker

        if azure_circuit_breaker.current_state == pybreaker.STATE_OPEN:
            raise pybreaker.CircuitBreakerError("Azure circuit breaker is open")

        client = self._get_client()
        stream = client.get_response(
            self._to_messages(messages),
            stream=True,
            options=self._options(
                deployment or settings.azure_openai_chat_deployment,
                temperature,
                max_tokens,
            ),
        )
        async for update in stream:
            if update.text:
                yield update.text

    # -----------------------------------------------------------------
    # Observability & cleanup
    # -----------------------------------------------------------------

    def setup_observability(self) -> None:
        """Configure OpenTelemetry tracing (Azure Monitor when available)."""
        try:
            provider = TracerProvider()
            connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
            if connection_string:
                try:
                    from azure.monitor.opentelemetry.exporter import (  # noqa: I001
                        AzureMonitorTraceExporter,
                    )
                    from opentelemetry.sdk.trace.export import BatchSpanProcessor

                    exporter = AzureMonitorTraceExporter(
                        connection_string=connection_string
                    )
                    provider.add_span_processor(BatchSpanProcessor(exporter))
                    logger.info("OpenTelemetry configured with Azure Monitor exporter")
                except ImportError:
                    logger.warning(
                        "azure-monitor exporter missing, falling back to console"
                    )
                    provider.add_span_processor(
                        SimpleSpanProcessor(ConsoleSpanExporter())
                    )
            else:
                provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(__name__)
            logger.info("OpenTelemetry observability configured")
        except Exception as e:
            logger.warning("Failed to setup observability: %s", e)

    def get_tracer(self) -> trace.Tracer | None:
        """Get the OpenTelemetry tracer, configuring it on first use."""
        if self._tracer is None:
            self.setup_observability()
        return self._tracer

    async def cleanup(self) -> None:
        """Close the Foundry chat client on shutdown."""
        if self._client is not None:
            close = getattr(self._client, "close", None)
            if close is not None:
                try:
                    await close()
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to close Foundry chat client: %s", exc)
            self._client = None


# Singleton instance for global access
agent_client_manager = AgentClientManager()
