"""
Image Generation Service - Handles image generation and storage.
"""
import logging
import uuid
from typing import Dict, Any, Optional
import aiohttp
import io
import hashlib
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """Service for generating and storing images using Azure OpenAI DALL-E."""
    
    def __init__(self):
        """Initialize the image generation service."""
        self.endpoint = settings.azure_openai_endpoint
        self.api_key = settings.azure_openai_api_key
        self.api_version = settings.azure_openai_api_version
        self.dalle_deployment = settings.azure_openai_dalle_deployment
        self.storage_connection_string = settings.storage_connection_string
        self.storage_container = settings.image_storage_container
        
        # Cache for generated images
        self.image_cache = {}
        
    async def generate_image(self, prompt: str, size: str = "1024x1024", 
                           quality: str = "standard", style: str = "natural") -> Dict[str, Any]:
        """
        Generate an image using Azure OpenAI DALL-E.
        
        Args:
            prompt: Text description of the image to generate
            size: Image size (1024x1024, 1792x1024, or 1024x1792)
            quality: Image quality (standard or hd)
            style: Image style (natural or vivid)
            
        Returns:
            Dict containing image information and URL
        """
        try:
            # Check if we have the necessary configuration
            if not self.endpoint or not self.api_key:
                logger.warning("Azure OpenAI credentials not configured - returning placeholder image")
                return await self._create_placeholder_response(prompt, size)
            
            # Create a hash of the prompt for caching
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
            cache_key = f"{prompt_hash}_{size}_{quality}_{style}"
            
            if cache_key in self.image_cache:
                logger.info(f"Returning cached image for prompt: {prompt[:50]}...")
                return self.image_cache[cache_key]
            
            # Generate image using Azure OpenAI DALL-E
            image_data = await self._call_dalle_api(prompt, size, quality, style)
            
            if image_data and "url" in image_data:
                # Store the image in blob storage
                stored_url = await self._store_image_from_url(image_data["url"], prompt)
                
                result = {
                    "id": str(uuid.uuid4()),
                    "prompt": prompt,
                    "image_url": stored_url or image_data["url"],
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "created_at": datetime.utcnow().isoformat(),
                    "cached": False
                }
                
                # Cache the result
                self.image_cache[cache_key] = result
                return result
            else:
                logger.error("Failed to generate image - no URL in response")
                return await self._create_placeholder_response(prompt, size)
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return await self._create_placeholder_response(prompt, size)
    
    async def _call_dalle_api(self, prompt: str, size: str, quality: str, style: str) -> Optional[Dict[str, Any]]:
        """Make API call to Azure OpenAI DALL-E service."""
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            payload = {
                "prompt": prompt,
                "size": size,
                "n": 1,
                "quality": quality,
                "style": style
            }
            
            url = f"{self.endpoint}/openai/deployments/{self.dalle_deployment}/images/generations"
            params = {"api-version": self.api_version}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, params=params, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and len(data["data"]) > 0:
                            return data["data"][0]
                    else:
                        error_text = await response.text()
                        logger.error(f"DALL-E API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling DALL-E API: {str(e)}")
            return None
    
    async def _store_image_from_url(self, image_url: str, prompt: str) -> Optional[str]:
        """Download image from URL and store in Azure Blob Storage."""
        try:
            if not self.storage_connection_string:
                logger.warning("Storage connection string not configured - skipping blob storage")
                return None
                
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return await self._upload_to_blob_storage(image_data, prompt)
                    else:
                        logger.error(f"Failed to download image: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error storing image: {str(e)}")
            return None
    
    async def _upload_to_blob_storage(self, image_data: bytes, prompt: str) -> Optional[str]:
        """Upload image data to Azure Blob Storage."""
        try:
            from azure.storage.blob.aio import BlobServiceClient
            
            # Create a unique filename
            image_id = str(uuid.uuid4())
            filename = f"{image_id}.png"
            
            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(self.storage_connection_string)
            
            # Create container if it doesn't exist
            container_client = blob_service_client.get_container_client(self.storage_container)
            try:
                await container_client.create_container()
            except Exception:
                pass  # Container might already exist
            
            # Upload the image
            blob_client = blob_service_client.get_blob_client(
                container=self.storage_container, 
                blob=filename
            )
            
            metadata = {
                "prompt": prompt[:500],  # Truncate prompt for metadata
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await blob_client.upload_blob(
                image_data, 
                overwrite=True,
                metadata=metadata,
                content_type="image/png"
            )
            
            # Return the blob URL
            return blob_client.url
            
        except Exception as e:
            logger.error(f"Error uploading to blob storage: {str(e)}")
            return None
    
    async def _create_placeholder_response(self, prompt: str, size: str) -> Dict[str, Any]:
        """Create a placeholder response when image generation fails."""
        return {
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "image_url": None,
            "size": size,
            "quality": "standard",
            "style": "natural",
            "created_at": datetime.utcnow().isoformat(),
            "cached": False,
            "placeholder": True,
            "message": "Image generation not available - Azure OpenAI credentials required"
        }
    
    async def get_cached_image(self, prompt_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached image by prompt hash."""
        return self.image_cache.get(prompt_hash)
    
    def clear_cache(self):
        """Clear the image cache."""
        self.image_cache.clear()
        logger.info("Image cache cleared")

# Singleton instance
image_service = ImageGenerationService()