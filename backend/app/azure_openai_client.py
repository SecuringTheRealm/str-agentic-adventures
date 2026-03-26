"""Azure OpenAI client for asynchronous chat completion and image generation calls."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Literal

from openai import AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


class AzureOpenAIClient:
    """Client wrapper around openai for Azure OpenAI Service."""

    def __init__(self) -> None:
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3)
    )
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        deployment: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        """Generate a chat completion from Azure OpenAI."""
        deployment_name = deployment or settings.azure_openai_chat_deployment

        # Convert messages to proper format for new SDK
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        response = await self.client.chat.completions.create(
            model=deployment_name,
            messages=formatted_messages,
            **kwargs,
        )
        return response.choices[0].message.content.strip()

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        deployment: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion from Azure OpenAI."""
        deployment_name = deployment or settings.azure_openai_chat_deployment

        # Convert messages to proper format for new SDK
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        # Force streaming to be enabled
        kwargs["stream"] = True

        response = await self.client.chat.completions.create(
            model=deployment_name,
            messages=formatted_messages,
            **kwargs,
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3)
    )
    async def generate_image(
        self,
        prompt: str,
        size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
        quality: Literal["low", "medium", "high"] = "medium",
        deployment: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Generate an image using Azure OpenAI gpt-image-1.

        Returns a dict with b64_json image data (as a data URI) on success.
        """
        deployment_name = deployment or settings.azure_openai_dalle_deployment
        try:
            response = await self.client.images.generate(
                model=deployment_name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
                **kwargs,
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
        """Return True if Azure OpenAI credentials are present."""
        return (
            bool(settings.azure_openai_endpoint)
            and bool(settings.azure_openai_api_key)
            and bool(settings.azure_openai_chat_deployment)
        )


# Module-level singleton – import and use this instead of instantiating AzureOpenAIClient directly.
azure_openai_client = AzureOpenAIClient()
