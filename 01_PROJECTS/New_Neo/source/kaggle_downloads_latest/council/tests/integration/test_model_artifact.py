"""External model-artifact tests.

They are deliberately skipped unless COUNCIL_MODEL_DIR names a supplied model
artifact. A skip is not a pass and does not make runtime claims.
"""
import os
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
import artifact_gate

MODEL_DIR = os.environ.get("COUNCIL_MODEL_DIR")


@unittest.skipUnless(MODEL_DIR, "COUNCIL_MODEL_DIR is required for artifact integration tests")
class ModelArtifactIntegrationTests(unittest.TestCase):
    def test_complete_pinned_artifact(self):
        root = Path(MODEL_DIR)
        self.assertTrue(root.is_dir())
        rec = artifact_gate.verify_offline_artifact(str(root))
        self.assertTrue(rec["exists"])
        self.assertTrue(rec["required_ok"])
        self.assertTrue(rec["weight_pinned_ok"])
        self.assertTrue(rec["tokenizer_files_ok"])
        self.assertTrue(rec["tokenizer_offline_safe"])

    def test_exactly_one_complete_model_dir(self):
        found = artifact_gate.find_complete_model_dir(str(Path(MODEL_DIR).parent))
        self.assertEqual(Path(found).resolve(), Path(MODEL_DIR).resolve())
