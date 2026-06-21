"""Anthropic client provisioning.

Builds the SDK client from `Settings` with a bounded timeout and one retry so
the LLM is treated as an unreliable dependency. The client is cached so we
don't rebuild it per request.
"""

from functools import lru_cache

import anthropic

from app.core.config import get_settings


@lru_cache
def get_client() -> anthropic.Anthropic:
    settings = get_settings()
    return anthropic.Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=settings.request_timeout,
        max_retries=settings.max_retries,
    )
