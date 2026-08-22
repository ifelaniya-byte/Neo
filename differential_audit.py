#!/usr/bin/env python3
"""Differential audit: same decision_id across runs should not flip without config change."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_decisions(run_dir: str) -> Dict[str, Dict[str, Any]]:
    path = Path(run_dir) / "paper" / "decisions.jsonl"
    out: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            did = rec.get("decision_id")
            if did:
                out[did] = rec
    return out


def compare_runs(run_a: str, run_b: str) -> Dict[str, Any]:
    a = load_decisions(run_a)
    b = load_decisions(run_b)
    shared = set(a) & set(b)
    flips = []
    for did in shared:
        va, vb = a[did].get("verdict"), b[did].get("verdict")
        ca, cb = a[did].get("config_hash"), b[did].get("config_hash")
        if va != vb and ca == cb:
            flips.append({"decision_id": did, "verdict_a": va, "verdict_b": vb, "config_hash": ca})
    return {
        "n_shared": len(shared),
        "n_unexplained_flips": len(flips),
        "flips": flips,
        "ok": len(flips) == 0,
    }
