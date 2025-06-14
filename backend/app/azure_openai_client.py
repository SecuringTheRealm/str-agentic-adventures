"""Azure OpenAI client for asynchronous chat completion and image generation calls."""

from __future__ import annotations

from typing import Any, Dict, List, Literal

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
        messages: List[Dict[str, str]],
        deployment: str | None = None,
        **kwargs: Any,
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
        messages: List[Dict[str, str]],
        deployment: str | None = None,
        **kwargs: Any,
    ):
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
        quality: Literal["standard", "hd"] = "standard",
        style: Literal["vivid", "natural"] = "vivid",
        deployment: str | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate an image using Azure OpenAI DALL-E."""
        deployment_name = deployment or settings.azure_openai_dalle_deployment
        try:
            # Use the new OpenAI SDK 1.0+ API for images
            response = await self.client.images.generate(
                model=deployment_name,
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1,
                **kwargs,
            )

            if response and response.data:
                image_data = response.data[0]
                return {
                    "success": True,
                    "image_url": image_data.url,
                    "revised_prompt": getattr(image_data, "revised_prompt", prompt),
                    "size": size,
                    "quality": quality,
                    "style": style,
                }
            else:
                return {
                    "success": False,
                    "error": "No image data returned from Azure OpenAI",
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to generate image: {str(e)}"}
