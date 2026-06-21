"""POST /summarize — thin HTTP layer over the summarizer service."""

from typing import Annotated

import anthropic
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.config import Settings, get_settings
from app.core.llm import get_client
from app.models.summary import LogSummary
from app.services.summarizer import summarize_log

router = APIRouter()


@router.post("/summarize", response_model=LogSummary)
async def summarize(
    request: Request,
    client: Annotated[anthropic.Anthropic, Depends(get_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LogSummary:
    log_text = (await request.body()).decode("utf-8")
    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Request body must not be empty")
    return summarize_log(log_text, client=client, settings=settings)
