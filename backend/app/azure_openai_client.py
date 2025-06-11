"""Azure OpenAI client for asynchronous chat completion calls."""

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
