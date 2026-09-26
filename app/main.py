import os
import time

import redis
from flask import Flask, Response, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Nombre total de requetes HTTP recues",
    ["endpoint", "code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duree des requetes HTTP en secondes",
    ["route"],
)

APP_INFO = Gauge(
    "app_info",
    "Informations sur la version actuellement deployee",
    ["version", "sha"],
)

VERSION = os.getenv("APP_VERSION", "dev")
COMMIT_SHA = os.getenv("COMMIT_SHA", "local")

APP_INFO.labels(
    version=VERSION,
    sha=COMMIT_SHA,
).set(1)


def create_app(redis_client=None):
    app = Flask(__name__)

    if redis_client is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

    app.config["REDIS_CLIENT"] = redis_client

    @app.before_request
    def start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def record_metrics(response):
        endpoint = request.endpoint or "unknown"
        route = request.url_rule.rule if request.url_rule else request.path

        REQUEST_COUNT.labels(
            endpoint=endpoint,
            code=str(response.status_code),
        ).inc()

        start_time = getattr(request, "_start_time", None)

        if start_time is not None:
            duration = time.perf_counter() - start_time
            REQUEST_LATENCY.labels(route=route).observe(duration)

        return response

    @app.get("/")
    def index():
        visits = app.config["REDIS_CLIENT"].incr("visits")

        return jsonify(
            {
                "message": "Evaluation DevOps ESIEA",
                "status": "ok",
                "visits": visits,
                "version": VERSION,
                "sha": COMMIT_SHA,
            }
        )

    @app.get("/health")
    def health():
        try:
            redis_ok = app.config["REDIS_CLIENT"].ping()

            if not redis_ok:
                raise RuntimeError("Redis ping failed")

            return jsonify(
                {
                    "status": "healthy",
                    "redis": "ok",
                    "version": VERSION,
                    "sha": COMMIT_SHA,
                }
            ), 200

        except Exception:
            return jsonify(
                {
                    "status": "unhealthy",
                    "redis": "error",
                    "version": VERSION,
                    "sha": COMMIT_SHA,
                }
            ), 503

    @app.get("/metrics")
    def metrics():
        return Response(
            generate_latest(),
            mimetype=CONTENT_TYPE_LATEST,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
