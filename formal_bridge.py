#!/usr/bin/env python3
"""
Optional bridge to external formal kernels (Lean/Coq/Isabelle).
Does not embed a kernel — only defines the interface and offline invocation contract.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import shutil
import subprocess


def kernel_available() -> Dict[str, bool]:
    return {
        "lean": bool(shutil.which("lean")),
        "coqc": bool(shutil.which("coqc")),
        "isabelle": bool(shutil.which("isabelle")),
    }


def submit_obligation(statement_id: str, formal_text: str, out_dir: str = "artifacts/formal") -> Dict[str, Any]:
    """
    Write an obligation file for external checking.
    Returns path; does not claim proven unless kernel returns success.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{statement_id}.txt"
    path.write_text(
        f"OBLIGATION {statement_id}\n"
        f"STATUS: unchecked\n"
        f"FORMAL:\n{formal_text}\n"
        f"NOTE: Run external kernel; do not treat as proven until kernel accepts.\n"
    )
    return {
        "ok": True,
        "path": str(path),
        "proven": False,
        "kernels": kernel_available(),
        "note": "unchecked until external kernel accepts",
    }


def try_lean_check(file_path: str) -> Dict[str, Any]:
    if not shutil.which("lean"):
        return {"ok": False, "proven": False, "reason": "lean_not_installed"}
    try:
        proc = subprocess.run(
            ["lean", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "ok": proc.returncode == 0,
            "proven": proc.returncode == 0,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
    except Exception as e:
        return {"ok": False, "proven": False, "error": str(e)}
