from sros import OperationState, Resolution, SROS
from sros.engineers import NonStationaryEngineer, StationaryEngineer


def test_stationary_rejects_undeclared_operations():
    problem = OperationState(state={}, objective="test", available_operations=["hold"])
    resolution = Resolution(operations=["invented"], engineer="stationary")
    report = StationaryEngineer().validate(problem, resolution)
    assert not report.passed
    assert "unknown_operation:invented" in report.risks


def test_non_stationary_requires_bound_transition_probe():
    problem = OperationState(
        state={},
        objective="dynamic test",
        available_operations=["hold"],
        transition_model="drift",
    )
    engineer = NonStationaryEngineer()
    resolution = engineer.propose(problem)
    report = engineer.validate(problem, resolution)
    assert not report.passed
    assert report.checks["transition_validation"] is False
    assert "transition_probe_not_bound" in report.risks


def test_non_stationary_accepts_only_after_transition_probe():
    problem = OperationState(
        state={},
        objective="dynamic test",
        available_operations=["hold"],
        transition_model="drift",
    )
    engineer = NonStationaryEngineer(transition_probe=lambda _problem, _resolution: True)
    resolution = engineer.propose(problem)
    report = engineer.validate(problem, resolution)
    assert report.passed
    assert report.checks["transition_validation"] is True


def test_sros_uses_non_stationary_engineer_when_transition_model_exists():
    problem = OperationState(
        state={}, objective="dynamic test", available_operations=["hold"], transition_model="drift"
    )
    result = SROS(non_stationary=NonStationaryEngineer(transition_probe=lambda *_: True)).solve(problem)
    assert result.regime == "non_stationary"
    assert result.status == "resolved"
    assert result.resolution.engineer == "non_stationary"
