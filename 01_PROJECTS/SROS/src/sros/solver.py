"""Top-level SROS orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Optional

from .engineers import Engineer, NonStationaryEngineer, StationaryEngineer
from .models import OperationState, ResolutionResult, ValidationReport
from .verification import CalibrationPolicy, FailureLedger, SchemaRegistry, adversarial_suite, attach_evidence


@dataclass(frozen=True)
class ResolutionPolicy:
    """Controls regime selection and evidence-based acceptance."""
    default_regime: str = "auto"
    require_validation: bool = True
    allow_fallback: bool = False
    calibration: CalibrationPolicy = CalibrationPolicy()


class SROS:
    """State Resolutions Operation Solver."""

    def __init__(
        self,
        stationary: Optional[Engineer] = None,
        non_stationary: Optional[Engineer] = None,
        policy: ResolutionPolicy = ResolutionPolicy(),
        regime_classifier: Optional[Callable[[OperationState], str]] = None,
        ledger: Optional[FailureLedger] = None,
        schema_registry: Optional[SchemaRegistry] = None,
    ) -> None:
        self.stationary = stationary or StationaryEngineer()
        self.non_stationary = non_stationary or NonStationaryEngineer()
        self.policy = policy
        self.regime_classifier = regime_classifier
        self.ledger = ledger or FailureLedger()
        self.schemas = schema_registry or self._default_schema_registry()

    @staticmethod
    def _default_schema_registry() -> SchemaRegistry:
        registry = SchemaRegistry()
        registry.register("regime", lambda value: value in {"stationary", "non_stationary"})
        registry.register("confidence", lambda value: isinstance(value, (int, float)) and isfinite(value) and 0.0 <= value <= 1.0)
        return registry

    def classify(self, problem: OperationState) -> str:
        if self.policy.default_regime in {"stationary", "non_stationary"}:
            return self.policy.default_regime
        if self.regime_classifier:
            regime = self.regime_classifier(problem)
            if self.schemas.validate("regime", regime):
                return regime
        return "non_stationary" if problem.transition_model else "stationary"

    def _engineer(self, regime: str) -> Engineer:
        return self.non_stationary if regime == "non_stationary" else self.stationary

    def solve(self, problem: OperationState) -> ResolutionResult:
        regime = self.classify(problem)
        engineer = self._engineer(regime)
        resolution = engineer.propose(problem)
        validation = self._apply_verification(problem, resolution, engineer.validate(problem, resolution), regime)

        if not validation.passed and self.policy.allow_fallback:
            alternate_regime = "stationary" if regime == "non_stationary" else "non_stationary"
            alternate = self._engineer(alternate_regime)
            alternate_resolution = alternate.propose(problem)
            alternate_validation = self._apply_verification(problem, alternate_resolution, alternate.validate(problem, alternate_resolution), alternate_regime)
            if alternate_validation.passed:
                regime, engineer, resolution, validation = alternate_regime, alternate, alternate_resolution, alternate_validation

        confidence = self._confidence(validation)
        accepted = (
            (not self.policy.require_validation or validation.passed)
            and self.schemas.validate("confidence", confidence)
            and self.policy.calibration.accepts(regime, confidence)
        )
        status = "resolved" if accepted else "unresolved"
        validation = self._with_acceptance_note(validation, accepted)
        return ResolutionResult(regime, resolution, validation, confidence, status)

    @staticmethod
    def _apply_verification(problem, resolution, validation, regime):
        findings = adversarial_suite(resolution)
        adversarial_ok = all(f.passed for f in findings)
        checks = dict(validation.checks)
        checks["adversarial_baseline"] = adversarial_ok
        risks = list(validation.risks)
        if not adversarial_ok:
            risks.append("adversarial_baseline_failed")
        metadata = attach_evidence(problem.metadata, problem.metadata.get("rag_settled", []))
        metadata.update({"regime": regime, "engineer": resolution.engineer})
        return ValidationReport(
            passed=validation.passed and adversarial_ok,
            checks=checks,
            risks=risks,
            metrics=validation.metrics,
            notes=validation.notes,
            metadata=metadata,
        )

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

    @staticmethod
    def _with_acceptance_note(validation: ValidationReport, accepted: bool) -> ValidationReport:
        note = "accepted_by_sros_contract" if accepted else "not_accepted_by_sros_contract"
        return ValidationReport(
            passed=validation.passed,
            checks=validation.checks,
            risks=validation.risks,
            metrics=validation.metrics,
            notes=[*validation.notes, note],
            metadata=validation.metadata,
        )


__all__ = ["SROS", "ResolutionPolicy"]
