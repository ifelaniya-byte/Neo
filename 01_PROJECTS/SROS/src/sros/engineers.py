"""Stationary and non-stationary engineering regimes.

The default implementations are deliberately conservative reference
implementations. They establish the protocol without pretending that the
existing Neo model/agent systems have already been integrated.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

from .models import OperationState, Resolution, ValidationReport


class Engineer(ABC):
    name: str

    @abstractmethod
    def propose(self, problem: OperationState) -> Resolution:
        raise NotImplementedError

    @abstractmethod
    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport:
        raise NotImplementedError


@dataclass
class StationaryEngineer(Engineer):
    """Engineer for a state assumed stable during one resolution cycle."""

    name: str = "stationary"
    external_proposer: Optional[Callable[[OperationState], Resolution]] = None

    def propose(self, problem: OperationState) -> Resolution:
        if self.external_proposer:
            result = self.external_proposer(problem)
            return Resolution(
                operations=list(result.operations),
                rationale=result.rationale,
                assumptions=list(result.assumptions),
                predicted_state=dict(result.predicted_state),
                engineer=self.name,
            )

        # Deterministic baseline: preserve the declared operation vocabulary
        # and produce a transparent proposal rather than inventing actions.
        operations = list(problem.available_operations)
        return Resolution(
            operations=operations,
            rationale="Reference stationary proposal using the declared operation set.",
            assumptions=["state_distribution_is_sufficiently_stable"],
            engineer=self.name,
        )

    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport:
        allowed = set(problem.available_operations)
        unknown = [op for op in resolution.operations if op not in allowed]
        passed = not unknown
        return ValidationReport(
            passed=passed,
            checks={
                "operations_declared": not unknown,
                "stationary_assumption_explicit": True,
            },
            risks=[f"unknown_operation:{op}" for op in unknown],
            notes=["Reference validation; domain-specific correctness gates must be bound by the integration layer."],
        )


@dataclass
class NonStationaryEngineer(Engineer):
    """Engineer for problems where relevant state variables may change."""

    name: str = "non_stationary"
    external_proposer: Optional[Callable[[OperationState], Resolution]] = None
    transition_probe: Optional[Callable[[OperationState, Resolution], bool]] = None

    def propose(self, problem: OperationState) -> Resolution:
        if self.external_proposer:
            result = self.external_proposer(problem)
            return Resolution(
                operations=list(result.operations),
                rationale=result.rationale,
                assumptions=list(result.assumptions),
                predicted_state=dict(result.predicted_state),
                engineer=self.name,
            )

        operations = list(problem.available_operations)
        return Resolution(
            operations=operations,
            rationale="Reference non-stationary proposal; transition-aware proposer is not yet bound.",
            assumptions=["state_may_change_during_resolution", "revalidation_is_required_after_transition"],
            engineer=self.name,
        )

    def validate(self, problem: OperationState, resolution: Resolution) -> ValidationReport:
        allowed = set(problem.available_operations)
        unknown = [op for op in resolution.operations if op not in allowed]
        transition_ok = self.transition_probe(problem, resolution) if self.transition_probe else False
        passed = not unknown and transition_ok
        risks: List[str] = [f"unknown_operation:{op}" for op in unknown]
        if self.transition_probe is None:
            risks.append("transition_probe_not_bound")
        return ValidationReport(
            passed=passed,
            checks={
                "operations_declared": not unknown,
                "transition_validation": transition_ok,
                "non_stationary_assumption_explicit": True,
            },
            risks=risks,
            notes=["A non-stationary resolution cannot be promoted without a transition validation mechanism."],
        )
