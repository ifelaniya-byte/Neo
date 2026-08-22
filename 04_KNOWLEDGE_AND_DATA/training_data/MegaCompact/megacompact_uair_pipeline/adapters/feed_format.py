#!/usr/bin/env python3
"""
Canonical data feed format for MegaCompact paper simulation.

Feed file: JSON object with schema_version=1.0.0 and an events[] array.
Each event MUST include event/observed/available timestamps for causality.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from adapters.historical import HistoricalAdapter, NormalizedHistoricalEvent

SCHEMA_VERSION = "1.0.0"
REQUIRED_EVENT_FIELDS = (
    "event_id",
    "entity_id",
    "event_timestamp_ms",
    "observed_timestamp_ms",
    "available_timestamp_ms",
    "event_type",
)


def _checksum_event(ev: Dict[str, Any]) -> str:
    body = {k: ev[k] for k in sorted(ev) if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_event(ev: Dict[str, Any]) -> Dict[str, Any]:
    missing = [f for f in REQUIRED_EVENT_FIELDS if f not in ev or ev[f] in (None, "")]
    if missing:
        return {"ok": False, "missing": missing}
    try:
        ets = int(ev["event_timestamp_ms"])
        ots = int(ev["observed_timestamp_ms"])
        ats = int(ev["available_timestamp_ms"])
    except (TypeError, ValueError) as e:
        return {"ok": False, "error": f"timestamp_cast:{e}"}
    if ats < ets:
        return {"ok": False, "error": "available_timestamp_ms < event_timestamp_ms", "causality": False}
    if ots < ets:
        return {"ok": False, "error": "observed_timestamp_ms < event_timestamp_ms"}
    return {"ok": True, "causality": True}


def validate_feed(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        return {"ok": False, "error": "feed_not_object"}
    if doc.get("schema_version") != SCHEMA_VERSION:
        return {"ok": False, "error": "schema_version_mismatch", "got": doc.get("schema_version")}
    for key in ("feed_id", "chain_id", "events"):
        if key not in doc:
            return {"ok": False, "error": f"missing_{key}"}
    events = doc["events"]
    if not isinstance(events, list) or len(events) < 1:
        return {"ok": False, "error": "events_empty"}
    failures = []
    for i, ev in enumerate(events):
        r = validate_event(ev)
        if not r.get("ok"):
            failures.append({"index": i, "event_id": ev.get("event_id"), **r})
    return {
        "ok": len(failures) == 0,
        "n_events": len(events),
        "failures": failures,
        "feed_id": doc.get("feed_id"),
        "schema_version": doc.get("schema_version"),
    }


def load_feed(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    report = validate_feed(doc)
    report["path"] = str(path)
    return {"doc": doc, "validation": report}


def feed_to_pipeline_events(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert validated feed events to pipeline-normalized dicts."""
    out = []
    chain = int(doc.get("chain_id") or 42161)
    for ev in doc.get("events") or []:
        row = dict(ev)
        row.setdefault("chain_id", chain)
        if "checksum" not in row:
            row["checksum"] = _checksum_event(row)
        out.append({
            "event_id": row["event_id"],
            "entity_id": row["entity_id"],
            "event_timestamp_ms": int(row["event_timestamp_ms"]),
            "observed_timestamp_ms": int(row["observed_timestamp_ms"]),
            "available_timestamp_ms": int(row["available_timestamp_ms"]),
            "event_type": row["event_type"],
            "chain_id": int(row.get("chain_id", chain)),
            "payload": row.get("payload") or {},
            "checksum": row.get("checksum"),
            "source": doc.get("source") or doc.get("feed_id"),
        })
    return out


def write_example_feed(path: Union[str, Path], n: int = 5) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = 1_700_000_000_000
    events = []
    for i in range(n):
        ets = base + i * 12_000
        ev = {
            "event_id": f"feed_ex_{i}",
            "entity_id": "pool_demo",
            "event_timestamp_ms": ets,
            "observed_timestamp_ms": ets + 200,
            "available_timestamp_ms": ets + 500,
            "event_type": "quote",
            "chain_id": 42161,
            "payload": {
                "mid_usd": 100.0 + i * 0.05,
                "bid_usd": 99.95 + i * 0.05,
                "ask_usd": 100.05 + i * 0.05,
                "gas_gwei": 0.05,
            },
        }
        ev["checksum"] = _checksum_event(ev)
        events.append(ev)
    doc = {
        "feed_id": "example_feed_v1",
        "schema_version": SCHEMA_VERSION,
        "chain_id": 42161,
        "source": "synthetic_example",
        "as_of": "2026-08-19",
        "license": "CC0-1.0",
        "events": events,
    }
    path.write_text(json.dumps(doc, indent=2))
    return path


def ingest_feed_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load + validate + convert. Fail-closed on validation errors."""
    loaded = load_feed(path)
    val = loaded["validation"]
    if not val.get("ok"):
        return {"ok": False, "validation": val, "events": []}
    events = feed_to_pipeline_events(loaded["doc"])
    return {"ok": True, "validation": val, "events": events, "n": len(events)}
