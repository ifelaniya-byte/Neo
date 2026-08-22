"""Auditable logic/tool/model capability registry for SROS."""
from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Capability:
    name: str
    kind: str
    regimes: frozenset[str]
    source: str
    available: bool = True
    verified: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)


class CapabilityRegistry:
    """Mutable inventory whose availability/verification can be refreshed."""
    def __init__(self, capabilities: Iterable[Capability] = ()) -> None:
        self._items: dict[str, Capability] = {c.name: c for c in capabilities}

    def register(self, capability: Capability) -> None:
        self._items[capability.name] = capability

    def update(self, name: str, *, available: bool | None = None,
               verified: bool | None = None, metadata: Mapping[str, str] | None = None) -> None:
        current = self._items[name]
        self._items[name] = Capability(
            name=current.name, kind=current.kind, regimes=current.regimes, source=current.source,
            available=current.available if available is None else available,
            verified=current.verified if verified is None else verified,
            metadata={**current.metadata, **(metadata or {})},
        )

    def applicable(self, regime: str) -> tuple[Capability, ...]:
        return tuple(c for c in self._items.values() if c.available and regime in c.regimes)

    def snapshot(self) -> tuple[Capability, ...]:
        return tuple(self._items.values())

    def as_context(self, regime: str) -> list[dict[str, object]]:
        return [{"name": c.name, "kind": c.kind, "source": c.source,
                 "verified": c.verified, "metadata": dict(c.metadata)}
                for c in self.applicable(regime)]

    def refresh_runtime(self) -> None:
        """Probe local tools and update their status; never assumes access."""
        import_checks = {
            "sqlite": "sqlite3",
            "sympy_optional": "sympy",
            "pytest": "pytest",
        }
        for capability, module in import_checks.items():
            found = importlib.util.find_spec(module) is not None
            self.update(capability, available=found, verified=found,
                        metadata={"probe": f"importlib:{module}"})
        command_checks = {"git_github": "git", "container_sandbox": "docker"}
        for capability, command in command_checks.items():
            found = shutil.which(command) is not None
            self.update(capability, available=found, verified=found,
                        metadata={"probe": f"which:{command}"})
        # CUDA is deliberately a conservative capability: Python package
        # presence is not enough to claim a usable GPU.
        cuda = importlib.util.find_spec("torch") is not None
        self.update("gpu_cuda", available=cuda, verified=False,
                    metadata={"probe": "torch-presence-only; CUDA still unverified"})


def default_capabilities(repo_root: Path | None = None) -> CapabilityRegistry:
    registry = CapabilityRegistry()
    logic = {
        "schema_validation": ("both", True), "adversarial_validation": ("both", True),
        "formal_identity_checks": ("stationary", True), "transition_validation": ("non_stationary", True),
        "failure_ledger": ("both", True), "evidence_provenance": ("both", True),
        "uncertainty_and_abstention": ("both", False), "causal_reasoning": ("non_stationary", False),
        "counterfactual_reasoning": ("non_stationary", False), "mathematical_reasoning": ("stationary", False),
        "code_structural_reasoning": ("both", False), "model_disagreement_analysis": ("both", False),
    }
    for name, (regime, verified) in logic.items():
        regimes = frozenset({"stationary", "non_stationary"} if regime == "both" else {regime})
        registry.register(Capability(name, "logic", regimes, "SROS/corpus", verified=verified))

    tools = {
        "python_runtime": ("both", True), "filesystem_repository": ("both", True),
        "git_github": ("both", False), "sqlite": ("both", False), "sympy_optional": ("stationary", False),
        "pytest": ("both", False), "gpu_cuda": ("both", False), "external_llm": ("both", False),
        "external_web_research": ("both", False), "container_sandbox": ("both", False),
    }
    for name, (regime, verified) in tools.items():
        regimes = frozenset({"stationary", "non_stationary"} if regime == "both" else {regime})
        registry.register(Capability(name, "tool", regimes, "runtime/environment", verified=verified))

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
