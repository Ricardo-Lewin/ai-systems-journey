"""Per-request token and dollar-cost logging.

Every LLM call should log its usage through `log_usage` so cost is observable
from day one (the dashboard arrives in Module 4 — this is the raw signal it
will consume).
"""

import logging

logger = logging.getLogger(__name__)

# USD per single token, keyed by model id. Source: Anthropic pricing
# (Opus 4.x tier: $5.00 / MTok input, $25.00 / MTok output).
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-8": {"input": 5.00 / 1_000_000, "output": 25.00 / 1_000_000},
    "claude-opus-4-7": {"input": 5.00 / 1_000_000, "output": 25.00 / 1_000_000},
    "claude-sonnet-4-6": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
    "claude-haiku-4-5": {"input": 1.00 / 1_000_000, "output": 5.00 / 1_000_000},
}


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the USD cost for a call, or 0.0 if the model is unknown."""
    rates = PRICING.get(model)
    if rates is None:
        logger.warning("No pricing for model %r — reporting cost as $0.00", model)
        return 0.0
    return input_tokens * rates["input"] + output_tokens * rates["output"]


def log_usage(usage, model: str) -> float:
    """Log input/output tokens and computed dollar cost. Returns the cost."""
    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    cost = compute_cost(model, input_tokens, output_tokens)
    logger.info(
        "usage — model=%s input_tokens=%d output_tokens=%d cost=$%.6f",
        model,
        input_tokens,
        output_tokens,
        cost,
    )
    return cost
