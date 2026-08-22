"""Domain contracts for the State Resolutions Operation Solver."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class OperationState:
    """A snapshot of the problem being solved."""
    state: Mapping[str, Any]
    objective: str
    constraints: Mapping[str, Any] = field(default_factory=dict)
    available_operations: List[str] = field(default_factory=list)
    evaluation_criteria: Mapping[str, float] = field(default_factory=dict)
    transition_model: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Resolution:
    """A proposed operation sequence plus auditable capability provenance."""
    operations: List[str]
    rationale: str = ""
    assumptions: List[str] = field(default_factory=list)
    predicted_state: Mapping[str, Any] = field(default_factory=dict)
    engineer: str = "unknown"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationReport:
    """Evidence produced by a validation stage."""
    passed: bool
    checks: Mapping[str, bool] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    metrics: Mapping[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolutionResult:
    """Complete SROS decision record."""
    regime: str
    resolution: Resolution
    validation: ValidationReport
    confidence: float
    status: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime,
            "resolution": {
                "operations": self.resolution.operations,
                "rationale": self.resolution.rationale,
                "assumptions": self.resolution.assumptions,
                "predicted_state": dict(self.resolution.predicted_state),
                "engineer": self.resolution.engineer,
                "metadata": dict(self.resolution.metadata),
            },
            "validation": {
                "passed": self.validation.passed,
                "checks": dict(self.validation.checks),
                "risks": list(self.validation.risks),
                "metrics": dict(self.validation.metrics),
                "notes": list(self.validation.notes),
                "metadata": dict(self.validation.metadata),
            },
            "confidence": self.confidence,
            "status": self.status,
        }
