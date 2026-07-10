FROM ghcr.io/astral-sh/uv:python3.14-alpine3.23
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# If you can, prefer binary wheels to skip postgres headers:
# in requirements.prod.txt use: psycopg[binary]==<version>
# (otherwise we'll keep postgresql-dev only for build)
RUN apk add --no-cache \
      gcc \
      libffi-dev \
      musl-dev \
      openssl-dev \
      zlib-dev

WORKDIR /app
# Use pip cache, build wheels once, then install from wheels (fast on rebuilds)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . /app
RUN uv sync --locked --no-dev

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
