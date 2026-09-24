def test_admin_can_create_project(
    client,
    admin_user,
    auth_headers,
):
    headers = auth_headers(
        admin_user.username,
        "SecurePassword123!",
    )

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "SecureOps Test",
            "description": ("Test project"),
        },
    )

    assert response.status_code == 201

    assert response.json()["name"] == "SecureOps Test"


def test_viewer_cannot_create_project(
    client,
    viewer_user,
    auth_headers,
):
    headers = auth_headers(
        viewer_user.username,
        "SecurePassword123!",
    )

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Forbidden Project"},
    )

    assert response.status_code == 403


def test_duplicate_project_returns_409(
    client,
    admin_user,
    auth_headers,
):
    headers = auth_headers(
        admin_user.username,
        "SecurePassword123!",
    )

    payload = {"name": "Duplicate Project"}

    first = client.post(
        "/api/v1/projects",
        headers=headers,
        json=payload,
    )

    second = client.post(
        "/api/v1/projects",
        headers=headers,
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409
