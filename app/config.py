"""Application configuration management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the NSFW checker service loaded from environment variables."""

    openai_api_key: str
    port: int = 8080
    max_file_size_mb: int = 25
    cors_origins: str = ""  # Comma-separated list, empty means allow all in dev
    rate_limit: str = "10/minute"  # Rate limit for API endpoints

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> "Settings":
    """Provide application settings instance.

    Returns the cached Settings instance. Wrapped in a function to ease testing
    overrides where necessary.
    """

    return settings


settings = Settings()
