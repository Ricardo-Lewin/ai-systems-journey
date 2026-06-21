# Decision Log — Module 1: LLM API Fundamentals

The choices behind the `/summarize` service and **why**, including what was rejected. Pairs with
the [PRD](PRD-module-1-llm-api.md) (intent + metrics) and [PROGRESS.md](PROGRESS.md) (status).

Format per entry: **Context → Decision → Rejected → Consequences.**

---

## D1 — Layered `app/` package (router → service → core) over a single file

**Context.** The working service started as one `service/main.py`. The journey's modules chain into
*one evolving system* (RAG → agent → hardening → multi-agent), so module 2+ will keep adding to this
codebase, not start fresh.

**Decision.** Refactor into a single growing `app/` package with thin routers, business logic in
`services/`, shared infra (config, LLM client, cost, timing, logging) in `core/`, and Pydantic in
`models/`. Dependencies (client, settings) are injected via FastAPI `Depends`.

**Rejected.**
- *Stay single-file* — fastest now, but every later module compounds the cleanup debt.
- *Per-module apps in a monorepo* — more isolation, but duplicated infra and multiple deploy targets
  for what is meant to be one evolving system.
- *src-layout packaging* — correct for distributables; unnecessary ceremony for a deployed service.

**Consequences.** The summarizer became a reference vertical slice future modules copy. DI made a
no-network test suite trivial (override the client). Conventions are written down in `CLAUDE.md`.

---

## D2 — uv for dependency + environment management

**Context.** Need reproducible installs and a Docker-friendly toolchain; deploys are coming.

**Decision.** uv + `pyproject.toml` + `uv.lock`; dev tools (pytest, ruff) in a `dev` dependency group;
the Docker image installs `--no-dev` from the frozen lock.

**Rejected.** *Poetry* (mature but slower, heavier) and *pip + requirements.txt* (universal but no
lockfile/resolver guarantees). uv gives a fast resolver, a real lockfile, and a clean Docker story.

**Consequences.** `uv sync` is near-instant; the prod image is 80 MB and excludes dev deps. The lock
resolved on local Python 3.14 but the image pins 3.12 — fine under `requires-python >=3.11`, worth
remembering if a version-specific wheel ever bites.

---

## D3 — Structured output via `messages.parse()` + Pydantic, with a structured fallback

**Context.** The endpoint must return JSON the caller can act on, and the LLM is an unreliable
dependency (timeouts, API errors, occasionally unparseable output).

**Decision.** Use `client.messages.parse(output_format=LogSummary)` to enforce the schema, wrap the
call in timeout + 1 retry, and on *any* failure return a structured fallback
(`status="unknown"`, `confidence="low"`) instead of raising. The caller never sees garbage.

**Rejected.**
- *Free-form text + regex/manual JSON parsing* — brittle, exactly the garbage path this avoids.
- *Raw `output_config` JSON schema* — works, but `parse()` + Pydantic gives validation and typed
  objects for free.
- *Propagate errors as 5xx* — leaks an unreliable dependency's failures to the client; the fallback
  keeps the contract (always a valid `LogSummary`) intact.

**Consequences.** "100% schema-valid responses" became an achievable, tested guarantee (happy path,
API-error fallback, empty-body 400).

---

## D4 — Deploy to Fly.io

**Context.** The PRD bar is "deployed, not localhost." Single FastAPI container, one secret, want low
ceremony and a remote builder (no local Docker daemon available).

**Decision.** Fly.io with a uv-based Dockerfile, `fly.toml` (port 8080, `/health` check, HTTPS), secret
via `fly secrets set`, built on Fly's remote builder.

**Rejected.** *Render* and *Railway* — both viable git-connected PaaS; Fly chosen for the explicit
Docker/secret control and remote build that fit the constraints. Not a strong rejection — revisit if
Fly's billing or cold-start behavior becomes a problem.

**Consequences.** Live at https://ai-systems-journey.fly.dev. Remote builder sidestepped the missing
local Docker. The `/health` endpoint (added for Fly's check) doubles as general liveness.

---

## D5 — Raise the cost ceiling $0.01 → $0.02; keep Opus 4.8, defer model choice to an eval

**Context.** The PRD set < $0.01/request. The first live log measured **$0.017**
(1299 in / 421 out tokens) — output tokens at $25/MTok dominate. The $0.01 target was a guess made
before any real measurement.

**Decision.** Raise the ceiling to **< $0.02** and stay on `claude-opus-4-8` for now. Defer any switch
to a cheaper model until Module 2 gives us an eval set to judge quality loss against.

**Rejected (for now).**
- *Route to Haiku/Sonnet* — Haiku ($1/$5 per MTok) would cut the same call to ≈ $0.0034, but on
  messy/truncated logs the quality risk is unmeasured. Don't trade accuracy blind — decide with an eval.
- *Cap output tokens / terser schema* — fewer output tokens, but risks truncating `key_events`/`errors`,
  the most useful fields.

**Consequences.** Real logs (~$0.0177) now sit inside the ceiling honestly. Created a concrete,
evidence-backed question for Module 2's eval work: *is a cheaper model good enough on these logs?*

---

## D6 — Scale-to-zero (`min_machines_running = 0`): accept cold-start latency for near-zero idle cost

**Context.** Cost control is a journey theme, and the primary user is me via CLI/curl (bursty, low
traffic). After adding latency logging: **warm** `/summarize` ≈ 6s (within p95 < 10s ✅), but a **cold
start** (machine waking from zero) measured ≈ **12.3s** — over target on the first hit after idle.

**Decision.** Keep `min_machines_running = 0`. Accept the occasional cold-start hit in exchange for
near-zero idle cost; treat the p95 < 10s target as a *warm* metric for now.

**Rejected.** *`min_machines_running = 1`* — keeps a machine always warm (~6s p95 every time) but bills
24/7, which contradicts the cost-control intent for a personal, low-traffic tool.

**Consequences.** Idle cost is negligible; first-request-after-idle latency is the known cost. If this
ever fronts a latency-sensitive consumer (a CI gate, a UI), revisit — keep one warm, or add a keep-warm
ping. This is the kind of cost/latency lever Module 4 (production hardening) will tune deliberately.
