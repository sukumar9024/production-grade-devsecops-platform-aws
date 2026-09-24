def test_liveness(
    client,
):
    response = client.get("/health/live")

    assert response.status_code == 200

    assert response.json()["status"] == "alive"


def test_readiness(
    client,
):
    response = client.get("/health/ready")

    assert response.status_code == 200

    assert response.json()["status"] == "ready"

    assert response.json()["database"]["status"] == "healthy"


def test_health_response_contains_request_id(
    client,
):
    response = client.get("/health/live")

    assert "X-Request-ID" in response.headers


def test_supplied_request_id_is_returned(
    client,
):
    response = client.get(
        "/health/live",
        headers={"X-Request-ID": ("test-correlation-id")},
    )

    assert response.headers["X-Request-ID"] == "test-correlation-id"


def test_request_id_is_generated(
    client,
):
    response = client.get("/health/live")

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) > 0


def test_404_contains_request_id(
    client,
):
    response = client.get(
        "/does-not-exist",
        headers={"X-Request-ID": "error-test"},
    )

    assert response.status_code == 404

    assert response.json()["request_id"] == "error-test"


def test_database_outage_returns_503_without_affecting_liveness(client, monkeypatch):
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session

    def unavailable(*args, **kwargs):
        raise OperationalError("query", {}, Exception("connection secret"))

    monkeypatch.setattr(Session, "execute", unavailable)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["database"]["status"] == "unhealthy"
    assert "secret" not in response.text
    assert client.get("/health/live").status_code == 200


def test_openapi_is_available_under_versioned_proxy_prefix(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/auth/login" in schema["paths"]
    assert "/api/v1/services" in schema["paths"]
    assert client.get("/api/v1/docs").status_code == 200
