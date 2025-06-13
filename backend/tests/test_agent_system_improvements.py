"""
Tests for agent system improvements, particularly fallback behavior.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestAgentSystemImprovements:
    """Test suite for agent system improvements."""

    @pytest.fixture
    def dm_agent_mock(self):
        """Create a mock Dungeon Master agent instance."""
        with patch('app.agents.dungeon_master_agent.kernel_manager'):
            # Mock the DungeonMasterAgent to avoid Azure dependencies
            from app.agents.dungeon_master_agent import DungeonMasterAgent
            
            agent = DungeonMasterAgent.__new__(DungeonMasterAgent)
            agent.active_sessions = {}
            agent.narrative_memory = MagicMock()
            agent.kernel = MagicMock()
            agent._fallback_mode = False
            
            return agent

    def test_fallback_initialization(self, dm_agent_mock):
        """Test that fallback components are properly initialized."""
        # Trigger fallback initialization
        dm_agent_mock._initialize_fallback_components()
        
        assert hasattr(dm_agent_mock, '_fallback_mode')
        assert dm_agent_mock._fallback_mode is True
        assert hasattr(dm_agent_mock, '_fallback_dice')
        assert hasattr(dm_agent_mock, '_fallback_responses')
        assert hasattr(dm_agent_mock, '_fallback_campaign_templates')
        
        # Check that dice functions are available
        assert 'd4' in dm_agent_mock._fallback_dice
        assert 'd20' in dm_agent_mock._fallback_dice
        assert callable(dm_agent_mock._fallback_dice['d20'])

    def test_fallback_dice_roll(self, dm_agent_mock):
        """Test fallback dice rolling functionality."""
        dm_agent_mock._initialize_fallback_components()
        
        # Test basic dice roll
        result = dm_agent_mock._fallback_dice_roll("1d20")
        assert 'rolls' in result
        assert 'total' in result
        assert 'notation' in result
        assert len(result['rolls']) == 1
        assert 1 <= result['rolls'][0] <= 20
        assert result['total'] == result['rolls'][0]

    def test_fallback_dice_roll_with_modifier(self, dm_agent_mock):
        """Test fallback dice rolling with modifiers."""
        dm_agent_mock._initialize_fallback_components()
        
        # Test dice roll with positive modifier
        result = dm_agent_mock._fallback_dice_roll("1d6+3")
        assert 'modifier' in result
        assert result['modifier'] == 3
        assert result['total'] == result['rolls'][0] + 3
        
        # Test dice roll with negative modifier
        result = dm_agent_mock._fallback_dice_roll("1d6-2")
        assert result['modifier'] == -2
        assert result['total'] == result['rolls'][0] - 2

    def test_fallback_multiple_dice(self, dm_agent_mock):
        """Test fallback rolling multiple dice."""
        dm_agent_mock._initialize_fallback_components()
        
        result = dm_agent_mock._fallback_dice_roll("3d6")
        assert len(result['rolls']) == 3
        assert all(1 <= roll <= 6 for roll in result['rolls'])
        assert result['total'] == sum(result['rolls'])

    def test_fallback_invalid_dice_notation(self, dm_agent_mock):
        """Test fallback handling of invalid dice notation."""
        dm_agent_mock._initialize_fallback_components()
        
        result = dm_agent_mock._fallback_dice_roll("invalid")
        assert 'error' in result
        assert 'Invalid dice notation' in result['error']

    def test_fallback_generate_response(self, dm_agent_mock):
        """Test fallback response generation."""
        dm_agent_mock._initialize_fallback_components()
        
        # Test different contexts
        combat_response = dm_agent_mock._fallback_generate_response("combat")
        assert isinstance(combat_response, str)
        assert len(combat_response) > 0
        
        exploration_response = dm_agent_mock._fallback_generate_response("exploration")
        assert isinstance(exploration_response, str)
        assert len(exploration_response) > 0
        
        default_response = dm_agent_mock._fallback_generate_response("default")
        assert isinstance(default_response, str)
        assert len(default_response) > 0

    @pytest.mark.asyncio
    async def test_fallback_input_processing(self, dm_agent_mock):
        """Test input processing in fallback mode."""
        dm_agent_mock._initialize_fallback_components()
        dm_agent_mock._fallback_mode = True
        
        # Test basic input
        result = await dm_agent_mock._process_input_fallback("I look around", {})
        assert 'message' in result
        assert 'narration' in result
        assert 'state_updates' in result
        assert result.get('fallback_mode') is True

    @pytest.mark.asyncio
    async def test_fallback_dice_input_processing(self, dm_agent_mock):
        """Test dice roll input processing in fallback mode."""
        dm_agent_mock._initialize_fallback_components()
        dm_agent_mock._fallback_mode = True
        
        # Test dice roll input
        result = await dm_agent_mock._process_input_fallback("roll 1d20", {})
        assert 'dice_result' in result
        assert 'message' in result
        assert 'rolls' in result['dice_result']

    @pytest.mark.asyncio
    async def test_fallback_combat_input_processing(self, dm_agent_mock):
        """Test combat input processing in fallback mode."""
        dm_agent_mock._initialize_fallback_components()
        dm_agent_mock._fallback_mode = True
        
        # Test combat input
        result = await dm_agent_mock._process_input_fallback("I attack the orc", {})
        assert 'message' in result
        assert 'attack' in result['message'].lower() or 'attempt' in result['message'].lower()

    def test_handle_fallback_dice_roll_extraction(self, dm_agent_mock):
        """Test extraction of dice notation from user input."""
        dm_agent_mock._initialize_fallback_components()
        
        # Test various input formats
        test_cases = [
            "roll 2d6",
            "I want to roll 1d20+5", 
            "Can you roll 3d8-2 for damage?",
            "roll a d20"
        ]
        
        for test_input in test_cases:
            result = dm_agent_mock._handle_fallback_dice_roll(test_input)
            assert 'rolls' in result
            assert 'total' in result
            assert len(result['rolls']) > 0

    def test_fallback_campaign_templates(self, dm_agent_mock):
        """Test that fallback campaign templates are properly structured."""
        dm_agent_mock._initialize_fallback_components()
        
        templates = dm_agent_mock._fallback_campaign_templates
        assert 'fantasy' in templates
        assert 'modern' in templates
        assert 'sci-fi' in templates
        
        for template_name, template_data in templates.items():
            assert 'setting' in template_data
            assert 'themes' in template_data
            assert 'locations' in template_data
            assert 'npcs' in template_data
            assert isinstance(template_data['themes'], list)
            assert isinstance(template_data['locations'], list)
            assert isinstance(template_data['npcs'], list)

    @pytest.mark.asyncio
    async def test_fallback_error_handling(self, dm_agent_mock):
        """Test error handling in fallback mode."""
        dm_agent_mock._initialize_fallback_components()
        dm_agent_mock._fallback_mode = True
        
        # Test with malformed input that might cause errors
        result = await dm_agent_mock._process_input_fallback("", {})
        assert 'message' in result
        # Should not raise an exception and should provide some response

    def test_dice_roll_bounds_checking(self, dm_agent_mock):
        """Test that dice rolls stay within expected bounds."""
        dm_agent_mock._initialize_fallback_components()
        
        # Test multiple rolls to check bounds
        for _ in range(10):
            result = dm_agent_mock._fallback_dice_roll("1d20")
            assert 1 <= result['rolls'][0] <= 20
            
            result = dm_agent_mock._fallback_dice_roll("2d6")
            assert len(result['rolls']) == 2
            assert all(1 <= roll <= 6 for roll in result['rolls'])
            assert 2 <= result['total'] <= 12

    def test_fallback_mode_detection(self, dm_agent_mock):
        """Test that fallback mode is properly detected."""
        # Initially not in fallback mode
        assert not getattr(dm_agent_mock, '_fallback_mode', False)
        
        # Initialize fallback
        dm_agent_mock._initialize_fallback_components()
        
        # Should now be in fallback mode
        assert dm_agent_mock._fallback_mode is True

    def test_dice_notation_parsing(self, dm_agent_mock):
        """Test parsing of different dice notation formats."""
        dm_agent_mock._initialize_fallback_components()
        
        test_cases = [
            ("1d20", 1, 20, 0),
            ("2d6+3", 2, 6, 3),
            ("3d8-2", 3, 8, -2),
            ("d4", 1, 4, 0),  # Should handle missing count
        ]
        
        for notation, expected_count, expected_size, expected_mod in test_cases:
            result = dm_agent_mock._fallback_dice_roll(notation)
            if 'error' not in result:
                assert len(result['rolls']) == expected_count
                assert all(1 <= roll <= expected_size for roll in result['rolls'])
                assert result['modifier'] == expected_mod