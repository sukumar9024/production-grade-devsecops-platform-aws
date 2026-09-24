import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("aws_runtime", Path(__file__).resolve().parents[2] / "scripts/aws-runtime-config.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RuntimeConfigTests(unittest.TestCase):
    def outputs(self):
        values = {key: "sample-resource" for key in ["app_secret_arn", "database_secret_arn", "database_endpoint",
            "redis_secret_arn", "redis_endpoint", "application_bucket", "target_group_arn", "log_group_name"]}
        values["ecr_repository_urls"] = {"backend": "registry.example/backend", "frontend": "registry.example/frontend"}
        return {key: {"value": value} for key, value in values.items()}

    def test_maps_actual_repository_paths_and_region(self):
        result = runtime.build_config(self.outputs(), "ap-south-1", "app.example.com")
        self.assertEqual(result["ecr_registry"], "registry.example")
        self.assertEqual(result["database_host"], "sample-resource")
        self.assertEqual(result["cors_origins"], "https://app.example.com")
        self.assertNotIn("password", result)

    def test_placeholder_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            runtime.build_config(self.outputs(), "ap-south-1", "********")

    def test_cross_account_repository_mismatch_is_rejected(self):
        outputs = self.outputs()
        outputs["ecr_repository_urls"]["value"]["frontend"] = "other.example/frontend"
        with self.assertRaises(ValueError):
            runtime.build_config(outputs, "ap-south-1", "app.example.com")
