#!/usr/bin/env python3
"""EC2-side deployment wrapper. Secret values never transit the Ansible controller."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root", default="/opt/secureops")
    parser.add_argument("--observability", action="store_true")
    args, _ = parser.parse_known_args()
    root = Path(args.root).resolve()
    env = dict(os.environ)
    for line in (root / ".env.aws").read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            env[key] = value
    if args.observability:
        if not env.get("OPENSEARCH_HOST"):
            raise ValueError("A managed OpenSearch endpoint is required")
        subprocess.run([sys.executable, str(root / "scripts/configure-observability.py"),
            "--root", str(root)], env=env, cwd=root, check=True)
        subprocess.run(["docker", "compose", "-p", "secureops-observability", "-f",
            str(root / "compose.observability.prod.yaml"), "up", "-d"],
            env=env, cwd=root, check=True)
        return
    # JSON is kept only in this process; never put secrets on a command line.
    result = subprocess.run(["aws", "secretsmanager", "get-secret-value", "--secret-id",
        env["APP_SECRET_ARN"], "--query", "SecretString", "--output", "text"],
        env=env, text=True, capture_output=True, check=True)
    app = json.loads(result.stdout)
    env["SMOKE_IDENTITY"] = app["smoke_identity"]
    env["SMOKE_PASSWORD"] = app["smoke_password"]
    subprocess.run([sys.executable, str(root / "scripts/fetch-secrets.py"), "--output",
        str(root / ".env.runtime")], cwd=root, env=env, check=True)
    result = subprocess.run(["aws", "ecr", "get-login-password"],
        env=env, text=True, capture_output=True, check=True)
    subprocess.run(["docker", "login", "--username", "AWS", "--password-stdin",
        env["ECR_REGISTRY"]], input=result.stdout, env=env, text=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run([sys.executable, str(root / "scripts/deploy.py"), *sys.argv[1:]],
        env=env, cwd=root, check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Avoid printing subprocess stdout/stderr, parsed JSON or configuration.
        raise SystemExit(f"Deployment failed ({type(error).__name__}); inspect the host release status.") from None
