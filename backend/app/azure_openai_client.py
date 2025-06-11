"""Azure OpenAI client for asynchronous chat completion and image generation calls."""

from __future__ import annotations

from typing import Any, Dict, List

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


class AzureOpenAIClient:
    """Client wrapper around openai for Azure OpenAI Service."""

    def __init__(self) -> None:
        openai.api_type = "azure"
        openai.api_version = settings.azure_openai_api_version
        openai.api_key = settings.azure_openai_api_key
        openai.base_url = settings.azure_openai_endpoint

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
        response = await openai.ChatCompletion.acreate(
            deployment_id=deployment_name,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message["content"].strip()

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3)
    )
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        deployment: str | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate an image using Azure OpenAI DALL-E."""
        deployment_name = deployment or settings.azure_openai_dalle_deployment
        try:
            response = await openai.Image.acreate(
                deployment_id=deployment_name,
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
                    "image_url": image_data.get("url"),
                    "revised_prompt": image_data.get("revised_prompt", prompt),
                    "size": size,
                    "quality": quality,
                    "style": style
                }
            else:
                return {
                    "success": False,
                    "error": "No image data returned from Azure OpenAI"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate image: {str(e)}"
            }
