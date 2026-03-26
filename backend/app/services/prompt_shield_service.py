"""Async service for Azure AI Content Safety Prompt Shields API."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

logger = logging.getLogger(__name__)


@dataclass
class ShieldResult:
    """Result from the Prompt Shields API."""

    user_prompt_attack_detected: bool
    document_attack_detected: bool

    @property
    def attack_detected(self) -> bool:
        """Return True if any attack was detected."""
        return self.user_prompt_attack_detected or self.document_attack_detected


class PromptShieldService:
    """Calls Azure AI Content Safety Prompt Shields API before messages reach LLM.

    Authenticates via API key when ``CONTENT_SAFETY_API_KEY`` is set, otherwise
    falls back to managed identity (DefaultAzureCredential).
    """

    def __init__(self) -> None:
        self._endpoint = os.getenv("CONTENT_SAFETY_ENDPOINT")
        self._api_key = os.getenv("CONTENT_SAFETY_API_KEY")
        self._is_configured = bool(self._endpoint)
        self._credential: AsyncDefaultAzureCredential | None = None
        if not self._is_configured:
            logger.warning("CONTENT_SAFETY_ENDPOINT not set — Prompt Shields disabled.")

    def is_configured(self) -> bool:
        """Return True if the service is configured with an endpoint."""
        return self._is_configured

    async def check_user_input(
        self, user_input: str, documents: list[str] | None = None
    ) -> ShieldResult:
        """Check user input for prompt injection attacks.

        Args:
            user_input: The user's message to check.
            documents: Optional list of documents to check for indirect attacks.

        Returns:
            ShieldResult indicating whether an attack was detected.
            Fails open (returns False/False) on API errors to avoid blocking users.
        """
        if not self._is_configured:
            return ShieldResult(False, False)

        url = (
            f"{self._endpoint.rstrip('/')}"
            "/contentsafety/text:shieldPrompt?api-version=2024-09-01"
        )
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Ocp-Apim-Subscription-Key"] = self._api_key
        else:
            # Use managed identity when no API key is provided
            try:
                if self._credential is None:
                    from azure.identity.aio import DefaultAzureCredential as _Cred

                    self._credential = _Cred()
                token = await self._credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                )
                headers["Authorization"] = f"Bearer {token.token}"
            except Exception as exc:
                logger.error("Failed to acquire managed identity token: %s", exc)
                return ShieldResult(False, False)  # fail open

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    url,
                    json={"userPrompt": user_input, "documents": documents or []},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return ShieldResult(
                        user_prompt_attack_detected=data.get(
                            "userPromptAnalysis", {}
                        ).get("attackDetected", False),
                        document_attack_detected=any(
                            d.get("attackDetected", False)
                            for d in data.get("documentsAnalysis", [])
                        ),
                    )
                logger.error("Prompt Shields API returned %s", resp.status)
                return ShieldResult(False, False)  # fail open
        except Exception as exc:
            logger.error("Prompt Shields check failed: %s", exc)
            return ShieldResult(False, False)  # fail open


prompt_shield_service = PromptShieldService()
