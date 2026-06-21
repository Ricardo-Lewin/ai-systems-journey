"""Typed application configuration.

All runtime config and secrets flow through this module. Read values from the
environment (or a gitignored `.env`) — never hardcode keys. Add new settings
here and document them in `.env.example`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Secret — supplied via env var ANTHROPIC_API_KEY or .env. No default.
    anthropic_api_key: str

    # LLM defaults. Per the journey's convention, default to the most capable
    # Claude model and override only deliberately.
    model: str = "claude-opus-4-8"
    max_tokens: int = 1024

    # Treat the LLM as an unreliable dependency: bounded timeout + one retry.
    request_timeout: float = 30.0
    max_retries: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (validated once at first access)."""
    return Settings()
