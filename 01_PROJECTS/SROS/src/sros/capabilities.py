"""Capability registry for SROS engineering regimes.

The registry is intentionally explicit and evidence-oriented.  Engineers may
use every capability that is applicable to their selected regime, while the
registry records provenance and whether a capability is actually available.
It does not claim that a documented capability is executable unless a probe
confirms it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Capability:
    name: str
    kind: str  # logic | tool | model | evidence
    regimes: frozenset[str]
    source: str
    available: bool = True
    verified: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)


class CapabilityRegistry:
    """Mutable, auditable capability inventory shared by both engineers."""

    def __init__(self, capabilities: Iterable[Capability] = ()) -> None:
        self._items: dict[str, Capability] = {c.name: c for c in capabilities}

    def register(self, capability: Capability) -> None:
        self._items[capability.name] = capability

    def update(self, name: str, *, available: bool | None = None,
               verified: bool | None = None, metadata: Mapping[str, str] | None = None) -> None:
        current = self._items[name]
        self._items[name] = Capability(
            name=current.name,
            kind=current.kind,
            regimes=current.regimes,
            source=current.source,
            available=current.available if available is None else available,
            verified=current.verified if verified is None else verified,
            metadata={**current.metadata, **(metadata or {})},
        )

    def applicable(self, regime: str) -> tuple[Capability, ...]:
        return tuple(c for c in self._items.values() if c.available and regime in c.regimes)

    def snapshot(self) -> tuple[Capability, ...]:
        return tuple(self._items.values())

    def as_context(self, regime: str) -> list[dict[str, object]]:
        """Return only applicable capabilities, preserving provenance."""
        return [
            {
                "name": c.name,
                "kind": c.kind,
                "source": c.source,
                "verified": c.verified,
                "metadata": dict(c.metadata),
            }
            for c in self.applicable(regime)
        ]


def default_capabilities(repo_root: Path | None = None) -> CapabilityRegistry:
    """Build the baseline corpus/tool inventory without claiming model access."""
    registry = CapabilityRegistry()
    logic = {
        "schema_validation": ("both", True),
        "adversarial_validation": ("both", True),
        "formal_identity_checks": ("stationary", True),
        "transition_validation": ("non_stationary", True),
        "failure_ledger": ("both", True),
        "evidence_provenance": ("both", True),
        "uncertainty_and_abstention": ("both", False),
        "causal_reasoning": ("non_stationary", False),
        "counterfactual_reasoning": ("non_stationary", False),
        "mathematical_reasoning": ("stationary", False),
        "code_structural_reasoning": ("both", False),
        "model_disagreement_analysis": ("both", False),
    }
    for name, (regime, verified) in logic.items():
        regimes = frozenset({"stationary", "non_stationary"} if regime == "both" else {regime})
        registry.register(Capability(name, "logic", regimes, "SROS/corpus", verified=verified))

    tools = {
        "python_runtime": ("both", True),
        "filesystem_repository": ("both", True),
        "git_github": ("both", False),
        "sqlite": ("both", False),
        "sympy_optional": ("stationary", False),
        "pytest": ("both", False),
        "gpu_cuda": ("both", False),
        "external_llm": ("both", False),
        "external_web_research": ("both", False),
        "container_sandbox": ("both", False),
    }
    for name, (regime, verified) in tools.items():
        regimes = frozenset({"stationary", "non_stationary"} if regime == "both" else {regime})
        registry.register(Capability(name, "tool", regimes, "runtime/environment", verified=verified))

    # Model records are resources, not executable tools.  Keeping them here
    # makes their availability explicit without falsely implying API access.
    corpus = {
        "ChatGPT_corpus": "05_DOCUMENTATION/AI_Models/CHATGPT_FULL_CORPUS_2026-08-21.md",
        "Claude_corpus": "05_DOCUMENTATION/AI_Models/Claude_Assessment.txt",
        "Grok_corpus": "05_DOCUMENTATION/AI_Models/Grok_Review.txt",
        "Qwen_corpus": "05_DOCUMENTATION/AI_Models/QWEN_Models.txt",
        "Devin_corpus": "05_DOCUMENTATION/AI_Models/Devin_Info.txt",
        "Perplexity_corpus": "05_DOCUMENTATION/AI_Models/Perplexity_Capabilities.txt",
        "LMArena_corpus": "05_DOCUMENTATION/AI_Models/LMArena_Benchmarks.txt",
        "OmniRoute_corpus": "05_DOCUMENTATION/AI_Models/OmniRoute_Analysis.txt",
    }
    for name, source in corpus.items():
        exists = (repo_root / source).exists() if repo_root else True
        registry.register(Capability(name, "model", frozenset({"stationary", "non_stationary"}), source, available=exists))
    return registry
