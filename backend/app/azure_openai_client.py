"""Azure OpenAI image-generation helper.

Chat/completions run through the Microsoft Agent Framework FoundryChatClient
(see ``agent_client_setup.py``).  This module is the sanctioned, thin
images-only wrapper around the platform ``openai`` SDK (``AsyncAzureOpenAI``)
for the gpt-image-1 family, which the Agent/Responses surface does not cover.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Awaitable
from typing import Any, Literal

import pybreaker
from openai import AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

# Shared circuit breaker for all Azure AI calls (chat via the Agent Framework
# client and image generation here).  Opens after 3 consecutive failures and
# auto-resets after 60 seconds.  /health/dependencies reports its state.
azure_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=60,
    name="azure_openai",
)


async def guarded_azure_call[T](awaitable: Awaitable[T]) -> T:
    """Run an Azure AI coroutine under the shared circuit breaker.

    Skips the call (raising ``CircuitBreakerError``) while the breaker is open,
    records success/failure via pybreaker's public sync ``call()`` API, and
    re-raises so callers can fall back deterministically.
    """
    if azure_circuit_breaker.current_state == pybreaker.STATE_OPEN:
        raise pybreaker.CircuitBreakerError("Azure circuit breaker is open")
    try:
        result = await awaitable
    except Exception as exc:
        _record_failure(exc)
        raise
    azure_circuit_breaker.call(lambda: None)  # record success
    return result


def _record_failure(error: Exception) -> None:
    """Record a failure in the circuit breaker via its public API."""
    with contextlib.suppress(Exception):
        azure_circuit_breaker.call(_raise, error)


def _raise(error: Exception) -> None:
    raise error


class AzureOpenAIClient:
    """Thin wrapper around ``AsyncAzureOpenAI`` for image generation only.

    Uses managed identity (DefaultAzureCredential) by default and falls back to
    an API key when ``AZURE_OPENAI_API_KEY`` is set (local development).
    """

    def __init__(self) -> None:
        if settings.azure_openai_api_key:
            logger.info("Initialising Azure OpenAI image client with API key auth")
            self.client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
        else:
            logger.info("Initialising Azure OpenAI image client with managed identity")
            from azure.identity.aio import (
                DefaultAzureCredential,
                get_bearer_token_provider,
            )

            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            self.client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3)
    )
    async def generate_image(
        self,
        prompt: str,
        size: Literal["1024x1024", "1536x1024", "1024x1536", "auto"] = "1024x1024",
        quality: Literal["low", "medium", "high"] = "medium",
        deployment: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Generate an image using the Azure OpenAI gpt-image-1 family.

        Returns a dict with b64_json image data (as a data URI) on success.
        """
        deployment_name = deployment or settings.azure_openai_dalle_deployment
        try:
            response = await guarded_azure_call(
                self.client.images.generate(
                    model=deployment_name,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1,
                    **kwargs,
                )
            )

            if response and response.data:
                image_data = response.data[0]
                b64 = image_data.b64_json
                data_uri = f"data:image/png;base64,{b64}"
                return {
                    "success": True,
                    "image_url": data_uri,
                    "b64_json": b64,
                    "revised_prompt": getattr(image_data, "revised_prompt", prompt),
                    "size": size,
                    "quality": quality,
                }
            return {
                "success": False,
                "error": "No image data returned from Azure OpenAI",
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to generate image: {str(e)}"}

    def is_configured(self) -> bool:
        """Return True if Azure OpenAI image generation is configured."""
        return settings.is_azure_openai_configured()


# Module-level singleton – import and use this instead of instantiating directly.
azure_openai_client = AzureOpenAIClient()
