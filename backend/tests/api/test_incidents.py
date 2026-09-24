def test_create_incident(
    client,
    engineer_user,
    service,
    auth_headers,
):
    headers = auth_headers(
        engineer_user.username,
        "SecurePassword123!",
    )

    response = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "service_id": str(service.id),
            "title": "Backend unavailable",
            "description": ("Health check failed."),
            "severity": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "open"
    assert data["severity"] == "high"
    assert data["resolved_at"] is None


def test_viewer_cannot_read_audit_logs(
    client,
    viewer_user,
    auth_headers,
):
    headers = auth_headers(
        viewer_user.username,
        "SecurePassword123!",
    )

    response = client.get(
        "/api/v1/audit-logs",
        headers=headers,
    )

    assert response.status_code == 403


def test_incident_resolution_records_timestamp(
    client, service, engineer_user, auth_headers
):
    headers = auth_headers(engineer_user.username, "SecurePassword123!")
    created = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "service_id": str(service.id),
            "title": "Backend unavailable",
            "description": "Backend failed readiness probes",
            "severity": "critical",
        },
    )
    assert created.status_code == 201
    url = "/api/v1/incidents/" + created.json()["id"]
    resolved = client.patch(url, headers=headers, json={"status": "resolved"})
    assert resolved.status_code == 200
    assert resolved.json()["resolved_at"] is not None
    assert (
        client.patch(url, headers=headers, json={"status": "closed"}).status_code == 200
    )
    assert (
        client.patch(url, headers=headers, json={"status": "open"}).status_code == 409
    )
