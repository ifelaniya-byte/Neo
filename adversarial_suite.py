#!/usr/bin/env python3
"""
Adversarial suite: planted bugs the engineers must catch
(causality leaks, net-PnL mismatches, NaNs, completeness overclaims).
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from pathlib import Path
from engineers import DoublePassEngineerGate, EngineerVerdict


def planted_cases() -> List[Dict[str, Any]]:
    return [
        {
            "id": "leak_future_feature",
            "subject_type": "NormalizedEvent",
            "subject": {
                "event_id": "adv-1",
                "event_timestamp_ms": 1000,
                "observed_timestamp_ms": 1000,
                "available_timestamp_ms": 500,  # before observed — bad
                "event_type": "swap",
                "entity_id": "pool",
                "chain_id": 42161,
            },
            "expect_blocked": True,
            "reason": "available < observed",
        },
        {
            "id": "net_pnl_mismatch",
            "subject_type": "OutcomeLabel",
            "subject": {
                "decision_id": "adv-2",
                "action_id": "a1",
                "realized_output_usd": 100.0,
                "input_cost_usd": 90.0,
                "gas_usd": 1.0,
                "protocol_fees_usd": 0.0,
                "borrow_fees_usd": 0.0,
                "bridge_fees_usd": 0.0,
                "slippage_cost_usd": 0.0,
                "revert_cost_usd": 0.0,
                "other_costs_usd": 0.0,
                "net_pnl_usd": 50.0,  # should be ~9
                "outcome_timestamp_ms": 2000,
                "reverted": False,
            },
            "expect_blocked": True,
            "reason": "net_pnl identity broken",
        },
        {
            "id": "nan_payload",
            "subject_type": "dict",
            "subject": {"decision_id": "adv-3", "score": float("nan")},
            "expect_blocked": True,
            "reason": "NaN not allowed",
        },
        {
            "id": "completeness_overclaim",
            "subject_type": "dict",
            "subject": {"claim": "This is the complete conclusive world physics theory of everything"},
            "expect_blocked": True,
            "reason": "completeness overclaim",
        },
        {
            "id": "clean_event",
            "subject_type": "NormalizedEvent",
            "subject": {
                "event_id": "adv-ok",
                "event_timestamp_ms": 1000,
                "observed_timestamp_ms": 1000,
                "available_timestamp_ms": 1100,
                "event_type": "swap",
                "entity_id": "pool",
                "chain_id": 42161,
            },
            "expect_blocked": False,
            "reason": "valid causality",
        },
    ]


def run_suite(ledger_path: str = "artifacts/adversarial_ledger.jsonl") -> Dict[str, Any]:
    # Isolated ledger dir so engineer ledger_memory does not scan entire artifacts/
    Path(ledger_path).parent.mkdir(parents=True, exist_ok=True)
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    results = []
    n_pass = 0
    n_fail = 0
    for case in planted_cases():
        r = gate.run(case["subject"], case["id"], case["subject_type"])
        blocked = not r.allowed_for_llm
        ok = blocked == case["expect_blocked"]
        if ok:
            n_pass += 1
        else:
            n_fail += 1
        results.append({
            "id": case["id"],
            "expect_blocked": case["expect_blocked"],
            "got_blocked": blocked,
            "verdict": r.final_verdict.value,
            "suite_ok": ok,
            "reason": case["reason"],
        })
    return {
        "n_cases": len(results),
        "n_suite_pass": n_pass,
        "n_suite_fail": n_fail,
        "all_ok": n_fail == 0,
        "results": results,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_suite(), indent=2))
