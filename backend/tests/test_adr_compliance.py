"""
Tests to validate ADR compliance and implementation status.

All paths are resolved relative to the project root so these tests
pass regardless of the working directory used to invoke pytest
(e.g. ``cd backend && uv run pytest tests/``).
"""

import os
import pathlib
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project root is two levels up from this file (tests/ -> backend/ -> project root)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


class TestADRCompliance:
    """Test ADR implementation compliance."""

    def test_adr_0001_semantic_kernel_superseded_by_0018(self) -> None:
        """Test that ADR 0001 (Agent Framework) has been superseded by ADR 0018."""
        # ADR 0001 should now be superseded
        adr_0001 = PROJECT_ROOT / "docs" / "adr" / "0001-semantic-kernel-multi-agent-framework.md"
        assert adr_0001.exists(), "ADR 0001 should still exist for historical reference"

        content = adr_0001.read_text()
        assert "superseded" in content.lower(), (
            "ADR 0001 should be marked as superseded"
        )
        assert "0018" in content, (
            "ADR 0001 should reference ADR 0018"
        )

    def test_adr_0018_azure_ai_agents_implementation(self) -> None:
        """Test that ADR 0018 (Azure AI Agents SDK) is implemented."""
        # Test that agent client setup exists
        agent_client_path = PROJECT_ROOT / "backend" / "app" / "agent_client_setup.py"
        assert agent_client_path.exists(), (
            "Azure AI Agent client setup file should exist"
        )

        # Test that the file contains actual implementation
        content = agent_client_path.read_text()
        assert "AgentClientManager" in content, (
            "AgentClientManager class should be implemented"
        )
        assert "get_chat_client" in content, (
            "get_chat_client method should be implemented"
        )
        assert "ChatCompletionsClient" in content, (
            "Azure AI Inference integration should be present"
        )
        assert "OpenTelemetry" in content or "opentelemetry" in content, (
            "OpenTelemetry observability should be present"
        )

    def test_adr_0002_multi_agent_architecture(self) -> None:
        """Test that ADR 0002 (Multi-Agent Architecture) is implemented."""
        # Test that all required agents exist
        agents_path = PROJECT_ROOT / "backend" / "app" / "agents"
        assert agents_path.exists(), "Agents directory should exist"

        required_agents = [
            "dungeon_master_agent.py",
            "narrator_agent.py",
            "scribe_agent.py",
            "combat_mc_agent.py",
            "combat_cartographer_agent.py",
            "artist_agent.py",
        ]

        for agent_file in required_agents:
            agent_path = agents_path / agent_file
            assert agent_path.exists(), f"Agent {agent_file} should exist"

            # Test that each agent has actual implementation
            content = agent_path.read_text()
            assert "class " in content, (
                f"Agent {agent_file} should contain a class definition"
            )
            assert (
                "agent_client_manager" in content
                or "AgentClientManager" in content
                or "ChatCompletionsClient" in content
                or "openai_client" in content
                or "BaseAgent" in content
            ), f"Agent {agent_file} should integrate with Azure AI SDK or OpenAI"

    def test_adr_0003_data_storage_implementation(self) -> None:
        """Test that ADR 0003 (Data Storage Strategy) is implemented."""
        # Test that database setup exists
        db_path = PROJECT_ROOT / "backend" / "app" / "database.py"
        assert db_path.exists(), (
            "Database setup file should exist"
        )

        # Test database configuration
        content = db_path.read_text()
        assert "SQLAlchemy" in content or "sqlalchemy" in content, (
            "SQLAlchemy should be configured"
        )
        assert "SessionLocal" in content, (
            "Database session management should be implemented"
        )
        assert "get_session" in content, "Session factory should be implemented"

        # Test that models exist
        models_path = PROJECT_ROOT / "backend" / "app" / "models" / "db_models.py"
        assert models_path.exists(), (
            "Database models should exist"
        )

        content = models_path.read_text()
        assert "class Character" in content, "Character model should be implemented"
        assert "Base" in content, "SQLAlchemy Base should be used"

    def test_adr_0004_frontend_architecture(self) -> None:
        """Test that ADR 0004 (React TypeScript Frontend) is implemented."""
        frontend_path = PROJECT_ROOT / "frontend"

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

    def test_adr_0005_azure_openai_integration(self) -> None:
        """Test that ADR 0005 (Azure OpenAI Integration) is implemented."""
        # Test that Azure OpenAI client exists
        client_path = PROJECT_ROOT / "backend" / "app" / "azure_openai_client.py"
        assert client_path.exists(), (
            "Azure OpenAI client should exist"
        )

        # Test client implementation
        content = client_path.read_text()
        assert "class AzureOpenAIClient" in content, (
            "AzureOpenAIClient class should be implemented"
        )
        assert "chat_completion" in content, (
            "Chat completion method should be implemented"
        )
        assert "azure" in content.lower(), (
            "Azure-specific configuration should be present"
        )

        # Test configuration exists
        config_path = PROJECT_ROOT / "backend" / "app" / "config.py"
        assert config_path.exists(), "Configuration file should exist"

        content = config_path.read_text()
        assert "azure_openai" in content.lower(), (
            "Azure OpenAI configuration should be present"
        )
        assert "AZURE_OPENAI_ENDPOINT" in content, (
            "Azure OpenAI endpoint configuration should exist"
        )

    def test_adr_0006_character_progression_exists(self) -> None:
        """Test that ADR 0006 (D&D 5e Character Progression) exists."""
        adr_path = PROJECT_ROOT / "docs" / "adr" / "0006-dnd-5e-character-progression-system.md"
        assert adr_path.exists(), "ADR 0006 file should exist"

        content = adr_path.read_text()
        assert "Character Progression" in content, (
            "ADR should be about character progression"
        )
        assert "status: accepted" in content.lower(), "ADR should be accepted"

    def test_agent_database_integration(self) -> None:
        """Test that agents are integrated with persistent storage."""
        # Test ScribeAgent uses database
        scribe_path = PROJECT_ROOT / "backend" / "app" / "agents" / "scribe_agent.py"
        assert scribe_path.exists(), "ScribeAgent should exist"

        content = scribe_path.read_text()
        assert "get_session" in content, "ScribeAgent should use database sessions"
        assert "Character" in content, "ScribeAgent should use Character model"
        assert "db.add" in content or "db.query" in content, (
            "ScribeAgent should perform database operations"
        )

    def test_comprehensive_adr_coverage(self) -> None:
        """Test that all ADRs have corresponding implementations."""
        adr_directory = PROJECT_ROOT / "docs" / "adr"
        assert adr_directory.exists(), "ADR directory should exist"

        # Count ADR files (excluding template and index)
        adr_files = list(adr_directory.glob("0*.md"))
        adr_files = [f for f in adr_files if not f.name.startswith("template")]

        # Should have at least 6 ADRs (0001-0006)
        assert len(adr_files) >= 6, "Should have at least 6 ADRs implemented"

        # Verify ADR index is updated
        index_path = adr_directory / "index.md"
        assert index_path.exists(), "ADR index should exist"

        content = index_path.read_text()
        assert "0006" in content, "ADR index should reference ADR 0006"
