#!/usr/bin/env python3
"""Convert Terraform JSON outputs into private, nonsecret Ansible variables."""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit


def build_config(outputs, region, domain):
    if not region or not domain or "*" in region + domain:
        raise ValueError("Replace the region/domain placeholders first")
    parsed = urlsplit("https://" + domain)
    if parsed.hostname != domain or parsed.path or parsed.query or parsed.fragment:
        raise ValueError("Supply the DNS hostname only, without a scheme/path")
    values = {name: item["value"] for name, item in outputs.items()}
    mapping = {
        "app_secret_arn": "app_secret_arn",
        "database_secret_arn": "database_secret_arn",
        "database_host": "database_endpoint",
        "redis_secret_arn": "redis_secret_arn",
        "redis_host": "redis_endpoint",
        "application_bucket": "application_bucket",
        "target_group_arn": "target_group_arn",
        "log_group_name": "log_group_name",
    }
    result = {target: values[source] for target, source in mapping.items()}
    if any(not isinstance(value, str) or not value or "*" in value for value in result.values()):
        raise ValueError("Terraform outputs contain missing or placeholder resource values")
    repos = values["ecr_repository_urls"]
    backend_registry, backend_repo = repos["backend"].split("/", 1)
    frontend_registry, frontend_repo = repos["frontend"].split("/", 1)
    if backend_registry != frontend_registry:
        raise ValueError("Backend and frontend registries must match")
    result.update(aws_region=region, ecr_registry=backend_registry,
                  backend_repository=backend_repo, frontend_repository=frontend_repo,
                  opensearch_endpoint=values.get("opensearch_endpoint", ""),
                  cors_origins="https://" + domain)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_config(json.loads(args.outputs.read_text()), args.region, args.domain)
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Refuse overwrite so a previous environment's config cannot be lost silently.
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print("Private Ansible runtime variables written; no secret values are included.")


if __name__ == "__main__":
    main()
