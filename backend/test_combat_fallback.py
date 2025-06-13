"""
Test combat MC agent fallback behavior when plugin registration fails.
"""
import sys
from unittest.mock import Mock, patch, MagicMock
import asyncio


def test_combat_mc_fallback_mode():
    """Test that combat MC agent works in fallback mode when plugin registration fails."""
    
    # Mock all dependencies
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        # Mock kernel manager to simulate plugin registration failure
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin registration failed"))
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            # Import after mocking
            from app.agents.combat_mc_agent import CombatMCAgent
            
            # Create agent - should trigger fallback mode
            agent = CombatMCAgent()
            
            # Verify fallback mode is enabled
            assert agent.is_fallback_mode() == True
            
            # Test capabilities in fallback mode
            capabilities = agent.get_capabilities()
            assert capabilities["mode"] == "fallback"
            assert "basic_initiative_rolling" in capabilities["capabilities"]
            assert "no_advanced_spell_effects" in capabilities["limitations"]


def test_combat_mc_normal_mode():
    """Test that combat MC agent works in normal mode when plugin registration succeeds."""
    
    # Mock all dependencies
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        # Mock successful plugin registration
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock()  # No exception - success
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            # Import after mocking
            from app.agents.combat_mc_agent import CombatMCAgent
            
            # Create agent - should work normally
            agent = CombatMCAgent()
            
            # Verify normal mode
            assert agent.is_fallback_mode() == False
            
            # Test capabilities in normal mode
            capabilities = agent.get_capabilities()
            assert capabilities["mode"] == "full"
            assert "advanced_dice_rolling" in capabilities["capabilities"]
            assert capabilities["limitations"] == []


def test_fallback_dice_rolling():
    """Test fallback dice rolling mechanics."""
    
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin failed"))
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            from app.agents.combat_mc_agent import CombatMCAgent
            
            agent = CombatMCAgent()
            
            # Test d20 roll
            result = agent._fallback_roll_d20(modifier=3)
            assert "rolls" in result
            assert "total" in result
            assert "modifier" in result
            assert result["modifier"] == 3
            assert 4 <= result["total"] <= 23  # 1d20+3 range
            
            # Test advantage
            result = agent._fallback_roll_d20(modifier=0, advantage=True)
            assert result["advantage_type"] == "advantage"
            assert len(result["rolls"]) == 2
            
            # Test disadvantage  
            result = agent._fallback_roll_d20(modifier=0, disadvantage=True)
            assert result["advantage_type"] == "disadvantage"
            assert len(result["rolls"]) == 2
            
            # Test damage roll
            damage_result = agent._fallback_roll_damage("1d6+2")
            assert "total" in damage_result
            assert "rolls" in damage_result
            assert "modifier" in damage_result
            assert 3 <= damage_result["total"] <= 8  # 1d6+2 range


def test_fallback_combat_action():
    """Test fallback combat action processing."""
    
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin failed"))
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            from app.agents.combat_mc_agent import CombatMCAgent
            
            agent = CombatMCAgent()
            
            # Create a test encounter
            encounter = {
                "id": "test_encounter",
                "status": "active",
                "round": 1,
                "turn_order": []
            }
            
            # Test attack action
            action_data = {
                "type": "attack",
                "actor_id": "player1",
                "target_id": "enemy1", 
                "attack_bonus": 5,
                "target_ac": 15,
                "damage": "1d8+3"
            }
            
            result = agent._process_fallback_combat_action(encounter, action_data)
            
            assert "success" in result
            assert "message" in result
            assert "attack_roll" in result
            assert result["action_type"] == "attack"
            
            if result["success"]:
                assert "damage" in result
                assert result["damage"] > 0
            
            # Test skill check action
            skill_action = {
                "type": "skill_check",
                "actor_id": "player1",
                "modifier": 3,
                "dc": 15
            }
            
            skill_result = agent._process_fallback_combat_action(encounter, skill_action)
            assert skill_result["action_type"] == "skill_check"
            assert "roll" in skill_result
            assert "success" in skill_result


async def test_encounter_creation_fallback():
    """Test encounter creation works in fallback mode."""
    
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin failed"))
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            from app.agents.combat_mc_agent import CombatMCAgent
            
            agent = CombatMCAgent()
            
            # Test encounter creation
            party_info = {
                "members": [
                    {"id": "player1", "level": 3, "name": "Fighter"},
                    {"id": "player2", "level": 3, "name": "Wizard"}
                ]
            }
            
            narrative_context = {
                "location": "forest",
                "setting": "dark woods"
            }
            
            encounter = await agent.create_encounter(party_info, narrative_context)
            
            assert "id" in encounter
            assert "enemies" in encounter
            assert "status" in encounter
            assert encounter["status"] == "ready"
            assert len(encounter["enemies"]) > 0


async def test_initiative_rolling_fallback():
    """Test initiative rolling works in fallback mode."""
    
    with patch.dict('sys.modules', {
        'semantic_kernel': Mock(),
        'app.config': Mock(),
        'app.plugins.rules_engine_plugin': Mock(),
    }):
        mock_kernel = Mock()
        mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin failed"))
        
        with patch('app.agents.combat_mc_agent.kernel_manager') as mock_manager:
            mock_manager.create_kernel.return_value = mock_kernel
            
            from app.agents.combat_mc_agent import CombatMCAgent
            
            agent = CombatMCAgent()
            
            # Create encounter first
            party_info = {"members": [{"id": "player1", "level": 2}]}
            encounter = await agent.create_encounter(party_info, {"location": "dungeon"})
            encounter_id = encounter["id"]
            
            # Test starting combat
            party_members = [
                {
                    "id": "player1",
                    "name": "Test Fighter",
                    "abilities": {"dexterity": 14}  # +2 modifier
                }
            ]
            
            combat_state = await agent.start_combat(encounter_id, party_members)
            
            assert "turn_order" in combat_state
            assert len(combat_state["turn_order"]) > 0
            assert combat_state["status"] == "active"
            
            # Check that initiative was rolled
            for participant in combat_state["turn_order"]:
                assert "initiative" in participant
                assert participant["initiative"] > 0


if __name__ == "__main__":
    # Run the tests
    test_combat_mc_fallback_mode()
    test_combat_mc_normal_mode()
    test_fallback_dice_rolling()
    test_fallback_combat_action()
    
    # Run async tests
    asyncio.run(test_encounter_creation_fallback())
    asyncio.run(test_initiative_rolling_fallback())
    
    print("All tests passed!")