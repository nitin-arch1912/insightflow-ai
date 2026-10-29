"""
Application settings loaded from environment variables.

We use pydantic-settings so every setting is:
  - Typed  (Python type hints enforce the shape)
  - Validated at startup (the app crashes fast with a clear error if misconfigured)
  - Sourced from environment / .env file (never hard-coded secrets)

Usage anywhere in the app:
    from app.core.config import settings
    print(settings.app_version)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # Application                                                          #
    # ------------------------------------------------------------------ #
    app_name: str = "InsightFlow AI"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ------------------------------------------------------------------ #
    # Server                                                               #
    # ------------------------------------------------------------------ #
    host: str = "0.0.0.0"
    port: int = 8000

    # ------------------------------------------------------------------ #
    # Database (Phase 3)                                                   #
    # ------------------------------------------------------------------ #
    database_url: str | None = None

    # ------------------------------------------------------------------ #
    # AI Provider (Phase 7)                                                #
    # ------------------------------------------------------------------ #
    openai_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # ------------------------------------------------------------------ #
    # Pydantic-settings configuration                                      #
    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Silently ignore unknown env vars
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    lru_cache ensures we parse the environment exactly once.
    In tests, call get_settings.cache_clear() to reset between test cases.
    """
    return Settings()


# Convenience singleton — import this everywhere
settings: Settings = get_settings()
