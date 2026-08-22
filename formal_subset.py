#!/usr/bin/env python3
"""
Independent formal-subset audit pack.
Exports machine-checkable obligations for net-PnL identity and causality.
Does NOT claim proven until an external kernel (Lean/Coq) accepts.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from formal_bridge import submit_obligation, kernel_available, try_lean_check


OBLIGATIONS = [
    {
        "id": "net_pnl_identity",
        "formal": (
            "theorem net_pnl_identity (gross costs : ℝ) :\n"
            "  net = gross - costs → net + costs = gross\n"
            "-- Product obligation: OutcomeLabel net_pnl_usd MUST equal "
            "gross_pnl_usd - sum(all cost components)."
        ),
    },
    {
        "id": "causality_available_after_event",
        "formal": (
            "theorem causality_available (event_ts available_ts : ℕ) :\n"
            "  available_ts ≥ event_ts\n"
            "-- Product obligation: available_timestamp_ms ≥ event_timestamp_ms "
            "for every NormalizedEvent / packet feature."
        ),
    },
    {
        "id": "abstain_default",
        "formal": (
            "theorem abstain_default :\n"
            "  ¬(smt_allow ∧ interval_allow ∧ constraints_pass) → verdict = ABSTAIN\n"
            "-- Product obligation: TRADE only if SMT + interval + constraints all pass."
        ),
    },
]


def export_formal_subset(out_dir: str = "artifacts/formal") -> Dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for obl in OBLIGATIONS:
        r = submit_obligation(obl["id"], obl["formal"], out_dir=out_dir)
        written.append(r)
    manifest = {
        "version": "1.0.0-product",
        "kind": "formal_subset_pack",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "n_obligations": len(written),
        "obligations": written,
        "kernels": kernel_available(),
        "proven_count": 0,
        "note": "Unchecked until external kernel accepts. Product ships obligations, not proofs.",
    }
    path = out / "formal_subset_manifest.json"
    path.write_text(json.dumps(manifest, indent=2))
    manifest["path"] = str(path)
    return manifest


def attempt_kernel_checks(out_dir: str = "artifacts/formal") -> Dict[str, Any]:
    results = []
    for obl in OBLIGATIONS:
        p = Path(out_dir) / f"{obl['id']}.txt"
        if p.exists():
            results.append({"id": obl["id"], **try_lean_check(str(p))})
        else:
            results.append({"id": obl["id"], "ok": False, "proven": False, "reason": "missing_file"})
    return {
        "n": len(results),
        "n_proven": sum(1 for r in results if r.get("proven")),
        "results": results,
        "note": "Lean may be absent; product still valid with obligations exported.",
    }
