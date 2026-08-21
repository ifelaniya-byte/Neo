"""Verification infrastructure admitted from the engineer upgrade roadmap."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from hashlib import sha256
import json
from math import isfinite
from typing import Any, Callable, Iterable, Mapping, Sequence


class SchemaRegistry:
    """Runtime schema registry for SROS boundary objects."""
    def __init__(self) -> None:
        self._schemas: dict[str, Callable[[Any], bool]] = {}

    def register(self, name: str, validator: Callable[[Any], bool]) -> None:
        self._schemas[name] = validator

    def validate(self, name: str, value: Any) -> bool:
        validator = self._schemas.get(name)
        if validator is None:
            raise KeyError(f"schema_not_registered:{name}")
        return bool(validator(value))


@dataclass(frozen=True)
class ConstantsDB:
    """Named dimensional metadata. It never invents conversions."""
    dimensions: Mapping[str, str] = field(default_factory=dict)

    def require_same_dimension(self, *names: str) -> bool:
        dims = [self.dimensions[name] for name in names]
        return len(set(dims)) <= 1


@dataclass(frozen=True)
class FormalCheckResult:
    checked: bool
    passed: bool
    expression: str
    reason: str = ""


def optional_sympy_identity(expression: str) -> FormalCheckResult:
    """Check a formal identity when SymPy is installed; otherwise abstain."""
    try:
        import sympy  # type: ignore
    except ImportError:
        return FormalCheckResult(False, False, expression, "sympy_not_installed")
    try:
        parsed = sympy.sympify(expression)
        if not isinstance(parsed, sympy.Equality):
            return FormalCheckResult(False, False, expression, "not_an_equality")
        return FormalCheckResult(True, bool(sympy.simplify(parsed.lhs - parsed.rhs) == 0), expression)
    except Exception as exc:
        return FormalCheckResult(True, False, expression, f"parse_error:{type(exc).__name__}")


@dataclass(frozen=True)
class FailureRecord:
    decision_id: str
    signature: str
    reason: str


class FailureLedger:
    """In-memory ledger query for repeated failure patterns."""
    def __init__(self, records: Iterable[FailureRecord] = ()) -> None:
        self.records = list(records)

    def add(self, record: FailureRecord) -> None:
        self.records.append(record)

    def repeated(self, signature: str, minimum: int = 2) -> list[FailureRecord]:
        matches = [r for r in self.records if r.signature == signature]
        return matches if len(matches) >= minimum else []


@dataclass(frozen=True)
class AdversarialFinding:
    name: str
    passed: bool
    detail: str


def adversarial_suite(proposal: Any) -> list[AdversarialFinding]:
    """Baseline adversarial checks for a proposal-like object."""
    findings: list[AdversarialFinding] = []
    operations = getattr(proposal, "operations", None)
    findings.append(AdversarialFinding("operations_is_sequence", isinstance(operations, (list, tuple)), ""))
    if isinstance(operations, (list, tuple)):
        findings.append(AdversarialFinding("operations_are_strings", all(isinstance(x, str) for x in operations), ""))
    payload = getattr(proposal, "predicted_state", {})
    finite = isinstance(payload, Mapping) and all(not isinstance(v, float) or isfinite(v) for v in payload.values())
    findings.append(AdversarialFinding("predicted_state_finite", finite, ""))
    return findings


@dataclass(frozen=True)
class CalibrationPolicy:
    minimum_confidence: Mapping[str, float] = field(default_factory=lambda: {"stationary": 0.5, "non_stationary": 0.5})

    def accepts(self, regime: str, confidence: float) -> bool:
        threshold = self.minimum_confidence.get(regime, 1.0)
        return isfinite(confidence) and 0.0 <= confidence <= 1.0 and confidence >= threshold


def parallel_double_pass(items: Sequence[Any], check: Callable[[Any], Any], workers: int = 2) -> list[tuple[Any, Any]]:
    """Run two verification passes per item with bounded parallelism."""
    def run(item: Any) -> tuple[Any, Any]:
        return check(item), check(item)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        return list(executor.map(run, items))


def attach_evidence(metadata: Mapping[str, Any], settled_hits: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    result = dict(metadata)
    result["rag_settled"] = [dict(hit) for hit in settled_hits]
    return result


@dataclass(frozen=True)
class PromotionCandidate:
    signature: str
    confirmations: int
    evidence_ids: tuple[str, ...] = ()


class PromotionQueue:
    """Queue repeated human-confirmed patterns; never auto-deploy them."""
    def __init__(self) -> None:
        self._items: list[PromotionCandidate] = []

    def consider(self, candidate: PromotionCandidate, minimum_confirmations: int = 3) -> bool:
        if candidate.confirmations < minimum_confirmations:
            return False
        self._items.append(candidate)
        return True

    @property
    def items(self) -> tuple[PromotionCandidate, ...]:
        return tuple(self._items)


def decision_fingerprint(decision_id: str, payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(f"{decision_id}|{canonical}".encode()).hexdigest()


def differential_check(first_decision_id: str, first: Mapping[str, Any], second_decision_id: str, second: Mapping[str, Any]) -> bool:
    """Require identical decision IDs and canonical payloads across runs."""
    return first_decision_id == second_decision_id and decision_fingerprint(first_decision_id, first) == decision_fingerprint(second_decision_id, second)


__all__ = ["SchemaRegistry", "ConstantsDB", "FormalCheckResult", "optional_sympy_identity", "FailureRecord", "FailureLedger", "AdversarialFinding", "adversarial_suite", "CalibrationPolicy", "parallel_double_pass", "attach_evidence", "PromotionCandidate", "PromotionQueue", "decision_fingerprint", "differential_check"]
