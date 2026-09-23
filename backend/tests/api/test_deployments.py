def test_create_deployment(
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
        "/api/v1/deployments",
        headers=headers,
        json={
            "service_id": str(service.id),
            "version": "1.1.0",
            "git_commit": "123456789abcdef",
            "pipeline_id": "test-1",
        },
    )

    assert response.status_code == 201

    assert response.json()[
        "status"
    ] == "pending"

def test_invalid_deployment_transition(
    client,
    engineer_user,
    service,
    auth_headers,
):
    headers = auth_headers(
        engineer_user.username,
        "SecurePassword123!",
    )

    created = client.post(
        "/api/v1/deployments",
        headers=headers,
        json={
            "service_id": str(service.id),
            "version": "1.1.0",
            "git_commit": "123456789abcdef",
        },
    )

    deployment_id = created.json()["id"]

    failed = client.patch(
        f"/api/v1/deployments/{deployment_id}",
        headers=headers,
        json={
            "status": "failed",
            "failure_reason": "Test failure",
        },
    )

    assert failed.status_code == 200

    invalid = client.patch(
        f"/api/v1/deployments/{deployment_id}",
        headers=headers,
        json={
            "status": "success"
        },
    )

    assert invalid.status_code == 409