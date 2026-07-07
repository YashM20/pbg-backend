FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-cache
COPY app ./app

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app /app
EXPOSE 8001
CMD ["/bin/sh", "-c", "exec /app/.venv/bin/fastapi run app/main.py --port ${PORT:-8001} --host 0.0.0.0"]