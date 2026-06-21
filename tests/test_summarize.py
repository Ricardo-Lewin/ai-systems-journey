"""Endpoint tests for POST /summarize.

The Anthropic client is overridden via FastAPI dependency injection, so these
tests make no network calls.
"""

from types import SimpleNamespace

import anthropic
import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.llm import get_client
from app.main import app
from app.models.summary import LogSummary

VALID_SUMMARY = LogSummary(
    status="failure",
    summary="Trivy found a critical vulnerability and the pipeline failed.",
    key_events=["trivy scan started", "critical CVE found"],
    errors=["CRITICAL severity vulnerability in base image"],
    suggested_next_step="Bump the base image to a patched version.",
    confidence="high",
)

USAGE = SimpleNamespace(input_tokens=312, output_tokens=89)


class _ParseResponse:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output
        self.usage = USAGE


class _Messages:
    def __init__(self, parsed_output=None, exc=None):
        self._parsed_output = parsed_output
        self._exc = exc

    def parse(self, **_kwargs):
        if self._exc is not None:
            raise self._exc
        return _ParseResponse(self._parsed_output)


class _FakeClient:
    def __init__(self, parsed_output=None, exc=None):
        self.messages = _Messages(parsed_output=parsed_output, exc=exc)


def _override(client: _FakeClient):
    app.dependency_overrides[get_client] = lambda: client
    app.dependency_overrides[get_settings] = lambda: Settings(anthropic_api_key="test-key")


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_happy_path_returns_parsed_summary():
    _override(_FakeClient(parsed_output=VALID_SUMMARY))
    client = TestClient(app)

    resp = client.post("/summarize", content="some deployment log text")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "failure"
    assert body["confidence"] == "high"
    assert body["errors"]


def test_api_error_returns_structured_fallback():
    exc = anthropic.APIConnectionError(
        message="boom",
        request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
    )
    _override(_FakeClient(exc=exc))
    client = TestClient(app)

    resp = client.post("/summarize", content="some deployment log text")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "unknown"
    assert body["confidence"] == "low"


def test_empty_body_returns_400():
    _override(_FakeClient(parsed_output=VALID_SUMMARY))
    client = TestClient(app)

    resp = client.post("/summarize", content="   ")

    assert resp.status_code == 400
