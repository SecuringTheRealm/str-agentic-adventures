"""
Configuration for the backend application.
"""

from typing import Annotated, Any

from dotenv import load_dotenv
from fastapi import Depends
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", frozen=True)

    # Azure OpenAI Settings
    # Pydantic-settings automatically reads from environment variables
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    azure_openai_api_version: str = "2025-04-01-preview"

    # Model Deployments (names match Bicep deployment resource names)
    azure_openai_chat_deployment: str = "gpt-41-mini"
    azure_openai_dalle_deployment: str = "gpt-image-1-mini"
    azure_openai_realtime_deployment: str = "gpt-realtime-mini"

    # Per-agent chat deployment overrides (F03). Empty string falls back to
    # ``azure_openai_chat_deployment`` via ``deployment_for()``. Only the three
    # chat-driven agents get their own knob; image/scribe agents do not call chat.
    azure_openai_dm_deployment: str = ""
    azure_openai_narrator_deployment: str = ""
    azure_openai_combat_deployment: str = ""

    # Microsoft Foundry project endpoint (Agent Framework FoundryChatClient).
    # Format: https://<account>.services.ai.azure.com/api/projects/<project>
    azure_ai_project_endpoint: str = ""

    # Image generation cost controls
    # Limits the number of DALL-E images generated per session to reduce spend.
    max_images_per_session: int = 3
    image_session_window_minutes: int = 30

    # Auto-save interval: persist game state every N player interactions.
    auto_save_interval: int = 5

    # Azure AI Content Safety
    content_safety_endpoint: str = ""
    content_safety_api_key: str = ""

    # Storage Settings
    azure_storage_account_name: str = ""
    storage_connection_string: str = ""

    # CORS Settings
    # Comma-separated list of allowed origins for CORS
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # App Settings
    # Note: Default binds to all interfaces (0.0.0.0) for development convenience.
    # Production deployments MUST override via APP_HOST environment variable
    # to bind to specific interface (e.g., 127.0.0.1 or specific IP).
    app_host: str = "0.0.0.0"  # noqa: S104
    app_port: int = 8000
    app_debug: bool = False
    app_log_level: str = "INFO"

    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI (image generation) is properly configured.

        Authentication is handled by DefaultAzureCredential, so an API key
        is not required.  The key field is kept for local-development use.
        """
        return bool(self.azure_openai_endpoint) and bool(
            self.azure_openai_chat_deployment
        )

    def is_foundry_configured(self) -> bool:
        """Check if the Microsoft Foundry project endpoint is configured.

        Gates the Agent Framework FoundryChatClient chat path; when False,
        agents use deterministic fallback logic.
        """
        return bool(self.azure_ai_project_endpoint)

    def deployment_for(self, setting_name: str) -> str:
        """Resolve a per-agent deployment override, defaulting to the chat model."""
        return getattr(self, setting_name, "") or self.azure_openai_chat_deployment


# Global configuration instance - initialized at startup
_settings: Settings | None = None


def init_settings() -> Settings:
    """Initialize settings by loading .env file. Called at startup."""
    global _settings
    # Load environment variables from .env file
    load_dotenv()

    try:
        _settings = Settings()
        return _settings
    except Exception as e:
        # Check if this is due to missing Azure OpenAI configuration
        error_msg = str(e)
        if "azure_openai" in error_msg.lower():
            raise ValueError(
                "Azure OpenAI configuration is missing or invalid. "
                "This agentic demo requires proper Azure OpenAI setup. "
                "Please ensure the following environment variables are set: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_CHAT_DEPLOYMENT. "
                "Authentication uses DefaultAzureCredential (managed identity) "
                "by default; set AZURE_OPENAI_API_KEY only for local development."
            ) from e
        # Re-raise original error for non-Azure OpenAI issues
        raise


def get_settings() -> Settings:
    """Get the settings instance. Used for FastAPI dependency injection."""
    global _settings
    if _settings is None:
        _settings = init_settings()
    return _settings


def set_settings(settings: Settings) -> None:
    """Set the global settings instance. Used for testing."""
    global _settings
    _settings = settings


# For backward compatibility, expose as 'settings'
class SettingsProxy:
    """Proxy object that forwards attribute access to the settings instance."""

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        return getattr(get_settings(), name)

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
        return setattr(get_settings(), name, value)


settings = SettingsProxy()


# FastAPI dependency for configuration injection
def get_config() -> Settings:
    """FastAPI dependency to inject configuration."""
    return get_settings()


# Type alias for dependency injection
ConfigDep = Annotated[Settings, Depends(get_config)]
