# Progress

Rolling tracker for the AI Systems Journey. See [README.md](README.md) for the why and the
full module arc; this file is the running status + changelog.

Each module follows the same rhythm: **PRD → build (deployed) → decision log → demo.**

## Status

Legend: ⚪ not started · 🟡 in progress · 🟢 shipped

| # | Module | Status | Destination artifact | Notes |
|---|--------|--------|----------------------|-------|
| 0 | Setup & daily driver | 🟢 shipped | This repo + agentic toolchain | Repo, synthetic logs, layered `app/` skeleton |
| 1 | LLM API fundamentals | 🟡 in progress | FastAPI service: structured output + cost logging | `/summarize` live; deploy + decision log remain |
| 2 | Retrieval-Augmented Generation | ⚪ not started | Grounded Q&A over a real corpus + eval set | |
| 3 | Tool use & single agent | ⚪ not started | Agent that takes real actions, with guardrails | |
| 4 | Production hardening | ⚪ not started | Observability, cost control, failure recovery | Cost signal already emitted in `core/cost.py` |
| 5 | Multi-agent orchestration | ⚪ not started | Coordinated agents + framework tradeoff writeup | |
| 6 | Capstone | ⚪ not started | Deployed agentic system, end-to-end | |

## Module 1 — checklist

- [x] `POST /summarize` endpoint: raw log in, structured JSON out
- [x] Schema validation via `messages.parse()` + Pydantic (`LogSummary`)
- [x] Structured fallback on failure (`status="unknown"`, `confidence="low"`) — never returns garbage
- [x] Timeout + one retry (LLM treated as unreliable dependency)
- [x] Per-request token + dollar-cost logging
- [x] API key from env / `.env`, never hardcoded
- [x] Layered `app/` architecture (router → service → core) + tests
- [x] PRD (one page: problem, users, success metrics, scope cuts) — [PRD-module-1-llm-api.md](PRD-module-1-llm-api.md)
- [ ] Deployed (not localhost) on a cloud host
- [ ] Decision log (choices + what was rejected)
- [ ] Demo (live URL + README section)

## Changelog

### 2026-06-20
- Wrote the Module 1 PRD ([PRD-module-1-llm-api.md](PRD-module-1-llm-api.md)): primary user is
  CLI/curl dogfooding; success = 100% schema-valid, < $0.01/req, p95 < 10s, deployed on Fly.io.
- Refactored the summarizer from a single `service/main.py` into a layered `app/` package
  (router → service → core), the foundation modules 2–6 build on.
- Added typed config (`pydantic-settings`), uv tooling + lockfile, `CLAUDE.md` conventions,
  and a no-network test suite (3 passing).

### June 2026 — Module 0 kickoff
- Created the repo and journey README.
- Generated 15 synthetic deployment logs (`synthetic-logs/`) spanning success, failure,
  partial/rollback, and malformed cases — the test inputs for Module 1.
- Built the first `/summarize` service (structured output + cost logging).
