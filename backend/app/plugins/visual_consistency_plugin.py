"""
Visual Consistency Plugin for the Semantic Kernel.
This plugin ensures visual consistency across generated artwork in campaigns.
"""

import json
import logging
from typing import Any

# Note: Converted from Semantic Kernel plugin to direct function calls

logger = logging.getLogger(__name__)


class VisualConsistencyPlugin:
    """
    Plugin that ensures visual consistency across generated artwork.
    Manages visual themes, character appearance consistency, and world-building coherence.
    """

    def __init__(self) -> None:
        """Initialize the visual consistency plugin."""
        # Track visual elements for consistency
        self.character_visual_profiles = {}
        self.world_visual_themes = {}
        self.campaign_visual_contexts = {}
        self.consistency_violations = []

#     # @kernel_function(
#         description="Create a visual consistency profile for a character.",
#         name="create_character_visual_profile",
#     )
    def create_character_visual_profile(
        self,
        character_id: str,
        character_name: str,
        visual_description: str,
        reference_art: str = "",
    ) -> dict[str, Any]:
        """
        Create a visual consistency profile for a character.

        Args:
            character_id: Unique identifier for the character
            character_name: Name of the character
            visual_description: Detailed visual description
            reference_art: JSON string with reference artwork data

        Returns:
            Dict[str, Any]: Created visual profile
        """
        try:
            # Parse reference art if provided
            references = []
            if reference_art:
                try:
                    references = json.loads(reference_art)
                except (json.JSONDecodeError, TypeError):
                    references = []

            # Extract visual elements
            visual_elements = self._extract_visual_elements(visual_description)

            # Create visual profile
            profile = {
                "character_id": character_id,
                "character_name": character_name,
                "visual_description": visual_description,
                "visual_elements": visual_elements,
                "reference_art": references,
                "consistency_rules": self._generate_consistency_rules(visual_elements),
                "created_timestamp": self._get_timestamp(),
                "update_count": 0,
                "violation_history": [],
            }

            self.character_visual_profiles[character_id] = profile

            return {
                "status": "success",
                "character_id": character_id,
                "visual_elements": visual_elements,
                "consistency_rules": profile["consistency_rules"],
                "message": f"Visual profile created for {character_name}",
            }

        except Exception as e:
            logger.error(f"Error creating character visual profile: {str(e)}")
            return {
                "status": "error",
                "error": f"Character visual profile creation failed: {str(e)}",
            }

#     # @kernel_function(
#         description="Validate visual consistency for a character portrait.",
#         name="validate_character_consistency",
#     )
    def validate_character_consistency(
        self, character_id: str, new_description: str, generation_prompt: str = ""
    ) -> dict[str, Any]:
        """
        Validate visual consistency for a character portrait.

        Args:
            character_id: ID of the character being validated
            new_description: Description of newly generated artwork
            generation_prompt: Prompt used for generation

        Returns:
            Dict[str, Any]: Validation results with consistency score
        """
        try:
            if character_id not in self.character_visual_profiles:
                return {
                    "status": "no_profile",
                    "message": "No visual profile found for character",
                    "requires_profile_creation": True,
                }

            profile = self.character_visual_profiles[character_id]

            # Extract elements from new description
            new_elements = self._extract_visual_elements(new_description)

            # Compare with profile elements
            consistency_score = self._calculate_consistency_score(
                profile["visual_elements"], new_elements
            )

            # Check for violations
            violations = self._check_consistency_violations(
                profile, new_elements, generation_prompt
            )

            # Record validation
            validation_record = {
                "new_description": new_description,
                "new_elements": new_elements,
                "consistency_score": consistency_score,
                "violations": violations,
                "timestamp": self._get_timestamp(),
            }
            profile["violation_history"].append(validation_record)

            # Update profile if score is good
            if consistency_score >= 0.8 and not violations:
                self._update_profile_elements(profile, new_elements)

            return {
                "status": "success",
                "character_id": character_id,
                "consistency_score": consistency_score,
                "is_consistent": consistency_score >= 0.7 and len(violations) == 0,
                "violations": violations,
                "recommendations": self._generate_consistency_recommendations(
                    profile, violations
                ),
            }

        except Exception as e:
            logger.error(f"Error validating character consistency: {str(e)}")
            return {
                "status": "error",
                "error": f"Character consistency validation failed: {str(e)}",
            }

#     # @kernel_function(
#         description="Create a visual theme for a campaign or world.",
#         name="create_world_visual_theme",
#     )
    def create_world_visual_theme(
        self,
        theme_id: str,
        theme_name: str,
        theme_description: str,
        style_guidelines: str = "",
    ) -> dict[str, Any]:
        """
        Create a visual theme for a campaign or world.

        Args:
            theme_id: Unique identifier for the theme
            theme_name: Name of the visual theme
            theme_description: Description of the theme
            style_guidelines: JSON string with style guidelines

        Returns:
            Dict[str, Any]: Created visual theme
        """
        try:
            # Parse style guidelines if provided
            guidelines = {}
            if style_guidelines:
                try:
                    guidelines = json.loads(style_guidelines)
                except (json.JSONDecodeError, TypeError):
                    guidelines = {}

            # Extract theme elements
            theme_elements = self._extract_theme_elements(theme_description)

            # Create visual theme
            theme = {
                "theme_id": theme_id,
                "theme_name": theme_name,
                "theme_description": theme_description,
                "theme_elements": theme_elements,
                "style_guidelines": guidelines,
                "consistency_requirements": self._generate_theme_requirements(
                    theme_elements
                ),
                "created_timestamp": self._get_timestamp(),
                "usage_count": 0,
                "associated_content": [],
            }

            self.world_visual_themes[theme_id] = theme

            return {
                "status": "success",
                "theme_id": theme_id,
                "theme_elements": theme_elements,
                "consistency_requirements": theme["consistency_requirements"],
                "message": f"Visual theme '{theme_name}' created successfully",
            }

        except Exception as e:
            logger.error(f"Error creating world visual theme: {str(e)}")
            return {
                "status": "error",
                "error": f"World visual theme creation failed: {str(e)}",
            }

#     # @kernel_function(
#         description="Validate visual consistency with world theme.",
#         name="validate_world_consistency",
#     )
    def validate_world_consistency(
        self, theme_id: str, content_description: str, content_type: str = "scene"
    ) -> dict[str, Any]:
        """
        Validate visual consistency with world theme.

        Args:
            theme_id: ID of the world theme
            content_description: Description of the content to validate
            content_type: Type of content (scene, item, location, etc.)

        Returns:
            Dict[str, Any]: World consistency validation results
        """
        try:
            if theme_id not in self.world_visual_themes:
                return {
                    "status": "no_theme",
                    "message": "No world visual theme found",
                    "requires_theme_creation": True,
                }

            theme = self.world_visual_themes[theme_id]

            # Extract elements from content
            content_elements = self._extract_visual_elements(content_description)

            # Check theme consistency
            consistency_score = self._calculate_theme_consistency(
                theme["theme_elements"], content_elements
            )

            # Check for theme violations
            violations = self._check_theme_violations(
                theme, content_elements, content_type
            )

            # Update theme usage
            theme["usage_count"] += 1
            theme["associated_content"].append(
                {
                    "description": content_description,
                    "type": content_type,
                    "elements": content_elements,
                    "consistency_score": consistency_score,
                    "timestamp": self._get_timestamp(),
                }
            )

            return {
                "status": "success",
                "theme_id": theme_id,
                "consistency_score": consistency_score,
                "is_consistent": consistency_score >= 0.7 and len(violations) == 0,
                "violations": violations,
                "theme_adherence": self._calculate_theme_adherence(
                    theme, content_elements
                ),
                "recommendations": self._generate_theme_recommendations(
                    theme, violations
                ),
            }

        except Exception as e:
            logger.error(f"Error validating world consistency: {str(e)}")
            return {
                "status": "error",
                "error": f"World consistency validation failed: {str(e)}",
            }

#     # @kernel_function(
#         description="Get consistency report for a campaign.",
#         name="get_campaign_consistency_report",
#     )
    def get_campaign_consistency_report(self, campaign_id: str) -> dict[str, Any]:
        """
        Get a comprehensive consistency report for a campaign.

        Args:
            campaign_id: ID of the campaign

        Returns:
            Dict[str, Any]: Comprehensive consistency report
        """
        try:
            # Get campaign context if exists
            self.campaign_visual_contexts.get(campaign_id, {})

            # Analyze character consistency
            character_analysis = self._analyze_character_consistency(campaign_id)

            # Analyze world theme consistency
            theme_analysis = self._analyze_theme_consistency(campaign_id)

            # Calculate overall consistency score
            overall_score = self._calculate_overall_consistency(
                character_analysis, theme_analysis
            )

            # Generate recommendations
            recommendations = self._generate_campaign_recommendations(
                character_analysis, theme_analysis
            )

            # Create report
            report = {
                "campaign_id": campaign_id,
                "overall_consistency_score": overall_score,
                "character_consistency": character_analysis,
                "theme_consistency": theme_analysis,
                "total_violations": len(self.consistency_violations),
                "recommendations": recommendations,
                "generated_timestamp": self._get_timestamp(),
            }

            return {
                "status": "success",
                "report": report,
                "summary": {
                    "overall_score": overall_score,
                    "character_profiles": len(character_analysis.get("profiles", [])),
                    "theme_adherence": theme_analysis.get("average_score", 0.0),
                    "total_recommendations": len(recommendations),
                },
            }

        except Exception as e:
            logger.error(f"Error generating consistency report: {str(e)}")
            return {
                "status": "error",
                "error": f"Consistency report generation failed: {str(e)}",
            }

    def _extract_visual_elements(self, description: str) -> dict[str, Any]:
        """Extract visual elements from description."""
        elements = {
            "colors": self._extract_colors(description),
            "physical_features": self._extract_physical_features(description),
            "clothing_armor": self._extract_clothing_armor(description),
            "accessories": self._extract_accessories(description),
            "pose_expression": self._extract_pose_expression(description),
            "environment": self._extract_environment(description),
        }

        return {k: v for k, v in elements.items() if v}

    def _extract_colors(self, description: str) -> list[str]:
        """Extract color information from description."""
        colors = []
        color_terms = [
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "orange",
            "pink",
            "brown",
            "black",
            "white",
            "gray",
            "gold",
            "silver",
            "copper",
            "crimson",
            "azure",
            "emerald",
            "amber",
            "violet",
            "scarlet",
        ]

        desc_lower = description.lower()
        for color in color_terms:
            if color in desc_lower:
                colors.append(color)

        return colors

    def _extract_physical_features(self, description: str) -> list[str]:
        """Extract physical features from description."""
        features = []
        feature_terms = [
            "tall",
            "short",
            "muscular",
            "slender",
            "beard",
            "mustache",
            "long hair",
            "short hair",
            "bald",
            "scar",
            "tattoo",
            "blue eyes",
            "green eyes",
            "brown eyes",
            "pale",
            "tanned",
            "dark skin",
        ]

        desc_lower = description.lower()
        for feature in feature_terms:
            if feature in desc_lower:
                features.append(feature)

        return features

    def _extract_clothing_armor(self, description: str) -> list[str]:
        """Extract clothing and armor information."""
        items = []
        clothing_terms = [
            "robe",
            "cloak",
            "armor",
            "leather",
            "chainmail",
            "plate",
            "helmet",
            "boots",
            "gloves",
            "belt",
            "tunic",
            "dress",
            "hood",
            "cape",
            "bracers",
        ]

        desc_lower = description.lower()
        for item in clothing_terms:
            if item in desc_lower:
                items.append(item)

        return items

    def _extract_accessories(self, description: str) -> list[str]:
        """Extract accessories from description."""
        accessories = []
        accessory_terms = [
            "sword",
            "staff",
            "bow",
            "shield",
            "ring",
            "necklace",
            "pendant",
            "amulet",
            "crown",
            "circlet",
            "wand",
            "dagger",
        ]

        desc_lower = description.lower()
        for accessory in accessory_terms:
            if accessory in desc_lower:
                accessories.append(accessory)

        return accessories

    def _extract_pose_expression(self, description: str) -> list[str]:
        """Extract pose and expression information."""
        poses = []
        pose_terms = [
            "standing",
            "sitting",
            "kneeling",
            "fighting stance",
            "relaxed",
            "serious",
            "smiling",
            "frowning",
            "determined",
            "confident",
        ]

        desc_lower = description.lower()
        for pose in pose_terms:
            if pose in desc_lower:
                poses.append(pose)

        return poses

    def _extract_environment(self, description: str) -> list[str]:
        """Extract environment elements."""
        environment = []
        env_terms = [
            "forest",
            "dungeon",
            "castle",
            "tavern",
            "battlefield",
            "mountains",
            "desert",
            "ocean",
            "city",
            "village",
        ]

        desc_lower = description.lower()
        for env in env_terms:
            if env in desc_lower:
                environment.append(env)

        return environment

    def _extract_theme_elements(self, description: str) -> dict[str, Any]:
        """Extract theme elements from description."""
        return {
            "genre": self._detect_genre(description),
            "setting": self._detect_setting(description),
            "mood": self._detect_mood(description),
            "technology_level": self._detect_technology_level(description),
            "magical_elements": self._detect_magical_elements(description),
        }

    def _detect_genre(self, description: str) -> str:
        """Detect genre from description."""
        desc_lower = description.lower()

        if any(term in desc_lower for term in ["fantasy", "magic", "dragon", "wizard"]):
            return "fantasy"
        if any(term in desc_lower for term in ["sci-fi", "space", "robot", "future"]):
            return "science_fiction"
        if any(term in desc_lower for term in ["medieval", "knight", "castle"]):
            return "medieval"
        if any(term in desc_lower for term in ["modern", "contemporary", "city"]):
            return "modern"
        return "generic"

    def _detect_setting(self, description: str) -> str:
        """Detect setting from description."""
        desc_lower = description.lower()

        if any(term in desc_lower for term in ["urban", "city", "street"]):
            return "urban"
        if any(term in desc_lower for term in ["wilderness", "forest", "nature"]):
            return "wilderness"
        if any(term in desc_lower for term in ["dungeon", "underground", "cave"]):
            return "underground"
        if any(term in desc_lower for term in ["indoor", "building", "interior"]):
            return "indoor"
        return "outdoor"

    def _detect_mood(self, description: str) -> str:
        """Detect mood from description."""
        desc_lower = description.lower()

        if any(term in desc_lower for term in ["dark", "gloomy", "ominous"]):
            return "dark"
        if any(term in desc_lower for term in ["bright", "cheerful", "happy"]):
            return "bright"
        if any(term in desc_lower for term in ["mysterious", "eerie", "haunting"]):
            return "mysterious"
        if any(term in desc_lower for term in ["epic", "heroic", "grand"]):
            return "epic"
        return "neutral"

    def _detect_technology_level(self, description: str) -> str:
        """Detect technology level from description."""
        desc_lower = description.lower()

        if any(term in desc_lower for term in ["primitive", "stone", "tribal"]):
            return "primitive"
        if any(term in desc_lower for term in ["medieval", "sword", "armor"]):
            return "medieval"
        if any(term in desc_lower for term in ["renaissance", "gunpowder"]):
            return "renaissance"
        if any(term in desc_lower for term in ["industrial", "steam", "machine"]):
            return "industrial"
        if any(term in desc_lower for term in ["modern", "contemporary"]):
            return "modern"
        if any(term in desc_lower for term in ["futuristic", "advanced", "sci-fi"]):
            return "futuristic"
        return "mixed"

    def _detect_magical_elements(self, description: str) -> list[str]:
        """Detect magical elements from description."""
        magical = []
        magic_terms = [
            "magic",
            "spell",
            "enchanted",
            "mystical",
            "glowing",
            "rune",
            "crystal",
            "potion",
            "wizard",
            "sorcerer",
        ]

        desc_lower = description.lower()
        for term in magic_terms:
            if term in desc_lower:
                magical.append(term)

        return magical

    def _generate_consistency_rules(self, visual_elements: dict[str, Any]) -> list[str]:
        """Generate consistency rules from visual elements."""
        rules = []

        if visual_elements.get("colors"):
            rules.append(
                f"Maintain primary colors: {', '.join(visual_elements['colors'][:3])}"
            )

        if visual_elements.get("physical_features"):
            rules.append(
                f"Preserve key features: {', '.join(visual_elements['physical_features'][:3])}"
            )

        if visual_elements.get("clothing_armor"):
            rules.append(
                f"Keep signature items: {', '.join(visual_elements['clothing_armor'][:2])}"
            )

        return rules

    def _calculate_consistency_score(
        self, profile_elements: dict[str, Any], new_elements: dict[str, Any]
    ) -> float:
        """Calculate consistency score between profile and new elements."""
        if not profile_elements or not new_elements:
            return 0.0

        scores = []

        for category in profile_elements:
            if category in new_elements:
                profile_items = (
                    set(profile_elements[category])
                    if profile_elements[category]
                    else set()
                )
                new_items = (
                    set(new_elements[category]) if new_elements[category] else set()
                )

                if profile_items and new_items:
                    # Calculate Jaccard similarity
                    intersection = len(profile_items.intersection(new_items))
                    union = len(profile_items.union(new_items))
                    similarity = intersection / union if union > 0 else 0.0
                    scores.append(similarity)
                elif not profile_items and not new_items:
                    scores.append(1.0)  # Both empty
                else:
                    scores.append(0.0)  # One empty, one not

        return sum(scores) / len(scores) if scores else 0.0

    def _check_consistency_violations(
        self, profile: dict[str, Any], new_elements: dict[str, Any], prompt: str
    ) -> list[dict[str, Any]]:
        """Check for consistency violations."""
        violations = []
        rules = profile.get("consistency_rules", [])

        # Check each rule
        for rule in rules:
            if self._violates_rule(rule, new_elements, prompt):
                violations.append(
                    {
                        "rule": rule,
                        "severity": "medium",
                        "description": f"Generated content may violate: {rule}",
                    }
                )

        return violations

    def _violates_rule(self, rule: str, elements: dict[str, Any], prompt: str) -> bool:
        """Check if elements violate a specific rule."""
        # Simple rule checking - could be enhanced with more sophisticated logic
        rule_lower = rule.lower()
        combined_text = (str(elements) + " " + prompt).lower()

        # Check for color consistency
        if "color" in rule_lower:
            if "red" in rule_lower and "red" not in combined_text:
                return True
            if "blue" in rule_lower and "blue" not in combined_text:
                return True

        # Check for feature consistency
        if "feature" in rule_lower:
            if "beard" in rule_lower and "beard" not in combined_text:
                return True

        return False

    def _generate_consistency_recommendations(
        self, profile: dict[str, Any], violations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations for maintaining consistency."""
        recommendations = []

        # Add rule-based recommendations
        for rule in profile.get("consistency_rules", []):
            recommendations.append(f"Ensure: {rule}")

        # Add violation-specific recommendations
        for violation in violations:
            recommendations.append(f"Address violation: {violation['description']}")

        return recommendations

    def _generate_theme_requirements(self, theme_elements: dict[str, Any]) -> list[str]:
        """Generate theme consistency requirements."""
        requirements = []

        if theme_elements.get("genre"):
            requirements.append(f"Maintain {theme_elements['genre']} genre elements")

        if theme_elements.get("mood"):
            requirements.append(f"Preserve {theme_elements['mood']} mood")

        if theme_elements.get("technology_level"):
            requirements.append(
                f"Keep {theme_elements['technology_level']} technology level"
            )

        return requirements

    def _calculate_theme_consistency(
        self, theme_elements: dict[str, Any], content_elements: dict[str, Any]
    ) -> float:
        """Calculate consistency with theme."""
        # Simple theme consistency calculation
        matches = 0
        total = 0

        for key in theme_elements:
            if key in content_elements:
                total += 1
                if theme_elements[key] == content_elements.get(key):
                    matches += 1

        return matches / total if total > 0 else 0.0

    def _check_theme_violations(
        self, theme: dict[str, Any], elements: dict[str, Any], content_type: str
    ) -> list[dict[str, Any]]:
        """Check for theme violations."""
        violations = []
        requirements = theme.get("consistency_requirements", [])

        for requirement in requirements:
            if self._violates_theme_requirement(requirement, elements):
                violations.append(
                    {
                        "requirement": requirement,
                        "severity": "medium",
                        "content_type": content_type,
                    }
                )

        return violations

    def _violates_theme_requirement(
        self, requirement: str, elements: dict[str, Any]
    ) -> bool:
        """Check if elements violate theme requirement."""
        # Simple requirement checking
        req_lower = requirement.lower()
        elements_text = str(elements).lower()

        if "fantasy" in req_lower and "fantasy" not in elements_text:
            return True
        return bool("dark" in req_lower and "dark" not in elements_text)

    def _calculate_theme_adherence(
        self, theme: dict[str, Any], elements: dict[str, Any]
    ) -> dict[str, float]:
        """Calculate theme adherence metrics."""
        return {
            "genre_adherence": 0.8,  # Placeholder calculation
            "mood_adherence": 0.7,
            "style_adherence": 0.9,
        }

    def _generate_theme_recommendations(
        self, theme: dict[str, Any], violations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate theme consistency recommendations."""
        recommendations = []

        for requirement in theme.get("consistency_requirements", []):
            recommendations.append(f"Follow theme requirement: {requirement}")

        for violation in violations:
            recommendations.append(
                f"Address theme violation: {violation['requirement']}"
            )

        return recommendations

    def _analyze_character_consistency(self, campaign_id: str) -> dict[str, Any]:
        """Analyze character consistency for campaign."""
        profiles = []
        for char_id, profile in self.character_visual_profiles.items():
            if True:  # Simple campaign association
                profiles.append(
                    {
                        "character_id": char_id,
                        "character_name": profile["character_name"],
                        "consistency_score": self._calculate_character_consistency_score(
                            profile
                        ),
                        "violation_count": len(profile.get("violation_history", [])),
                    }
                )

        return {
            "profiles": profiles,
            "average_score": sum(p["consistency_score"] for p in profiles)
            / len(profiles)
            if profiles
            else 0.0,
            "total_violations": sum(p["violation_count"] for p in profiles),
        }

    def _analyze_theme_consistency(self, campaign_id: str) -> dict[str, Any]:
        """Analyze theme consistency for campaign."""
        themes = []
        for theme_id, theme in self.world_visual_themes.items():
            if True:  # Simple campaign association
                themes.append(
                    {
                        "theme_id": theme_id,
                        "theme_name": theme["theme_name"],
                        "usage_count": theme["usage_count"],
                        "consistency_score": self._calculate_theme_consistency_score(
                            theme
                        ),
                    }
                )

        return {
            "themes": themes,
            "average_score": sum(t["consistency_score"] for t in themes) / len(themes)
            if themes
            else 0.0,
            "total_usage": sum(t["usage_count"] for t in themes),
        }

    def _calculate_character_consistency_score(self, profile: dict[str, Any]) -> float:
        """Calculate consistency score for character profile."""
        history = profile.get("violation_history", [])
        if not history:
            return 1.0

        scores = [h.get("consistency_score", 0.0) for h in history]
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_theme_consistency_score(self, theme: dict[str, Any]) -> float:
        """Calculate consistency score for theme."""
        content = theme.get("associated_content", [])
        if not content:
            return 1.0

        scores = [c.get("consistency_score", 0.0) for c in content]
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_overall_consistency(
        self, character_analysis: dict[str, Any], theme_analysis: dict[str, Any]
    ) -> float:
        """Calculate overall consistency score."""
        char_score = character_analysis.get("average_score", 0.0)
        theme_score = theme_analysis.get("average_score", 0.0)

        return (char_score + theme_score) / 2.0

    def _generate_campaign_recommendations(
        self, character_analysis: dict[str, Any], theme_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate campaign-wide recommendations."""
        recommendations = []

        if character_analysis.get("average_score", 0.0) < 0.7:
            recommendations.append("Improve character visual consistency")

        if theme_analysis.get("average_score", 0.0) < 0.7:
            recommendations.append("Strengthen world theme adherence")

        if character_analysis.get("total_violations", 0) > 5:
            recommendations.append("Review and update character visual profiles")

        return recommendations

    def _update_profile_elements(
        self, profile: dict[str, Any], new_elements: dict[str, Any]
    ) -> None:
        """Update profile with new consistent elements."""
        for category, elements in new_elements.items():
            if category in profile["visual_elements"]:
                # Merge elements while maintaining uniqueness
                existing = set(profile["visual_elements"][category])
                new_set = set(elements)
                profile["visual_elements"][category] = list(existing.union(new_set))

        profile["update_count"] += 1

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime

        return datetime.datetime.now().isoformat()
