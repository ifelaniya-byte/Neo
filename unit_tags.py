#!/usr/bin/env python3
"""Unit tags on feature payloads + optional dimensional checks via constants_db."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from constants_db import get_constants_db


def tag_feature(name: str, value: float, unit: str, kind: str = "scalar") -> Dict[str, Any]:
    return {"name": name, "value": value, "unit": unit, "kind": kind}


def attach_unit_tags(payload: Dict[str, Any], tags: List[Dict[str, Any]]) -> Dict[str, Any]:
    out = dict(payload)
    out["unit_tags"] = tags
    return out


def check_length_pair(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Convert both to meters and compare magnitudes if both are lengths."""
    length_units = {"m", "cm", "mm", "km", "nm", "angstrom"}
    if a.get("unit") not in length_units or b.get("unit") not in length_units:
        return {"ok": True, "skipped": True, "reason": "not_both_length"}
    cdb = get_constants_db()
    try:
        av = cdb.convert_length(float(a["value"]), a["unit"], "m")
        bv = cdb.convert_length(float(b["value"]), b["unit"], "m")
        return {"ok": True, "a_m": av, "b_m": bv, "ratio": (av / bv) if bv else None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stationary_unit_probe(payload: Dict[str, Any]) -> Dict[str, Any]:
    tags = payload.get("unit_tags") or []
    if not tags:
        return {"ok": True, "n_tags": 0, "note": "no unit tags"}
    bad = [t for t in tags if "unit" not in t or "value" not in t]
    return {"ok": len(bad) == 0, "n_tags": len(tags), "malformed": len(bad)}
