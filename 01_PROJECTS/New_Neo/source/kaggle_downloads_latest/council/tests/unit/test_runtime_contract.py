#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)
import artifact_gate
import smoke_scorer


class RuntimeContractTests(unittest.TestCase):
    def test_smoke_v2_hash_and_schema(self):
        path = os.path.join(BASE, "datasets", "smoke-v2.jsonl")
        with open(os.path.join(BASE, "datasets", "smoke-v2.manifest.json"), encoding="utf-8") as f:
            man = json.load(f)
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(digest, man["sha256"])
        self.assertEqual(man["records"], 60)
        items = smoke_scorer.load_smoke(path)
        self.assertTrue(smoke_scorer.validate_benchmark(items))
        self.assertEqual(len(items), 60)

    def test_validate_rejects_duplicate_and_bad_scorer(self):
        items = smoke_scorer.load_smoke()
        bad = list(items)
        bad.append(dict(items[0]))
        with self.assertRaises(ValueError):
            smoke_scorer.validate_benchmark(bad)
        empty = []
        with self.assertRaises(ValueError):
            smoke_scorer.validate_benchmark(empty)
        broken = [dict(items[0], scorer="not-a-scorer")]
        with self.assertRaises(ValueError):
            smoke_scorer.validate_benchmark(broken)

    def test_worker_usage_exit_2(self):
        r = subprocess.run(
            [sys.executable, os.path.join(BASE, "worker_entry.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_worker_fails_without_cuda_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "req.json"
            out = Path(td) / "out.json"
            req.write_text(json.dumps({
                "model": "/no/such/model",
                "prompt": "hi",
                "local_files_only": True,
            }))
            r = subprocess.run(
                [sys.executable, os.path.join(BASE, "worker_entry.py"),
                 str(req), str(out)],
                capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertTrue(out.exists())
            body = json.loads(out.read_text())
            self.assertFalse(body.get("ok"))

    def test_ledger_events_explain_mint(self):
        with open(os.path.join(BASE, "usd_ledger.json"), encoding="utf-8") as f:
            raw = json.load(f)
        mints = [e for e in raw["events"] if e.get("kind") == "mint"]
        self.assertEqual(sum(e.get("usd", 0) for e in mints), raw["global_minted"])
        self.assertTrue(all("t" in e and "session" in e for e in mints))


if __name__ == "__main__":
    unittest.main()
