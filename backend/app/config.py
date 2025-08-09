"""
Configuration for the backend application.
"""

import os
from typing import Optional, Annotated
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from fastapi import Depends


class Settings(BaseSettings):
    # Azure OpenAI Settings
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
    )

    # Model Deployments
    azure_openai_chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
    azure_openai_embedding_deployment: str = os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""
    )
    azure_openai_dalle_deployment: str = os.getenv(
        "AZURE_OPENAI_DALLE_DEPLOYMENT", "dall-e-3"
    )

    # Semantic Kernel Settings
    semantic_kernel_debug: bool = (
        os.getenv("SEMANTIC_KERNEL_DEBUG", "False").lower() == "true"
    )

    # Storage Settings
    storage_connection_string: str = os.getenv("STORAGE_CONNECTION_STRING", "")

    # App Settings
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_debug: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "info").upper()

    class Config:
        env_file = ".env"

    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return (
            bool(self.azure_openai_endpoint)
            and bool(self.azure_openai_api_key)
            and bool(self.azure_openai_chat_deployment)
            and bool(self.azure_openai_embedding_deployment)
        )


# Global configuration instance - initialized at startup
_settings: Optional[Settings] = None


def init_settings() -> Settings:
    """Initialize settings by loading .env file. Called at startup."""
    # Load environment variables from .env file
    load_dotenv()

    try:
        settings = Settings()
        return settings
    except Exception as e:
        # Check if this is due to missing Azure OpenAI configuration
        error_msg = str(e)
        if "azure_openai" in error_msg.lower():
            raise ValueError(
                "Azure OpenAI configuration is missing or invalid. "
                "This agentic demo requires proper Azure OpenAI setup. "
                "Please ensure the following environment variables are set: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_CHAT_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            ) from e
        else:
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

    def __getattr__(self, name):
        return getattr(get_settings(), name)

    def __setattr__(self, name, value):
        return setattr(get_settings(), name, value)


settings = SettingsProxy()


# FastAPI dependency for configuration injection
def get_config() -> Settings:
    """FastAPI dependency to inject configuration."""
    return get_settings()


# Type alias for dependency injection
ConfigDep = Annotated[Settings, Depends(get_config)]
