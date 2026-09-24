#!/usr/bin/env python3
"""Create a disposable CI user and exercise the built images through the gateway."""
import json
import os
import secrets
import urllib.request
import uuid

from smoke import check


def main():
    base = "http://127.0.0.1:8080"
    username = "ci_" + uuid.uuid4().hex[:16]
    password = secrets.token_urlsafe(32)
    request = urllib.request.Request(
        base + "/api/v1/auth/register",
        data=json.dumps({"username": username, "email": username + "@example.com",
                         "password": password, "full_name": "Disposable CI account"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 201:
            raise RuntimeError("CI account registration failed")
    os.environ["SMOKE_IDENTITY"] = username
    os.environ["SMOKE_PASSWORD"] = password
    check(base)
    print("Built-container smoke passed: gateway, UI, readiness, registration, login, API and logout.")


if __name__ == "__main__":
    main()
