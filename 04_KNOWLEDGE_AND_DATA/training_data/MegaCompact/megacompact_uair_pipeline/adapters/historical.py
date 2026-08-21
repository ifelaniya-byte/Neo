#!/usr/bin/env python3
"""
Historical data adapters for paper-only simulation assurance.

Provides normalized, availability-timestamped events from local files
(CSV / JSONL / parquet when pyarrow present). Never signs or broadcasts.
Live RPC remains opt-in and read-only via chain_observer_ro.
"""
from __future__ import annotations

import csv
import json
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union


@dataclass
class NormalizedHistoricalEvent:
    event_id: str
    event_timestamp_ms: int
    available_timestamp_ms: int
    event_type: str
    chain_id: int
    payload: Dict[str, Any]
    source: str
    source_row: int = 0
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _row_checksum(row: Dict[str, Any]) -> str:
    raw = json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode()
    return _sha256_hex(raw)


class HistoricalAdapter:
    """
    Load historical market-like events into the same NormalizedEvent shape
    the pipeline expects, with explicit available_timestamp_ms.
    """

    def __init__(
        self,
        chain_id: int = 42161,
        availability_lag_ms: int = 0,
        default_event_type: str = "quote",
    ):
        self.chain_id = chain_id
        self.availability_lag_ms = availability_lag_ms
        self.default_event_type = default_event_type

    def from_jsonl(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        out: List[NormalizedHistoricalEvent] = []
        with path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                out.append(self._normalize(row, source=str(path), source_row=i))
        return out

    def from_csv(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        out: List[NormalizedHistoricalEvent] = []
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # coerce numeric-looking fields
                coerced: Dict[str, Any] = {}
                for k, v in row.items():
                    if v is None or v == "":
                        coerced[k] = v
                        continue
                    try:
                        if "." in str(v):
                            coerced[k] = float(v)
                        else:
                            coerced[k] = int(v)
                    except ValueError:
                        coerced[k] = v
                out.append(self._normalize(coerced, source=str(path), source_row=i))
        return out

    def from_parquet(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        try:
            import pyarrow.parquet as pq  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "pyarrow required for parquet historical adapter; use JSONL/CSV otherwise"
            ) from e
        table = pq.read_table(path)
        rows = table.to_pylist()
        return [
            self._normalize(row, source=str(path), source_row=i)
            for i, row in enumerate(rows)
        ]

    def from_records(self, rows: List[Dict[str, Any]], source: str = "records") -> List[NormalizedHistoricalEvent]:
        return [self._normalize(r, source=source, source_row=i) for i, r in enumerate(rows)]

    def _normalize(self, row: Dict[str, Any], source: str, source_row: int) -> NormalizedHistoricalEvent:
        ts = int(row.get("event_timestamp_ms") or row.get("timestamp_ms") or row.get("ts_ms") or 0)
        avail = int(row.get("available_timestamp_ms") or (ts + self.availability_lag_ms))
        eid = str(row.get("event_id") or f"{Path(source).stem}_{source_row}_{ts}")
        etype = str(row.get("event_type") or self.default_event_type)
        chain = int(row.get("chain_id") or self.chain_id)
        payload = {k: v for k, v in row.items() if k not in (
            "event_id", "event_timestamp_ms", "available_timestamp_ms",
            "event_type", "chain_id", "timestamp_ms", "ts_ms"
        )}
        # Ensure causality: available >= event
        if avail < ts:
            avail = ts
        return NormalizedHistoricalEvent(
            event_id=eid,
            event_timestamp_ms=ts,
            available_timestamp_ms=avail,
            event_type=etype,
            chain_id=chain,
            payload=payload,
            source=source,
            source_row=source_row,
            checksum=_row_checksum(row),
        )

    def iter_as_pipeline_events(self, events: List[NormalizedHistoricalEvent]) -> Iterator[Dict[str, Any]]:
        """Yield dicts compatible with engineer/schema NormalizedEvent checks."""
        for e in events:
            yield {
                "event_id": e.event_id,
                "event_timestamp_ms": e.event_timestamp_ms,
                "available_timestamp_ms": e.available_timestamp_ms,
                "event_type": e.event_type,
                "chain_id": e.chain_id,
                "payload": e.payload,
                "source": e.source,
                "checksum": e.checksum,
            }


def write_sample_jsonl(path: Union[str, Path], n: int = 5) -> Path:
    """Write a small synthetic historical file for demos/tests."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = 1_700_000_000_000
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            row = {
                "event_id": f"hist_{i}",
                "event_timestamp_ms": base + i * 12_000,
                "available_timestamp_ms": base + i * 12_000 + 500,
                "event_type": "quote",
                "chain_id": 42161,
                "mid_usd": 100.0 + i * 0.1,
                "bid_usd": 99.9 + i * 0.1,
                "ask_usd": 100.1 + i * 0.1,
                "gas_gwei": 0.05,
            }
            f.write(json.dumps(row) + "\n")
    return path
