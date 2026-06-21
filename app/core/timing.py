"""Per-request latency logging.

Logs end-to-end duration for every request as a structured line, alongside the
cost signal from `core/cost.py`. Together they're the raw feed for the Module 4
observability dashboard (latency p95, cost/request).
"""

import logging
import time

from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


async def log_request_timing(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request — method=%s path=%s status=%d duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response
