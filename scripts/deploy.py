#!/usr/bin/env python3
"""Serialized blue/green deployment on a Linux EC2 host. Requires Python 3.10+."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke import check as smoke_check

IMAGE = re.compile(r"^[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}$")


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def atomic_write(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as output:
            output.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Deployer:
    def __init__(self, root, runner=run, checker=smoke_check):
        self.root = Path(root).resolve()
        self.state = self.root / ".runtime"
        self.state.mkdir(mode=0o700, exist_ok=True)
        self.runner, self.checker = runner, checker

    def load(self, name):
        path = self.state / f"{name}.json"
        return json.loads(path.read_text()) if path.exists() else None

    def save(self, name, data):
        atomic_write(self.state / f"{name}.json", json.dumps(data, indent=2) + "\n")

    def release(self, slot, git_sha, pipeline_id, environment, backend, frontend):
        if slot not in {"blue", "green"} or environment not in {"dev", "staging", "production"}:
            raise ValueError("Invalid slot or environment")
        if not re.fullmatch(r"[a-f0-9]{40}", git_sha):
            raise ValueError("A full Git SHA is required")
        if not all(IMAGE.fullmatch(image) for image in (backend, frontend)):
            raise ValueError("Both images must be pinned to sha256 digests")
        return {"slot": slot, "git_commit": git_sha, "version": git_sha,
                "pipeline_id": pipeline_id, "environment": environment,
                "backend_image": backend, "frontend_image": frontend,
                "deployed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "app_port": 18080 if slot == "blue" else 18081,
                "metrics_port": 18000 if slot == "blue" else 18001}

    def compose(self, release, *arguments):
        env = dict(os.environ, BACKEND_IMAGE=release["backend_image"],
            FRONTEND_IMAGE=release["frontend_image"], APP_PORT=str(release["app_port"]),
            METRICS_PORT=str(release["metrics_port"]),
            RUNTIME_ENV_FILE=str(self.state / f"env-{release['git_commit']}"))
        self.runner(["docker", "compose", "-p", f"secureops-{release['slot']}",
                     "-f", str(self.root / "compose.prod.yaml"), *arguments], cwd=self.root, env=env)

    def switch(self, release):
        atomic_write(self.root / "docker/gateway/upstream.conf",
            f"upstream active_slot {{ server 127.0.0.1:{release['app_port']}; keepalive 16; }}\n", 0o644)
        self.runner(["docker", "compose", "-p", "secureops-gateway", "-f",
            str(self.root / "compose.gateway.yaml"), "up", "-d"], cwd=self.root)
        self.runner(["docker", "exec", "secureops-gateway", "nginx", "-t"])
        self.runner(["docker", "exec", "secureops-gateway", "nginx", "-s", "reload"])
        # Prometheus file discovery follows the active slot, not the standby.
        atomic_write(self.root / "monitoring/targets/backend.json", json.dumps([
            {"targets": [f"127.0.0.1:{release['metrics_port']}"],
             "labels": {"environment": release["environment"], "version": release["git_commit"]}}
        ]) + "\n", 0o644)

    def verify_alb(self):
        target_group, instance = os.getenv("TARGET_GROUP_ARN"), os.getenv("APP_INSTANCE_ID")
        if target_group and instance:
            self.runner(["aws", "elbv2", "wait", "target-in-service", "--target-group-arn",
                target_group, "--targets", f"Id={instance},Port=8080"])

    def record_metrics(self, release, success):
        value = 1 if success else 0
        # Only validated hex SHA is used as a label; never arbitrary CLI input.
        atomic_write(self.root / "monitoring/textfile/deployment.prom",
            '# HELP secureops_deployment_success Whether the last deployment succeeded.\n'
            '# TYPE secureops_deployment_success gauge\n'
            f'secureops_deployment_success {value}\n'
            '# HELP secureops_deployment_timestamp_seconds Last deployment attempt time.\n'
            '# TYPE secureops_deployment_timestamp_seconds gauge\n'
            f'secureops_deployment_timestamp_seconds {time.time()}\n'
            '# HELP secureops_release_info Current release metadata.\n'
            '# TYPE secureops_release_info gauge\n'
            f'secureops_release_info{{version="{release["git_commit"]}"}} 1\n', 0o644)

    def deploy(self, candidate):
        current = self.load("current")
        if current and current["slot"] == candidate["slot"]:
            raise ValueError("Candidate must use the inactive slot")
        switched = False
        atomic_write(self.state / f"env-{candidate['git_commit']}", (self.root / ".env.runtime").read_text())
        try:
            self.compose(candidate, "pull")
            # Migrations must be backward compatible with the currently serving version.
            self.compose(candidate, "run", "--rm", "--no-deps", "backend", "alembic", "upgrade", "head")
            self.compose(candidate, "run", "--rm", "--no-deps", "backend", "python", "-m", "scripts.seed_roles")
            self.compose(candidate, "up", "-d", "--wait", "--wait-timeout", "120")
            self.checker(f"http://127.0.0.1:{candidate['app_port']}")
            switched = True  # Even a failed reload may have changed the gateway file.
            self.switch(candidate)
            self.checker("http://127.0.0.1:8080")
            self.verify_alb()
            if current:
                self.save("previous", current)
            self.save("current", candidate)
            self.save("last-attempt", dict(candidate, status="success"))
            self.record_metrics(candidate, True)
        except Exception:
            self.save("last-attempt", dict(candidate, status="failed"))
            rollback_failed = False
            if switched and current:
                try:
                    self.switch(current)
                    self.checker("http://127.0.0.1:8080")
                    self.verify_alb()
                except Exception:
                    rollback_failed = True
            elif switched:
                # First release has no safe fallback; stop the gateway.
                self.runner(["docker", "stop", "secureops-gateway"])
            try:
                self.compose(candidate, "down")
            finally:
                self.record_metrics(current or candidate, False)
            if rollback_failed:
                raise RuntimeError("Deployment failed and rollback verification failed; operator intervention required")
            raise

    def rollback(self):
        previous, current = self.load("previous"), self.load("current")
        if not previous or not current:
            raise RuntimeError("No previous release is available")
        self.compose(previous, "up", "-d", "--wait", "--wait-timeout", "120")
        self.checker(f"http://127.0.0.1:{previous['app_port']}")
        try:
            self.switch(previous)
            self.checker("http://127.0.0.1:8080")
            self.verify_alb()
        except Exception:
            self.switch(current)
            raise
        self.save("current", previous)
        self.save("previous", current)
        self.save("last-attempt", dict(previous, status="rolled_back"))
        self.record_metrics(previous, True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--git-sha")
    parser.add_argument("--pipeline-id")
    parser.add_argument("--environment", choices=["dev", "staging", "production"])
    parser.add_argument("--backend-image")
    parser.add_argument("--frontend-image")
    args = parser.parse_args()
    manager = Deployer(args.root)
    with (manager.state / "deployment.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not os.getenv("SMOKE_IDENTITY") or not os.getenv("SMOKE_PASSWORD"):
            parser.error("SMOKE_IDENTITY and SMOKE_PASSWORD must identify a provisioned smoke account")
        if args.rollback:
            manager.rollback()
        else:
            if not all([args.git_sha, args.pipeline_id, args.environment, args.backend_image, args.frontend_image]):
                parser.error("All release metadata arguments are required")
            if args.environment == "production" and not all(os.getenv(k) for k in ("TARGET_GROUP_ARN", "APP_INSTANCE_ID")):
                parser.error("Production requires TARGET_GROUP_ARN and APP_INSTANCE_ID for ALB verification")
            current = manager.load("current")
            slot = "green" if current and current["slot"] == "blue" else "blue"
            manager.deploy(manager.release(slot, args.git_sha, args.pipeline_id, args.environment,
                                           args.backend_image, args.frontend_image))
    print("Release verified. Metadata saved under .runtime/.")


if __name__ == "__main__":
    main()
