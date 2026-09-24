def test_register_user(
    client,
    roles,
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == ("newuser@example.com")

    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_registration_rejected(
    client,
    roles,
):
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicate",
        "password": "SecurePassword123!",
    }

    first = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_success(
    client,
    viewer_user,
):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "identity": viewer_user.email,
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(
    client,
    viewer_user,
):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "identity": viewer_user.email,
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token(
    client,
):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_refresh_token_flow(
    client,
    viewer_user,
):
    login = client.post(
        "/api/v1/auth/login",
        json={
            "identity": viewer_user.email,
            "password": "SecurePassword123!",
        },
    )

    refresh_token = login.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_logout_revokes_refresh_token(
    client,
    viewer_user,
):
    login = client.post(
        "/api/v1/auth/login",
        json={
            "identity": viewer_user.email,
            "password": "SecurePassword123!",
        },
    )

    tokens = login.json()

    headers = {"Authorization": (f"Bearer {tokens['access_token']}")}

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": (tokens["refresh_token"])},
        headers=headers,
    )

    assert logout.status_code == 204

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": (tokens["refresh_token"])},
    )

    assert refresh.status_code == 401
