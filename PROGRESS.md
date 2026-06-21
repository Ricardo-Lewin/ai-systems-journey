# Progress

Rolling tracker for the AI Systems Journey. See [README.md](README.md) for the why and the
full module arc; this file is the running **status**. Dated, what-changed-when entries live in
[CHANGELOG.md](CHANGELOG.md).

Each module follows the same rhythm: **PRD → build (deployed) → decision log → demo.**

## Status

Legend: ⚪ not started · 🟡 in progress · 🟢 shipped

| # | Module | Status | Destination artifact | Notes |
|---|--------|--------|----------------------|-------|
| 0 | Setup & daily driver | 🟢 shipped | This repo + agentic toolchain | Repo, synthetic logs, layered `app/` skeleton |
| 1 | LLM API fundamentals | 🟢 shipped | FastAPI service: structured output + cost logging | Live on Fly.io; PRD + decision log + demo done |
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
- [x] Deployed (not localhost) — live at https://ai-systems-journey.fly.dev (Fly.io, scale-to-zero)
- [x] Decision log (choices + what was rejected) — [DECISION-LOG-module-1-llm-api.md](DECISION-LOG-module-1-llm-api.md)
- [x] Demo (live URL + README section) — https://ai-systems-journey.fly.dev, see README

**Success metrics — live readings:**
- ✅ Schema-valid response: real logs return a valid `LogSummary` (e.g. status `failure`, confidence `high`).
- ✅ Deployed + reachable: `/health` ok, `/summarize` ok over HTTPS.
- ✅ **Cost/request:** ~$0.017–$0.018 per real log, within the **revised < $0.02** ceiling
  (raised from $0.01 after the live reading; Opus 4.8 kept over a cheaper model pending an eval).
- 🟡 **Latency p95:** now instrumented (`core/timing.py` logs `duration_ms`). **Warm** `/summarize`
  ≈ 5.6–6.0s end-to-end (within < 10s ✅); `/health` < 2ms. **Cold start** (scale-to-zero machine
  waking) measured ≈ 12.3s — exceeds the target on the first hit after idle. Cost vs. latency
  tradeoff (keep `min_machines_running = 0` vs. 1) → decision log.

---

Full dated history: [CHANGELOG.md](CHANGELOG.md).
