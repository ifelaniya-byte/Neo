#!/usr/bin/env python3
"""Pinned physical/math constants + simple unit conversions (CODATA-style snapshot)."""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

CONSTANTS_VERSION = "2026-snapshot-local"

@dataclass
class Constant:
    id: str
    name: str
    value: float
    unit: str
    source: str = "CODATA-style curated snapshot"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ConstantsDB:
    def __init__(self):
        self.version = CONSTANTS_VERSION
        self.constants: Dict[str, Constant] = {}
        self._build()

    def _add(self, c: Constant) -> None:
        self.constants[c.id] = c

    def _build(self) -> None:
        rows = [
            ("c", "speed of light in vacuum", 299792458.0, "m/s", "exact SI"),
            ("h", "Planck constant", 6.62607015e-34, "J s", "exact SI"),
            ("hbar", "reduced Planck constant", 1.054571817e-34, "J s", "h/(2π)"),
            ("e", "elementary charge", 1.602176634e-19, "C", "exact SI"),
            ("k_B", "Boltzmann constant", 1.380649e-23, "J/K", "exact SI"),
            ("N_A", "Avogadro constant", 6.02214076e23, "1/mol", "exact SI"),
            ("R", "molar gas constant", 8.314462618, "J/(mol K)", "N_A k_B"),
            ("G", "Newtonian gravitational constant", 6.67430e-11, "m^3/(kg s^2)", "CODATA recommended"),
            ("epsilon0", "vacuum electric permittivity", 8.8541878128e-12, "F/m", "derived"),
            ("mu0", "vacuum magnetic permeability", 1.25663706212e-6, "N/A^2", "derived"),
            ("m_e", "electron mass", 9.1093837015e-31, "kg", "CODATA"),
            ("m_p", "proton mass", 1.67262192369e-27, "kg", "CODATA"),
            ("alpha", "fine-structure constant", 7.2973525693e-3, "1", "CODATA"),
            ("g", "standard gravity", 9.80665, "m/s^2", "conventional"),
            ("pi", "pi", 3.141592653589793, "1", "math"),
            ("e_euler", "Euler's number", 2.718281828459045, "1", "math"),
        ]
        for id_, name, val, unit, notes in rows:
            self._add(Constant(id=id_, name=name, value=val, unit=unit, notes=notes))

    def get(self, id_: str) -> Optional[Dict[str, Any]]:
        c = self.constants.get(id_)
        return c.to_dict() if c else None

    def convert_length(self, value: float, from_u: str, to_u: str) -> float:
        to_m = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "nm": 1e-9, "angstrom": 1e-10}
        if from_u not in to_m or to_u not in to_m:
            raise ValueError(f"unsupported length units: {from_u}->{to_u}")
        return value * to_m[from_u] / to_m[to_u]

    def convert_energy(self, value: float, from_u: str, to_u: str) -> float:
        # to Joules
        to_j = {"J": 1.0, "eV": 1.602176634e-19, "keV": 1.602176634e-16, "MeV": 1.602176634e-13}
        if from_u not in to_j or to_u not in to_j:
            raise ValueError(f"unsupported energy units: {from_u}->{to_u}")
        return value * to_j[from_u] / to_j[to_u]

    def export(self) -> Dict[str, Any]:
        return {"version": self.version, "n": len(self.constants),
                "constants": [c.to_dict() for c in self.constants.values()]}

_DB = None

def get_constants_db() -> ConstantsDB:
    global _DB
    if _DB is None:
        _DB = ConstantsDB()
    return _DB
