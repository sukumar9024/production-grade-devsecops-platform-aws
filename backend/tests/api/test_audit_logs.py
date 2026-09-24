from sqlalchemy import select

from app.models.audit_log import AuditLog


def test_project_mutations_create_correlated_audit_events(
    client, admin_user, auth_headers, db_session
):
    headers = auth_headers(admin_user.username, "SecurePassword123!")
    headers["X-Request-ID"] = "audit-project-creation"
    response = client.post(
        "/api/v1/projects", headers=headers, json={"name": "Audited project"}
    )
    assert response.status_code == 201
    identifier = response.json()["id"]
    event = db_session.scalar(
        select(AuditLog).where(AuditLog.action == "project.created")
    )
    assert event is not None
    assert event.user_id == admin_user.id
    assert event.resource_id == identifier
    assert event.request_id == "audit-project-creation"
    assert (
        client.patch(
            f"/api/v1/projects/{identifier}",
            headers=headers,
            json={"name": "Updated project"},
        ).status_code
        == 200
    )
    assert (
        client.delete(f"/api/v1/projects/{identifier}", headers=headers).status_code
        == 204
    )
    actions = set(db_session.scalars(select(AuditLog.action)).all())
    assert {"project.created", "project.updated", "project.deleted"} <= actions


def test_auth_audited_without_secrets(client, viewer_user, db_session):
    client.post(
        "/api/v1/auth/login",
        json={"identity": viewer_user.username, "password": "wrongpassword"},
    )
    result = client.post(
        "/api/v1/auth/login",
        json={"identity": viewer_user.username, "password": "SecurePassword123!"},
    )
    client.post(
        "/api/v1/auth/logout", json={"refresh_token": result.json()["refresh_token"]}
    )
    events = list(db_session.scalars(select(AuditLog)).all())
    assert {"auth.login.failure", "auth.login.success", "auth.logout"} <= {
        event.action for event in events
    }
    assert "password" not in str([event.details for event in events]).lower()


def test_audit_logs_admin_only(client, viewer_user, auth_headers):
    response = client.get(
        "/api/v1/audit-logs",
        headers=auth_headers(viewer_user.username, "SecurePassword123!"),
    )
    assert response.status_code == 403
