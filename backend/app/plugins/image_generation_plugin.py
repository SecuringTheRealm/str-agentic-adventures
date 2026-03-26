"""
Image Generation Plugin for the Agent Framework.
This plugin provides core image generation capabilities using Azure OpenAI gpt-image-1.
"""

import base64
import logging
import uuid
from typing import Any

# Note: Converted from Agent plugin to direct function calls
from app.azure_openai_client import azure_openai_client
from app.services.blob_storage_service import get_blob_storage_service

logger = logging.getLogger(__name__)


class ImageGenerationPlugin:
    """
    Plugin that provides image generation capabilities using Azure OpenAI gpt-image-1.
    Handles prompt optimization, image generation parameters, and result processing.
    """

    def __init__(self) -> None:
        """Initialize the image generation plugin."""
        self.azure_client = azure_openai_client
        # Store generation history for consistency tracking
        self.generation_history = []

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "medium",
    ) -> dict[str, Any]:
        """
        Generate an image using Azure OpenAI gpt-image-1.

        Args:
            prompt: Text description of the image to generate
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (low, medium, high)

        Returns:
            Dict[str, Any]: Generation result with image data URI and metadata
        """
        try:
            # Optimize prompt for better results
            optimized_prompt = self._optimize_prompt(prompt)

            # Generate the image
            result = self.azure_client.generate_image(
                prompt=optimized_prompt, size=size, quality=quality
            )

            # Try uploading to blob storage for a SAS URL instead of a data URI
            image_url = result.get("image_url")
            if result.get("success") and result.get("b64_json"):
                image_url = self._try_upload_to_blob(result["b64_json"]) or image_url

            # Store in generation history
            generation_record = {
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "parameters": {"size": size, "quality": quality},
                "result": result,
                "timestamp": self._get_timestamp(),
            }
            self.generation_history.append(generation_record)

            return {
                "status": "success" if result.get("success") else "error",
                "image_url": image_url,
                "revised_prompt": result.get("revised_prompt", optimized_prompt),
                "original_prompt": prompt,
                "generation_parameters": {
                    "size": size,
                    "quality": quality,
                },
                "error": result.get("error") if not result.get("success") else None,
            }

        except Exception as e:
            logger.error("Error generating image: %s", str(e))
            return {"status": "error", "error": f"Image generation failed: {str(e)}"}

    def optimize_prompt(
        self, prompt: str, art_style: str = "fantasy", context: str = "RPG"
    ) -> dict[str, Any]:
        """
        Optimize a text prompt for better image generation results.

        Args:
            prompt: Original text prompt
            art_style: Desired art style (fantasy, realistic, cartoon, etc.)
            context: Context for optimization (RPG, portrait, scene, etc.)

        Returns:
            Dict[str, Any]: Optimized prompt and optimization details
        """
        try:
            optimized_prompt = self._optimize_prompt(prompt, art_style, context)

            return {
                "status": "success",
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "art_style": art_style,
                "context": context,
                "optimizations_applied": self._get_optimization_details(
                    prompt, optimized_prompt
                ),
            }

        except Exception as e:
            logger.error("Error optimizing prompt: %s", str(e))
            return {"status": "error", "error": f"Prompt optimization failed: {str(e)}"}

    def get_generation_history(self, limit: int = 10) -> dict[str, Any]:
        """
        Get recent image generation history.

        Args:
            limit: Maximum number of recent generations to return

        Returns:
            Dict[str, Any]: Recent generation history
        """
        try:
            recent_history = (
                self.generation_history[-limit:] if self.generation_history else []
            )

            return {
                "status": "success",
                "total_generations": len(self.generation_history),
                "recent_generations": [
                    {
                        "prompt": record["original_prompt"],
                        "optimized_prompt": record["optimized_prompt"],
                        "parameters": record["parameters"],
                        "success": record["result"].get("success", False),
                        "timestamp": record["timestamp"],
                    }
                    for record in recent_history
                ],
            }

        except Exception as e:
            logger.error("Error getting generation history: %s", str(e))
            return {
                "status": "error",
                "error": f"Failed to get generation history: {str(e)}",
            }

    def _try_upload_to_blob(self, b64_json: str) -> str | None:
        """Attempt to upload base64 image data to blob storage and return a SAS URL.

        Returns None if blob storage is unavailable, keeping the data URI fallback.
        """
        try:
            blob_service = get_blob_storage_service()
            image_bytes = base64.b64decode(b64_json)
            blob_name = f"{uuid.uuid4()}.png"
            return blob_service.upload_image(
                container="images",
                blob_name=blob_name,
                data=image_bytes,
                content_type="image/png",
            )
        except Exception as e:
            logger.warning("Blob upload failed, falling back to data URI: %s", e)
            return None

    def _optimize_prompt(
        self, prompt: str, art_style: str = "fantasy", context: str = "RPG"
    ) -> str:
        """Optimize a prompt for better image generation results."""
        optimized = prompt.strip()

        # Add art style if not already specified
        style_keywords = [
            "art",
            "style",
            "painting",
            "illustration",
            "digital",
            "photo",
        ]
        if not any(keyword in optimized.lower() for keyword in style_keywords):
            if art_style == "fantasy":
                optimized += ", high quality digital art, fantasy RPG style"
            elif art_style == "realistic":
                optimized += ", photorealistic, high detail"
            elif art_style == "cartoon":
                optimized += ", cartoon style illustration"
            else:
                optimized += f", {art_style} art style"

        # Add quality enhancers based on context
        if context.lower() == "portrait" or "character" in optimized.lower():
            if "lighting" not in optimized.lower():
                optimized += ", atmospheric lighting"
            if "detail" not in optimized.lower():
                optimized += ", detailed features"
        elif context.lower() == "scene" or "landscape" in optimized.lower():
            if "composition" not in optimized.lower():
                optimized += ", cinematic composition"
            if "lighting" not in optimized.lower():
                optimized += ", dramatic lighting"

        # Add general quality enhancers
        quality_terms = ["professional", "detailed", "high quality"]
        if not any(term in optimized.lower() for term in quality_terms):
            optimized += ", professional quality"

        return optimized

    def _get_optimization_details(self, original: str, optimized: str) -> list:
        """Get details about what optimizations were applied."""
        details = []

        if "art" in optimized.lower() and "art" not in original.lower():
            details.append("Added art style specification")

        if "lighting" in optimized.lower() and "lighting" not in original.lower():
            details.append("Added lighting enhancement")

        if "quality" in optimized.lower() and "quality" not in original.lower():
            details.append("Added quality enhancement")

        if "composition" in optimized.lower() and "composition" not in original.lower():
            details.append("Added composition enhancement")

        if len(optimized) > len(original):
            details.append("Enhanced prompt length and detail")

        return details

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime

        return datetime.datetime.now().isoformat()
