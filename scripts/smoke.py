#!/usr/bin/env python3
"""Verify frontend, dependency readiness, login and a database-backed API."""
import argparse
import json
import os
import urllib.error
import urllib.request


def request(base, path, payload=None, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base.rstrip("/") + path,
        data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
        if response.status != 200:
            raise RuntimeError(f"{path} returned {response.status}")
        return data


def check(base, require_auth=True):
    html = request(base, "/")
    if b"<html" not in html.lower():
        raise RuntimeError("Frontend did not return HTML")
    request(base, "/health/live")
    health = json.loads(request(base, "/health/ready"))
    if health.get("status") != "ready":
        raise RuntimeError("Required dependencies are not ready")
    if require_auth:
        identity = os.environ["SMOKE_IDENTITY"]
        password = os.environ["SMOKE_PASSWORD"]
        tokens = json.loads(request(base, "/api/v1/auth/login", {"identity": identity, "password": password}))
        try:
            request(base, "/api/v1/auth/me", token=tokens["access_token"])
            request(base, "/api/v1/projects", token=tokens["access_token"])
        finally:
            # Logout returns 204; use its own request, preserving strict smoke checks above.
            req = urllib.request.Request(base.rstrip("/") + "/api/v1/auth/logout",
                data=json.dumps({"refresh_token": tokens["refresh_token"]}).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {tokens['access_token']}"})
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status not in {200, 204}:
                    raise RuntimeError("Logout failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--health-only", action="store_true", help="Local diagnostics only, not a release gate")
    args = parser.parse_args()
    try:
        check(args.url, not args.health_only)
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f"Smoke check failed ({type(error).__name__}); credentials and bodies omitted.")
    print("Smoke checks passed" + (" (health only)" if args.health_only else " (including authentication and database API)"))
