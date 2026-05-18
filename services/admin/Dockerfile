FROM python:3.12-slim as base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    UV_VERSION=0.6.8 \
    UV_SYSTEM_PYTHON=1

RUN pip install "uv==$UV_VERSION"

COPY pyproject.toml uv.lock ./

FROM base as test
RUN uv sync --extra dev --no-install-project
COPY . .
CMD ["pytest"]

FROM base as prod
RUN uv sync --extra dev --no-install-project
COPY . .
CMD [".venv/bin/python", "start.py"]
