"""Schema for a structured log summary returned by POST /summarize."""

from typing import Literal

from pydantic import BaseModel


class LogSummary(BaseModel):
    status: Literal["success", "failure", "partial", "unknown"]
    summary: str
    key_events: list[str]
    errors: list[str]
    suggested_next_step: str
    confidence: Literal["high", "medium", "low"]
