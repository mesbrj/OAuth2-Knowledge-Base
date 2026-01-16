"""
Application settings and configuration management.
Uses pydantic-settings to load configuration from environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    HYDRA_ADMIN_URL: str = "http://localhost:4445"
    HYDRA_PUBLIC_URL: str = "http://localhost:4444"
    OAUTH2_CLIENT_ID: Optional[str] = None
    OAUTH2_CLIENT_SECRET: Optional[str] = None

    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8080/auth/github-callback"

    KETO_READ_URL: str = "http://localhost:4466"
    KETO_WRITE_URL: str = "http://localhost:4467"
    KETO_NAMESPACE: str = "fastapi-resource-server"

    APP_URL: str = "http://localhost:8080"
    ENVIRONMENT: str = "development"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()