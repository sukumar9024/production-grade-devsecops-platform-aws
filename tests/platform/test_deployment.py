import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("deploy", ROOT / "scripts/deploy.py")
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".env.runtime").write_text("JWT_SECRET=private-value\n")
        self.manager = deploy.Deployer(self.root, runner=lambda *a, **kw: None, checker=lambda url: None)
        self.old = self.manager.release("blue", "a" * 40, "1", "staging", "repo/backend@sha256:" + "a" * 64, "repo/frontend@sha256:" + "b" * 64)
        self.manager.save("current", self.old)
        self.manager.switch(self.old)
        self.new = self.manager.release("green", "b" * 40, "2", "staging", "repo/backend@sha256:" + "c" * 64, "repo/frontend@sha256:" + "d" * 64)

    def tearDown(self):
        self.temp.cleanup()

    def test_mutable_images_are_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.release("green", "b" * 40, "2", "staging", "repo/backend:latest", "repo/frontend:latest")

    def test_candidate_failure_leaves_current_release(self):
        def unhealthy(url):
            raise RuntimeError("not ready")
        self.manager.checker = unhealthy
        with self.assertRaises(RuntimeError):
            self.manager.deploy(self.new)
        self.assertEqual(self.manager.load("current")["git_commit"], "a" * 40)
        self.assertIn("18080", (self.root / "docker/gateway/upstream.conf").read_text())
        self.assertFalse((self.root / ".runtime/previous.json").exists())

    def test_failure_after_switch_restores_previous_gateway(self):
        def unhealthy_gateway(url):
            if url.endswith(":8080"):
                raise RuntimeError("gateway failed")
        self.manager.checker = unhealthy_gateway
        with self.assertRaises(RuntimeError):
            self.manager.deploy(self.new)
        self.assertIn("18080", (self.root / "docker/gateway/upstream.conf").read_text())
        self.assertEqual(self.manager.load("current")["git_commit"], "a" * 40)

    def test_success_records_current_previous_and_private_env(self):
        self.manager.deploy(self.new)
        self.assertEqual(self.manager.load("current")["git_commit"], "b" * 40)
        self.assertEqual(self.manager.load("previous")["git_commit"], "a" * 40)
        self.assertEqual((self.root / (".runtime/env-" + "b" * 40)).stat().st_mode & 0o777, 0o600)
        self.assertNotIn("private-value", json.dumps(self.manager.load("current")))

    def test_explicit_rollback_checks_restored_release(self):
        self.manager.deploy(self.new)
        checked = []
        self.manager.checker = checked.append
        self.manager.rollback()
        self.assertEqual(self.manager.load("current")["git_commit"], "a" * 40)
        self.assertIn("http://127.0.0.1:8080", checked)

    def test_gateway_uses_scanned_release_image_and_restores_it_on_rollback(self):
        images = []

        def capture(command, **kwargs):
            if "secureops-gateway" in command and "up" in command:
                images.append(kwargs["env"]["GATEWAY_IMAGE"])

        self.manager.runner = capture
        self.manager.deploy(self.new)
        self.manager.rollback()
        self.assertEqual(images, [self.new["frontend_image"], self.old["frontend_image"]])
        self.assertEqual((self.root / ".runtime/gateway.env").read_text(),
                         f"GATEWAY_IMAGE={self.old['frontend_image']}\n")

    def test_failed_first_release_cannot_restart_gateway_on_reboot(self):
        (self.root / ".runtime/current.json").unlink()
        (self.root / ".runtime/gateway.env").unlink()

        def unhealthy_gateway(url):
            if url.endswith(":8080"):
                raise RuntimeError("gateway failed")

        self.manager.checker = unhealthy_gateway
        with self.assertRaises(RuntimeError):
            self.manager.deploy(self.new)
        self.assertFalse((self.root / ".runtime/gateway.env").exists())
        self.assertIsNone(self.manager.load("current"))


if __name__ == "__main__":
    unittest.main()
