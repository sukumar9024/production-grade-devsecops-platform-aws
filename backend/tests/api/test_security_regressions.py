import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.core.metrics import LOGIN_FAILURES_TOTAL
from app.core.security import create_access_token
from app.main import create_application
from app.models.enums import UserStatus
from app.models.refresh_token import RefreshToken


def login(client, user):
    response = client.post(
        "/api/v1/auth/login",
        json={"identity": user.username, "password": "SecurePassword123!"},
    )
    assert response.status_code == 200
    return response.json()


def test_disabled_user_cannot_refresh(client, viewer_user, db_session):
    tokens = login(client, viewer_user)
    viewer_user.status = UserStatus.DISABLED
    db_session.commit()
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 403


def test_refresh_rotates_and_rejects_replay(client, viewer_user):
    tokens = login(client, viewer_user)
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    assert response.json()["refresh_token"] != tokens["refresh_token"]
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )


def test_refresh_checks_stored_expiry(client, viewer_user, db_session):
    tokens = login(client, viewer_user)
    stored = db_session.scalar(select(RefreshToken))
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )


def test_refresh_checks_token_owner(client, viewer_user, admin_user, db_session):
    tokens = login(client, viewer_user)
    stored = db_session.scalar(select(RefreshToken))
    stored.user_id = admin_user.id
    db_session.commit()
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )


def test_failed_login_counted(client, viewer_user):
    before = LOGIN_FAILURES_TOTAL._value.get()
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"identity": viewer_user.username, "password": "invalid"},
        ).status_code
        == 401
    )
    assert LOGIN_FAILURES_TOTAL._value.get() == before + 1


@pytest.mark.parametrize("claim", ["access", "refresh"])
def test_expired_tokens_rejected(client, viewer_user, claim):
    token = jwt.encode(
        {
            "sub": str(viewer_user.id),
            "type": claim,
            "jti": str(uuid.uuid4()),
            "iat": datetime.now(UTC) - timedelta(minutes=10),
            "exp": datetime.now(UTC) - timedelta(seconds=1),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    if claim == "access":
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
    else:
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 401


def test_claimed_admin_role_does_not_override_database(client, viewer_user):
    token = create_access_token(str(viewer_user.id), "Admin")
    assert (
        client.get(
            "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 403
    )


def test_access_token_cannot_be_used_to_refresh(client, viewer_user):
    token = create_access_token(str(viewer_user.id), "Viewer")
    assert (
        client.post("/api/v1/auth/refresh", json={"refresh_token": token}).status_code
        == 401
    )


def test_disabled_user_access_rejected(client, viewer_user, db_session):
    tokens = login(client, viewer_user)
    viewer_user.status = UserStatus.DISABLED
    db_session.commit()
    assert (
        client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        ).status_code
        == 403
    )


def test_validation_response_does_not_echo_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "bad", "username": "bad", "password": "secret"},
    )
    assert response.status_code == 422
    assert "secret" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_unhandled_error_has_correlation_id_without_details():
    application = create_application()

    @application.get("/test-crash")
    def crash():
        raise RuntimeError("sensitive database password")

    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/test-crash", headers={"X-Request-ID": "crash-test"})
    assert response.status_code == 500
    assert (
        response.json()["request_id"]
        == response.headers["X-Request-ID"]
        == "crash-test"
    )
    assert "sensitive" not in response.text


def test_cors_preflight(client):
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_readiness_includes_redis(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["redis"]["status"] == "healthy"


def test_redis_failure_makes_not_ready(client, monkeypatch):
    from redis import ConnectionError, Redis

    def unavailable(self):
        raise ConnectionError("secret must not be exposed")

    monkeypatch.setattr(Redis, "ping", unavailable)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["redis"]["status"] == "unhealthy"
    assert "secret" not in response.text


def test_untrusted_forwarded_ip_is_not_used():
    from starlette.requests import Request

    from app.core.request_context import get_client_ip

    request = Request(
        {
            "type": "http",
            "headers": [(b"x-forwarded-for", b"forged-address")],
            "client": ("127.0.0.1", 1234),
        }
    )
    assert get_client_ip(request) == "127.0.0.1"


def test_unsafe_correlation_id_is_replaced(client):
    response = client.get(
        "/health/live", headers={"X-Request-ID": "invalid id with spaces"}
    )
    uuid.UUID(response.headers["X-Request-ID"])


def test_empty_project_name_rejected(client, admin_user, auth_headers):
    headers = auth_headers(admin_user.username, "SecurePassword123!")
    assert (
        client.post(
            "/api/v1/projects", headers=headers, json={"name": "   "}
        ).status_code
        == 422
    )


def test_503_health_error_has_request_id(client, monkeypatch):
    from redis import ConnectionError, Redis

    def unavailable(self):
        raise ConnectionError("unavailable")

    monkeypatch.setattr(Redis, "ping", unavailable)
    response = client.get(
        "/health/ready", headers={"X-Request-ID": "dependency-failure"}
    )
    assert response.status_code == 503
    assert response.json()["request_id"] == "dependency-failure"


def test_log_and_metric_route_includes_api_prefix(client, caplog):
    from app.core.metrics import HTTP_REQUESTS_TOTAL

    before = HTTP_REQUESTS_TOTAL.labels(
        method="GET", endpoint="/api/v1/projects/{project_id}", status_code="401"
    )._value.get()
    response = client.get("/api/v1/projects/" + str(uuid.uuid4()))
    assert response.status_code == 401
    assert (
        HTTP_REQUESTS_TOTAL.labels(
            method="GET", endpoint="/api/v1/projects/{project_id}", status_code="401"
        )._value.get()
        == before + 1
    )
    assert any(
        getattr(record, "endpoint", "") == "/api/v1/projects/{project_id}"
        for record in caplog.records
    )


def test_admin_can_change_role_and_status(
    client, admin_user, viewer_user, auth_headers
):
    headers = auth_headers(admin_user.username, "SecurePassword123!")
    role = client.patch(
        f"/api/v1/users/{viewer_user.id}/role",
        headers=headers,
        json={"role": "Engineer"},
    )
    assert role.status_code == 200
    assert role.json()["role"]["name"] == "Engineer"
    status = client.patch(
        f"/api/v1/users/{viewer_user.id}/status",
        headers=headers,
        json={"status": "disabled"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "disabled"


def test_admin_cannot_demote_or_disable_self(client, admin_user, auth_headers):
    headers = auth_headers(admin_user.username, "SecurePassword123!")
    assert (
        client.patch(
            f"/api/v1/users/{admin_user.id}/role",
            headers=headers,
            json={"role": "Viewer"},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/v1/users/{admin_user.id}/status",
            headers=headers,
            json={"status": "disabled"},
        ).status_code
        == 400
    )
