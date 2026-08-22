#!/usr/bin/env python3
"""
Lab CI job for simulation-assurance gates.

Runs adversarial suite + independent audit (+ optional mechanical battery).
Intended for every PR / commit in a research lab setting.
Exit code 0 only if all required gates pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_lab_ci(
    run_dir: str = "artifacts/run_lab_ci",
    include_battery: bool = True,
    include_overclaim_probe: bool = True,
) -> Dict[str, Any]:
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "job": "lab_ci",
        "version": "1.0.0",
        "timestamp": _utc(),
        "product": "simulation_assurance",
        "live_trading": False,
        "checks": {},
        "failed": [],
    }

    # 1. Adversarial suite
    try:
        from adversarial_suite import run_suite
        adv = run_suite(ledger_path=str(run_path / "adversarial_ledger.jsonl"))
        report["checks"]["adversarial"] = {
            "all_ok": adv.get("all_ok"),
            "n_suite_pass": adv.get("n_suite_pass"),
            "n_cases": adv.get("n_cases"),
        }
        if not adv.get("all_ok"):
            report["failed"].append("adversarial")
    except Exception as e:
        report["checks"]["adversarial"] = {"all_ok": False, "error": str(e)}
        report["failed"].append("adversarial")

    # 2. Independent audit
    try:
        from independent_audit import run_independent_audit
        audit = run_independent_audit(str(run_path / "independent_audit"))
        report["checks"]["independent_audit"] = {
            "ok": audit.get("ok"),
            "failed": audit.get("failed"),
            "double_pass": audit.get("checks", {}).get("double_pass"),
            "adversarial": audit.get("checks", {}).get("adversarial"),
        }
        if not audit.get("ok"):
            report["failed"].append("independent_audit")
    except Exception as e:
        report["checks"]["independent_audit"] = {"ok": False, "error": str(e)}
        report["failed"].append("independent_audit")

    # 3. Optional mechanical battery
    if include_battery:
        try:
            from tools.verifiers import full_mechanical_battery
            bat = full_mechanical_battery()
            # adversarial inside battery is nested; require double_pass PASS
            dp = bat.get("double_pass")
            dp_ok = dp == "PASS" or (isinstance(dp, dict) and dp.get("final_verdict") == "PASS")
            adv_ok = True
            if isinstance(bat.get("adversarial"), dict):
                adv_ok = bool(bat["adversarial"].get("all_ok", True))
            report["checks"]["mechanical_battery"] = {
                "double_pass_ok": dp_ok,
                "adversarial_ok": adv_ok,
                "keys": list(bat.keys()),
            }
            if not dp_ok:
                report["failed"].append("mechanical_battery_double_pass")
        except Exception as e:
            report["checks"]["mechanical_battery"] = {"error": str(e)}
            report["failed"].append("mechanical_battery")

    # 4. Completeness overclaim must stay blocked
    if include_overclaim_probe:
        try:
            from engineers import DoublePassEngineerGate
            gate = DoublePassEngineerGate(ledger_path=str(run_path / "overclaim_ledger.jsonl"))
            r = gate.run(
                {"claim": "complete conclusive world physics catalogue as oracle stage"},
                subject_type="claim",
                subject_id="ci_overclaim",
            )
            blocked = r.to_dict().get("final_verdict") == "BLOCKED"
            report["checks"]["overclaim_probe"] = {
                "blocked": blocked,
                "verdict": r.to_dict().get("final_verdict"),
            }
            if not blocked:
                report["failed"].append("overclaim_not_blocked")
        except Exception as e:
            report["checks"]["overclaim_probe"] = {"error": str(e)}
            report["failed"].append("overclaim_probe")

    # 5. Feed format self-check
    try:
        from adapters.feed_format import write_example_feed, ingest_feed_file
        example = run_path / "example_feed.json"
        write_example_feed(example, n=3)
        ing = ingest_feed_file(example)
        report["checks"]["feed_format"] = {
            "ok": ing.get("ok"),
            "n": ing.get("n"),
            "validation_ok": (ing.get("validation") or {}).get("ok"),
        }
        if not ing.get("ok"):
            report["failed"].append("feed_format")
    except Exception as e:
        report["checks"]["feed_format"] = {"error": str(e)}
        report["failed"].append("feed_format")

    # 6. LLM wrapper refuse probe
    try:
        from llm_wrapper import ClearedLLMGateway
        gw = ClearedLLMGateway()
        blocked_subj = {"raw": "uncleared text", "allowed_for_llm": False}
        refuse = gw.interpret(blocked_subj)
        report["checks"]["llm_wrapper_refuse"] = {
            "refused": refuse.get("status") == "refused",
            "detail": refuse.get("reason"),
        }
        if refuse.get("status") != "refused":
            report["failed"].append("llm_wrapper_did_not_refuse")
    except Exception as e:
        report["checks"]["llm_wrapper_refuse"] = {"error": str(e)}
        report["failed"].append("llm_wrapper")

    report["ok"] = len(report["failed"]) == 0
    out = run_path / "lab_ci_report.json"
    out.write_text(json.dumps(report, indent=2, default=str))
    report["report_path"] = str(out)
    return report


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="MegaCompact lab CI — adversarial + independent audit")
    p.add_argument("--run-dir", default="artifacts/run_lab_ci")
    p.add_argument("--no-battery", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    report = run_lab_ci(
        run_dir=args.run_dir,
        include_battery=not args.no_battery,
    )
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("lab_ci ok=", report["ok"], "failed=", report["failed"])
        print("report:", report.get("report_path"))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
