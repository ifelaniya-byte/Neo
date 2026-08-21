"""Top-level SROS orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .engineers import Engineer, NonStationaryEngineer, StationaryEngineer
from .models import OperationState, ResolutionResult, ValidationReport


@dataclass(frozen=True)
class ResolutionPolicy:
    """Controls how SROS selects and accepts an engineering regime."""

    default_regime: str = "auto"
    require_validation: bool = True
    allow_fallback: bool = True


class SROS:
    """State Resolutions Operation Solver.

    SROS delegates engineering to stationary/non-stationary specialists and
    owns regime selection plus the final acceptance contract.
    """

    def __init__(
        self,
        stationary: Optional[Engineer] = None,
        non_stationary: Optional[Engineer] = None,
        policy: ResolutionPolicy = ResolutionPolicy(),
        regime_classifier: Optional[Callable[[OperationState], str]] = None,
    ) -> None:
        self.stationary = stationary or StationaryEngineer()
        self.non_stationary = non_stationary or NonStationaryEngineer()
        self.policy = policy
        self.regime_classifier = regime_classifier

    def classify(self, problem: OperationState) -> str:
        if self.policy.default_regime in {"stationary", "non_stationary"}:
            return self.policy.default_regime
        if self.regime_classifier:
            regime = self.regime_classifier(problem)
            if regime in {"stationary", "non_stationary"}:
                return regime
        # Explicit transition modeling is the strongest local signal that the
        # problem should use the dynamic regime.
        return "non_stationary" if problem.transition_model else "stationary"

    def _engineer(self, regime: str) -> Engineer:
        return self.non_stationary if regime == "non_stationary" else self.stationary

    def solve(self, problem: OperationState) -> ResolutionResult:
        regime = self.classify(problem)
        engineer = self._engineer(regime)
        resolution = engineer.propose(problem)
        validation = engineer.validate(problem, resolution)

        if not validation.passed and self.policy.allow_fallback:
            alternate_regime = "stationary" if regime == "non_stationary" else "non_stationary"
            alternate = self._engineer(alternate_regime)
            alternate_resolution = alternate.propose(problem)
            alternate_validation = alternate.validate(problem, alternate_resolution)
            if alternate_validation.passed:
                regime = alternate_regime
                resolution = alternate_resolution
                validation = alternate_validation

        confidence = self._confidence(validation)
        status = "resolved" if validation.passed else "unresolved"
        return ResolutionResult(regime, resolution, validation, confidence, status)

    @staticmethod
    def _confidence(validation: ValidationReport) -> float:
        checks = list(validation.checks.values())
        if not checks:
            return 0.0
        passed = sum(1 for value in checks if value)
        base = passed / len(checks)
        if validation.risks:
            base *= max(0.0, 1.0 - min(0.5, 0.1 * len(validation.risks)))
        return round(base, 4)


__all__ = ["SROS", "ResolutionPolicy"]
