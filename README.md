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

🟢 **Module 0 — in progress** (June 2026)

## Stack (evolving)

Python · FastAPI · LLM APIs · vector search · agent orchestration · deployed on a cloud host with tracing + cost dashboards.

---

*Started June 2026. Building in public, one module at a time.*
