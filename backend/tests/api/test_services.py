def test_service_lifecycle_and_permissions(
    client, project, admin_user, engineer_user, viewer_user, auth_headers
):
    engineer = auth_headers(engineer_user.username, "SecurePassword123!")
    viewer = auth_headers(viewer_user.username, "SecurePassword123!")
    admin = auth_headers(admin_user.username, "SecurePassword123!")
    payload = {
        "name": "backend-api",
        "project_id": str(project.id),
        "environment": "dev",
        "version": "1.0.0",
    }
    created = client.post("/api/v1/services", headers=engineer, json=payload)
    assert created.status_code == 201
    identifier = created.json()["id"]
    assert (
        client.post("/api/v1/services", headers=engineer, json=payload).status_code
        == 409
    )
    listing = client.get("/api/v1/services", headers=viewer)
    assert listing.status_code == 200
    assert listing.json()[0]["id"] == identifier
    assert (
        client.patch(
            f"/api/v1/services/{identifier}", headers=viewer, json={"status": "healthy"}
        ).status_code
        == 403
    )
    updated = client.patch(
        f"/api/v1/services/{identifier}", headers=engineer, json={"status": "healthy"}
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "healthy"
    assert (
        client.delete(f"/api/v1/services/{identifier}", headers=engineer).status_code
        == 403
    )
    assert (
        client.delete(f"/api/v1/services/{identifier}", headers=admin).status_code
        == 204
    )
    assert (
        client.get(f"/api/v1/services/{identifier}", headers=viewer).status_code == 404
    )
