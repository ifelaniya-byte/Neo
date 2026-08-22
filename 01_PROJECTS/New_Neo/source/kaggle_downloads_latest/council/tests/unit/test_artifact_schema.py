import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
import artifact_gate


class ArtifactGateSchemaTests(unittest.TestCase):
    def test_absent_artifact_has_stable_schema(self):
        rec = artifact_gate.verify_offline_artifact(str(BASE / "missing-model"))
        self.assertEqual(rec["status"], "absent")
        self.assertFalse(rec["exists"])
        for key in ("tokenizer_offline_safe", "chat_template_embedded",
                    "tokenizer_remote_refs", "config_load_ok", "tokenizer_load_ok"):
            self.assertIn(key, rec)
            self.assertIsNone(rec[key])
