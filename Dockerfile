# Build + run the service with uv. Base image ships uv + Python 3.12.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Reproducible, container-friendly uv behavior; don't fetch other Pythons.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependencies first (cached layer) from the lockfile only — no dev deps.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Then the application source.
COPY app ./app

EXPOSE 8080
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
