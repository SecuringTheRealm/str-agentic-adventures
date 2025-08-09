"""
Image Generation Plugin for the Semantic Kernel.
This plugin provides core image generation capabilities using Azure OpenAI DALL-E.
"""

import logging
from typing import Dict, Any

from semantic_kernel.functions import kernel_function
from app.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)


class ImageGenerationPlugin:
    """
    Plugin that provides image generation capabilities using Azure OpenAI DALL-E.
    Handles prompt optimization, image generation parameters, and result processing.
    """

    def __init__(self):
        """Initialize the image generation plugin."""
        self.azure_client = AzureOpenAIClient()
        # Store generation history for consistency tracking
        self.generation_history = []

    @kernel_function(
        description="Generate an image using DALL-E based on a text prompt.",
        name="generate_image",
    )
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
    ) -> Dict[str, Any]:
        """
        Generate an image using Azure OpenAI DALL-E.

        Args:
            prompt: Text description of the image to generate
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            style: Image style (vivid, natural)

        Returns:
            Dict[str, Any]: Generation result with image URL and metadata
        """
        try:
            # Optimize prompt for better results
            optimized_prompt = self._optimize_prompt(prompt)

            # Generate the image
            result = self.azure_client.generate_image(
                prompt=optimized_prompt, size=size, quality=quality, style=style
            )

            # Store in generation history
            generation_record = {
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "parameters": {"size": size, "quality": quality, "style": style},
                "result": result,
                "timestamp": self._get_timestamp(),
            }
            self.generation_history.append(generation_record)

            return {
                "status": "success" if result.get("success") else "error",
                "image_url": result.get("image_url"),
                "revised_prompt": result.get("revised_prompt", optimized_prompt),
                "original_prompt": prompt,
                "generation_parameters": {
                    "size": size,
                    "quality": quality,
                    "style": style,
                },
                "error": result.get("error") if not result.get("success") else None,
            }

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {"status": "error", "error": f"Image generation failed: {str(e)}"}

    @kernel_function(
        description="Optimize a text prompt for better image generation results.",
        name="optimize_prompt",
    )
    def optimize_prompt(
        self, prompt: str, art_style: str = "fantasy", context: str = "RPG"
    ) -> Dict[str, Any]:
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
            logger.error(f"Error optimizing prompt: {str(e)}")
            return {"status": "error", "error": f"Prompt optimization failed: {str(e)}"}

    @kernel_function(
        description="Get generation history for analysis and consistency tracking.",
        name="get_generation_history",
    )
    def get_generation_history(self, limit: int = 10) -> Dict[str, Any]:
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
            logger.error(f"Error getting generation history: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to get generation history: {str(e)}",
            }

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
