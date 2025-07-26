FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-cache

COPY . .


CMD ["/app/.venv/bin/sqlmesh", "plan", "prod", "--auto-apply"]
