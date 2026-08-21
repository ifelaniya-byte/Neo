import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[2]


class ReleaseConsistencyTests(unittest.TestCase):
    def test_current_state_matches_handoff(self):
        state = json.loads((BASE / "CURRENT_STATE.json").read_text(encoding="utf-8"))
        handoff = (BASE / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertEqual(state["release_id"], "council-20260813-r003")
        self.assertEqual(state["previous_release_id"], "council-20260813-r002")
        self.assertIn(state["release_id"], handoff)
        self.assertEqual(state["project_state"], "recovered-control-plane")

    def test_runtime_counts_match_absent_evidence(self):
        state = json.loads((BASE / "CURRENT_STATE.json").read_text(encoding="utf-8"))
        reports = list((BASE / "runs").glob("**/run_report.json")) if (BASE / "runs").exists() else []
        self.assertEqual(reports, [])
        self.assertEqual(state["runtime_verified_models"], 0)
        self.assertFalse(state["runtime"]["run_report_present"])
        self.assertFalse(state["benchmark"]["executed"])

    def test_missing_tensor_is_not_claimed_present(self):
        state = json.loads((BASE / "CURRENT_STATE.json").read_text(encoding="utf-8"))
        artifact = state["model_artifact"]
        self.assertEqual(artifact["local_state"], "absent")
        self.assertEqual(state["runtime_verified_models"], 0)
        self.assertFalse(state["benchmark"]["executed"])
