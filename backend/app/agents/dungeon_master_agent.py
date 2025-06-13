"""
Dungeon Master Agent - The orchestrator agent that coordinates all other agents.
"""

import logging
import random
from typing import Dict, Any, Tuple

# Note: Updated for newer Semantic Kernel version
# ToolManager import commented out as it's causing issues
# from semantic_kernel.tools.tool_manager import ToolManager

from app.kernel_setup import kernel_manager
from app.agents.narrator_agent import get_narrator
from app.agents.artist_agent import get_artist
from app.agents.scribe_agent import get_scribe
# Temporarily commenting out other agent imports to fix SK compatibility
# from app.agents.combat_mc_agent import combat_mc
# from app.agents.combat_cartographer_agent import combat_cartographer

logger = logging.getLogger(__name__)


class DungeonMasterAgent:
    """
    Dungeon Master Agent that acts as the orchestrator for all other agents.
    This is the primary user-facing agent that manages player interactions and conversation flow.
    """

    def __init__(self):
        """Initialize the Dungeon Master agent with its own kernel instance."""
        # Initialize basic attributes first
        self.active_sessions = {}
        self._fallback_mode = False
        self.kernel = None
        
        try:
            # Try to create kernel - this will fail if Azure OpenAI is not configured
            self.kernel = kernel_manager.create_kernel()
            # ToolManager initialization commented out as it's causing issues
            # self.tool_manager = ToolManager(self.kernel)
            self._register_plugins()
            
        except Exception as e:
            # Check if this is a configuration error
            error_msg = str(e)
            if (("validation errors for Settings" in error_msg and (
                "azure_openai" in error_msg or "openai" in error_msg
            )) or "Azure OpenAI configuration is missing or invalid" in error_msg):
                logger.warning(
                    "Azure OpenAI configuration is missing or invalid. "
                    "Operating in fallback mode with basic functionality. "
                    "For full AI features, ensure the following environment variables are set: "
                    "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                    "AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
                )
                # Initialize in fallback mode
                self._fallback_mode = True
                self._initialize_fallback_components()
            else:
                # Re-raise other errors as-is
                raise

    def _register_plugins(self):
        """Register necessary plugins for the Dungeon Master agent."""
        try:
            # Import plugins
            from app.plugins.narrative_memory_plugin import NarrativeMemoryPlugin
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            # Create plugin instances
            narrative_memory = NarrativeMemoryPlugin()
            rules_engine = RulesEnginePlugin()

            # Register plugins with the kernel using the new API
            self.kernel.add_plugin(narrative_memory, "Memory")
            self.kernel.add_plugin(rules_engine, "Rules")

            # Add tools to the tool manager
            # self.tool_manager.add_tool(narrative_memory.remember_fact)
            # self.tool_manager.add_tool(narrative_memory.recall_facts)
            # self.tool_manager.add_tool(rules_engine.roll_dice)

            logger.info("Dungeon Master agent plugins registered successfully")
        except Exception as e:
            logger.error(f"Error registering Dungeon Master agent plugins: {str(e)}")
            # Implement proper fallback behavior when plugin registration fails
            self._fallback_mode = True
            logger.warning("Dungeon Master agent entering fallback mode - using core functionality without advanced plugins")
            
            # Initialize basic fallback components
            self._initialize_fallback_components()

    def _initialize_fallback_components(self):
        """Initialize fallback components when plugin registration fails."""
        try:
            # Set fallback mode flag
            self._fallback_mode = True
            
            # Initialize basic dice rolling functionality
            self._fallback_dice = {
                "d4": lambda n=1: [random.randint(1, 4) for _ in range(n)],
                "d6": lambda n=1: [random.randint(1, 6) for _ in range(n)],
                "d8": lambda n=1: [random.randint(1, 8) for _ in range(n)],
                "d10": lambda n=1: [random.randint(1, 10) for _ in range(n)],
                "d12": lambda n=1: [random.randint(1, 12) for _ in range(n)],
                "d20": lambda n=1: [random.randint(1, 20) for _ in range(n)],
                "d100": lambda n=1: [random.randint(1, 100) for _ in range(n)]
            }
            
            # Initialize basic narrative responses
            self._fallback_responses = {
                "combat": [
                    "The battle intensifies as your enemies press their attack!",
                    "Steel clashes against steel in the heat of combat!",
                    "The tide of battle shifts with each passing moment!"
                ],
                "exploration": [
                    "You venture forth into the unknown, ready for whatever awaits.",
                    "The path ahead is shrouded in mystery and possibility.",
                    "Your footsteps echo as you explore this new area."
                ],
                "social": [
                    "The conversation takes an interesting turn...",
                    "Your words carry weight in this interaction.",
                    "The NPCs listen carefully to what you have to say."
                ],
                "default": [
                    "The adventure continues as you face new challenges.",
                    "Your actions have consequences in this unfolding story.",
                    "The world responds to your choices and decisions."
                ]
            }
            
            # Initialize basic campaign templates
            self._fallback_campaign_templates = {
                "fantasy": {
                    "setting": "A classic fantasy world of magic and adventure",
                    "themes": ["heroism", "magic", "ancient evils"],
                    "locations": ["tavern", "dungeon", "forest", "castle"],
                    "npcs": ["innkeeper", "guard", "wizard", "merchant"]
                },
                "modern": {
                    "setting": "Contemporary world with hidden supernatural elements",
                    "themes": ["mystery", "investigation", "urban fantasy"],
                    "locations": ["city", "office", "warehouse", "apartment"],
                    "npcs": ["detective", "informant", "scientist", "witness"]
                },
                "sci-fi": {
                    "setting": "Futuristic space-faring civilization",
                    "themes": ["technology", "exploration", "alien contact"],
                    "locations": ["space station", "planet", "ship", "laboratory"],
                    "npcs": ["captain", "engineer", "scientist", "alien"]
                }
            }
            
            logger.info("Fallback components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing fallback components: {str(e)}")
            # Even fallback initialization failed - set to minimal mode
            self._fallback_mode = True
            self._minimal_mode = True

    def _fallback_dice_roll(self, dice_notation: str) -> Dict[str, Any]:
        """Fallback dice rolling when plugins aren't available."""
        import re
        
        try:
            # Parse dice notation (e.g., "2d6+3", "1d20")
            match = re.match(r"(\d+)?d(\d+)([+-]\d+)?", dice_notation.lower())
            if not match:
                return {"error": f"Invalid dice notation: {dice_notation}"}
            
            num_dice = int(match.group(1)) if match.group(1) else 1
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            # Roll the dice
            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            return {
                "notation": dice_notation,
                "rolls": rolls,
                "modifier": modifier,
                "total": total,
                "details": f"Rolled {rolls} + {modifier} = {total}"
            }
            
        except Exception as e:
            return {"error": f"Error rolling dice: {str(e)}"}

    def _fallback_generate_response(self, context: str = "default") -> str:
        """Generate a basic narrative response in fallback mode."""
        import random
        
        responses = self._fallback_responses.get(context, self._fallback_responses["default"])
        return random.choice(responses)

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign based on the provided settings.

        Args:
            campaign_data: Campaign settings and preferences

        Returns:
            Dict[str, Any]: The created campaign
        """
        try:
            campaign_id = campaign_data.get(
                "id", f"campaign_{len(self.active_sessions) + 1}"
            )

            # Create basic campaign
            campaign = {
                "id": campaign_id,
                "name": campaign_data.get("name", "Unnamed Adventure"),
                "setting": campaign_data.get("setting", "fantasy"),
                "tone": campaign_data.get("tone", "heroic"),
                "homebrew_rules": campaign_data.get("homebrew_rules", []),
                "characters": [],
                "session_log": [],
                "state": "created",
            }

            # Generate world concept with Narrator
            world_context = {"setting": campaign["setting"], "tone": campaign["tone"]}

            # Use the get_narrator function to get a narrator instance
            narrator_agent = get_narrator()
            world_description = await narrator_agent.describe_scene(world_context)
            campaign["world_description"] = world_description

            # Use the get_artist function to get an artist instance
            artist_agent = get_artist()
            world_art = await artist_agent.illustrate_scene(world_context)
            campaign["world_art"] = world_art

            # Store campaign
            self.active_sessions[campaign_id] = campaign

            return campaign

        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            return {"error": "Failed to create campaign"}

    async def process_input(
        self, user_input: str, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Process user input and coordinate responses from specialized agents.

        Args:
            user_input: The player's input text
            context: Additional context information (game state, etc.)

        Returns:
            Dict[str, Any]: The response data including messages and any updates
        """
        if not context:
            context = {}

        logger.info(f"Processing player input: {user_input}")

        # Check if we're in fallback mode
        if getattr(self, '_fallback_mode', False):
            return await self._process_input_fallback(user_input, context)

        try:
            # Analyze the input type to determine which agents to invoke
            input_type, input_details = await self._analyze_input(user_input, context)

            # Prepare response object
            response = {
                "message": "",
                "narration": "",
                "state_updates": {},
                "visuals": [],
                "combat_updates": None,
            }

            # Route to appropriate agents based on input type
            if input_type == "narrative":
                # Handle narrative input with Narrator agent
                narrator_agent = get_narrator()
                narrative_result = await narrator_agent.process_action(
                    user_input, context
                )
                response["message"] = narrative_result.get("description", "")
                response["state_updates"] = narrative_result.get("state_updates", {})

                # Generate scene illustration if significant
                if narrative_result.get("significant_moment", False):
                    artist_agent = get_artist()
                    scene_art = await artist_agent.illustrate_scene(
                        narrative_result.get("scene_context", {})
                    )
                    response["visuals"].append(scene_art)

            elif input_type == "character":
                # Handle character-related input with Scribe agent
                scribe_agent = get_scribe()
                character_id = context.get("character_id")
                if character_id:
                    character_result = await scribe_agent.update_character(
                        character_id, input_details
                    )
                    response["message"] = "Your character has been updated."
                    response["state_updates"] = {"character": character_result}
                else:
                    response["message"] = "No character ID provided for update."

            elif input_type == "combat":
                # Combat functionality is temporarily disabled
                response["message"] = "Combat functionality is temporarily disabled."

                # Commented out due to missing combat agent implementation
                # Handle combat input with Combat MC agent
                # if context.get("combat_state") == "active":
                #     combat_mc_agent = get_combat_mc()
                #     combat_result = await combat_mc_agent.process_combat_action(
                #         user_input,
                #         context.get("combat_id"),
                #         context.get("character_id")
                #     )
                #     response["message"] = combat_result.get("description", "")
                #     response["combat_updates"] = combat_result.get("updates", {})
                #
                #     # Update battle map if needed
                #     if "map_id" in context:
                #         combat_cartographer_agent = get_combat_cartographer()
                #         updated_map = await combat_cartographer_agent.update_map_with_combat_state(
                #             context["map_id"],
                #             combat_result.get("updates", {})
                #         )
                #         response["visuals"].append(updated_map)
                # else:
                #     # Initiate combat if needed
                #     combat_context = {
                #         "location": context.get("location", "unknown"),
                #         "encounter_type": input_details.get("encounter_type", "random")
                #     }
                #     combat_mc_agent = get_combat_mc()
                #     encounter = await combat_mc_agent.create_encounter(
                #         {"members": [{"id": context.get("character_id")}]},
                #         combat_context
                #     )
                #
                #     # Generate battle map
                #     combat_cartographer_agent = get_combat_cartographer()
                #     battle_map = await combat_cartographer_agent.generate_battle_map(
                #         combat_context,
                #         encounter
                #     )
                #
                #     response["message"] = "Combat has begun! Roll for initiative!"
                #     response["combat_updates"] = encounter
                #     response["visuals"].append(battle_map)

            # If no input type was matched, provide generic response
            if not response["message"]:
                response["message"] = (
                    f"I understand your request '{user_input}'. How would you like to proceed?"
                )

            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                "message": "I'm sorry, I encountered an issue processing your request. Please try again.",
                "error": str(e),
            }

    async def _process_input_fallback(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input in fallback mode with basic functionality."""
        logger.info("Processing input in fallback mode")
        
        try:
            # Check for dice rolls first
            input_lower = user_input.lower()
            if any(dice in input_lower for dice in ["roll", "d4", "d6", "d8", "d10", "d12", "d20", "d100"]):
                dice_result = self._handle_fallback_dice_roll(user_input)
                return {
                    "message": dice_result.get("details", "Dice rolled"),
                    "dice_result": dice_result,
                    "state_updates": {},
                    "visuals": [],
                    "combat_updates": None
                }
            
            # Use the full input analysis even in fallback mode (just without AI)
            input_type, input_details = await self._analyze_input(user_input, context)
            
            # Generate appropriate response based on input type
            if input_type == "combat":
                action_type = input_details.get("action_type", "combat_general")
                if action_type == "spell_casting":
                    message = "You focus your magical energy and cast your spell!"
                elif action_type == "physical_attack":
                    message = "You strike with precision and force!"
                else:
                    message = "The battle intensifies as combat unfolds!"
                message += f" You attempt to {user_input.lower()}."
                
            elif input_type == "character":
                message = "You manage your character's capabilities and equipment."
                
            elif input_type == "narrative":
                action_type = input_details.get("action_type", "exploration")
                if action_type == "social_interaction":
                    message = "The conversation develops as you engage with others. You try to communicate your intentions."
                elif action_type == "movement":
                    message = "You move carefully through the environment, taking in your new surroundings."
                else:
                    message = "You explore the area around you, alert for anything of interest. You carefully examine your surroundings."
            else:
                # Default response
                message = f"The adventure continues as you take action: {user_input}"
            
            return {
                "message": message,
                "narration": f"In this moment of adventure, {message.lower()}",
                "state_updates": {"last_action": user_input},
                "visuals": [],
                "combat_updates": None,
                "fallback_mode": True
            }
            
        except Exception as e:
            logger.error(f"Error in fallback processing: {str(e)}")
            return {
                "message": "The adventure continues, though the path is unclear.",
                "error": f"Fallback processing failed: {str(e)}",
                "state_updates": {},
                "visuals": [],
                "combat_updates": None,
                "fallback_mode": True
            }

    def _handle_fallback_dice_roll(self, user_input: str) -> Dict[str, Any]:
        """Handle dice rolling in fallback mode."""
        import re
        
        # Extract dice notation from input
        dice_patterns = [
            r"(\d*d\d+(?:[+-]\d+)?)",  # Standard notation like 2d6+3
            r"roll\s+(\d*d\d+)",       # "roll 2d6"
            r"(\d+)d(\d+)",            # Simple XdY format
        ]
        
        for pattern in dice_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                if len(match.groups()) == 1:
                    dice_notation = match.group(1)
                else:
                    # Handle XdY format
                    num_dice = match.group(1) or "1"
                    die_size = match.group(2)
                    dice_notation = f"{num_dice}d{die_size}"
                
                return self._fallback_dice_roll(dice_notation)
        
        # Default to d20 if no specific dice found
        return self._fallback_dice_roll("1d20")

    async def _analyze_input(
        self, user_input: str, context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze user input to determine its type and extract relevant details.

        Args:
            user_input: The player's input text
            context: Current game context

        Returns:
            Tuple[str, Dict[str, Any]]: Input type and extracted details
        """
        # Skip AI analysis if in fallback mode or if Azure OpenAI is not available
        if not getattr(self, '_fallback_mode', True):
            try:
                # Enhanced input analysis using Azure OpenAI for better intent recognition
                from app.azure_openai_client import AzureOpenAIClient

                openai_client = AzureOpenAIClient()

                # Prepare analysis prompt for the AI
                analysis_prompt = f"""
                Analyze the following D&D player input and classify it into one of these categories:
                - "combat" (fighting, attacking, casting spells, initiative, combat actions)
                - "character" (inventory management, leveling up, equipment, abilities, character sheet updates)
                - "narrative" (exploration, roleplay, story actions, talking to NPCs)

                Player input: "{user_input}"
                Current context: {context.get("location", "unknown location")}

                Respond with JSON format:
                {{"category": "combat|character|narrative", "action_type": "specific_action", "confidence": 0.8}}
                """

                messages = [
                    {
                        "role": "system",
                        "content": "You are a D&D game assistant that analyzes player intent. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ]

                # Get AI analysis
                response = await openai_client.chat_completion(
                    messages, max_tokens=150, temperature=0.3
                )

                # Parse AI response
                import json

                try:
                    analysis = json.loads(response.strip())
                    category = analysis.get("category", "narrative")
                    action_type = analysis.get("action_type", "general")
                    confidence = analysis.get("confidence", 0.5)

                    # If confidence is too low, fall back to keyword analysis
                    if confidence < 0.6:
                        raise ValueError("Low confidence, using fallback")

                    return category, {
                        "action_type": action_type,
                        "confidence": confidence,
                        "method": "ai_analysis",
                    }

                except (json.JSONDecodeError, ValueError):
                    # Fall back to keyword analysis if AI parsing fails
                    logger.warning(
                        "AI analysis failed, falling back to keyword-based approach"
                    )

            except Exception as e:
                logger.warning(
                    f"Enhanced input analysis failed: {str(e)}, using keyword-based approach"
                )

        # Fallback: Enhanced keyword-based approach with better patterns
        input_lower = user_input.lower()

        # Combat indicators with more comprehensive patterns
        combat_keywords = [
            "attack",
            "fight",
            "cast spell",
            "initiative",
            "roll",
            "hit",
            "damage",
            "sword",
            "bow",
            "magic",
            "spell",
            "fireball",
            "heal",
            "defend",
            "dodge",
            "weapon",
            "armor class",
            "saving throw",
            "d20",
            "strike",
            "shoot",
        ]
        if any(term in input_lower for term in combat_keywords):
            # Determine specific combat action type
            if any(
                term in input_lower for term in ["cast", "spell", "magic", "fireball"]
            ):
                action_type = "spell_casting"
            elif any(
                term in input_lower
                for term in ["attack", "hit", "strike", "sword", "bow"]
            ):
                action_type = "physical_attack"
            elif any(term in input_lower for term in ["roll", "d20", "saving throw"]):
                action_type = "dice_roll"
            else:
                action_type = "combat_general"
            return "combat", {"action_type": action_type, "method": "keyword_analysis"}

        # Character management indicators
        character_keywords = [
            "inventory",
            "equip",
            "level up",
            "spell",
            "ability",
            "stats",
            "character sheet",
            "equipment",
            "items",
            "backpack",
            "armor",
            "experience",
            "skills",
            "proficiency",
        ]
        if any(term in input_lower for term in character_keywords):
            # Determine specific character action type
            if any(
                term in input_lower
                for term in ["inventory", "items", "equipment", "equip"]
            ):
                action_type = "inventory_management"
            elif any(
                term in input_lower for term in ["level up", "experience", "stats"]
            ):
                action_type = "character_advancement"
            elif any(term in input_lower for term in ["spell", "ability", "skills"]):
                action_type = "ability_management"
            else:
                action_type = "character_general"
            return "character", {
                "action_type": action_type,
                "method": "keyword_analysis",
            }

        # Movement and exploration indicators
        movement_keywords = [
            "go",
            "move",
            "walk",
            "run",
            "enter",
            "exit",
            "north",
            "south",
            "east",
            "west",
        ]
        if any(term in input_lower for term in movement_keywords):
            return "narrative", {
                "action_type": "movement",
                "method": "keyword_analysis",
            }

        # Social interaction indicators
        social_keywords = [
            "talk",
            "speak",
            "say",
            "tell",
            "ask",
            "persuade",
            "intimidate",
            "deceive",
        ]
        if any(term in input_lower for term in social_keywords):
            return "narrative", {
                "action_type": "social_interaction",
                "method": "keyword_analysis",
            }

        # Default to narrative with general exploration
        return "narrative", {"action_type": "exploration", "method": "keyword_analysis"}


# Lazy singleton instance
_dungeon_master = None


def get_dungeon_master():
    """Get the dungeon master instance, creating it if necessary."""
    global _dungeon_master
    if _dungeon_master is None:
        _dungeon_master = DungeonMasterAgent()
    return _dungeon_master


# For backward compatibility during import-time checks
dungeon_master = None
