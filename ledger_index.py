#!/usr/bin/env python3
"""Cross-run index over verification_ledger.jsonl files under artifacts/.

Speed policy (product work on full):
  - Cap number of ledger files and lines scanned (default) so engineer passes
    stay O(1)-ish even when artifacts/ accumulates many runs.
  - Set MEGACOMPACT_LEDGER_ROOT or pass root= to narrow scope.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Defaults tuned for lab CI / adversarial speed
_MAX_LEDGER_FILES = int(os.environ.get("MEGACOMPACT_MAX_LEDGER_FILES", "12"))
_MAX_LINES_PER_FILE = int(os.environ.get("MEGACOMPACT_MAX_LEDGER_LINES", "200"))


def find_ledgers(root: str = "artifacts") -> List[Path]:
    root_p = Path(root)
    if not root_p.exists():
        return []
    paths = sorted(root_p.rglob("verification_ledger.jsonl")) + sorted(
        root_p.rglob("*_ledger.jsonl")
    )
    # Prefer newest by mtime; cap count
    paths = sorted(paths, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return paths[:_MAX_LEDGER_FILES]


def load_entries(paths: Optional[List[Path]] = None, root: str = "artifacts") -> List[Dict[str, Any]]:
    paths = paths or find_ledgers(root)
    entries = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                # Read only the tail for large files (recent patterns matter most)
                lines = f.readlines()
                if len(lines) > _MAX_LINES_PER_FILE:
                    lines = lines[-_MAX_LINES_PER_FILE:]
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rec["_ledger_path"] = str(p)
                    rec["_line"] = i + 1
                    entries.append(rec)
        except OSError:
            continue
    return entries


def search(
    query: str,
    root: str = "artifacts",
    event_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    q = query.lower().strip()
    out = []
    for rec in load_entries(root=root):
        if event_type and rec.get("event_type") != event_type:
            continue
        blob = json.dumps(rec, default=str).lower()
        if not q or q in blob:
            out.append(rec)
        if len(out) >= limit:
            break
    return out[:limit]


def stats(root: str = "artifacts") -> Dict[str, Any]:
    paths = find_ledgers(root)
    entries = load_entries(paths, root=root)
    return {
        "n_ledger_files_scanned": len(paths),
        "n_entries_loaded": len(entries),
        "max_files": _MAX_LEDGER_FILES,
        "max_lines_per_file": _MAX_LINES_PER_FILE,
    }
