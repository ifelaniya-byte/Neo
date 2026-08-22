#!/usr/bin/env python3
"""Local artifact tool-set: list runs, read reports, merkle, pin, compare, ledgers."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from merkle_artifacts import build_merkle, write_merkle
except Exception:
    build_merkle = write_merkle = None  # type: ignore
try:
    from bit_exact_replay import compare_runs, write_pin, pin_matrix
except Exception:
    compare_runs = write_pin = pin_matrix = None  # type: ignore
try:
    from ledger_index import summary as ledger_summary, search as ledger_search, find_ledgers
except Exception:
    ledger_summary = ledger_search = find_ledgers = None  # type: ignore


def list_runs(artifacts_root: str = "artifacts") -> List[Dict[str, Any]]:
    root = Path(artifacts_root)
    if not root.exists():
        return []
    runs = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p.name.startswith("run_") or p.name in ("run_scaled", "run_complete")):
            runs.append({
                "run_id": p.name,
                "path": str(p),
                "has_reports": (p / "reports").exists(),
                "has_audits": (p / "audits").exists(),
            })
    return runs


def load_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": "missing", "path": path}
    return json.loads(p.read_text(encoding="utf-8"))


def run_summary(run_dir: str) -> Dict[str, Any]:
    base = Path(run_dir)
    candidates = [
        base / "reports" / "run_summary.json",
        base / "reports" / "final_summary.json",
    ]
    for c in candidates:
        if c.exists():
            return load_json(str(c))
    return {"ok": False, "error": "no_summary"}


def merkle(run_dir: str, write: bool = False) -> Dict[str, Any]:
    if build_merkle is None:
        return {"ok": False, "error": "merkle_unavailable"}
    if write and write_merkle:
        return write_merkle(run_dir)
    return build_merkle(run_dir)


def pin(run_dir: str) -> Dict[str, Any]:
    if write_pin is None:
        return {"ok": False, "error": "pin_unavailable"}
    path = write_pin(run_dir)
    return {"ok": True, "path": str(path), "matrix": pin_matrix() if pin_matrix else {}}


def compare(run_a: str, run_b: str) -> Dict[str, Any]:
    if compare_runs is None:
        return {"ok": False, "error": "compare_unavailable"}
    return compare_runs(run_a, run_b)


def ledgers(artifacts_root: str = "artifacts") -> Dict[str, Any]:
    if ledger_summary is None:
        return {"ok": False, "error": "ledger_index_unavailable"}
    return ledger_summary(artifacts_root)


def ledger_query(query: str, artifacts_root: str = "artifacts", limit: int = 20) -> List[Dict[str, Any]]:
    if ledger_search is None:
        return []
    return ledger_search(query, root=artifacts_root, limit=limit)
