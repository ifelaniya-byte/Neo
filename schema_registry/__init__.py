"""Versioned schema registry for events, packets, labels."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).parent

def list_schemas() -> List[str]:
    return sorted(p.name for p in _ROOT.glob("*.json"))

def load_schema(name: str) -> Dict[str, Any]:
    path = _ROOT / name
    if not path.exists():
        # allow short names
        path = _ROOT / f"{name}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def validate_required(obj: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in schema.get("required", []) if k not in obj]
    return {"ok": len(missing) == 0, "missing": missing, "schema_id": schema.get("schema_id")}
