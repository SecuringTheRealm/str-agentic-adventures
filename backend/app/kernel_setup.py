"""
Semantic Kernel setup and initialization for the AI Dungeon Master.
"""

import logging
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
)

from app.config import settings

logger = logging.getLogger(__name__)


class KernelManager:
    """Manager class for creating and configuring Semantic Kernel instances."""

    def __init__(self):
        """Initialize the kernel manager."""
        self._shared_kernel = None
        self._is_configured = False
        self._fallback_mode = False

    def get_kernel(self) -> Optional[sk.Kernel]:
        """
        Get the shared Semantic Kernel instance, creating it if necessary.

        Returns:
            Optional[sk.Kernel]: Configured Semantic Kernel instance, or None in fallback mode
        """
        # Return cached kernel if already created
        if self._shared_kernel is not None:
            return self._shared_kernel

        # Return None if we're in fallback mode
        if self._fallback_mode:
            return None

        # Try to create kernel if not already configured
        if not self._is_configured:
            try:
                self._shared_kernel = self._create_kernel()
                self._is_configured = True
                logger.info("Shared Semantic Kernel initialized successfully")
            except ValueError as e:
                # Configuration error - enter fallback mode
                logger.warning(
                    f"Azure OpenAI not configured, entering fallback mode: {e}"
                )
                self._fallback_mode = True
                return None
            except Exception as e:
                # Other errors - log and enter fallback mode
                logger.error(f"Failed to initialize Semantic Kernel: {e}")
                self._fallback_mode = True
                return None

        return self._shared_kernel

    def _create_kernel(self) -> sk.Kernel:
        """
        Create and configure a new Semantic Kernel instance.

        Returns:
            sk.Kernel: Configured Semantic Kernel instance
        """
        # Check if Azure OpenAI is configured before trying to use it
        if not settings.is_azure_openai_configured():
            raise ValueError(
                "Azure OpenAI configuration is missing or invalid. "
                "This agentic demo requires proper Azure OpenAI setup. "
                "Please ensure the following environment variables are set: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            )

        # Create a new kernel
        kernel = sk.Kernel()

        # Configure kernel with Azure OpenAI service
        try:
            # Add Azure Chat service
            chat_service = AzureChatCompletion(
                deployment_name=settings.azure_openai_chat_deployment,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            kernel.add_service(chat_service)

            # Add Azure Embedding service
            embedding_service = AzureTextEmbedding(
                deployment_name=settings.azure_openai_embedding_deployment,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            kernel.add_service(embedding_service)

            logger.info(
                "Semantic Kernel configured successfully with Azure OpenAI services."
            )
        except Exception as e:
            logger.error(f"Failed to configure Semantic Kernel: {str(e)}")
            raise

        return kernel

    def create_kernel(self) -> sk.Kernel:
        """
        Create a new Semantic Kernel instance (legacy method for backward compatibility).

        Returns:
            sk.Kernel: Configured Semantic Kernel instance

        Raises:
            ValueError: If Azure OpenAI is not configured
        """
        return self._create_kernel()

    def is_fallback_mode(self) -> bool:
        """Check if kernel manager is in fallback mode (no Azure OpenAI)."""
        # Trigger initialization if not yet done
        self.get_kernel()
        return self._fallback_mode


# Singleton instance for global access
kernel_manager = KernelManager()
