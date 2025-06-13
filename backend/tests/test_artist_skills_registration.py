"""
Test for Artist Agent skills registration functionality.
"""
import pytest
import os
from unittest.mock import Mock, patch


class TestArtistAgentSkillsRegistration:
    """Test class for Artist Agent skills registration."""

    def test_artist_agent_skills_registration(self):
        """Test that ArtistAgent properly registers all required skills."""
        
        # Set up environment variables to avoid config validation errors
        test_env = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_CHAT_DEPLOYMENT': 'test-chat',
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': 'test-embedding',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }
        
        with patch.dict(os.environ, test_env), \
             patch.dict('sys.modules', {
                'semantic_kernel': Mock(),
                'semantic_kernel.functions': Mock(),
                'semantic_kernel.connectors': Mock(),
                'semantic_kernel.connectors.ai': Mock(),
                'semantic_kernel.connectors.ai.open_ai': Mock(),
             }):
            
            # Create a mock kernel with detailed tracking
            mock_kernel = Mock()
            add_plugin_mock = Mock()
            mock_kernel.add_plugin = add_plugin_mock
            
            with patch('app.kernel_setup.kernel_manager') as mock_manager, \
                 patch('app.azure_openai_client.AzureOpenAIClient'):
                
                mock_manager.create_kernel.return_value = mock_kernel
                
                # Import and create ArtistAgent
                from app.agents.artist_agent import ArtistAgent
                artist = ArtistAgent()
                
                # Verify all 5 required skills plugins were registered
                assert add_plugin_mock.call_count == 5, f"Expected 5 plugin registrations, got {add_plugin_mock.call_count}"
                
                # Check that all required skills are registered
                plugin_names = [call[0][1] for call in add_plugin_mock.call_args_list]
                expected_plugins = [
                    'ImageGeneration',
                    'ArtStyleAnalysis', 
                    'VisualConsistency',
                    'CharacterVisualization',
                    'SceneComposition'
                ]
                
                for expected_plugin in expected_plugins:
                    assert expected_plugin in plugin_names, f"Plugin {expected_plugin} not registered"
                
                # Verify the artist has direct access to all plugin instances
                assert hasattr(artist, 'image_generation'), "Missing image_generation plugin reference"
                assert hasattr(artist, 'art_style_analysis'), "Missing art_style_analysis plugin reference"
                assert hasattr(artist, 'visual_consistency'), "Missing visual_consistency plugin reference"
                assert hasattr(artist, 'character_visualization'), "Missing character_visualization plugin reference"
                assert hasattr(artist, 'scene_composition'), "Missing scene_composition plugin reference"

    def test_artist_skills_plugin_types(self):
        """Test that the registered plugins are of the correct types."""
        
        # Set up environment variables to avoid config validation errors
        test_env = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_CHAT_DEPLOYMENT': 'test-chat',
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': 'test-embedding',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }
        
        with patch.dict(os.environ, test_env), \
             patch.dict('sys.modules', {
                'semantic_kernel': Mock(),
                'semantic_kernel.functions': Mock(),
                'semantic_kernel.connectors': Mock(),
                'semantic_kernel.connectors.ai': Mock(),
                'semantic_kernel.connectors.ai.open_ai': Mock(),
             }):
            
            mock_kernel = Mock()
            mock_kernel.add_plugin = Mock()
            
            with patch('app.kernel_setup.kernel_manager') as mock_manager, \
                 patch('app.azure_openai_client.AzureOpenAIClient'):
                
                mock_manager.create_kernel.return_value = mock_kernel
                
                from app.agents.artist_agent import ArtistAgent
                from app.plugins.image_generation_plugin import ImageGenerationPlugin
                from app.plugins.art_style_analysis_plugin import ArtStyleAnalysisPlugin
                from app.plugins.visual_consistency_plugin import VisualConsistencyPlugin
                from app.plugins.character_visualization_plugin import CharacterVisualizationPlugin
                from app.plugins.scene_composition_plugin import SceneCompositionPlugin
                
                artist = ArtistAgent()
                
                # Verify plugin types
                assert isinstance(artist.image_generation, ImageGenerationPlugin)
                assert isinstance(artist.art_style_analysis, ArtStyleAnalysisPlugin)
                assert isinstance(artist.visual_consistency, VisualConsistencyPlugin)
                assert isinstance(artist.character_visualization, CharacterVisualizationPlugin)
                assert isinstance(artist.scene_composition, SceneCompositionPlugin)

    def test_artist_skills_registration_error_handling(self):
        """Test that skills registration handles errors gracefully."""
        
        # Set up environment variables to avoid config validation errors
        test_env = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_CHAT_DEPLOYMENT': 'test-chat',
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': 'test-embedding',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }
        
        with patch.dict(os.environ, test_env), \
             patch.dict('sys.modules', {
                'semantic_kernel': Mock(),
                'semantic_kernel.functions': Mock(),
                'semantic_kernel.connectors': Mock(),
                'semantic_kernel.connectors.ai': Mock(),
                'semantic_kernel.connectors.ai.open_ai': Mock(),
             }):
            
            mock_kernel = Mock()
            # Make add_plugin raise an exception
            mock_kernel.add_plugin.side_effect = Exception("Plugin registration failed")
            
            with patch('app.kernel_setup.kernel_manager') as mock_manager, \
                 patch('app.azure_openai_client.AzureOpenAIClient'):
                
                mock_manager.create_kernel.return_value = mock_kernel
                
                # Import and try to create ArtistAgent
                from app.agents.artist_agent import ArtistAgent
                
                # This should raise an exception since error handling re-raises
                with pytest.raises(Exception, match="Plugin registration failed"):
                    ArtistAgent()