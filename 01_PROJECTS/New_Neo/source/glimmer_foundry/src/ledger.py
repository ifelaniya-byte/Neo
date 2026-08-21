"""Betting Ledger — tracks verified gains vs failures + estimated cost."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Ledger:
    winnings: float = 0.0          # cumulative verified score gains
    losses: float = 0.0            # failures + estimated GPU cost
    accepted: int = 0
    rejected: int = 0
    gpu_hours: float = 0.0
    cost_per_hour: float = 0.20    # Vast/RunPod 4090 ballpark
    started_at: float = field(default_factory=time.time)
    events: list[dict] = field(default_factory=list)

    @property
    def profit(self) -> float:
        return self.winnings - self.losses

    def record_accept(self, delta_score: float = 1.0) -> None:
        self.accepted += 1
        self.winnings += max(0.0, delta_score)
        self.events.append({"t": time.time(), "kind": "accept", "delta": delta_score})

    def record_reject(self, penalty: float = 0.1) -> None:
        self.rejected += 1
        self.losses += penalty
        self.events.append({"t": time.time(), "kind": "reject", "penalty": penalty})

    def tick_gpu(self, hours: float) -> None:
        self.gpu_hours += hours
        self.losses += hours * self.cost_per_hour

    def to_dict(self) -> dict:
        d = asdict(self)
        d["profit"] = self.profit
        d["uptime_sec"] = time.time() - self.started_at
        return d

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        p = Path(path)
        if not p.exists():
            return cls()
        with open(p) as f:
            data = json.load(f)
        # strip computed fields
        data.pop("profit", None)
        data.pop("uptime_sec", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
