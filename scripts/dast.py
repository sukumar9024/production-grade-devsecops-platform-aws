#!/usr/bin/env python3
"""Run baseline and authenticated API DAST only against an explicit staging URL."""
import argparse
import html
import json
import os
from pathlib import Path
import subprocess
import re
from urllib.parse import urlsplit


def gate(report):
    if not isinstance(report.get("site"), list) or not report["site"]:
        raise ValueError("ZAP report contains no scanned site; release blocked")
    alerts = [alert for site in report.get("site", []) for alert in site.get("alerts", [])]
    return [alert for alert in alerts if int(alert.get("riskcode", 0)) >= 3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("staging_url")
    args = parser.parse_args()
    url = args.staging_url.rstrip("/")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        parser.error("An explicit HTTPS staging URL is required")
    if not all(os.environ.get(key) for key in ("SMOKE_IDENTITY", "SMOKE_PASSWORD")):
        parser.error("Staging smoke credentials are required")
    root = Path(__file__).resolve().parents[1]
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    env = dict(os.environ, DAST_URL=url)
    # This writeable output directory is solely for disposable ZAP reports.
    reports.chmod(0o777)
    try:
        for mode, target, report in [("zap-baseline.py", url, "zap-baseline"),
                                     ("zap-api-scan.py", url + "/api/v1/openapi.json", "zap-api")]:
            command = ["docker", "run", "--rm", "-v", f"{reports}:/zap/wrk:rw",
                "-v", f"{root / 'security/zap-hook.py'}:/zap/zap-hook.py:ro",
                "-e", "SMOKE_IDENTITY", "-e", "SMOKE_PASSWORD", "-e", "DAST_URL",
                "ghcr.io/zaproxy/zaproxy:2.17.0", mode, "-t", target,
                "-J", report + ".json", "-r", report + ".html", "--hook", "/zap/zap-hook.py"]
            if mode == "zap-api-scan.py":
                command += ["-f", "openapi", "-S"]  # Safe scan excludes active data-changing attacks.
            # URL is validated HTTPS; it is one argv element after -t, never shell code.
            # The bounded scan completes before the default 15-minute access token expires.
            result = subprocess.run(command, env=env, timeout=600)  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args
            path = reports / (report + ".json")
            if result.returncode not in {0, 1, 2} or not path.exists():
                raise SystemExit("ZAP failed to produce a report; release blocked")
            data = json.loads(path.read_text())
            if gate(data):
                raise SystemExit("ZAP reported high-risk vulnerabilities; release blocked")
    finally:
        # ZAP evidence may contain authenticated request headers or login bodies.
        # Keep useful findings while removing credentials before Jenkins archives them.
        password = os.environ["SMOKE_PASSWORD"]
        for path in reports.glob("zap-*"):
            if path.suffix not in {".json", ".html"}:
                continue
            content = path.read_text()
            for sensitive in {password, html.escape(password), json.dumps(password)[1:-1]}:
                content = content.replace(sensitive, "[REDACTED]")
            content = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED-JWT]", content)
            path.write_text(content)
        reports.chmod(0o755)


if __name__ == "__main__":
    main()
