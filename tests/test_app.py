from unittest.mock import Mock

from app.main import create_app


def build_client():
    fake_redis = Mock()
    fake_redis.ping.return_value = True
    fake_redis.incr.return_value = 1

    app = create_app(redis_client=fake_redis)
    app.config["TESTING"] = True

    return app.test_client(), fake_redis


def test_index_returns_expected_response():
    client, fake_redis = build_client()

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Evaluation DevOps ESIEA"
    assert data["status"] == "ok"
    assert data["visits"] == 1

    fake_redis.incr.assert_called_once_with("visits")


def test_health_checks_redis():
    client, fake_redis = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
    assert response.get_json()["redis"] == "ok"

    fake_redis.ping.assert_called_once()


def test_health_returns_503_when_redis_fails():
    client, fake_redis = build_client()

    fake_redis.ping.side_effect = ConnectionError("Redis unavailable")

    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json()["status"] == "unhealthy"
    assert response.get_json()["redis"] == "error"


def test_metrics_are_exposed():
    client, _ = build_client()

    client.get("/")
    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "app_info" in body
