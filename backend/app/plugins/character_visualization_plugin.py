"""
Character Visualization Plugin for the Semantic Kernel.
This plugin provides specialized character portrait generation and visualization capabilities.
"""
import logging
from typing import Dict, Any, List

from semantic_kernel.functions import kernel_function
from app.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)


class CharacterVisualizationPlugin:
    """
    Plugin that provides specialized character portrait generation and visualization.
    Focuses on creating detailed, consistent character portraits for RPG characters.
    """

    def __init__(self):
        """Initialize the character visualization plugin."""
        self.azure_client = AzureOpenAIClient()
        self.character_portraits = {}
        self.character_variations = {}

    @kernel_function(
        description="Generate a detailed character portrait based on character details.",
        name="generate_character_portrait"
    )
    def generate_character_portrait(self, character_name: str, race: str = "human",
                                  character_class: str = "adventurer", gender: str = "",
                                  physical_description: str = "", equipment: str = "",
                                  personality_traits: str = "") -> Dict[str, Any]:
        """
        Generate a detailed character portrait.
        
        Args:
            character_name: Name of the character
            race: Character race (human, elf, dwarf, etc.)
            character_class: Character class (fighter, wizard, rogue, etc.)
            gender: Character gender
            physical_description: Detailed physical description
            equipment: Equipment and clothing description
            personality_traits: Personality traits to reflect in portrait
            
        Returns:
            Dict[str, Any]: Generated portrait details and image
        """
        try:
            # Build comprehensive character prompt
            prompt = self._build_character_prompt(
                character_name, race, character_class, gender,
                physical_description, equipment, personality_traits
            )
            
            # Generate the portrait
            result = self.azure_client.generate_image(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            # Create character ID for tracking
            character_id = f"{character_name.lower().replace(' ', '_')}_{len(self.character_portraits) + 1}"
            
            # Store portrait data
            portrait_data = {
                "character_id": character_id,
                "character_name": character_name,
                "race": race,
                "character_class": character_class,
                "gender": gender,
                "physical_description": physical_description,
                "equipment": equipment,
                "personality_traits": personality_traits,
                "generation_prompt": prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp(),
                "variations": []
            }
            
            self.character_portraits[character_id] = portrait_data
            
            if result.get("success"):
                return {
                    "status": "success",
                    "character_id": character_id,
                    "character_name": character_name,
                    "image_url": result["image_url"],
                    "prompt_used": prompt,
                    "revised_prompt": result.get("revised_prompt", prompt),
                    "character_details": {
                        "race": race,
                        "class": character_class,
                        "gender": gender
                    }
                }
            else:
                return {
                    "status": "error",
                    "character_id": character_id,
                    "error": result.get("error", "Portrait generation failed")
                }
                
        except Exception as e:
            logger.error(f"Error generating character portrait: {str(e)}")
            return {
                "status": "error",
                "error": f"Character portrait generation failed: {str(e)}"
            }

    @kernel_function(
        description="Generate a character portrait variation for different scenarios.",
        name="generate_character_variation"
    )
    def generate_character_variation(self, character_id: str, variation_type: str = "combat",
                                   scenario_description: str = "", mood: str = "determined") -> Dict[str, Any]:
        """
        Generate a character portrait variation for different scenarios.
        
        Args:
            character_id: ID of the base character
            variation_type: Type of variation (combat, social, exploration, resting)
            scenario_description: Description of the scenario
            mood: Character mood for the variation
            
        Returns:
            Dict[str, Any]: Generated variation details
        """
        try:
            if character_id not in self.character_portraits:
                return {
                    "status": "error",
                    "error": "Character not found"
                }
            
            base_character = self.character_portraits[character_id]
            
            # Build variation prompt
            variation_prompt = self._build_variation_prompt(
                base_character, variation_type, scenario_description, mood
            )
            
            # Generate the variation
            result = self.azure_client.generate_image(
                prompt=variation_prompt,
                size="1024x1024",
                quality="standard",
                style="vivid"
            )
            
            # Create variation data
            variation_data = {
                "variation_id": f"{character_id}_var_{len(base_character['variations']) + 1}",
                "base_character_id": character_id,
                "variation_type": variation_type,
                "scenario_description": scenario_description,
                "mood": mood,
                "generation_prompt": variation_prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp()
            }
            
            # Store variation
            base_character["variations"].append(variation_data)
            
            if result.get("success"):
                return {
                    "status": "success",
                    "variation_id": variation_data["variation_id"],
                    "character_name": base_character["character_name"],
                    "variation_type": variation_type,
                    "image_url": result["image_url"],
                    "prompt_used": variation_prompt,
                    "base_character_id": character_id
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Variation generation failed")
                }
                
        except Exception as e:
            logger.error(f"Error generating character variation: {str(e)}")
            return {
                "status": "error",
                "error": f"Character variation generation failed: {str(e)}"
            }

    @kernel_function(
        description="Generate a group portrait with multiple characters.",
        name="generate_group_portrait"
    )
    def generate_group_portrait(self, character_ids: str, group_name: str = "Adventure Party",
                              scene_setting: str = "tavern", interaction: str = "standing together") -> Dict[str, Any]:
        """
        Generate a group portrait with multiple characters.
        
        Args:
            character_ids: Comma-separated list of character IDs
            group_name: Name for the group
            scene_setting: Setting for the group portrait
            interaction: Type of interaction between characters
            
        Returns:
            Dict[str, Any]: Generated group portrait
        """
        try:
            # Parse character IDs
            char_ids = [cid.strip() for cid in character_ids.split(",") if cid.strip()]
            
            if not char_ids:
                return {
                    "status": "error",
                    "error": "No character IDs provided"
                }
            
            # Get character data
            characters = []
            for char_id in char_ids:
                if char_id in self.character_portraits:
                    characters.append(self.character_portraits[char_id])
                else:
                    logger.warning(f"Character {char_id} not found")
            
            if not characters:
                return {
                    "status": "error",
                    "error": "No valid characters found"
                }
            
            # Build group prompt
            group_prompt = self._build_group_prompt(
                characters, group_name, scene_setting, interaction
            )
            
            # Generate the group portrait
            result = self.azure_client.generate_image(
                prompt=group_prompt,
                size="1792x1024",  # Wider format for group
                quality="standard",
                style="vivid"
            )
            
            # Create group portrait data
            group_id = f"group_{len(self.character_variations) + 1}"
            group_data = {
                "group_id": group_id,
                "group_name": group_name,
                "character_ids": char_ids,
                "character_names": [c["character_name"] for c in characters],
                "scene_setting": scene_setting,
                "interaction": interaction,
                "generation_prompt": group_prompt,
                "generation_result": result,
                "created_timestamp": self._get_timestamp()
            }
            
            self.character_variations[group_id] = group_data
            
            if result.get("success"):
                return {
                    "status": "success",
                    "group_id": group_id,
                    "group_name": group_name,
                    "character_count": len(characters),
                    "character_names": group_data["character_names"],
                    "image_url": result["image_url"],
                    "prompt_used": group_prompt,
                    "scene_setting": scene_setting
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Group portrait generation failed")
                }
                
        except Exception as e:
            logger.error(f"Error generating group portrait: {str(e)}")
            return {
                "status": "error",
                "error": f"Group portrait generation failed: {str(e)}"
            }

    @kernel_function(
        description="Get character portrait gallery for a character.",
        name="get_character_gallery"
    )
    def get_character_gallery(self, character_id: str) -> Dict[str, Any]:
        """
        Get all portraits and variations for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dict[str, Any]: Character portrait gallery
        """
        try:
            if character_id not in self.character_portraits:
                return {
                    "status": "error",
                    "error": "Character not found"
                }
            
            character = self.character_portraits[character_id]
            
            # Compile gallery
            gallery = {
                "character_id": character_id,
                "character_name": character["character_name"],
                "base_portrait": {
                    "image_url": character["generation_result"].get("image_url"),
                    "prompt": character["generation_prompt"],
                    "created": character["created_timestamp"]
                },
                "variations": [],
                "total_images": 1 + len(character["variations"])
            }
            
            # Add variations
            for variation in character["variations"]:
                if variation["generation_result"].get("success"):
                    gallery["variations"].append({
                        "variation_id": variation["variation_id"],
                        "type": variation["variation_type"],
                        "mood": variation["mood"],
                        "image_url": variation["generation_result"]["image_url"],
                        "scenario": variation["scenario_description"],
                        "created": variation["created_timestamp"]
                    })
            
            return {
                "status": "success",
                "gallery": gallery
            }
            
        except Exception as e:
            logger.error(f"Error getting character gallery: {str(e)}")
            return {
                "status": "error",
                "error": f"Character gallery retrieval failed: {str(e)}"
            }

    @kernel_function(
        description="Generate character expression study showing different emotions.",
        name="generate_expression_study"
    )
    def generate_expression_study(self, character_id: str, expressions: str = "happy,sad,angry,surprised") -> Dict[str, Any]:
        """
        Generate a character expression study showing different emotions.
        
        Args:
            character_id: ID of the character
            expressions: Comma-separated list of expressions to generate
            
        Returns:
            Dict[str, Any]: Expression study results
        """
        try:
            if character_id not in self.character_portraits:
                return {
                    "status": "error",
                    "error": "Character not found"
                }
            
            base_character = self.character_portraits[character_id]
            expression_list = [e.strip() for e in expressions.split(",") if e.strip()]
            
            if not expression_list:
                return {
                    "status": "error",
                    "error": "No expressions provided"
                }
            
            # Generate expression variations
            expression_results = []
            
            for expression in expression_list:
                # Build expression prompt
                expr_prompt = self._build_expression_prompt(base_character, expression)
                
                # Generate the expression
                result = self.azure_client.generate_image(
                    prompt=expr_prompt,
                    size="1024x1024",
                    quality="standard",
                    style="vivid"
                )
                
                expression_data = {
                    "expression": expression,
                    "prompt": expr_prompt,
                    "result": result,
                    "success": result.get("success", False)
                }
                
                expression_results.append(expression_data)
            
            # Create study data
            study_id = f"{character_id}_expressions"
            study_data = {
                "study_id": study_id,
                "character_id": character_id,
                "character_name": base_character["character_name"],
                "expressions": expression_results,
                "created_timestamp": self._get_timestamp()
            }
            
            successful_expressions = [e for e in expression_results if e["success"]]
            
            return {
                "status": "success",
                "study_id": study_id,
                "character_name": base_character["character_name"],
                "total_expressions": len(expression_list),
                "successful_generations": len(successful_expressions),
                "expressions": [
                    {
                        "expression": e["expression"],
                        "image_url": e["result"].get("image_url"),
                        "success": e["success"]
                    }
                    for e in expression_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating expression study: {str(e)}")
            return {
                "status": "error",
                "error": f"Expression study generation failed: {str(e)}"
            }

    def _build_character_prompt(self, name: str, race: str, char_class: str, gender: str,
                              physical_desc: str, equipment: str, personality: str) -> str:
        """Build a comprehensive character portrait prompt."""
        # Base prompt
        prompt = f"Fantasy character portrait of {name}"
        
        # Add demographics
        if gender and race:
            prompt += f", a {gender} {race}"
        elif race:
            prompt += f", a {race}"
        
        if char_class:
            prompt += f" {char_class}"
        
        # Add physical description
        if physical_desc:
            prompt += f". {physical_desc}"
        
        # Add equipment description
        if equipment:
            prompt += f". Wearing {equipment}"
        
        # Add personality reflection
        if personality:
            personality_visual = self._translate_personality_to_visual(personality)
            if personality_visual:
                prompt += f". {personality_visual}"
        
        # Add quality enhancers
        prompt += ". High quality digital art, fantasy RPG character portrait, detailed facial features, atmospheric lighting, professional character art, three-quarter view"
        
        return prompt

    def _build_variation_prompt(self, base_character: Dict[str, Any], variation_type: str,
                              scenario: str, mood: str) -> str:
        """Build a variation prompt based on base character and scenario."""
        base_desc = f"{base_character['character_name']}, a {base_character['race']} {base_character['character_class']}"
        
        if base_character.get("physical_description"):
            base_desc += f". {base_character['physical_description']}"
        
        # Add variation-specific elements
        if variation_type == "combat":
            base_desc += f". In combat stance, {mood} expression, battle-ready pose"
            if scenario:
                base_desc += f". {scenario}"
            base_desc += ". Dynamic action pose, weapon drawn, intense lighting"
        
        elif variation_type == "social":
            base_desc += f". In social setting, {mood} expression, approachable pose"
            if scenario:
                base_desc += f". {scenario}"
            base_desc += ". Friendly demeanor, warm lighting, conversational pose"
        
        elif variation_type == "exploration":
            base_desc += f". Ready for exploration, {mood} expression, alert pose"
            if scenario:
                base_desc += f". {scenario}"
            base_desc += ". Cautious stance, outdoor lighting, adventure gear visible"
        
        elif variation_type == "resting":
            base_desc += f". At rest, {mood} expression, relaxed pose"
            if scenario:
                base_desc += f". {scenario}"
            base_desc += ". Comfortable position, soft lighting, peaceful atmosphere"
        
        # Add quality enhancers
        base_desc += ". High quality digital art, fantasy RPG character, detailed features, atmospheric lighting"
        
        return base_desc

    def _build_group_prompt(self, characters: List[Dict[str, Any]], group_name: str,
                          setting: str, interaction: str) -> str:
        """Build a group portrait prompt."""
        # Start with group description
        prompt = f"Fantasy RPG group portrait of '{group_name}'"
        
        # Add character descriptions
        char_descriptions = []
        for char in characters:
            desc = f"a {char['race']} {char['character_class']}"
            if char.get("physical_description"):
                # Extract key features
                key_features = self._extract_key_features(char["physical_description"])
                if key_features:
                    desc += f" ({key_features})"
            char_descriptions.append(desc)
        
        if char_descriptions:
            prompt += f", featuring {', '.join(char_descriptions)}"
        
        # Add setting and interaction
        prompt += f". Scene: {setting}, {interaction}"
        
        # Add group dynamics
        prompt += ". Group composition showing camaraderie and team unity"
        
        # Add quality enhancers
        prompt += ". High quality digital art, fantasy RPG group portrait, detailed characters, atmospheric lighting, professional composition, wide angle view"
        
        return prompt

    def _build_expression_prompt(self, character: Dict[str, Any], expression: str) -> str:
        """Build an expression study prompt."""
        base_desc = f"Close-up portrait of {character['character_name']}, a {character['race']} {character['character_class']}"
        
        if character.get("physical_description"):
            key_features = self._extract_key_features(character["physical_description"])
            if key_features:
                base_desc += f". {key_features}"
        
        # Add expression
        expression_desc = self._get_expression_description(expression)
        base_desc += f". {expression_desc}"
        
        # Add quality enhancers
        base_desc += ". High quality digital art, fantasy character portrait, detailed facial expression, portrait lighting, emotional depth"
        
        return base_desc

    def _translate_personality_to_visual(self, personality: str) -> str:
        """Translate personality traits to visual characteristics."""
        personality_lower = personality.lower()
        visual_elements = []
        
        if "confident" in personality_lower:
            visual_elements.append("confident posture and direct gaze")
        if "shy" in personality_lower or "timid" in personality_lower:
            visual_elements.append("reserved posture and gentle expression")
        if "aggressive" in personality_lower:
            visual_elements.append("fierce expression and assertive stance")
        if "wise" in personality_lower:
            visual_elements.append("thoughtful expression and knowing eyes")
        if "cheerful" in personality_lower or "happy" in personality_lower:
            visual_elements.append("warm smile and bright eyes")
        if "serious" in personality_lower or "stern" in personality_lower:
            visual_elements.append("serious expression and firm jawline")
        
        return ", ".join(visual_elements) if visual_elements else ""

    def _extract_key_features(self, description: str) -> str:
        """Extract key visual features from description."""
        # Simple extraction of important visual elements
        key_terms = []
        desc_lower = description.lower()
        
        # Hair
        if "long hair" in desc_lower:
            key_terms.append("long hair")
        elif "short hair" in desc_lower:
            key_terms.append("short hair")
        elif "bald" in desc_lower:
            key_terms.append("bald")
        
        # Facial hair
        if "beard" in desc_lower:
            key_terms.append("beard")
        if "mustache" in desc_lower:
            key_terms.append("mustache")
        
        # Eye color
        if "blue eyes" in desc_lower:
            key_terms.append("blue eyes")
        elif "green eyes" in desc_lower:
            key_terms.append("green eyes")
        elif "brown eyes" in desc_lower:
            key_terms.append("brown eyes")
        
        # Distinctive features
        if "scar" in desc_lower:
            key_terms.append("scar")
        if "tattoo" in desc_lower:
            key_terms.append("tattoo")
        
        return ", ".join(key_terms[:3])  # Limit to top 3 features

    def _get_expression_description(self, expression: str) -> str:
        """Get detailed description for an expression."""
        expressions = {
            "happy": "Bright, genuine smile with sparkling eyes and raised cheeks",
            "sad": "Downturned mouth, drooping eyelids, and melancholic gaze",
            "angry": "Furrowed brow, clenched jaw, and intense, narrowed eyes",
            "surprised": "Wide eyes, raised eyebrows, and slightly open mouth",
            "fearful": "Wide eyes with tension, raised eyebrows, and worried expression",
            "disgusted": "Wrinkled nose, turned-down mouth, and squinted eyes",
            "neutral": "Calm, composed expression with relaxed facial features",
            "determined": "Set jaw, focused eyes, and firm expression",
            "confused": "Slightly furrowed brow, tilted head, and questioning look",
            "amused": "Slight smile, crinkled eyes, and hint of laughter"
        }
        
        return expressions.get(expression.lower(), f"{expression} expression")

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        import datetime
        return datetime.datetime.now().isoformat()