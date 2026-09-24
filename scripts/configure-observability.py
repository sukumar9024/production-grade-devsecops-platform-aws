#!/usr/bin/env python3
"""Render private Alertmanager/Grafana configuration from the AWS app secret."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

spec = importlib.util.spec_from_file_location("fetch_secrets", Path(__file__).with_name("fetch-secrets.py"))
secrets_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secrets_module)


def render(root, secret):
    password = secret["grafana_admin_password"]
    webhook = secret["alert_webhook_url"]
    if len(password) < 16 or urlsplit(webhook).scheme != "https":
        raise ValueError("Require a strong Grafana password and HTTPS notification webhook")
    # JSON is valid YAML and safely escapes URL characters.
    config = {"route": {"receiver": "operations", "group_by": ["alertname", "instance"],
                        "group_wait": "30s", "group_interval": "5m", "repeat_interval": "4h"},
              "receivers": [{"name": "operations", "slack_configs": [
                  {"api_url": webhook, "channel": secret.get("alert_channel", "#secureops-alerts"),
                   "send_resolved": True}]}]}
    root = Path(root)
    # Container UID65534 reads this file; keep its containing directory private to ops.
    path = root / "monitoring/alertmanager.runtime.yml"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(config, output)
    os.chown(path, 65534, 65534)
    os.chmod(path, 0o600)
    secrets_module.write_env(root / ".env.observability", {"GF_SECURITY_ADMIN_PASSWORD": password})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    try:
        render(args.root, secrets_module.secret(os.environ["APP_SECRET_ARN"]))
    except (KeyError, ValueError, RuntimeError, OSError):
        raise SystemExit("Observability secret configuration failed; no secrets printed.")
    print("Private observability configuration written. Notification delivery is not yet tested.")
