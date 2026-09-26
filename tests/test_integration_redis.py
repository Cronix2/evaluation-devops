import os

import redis

from app.main import create_app


def test_application_uses_real_redis():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    real_redis = redis.Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
    )

    real_redis.delete("visits")

    app = create_app(redis_client=real_redis)
    app.config["TESTING"] = True

    client = app.test_client()

    first_response = client.get("/")
    second_response = client.get("/")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.get_json()
    second_data = second_response.get_json()

    assert first_data["visits"] == 1
    assert second_data["visits"] == 2

    assert real_redis.get("visits") == "2"

    health_response = client.get("/health")

    assert health_response.status_code == 200
    assert health_response.get_json()["redis"] == "ok"
