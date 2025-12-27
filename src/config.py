"""Configuration management using pydantic-settings."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # SerpAPI (required)
    serpapi_api_key: str = Field(
        ...,
        description="SerpAPI key for Google Scholar access",
    )

    # CORE API (optional, for full-text access)
    core_api_key: Optional[str] = Field(
        default=None,
        description="CORE API key for Open Access full-text (free at core.ac.uk)",
    )


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
