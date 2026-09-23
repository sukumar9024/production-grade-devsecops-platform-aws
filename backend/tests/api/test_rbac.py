def test_admin_can_list_users(
    client,
    admin_user,
    auth_headers,
):
    headers = auth_headers(
        admin_user.username,
        "SecurePassword123!",
    )

    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code == 200


def test_viewer_cannot_list_users(
    client,
    viewer_user,
    auth_headers,
):
    headers = auth_headers(
        viewer_user.username,
        "SecurePassword123!",
    )

    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code == 403


def test_engineer_cannot_list_users(
    client,
    engineer_user,
    auth_headers,
):
    headers = auth_headers(
        engineer_user.username,
        "SecurePassword123!",
    )

    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code == 403