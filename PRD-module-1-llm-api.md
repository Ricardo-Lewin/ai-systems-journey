# PRD — Module 1: LLM API Fundamentals

**Artifact:** A FastAPI service, `POST /summarize`, that turns a raw deployment log into a
validated, structured summary — with cost logged per request and a structured fallback so it
never returns garbage. *Status: 🟡 in progress — see [PROGRESS.md](PROGRESS.md).*

## Problem

Deploy logs are noisy and slow to triage: when a pipeline fails (or half-fails and rolls back),
you skim dozens of lines to answer three questions — *what happened, what broke, what do I do
next.* An LLM can answer those in one shot, but only if the output is **structured enough to act
on** and the call is **reliable and cost-aware** enough to trust. This module proves that
pattern end-to-end on a real, messy input domain.

## Users

**Primary: me, via CLI/curl.** Pipe a log file to the endpoint and read back a structured triage
(`status`, `summary`, `key_events`, `errors`, `suggested_next_step`, `confidence`). This is the
dogfooding step — prove it's useful by hand before wiring it into a pipeline or UI later.

```bash
curl -s --data-binary @synthetic-logs/02_fail_scan_critical.log \
  https://<app>/summarize | jq
```

Secondary (not built here): a CI pipeline or a Module 4 dashboard/bot calling the same endpoint.
The service is designed headless so those can consume it unchanged.

## Success metrics (definition of done)

| Metric | Target |
|--------|--------|
| **Schema-valid response rate** | 100% of responses are a valid `LogSummary` — a real parse **or** a structured fallback. Never raw/garbage output to the caller. |
| **Cost per request** | Logged on every call; stays **< $0.01/request** for a typical deploy log (a few hundred input tokens at Opus 4.8 rates). |
| **Latency (p95)** | p95 end-to-end **< 10s**, backstopped by a 30s timeout + 1 retry (LLM treated as an unreliable dependency). |
| **Deployed + reachable** | A **live public URL** (Fly.io) returns a valid summary for a posted log — not localhost. |

## Scope

**In:**
- Single endpoint `POST /summarize`: raw log text in → `LogSummary` JSON out.
- Schema enforcement via `messages.parse()` + Pydantic; structured fallback (`status:"unknown"`,
  `confidence:"low"`) on timeout, API error, or unparseable output.
- Per-request token + dollar-cost logging to stdout.
- API key from env / `.env`, never hardcoded.
- Deployed to Fly.io.

**Out (deferred):**
- **Auth / rate limiting** — single trusted caller for now.
- **Persistence / history** — stateless; summaries aren't stored (DB arrives when a module needs it).
- **UI / dashboard** — cost goes to stdout; the dashboard is Module 4.
- **Multi-format / batch** — one raw-text log per request; no batch endpoint, no multi-file ingestion.

## Approach (built)

Layered `app/` package (router → service → core): the router is thin HTTP, `services/summarizer.py`
owns the prompt + parse + fallback, `core/` holds config, the Anthropic client (timeout + retry),
and cost logging. Model defaults to `claude-opus-4-8`. See [CLAUDE.md](CLAUDE.md) for conventions.

## Risks & open decisions

- **LLM unreliability** → mitigated by timeout + retry + structured fallback (the core promise).
- **Cost drift on large logs** → input scales with log size; the per-request cost log is the early
  warning, and capping/truncation is a candidate if real logs blow the budget.
- **Deploy target** → Fly.io chosen (Dockerfile + `fly secrets set ANTHROPIC_API_KEY`); the full
  rationale and anything rejected go in the Module 1 **decision log** (next deliverable).
