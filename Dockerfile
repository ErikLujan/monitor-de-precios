# Dockerfile multi-stage para monitor-de-precios
# Stage 1: Base con dependencias del sistema
FROM python:3.11.5-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# Stage 2: Dependencias Python con uv
FROM base AS deps

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev


# Stage 3: Playwright con Chromium
FROM deps AS playwright

RUN uv run playwright install chromium --with-deps


# Stage 4: Runtime final
FROM playwright AS runtime

# Copiar código fuente
COPY src/ ./src/
COPY products.yaml.example ./products.yaml.example

# Crear directorios para datos y logs
RUN mkdir -p /app/data /app/logs

# Usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Comando por defecto: scheduler
CMD ["python", "-m", "monitor_de_precios.cli.main", "scheduler"]