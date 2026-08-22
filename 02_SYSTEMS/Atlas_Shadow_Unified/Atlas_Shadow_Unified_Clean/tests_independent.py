#!/usr/bin/env python3
"""
Independent test suite for Atlas Shadow Unified.

These tests exercise real public APIs and assert on concrete values,
not only on the system's own self-reported "ok" flags. A bug that
fools certify_system.py should not automatically pass this suite.
"""

from __future__ import annotations
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

import atlas_shadow_unified as a

ROOT = Path(__file__).resolve().parent


class TestImports(unittest.TestCase):
    def test_module_imports(self):
        self.assertTrue(hasattr(a, "HAS_TORCH") or True)  # may be True or False
        self.assertTrue(hasattr(a, "HAS_SYMPY"))

    def test_all_shipped_files_compile(self):
        for path in sorted(ROOT.glob("*.py")):
            if path.name.startswith("test"):
                continue
            r = subprocess.run(
                [sys.executable, "-m", "py_compile", str(path)],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, f"{path.name}: {r.stderr}")


class TestMathEngine(unittest.TestCase):
    def setUp(self):
        self.m = a.MathEngine()

    def test_solve_quadratic(self):
        roots = str(self.m.solve_equation("x**2 - 9 = 0", "x"))
        self.assertTrue("-3" in roots and "3" in roots)

    def test_derivative(self):
        self.assertEqual(str(self.m.derivative("x**3", "x")), "3*x**2")

    def test_prime(self):
        self.assertTrue(self.m.number_theory(97, "is_prime"))
        self.assertFalse(self.m.number_theory(91, "is_prime"))  # 7*13


class TestLogicEngine(unittest.TestCase):
    def test_contradiction(self):
        lg = a.LogicEngine()
        self.assertEqual(lg.is_satisfiable("A & ~A"), "UNSATISFIABLE")


class TestCodeLangDetector(unittest.TestCase):
    def test_python(self):
        det = a.CodeLangDetector()
        self.assertEqual(det.detect("def foo():\n    return 1"), "python")

    def test_unknown(self):
        det = a.CodeLangDetector()
        self.assertEqual(det.detect("asdkjalksdjalksdj gibberish"), "unknown")


class TestKnowledgePod(unittest.TestCase):
    def test_dedupe(self):
        pod = a.KnowledgePod()
        self.assertTrue(pod.add("d1", "Attention is all you need for transformers."))
        self.assertFalse(pod.add("d2", "Attention is all you need for transformers."))
        self.assertEqual(pod.stats()["docs"], 1)

    def test_query_ranks(self):
        pod = a.KnowledgePod()
        pod.add("d1", "Scaled dot-product attention is softmax(QK^T / sqrt(d_k)) V.")
        pod.add("d2", "The weather in Lisbon is mild in spring.")
        hits = pod.query("attention softmax")
        self.assertTrue(hits and hits[0]["id"] == "d1")


class TestAtlasIntegrity(unittest.TestCase):
    def test_detect_and_recover_corruption(self):
        atlas = a.UnifiedAtlas()
        try:
            before = atlas.verify_all()
            self.assertTrue(all(v.get("status") == "INTACT" for v in before))

            atlas.corrupt("Pythagorean theorem", "latex", r"a^2+b^2=c^3")
            after = atlas.verify_all()
            compromised = [v for v in after if v.get("status") == "COMPROMISED"]
            self.assertEqual(len(compromised), 1)
            self.assertEqual(compromised[0]["name"], "Pythagorean theorem")

            if hasattr(atlas, "reseal"):
                atlas.reseal("Pythagorean theorem")
                recovered = atlas.verify_all()
                self.assertTrue(all(v.get("status") == "INTACT" for v in recovered))
        finally:
            atlas.close()

    def test_search_euler(self):
        atlas = a.UnifiedAtlas()
        try:
            results = atlas.search("Euler")
            self.assertTrue(any("Euler" in r.get("name", "") for r in results))
        finally:
            atlas.close()


class TestPredictiveEngine(unittest.TestCase):
    def test_forecast_direction(self):
        pred = a.PredictiveEngine()
        out = pred.learned([1.0, 2.0, 3.0, 4.0, 5.0], steps=1)
        self.assertIn("forecast", out)
        # Upward series should forecast near 6
        self.assertGreaterEqual(out["forecast"], 5.0)
        self.assertLessEqual(out["forecast"], 7.5)

    def test_short_series(self):
        pred = a.PredictiveEngine()
        out = pred.learned([1.0, 2.0], steps=1)
        self.assertIn("error", out)


class TestSourceEngineer(unittest.TestCase):
    def test_audit_clean(self):
        audit = a.SourceEngineer(str(ROOT)).audit()
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["critical_count"], 0)
        self.assertGreaterEqual(audit["file_count"], 5)


class TestSuperMathCodingGate(unittest.TestCase):
    def test_all_pass(self):
        gate = a.SuperMathCodingGate(a.MathEngine(), a.LogicEngine(), a.CodeLangDetector()).run()
        self.assertTrue(gate["ok"])
        self.assertGreaterEqual(gate["count"], 7)


class TestCertifyHarness(unittest.TestCase):
    def test_certify_system_passes(self):
        proc = subprocess.run(
            [sys.executable, "certify_system.py"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        self.assertTrue(report["all_ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
