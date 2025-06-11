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
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
    )

    # Model Deployments
    azure_openai_chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    azure_openai_embedding_deployment: str = os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )

    # Semantic Kernel Settings
    semantic_kernel_debug: bool = (
        os.getenv("SEMANTIC_KERNEL_DEBUG", "False").lower() == "true"
    )

    # Storage Settings
    storage_connection_string: str = os.getenv("STORAGE_CONNECTION_STRING")

    # App Settings
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_debug: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "info").upper()

    class Config:
        env_file = ".env"


settings = Settings()
