#!/usr/bin/env python3
"""Create local-only random credentials without replacing existing configuration."""
import os
import secrets
from pathlib import Path


def main():
    path = Path(__file__).resolve().parents[1] / ".env"
    values = {key: secrets.token_hex(32) for key in (
        "POSTGRES_PASSWORD", "REDIS_PASSWORD", "JWT_SECRET", "GRAFANA_ADMIN_PASSWORD"
    )}
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SystemExit(".env already exists; it was not changed.")
    with os.fdopen(fd, "w") as output:
        output.write("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
    print("Created .env with fresh local credentials (mode 0600).")


if __name__ == "__main__":
    main()
