#!/usr/bin/env python3
"""Ordered registry of Stationary engineer check names (documentation + flags)."""
from __future__ import annotations
from typing import Dict, List

# name -> enabled by default
STATIONARY_CHECKS: Dict[str, bool] = {
    "subject_present": True,
    "schema.non_empty_dict": True,
    "schema_registry.required": True,
    "causality.timestamps": True,
    "accounting.net_pnl": True,
    "finite.nan_inf": True,
    "source.ast_parse": True,
    "math.arithmetic_identity": True,
    "math.isfinite_pi": True,
    "logic.no_contradiction": True,
    "atlas.claim_gate": True,
    "atlas.catalogue_loaded": True,
    "settled_db.loaded": True,
    "settled_db.no_completeness_overclaim": True,
    "ledger_memory.recent_patterns": True,
    "rag_settled.evidence": True,
    "sympy.identity": True,
    "constants.lookup": True,
    "unit_tags.probe": True,
}

def enabled_checks() -> List[str]:
    return [k for k, v in STATIONARY_CHECKS.items() if v]
