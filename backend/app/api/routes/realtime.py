"""Realtime voice token endpoint for WebRTC connections."""

import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("/token")
async def get_realtime_token() -> dict:
    """Mint an ephemeral WebRTC token for the Azure Foundry realtime API.

    Returns:
        Dict with token, endpoint, deployment, and voice config.
    """
    if not settings.azure_openai_endpoint:
        raise HTTPException(status_code=503, detail="Azure OpenAI endpoint not configured")

    try:
        # Use API key if available (dev), otherwise managed identity
        endpoint = settings.azure_openai_endpoint.rstrip("/")

        if settings.azure_openai_api_key:
            headers = {
                "api-key": settings.azure_openai_api_key,
                "Content-Type": "application/json",
            }
        else:
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json",
            }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{endpoint}/openai/realtime/sessions?api-version=2025-04-01-preview",
                headers=headers,
                json={
                    "model": "gpt-realtime-mini",
                    "voice": "ballad",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        return {
            "token": data.get("client_secret", {}).get("value"),
            "endpoint": endpoint,
            "deployment": "gpt-realtime-mini",
            "voice": "ballad",
            "expires_at": data.get("client_secret", {}).get("expires_at"),
        }

    except httpx.HTTPStatusError as e:
        logger.error("Failed to mint realtime token: HTTP %s — %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=502, detail="Failed to create realtime session token") from e
    except Exception as e:
        logger.error("Failed to mint realtime token: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create realtime session token") from e
