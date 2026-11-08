# Dockerfile multi-stage para monitor-de-precios
# Stage 1: Base con dependencias del sistema
FROM python:3.11.5-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS deps

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

FROM base AS playwright

COPY --from=deps /app/.venv /app/.venv

COPY --from=deps /usr/local/bin/uv /usr/local/bin/uv

ENV PATH="/app/.venv/bin:$PATH"

RUN uv run playwright install chromium --with-deps

FROM base AS runtime

COPY --from=playwright /root/.cache/ms-playwright /root/.cache/ms-playwright

COPY --from=deps /app/.venv /app/.venv

COPY src/ ./src/

COPY products.yaml.example ./products.yaml.example

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

    EXPOSE 8501

    USER 1000:1000

    CMD ["python", "-m", "monitor_de_precios.cli.main", "scheduler"]