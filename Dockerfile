# ========= BUILDER: uv + deps =========
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

WORKDIR /app

# Kopiujemy definicje zależności
COPY pyproject.toml uv.lock ./

# Instalacja zależności w .venv (bez dev)
RUN uv sync --frozen --no-dev

# Kopiujemy źródła
COPY src ./src


# ========= RUNTIME: ultra-slim backend =========
FROM python:3.12-slim AS runtime

WORKDIR /app

# Zależności systemowe (minimalne, ale stabilizują buildy)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Przenosimy venv + kod
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/src ./src
COPY pyproject.toml ./

# PATH → używamy venv jako głównego interpretera
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Europe/Warsaw
ENV PYTHONPATH=/app/src


EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/health || exit 1

# Produkcyjny entrypoint
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
