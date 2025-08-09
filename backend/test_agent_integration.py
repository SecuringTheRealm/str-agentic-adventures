"""
Integration test for CombatMCAgent with mocked Azure dependencies.
This tests the actual agent implementation without requiring Azure OpenAI configuration.
"""

import asyncio
import os
from unittest.mock import Mock, patch

from app.agents.combat_mc_agent import CombatMCAgent
from app.plugins.rules_engine_plugin import RulesEnginePlugin


async def test_agent_integration() -> None:
    """Test that the CombatMCAgent can be created and used with mocked Azure dependencies."""

    # Mock the Azure OpenAI configuration
    with patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "test-chat",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "test-embedding",
        },
    ):
        # Mock the kernel creation to avoid actual Azure calls
        with patch(
            "app.kernel_setup.kernel_manager.create_kernel"
        ) as mock_kernel_manager:
            mock_kernel = Mock()
            mock_kernel.plugins = {"Rules": RulesEnginePlugin()}
            mock_kernel_manager.return_value = mock_kernel

            # Create the agent
            agent = CombatMCAgent()

            # Verify it's not in fallback mode (plugins are working)
            assert not agent.is_fallback_mode()

            # Create a test encounter
            party_info = {
                "members": [
                    {"level": 3, "class": "fighter"},
                    {"level": 3, "class": "wizard"},
                ]
            }
            narrative_context = {"location": "forest"}

            encounter = await agent.create_encounter(party_info, narrative_context)

            # Verify encounter was created
            assert "id" in encounter
            assert encounter["status"] == "ready"
            assert len(encounter["enemies"]) > 0

            # Start combat
            party_members = [
                {"id": "player1", "name": "Fighter", "abilities": {"dexterity": 14}},
                {"id": "player2", "name": "Wizard", "abilities": {"dexterity": 12}},
            ]

            combat_result = await agent.start_combat(encounter["id"], party_members)

            # Verify combat was started
            assert combat_result["status"] == "active"
            assert combat_result["round"] == 1
            assert len(combat_result["turn_order"]) > 0

            # Test plugin-based attack action
            attack_action = {
                "type": "attack",
                "actor_id": "player1",
                "target_id": "enemy_1",
                "attack_bonus": 5,
                "target_ac": 12,
                "damage": "1d8+3",
            }

            action_result = await agent.process_combat_action(
                encounter["id"], attack_action
            )

            # Verify action was processed using plugins
            assert action_result["action_type"] == "attack"
            assert "success" in action_result
            assert "attack_roll" in action_result

            # Test spell attack action
            spell_attack = {
                "type": "spell_attack",
                "actor_id": "player2",
                "target_id": "enemy_1",
                "spellcasting_modifier": 3,
                "proficiency_bonus": 2,
                "target_ac": 12,
                "damage": "1d10",
                "damage_type": "fire",
            }

            spell_result = await agent.process_combat_action(
                encounter["id"], spell_attack
            )

            # Verify spell attack was processed
            assert spell_result["action_type"] == "spell_attack"
            assert "spell_attack_bonus" in spell_result

            print("✓ Agent integration test passed!")
            print(f"✓ Encounter created: {encounter['id']}")
            print(
                f"✓ Combat started with {len(combat_result['turn_order'])} participants"
            )
            print(f"✓ Attack result: {action_result['message']}")
            print(f"✓ Spell attack result: {spell_result['message']}")


if __name__ == "__main__":
    asyncio.run(test_agent_integration())
