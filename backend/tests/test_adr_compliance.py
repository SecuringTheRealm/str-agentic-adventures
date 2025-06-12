"""
Tests to validate ADR compliance and implementation status.
"""
import pytest
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestADRCompliance:
    """Test ADR implementation compliance."""

    def test_adr_0001_semantic_kernel_implementation(self):
        """Test that ADR 0001 (Semantic Kernel) is implemented."""
        # Test that kernel setup exists
        assert Path("app/kernel_setup.py").exists(), "Semantic Kernel setup file should exist"
        
        # Test that the file contains actual implementation
        with open("app/kernel_setup.py", "r") as f:
            content = f.read()
            assert "KernelManager" in content, "KernelManager class should be implemented"
            assert "create_kernel" in content, "create_kernel method should be implemented"
            assert "AzureChatCompletion" in content, "Azure OpenAI integration should be present"
            assert "AzureTextEmbedding" in content, "Azure embedding service should be present"

    def test_adr_0002_multi_agent_architecture(self):
        """Test that ADR 0002 (Multi-Agent Architecture) is implemented."""
        # Test that all required agents exist
        agents_path = Path("app/agents")
        assert agents_path.exists(), "Agents directory should exist"
        
        required_agents = [
            "dungeon_master_agent.py",
            "narrator_agent.py", 
            "scribe_agent.py",
            "combat_mc_agent.py",
            "combat_cartographer_agent.py",
            "artist_agent.py"
        ]
        
        for agent_file in required_agents:
            agent_path = agents_path / agent_file
            assert agent_path.exists(), f"Agent {agent_file} should exist"
            
            # Test that each agent has actual implementation
            with open(agent_path, "r") as f:
                content = f.read()
                assert "class " in content, f"Agent {agent_file} should contain a class definition"
                assert "kernel_manager" in content or "KernelManager" in content, f"Agent {agent_file} should use Semantic Kernel"

    def test_adr_0003_data_storage_implementation(self):
        """Test that ADR 0003 (Data Storage Strategy) is implemented."""
        # Test that database setup exists
        assert Path("app/database.py").exists(), "Database setup file should exist"
        
        # Test database configuration
        with open("app/database.py", "r") as f:
            content = f.read()
            assert "SQLAlchemy" in content or "sqlalchemy" in content, "SQLAlchemy should be configured"
            assert "SessionLocal" in content, "Database session management should be implemented"
            assert "get_session" in content, "Session factory should be implemented"
            
        # Test that models exist
        assert Path("app/models/db_models.py").exists(), "Database models should exist"
        
        with open("app/models/db_models.py", "r") as f:
            content = f.read()
            assert "class Character" in content, "Character model should be implemented"
            assert "Base" in content, "SQLAlchemy Base should be used"

    def test_adr_0004_frontend_architecture(self):
        """Test that ADR 0004 (React TypeScript Frontend) is implemented."""
        frontend_path = Path("../frontend")
        
        # Test that frontend directory exists
        assert frontend_path.exists(), "Frontend directory should exist"
        
        # Test package.json for React and TypeScript
        package_json = frontend_path / "package.json"
        assert package_json.exists(), "Frontend package.json should exist"
        
        # Test TypeScript configuration
        tsconfig = frontend_path / "tsconfig.json"
        assert tsconfig.exists(), "TypeScript configuration should exist"
        
        # Test that src directory exists
        src_path = frontend_path / "src"
        assert src_path.exists(), "Frontend src directory should exist"
        
        # Test that components exist
        components_path = src_path / "components"
        assert components_path.exists(), "Components directory should exist"

    def test_adr_0005_azure_openai_integration(self):
        """Test that ADR 0005 (Azure OpenAI Integration) is implemented."""
        # Test that Azure OpenAI client exists
        assert Path("app/azure_openai_client.py").exists(), "Azure OpenAI client should exist"
        
        # Test client implementation
        with open("app/azure_openai_client.py", "r") as f:
            content = f.read()
            assert "class AzureOpenAIClient" in content, "AzureOpenAIClient class should be implemented"
            assert "chat_completion" in content, "Chat completion method should be implemented"
            assert "azure" in content.lower(), "Azure-specific configuration should be present"
            
        # Test configuration exists
        assert Path("app/config.py").exists(), "Configuration file should exist"
        
        with open("app/config.py", "r") as f:
            content = f.read()
            assert "azure_openai" in content.lower(), "Azure OpenAI configuration should be present"
            assert "AZURE_OPENAI_ENDPOINT" in content, "Azure OpenAI endpoint configuration should exist"

    def test_adr_0006_character_progression_exists(self):
        """Test that ADR 0006 (D&D 5e Character Progression) exists."""
        adr_path = Path("../docs/adr/0006-dnd-5e-character-progression-system.md")
        assert adr_path.exists(), "ADR 0006 file should exist"
        
        with open(adr_path, "r") as f:
            content = f.read()
            assert "Character Progression" in content, "ADR should be about character progression"
            assert "status: accepted" in content.lower(), "ADR should be accepted"

    def test_agent_database_integration(self):
        """Test that agents are integrated with persistent storage."""
        # Test ScribeAgent uses database
        scribe_path = Path("app/agents/scribe_agent.py")
        assert scribe_path.exists(), "ScribeAgent should exist"
        
        with open(scribe_path, "r") as f:
            content = f.read()
            assert "get_session" in content, "ScribeAgent should use database sessions"
            assert "Character" in content, "ScribeAgent should use Character model"
            assert "db.add" in content or "db.query" in content, "ScribeAgent should perform database operations"

    def test_comprehensive_adr_coverage(self):
        """Test that all ADRs have corresponding implementations."""
        adr_directory = Path("../docs/adr")
        assert adr_directory.exists(), "ADR directory should exist"
        
        # Count ADR files (excluding template and index)
        adr_files = list(adr_directory.glob("0*.md"))
        adr_files = [f for f in adr_files if not f.name.startswith("template")]
        
        # Should have at least 6 ADRs (0001-0006)
        assert len(adr_files) >= 6, "Should have at least 6 ADRs implemented"
        
        # Verify ADR index is updated
        index_path = adr_directory / "index.md"
        assert index_path.exists(), "ADR index should exist"
        
        with open(index_path, "r") as f:
            content = f.read()
            assert "0006" in content, "ADR index should reference ADR 0006"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])