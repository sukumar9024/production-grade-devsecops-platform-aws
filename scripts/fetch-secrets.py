#!/usr/bin/env python3
"""Fetch AWS secrets into a private Docker env file; never print secret values."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import quote


def secret(arn):
    result = subprocess.run(
        ["aws", "secretsmanager", "get-secret-value", "--secret-id", arn,
         "--query", "SecretString", "--output", "text"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError("Secrets Manager retrieval failed; check identity and secret permissions.")
    return json.loads(result.stdout)


def build_values(app, database, redis, environment):
    if environment not in {"dev", "staging", "production"}:
        raise ValueError("ENVIRONMENT must be dev, staging or production")
    if len(app.get("jwt_secret", "")) < 32:
        raise ValueError("App secret requires a jwt_secret of at least 32 characters")
    for value in [*app.values(), *database.values(), *redis.values()]:
        if isinstance(value, str) and any(char in value for char in "\r\n\x00"):
            raise ValueError("Multiline secret values are not supported")
    host = os.environ["DATABASE_HOST"]
    dbname = os.environ.get("DATABASE_NAME", "secureops")
    redis_host = os.environ["REDIS_HOST"]
    ca = "/etc/ssl/certs/rds-global-bundle.pem"
    return {
        "ENVIRONMENT": environment,
        "DEBUG": "false",
        "JWT_SECRET": app["jwt_secret"],
        "DATABASE_URL": f"postgresql+psycopg://{quote(database['username'], safe='')}:{quote(database['password'], safe='')}@{host}:5432/{quote(dbname, safe='')}?sslmode=verify-full&sslrootcert={ca}",
        "REDIS_URL": f"rediss://:{quote(redis['password'], safe='')}@{redis_host}:6379/0?ssl_cert_reqs=required",
        "CORS_ORIGINS": os.environ.get("CORS_ORIGINS", ""),
        "AWS_REGION": os.environ["AWS_REGION"],
        "S3_BUCKET": os.environ.get("S3_BUCKET", ""),
    }


def write_env(path, values):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".secrets-")
    try:
        with os.fdopen(fd, "w") as output:
            for key, value in values.items():
                if any(char in str(value) for char in "\r\n\x00"):
                    raise ValueError("Invalid environment value")
                output.write(f"{key}={value}\n")
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=".env.runtime")
    args = parser.parse_args()
    try:
        values = build_values(secret(os.environ["APP_SECRET_ARN"]),
                              secret(os.environ["DATABASE_SECRET_ARN"]),
                              secret(os.environ["REDIS_SECRET_ARN"]),
                              os.environ["ENVIRONMENT"])
        write_env(args.output, values)
    except (KeyError, ValueError, RuntimeError) as error:
        raise SystemExit(f"Secret configuration failed: {type(error).__name__}. No values were printed.")
    print("Runtime configuration written with mode 0600.")


if __name__ == "__main__":
    main()
