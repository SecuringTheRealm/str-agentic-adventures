"""
Test for Combat Cartographer Agent skills registration functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch


class TestCombatCartographerAgentSkillsRegistration:
    """Test class for Combat Cartographer Agent skills registration."""

    def test_combat_cartographer_agent_skills_registration(self):
        """Test that CombatCartographerAgent properly registers all required skills."""

        # Set up environment variables to avoid config validation errors
        test_env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "test-chat",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "test-embedding",
            "AZURE_OPENAI_API_VERSION": "2023-05-15",
        }

        with (
            patch.dict(os.environ, test_env),
            patch.dict(
                "sys.modules",
                {
                    "semantic_kernel": Mock(),
                    "semantic_kernel.functions": Mock(),
                    "semantic_kernel.connectors": Mock(),
                    "semantic_kernel.connectors.ai": Mock(),
                    "semantic_kernel.connectors.ai.open_ai": Mock(),
                },
            ),
        ):
            # Create a mock kernel with detailed tracking
            mock_kernel = Mock()
            add_plugin_mock = Mock()
            mock_kernel.add_plugin = add_plugin_mock

            with (
                patch("app.kernel_setup.kernel_manager") as mock_manager,
                patch("app.azure_openai_client.AzureOpenAIClient"),
            ):
                mock_manager.create_kernel.return_value = mock_kernel

                # Import and create CombatCartographerAgent
                from app.agents.combat_cartographer_agent import CombatCartographerAgent

                cartographer = CombatCartographerAgent()

                # Verify all 5 required skills plugins were registered
                assert add_plugin_mock.call_count == 5, (
                    f"Expected 5 plugin registrations, got {add_plugin_mock.call_count}"
                )

                # Check that all required skills are registered
                plugin_names = [call[0][1] for call in add_plugin_mock.call_args_list]
                expected_plugins = [
                    "MapGeneration",
                    "TacticalAnalysis",
                    "TerrainAssessment",
                    "BattlePositioning",
                    "EnvironmentalHazards",
                ]

                for expected_plugin in expected_plugins:
                    assert expected_plugin in plugin_names, (
                        f"Plugin {expected_plugin} not registered"
                    )

                # Verify the cartographer has direct access to all plugin instances
                assert hasattr(cartographer, "map_generation"), (
                    "Missing map_generation plugin reference"
                )
                assert hasattr(cartographer, "tactical_analysis"), (
                    "Missing tactical_analysis plugin reference"
                )
                assert hasattr(cartographer, "terrain_assessment"), (
                    "Missing terrain_assessment plugin reference"
                )
                assert hasattr(cartographer, "battle_positioning"), (
                    "Missing battle_positioning plugin reference"
                )
                assert hasattr(cartographer, "environmental_hazards"), (
                    "Missing environmental_hazards plugin reference"
                )

    def test_combat_cartographer_skills_plugin_types(self):
        """Test that the registered plugins are of the correct types."""

        # Set up environment variables to avoid config validation errors
        test_env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "test-chat",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "test-embedding",
            "AZURE_OPENAI_API_VERSION": "2023-05-15",
        }

        with (
            patch.dict(os.environ, test_env),
            patch.dict(
                "sys.modules",
                {
                    "semantic_kernel": Mock(),
                    "semantic_kernel.functions": Mock(),
                    "semantic_kernel.connectors": Mock(),
                    "semantic_kernel.connectors.ai": Mock(),
                    "semantic_kernel.connectors.ai.open_ai": Mock(),
                },
            ),
        ):
            mock_kernel = Mock()
            mock_kernel.add_plugin = Mock()

            with (
                patch("app.kernel_setup.kernel_manager") as mock_manager,
                patch("app.azure_openai_client.AzureOpenAIClient"),
            ):
                mock_manager.create_kernel.return_value = mock_kernel

                from app.agents.combat_cartographer_agent import CombatCartographerAgent
                from app.plugins.map_generation_plugin import MapGenerationPlugin
                from app.plugins.tactical_analysis_plugin import TacticalAnalysisPlugin
                from app.plugins.terrain_assessment_plugin import (
                    TerrainAssessmentPlugin,
                )
                from app.plugins.battle_positioning_plugin import (
                    BattlePositioningPlugin,
                )
                from app.plugins.environmental_hazards_plugin import (
                    EnvironmentalHazardsPlugin,
                )

                cartographer = CombatCartographerAgent()

                # Verify plugin types
                assert isinstance(cartographer.map_generation, MapGenerationPlugin)
                assert isinstance(
                    cartographer.tactical_analysis, TacticalAnalysisPlugin
                )
                assert isinstance(
                    cartographer.terrain_assessment, TerrainAssessmentPlugin
                )
                assert isinstance(
                    cartographer.battle_positioning, BattlePositioningPlugin
                )
                assert isinstance(
                    cartographer.environmental_hazards, EnvironmentalHazardsPlugin
                )

    def test_combat_cartographer_skills_registration_error_handling(self):
        """Test that skills registration handles errors gracefully."""

        # Set up environment variables to avoid config validation errors
        test_env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "test-chat",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "test-embedding",
            "AZURE_OPENAI_API_VERSION": "2023-05-15",
        }

        with (
            patch.dict(os.environ, test_env),
            patch.dict(
                "sys.modules",
                {
                    "semantic_kernel": Mock(),
                    "semantic_kernel.functions": Mock(),
                    "semantic_kernel.connectors": Mock(),
                    "semantic_kernel.connectors.ai": Mock(),
                    "semantic_kernel.connectors.ai.open_ai": Mock(),
                },
            ),
        ):
            mock_kernel = Mock()
            # Make add_plugin raise an exception
            mock_kernel.add_plugin.side_effect = Exception("Plugin registration failed")

            with (
                patch("app.kernel_setup.kernel_manager") as mock_manager,
                patch("app.azure_openai_client.AzureOpenAIClient"),
            ):
                mock_manager.create_kernel.return_value = mock_kernel

                # Import and try to create CombatCartographerAgent
                from app.agents.combat_cartographer_agent import CombatCartographerAgent

                # This should raise an exception since error handling re-raises
                with pytest.raises(Exception, match="Plugin registration failed"):
                    CombatCartographerAgent()

    def test_combat_cartographer_plugin_functions_exist(self):
        """Test that all required plugin functions exist and are properly decorated."""

        # Test MapGenerationPlugin
        from app.plugins.map_generation_plugin import MapGenerationPlugin

        map_plugin = MapGenerationPlugin()

        # Check that kernel functions exist
        assert hasattr(map_plugin, "generate_tactical_map")
        assert hasattr(map_plugin, "create_grid_system")

        # Test TacticalAnalysisPlugin
        from app.plugins.tactical_analysis_plugin import TacticalAnalysisPlugin

        tactical_plugin = TacticalAnalysisPlugin()

        assert hasattr(tactical_plugin, "analyze_tactical_positions")
        assert hasattr(tactical_plugin, "assess_combat_threats")
        assert hasattr(tactical_plugin, "calculate_optimal_positioning")

        # Test TerrainAssessmentPlugin
        from app.plugins.terrain_assessment_plugin import TerrainAssessmentPlugin

        terrain_plugin = TerrainAssessmentPlugin()

        assert hasattr(terrain_plugin, "assess_terrain_features")
        assert hasattr(terrain_plugin, "analyze_movement_costs")
        assert hasattr(terrain_plugin, "evaluate_defensive_terrain")

        # Test BattlePositioningPlugin
        from app.plugins.battle_positioning_plugin import BattlePositioningPlugin

        positioning_plugin = BattlePositioningPlugin()

        assert hasattr(positioning_plugin, "calculate_starting_positions")
        assert hasattr(positioning_plugin, "recommend_formation_adjustments")
        assert hasattr(positioning_plugin, "optimize_unit_spacing")

        # Test EnvironmentalHazardsPlugin
        from app.plugins.environmental_hazards_plugin import EnvironmentalHazardsPlugin

        hazards_plugin = EnvironmentalHazardsPlugin()

        assert hasattr(hazards_plugin, "identify_environmental_hazards")
        assert hasattr(hazards_plugin, "provide_hazard_mitigation")
        assert hasattr(hazards_plugin, "monitor_dynamic_hazards")
