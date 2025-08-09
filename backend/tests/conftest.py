"""
Test configuration and utilities for improved configuration handling.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.config import Settings, set_settings, get_config
from app.main import app

# Import factories for use in tests (gracefully handle missing dependencies)
try:
    from .factories import (
        CharacterFactory,
        FighterCharacterFactory,
        WizardCharacterFactory,
        CampaignFactory,
        CombatEncounterFactory,
        AttackActionFactory,
        SpellAttackActionFactory,
        SpellDamageActionFactory,
        SkillCheckActionFactory,
        SavingThrowActionFactory,
    )

    _FACTORIES_AVAILABLE = True
except ImportError as e:
    # factory_boy not available in this environment
    _FACTORIES_AVAILABLE = False
    # Create dummy factories for graceful degradation
    CharacterFactory = None
    FighterCharacterFactory = None
    WizardCharacterFactory = None
    CampaignFactory = None
    CombatEncounterFactory = None
    AttackActionFactory = None
    SpellAttackActionFactory = None
    SpellDamageActionFactory = None
    SkillCheckActionFactory = None
    SavingThrowActionFactory = None


@pytest.fixture
def factories_available():
    """Check if factory_boy is available in this environment."""
    return _FACTORIES_AVAILABLE


@pytest.fixture
def character_factory():
    """Factory for creating character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CharacterFactory


@pytest.fixture
def fighter_character_factory():
    """Factory for creating fighter character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return FighterCharacterFactory


@pytest.fixture
def wizard_character_factory():
    """Factory for creating wizard character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return WizardCharacterFactory


@pytest.fixture
def campaign_factory():
    """Factory for creating campaign data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CampaignFactory


@pytest.fixture
def combat_encounter_factory():
    """Factory for creating combat encounter data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CombatEncounterFactory


@pytest.fixture
def attack_action_factory():
    """Factory for creating attack action data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return AttackActionFactory


@pytest.fixture
def spell_attack_action_factory():
    """Factory for creating spell attack action data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return SpellAttackActionFactory


def create_test_config():
    """Factory for creating character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CharacterFactory


@pytest.fixture
def fighter_character_factory():
    """Factory for creating fighter character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return FighterCharacterFactory


@pytest.fixture
def wizard_character_factory():
    """Factory for creating wizard character data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return WizardCharacterFactory


@pytest.fixture
def campaign_factory():
    """Factory for creating campaign data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CampaignFactory


@pytest.fixture
def combat_encounter_factory():
    """Factory for creating combat encounter data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return CombatEncounterFactory


@pytest.fixture
def attack_action_factory():
    """Factory for creating attack action data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return AttackActionFactory


@pytest.fixture
def spell_attack_action_factory():
    """Factory for creating spell attack action data."""
    if not _FACTORIES_AVAILABLE:
        pytest.skip("factory_boy not available in this environment")
    return SpellAttackActionFactory
    """Create a test configuration with minimal Azure OpenAI settings."""
    return Settings(
        azure_openai_endpoint="https://test.openai.azure.com",
        azure_openai_api_key="test-api-key",
        azure_openai_chat_deployment="test-chat-deployment",
        azure_openai_embedding_deployment="test-embedding-deployment",
        azure_openai_api_version="2023-12-01-preview",
        azure_openai_dalle_deployment="dall-e-3",
        semantic_kernel_debug=False,
        storage_connection_string="",
        app_host="0.0.0.0",
        app_port=8000,
        app_debug=False,
        app_log_level="INFO",
    )


def create_test_config_missing_azure():
    """Create a test configuration with missing Azure OpenAI settings."""
    return Settings(
        azure_openai_endpoint="",
        azure_openai_api_key="",
        azure_openai_chat_deployment="",
        azure_openai_embedding_deployment="",
        azure_openai_api_version="2023-12-01-preview",
        azure_openai_dalle_deployment="dall-e-3",
        semantic_kernel_debug=False,
        storage_connection_string="",
        app_host="0.0.0.0",
        app_port=8000,
        app_debug=False,
        app_log_level="INFO",
    )


@pytest.fixture
def test_config():
    """Create a test configuration with minimal Azure OpenAI settings."""
    return create_test_config()


@pytest.fixture
def test_config_missing_azure():
    """Create a test configuration with missing Azure OpenAI settings."""
    return create_test_config_missing_azure()


@pytest.fixture
def client_with_config():
    """Create a test client with injected configuration."""
    test_config = create_test_config()
    # Override the configuration dependency
    app.dependency_overrides[get_config] = lambda: test_config
    client = TestClient(app)
    yield client
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_missing_config():
    """Create a test client with missing configuration."""
    test_config_missing = create_test_config_missing_azure()
    # Override the configuration dependency
    app.dependency_overrides[get_config] = lambda: test_config_missing
    client = TestClient(app)
    yield client
    # Clean up
    app.dependency_overrides.clear()


def override_config_dependency(test_config: Settings):
    """Utility function to override config dependency for a specific test."""

    def override():
        return test_config

    return override
