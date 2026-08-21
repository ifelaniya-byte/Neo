from sros import OperationState, SROS


def test_stationary_default_resolution():
    problem = OperationState(
        state={"temperature": 20},
        objective="maintain stable operation",
        available_operations=["hold", "inspect"],
    )
    result = SROS().solve(problem)
    assert result.regime == "stationary"
    assert result.status == "resolved"
    assert result.resolution.engineer == "stationary"


def test_non_stationary_requires_transition_validation():
    problem = OperationState(
        state={"temperature": 20},
        objective="maintain operation while conditions change",
        available_operations=["hold", "inspect"],
        transition_model="temperature_drift",
    )
    result = SROS().solve(problem)
    assert result.regime == "non_stationary"
    assert result.status == "unresolved"
    assert "transition_probe_not_bound" in result.validation.risks


def test_classifier_can_select_regime():
    problem = OperationState(state={}, objective="dynamic problem")
    solver = SROS(regime_classifier=lambda _: "non_stationary")
    result = solver.solve(problem)
    assert result.regime == "non_stationary"
