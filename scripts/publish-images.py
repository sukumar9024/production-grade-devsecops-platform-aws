#!/usr/bin/env python3
"""Push the exact locally scanned images under immutable Git SHA tags."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--environment", choices=["dev", "staging", "prod"], required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"\d{12}\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com(?:\.cn)?", args.registry):
        parser.error("Invalid ECR registry")
    if not re.fullmatch(r"[a-f0-9]{40}", args.sha):
        parser.error("A full Git commit SHA is required")
    password = subprocess.run(["aws", "ecr", "get-login-password"], capture_output=True, text=True, check=True).stdout
    subprocess.run(["docker", "login", "--username", "AWS", "--password-stdin", args.registry], input=password, text=True, check=True)
    release = {"git_commit": args.sha, "pipeline_id": os.environ.get("BUILD_TAG", "manual"),
               "environment": "production" if args.environment == "prod" else args.environment}
    for component in ("backend", "frontend"):
        repository = f"secureops-{args.environment}-{component}"
        tagged = f"{args.registry}/{repository}:{args.sha}"
        subprocess.run(["docker", "tag", f"secureops-{component}:{args.sha}", tagged], check=True)
        subprocess.run(["docker", "push", tagged], check=True)
        digest = subprocess.run(["aws", "ecr", "describe-images", "--repository-name", repository,
            "--image-ids", f"imageTag={args.sha}", "--query", "imageDetails[0].imageDigest", "--output", "text"],
            capture_output=True, text=True, check=True).stdout.strip()
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
            raise RuntimeError("ECR returned no image digest")
        release[f"{component}_image"] = f"{args.registry}/{repository}@{digest}"
    Path("reports").mkdir(exist_ok=True)
    Path(f"reports/release-{args.environment}.json").write_text(json.dumps(release, indent=2) + "\n")


if __name__ == "__main__":
    main()
