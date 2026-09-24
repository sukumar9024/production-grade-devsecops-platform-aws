import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("dast", Path(__file__).resolve().parents[2] / "scripts/dast.py")
dast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dast)


class DastGateTests(unittest.TestCase):
    def test_empty_report_does_not_pass(self):
        with self.assertRaises(ValueError):
            dast.gate({})

    def test_high_risk_blocks(self):
        self.assertEqual(len(dast.gate({"site": [{"alerts": [{"riskcode": "3"}]}]})), 1)

    def test_medium_is_retained_for_review_without_high_gate(self):
        self.assertEqual(dast.gate({"site": [{"alerts": [{"riskcode": "2"}]}]}), [])
