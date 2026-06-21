"""Log-summarization business logic.

Calls Claude to turn raw deployment log text into a validated `LogSummary`.
The LLM is treated as unreliable: on timeout, API error, or unparseable
output we return a structured fallback (status "unknown", confidence "low")
rather than raising garbage at the caller. Every call logs its token/cost
usage.
"""

import logging

import anthropic

from app.core.config import Settings
from app.core.cost import log_usage
from app.models.summary import LogSummary

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You analyze deployment log text and return a structured summary.
Return ONLY valid JSON matching this exact schema — no prose, no markdown fences:

{
  "status": "success" | "failure" | "partial" | "unknown",
  "summary": "<one sentence describing the overall outcome>",
  "key_events": ["<notable event>", ...],
  "errors": ["<error message>", ...],
  "suggested_next_step": "<actionable recommendation, or 'none required'>",
  "confidence": "high" | "medium" | "low"
}

Rules:
- status "success": all stages completed without errors
- status "failure": pipeline or deployment failed
- status "partial": some stages succeeded, some failed or rolled back
- status "unknown": cannot determine from the log
- confidence reflects how clearly the log supports the status choice\
"""


def _fallback(reason: str) -> LogSummary:
    logger.warning("Returning fallback summary — %s", reason)
    return LogSummary(
        status="unknown",
        summary="Unable to produce a structured summary from the model response.",
        key_events=[],
        errors=[reason],
        suggested_next_step="Retry the request or inspect the log manually.",
        confidence="low",
    )


def summarize_log(
    log_text: str,
    client: anthropic.Anthropic,
    settings: Settings,
) -> LogSummary:
    """Summarize raw log text into a validated LogSummary, never raising."""
    response = None
    try:
        response = client.messages.parse(
            model=settings.model,
            max_tokens=settings.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": log_text}],
            output_format=LogSummary,
        )
        result = response.parsed_output
        if result is None:
            return _fallback("Model returned empty or unparseable content")
        return result
    except anthropic.APITimeoutError as exc:
        logger.error("Anthropic API timeout: %s", exc)
        return _fallback(f"API timeout: {exc}")
    except anthropic.APIError as exc:
        logger.error("Anthropic API error: %s", exc)
        return _fallback(f"API error: {exc}")
    except Exception as exc:  # noqa: BLE001 — never leak a raw error to the caller
        logger.error("Unexpected error during summarization: %s", exc)
        return _fallback(f"Unexpected error: {exc}")
    finally:
        if response is not None:
            log_usage(response.usage, settings.model)
