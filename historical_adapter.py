#!/usr/bin/env python3
"""
Historical market/event adapters + availability-stamped normalization.
Paper/research only — no live signing or broadcast.
"""
from __future__ import annotations
import csv
import json
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator
from datetime import datetime, timezone


@dataclass
class NormalizedHistoricalEvent:
    event_id: str
    event_timestamp_ms: int
    available_timestamp_ms: int
    observed_timestamp_ms: int
    event_type: str
    chain_id: int
    venue: str
    payload: Dict[str, Any]
    source: str
    source_row: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HistoricalAdapter(ABC):
    """Protocol for historical data sources with time-causality fields."""

    @abstractmethod
    def iter_events(self) -> Iterator[NormalizedHistoricalEvent]:
        ...

    def load_all(self) -> List[NormalizedHistoricalEvent]:
        return list(self.iter_events())


class JSONLHistoricalAdapter(HistoricalAdapter):
    """Load events from JSONL (each line a dict with required time fields)."""

    def __init__(self, path: str, chain_id: int = 42161, availability_delay_ms: int = 0):
        self.path = Path(path)
        self.chain_id = chain_id
        self.availability_delay_ms = availability_delay_ms

    def iter_events(self) -> Iterator[NormalizedHistoricalEvent]:
        if not self.path.exists():
            return
        with self.path.open() as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                ts = int(raw.get("event_timestamp_ms") or raw.get("timestamp_ms") or 0)
                avail = int(raw.get("available_timestamp_ms") or (ts + self.availability_delay_ms))
                obs = int(raw.get("observed_timestamp_ms") or avail)
                eid = str(raw.get("event_id") or f"hist_{self.path.stem}_{i}")
                yield NormalizedHistoricalEvent(
                    event_id=eid,
                    event_timestamp_ms=ts,
                    available_timestamp_ms=avail,
                    observed_timestamp_ms=obs,
                    event_type=str(raw.get("event_type") or "quote"),
                    chain_id=int(raw.get("chain_id") or self.chain_id),
                    venue=str(raw.get("venue") or "unknown"),
                    payload=raw.get("payload") or {k: v for k, v in raw.items()
                                                   if k not in ("event_id", "event_timestamp_ms",
                                                                "available_timestamp_ms", "observed_timestamp_ms")},
                    source=str(self.path),
                    source_row=i,
                )


class CSVHistoricalAdapter(HistoricalAdapter):
    """Minimal CSV adapter: columns event_id, event_timestamp_ms, available_timestamp_ms, ..."""

    def __init__(self, path: str, chain_id: int = 42161, availability_delay_ms: int = 0):
        self.path = Path(path)
        self.chain_id = chain_id
        self.availability_delay_ms = availability_delay_ms

    def iter_events(self) -> Iterator[NormalizedHistoricalEvent]:
        if not self.path.exists():
            return
        with self.path.open(newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                ts = int(float(row.get("event_timestamp_ms") or row.get("timestamp_ms") or 0))
                avail = int(float(row.get("available_timestamp_ms") or (ts + self.availability_delay_ms)))
                obs = int(float(row.get("observed_timestamp_ms") or avail))
                eid = str(row.get("event_id") or f"csv_{self.path.stem}_{i}")
                yield NormalizedHistoricalEvent(
                    event_id=eid,
                    event_timestamp_ms=ts,
                    available_timestamp_ms=avail,
                    observed_timestamp_ms=obs,
                    event_type=str(row.get("event_type") or "quote"),
                    chain_id=int(row.get("chain_id") or self.chain_id),
                    venue=str(row.get("venue") or "csv"),
                    payload=dict(row),
                    source=str(self.path),
                    source_row=i,
                )


def adapter_from_path(path: str, **kwargs) -> HistoricalAdapter:
    p = Path(path)
    if p.suffix.lower() == ".jsonl":
        return JSONLHistoricalAdapter(path, **kwargs)
    if p.suffix.lower() == ".csv":
        return CSVHistoricalAdapter(path, **kwargs)
    raise ValueError(f"Unsupported historical format: {p.suffix}")


def validate_causality(events: List[NormalizedHistoricalEvent]) -> Dict[str, Any]:
    """Fail-closed causality: available >= observed >= event (or available >= event)."""
    bad = []
    for e in events:
        if e.available_timestamp_ms < e.event_timestamp_ms:
            bad.append({"event_id": e.event_id, "reason": "available < event"})
        if e.observed_timestamp_ms < e.event_timestamp_ms:
            bad.append({"event_id": e.event_id, "reason": "observed < event"})
    return {"ok": len(bad) == 0, "n": len(events), "violations": bad[:20]}
