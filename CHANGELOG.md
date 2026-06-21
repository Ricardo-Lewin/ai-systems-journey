# Changelog

All notable changes to this project. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this is a build-in-public journey, so entries are
dated and grouped by **module milestone** rather than software versions. Status lives in
[PROGRESS.md](PROGRESS.md); the *why* behind choices lives in the per-module decision logs.

## [Unreleased]

_Nothing in flight._

## 2026-06-21 — Module 1: deployed + instrumented

### Added
- **Deployed to Fly.io** — live at https://ai-systems-journey.fly.dev. Dockerfile (uv-based, remote
  build), `fly.toml` (port 8080, `/health` check, HTTPS, scale-to-zero), `.dockerignore`.
- `/health` liveness endpoint (`app/routers/health.py`) for Fly's health check.
- Per-request latency logging — `app/core/timing.py` middleware logs `duration_ms` end-to-end.
- Module 1 decision log ([DECISION-LOG-module-1-llm-api.md](DECISION-LOG-module-1-llm-api.md)):
  6 decisions (architecture, uv, structured output + fallback, Fly.io, cost ceiling, scale-to-zero).
- Module 1 demo section in the README (live URL + example request + honest metrics).
- `CHANGELOG.md` (this file); PROGRESS.md now tracks status only and links here.

### Changed
- Raised the PRD cost ceiling **$0.01 → $0.02** after a live log measured $0.017 (output tokens at
  $25/MTok dominate); kept `claude-opus-4-8`, deferred any cheaper-model switch to a Module 2 eval.

### Verified (live)
- `/health` ok, `/summarize` returns a valid `LogSummary`, cost + latency logged in prod.
- Warm `/summarize` ≈ 6s (within p95 < 10s); cold start ≈ 12.3s (first hit after idle, over target).

## 2026-06-20 — Module 1: architecture + PRD

### Added
- Module 1 PRD ([PRD-module-1-llm-api.md](PRD-module-1-llm-api.md)): primary user CLI/curl;
  success = 100% schema-valid, cost/req ceiling, p95 < 10s, deployed on Fly.io.
- Typed config (`pydantic-settings`), uv tooling + lockfile, `CLAUDE.md` conventions.
- No-network test suite (FastAPI `TestClient` + dependency overrides).

### Changed
- Refactored the summarizer from a single `service/main.py` into a layered `app/` package
  (router → service → core) — the foundation modules 2–6 build on.

### Removed
- `service/` (migrated into `app/`).

## June 2026 — Module 0: kickoff

### Added
- Repo + journey README.
- 15 synthetic deployment logs (`synthetic-logs/`) spanning success, failure, partial/rollback, and
  malformed cases — the test inputs for Module 1.
- First `/summarize` service (structured output + cost logging).
