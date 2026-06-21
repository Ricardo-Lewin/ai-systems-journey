"""FastAPI application factory.

As the journey progresses, new features are added as additional routers
(`app/routers/`) backed by services (`app/services/`) — shared infra stays in
`app/core/`. This file just wires them together.
"""

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.core.timing import log_request_timing
from app.routers import health, summarize


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AI Systems Journey")
    app.middleware("http")(log_request_timing)
    app.include_router(health.router)
    app.include_router(summarize.router)
    return app


app = create_app()
