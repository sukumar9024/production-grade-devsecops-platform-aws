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
            "description": (
                "Health check failed."
            ),
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