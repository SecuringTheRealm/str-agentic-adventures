"""
Semantic Kernel setup and initialization for the AI Dungeon Master.
"""
import logging

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding

from app.config import settings

logger = logging.getLogger(__name__)

class KernelManager:
    """Manager class for creating and configuring Semantic Kernel instances."""

    @staticmethod
    def create_kernel() -> sk.Kernel:
        """
        Create and configure a new Semantic Kernel instance.

        Returns:
            sk.Kernel: Configured Semantic Kernel instance
        """
        # Create a new kernel
        kernel = sk.Kernel()

        # Configure kernel with Azure OpenAI service
        try:
            # Add Azure Chat service
            chat_service = AzureChatCompletion(
                deployment_name=settings.azure_openai_chat_deployment,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version
            )
            kernel.add_service(chat_service)

            # Add Azure Embedding service
            embedding_service = AzureTextEmbedding(
                deployment_name=settings.azure_openai_embedding_deployment,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version
            )
            kernel.add_service(embedding_service)

            logger.info("Semantic Kernel configured successfully with Azure OpenAI services.")
        except Exception as e:
            logger.error(f"Failed to configure Semantic Kernel: {str(e)}")
            raise

        return kernel


# Singleton instance for global access
kernel_manager = KernelManager()
