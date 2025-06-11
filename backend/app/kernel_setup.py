"""
Semantic Kernel setup and initialization for the AI Dungeon Master.
"""
import os
import logging
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.services.azure_text_embedding import AzureTextEmbedding

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
            # Only add services if configuration is provided
            if (settings.azure_openai_chat_deployment and 
                settings.azure_openai_endpoint and 
                settings.azure_openai_api_key):
                
                # Add Azure Chat service
                chat_service = AzureChatCompletion(
                    deployment_name=settings.azure_openai_chat_deployment,
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                kernel.add_service(chat_service)

                logger.info("Azure Chat service configured successfully.")
            else:
                logger.warning("Azure OpenAI Chat configuration incomplete. Chat service not configured.")

            if (settings.azure_openai_embedding_deployment and 
                settings.azure_openai_endpoint and 
                settings.azure_openai_api_key):
                
                # Add Azure Embedding service
                embedding_service = AzureTextEmbedding(
                    deployment_name=settings.azure_openai_embedding_deployment,
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                kernel.add_service(embedding_service)

                logger.info("Azure Embedding service configured successfully.")
            else:
                logger.warning("Azure OpenAI Embedding configuration incomplete. Embedding service not configured.")

        except Exception as e:
            logger.error(f"Failed to configure Semantic Kernel services: {str(e)}")
            # Don't raise here to allow the kernel to be created without services for development

        return kernel


# Singleton instance for global access
kernel_manager = KernelManager()
