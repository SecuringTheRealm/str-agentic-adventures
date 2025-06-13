"""
Simple test for combat MC agent fallback behavior.
"""
import sys
import os
from unittest.mock import Mock, patch
import asyncio

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_combat_agent_with_mocks():
    """Test combat agent behavior with mocked dependencies."""
    
    # Mock the semantic kernel and related modules
    mock_sk = Mock()
    mock_config = Mock()
    mock_config.settings = Mock()
    mock_config.settings.azure_openai_chat_deployment = "test"
    mock_config.settings.azure_openai_endpoint = "test"
    mock_config.settings.azure_openai_api_key = "test"
    mock_config.settings.azure_openai_api_version = "test"
    mock_config.settings.azure_openai_embedding_deployment = "test"
    
    mock_rules_plugin = Mock()
    mock_rules_plugin.RulesEnginePlugin = Mock()
    
    # Create a mock kernel that will fail when adding plugins
    mock_kernel = Mock()
    mock_kernel.add_plugin = Mock(side_effect=Exception("Plugin registration failed"))
    
    mock_kernel_manager = Mock()
    mock_kernel_manager.create_kernel = Mock(return_value=mock_kernel)
    
    with patch.dict('sys.modules', {
        'semantic_kernel': mock_sk,
        'semantic_kernel.connectors': Mock(),
        'semantic_kernel.connectors.ai': Mock(),
        'semantic_kernel.connectors.ai.open_ai': Mock(),
        'app.config': mock_config,
        'app.plugins.rules_engine_plugin': mock_rules_plugin,
        'app.kernel_setup': Mock(kernel_manager=mock_kernel_manager)
    }):
        # Mock the kernel_manager import in the combat_mc_agent module
        with patch('app.agents.combat_mc_agent.kernel_manager', mock_kernel_manager):
            # Now import and test the combat agent
            from app.agents.combat_mc_agent import CombatMCAgent
            
            print("Testing CombatMCAgent fallback behavior...")
            
            # Create the agent - this should trigger fallback mode
            agent = CombatMCAgent()
            
            # Test that fallback mode is enabled
            assert agent.is_fallback_mode() == True, "Agent should be in fallback mode"
            print("✓ Fallback mode enabled correctly")
            
            # Test capabilities
            capabilities = agent.get_capabilities()
            assert capabilities["mode"] == "fallback", "Mode should be fallback"
            assert "basic_initiative_rolling" in capabilities["capabilities"], "Should have basic capabilities"
            print("✓ Capabilities check passed")
            
            # Test fallback dice rolling
            result = agent._fallback_roll_d20(modifier=3)
            assert "total" in result, "Should have total"
            assert "rolls" in result, "Should have rolls"
            assert result["modifier"] == 3, "Modifier should be preserved"
            assert 4 <= result["total"] <= 23, f"Total should be in range 4-23, got {result['total']}"
            print("✓ Fallback d20 rolling works")
            
            # Test damage rolling
            damage = agent._fallback_roll_damage("2d6+3")
            assert "total" in damage, "Should have damage total"
            assert 5 <= damage["total"] <= 15, f"Damage should be in range 5-15, got {damage['total']}"
            print("✓ Fallback damage rolling works")
            
            # Test encounter creation
            party_info = {
                "members": [
                    {"id": "player1", "level": 2, "name": "Fighter"}
                ]
            }
            narrative_context = {"location": "forest"}
            
            async def test_async_functions():
                encounter = await agent.create_encounter(party_info, narrative_context)
                assert "id" in encounter, "Encounter should have ID"
                assert "enemies" in encounter, "Encounter should have enemies"
                assert encounter["status"] == "ready", "Encounter should be ready"
                print("✓ Encounter creation works in fallback mode")
                
                # Test combat start
                party_members = [
                    {"id": "player1", "name": "Fighter", "abilities": {"dexterity": 14}}
                ]
                
                combat_state = await agent.start_combat(encounter["id"], party_members)
                assert "turn_order" in combat_state, "Should have turn order"
                assert combat_state["status"] == "active", "Combat should be active"
                print("✓ Combat initialization works in fallback mode")
                
                # Test combat action processing
                action_data = {
                    "type": "attack",
                    "actor_id": "player1",
                    "target_id": "enemy_1",
                    "attack_bonus": 5,
                    "target_ac": 12,
                    "damage": "1d8+3"
                }
                
                action_result = await agent.process_combat_action(encounter["id"], action_data)
                assert "success" in action_result, "Action should have success indicator"
                assert "message" in action_result, "Action should have message"
                print("✓ Combat action processing works in fallback mode")
            
            # Run async tests
            asyncio.run(test_async_functions())
            
            print("\nAll tests passed! Combat MC agent fallback behavior is working correctly.")
            return True

def test_normal_mode():
    """Test that normal mode works when plugins load successfully."""
    
    # Mock successful plugin registration
    mock_sk = Mock()
    mock_config = Mock()
    mock_config.settings = Mock()
    mock_config.settings.azure_openai_chat_deployment = "test"
    mock_config.settings.azure_openai_endpoint = "test"
    mock_config.settings.azure_openai_api_key = "test"
    mock_config.settings.azure_openai_api_version = "test"
    mock_config.settings.azure_openai_embedding_deployment = "test"
    
    mock_rules_plugin = Mock()
    mock_rules_plugin.RulesEnginePlugin = Mock()
    
    # Create a mock kernel that succeeds when adding plugins
    mock_kernel = Mock()
    mock_kernel.add_plugin = Mock()  # No exception = success
    
    mock_kernel_manager = Mock()
    mock_kernel_manager.create_kernel = Mock(return_value=mock_kernel)
    
    with patch.dict('sys.modules', {
        'semantic_kernel': mock_sk,
        'semantic_kernel.connectors': Mock(),
        'semantic_kernel.connectors.ai': Mock(),
        'semantic_kernel.connectors.ai.open_ai': Mock(),
        'app.config': mock_config,
        'app.plugins.rules_engine_plugin': mock_rules_plugin,
        'app.kernel_setup': Mock(kernel_manager=mock_kernel_manager)
    }):
        with patch('app.agents.combat_mc_agent.kernel_manager', mock_kernel_manager):
            from app.agents.combat_mc_agent import CombatMCAgent
            
            print("\nTesting CombatMCAgent normal mode...")
            
            # Create the agent - should work in normal mode
            agent = CombatMCAgent()
            
            # Test that normal mode is enabled
            assert agent.is_fallback_mode() == False, "Agent should NOT be in fallback mode"
            print("✓ Normal mode enabled correctly")
            
            # Test capabilities
            capabilities = agent.get_capabilities()
            assert capabilities["mode"] == "full", "Mode should be full"
            assert "advanced_dice_rolling" in capabilities["capabilities"], "Should have advanced capabilities"
            assert capabilities["limitations"] == [], "Should have no limitations"
            print("✓ Full capabilities available")
            
            print("Normal mode test passed!")
            return True

if __name__ == "__main__":
    try:
        test_combat_agent_with_mocks()
        test_normal_mode()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)