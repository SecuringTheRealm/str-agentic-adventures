"""
Art Style Analysis Plugin for the Agent Framework.
This plugin provides art style analysis and consistency tracking capabilities.
"""

import json
import logging
from typing import Any

# Note: Converted from Agent plugin to direct function calls

logger = logging.getLogger(__name__)


class ArtStyleAnalysisPlugin:
    """
    Plugin that provides art style analysis and consistency tracking.
    Analyzes generated artwork for style consistency and provides recommendations.
    """

    def __init__(self) -> None:
        """Initialize the art style analysis plugin."""
        # Track style patterns and consistency
        self.style_profiles = {}
        self.style_history = []
        self.consistency_metrics = {}

    def analyze_art_style(
        self, image_description: str, prompt: str, art_metadata: str = ""
    ) -> dict[str, Any]:
        """
        Analyze the art style characteristics of a generated image.

        Args:
            image_description: Description of the generated image
            prompt: Original prompt used for generation
            art_metadata: JSON string with additional metadata

        Returns:
            Dict[str, Any]: Art style analysis results
        """
        try:
            # Parse metadata if provided
            metadata = {}
            if art_metadata:
                try:
                    metadata = json.loads(art_metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

            # Extract style characteristics
            style_characteristics = self._extract_style_characteristics(
                image_description, prompt, metadata
            )

            # Determine style category
            style_category = self._categorize_style(style_characteristics)

            # Store analysis for consistency tracking
            analysis_record = {
                "image_description": image_description,
                "prompt": prompt,
                "style_characteristics": style_characteristics,
                "style_category": style_category,
                "metadata": metadata,
                "timestamp": self._get_timestamp(),
            }
            self.style_history.append(analysis_record)

            return {
                "status": "success",
                "style_category": style_category,
                "characteristics": style_characteristics,
                "confidence": self._calculate_confidence(style_characteristics),
                "style_tags": self._generate_style_tags(style_characteristics),
                "analysis_id": len(self.style_history),
            }

        except Exception as e:
            logger.error(f"Error analyzing art style: {str(e)}")
            return {"status": "error", "error": f"Art style analysis failed: {str(e)}"}

    def check_style_consistency(
        self, image_group: str = "current_session", threshold: float = 0.7
    ) -> dict[str, Any]:
        """
        Check style consistency across multiple generated images.

        Args:
            image_group: Group identifier for consistency checking
            threshold: Minimum consistency score (0.0 to 1.0)

        Returns:
            Dict[str, Any]: Style consistency analysis
        """
        try:
            if len(self.style_history) < 2:
                return {
                    "status": "insufficient_data",
                    "message": "Need at least 2 analyzed images for consistency checking",
                }

            # Get recent analyses for comparison
            recent_analyses = (
                self.style_history[-5:]
                if len(self.style_history) >= 5
                else self.style_history
            )

            # Calculate consistency metrics
            consistency_score = self._calculate_consistency_score(recent_analyses)
            inconsistencies = self._identify_inconsistencies(recent_analyses, threshold)
            recommendations = self._generate_consistency_recommendations(
                inconsistencies
            )

            # Store consistency metrics
            consistency_record = {
                "group": image_group,
                "score": consistency_score,
                "threshold": threshold,
                "inconsistencies": inconsistencies,
                "recommendations": recommendations,
                "analyzed_count": len(recent_analyses),
                "timestamp": self._get_timestamp(),
            }
            self.consistency_metrics[image_group] = consistency_record

            return {
                "status": "success",
                "consistency_score": consistency_score,
                "is_consistent": consistency_score >= threshold,
                "inconsistencies": inconsistencies,
                "recommendations": recommendations,
                "analyzed_images": len(recent_analyses),
            }

        except Exception as e:
            logger.error(f"Error checking style consistency: {str(e)}")
            return {
                "status": "error",
                "error": f"Style consistency check failed: {str(e)}",
            }

    def create_style_profile(
        self, profile_name: str, style_description: str, reference_images: str = ""
    ) -> dict[str, Any]:
        """
        Create a style profile for maintaining consistency.

        Args:
            profile_name: Name for the style profile
            style_description: Description of the desired style
            reference_images: JSON string of reference image data

        Returns:
            Dict[str, Any]: Created style profile
        """
        try:
            # Parse reference images if provided
            references = []
            if reference_images:
                try:
                    references = json.loads(reference_images)
                except (json.JSONDecodeError, TypeError):
                    references = []

            # Extract style characteristics from description
            characteristics = self._extract_style_from_description(style_description)

            # Create style profile
            style_profile = {
                "name": profile_name,
                "description": style_description,
                "characteristics": characteristics,
                "reference_images": references,
                "created_timestamp": self._get_timestamp(),
                "usage_count": 0,
                "consistency_history": [],
            }

            self.style_profiles[profile_name] = style_profile

            return {
                "status": "success",
                "profile_name": profile_name,
                "characteristics": characteristics,
                "message": f"Style profile '{profile_name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating style profile: {str(e)}")
            return {
                "status": "error",
                "error": f"Style profile creation failed: {str(e)}",
            }

    def get_style_recommendations(
        self, target_style: str = "", current_prompt: str = ""
    ) -> dict[str, Any]:
        """
        Get recommendations for maintaining style consistency.

        Args:
            target_style: Target style profile name or description
            current_prompt: Current prompt to analyze

        Returns:
            Dict[str, Any]: Style recommendations
        """
        try:
            recommendations = []

            # Check if target style is a known profile
            if target_style in self.style_profiles:
                profile = self.style_profiles[target_style]
                profile_recommendations = self._get_profile_recommendations(
                    profile, current_prompt
                )
                recommendations.extend(profile_recommendations)

            # Analyze recent style history for patterns
            if self.style_history:
                history_recommendations = self._get_history_recommendations(
                    current_prompt
                )
                recommendations.extend(history_recommendations)

            # General style consistency recommendations
            general_recommendations = self._get_general_recommendations(current_prompt)
            recommendations.extend(general_recommendations)

            return {
                "status": "success",
                "recommendations": recommendations,
                "target_style": target_style,
                "current_prompt": current_prompt,
                "recommendation_count": len(recommendations),
            }

        except Exception as e:
            logger.error(f"Error getting style recommendations: {str(e)}")
            return {
                "status": "error",
                "error": f"Style recommendations failed: {str(e)}",
            }

    def _extract_style_characteristics(
        self, description: str, prompt: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract style characteristics from image data."""
        characteristics = {
            "art_medium": self._detect_art_medium(description, prompt),
            "color_palette": self._detect_color_palette(description, prompt),
            "lighting_style": self._detect_lighting_style(description, prompt),
            "composition_style": self._detect_composition_style(description, prompt),
            "detail_level": self._detect_detail_level(description, prompt),
            "artistic_movement": self._detect_artistic_movement(description, prompt),
        }

        # Add metadata insights
        if metadata:
            characteristics["generation_params"] = metadata.get(
                "generation_details", {}
            )

        return characteristics

    def _detect_art_medium(self, description: str, prompt: str) -> str:
        """Detect the art medium from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["digital", "cgi", "3d"]):
            return "digital"
        if any(term in text for term in ["oil", "painting", "painted"]):
            return "oil_painting"
        if any(term in text for term in ["watercolor", "wash"]):
            return "watercolor"
        if any(term in text for term in ["pencil", "sketch", "drawn"]):
            return "pencil"
        if any(term in text for term in ["ink", "pen"]):
            return "ink"
        return "mixed_media"

    def _detect_color_palette(self, description: str, prompt: str) -> str:
        """Detect the color palette from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["vibrant", "bright", "colorful"]):
            return "vibrant"
        if any(term in text for term in ["muted", "subdued", "pastel"]):
            return "muted"
        if any(term in text for term in ["monochrome", "black and white", "grayscale"]):
            return "monochrome"
        if any(term in text for term in ["warm", "orange", "red", "yellow"]):
            return "warm"
        if any(term in text for term in ["cool", "blue", "purple", "green"]):
            return "cool"
        return "balanced"

    def _detect_lighting_style(self, description: str, prompt: str) -> str:
        """Detect the lighting style from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["dramatic", "harsh", "strong shadows"]):
            return "dramatic"
        if any(term in text for term in ["soft", "diffused", "gentle"]):
            return "soft"
        if any(term in text for term in ["atmospheric", "mood", "ambient"]):
            return "atmospheric"
        if any(term in text for term in ["studio", "professional", "even"]):
            return "studio"
        return "natural"

    def _categorize_style(self, characteristics: dict[str, Any]) -> str:
        """Categorize the overall art style."""
        medium = characteristics.get("art_medium", "")
        lighting = characteristics.get("lighting_style", "")
        palette = characteristics.get("color_palette", "")

        if medium == "digital" and lighting == "dramatic":
            return "fantasy_digital"
        if medium == "oil_painting" and palette == "warm":
            return "classical_painting"
        if medium == "digital" and lighting == "soft":
            return "contemporary_digital"
        if medium == "watercolor":
            return "impressionist"
        return "mixed_style"

    def _calculate_consistency_score(self, analyses: list[dict[str, Any]]) -> float:
        """Calculate style consistency score across analyses."""
        if len(analyses) < 2:
            return 1.0

        # Compare characteristics across analyses
        consistency_scores = []

        for i in range(len(analyses) - 1):
            current = analyses[i]["style_characteristics"]
            next_analysis = analyses[i + 1]["style_characteristics"]

            # Calculate similarity for each characteristic
            similarities = []
            for key in current:
                if key in next_analysis:
                    if current[key] == next_analysis[key]:
                        similarities.append(1.0)
                    else:
                        similarities.append(0.5)  # Partial similarity
                else:
                    similarities.append(0.0)

            if similarities:
                consistency_scores.append(sum(similarities) / len(similarities))

        return (
            sum(consistency_scores) / len(consistency_scores)
            if consistency_scores
            else 1.0
        )

    def _identify_inconsistencies(
        self, analyses: list[dict[str, Any]], threshold: float
    ) -> list[dict[str, Any]]:
        """Identify style inconsistencies."""
        inconsistencies = []

        if len(analyses) < 2:
            return inconsistencies

        # Track characteristic variations
        char_variations = {}
        for analysis in analyses:
            for key, value in analysis["style_characteristics"].items():
                if key not in char_variations:
                    char_variations[key] = []
                char_variations[key].append(value)

        # Find characteristics with high variation
        for char, values in char_variations.items():
            unique_values = list(set(values))
            if len(unique_values) > 1:
                variation_ratio = len(unique_values) / len(values)
                if variation_ratio > (1.0 - threshold):
                    inconsistencies.append(
                        {
                            "characteristic": char,
                            "values": unique_values,
                            "variation_ratio": variation_ratio,
                            "severity": "high" if variation_ratio > 0.7 else "medium",
                        }
                    )

        return inconsistencies

    def _generate_consistency_recommendations(
        self, inconsistencies: list[dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations based on inconsistencies."""
        recommendations = []

        for inconsistency in inconsistencies:
            char = inconsistency["characteristic"]
            severity = inconsistency["severity"]

            if char == "art_medium":
                recommendations.append(
                    "Consider maintaining consistent art medium across generations"
                )
            elif char == "lighting_style":
                recommendations.append(
                    "Keep lighting style consistent for visual coherence"
                )
            elif char == "color_palette":
                recommendations.append(
                    "Maintain color palette consistency for unified look"
                )
            elif char == "composition_style":
                recommendations.append("Use consistent composition approach")

            if severity == "high":
                recommendations.append(
                    f"High variation in {char} detected - consider style profile"
                )

        return recommendations

    def _calculate_confidence(self, characteristics: dict[str, Any]) -> float:
        """Calculate confidence score for style analysis."""
        # Simple confidence based on number of detected characteristics
        detected_chars = sum(
            1 for v in characteristics.values() if v and v != "unknown"
        )
        total_chars = len(characteristics)
        return detected_chars / total_chars if total_chars > 0 else 0.0

    def _generate_style_tags(self, characteristics: dict[str, Any]) -> list[str]:
        """Generate style tags from characteristics."""
        tags = []
        for key, value in characteristics.items():
            if value and value != "unknown":
                tags.append(f"{key}:{value}")
        return tags

    def _extract_style_from_description(self, description: str) -> dict[str, Any]:
        """Extract style characteristics from text description."""
        return self._extract_style_characteristics(description, description, {})

    def _get_profile_recommendations(
        self, profile: dict[str, Any], prompt: str
    ) -> list[str]:
        """Get recommendations based on style profile."""
        recommendations = []
        characteristics = profile.get("characteristics", {})

        for char, value in characteristics.items():
            if value:
                recommendations.append(
                    f"Maintain {char}: {value} as per profile '{profile['name']}'"
                )

        return recommendations

    def _get_history_recommendations(self, prompt: str) -> list[str]:
        """Get recommendations based on style history."""
        recommendations = []

        if len(self.style_history) >= 3:
            recent = self.style_history[-3:]
            common_chars = self._find_common_characteristics(recent)

            for char, value in common_chars.items():
                recommendations.append(
                    f"Continue using {char}: {value} for consistency"
                )

        return recommendations

    def _find_common_characteristics(
        self, analyses: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Find common characteristics across analyses."""
        common = {}

        for analysis in analyses:
            for char, value in analysis["style_characteristics"].items():
                if char not in common:
                    common[char] = {}
                if value not in common[char]:
                    common[char][value] = 0
                common[char][value] += 1

        # Return most common values
        result = {}
        for char, values in common.items():
            if values:
                most_common = max(values.items(), key=lambda x: x[1])
                if most_common[1] >= 2:  # Appears at least twice
                    result[char] = most_common[0]

        return result

    def _get_general_recommendations(self, prompt: str) -> list[str]:
        """Get general style recommendations."""
        return [
            "Include specific art style keywords in prompt for consistency",
            "Specify lighting and composition preferences",
            "Use consistent quality and detail descriptors",
        ]

    def _detect_composition_style(self, description: str, prompt: str) -> str:
        """Detect composition style from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["close-up", "portrait", "headshot"]):
            return "close_up"
        if any(term in text for term in ["wide", "landscape", "panoramic"]):
            return "wide_shot"
        if any(term in text for term in ["centered", "symmetrical"]):
            return "centered"
        if any(term in text for term in ["dynamic", "action", "movement"]):
            return "dynamic"
        return "standard"

    def _detect_detail_level(self, description: str, prompt: str) -> str:
        """Detect detail level from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["highly detailed", "intricate", "complex"]):
            return "high"
        if any(term in text for term in ["simple", "minimalist", "clean"]):
            return "low"
        return "medium"

    def _detect_artistic_movement(self, description: str, prompt: str) -> str:
        """Detect artistic movement from description and prompt."""
        text = (description + " " + prompt).lower()

        if any(term in text for term in ["realistic", "photorealistic"]):
            return "realism"
        if any(term in text for term in ["impressionist", "impressionism"]):
            return "impressionism"
        if any(term in text for term in ["abstract", "cubist"]):
            return "abstract"
        if any(term in text for term in ["surreal", "surrealism"]):
            return "surrealism"
        return "contemporary"

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime

        return datetime.datetime.now().isoformat()
