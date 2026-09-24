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

    assert response.json()["status"] == "pending"


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
        json={"status": "success"},
    )

    assert invalid.status_code == 409


def test_deployment_progression(client, service, engineer_user, auth_headers):
    headers = auth_headers(engineer_user.username, "SecurePassword123!")
    created = client.post(
        "/api/v1/deployments",
        headers=headers,
        json={
            "service_id": str(service.id),
            "version": "2.0.0",
            "git_commit": "1234567890abcdef",
        },
    )
    assert created.status_code == 201
    url = "/api/v1/deployments/" + created.json()["id"]
    assert (
        client.patch(url, headers=headers, json={"status": "failed"}).status_code == 422
    )
    assert (
        client.patch(url, headers=headers, json={"status": "in_progress"}).status_code
        == 200
    )
    success = client.patch(url, headers=headers, json={"status": "success"})
    assert success.status_code == 200
    assert success.json()["deployed_at"] is not None
    assert success.json()["failure_reason"] is None
    assert (
        client.patch(url, headers=headers, json={"status": "pending"}).status_code
        == 409
    )
    assert (
        client.patch(url, headers=headers, json={"status": "rolled_back"}).status_code
        == 200
    )
