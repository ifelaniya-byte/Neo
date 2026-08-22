#!/usr/bin/env python3
"""Merkle-style hash tree over a run artifact directory."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _node_hash(left: str, right: str) -> str:
    return hashlib.sha256((left + right).encode()).hexdigest()


def build_merkle(root: str) -> Dict[str, Any]:
    root_p = Path(root)
    files = sorted([p for p in root_p.rglob("*") if p.is_file() and p.stat().st_size < 50_000_000])
    leaves: List[Tuple[str, str]] = [(str(p.relative_to(root_p)), _file_hash(p)) for p in files]
    if not leaves:
        return {"root": None, "n_files": 0, "leaves": []}
    layer = [h for _, h in leaves]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a
            nxt.append(_node_hash(a, b))
        layer = nxt
    return {
        "merkle_root": layer[0],
        "n_files": len(leaves),
        "leaves": [{"path": p, "sha256": h} for p, h in leaves],
    }


def write_merkle(root: str, out_name: str = "hashes/merkle.json") -> Dict[str, Any]:
    tree = build_merkle(root)
    out = Path(root) / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tree, indent=2))
    return tree
