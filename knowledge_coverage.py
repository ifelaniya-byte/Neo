#!/usr/bin/env python3
"""
Next-best alternative to a rejected 'complete world physics' oracle.

Rejected: omniscient / conclusive complete physics.
This module: maximize *coverage and honesty* of settled + atlas + open gaps
+ evidence attachment — without ever claiming completeness.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from atlas import get_atlas
from known_settled_db import get_settled_db
from rag_settled import search as rag_search
from constants_db import get_constants_db


def coverage_report(query: Optional[str] = None) -> Dict[str, Any]:
    atlas = get_atlas()
    db = get_settled_db()
    const = get_constants_db()
    report = {
        "title": "KnowledgeCoverageMaximizer",
        "disclaimer": (
            "Maximizes structured coverage of settled knowledge, formulas, constants, "
            "and explicit OPEN gaps. Not a theory of everything. Not conclusive world physics."
        ),
        "n_settled": len(db.entries),
        "n_formulas": len(atlas.formulas),
        "n_domains": len(atlas.domains),
        "n_languages": len(atlas.languages),
        "n_constants": len(const.constants),
        "n_open_problems": len(atlas.open_problems()),
        "open_problems": atlas.open_problems(),
        "completeness_claim_allowed": False,
    }
    if query:
        report["settled_hits"] = db.search(query, limit=8)
        report["atlas_hits"] = atlas.search(query, limit=8)
        report["rag_hits"] = rag_search(query, limit=5)
        report["claim_gate"] = db.reject_completeness_claim(query)
        report["atlas_claim_gate"] = atlas.verify_claim(query)
    return report


def best_effort_answer(query: str) -> Dict[str, Any]:
    """Best-effort grounded pack: settled + atlas + rag + opens — never final truth."""
    cov = coverage_report(query)
    return {
        "query": query,
        "mode": "best_effort_coverage",
        "not_a_complete_oracle": True,
        "coverage": cov,
        "recommendation": (
            "Use settled hits when assumptions match; treat OPEN domains as unknown; "
            "abstain on completeness-style questions."
        ),
    }


def evidence_for_decision(
    packet_summary: Optional[Dict[str, Any]] = None,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Attach knowledge coverage as *evidence* for plan_and_decide.

    Never overrides AbstentionGate / SMT / interval. Completeness claims stay blocked.
    """
    q = query or "causality net pnl abstain costs time-causal"
    if packet_summary:
        # light topical boost from packet fields if present
        bits = []
        for k in ("regime", "venue", "chain_id", "event_type"):
            if packet_summary.get(k) is not None:
                bits.append(str(packet_summary[k]))
        if bits:
            q = q + " " + " ".join(bits)
    pack = best_effort_answer(q)
    # Strip heavy nested dumps for decision attachment
    cov = pack.get("coverage") or {}
    return {
        "role": "evidence_only",
        "not_authority": True,
        "not_a_complete_oracle": True,
        "completeness_claim_allowed": False,
        "query": pack.get("query"),
        "n_settled_hits": len(cov.get("settled_hits") or []),
        "n_atlas_hits": len(cov.get("atlas_hits") or []),
        "n_rag_hits": len(cov.get("rag_hits") or []),
        "n_open_problems": cov.get("n_open_problems"),
        "claim_gate_ok": (cov.get("claim_gate") or {}).get("ok", True),
        "recommendation": pack.get("recommendation"),
        "settled_ids": [h.get("id") for h in (cov.get("settled_hits") or [])[:5] if isinstance(h, dict)],
        "rag_doc_ids": [h.get("doc_id") for h in (cov.get("rag_hits") or [])[:5] if isinstance(h, dict)],
    }
