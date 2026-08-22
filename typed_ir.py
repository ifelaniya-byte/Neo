#!/usr/bin/env python3
"""Typed intermediate representation for candidate actions before simulation."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


ALLOWED_KINDS = {"swap", "bridge", "wait", "abstain"}


@dataclass
class ActionIR:
    kind: str
    venue: str
    token_in: str
    token_out: str
    amount_in: float
    max_slippage_bps: float
    chain_id: int
    deadline_ms: int

    def validate(self) -> Dict[str, Any]:
        issues = []
        if self.kind not in ALLOWED_KINDS:
            issues.append(f"kind not allowed: {self.kind}")
        if self.amount_in < 0:
            issues.append("amount_in < 0")
        if self.max_slippage_bps < 0 or self.max_slippage_bps > 10_000:
            issues.append("slippage out of range")
        if self.chain_id <= 0:
            issues.append("chain_id invalid")
        if self.deadline_ms < 0:
            issues.append("deadline invalid")
        return {"ok": len(issues) == 0, "issues": issues, "action": asdict(self)}


def from_dict(d: Dict[str, Any]) -> ActionIR:
    return ActionIR(
        kind=str(d.get("kind", "abstain")),
        venue=str(d.get("venue", "")),
        token_in=str(d.get("token_in", "")),
        token_out=str(d.get("token_out", "")),
        amount_in=float(d.get("amount_in", 0)),
        max_slippage_bps=float(d.get("max_slippage_bps", 0)),
        chain_id=int(d.get("chain_id", 0)),
        deadline_ms=int(d.get("deadline_ms", 0)),
    )


def validate_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = [from_dict(a).validate() for a in actions]
    return {
        "ok": all(r["ok"] for r in results),
        "n": len(results),
        "results": results,
    }
