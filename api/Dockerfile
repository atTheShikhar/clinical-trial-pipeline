FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-cache

COPY . .

EXPOSE 8000
CMD ["/app/.venv/bin/gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.server:app", "--bind", "0.0.0.0:8000"]
