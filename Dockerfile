# ============================================================
# Stage 1 : builder
# ============================================================

FROM python:3.12.10-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# ============================================================
# Stage 2 : runtime
# ============================================================

FROM python:3.12.10-slim AS runtime

ARG APP_VERSION=dev
ARG COMMIT_SHA=local

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    APP_VERSION=${APP_VERSION} \
    COMMIT_SHA=${COMMIT_SHA}

WORKDIR /app

# curl sert au HEALTHCHECK
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system \
        --gid appgroup \
        --create-home \
        appuser

COPY --from=builder /install /usr/local

COPY app ./app

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK \
    --interval=10s \
    --timeout=3s \
    --start-period=10s \
    --retries=3 \
    CMD curl --fail http://localhost:5000/health || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "30", \
     "app.main:app"]
