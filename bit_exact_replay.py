#!/usr/bin/env python3
"""
Bit-exact / deterministic replay helpers: pin matrix + artifact compare + proof.
Supports cross-run and cross-machine replay proofs (hash equality under pin matrix).
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def pin_matrix() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "machine": platform.machine(),
        "implementation": platform.python_implementation(),
        "hash_seed": os.environ.get("PYTHONHASHSEED", "unset"),
        "hash_seed_note": "PYTHONHASHSEED=0 recommended for stable hashing",
        "timezone": "UTC",
    }


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    return hash_bytes(path.read_bytes())


def hash_json_canonical(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hash_bytes(raw)


def collect_run_hashes(run_dir: str, rel_paths: Optional[List[str]] = None) -> Dict[str, str]:
    root = Path(run_dir)
    rel_paths = rel_paths or [
        "reports/run_summary.json",
        "audits/audit_results.json",
        "hashes/merkle.json",
        "hashes/pin_matrix.json",
    ]
    out: Dict[str, str] = {}
    for rel in rel_paths:
        p = root / rel
        if p.exists():
            out[rel] = hash_file(p)
        else:
            out[rel] = "MISSING"
    return out


def compare_runs(run_a: str, run_b: str, rel_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    a_hashes = collect_run_hashes(run_a, rel_paths)
    b_hashes = collect_run_hashes(run_b, rel_paths)
    diffs = []
    keys = sorted(set(a_hashes) | set(b_hashes))
    for k in keys:
        ha, hb = a_hashes.get(k, "MISSING"), b_hashes.get(k, "MISSING")
        if ha != hb:
            diffs.append({"path": k, "status": "mismatch" if ha != "MISSING" and hb != "MISSING" else "missing_side",
                          "a": ha[:16] if ha != "MISSING" else "MISSING",
                          "b": hb[:16] if hb != "MISSING" else "MISSING"})
    return {
        "ok": len(diffs) == 0,
        "n_compared": len(keys),
        "diffs": diffs,
        "pin_matrix_a": pin_matrix(),
        "run_a": run_a,
        "run_b": run_b,
    }


def write_pin(run_dir: str) -> Path:
    path = Path(run_dir) / "hashes" / "pin_matrix.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pin_matrix(), indent=2))
    return path


def write_replay_proof(
    run_dir: str,
    reference_run: Optional[str] = None,
    rel_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Emit a replay proof artifact for this run (and optional cross-run compare).
    Product feature: labs can re-run and prove bit-exact equality under pin matrix.
    """
    run = Path(run_dir)
    hashes_dir = run / "hashes"
    hashes_dir.mkdir(parents=True, exist_ok=True)
    write_pin(run_dir)
    file_hashes = collect_run_hashes(run_dir, rel_paths)
    proof = {
        "version": "1.0.0-product",
        "kind": "bit_exact_replay_proof",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run),
        "pin_matrix": pin_matrix(),
        "file_hashes": file_hashes,
        "aggregate_hash": hash_json_canonical(file_hashes),
        "reference_compare": None,
        "ok": True,
        "note": "Re-run under same pin_matrix; compare aggregate_hash for bit-exact claim.",
    }
    if reference_run:
        cmp = compare_runs(run_dir, reference_run, rel_paths)
        proof["reference_compare"] = cmp
        proof["ok"] = bool(cmp.get("ok"))
    out = hashes_dir / "replay_proof.json"
    out.write_text(json.dumps(proof, indent=2))
    proof["path"] = str(out)
    return proof


# ---------------------------------------------------------------------------
# Product VD1: finished bit-exact replay proof API
# ---------------------------------------------------------------------------

def write_pin_matrix(run_dir: str) -> Dict[str, Any]:
    """Persist pin matrix under run_dir/hashes/pin_matrix.json."""
    root = Path(run_dir)
    hashes = root / "hashes"
    hashes.mkdir(parents=True, exist_ok=True)
    matrix = pin_matrix()
    matrix["written_at"] = datetime.now(timezone.utc).isoformat()
    path = hashes / "pin_matrix.json"
    path.write_text(json.dumps(matrix, indent=2, sort_keys=True))
    return {"ok": True, "path": str(path), "matrix": matrix}


def write_run_hashes(run_dir: str, rel_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    root = Path(run_dir)
    hashes_dir = root / "hashes"
    hashes_dir.mkdir(parents=True, exist_ok=True)
    collected = collect_run_hashes(run_dir, rel_paths)
    path = hashes_dir / "run_hashes.json"
    path.write_text(json.dumps(collected, indent=2, sort_keys=True))
    return {"ok": True, "path": str(path), "hashes": collected}


def replay_proof(
    run_a: str,
    run_b: str,
    rel_paths: Optional[List[str]] = None,
    require_pin_match: bool = True,
) -> Dict[str, Any]:
    """
    Cross-run / cross-machine bit-exact replay proof.

    Proof passes only if:
      - compared artifact hashes match
      - (optional) pin matrices are present and compatible
    """
    cmp = compare_runs(run_a, run_b, rel_paths)
    pin_a = Path(run_a) / "hashes" / "pin_matrix.json"
    pin_b = Path(run_b) / "hashes" / "pin_matrix.json"
    pin_report: Dict[str, Any] = {"present_a": pin_a.exists(), "present_b": pin_b.exists()}
    if pin_a.exists() and pin_b.exists():
        ma = json.loads(pin_a.read_text())
        mb = json.loads(pin_b.read_text())
        pin_report["match"] = (
            ma.get("python") == mb.get("python")
            and ma.get("hash_seed") == mb.get("hash_seed")
            and ma.get("implementation") == mb.get("implementation")
        )
        pin_report["a"] = {k: ma.get(k) for k in ("python", "platform", "machine", "hash_seed")}
        pin_report["b"] = {k: mb.get(k) for k in ("python", "platform", "machine", "hash_seed")}
    else:
        pin_report["match"] = False

    ok = bool(cmp.get("ok"))
    if require_pin_match and not pin_report.get("match"):
        ok = False

    return {
        "ok": ok,
        "artifact_compare": cmp,
        "pin_matrix": pin_report,
        "proof": "bit_exact_pass" if ok else "bit_exact_fail",
        "note": "Set PYTHONHASHSEED=0 and same deps for cross-machine proofs",
    }


def self_proof(run_dir: str) -> Dict[str, Any]:
    """Prove a run is bit-exact against itself after writing hashes + pin matrix."""
    write_pin_matrix(run_dir)
    write_run_hashes(run_dir)
    return replay_proof(run_dir, run_dir, require_pin_match=True)
