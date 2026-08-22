"""Stationary and non-stationary engineering regimes with capability context."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

from .capabilities import CapabilityRegistry, default_capabilities
from .models import OperationState, Resolution, ValidationReport


class Engineer(ABC):
    name: str
    @abstractmethod
    def propose(self, problem: OperationState) -> Resolution: ...
    @abstractmethod
    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport: ...
    @abstractmethod
    def refresh_capabilities(self) -> None: ...


@dataclass
class StationaryEngineer(Engineer):
    """Use all applicable stable-state logic/tools in stationary order."""
    name: str = "stationary"
    external_proposer: Optional[Callable[[OperationState], Resolution]] = None
    capabilities: Optional[CapabilityRegistry] = None

    def __post_init__(self) -> None:
        self.capabilities = self.capabilities or default_capabilities()

    def refresh_capabilities(self) -> None:
        assert self.capabilities is not None
        self.capabilities.refresh_runtime()
        self.capabilities.update("python_runtime", verified=True)
        self.capabilities.update("filesystem_repository", verified=True)

    def propose(self, problem: OperationState) -> Resolution:
        self.refresh_capabilities()
        assert self.capabilities is not None
        context = self.capabilities.as_context(self.name)
        if self.external_proposer:
            result = self.external_proposer(problem)
            return Resolution(list(result.operations), result.rationale, list(result.assumptions),
                              dict(result.predicted_state), self.name,
                              {**getattr(result, "metadata", {}), "capabilities": context})
        return Resolution(list(problem.available_operations),
                          "Reference stationary proposal using all applicable registered logic/tools.",
                          ["state_distribution_is_sufficiently_stable"], {}, self.name,
                          {"capabilities": context})

    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport:
        assert self.capabilities is not None
        unknown = [op for op in resolution.operations if op not in set(problem.available_operations)]
        applicable = self.capabilities.applicable(self.name)
        return ValidationReport(not unknown,
            {"operations_declared": not unknown, "stationary_assumption_explicit": True,
             "capability_context_attached": "capabilities" in resolution.metadata},
            [f"unknown_operation:{op}" for op in unknown],
            notes=[f"{len(applicable)} applicable capabilities loaded for stationary reasoning."],
            metadata={"capability_names": [c.name for c in applicable]})


@dataclass
class NonStationaryEngineer(Engineer):
    """Use all applicable transition-state logic/tools in non-stationary order."""
    name: str = "non_stationary"
    external_proposer: Optional[Callable[[OperationState], Resolution]] = None
    transition_probe: Optional[Callable[[OperationState, Resolution], bool]] = None
    capabilities: Optional[CapabilityRegistry] = None

    def __post_init__(self) -> None:
        self.capabilities = self.capabilities or default_capabilities()

    def refresh_capabilities(self) -> None:
        assert self.capabilities is not None
        self.capabilities.refresh_runtime()
        self.capabilities.update("python_runtime", verified=True)
        self.capabilities.update("filesystem_repository", verified=True)

    def propose(self, problem: OperationState) -> Resolution:
        self.refresh_capabilities()
        assert self.capabilities is not None
        context = self.capabilities.as_context(self.name)
        if self.external_proposer:
            result = self.external_proposer(problem)
            return Resolution(list(result.operations), result.rationale, list(result.assumptions),
                              dict(result.predicted_state), self.name,
                              {**getattr(result, "metadata", {}), "capabilities": context})
        return Resolution(list(problem.available_operations),
                          "Reference non-stationary proposal using all applicable transition-aware logic/tools.",
                          ["state_may_change_during_resolution", "revalidation_is_required_after_transition"], {},
                          self.name, {"capabilities": context})

    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport:
        assert self.capabilities is not None
        unknown = [op for op in resolution.operations if op not in set(problem.available_operations)]
        transition_ok = self.transition_probe(problem, resolution) if self.transition_probe else False
        applicable = self.capabilities.applicable(self.name)
        risks: List[str] = [f"unknown_operation:{op}" for op in unknown]
        if self.transition_probe is None:
            risks.append("transition_probe_not_bound")
        return ValidationReport(not unknown and transition_ok,
            {"operations_declared": not unknown, "transition_validation": transition_ok,
             "non_stationary_assumption_explicit": True,
             "capability_context_attached": "capabilities" in resolution.metadata},
            risks,
            notes=[f"{len(applicable)} applicable capabilities loaded for non-stationary reasoning.",
                   "A non-stationary resolution cannot be promoted without a transition validation mechanism."],
            metadata={"capability_names": [c.name for c in applicable]})
