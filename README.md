# AI Systems Journey

A 12-month, build-in-public log of leveling up from mid-level engineer to senior IC by learning to architect **production AI systems** — not demos.

## Why this exists

I'm a backend / DevOps engineer (FastAPI, Celery, Docker, CI/CD, SQL → Snowflake). The half of AI systems engineering that's scarce in 2026 isn't model research — it's shipping agentic systems that are **reliable, observable, and cost-controlled** under real traffic. That's an extension of production engineering I already do. This repo is me closing that gap in public.

The bet: the engineers who win aren't the ones who can call an LLM API — they're the ones who can ship an agent that runs for months without an incident.

## The arc

Each module ends in something **deployed and observable**, and the projects **chain into one evolving system** rather than six disconnected toys.

| # | Module | Destination artifact |
|---|--------|---------------------|
| 0 | Setup & daily driver | This repo + agentic coding toolchain |
| 1 | LLM API fundamentals | FastAPI service, structured output + cost logging |
| 2 | Retrieval-Augmented Generation | Grounded Q&A over a real corpus + eval set |
| 3 | Tool use & single agent | Agent that takes real actions, with guardrails |
| 4 | Production hardening | Observability, cost control, failure recovery |
| 5 | Multi-agent orchestration | Coordinated specialized agents + framework tradeoff writeup |
| 6 | Capstone | A deployed agentic system solving a real problem end-to-end |

## How I work each module

1. **PRD first** — one page: problem, users, success metrics, scope cuts.
2. **Build** — deployed, not localhost.
3. **Decision log** — the architectural choices and *why*, including what I rejected.
4. **Demo** — live URL + README + decision log.

The decision logs are the point. The reasoning matters more than the code.

## Status

🟢 **Module 1 — shipped** (June 2026) · live demo below. Full status in [PROGRESS.md](PROGRESS.md),
history in [CHANGELOG.md](CHANGELOG.md).

## Module 1 — Log Summarizer (live)

A FastAPI service that turns a raw deployment log into a validated, structured summary — with a
per-request cost + latency signal and a structured fallback so it never returns garbage.

**Live:** https://ai-systems-journey.fly.dev

```bash
# Summarize a deploy log (pipe any raw log to the endpoint)
curl -s --data-binary @synthetic-logs/02_fail_scan_critical.log \
  https://ai-systems-journey.fly.dev/summarize | jq
```

```jsonc
{
  "status": "failure",
  "summary": "Pipeline #48190 failed at the build stage because the security scan found a CRITICAL vulnerability that blocked image promotion.",
  "key_events": ["Docker image ledger-api:7e1b08d built successfully", "Trivy scan executed", "..."],
  "errors": ["CVE-2026-3119 in openssl 3.0.2 — severity CRITICAL", "..."],
  "suggested_next_step": "Bump openssl to >=3.0.14 in the base image, then rerun the pipeline.",
  "confidence": "high"
}
```

**How it's built:** layered FastAPI app (router → service → core), schema enforced via Anthropic's
`messages.parse()` + Pydantic, timeout + retry treating the LLM as an unreliable dependency, and
per-request token/cost + latency logged for observability. Deployed on Fly.io (scale-to-zero).

**Honest metrics** (measured live, not aspirational):

| Metric | Result |
|--------|--------|
| Schema-valid responses | 100% (real parse or structured fallback — never garbage) |
| Cost / request | ~$0.017 on a typical log (Opus 4.8; ceiling set at $0.02) |
| Latency | warm ≈ 6s · cold start ≈ 12s (scale-to-zero tradeoff) |

→ [PRD](PRD-module-1-llm-api.md) · [Decision log](DECISION-LOG-module-1-llm-api.md) (incl. what was rejected)

## Stack (evolving)

Python · FastAPI · LLM APIs · vector search · agent orchestration · deployed on a cloud host with tracing + cost dashboards.

---

*Started June 2026. Building in public, one module at a time.*
