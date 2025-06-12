"""
Configuration for the backend application.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Azure OpenAI Settings
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

    # Model Deployments
    azure_openai_chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    azure_openai_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_openai_dalle_deployment: str = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT", "dall-e-3")

    # Semantic Kernel Settings
    semantic_kernel_debug: bool = os.getenv("SEMANTIC_KERNEL_DEBUG", "False").lower() == "true"

    # Storage Settings
    storage_connection_string: str = os.getenv("STORAGE_CONNECTION_STRING")

    # App Settings
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_debug: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "info").upper()

    class Config:
        env_file = ".env"

# Lazy initialization to avoid validation during import
_settings = None

def get_settings() -> Settings:
    """Get the settings instance, creating it if necessary."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# For backward compatibility, expose as 'settings'
class SettingsProxy:
    """Proxy object that forwards attribute access to the settings instance."""
    def __getattr__(self, name):
        return getattr(get_settings(), name)
    
    def __setattr__(self, name, value):
        return setattr(get_settings(), name, value)

settings = SettingsProxy()
