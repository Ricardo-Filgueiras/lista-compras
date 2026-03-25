FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.12-alpine

LABEL maintainer="ricardo-filgueiras"

# Instala o binário do uv a partir da imagem oficial
COPY --from=uv /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT="/venv"
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src /app
COPY scripts /app/scripts

RUN apk update && apk add --no-cache \
    postgresql-client \
    curl \
    build-base \
    python3-dev \
    libffi-dev \
    cairo \
    cairo-dev \
    pango \
    pango-dev \
    gdk-pixbuf \
    gdk-pixbuf-dev \
    shared-mime-info \
    jpeg-dev \
    zlib-dev \
    fontconfig \
    ttf-dejavu

RUN uv sync --frozen --no-dev --no-install-project && \
    adduser --disabled-password --no-create-home duser && \
    mkdir -p /data/web/static && \
    mkdir -p /data/web/media && \
    chown -R duser:duser /venv && \
    chown -R duser:duser /data/web/static && \
    chown -R duser:duser /data/web/media && \
    chmod -R 755 /data/web/static && \
    chmod -R 755 /data/web/media && \
    chmod -R +x /app/scripts

ENV PATH="/app/scripts:/venv/bin:$PATH"

USER duser

CMD ["sh", "/app/scripts/entrypoint_prod.sh"]