#!/usr/bin/env python3
"""
Read-only chain observer interface with availability timestamps.
Does NOT sign or broadcast. Network fetch is optional and explicit.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import time


@dataclass
class ObservedEvent:
    event_id: str
    event_timestamp_ms: int
    observed_timestamp_ms: int
    available_timestamp_ms: int
    chain_id: int
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReadOnlyObserver:
    def __init__(self, chain_id: int = 42161, availability_delay_ms: int = 0):
        self.chain_id = chain_id
        self.availability_delay_ms = availability_delay_ms
        self._buffer: List[ObservedEvent] = []

    def ingest_local(self, event_id: str, event_timestamp_ms: int, payload: Dict[str, Any]) -> ObservedEvent:
        now = int(time.time() * 1000)
        ev = ObservedEvent(
            event_id=event_id,
            event_timestamp_ms=event_timestamp_ms,
            observed_timestamp_ms=now,
            available_timestamp_ms=now + self.availability_delay_ms,
            chain_id=self.chain_id,
            payload=payload,
        )
        self._buffer.append(ev)
        return ev

    def poll(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._buffer]

    def fetch_rpc_disabled(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "reason": "live_rpc_disabled_by_default",
            "note": "Enable only in explicit readonly config; never signing keys",
        }
