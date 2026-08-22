#!/usr/bin/env python3
"""Mechanical verifier tool-set: double-pass, SMT, interval, typed IR, causal, schema, units, sandbox."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from engineers import DoublePassEngineerGate, StationaryEngineer, EngineerVerdict

try:
    from smt_gate import pre_trade_gate, Constraint, solve
except Exception:
    pre_trade_gate = None  # type: ignore
try:
    from interval_arith import Interval, net_edge_interval, trade_allowed_by_interval
except Exception:
    Interval = net_edge_interval = trade_allowed_by_interval = None  # type: ignore
try:
    from typed_ir import validate_actions
except Exception:
    validate_actions = None  # type: ignore
try:
    from causal_graph import check_features
except Exception:
    check_features = None  # type: ignore
try:
    from schema_registry import load_schema, validate_required
except Exception:
    load_schema = validate_required = None  # type: ignore
try:
    from unit_tags import stationary_unit_probe, attach_unit_tags, tag_feature
except Exception:
    stationary_unit_probe = attach_unit_tags = tag_feature = None  # type: ignore
try:
    from sandbox import run as sandbox_run
except Exception:
    sandbox_run = None  # type: ignore
try:
    from adversarial_suite import run_suite
except Exception:
    run_suite = None  # type: ignore
try:
    from gate_fuzzer import fuzz
except Exception:
    fuzz = None  # type: ignore
try:
    from knowledge_facade import get_facade
except Exception:
    get_facade = None  # type: ignore


def double_pass(subject: Any, subject_id: str = "tool", subject_type: str = "dict",
                ledger_path: str = "artifacts/toolset_verify_ledger.jsonl") -> Dict[str, Any]:
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    r = gate.run(subject, subject_id, subject_type)
    return {
        "final_verdict": r.final_verdict.value,
        "allowed_for_llm": r.allowed_for_llm,
        "report": r.to_dict(),
    }


def stationary_only(subject: Any, subject_id: str = "tool", subject_type: str = "dict") -> Dict[str, Any]:
    r = StationaryEngineer().verify(subject, subject_id, subject_type)
    return {"verdict": r.verdict.value, "all_ok": r.all_ok, "issues": r.issues, "n_checks": len(r.checks)}


def smt_trade(net_edge_usd: float, revert_p: float, inclusion_p: float, ood: float,
              thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    if pre_trade_gate is None:
        return {"ok": False, "error": "smt_unavailable"}
    return pre_trade_gate(net_edge_usd, revert_p, inclusion_p, ood, thresholds)


def interval_edge(output_lo: float, output_hi: float, cost_lo: float, cost_hi: float,
                  min_edge: float = 1.0) -> Dict[str, Any]:
    if Interval is None:
        return {"ok": False, "error": "interval_unavailable"}
    edge = net_edge_interval(Interval(output_lo, output_hi), Interval(cost_lo, cost_hi))
    return trade_allowed_by_interval(edge, min_edge)


def typed_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    if validate_actions is None:
        return {"ok": False, "error": "typed_ir_unavailable"}
    return validate_actions(actions)


def causal_features(features: List[str]) -> Dict[str, Any]:
    if check_features is None:
        return {"ok": False, "error": "causal_unavailable"}
    return check_features(features)


def schema_check(obj: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    if load_schema is None:
        return {"ok": False, "error": "schema_unavailable"}
    sch = load_schema(schema_name)
    return validate_required(obj, sch)


def unit_probe(payload: Dict[str, Any]) -> Dict[str, Any]:
    if stationary_unit_probe is None:
        return {"ok": False, "error": "unit_tags_unavailable"}
    return stationary_unit_probe(payload)


def sandboxed(fn, timeout_s: float = 2.0) -> Dict[str, Any]:
    if sandbox_run is None:
        return {"ok": False, "error": "sandbox_unavailable"}
    return sandbox_run(fn, timeout_s=timeout_s)


def adversarial() -> Dict[str, Any]:
    if run_suite is None:
        return {"ok": False, "error": "adversarial_unavailable"}
    return run_suite()


def fuzz_gates(seeds: List[Dict[str, Any]], n: int = 10, seed: int = 0) -> Dict[str, Any]:
    if fuzz is None:
        return {"ok": False, "error": "fuzzer_unavailable"}
    return fuzz(seeds, n=n, seed=seed)


def knowledge_stats() -> Dict[str, Any]:
    if get_facade is None:
        return {"ok": False, "error": "facade_unavailable"}
    return get_facade().stats()


def full_mechanical_battery(subject: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run a standard battery of mechanical verifiers (local only)."""
    subject = subject or {
        "event_id": "battery",
        "event_timestamp_ms": 1000,
        "observed_timestamp_ms": 1000,
        "available_timestamp_ms": 1100,
        "event_type": "swap",
        "entity_id": "pool",
        "chain_id": 42161,
    }
    return {
        "double_pass": double_pass(subject, "battery", "NormalizedEvent"),
        "smt": smt_trade(2.0, 0.01, 0.95, 0.2),
        "interval": interval_edge(10, 12, 8, 9, 1.0),
        "causal": causal_features(["features_t", "outcome_t"]),
        "typed": typed_actions([{
            "kind": "swap", "venue": "x", "token_in": "A", "token_out": "B",
            "amount_in": 1.0, "max_slippage_bps": 30, "chain_id": 42161, "deadline_ms": 999,
        }]),
        "schema": schema_check(subject, "events_v1.json"),
        "adversarial": adversarial(),
        "knowledge": knowledge_stats(),
    }
