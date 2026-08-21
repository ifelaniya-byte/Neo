from sros import OperationState, SROS
from sros.models import Resolution
from sros.verification import (
    CalibrationPolicy,
    ConstantsDB,
    FailureLedger,
    FailureRecord,
    PromotionCandidate,
    PromotionQueue,
    SchemaRegistry,
    adversarial_suite,
    differential_check,
    parallel_double_pass,
)


def test_schema_registry_enforces_boundaries():
    registry = SchemaRegistry()
    registry.register("positive", lambda value: value > 0)
    assert registry.validate("positive", 2)
    assert not registry.validate("positive", -1)


def test_constants_db_rejects_mixed_dimensions():
    db = ConstantsDB({"length": "L", "width": "L", "mass": "M"})
    assert db.require_same_dimension("length", "width")
    assert not db.require_same_dimension("length", "mass")


def test_failure_ledger_finds_repeated_pattern():
    ledger = FailureLedger([FailureRecord("a", "x", "bad"), FailureRecord("b", "x", "bad")])
    assert len(ledger.repeated("x")) == 2


def test_adversarial_baseline_passes_valid_resolution():
    resolution = Resolution(operations=["hold"], predicted_state={"x": 1.0})
    assert all(item.passed for item in adversarial_suite(resolution))


def test_calibration_is_regime_specific_and_bounded():
    policy = CalibrationPolicy({"stationary": 0.7, "non_stationary": 0.9})
    assert policy.accepts("stationary", 0.7)
    assert not policy.accepts("stationary", 0.699)
    assert not policy.accepts("non_stationary", 1.1)


def test_parallel_double_pass_is_two_passes_per_item():
    calls = []
    result = parallel_double_pass([1, 2, 3], lambda value: calls.append(value) or value * 2)
    assert result == [(2, 2), (4, 4), (6, 6)]
    assert sorted(calls) == [1, 1, 2, 2, 3, 3]


def test_rag_evidence_is_attached_to_result_metadata():
    problem = OperationState(state={}, objective="test", available_operations=["hold"], metadata={"rag_settled": [{"id": "e1"}]})
    result = SROS().solve(problem)
    assert result.validation.metadata["rag_settled"] == [{"id": "e1"}]


def test_promotion_queue_requires_human_confirmations():
    queue = PromotionQueue()
    candidate = PromotionCandidate("pattern", confirmations=3, evidence_ids=("e1", "e2", "e3"))
    assert queue.consider(candidate)
    assert queue.items == (candidate,)


def test_differential_audit_detects_divergence():
    assert differential_check("d1", {"x": 1}, "d1", {"x": 1})
    assert not differential_check("d1", {"x": 1}, "d1", {"x": 2})
    assert not differential_check("d1", {"x": 1}, "d2", {"x": 1})
