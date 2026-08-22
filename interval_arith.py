#!/usr/bin/env python3
"""Interval arithmetic for rigorous numeric enclosures (not point estimates)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Interval:
    lo: float
    hi: float

    def __post_init__(self):
        if self.lo > self.hi:
            self.lo, self.hi = self.hi, self.lo

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other: "Interval") -> "Interval":
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other: "Interval") -> "Interval":
        candidates = [
            self.lo * other.lo, self.lo * other.hi,
            self.hi * other.lo, self.hi * other.hi,
        ]
        return Interval(min(candidates), max(candidates))

    def contains(self, x: float) -> bool:
        return self.lo <= x <= self.hi

    def width(self) -> float:
        return self.hi - self.lo

    def to_dict(self) -> Dict[str, float]:
        return {"lo": self.lo, "hi": self.hi}


def net_edge_interval(
    output: Interval,
    costs: Interval,
) -> Interval:
    """edge = output - costs, interval valued."""
    return output - costs


def trade_allowed_by_interval(edge: Interval, min_edge: float) -> Dict[str, Any]:
    """Allow only if entire interval is above min_edge (worst-case)."""
    ok = edge.lo >= min_edge
    return {
        "allow_trade": ok,
        "edge": edge.to_dict(),
        "min_edge": min_edge,
        "worst_case": edge.lo,
        "best_case": edge.hi,
    }
