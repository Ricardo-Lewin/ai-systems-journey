# CLAUDE.md

Guidance for working in this repo. See `README.md` for the project's purpose and module arc.

## Project

A build-in-public journey toward production AI systems. Modules chain into **one
evolving system** (LLM service → RAG → tool-use agent → hardening → multi-agent),
so the codebase grows in place — each module adds features, it does not start over.

## Architecture

One growing `app/` package, layered **router → service → core**:

| Layer | Path | Responsibility |
|-------|------|----------------|
| Router | `app/routers/` | HTTP only — parse the request, delegate, return. Keep thin. |
| Service | `app/services/` | Business logic — prompts, LLM calls, fallbacks. |
| Core | `app/core/` | Shared infra — config, LLM client, cost logging, logging setup. |
| Models | `app/models/` | Pydantic schemas (request/response shapes). |

`app/main.py` is the FastAPI factory (`create_app()`) that wires routers together.

**Adding a feature/module:** create a new router in `app/routers/`, back it with a
service in `app/services/`, define its schemas in `app/models/`, and reuse `app/core/`.
Register the router in `create_app()`. Don't put logic in routers; don't duplicate
infra that belongs in core.

## Model defaults

- Default to **`claude-opus-4-8`**. Only use another model if explicitly chosen; set it
  via the `MODEL` env var, don't hardcode in call sites.
- Use adaptive thinking (`thinking={"type": "adaptive"}`) for non-trivial calls.
- **Never hardcode the API key.** It comes from `Settings` (`ANTHROPIC_API_KEY` / `.env`).

## Config

All config and secrets are typed in `app/core/config.py` (`Settings`, pydantic-settings).
Add new settings there and document them in `.env.example`. Read settings via
`get_settings()` — don't reach for `os.environ` directly in feature code.

## Conventions

- **Every LLM call logs usage** via `app/core/cost.py` (`log_usage`) — tokens + dollar cost.
- **Treat the LLM as unreliable:** bounded timeout + retry on the client; return a
  structured fallback (e.g. `status="unknown"`, `confidence="low"`) instead of raising
  raw errors at the caller.
- Inject dependencies (client, settings) via FastAPI `Depends` so they can be overridden
  in tests.

## Commands

```bash
uv sync                                   # install deps + create/refresh uv.lock
cp .env.example .env                      # then add your ANTHROPIC_API_KEY
uv run uvicorn app.main:app --reload      # run the dev server
uv run pytest                             # run tests (no network)
uv run ruff check                         # lint
```
