#!/usr/bin/env python3
"""
Independent audit / formal subset (Product VD4).

Runs a self-contained audit battery that does not depend on pipeline stage
order, and emits formal obligations via formal_bridge for external kernels.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from engineers import DoublePassEngineerGate, EngineerVerdict

try:
    from formal_bridge import submit_obligation, kernel_available, try_lean_check
except Exception:
    submit_obligation = kernel_available = try_lean_check = None  # type: ignore

try:
    from signed_ledger import SignedLedger
except Exception:
    SignedLedger = None  # type: ignore

try:
    from adversarial_suite import run_suite
except Exception:
    run_suite = None  # type: ignore

try:
    from bit_exact_replay import self_proof, pin_matrix
except Exception:
    self_proof = pin_matrix = None  # type: ignore

try:
    from merkle_artifacts import build_merkle
except Exception:
    build_merkle = None  # type: ignore

try:
    from tools.verifiers import full_mechanical_battery
except Exception:
    full_mechanical_battery = None  # type: ignore


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class IndependentAuditor:
    """
    Product-facing independent audit runner for simulation-assurance labs.
    Paper-only: no live trading, no completeness claims.
    """

    def __init__(self, run_dir: Optional[str] = None, ledger_path: Optional[str] = None):
        self.run_dir = Path(run_dir or "artifacts/run_independent_audit")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or str(self.run_dir / "audit_engineer_ledger.jsonl")
        )
        self.signed = SignedLedger(path=str(self.run_dir / "signed_audit_ledger.jsonl")) if SignedLedger else None

    def run(self, subject: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        subject = subject or {
            "event_id": "audit_probe",
            "entity_id": "entity_audit",
            "event_timestamp_ms": 1000,
            "observed_timestamp_ms": 1050,
            "available_timestamp_ms": 1100,
            "event_type": "quote",
            "chain_id": 42161,
            "payload": {"mid_usd": 100.0},
        }
        report: Dict[str, Any] = {
            "auditor": "IndependentAuditor",
            "version": "1.0.0-product",
            "timestamp": _utc(),
            "product": "simulation_assurance",
            "live_trading": False,
            "checks": {},
        }

        # 1. Double-pass on subject
        dp = self.gate.run(subject, subject_id="independent_audit_subject", subject_type="NormalizedEvent")
        report["checks"]["double_pass"] = {
            "verdict": dp.final_verdict.value if hasattr(dp.final_verdict, "value") else str(dp.final_verdict),
            "allowed_for_llm": dp.allowed_for_llm,
        }

        # 2. Adversarial suite
        if run_suite:
            adv = run_suite()
            report["checks"]["adversarial"] = {
                "all_ok": adv.get("all_ok"),
                "n_suite_pass": adv.get("n_suite_pass"),
                "n_cases": adv.get("n_cases"),
            }
        else:
            report["checks"]["adversarial"] = {"all_ok": False, "error": "suite_unavailable"}

        # 3. Mechanical battery
        if full_mechanical_battery:
            bat = full_mechanical_battery(subject)
            report["checks"]["mechanical_battery"] = {
                k: (v.get("final_verdict") if isinstance(v, dict) and "final_verdict" in v else v)
                for k, v in bat.items()
            }
        else:
            report["checks"]["mechanical_battery"] = {"error": "unavailable"}

        # 4. Formal obligation (not proven until kernel accepts)
        formal_result: Dict[str, Any] = {"ok": False, "proven": False}
        if submit_obligation:
            formal_dir = self.run_dir / "formal"
            formal_dir.mkdir(parents=True, exist_ok=True)
            formal_result = submit_obligation(
                statement_id="audit_net_pnl_identity",
                formal_text="Net PnL identity: gross - sum(costs) == net for labeled outcomes",
                out_dir=str(formal_dir),
            )
            if try_lean_check and formal_result.get("path"):
                lean = try_lean_check(formal_result["path"])
                formal_result["lean_attempt"] = lean
        report["checks"]["formal_subset"] = formal_result
        report["checks"]["kernels_available"] = kernel_available() if kernel_available else {}

        # 5. Bit-exact self-proof on this audit run dir
        if self_proof:
            # write a minimal summary so hashes have something to pin
            summary_path = self.run_dir / "reports"
            summary_path.mkdir(parents=True, exist_ok=True)
            (summary_path / "run_summary.json").write_text(
                json.dumps({"audit": True, "ts": _utc()}, indent=2)
            )
            report["checks"]["bit_exact_self"] = self_proof(str(self.run_dir))
        else:
            report["checks"]["bit_exact_self"] = {"ok": False, "error": "unavailable"}

        # 6. Merkle over audit artifacts
        if build_merkle:
            report["checks"]["merkle"] = build_merkle(str(self.run_dir))
        else:
            report["checks"]["merkle"] = {"error": "unavailable"}

        # 7. Signed ledger entry
        if self.signed:
            entry = self.signed.append("independent_audit", {
                "double_pass": report["checks"]["double_pass"],
                "adversarial_ok": report["checks"].get("adversarial", {}).get("all_ok"),
            })
            report["checks"]["signed_ledger"] = {
                "entry_id": entry.entry_id,
                "algorithm": entry.algorithm,
                "verify": self.signed.verify_file(),
            }

        # Aggregate
        hard = []
        if report["checks"]["double_pass"].get("verdict") not in ("PASS", "pass"):
            hard.append("double_pass")
        if not report["checks"].get("adversarial", {}).get("all_ok"):
            hard.append("adversarial")
        report["ok"] = len(hard) == 0
        report["failed"] = hard
        report["product_claim"] = (
            "Paper-only simulation assurance under double-pass engineers. "
            "No live trading. Finite settled knowledge only."
        )

        out_path = self.run_dir / "independent_audit_report.json"
        out_path.write_text(json.dumps(report, indent=2, default=str))
        report["report_path"] = str(out_path)
        return report


def run_independent_audit(run_dir: Optional[str] = None) -> Dict[str, Any]:
    return IndependentAuditor(run_dir=run_dir).run()
