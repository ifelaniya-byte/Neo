from math import isfinite

from sros import OperationState, ResolutionPolicy, SROS


def test_stationary_default_resolution():
    problem = OperationState(state={"temperature": 20}, objective="maintain stable operation",
                             available_operations=["hold", "inspect"])
    result = SROS().solve(problem)
    assert result.regime == "stationary"
    assert result.status == "resolved"
    assert result.resolution.engineer == "stationary"
    assert isfinite(result.confidence)
    assert 0.0 <= result.confidence <= 1.0
    assert "accepted_by_sros_contract" in result.validation.notes


def test_non_stationary_requires_transition_validation():
    problem = OperationState(state={"temperature": 20}, objective="maintain operation while conditions change",
                             available_operations=["hold", "inspect"], transition_model="temperature_drift")
    result = SROS().solve(problem)
    assert result.regime == "non_stationary"
    assert result.status == "unresolved"
    assert "transition_probe_not_bound" in result.validation.risks
    assert "not_accepted_by_sros_contract" in result.validation.notes


def test_non_stationary_does_not_fallback_by_default():
    problem = OperationState(state={"temperature": 20}, objective="maintain operation while conditions change",
                             available_operations=["hold", "inspect"], transition_model="temperature_drift")
    result = SROS().solve(problem)
    assert result.regime == "non_stationary"
    assert result.resolution.engineer == "non_stationary"
    assert result.status == "unresolved"


def test_fallback_is_explicitly_opt_in():
    problem = OperationState(state={"temperature": 20}, objective="maintain operation while conditions change",
                             available_operations=["hold", "inspect"], transition_model="temperature_drift")
    result = SROS(policy=ResolutionPolicy(allow_fallback=True)).solve(problem)
    assert result.regime == "stationary"
    assert result.status == "resolved"


def test_classifier_can_select_regime():
    problem = OperationState(state={}, objective="dynamic problem")
    solver = SROS(regime_classifier=lambda _: "non_stationary")
    result = solver.solve(problem)
    assert result.regime == "non_stationary"


def test_stationary_loads_applicable_logic_and_tools():
    problem = OperationState(state={}, objective="inspect stable state", available_operations=["inspect"])
    result = SROS().solve(problem)
    names = result.validation.metadata["capability_names"]
    assert "schema_validation" in names
    assert "formal_identity_checks" in names
    assert "python_runtime" in names
    assert "causal_reasoning" not in names
    assert result.resolution.metadata["capabilities"]


def test_non_stationary_loads_transition_capabilities_only_in_its_regime():
    problem = OperationState(state={}, objective="adapt to changing state", available_operations=["inspect"],
                             transition_model="drift")
    result = SROS().solve(problem)
    names = result.validation.metadata["capability_names"]
    assert "transition_validation" in names
    assert "causal_reasoning" in names
    assert "counterfactual_reasoning" in names
    assert "formal_identity_checks" not in names
    assert result.resolution.metadata["capabilities"]
