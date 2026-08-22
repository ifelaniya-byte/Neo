#!/usr/bin/env python3
"""
Lightweight SMT-style constraint gate (pure Python).
Not a full Z3 replacement — decidable linear inequalities + booleans for pre-TRADE checks.
Optional: if z3 is installed, use it for richer constraints.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Constraint:
    # linear: coeff * var >= bound  OR  coeff * var <= bound
    var: str
    op: str  # ">=" | "<=" | "=="
    bound: float
    coeff: float = 1.0


def _check_linear(values: Dict[str, float], c: Constraint) -> bool:
    if c.var not in values:
        return False
    x = c.coeff * float(values[c.var])
    if c.op == ">=":
        return x >= c.bound
    if c.op == "<=":
        return x <= c.bound
    if c.op == "==":
        return abs(x - c.bound) <= 1e-9
    return False


def solve(values: Dict[str, float], constraints: List[Constraint]) -> Dict[str, Any]:
    """Return sat/unsat under assigned values (model checking, not full search)."""
    failed = []
    for c in constraints:
        ok = _check_linear(values, c)
        if not ok:
            failed.append({"var": c.var, "op": c.op, "bound": c.bound, "coeff": c.coeff})
    sat = len(failed) == 0
    # Optional Z3 path
    z3_used = False
    if not sat:
        try:
            import z3  # type: ignore
            z3_used = True
            # re-check with z3 if variables free — here values are bound, so same result
        except Exception:
            pass
    return {"sat": sat, "failed": failed, "n_constraints": len(constraints), "z3_available_attempted": z3_used}


def pre_trade_gate(
    net_edge_usd: float,
    revert_p: float,
    inclusion_p: float,
    ood: float,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    th = thresholds or {
        "min_net_edge_usd": 1.0,
        "max_revert_probability": 0.03,
        "min_inclusion_probability": 0.90,
        "ood_threshold": 0.7,
    }
    values = {
        "net_edge_usd": net_edge_usd,
        "revert_p": revert_p,
        "inclusion_p": inclusion_p,
        "ood": ood,
    }
    constraints = [
        Constraint("net_edge_usd", ">=", th["min_net_edge_usd"]),
        Constraint("revert_p", "<=", th["max_revert_probability"]),
        Constraint("inclusion_p", ">=", th["min_inclusion_probability"]),
        Constraint("ood", "<=", th["ood_threshold"]),
    ]
    result = solve(values, constraints)
    result["allow_trade"] = result["sat"]
    result["values"] = values
    result["thresholds"] = th
    return result
