#!/usr/bin/env python3
"""Explicit causal DAG + simple d-separation style feature legality checks."""
from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple


class CausalGraph:
    def __init__(self):
        self.edges: Set[Tuple[str, str]] = set()  # parent -> child

    def add_edge(self, parent: str, child: str) -> None:
        self.edges.add((parent, child))

    def parents(self, node: str) -> Set[str]:
        return {p for p, c in self.edges if c == node}

    def ancestors(self, node: str) -> Set[str]:
        seen: Set[str] = set()
        stack = list(self.parents(node))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.parents(n))
        return seen

    def would_create_cycle(self, parent: str, child: str) -> bool:
        # cycle if child is ancestor of parent
        return parent == child or parent in self.ancestors(child) or child in self.ancestors(parent) and parent in self.ancestors(child)

    def legal_feature_for_decision(self, feature: str, decision: str, banned: Set[str]) -> Dict[str, Any]:
        """Feature illegal if in banned (e.g. post-outcome) or is descendant of decision."""
        if feature in banned:
            return {"ok": False, "reason": "banned_post_outcome"}
        # if feature is downstream of decision in graph, illegal at decision time
        if feature in self.descendants(decision):
            return {"ok": False, "reason": "descendant_of_decision"}
        return {"ok": True, "reason": "allowed"}

    def descendants(self, node: str) -> Set[str]:
        seen: Set[str] = set()
        stack = [c for p, c in self.edges if p == node]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend([c for p, c in self.edges if p == n])
        return seen


def default_market_graph() -> CausalGraph:
    g = CausalGraph()
    # time structure
    for a, b in [
        ("market_state_t", "features_t"),
        ("features_t", "decision_t"),
        ("decision_t", "execution_t"),
        ("execution_t", "outcome_t"),
        ("outcome_t", "label_t"),
    ]:
        g.add_edge(a, b)
    return g


def check_features(features: List[str], decision_node: str = "decision_t") -> Dict[str, Any]:
    g = default_market_graph()
    banned = {"outcome_t", "label_t", "execution_t"}
    results = {f: g.legal_feature_for_decision(f, decision_node, banned) for f in features}
    return {"ok": all(r["ok"] for r in results.values()), "results": results}
