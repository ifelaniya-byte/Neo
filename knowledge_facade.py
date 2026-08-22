#!/usr/bin/env python3
"""Unified knowledge facade: atlas + KSKB + constants + rag + coverage (no completeness claim)."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from atlas import get_atlas
from known_settled_db import get_settled_db
from constants_db import get_constants_db
from rag_settled import search as rag_search, load_corpus
from knowledge_coverage import coverage_report, best_effort_answer


class KnowledgeFacade:
    def __init__(self):
        self.atlas = get_atlas()
        self.settled = get_settled_db()
        self.constants = get_constants_db()

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "query": query,
            "settled": self.settled.search(query, limit=limit),
            "atlas": self.atlas.search(query, limit=limit),
            "rag": rag_search(query, limit=min(5, limit)),
            "disclaimer": "Best-effort coverage only; not a complete oracle.",
        }

    def constant(self, id_: str) -> Optional[Dict[str, Any]]:
        return self.constants.get(id_)

    def coverage(self, query: Optional[str] = None) -> Dict[str, Any]:
        return coverage_report(query)

    def answer(self, query: str) -> Dict[str, Any]:
        return best_effort_answer(query)

    def stats(self) -> Dict[str, Any]:
        return {
            "n_settled": len(self.settled.entries),
            "n_formulas": len(self.atlas.formulas),
            "n_domains": len(self.atlas.domains),
            "n_languages": len(self.atlas.languages),
            "n_constants": len(self.constants.constants),
            "n_rag_docs": len(load_corpus()),
            "n_open_problems": len(self.atlas.open_problems()),
            "completeness_claim_allowed": False,
        }


def get_facade() -> KnowledgeFacade:
    return KnowledgeFacade()
