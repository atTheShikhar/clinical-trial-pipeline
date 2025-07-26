FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-cache

COPY . .

RUN /app/.venv/bin/python generate_dummy_data.py

EXPOSE 8000
CMD ["/app/.venv/bin/gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "src.server:app", "--bind", "0.0.0.0:8000"]
