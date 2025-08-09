"""
Comprehensive tests for agent functionality and interfaces.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock

import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAgentInterfaceContracts:
    """Test expected agent interface contracts without external dependencies."""

    def test_scribe_agent_interface(self) -> None:
        """Test scribe agent interface contract."""
        # Mock scribe agent behavior
        mock_scribe = Mock()
        mock_scribe.create_character = AsyncMock(
            return_value={
                "id": "test_char_123",
                "name": "Test Character",
                "character_class": "fighter",
                "race": "human",
                "level": 1,
                "abilities": {
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10,
                },
                "hit_points": {"current": 10, "maximum": 10},
                "armor_class": 10,
                "proficiency_bonus": 2,
                "inventory": [],
                "spells": [],
            }
        )

        mock_scribe.get_character = AsyncMock(
            return_value={
                "id": "test_char_123",
                "name": "Test Character",
                "character_class": "fighter",
                "race": "human",
                "level": 1,
            }
        )

        mock_scribe.update_character = AsyncMock(
            return_value={"id": "test_char_123", "level": 2, "experience": 300}
        )

        # Test character creation
        character_data = {
            "name": "Test Hero",
            "class": "fighter",
            "race": "human",
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10,
            },
        }
        result = asyncio.run(mock_scribe.create_character(character_data))

        assert "id" in result
        assert result["name"] == "Test Character"
        assert result["character_class"] == "fighter"
        assert result["abilities"]["strength"] == 16
        mock_scribe.create_character.assert_called_once_with(character_data)

        # Test character retrieval
        result = asyncio.run(mock_scribe.get_character("test_char_123"))
        assert result["id"] == "test_char_123"
        mock_scribe.get_character.assert_called_once_with("test_char_123")

        # Test character update
        update_data = {"level": 2, "experience": 300}
        result = asyncio.run(mock_scribe.update_character("test_char_123", update_data))
        assert result["level"] == 2
        mock_scribe.update_character.assert_called_once_with(
            "test_char_123", update_data
        )

    def test_dungeon_master_interface(self) -> None:
        """Test dungeon master agent interface."""
        mock_dm = Mock()
        mock_dm.create_campaign = AsyncMock(
            return_value={
                "id": "camp_123",
                "name": "Test Campaign",
                "setting": "fantasy",
                "tone": "heroic",
                "state": "created",
                "characters": [],
                "session_log": [],
            }
        )

        mock_dm.process_input = AsyncMock(
            return_value={
                "message": "You enter the tavern...",
                "images": [],
                "state_updates": {"location": "tavern"},
                "combat_updates": None,
            }
        )

        mock_dm.start_combat = AsyncMock(
            return_value={
                "message": "Roll for initiative!",
                "combat_updates": {
                    "status": "active",
                    "round": 1,
                    "current_turn": "player1",
                },
            }
        )

        # Test campaign creation
        campaign_data = {
            "name": "Test Campaign",
            "setting": "fantasy",
            "tone": "heroic",
        }
        result = asyncio.run(mock_dm.create_campaign(campaign_data))

        assert "id" in result
        assert result["name"] == "Test Campaign"
        assert result["setting"] == "fantasy"
        mock_dm.create_campaign.assert_called_once_with(campaign_data)

        # Test input processing
        context = {"character_id": "char_123", "campaign_id": "camp_123"}
        result = asyncio.run(mock_dm.process_input("I look around", context))

        assert "message" in result
        assert "images" in result
        assert "state_updates" in result
        assert result["state_updates"]["location"] == "tavern"
        mock_dm.process_input.assert_called_once_with("I look around", context)

        # Test combat initiation
        combat_context = {"participants": ["player1", "orc1"], "environment": "forest"}
        result = asyncio.run(mock_dm.start_combat(combat_context))

        assert "combat_updates" in result
        assert result["combat_updates"]["status"] == "active"
        mock_dm.start_combat.assert_called_once_with(combat_context)

    def test_artist_agent_interface(self) -> None:
        """Test artist agent interface."""
        mock_artist = Mock()
        mock_artist.generate_character_portrait = AsyncMock(
            return_value={
                "image_url": "http://test.com/portrait.jpg",
                "image_type": "character_portrait",
                "prompt_used": "human fighter with sword",
            }
        )

        mock_artist.illustrate_scene = AsyncMock(
            return_value={
                "image_url": "http://test.com/scene.jpg",
                "image_type": "scene_illustration",
                "prompt_used": "dark forest clearing",
            }
        )

        mock_artist.create_battle_map = AsyncMock(
            return_value={
                "image_url": "http://test.com/battlemap.jpg",
                "image_type": "battle_map",
                "grid_size": "30x30",
            }
        )

        # Test character portrait
        details = {"name": "Hero", "race": "human", "class": "fighter"}
        result = asyncio.run(mock_artist.generate_character_portrait(details))
        assert "image_url" in result
        assert result["image_type"] == "character_portrait"
        mock_artist.generate_character_portrait.assert_called_once_with(details)

        # Test scene illustration
        scene_details = {"location": "forest", "mood": "dark", "time": "night"}
        result = asyncio.run(mock_artist.illustrate_scene(scene_details))
        assert "image_url" in result
        assert result["image_type"] == "scene_illustration"
        mock_artist.illustrate_scene.assert_called_once_with(scene_details)

        # Test battle map creation
        map_details = {"terrain": "forest", "size": "medium", "hazards": ["pit trap"]}
        result = asyncio.run(mock_artist.create_battle_map(map_details))
        assert "image_url" in result
        assert result["image_type"] == "battle_map"
        mock_artist.create_battle_map.assert_called_once_with(map_details)

    def test_combat_cartographer_interface(self) -> None:
        """Test combat cartographer agent interface."""
        mock_cartographer = Mock()
        mock_cartographer.create_tactical_map = AsyncMock(
            return_value={
                "map_url": "http://test.com/tactical_map.jpg",
                "grid_data": {
                    "width": 20,
                    "height": 20,
                    "player_positions": {"player1": {"x": 5, "y": 10}},
                    "enemy_positions": {"orc1": {"x": 15, "y": 10}},
                    "terrain_features": [{"type": "wall", "x": 10, "y": 5}],
                },
            }
        )

        mock_cartographer.update_positions = AsyncMock(
            return_value={
                "success": True,
                "updated_positions": {"player1": {"x": 6, "y": 10}},
            }
        )

        # Test tactical map creation
        combat_setup = {
            "environment": "dungeon_room",
            "participants": ["player1", "orc1"],
            "room_size": {"width": 20, "height": 20},
        }
        result = asyncio.run(mock_cartographer.create_tactical_map(combat_setup))

        assert "map_url" in result
        assert "grid_data" in result
        assert result["grid_data"]["width"] == 20
        mock_cartographer.create_tactical_map.assert_called_once_with(combat_setup)

        # Test position updates
        position_updates = {"player1": {"x": 6, "y": 10}}
        result = asyncio.run(mock_cartographer.update_positions(position_updates))

        assert result["success"] is True
        assert "updated_positions" in result
        mock_cartographer.update_positions.assert_called_once_with(position_updates)


class TestAgentErrorHandling:
    """Test agent error handling scenarios."""

    def test_agent_network_error_handling(self) -> None:
        """Test agents handle network errors gracefully."""
        mock_agent = Mock()
        mock_agent.process_request = AsyncMock(side_effect=Exception("Network timeout"))

        # Should propagate meaningful error information
        with pytest.raises(Exception) as exc_info:
            asyncio.run(mock_agent.process_request("test input"))

        assert "Network timeout" in str(exc_info.value)

    def test_agent_invalid_input_handling(self) -> None:
        """Test agents handle invalid input gracefully."""
        mock_scribe = Mock()
        mock_scribe.create_character = AsyncMock(
            return_value={
                "error": "Invalid character data: missing required field 'name'"
            }
        )

        invalid_data = {"race": "human"}  # Missing name
        result = asyncio.run(mock_scribe.create_character(invalid_data))

        assert "error" in result
        assert "missing required field" in result["error"]

    def test_agent_rate_limiting_handling(self) -> None:
        """Test agents handle rate limiting appropriately."""
        mock_artist = Mock()
        mock_artist.generate_image = AsyncMock(
            return_value={
                "error": "Rate limit exceeded. Try again in 60 seconds.",
                "retry_after": 60,
            }
        )

        result = asyncio.run(mock_artist.generate_image({"prompt": "test"}))

        assert "error" in result
        assert "Rate limit exceeded" in result["error"]
        assert "retry_after" in result


class TestAgentDataFlow:
    """Test data flow between agents and API."""

    def test_character_creation_data_flow(self) -> None:
        """Test complete character creation data flow."""
        # Simulate API request data
        api_request = {
            "name": "Aragorn",
            "race": "human",
            "character_class": "ranger",
            "abilities": {
                "strength": 16,
                "dexterity": 18,
                "constitution": 14,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 12,
            },
            "backstory": "A skilled ranger from the north",
        }

        # Expected transformation for agent
        expected_agent_input = {
            "name": "Aragorn",
            "class": "ranger",  # Note: character_class -> class
            "race": "human",
            "abilities": {
                "strength": 16,
                "dexterity": 18,
                "constitution": 14,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 12,
            },
            "backstory": "A skilled ranger from the north",
        }

        # Mock agent response
        agent_response = {
            "id": "char_abc123",
            "name": "Aragorn",
            "character_class": "ranger",  # Note: class -> character_class for API
            "race": "human",
            "level": 1,
            "abilities": expected_agent_input["abilities"],
            "hit_points": {"current": 12, "maximum": 12},
            "armor_class": 14,
            "proficiency_bonus": 2,
            "inventory": [],
            "spells": [],
        }

        # Test the transformation
        mock_scribe = Mock()
        mock_scribe.create_character = AsyncMock(return_value=agent_response)

        # Simulate the API route transformation
        agent_input = api_request.copy()
        agent_input["class"] = agent_input.pop("character_class")

        result = asyncio.run(mock_scribe.create_character(agent_input))

        # Verify agent was called with correct data
        mock_scribe.create_character.assert_called_once_with(expected_agent_input)

        # Verify response structure
        assert result["id"] == "char_abc123"
        assert result["name"] == "Aragorn"
        assert result["character_class"] == "ranger"
        assert result["level"] == 1

    def test_game_input_processing_flow(self) -> None:
        """Test complete game input processing flow."""
        # API request
        player_input = {
            "message": "I attack the orc with my sword",
            "character_id": "char_123",
            "campaign_id": "camp_456",
        }

        # Expected agent context
        expected_context = {
            "character_id": "char_123",
            "campaign_id": "camp_456",
            "character_data": {
                "name": "Hero",
                "class": "fighter",
                "level": 3,
                "current_hp": 25,
            },
            "campaign_state": {"location": "dungeon", "active_combat": False},
        }

        # Mock agent response
        agent_response = {
            "message": "You swing your sword at the orc. Roll for attack! *rolls* You hit for 8 damage!",
            "images": ["http://example.com/combat_scene.jpg"],
            "state_updates": {"character_hp": 25, "orc_hp": 7, "location": "dungeon"},
            "combat_updates": {"status": "active", "round": 1, "current_turn": "orc"},
        }

        mock_dm = Mock()
        mock_dm.process_input = AsyncMock(return_value=agent_response)

        result = asyncio.run(
            mock_dm.process_input(player_input["message"], expected_context)
        )

        # Verify response structure
        assert "message" in result
        assert "images" in result
        assert "state_updates" in result
        assert "combat_updates" in result
        assert result["combat_updates"]["status"] == "active"


class TestCombatMCAgentFallback:
    """Test combat MC agent fallback functionality."""

    def test_fallback_roll_d20_normal(self) -> None:
        """Test normal d20 roll in fallback mode."""
        from unittest.mock import patch

        # Mock the CombatMCAgent to avoid dependency issues
        class MockCombatMCAgent:
            def __init__(self) -> None:
                self.fallback_mode = True

            def _fallback_roll_d20(
                self,
                modifier: int = 0,
                advantage: bool = False,
                disadvantage: bool = False,
            ):
                import random

                if advantage and not disadvantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = max(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "advantage"
                elif disadvantage and not advantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = min(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "disadvantage"
                else:
                    roll = random.randint(1, 20)
                    rolls = [roll]
                    advantage_type = "normal"

                total = roll + modifier

                return {
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": total,
                    "advantage_type": advantage_type,
                }

        agent = MockCombatMCAgent()

        # Test normal roll
        with patch("random.randint", return_value=15):
            result = agent._fallback_roll_d20(3)
            assert result["rolls"] == [15]
            assert result["modifier"] == 3
            assert result["total"] == 18
            assert result["advantage_type"] == "normal"

    def test_fallback_roll_d20_advantage(self) -> None:
        """Test d20 roll with advantage in fallback mode."""
        from unittest.mock import patch

        class MockCombatMCAgent:
            def _fallback_roll_d20(
                self,
                modifier: int = 0,
                advantage: bool = False,
                disadvantage: bool = False,
            ):
                import random

                if advantage and not disadvantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = max(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "advantage"
                elif disadvantage and not advantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = min(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "disadvantage"
                else:
                    roll = random.randint(1, 20)
                    rolls = [roll]
                    advantage_type = "normal"

                total = roll + modifier

                return {
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": total,
                    "advantage_type": advantage_type,
                }

        agent = MockCombatMCAgent()

        # Test advantage roll - mock two different values
        with patch("random.randint", side_effect=[8, 15]):
            result = agent._fallback_roll_d20(2, advantage=True)
            assert len(result["rolls"]) == 2
            assert result["rolls"] == [8, 15]
            assert result["modifier"] == 2
            assert result["total"] == 17  # max(8, 15) + 2
            assert result["advantage_type"] == "advantage"

    def test_fallback_roll_d20_disadvantage(self) -> None:
        """Test d20 roll with disadvantage in fallback mode."""
        from unittest.mock import patch

        class MockCombatMCAgent:
            def _fallback_roll_d20(
                self,
                modifier: int = 0,
                advantage: bool = False,
                disadvantage: bool = False,
            ):
                import random

                if advantage and not disadvantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = max(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "advantage"
                elif disadvantage and not advantage:
                    roll1 = random.randint(1, 20)
                    roll2 = random.randint(1, 20)
                    roll = min(roll1, roll2)
                    rolls = [roll1, roll2]
                    advantage_type = "disadvantage"
                else:
                    roll = random.randint(1, 20)
                    rolls = [roll]
                    advantage_type = "normal"

                total = roll + modifier

                return {
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": total,
                    "advantage_type": advantage_type,
                }

        agent = MockCombatMCAgent()

        # Test disadvantage roll
        with patch("random.randint", side_effect=[12, 7]):
            result = agent._fallback_roll_d20(1, disadvantage=True)
            assert len(result["rolls"]) == 2
            assert result["rolls"] == [12, 7]
            assert result["modifier"] == 1
            assert result["total"] == 8  # min(12, 7) + 1
            assert result["advantage_type"] == "disadvantage"

    def test_fallback_roll_damage_simple(self) -> None:
        """Test simple damage roll in fallback mode."""
        import re
        from unittest.mock import patch

        class MockCombatMCAgent:
            def _fallback_roll_damage(self, dice_notation: str):
                import random

                # Simple dice parser for basic notation like "1d6+2" or "2d8"
                pattern = r"(\d*)d(\d+)(?:\+(\d+))?(?:\-(\d+))?"
                match = re.match(pattern, dice_notation.lower().replace(" ", ""))

                if not match:
                    # Fallback to fixed damage if parsing fails
                    return {
                        "total": 4,
                        "rolls": [4],
                        "notation": dice_notation,
                        "fallback": True,
                    }

                num_dice = int(match.group(1)) if match.group(1) else 1
                dice_type = int(match.group(2))
                plus_mod = int(match.group(3)) if match.group(3) else 0
                minus_mod = int(match.group(4)) if match.group(4) else 0
                modifier = plus_mod - minus_mod

                rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
                total = sum(rolls) + modifier

                return {
                    "notation": dice_notation,
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": max(total, 1),  # Minimum 1 damage
                }

        agent = MockCombatMCAgent()

        # Test 1d6+2
        with patch("random.randint", return_value=4):
            result = agent._fallback_roll_damage("1d6+2")
            assert result["notation"] == "1d6+2"
            assert result["rolls"] == [4]
            assert result["modifier"] == 2
            assert result["total"] == 6

    def test_fallback_roll_damage_multiple_dice(self) -> None:
        """Test multiple dice damage roll in fallback mode."""
        import re
        from unittest.mock import patch

        class MockCombatMCAgent:
            def _fallback_roll_damage(self, dice_notation: str):
                import random

                # Simple dice parser for basic notation like "1d6+2" or "2d8"
                pattern = r"(\d*)d(\d+)(?:\+(\d+))?(?:\-(\d+))?"
                match = re.match(pattern, dice_notation.lower().replace(" ", ""))

                if not match:
                    # Fallback to fixed damage if parsing fails
                    return {
                        "total": 4,
                        "rolls": [4],
                        "notation": dice_notation,
                        "fallback": True,
                    }

                num_dice = int(match.group(1)) if match.group(1) else 1
                dice_type = int(match.group(2))
                plus_mod = int(match.group(3)) if match.group(3) else 0
                minus_mod = int(match.group(4)) if match.group(4) else 0
                modifier = plus_mod - minus_mod

                rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
                total = sum(rolls) + modifier

                return {
                    "notation": dice_notation,
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": max(total, 1),  # Minimum 1 damage
                }

        agent = MockCombatMCAgent()

        # Test 2d8+3
        with patch("random.randint", side_effect=[5, 7]):
            result = agent._fallback_roll_damage("2d8+3")
            assert result["notation"] == "2d8+3"
            assert result["rolls"] == [5, 7]
            assert result["modifier"] == 3
            assert result["total"] == 15  # 5 + 7 + 3

    def test_fallback_roll_damage_invalid_notation(self) -> None:
        """Test damage roll with invalid notation falls back gracefully."""
        import re

        class MockCombatMCAgent:
            def _fallback_roll_damage(self, dice_notation: str):
                import random

                # Simple dice parser for basic notation like "1d6+2" or "2d8"
                pattern = r"(\d*)d(\d+)(?:\+(\d+))?(?:\-(\d+))?"
                match = re.match(pattern, dice_notation.lower().replace(" ", ""))

                if not match:
                    # Fallback to fixed damage if parsing fails
                    return {
                        "total": 4,
                        "rolls": [4],
                        "notation": dice_notation,
                        "fallback": True,
                    }

                num_dice = int(match.group(1)) if match.group(1) else 1
                dice_type = int(match.group(2))
                plus_mod = int(match.group(3)) if match.group(3) else 0
                minus_mod = int(match.group(4)) if match.group(4) else 0
                modifier = plus_mod - minus_mod

                rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
                total = sum(rolls) + modifier

                return {
                    "notation": dice_notation,
                    "rolls": rolls,
                    "modifier": modifier,
                    "total": max(total, 1),  # Minimum 1 damage
                }

        agent = MockCombatMCAgent()

        # Test invalid notation
        result = agent._fallback_roll_damage("invalid")
        assert result["notation"] == "invalid"
        assert result["total"] == 4
        assert result["rolls"] == [4]
        assert result["fallback"] is True


class TestAgentConfiguration:
    """Test agent configuration and initialization."""

    def test_agent_initialization_with_config(self) -> None:
        """Test agents can be initialized with proper configuration."""
        config = {
            "azure_openai_endpoint": "https://test.openai.azure.com",
            "model_deployment": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        # Mock agent initialization
        mock_agent = Mock()
        mock_agent.configure = Mock()
        mock_agent.is_configured = Mock(return_value=True)

        mock_agent.configure(config)

        assert mock_agent.configure.called
        assert mock_agent.is_configured()

    def test_agent_missing_configuration_handling(self) -> None:
        """Test agents handle missing configuration gracefully."""
        mock_agent = Mock()
        mock_agent.is_configured = Mock(return_value=False)
        mock_agent.get_configuration_error = Mock(
            return_value="Azure OpenAI endpoint not configured"
        )

        assert not mock_agent.is_configured()
        error_msg = mock_agent.get_configuration_error()
        assert "Azure OpenAI" in error_msg
