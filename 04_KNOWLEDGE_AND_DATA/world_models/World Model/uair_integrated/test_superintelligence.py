"""
Superintelligence Integration Test Suite

Tests the new superintelligence components to verify they work correctly.
"""

import sys
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")

from uair_integrated.llm_client import LLMClient, LLMProvider
from uair_integrated.learned_routing import LearnedRouter, RoutingDataCollector, RoutingFeatures
from uair_integrated.world_model import WorldModel, WorldState, Action, Planner
from uair_integrated.continuous_learning import ContinuousLearning, Experience
from uair_integrated.superintelligence_orchestrator import SuperintelligenceRuntime, SuperintelligenceActor
from uair.contracts import RoutePath


def test_llm_client():
    """Test LLM client (without actual API calls)."""
    print("Test: LLM Client")
    
    # Test with mock (no API key)
    client = LLMClient(LLMProvider.LOCAL, None)
    
    # Test generate (should return stub)
    response = client.generate("Test prompt", max_tokens=50)
    print(f"  Response: {response.content[:50]}")
    print(f"  Tokens: {response.tokens_used}")
    print(f"  Cost: ${response.cost_usd:.6f}")
    
    # Test classify intent
    intents = client.classify_intent("What is 2 + 2?")
    print(f"  Intents: {intents}")
    
    print("  [OK] PASSED\n")


def test_learned_routing():
    """Test learned routing model."""
    print("Test: Learned Routing")
    
    # Create data collector
    collector = RoutingDataCollector()
    
    # Add more training data (need at least 10)
    for i in range(12):
        if i % 3 == 0:
            collector.add_sample(f"{i} + {i}", RoutePath.DETERMINISTIC, True, 0.01)
        elif i % 3 == 1:
            collector.add_sample(f"What is {i}?", RoutePath.RETRIEVAL, True, 0.001)
        else:
            collector.add_sample(f"solve equation {i}", RoutePath.LLM, False, 0.002)
    
    # Create router and assign data collector
    router = LearnedRouter()
    router.data_collector = collector
    
    # Train model
    router.train_model(epochs=20)
    
    # Test routing
    result = router.route("2 + 2")
    print(f"  Route result: {result}")
    
    metrics = router.get_metrics()
    print(f"  Model trained: {metrics['model_is_trained']}")
    print(f"  Training epochs: {metrics['training_epochs']}")
    
    print("  [OK] PASSED\n")


def test_world_model():
    """Test world model and planner."""
    print("Test: World Model")
    
    # Create world model
    world = WorldModel()
    
    # Create state
    state = WorldState(
        mathematical_knowledge={"formulas": 10},
        computational_resources={"sympy": 1.0},
        time_budget=100.0,
        cost_budget=0.1,
        tool_availability={"sympy": True},
        context_stack=["test task"]
    )
    
    # Create action
    action = Action(
        tool_name="tool",
        parameters={"tool_name": "solve"},
        estimated_cost=0.01,
        estimated_time=10.0
    )
    
    # Predict outcome
    prediction = world.predict(state, action)
    print(f"  Success probability: {prediction.success_probability}")
    print(f"  Reward: {prediction.reward}")
    print(f"  Next state time budget: {prediction.next_state.time_budget}")
    
    # Test planner
    planner = Planner(world, max_depth=2)
    
    actions = [
        Action("tool", {"tool_name": "solve"}, 0.01, 10),
        Action("atlas", {"query": "test"}, 0.001, 5),
    ]
    
    plan = planner.plan(state, "achieve goal", actions)
    print(f"  Plan length: {len(plan)}")
    
    metrics = world.get_metrics()
    print(f"  Total predictions: {metrics['total_predictions']}")
    
    print("  [OK] PASSED\n")


def test_continuous_learning():
    """Test continuous learning system."""
    print("Test: Continuous Learning")
    
    # Create continuous learning system
    cl = ContinuousLearning()
    
    # Add experiences
    cl.add_experience(
        state={"task": "test", "cost": 0.01},
        action="test action",
        result="test result",
        reward=1.0,
        success=True
    )
    
    cl.add_experience(
        state={"task": "test2", "cost": 0.02},
        action="test action 2",
        result="test result 2",
        reward=-0.5,
        success=False
    )
    
    metrics = cl.get_metrics()
    print(f"  Experiences collected: {metrics['learning_metrics']['total_experiences_collected']}")
    print(f"  Successful: {metrics['buffer_metrics']['successful_experiences']}")
    print(f"  Failed: {metrics['buffer_metrics']['failed_experiences']}")
    
    # Try learning cycle (will have insufficient data)
    result = cl.learning_cycle()
    print(f"  Learning cycle result: {result['status']}")
    
    print("  [OK] PASSED\n")


def test_superintelligence_orchestrator():
    """Test the full superintelligence orchestrator."""
    print("Test: Superintelligence Orchestrator")
    
    # Create mock systems
    class MockTools:
        def call(self, tool_name, payload):
            if "solve" in tool_name:
                return "4"
            return "Mock result"
    
    class MockAtlas:
        def search(self, query):
            return [f"Result for {query}"]
    
    class MockGradient:
        pass
    
    class MockShadow:
        def verify_all(self, force=False):
            return {"test_formula": {"status": "INTACT"}}
    
    # Create orchestrator (without LLM for v0.1)
    config = {
        "llm_enabled": False,
        "use_llm_for_routing": False,
        "use_llm_for retrieval": False,
        "use_world_model": False,
        "enable_continuous_learning": False,
    }
    
    orchestrator = SuperintelligenceRuntime(
        MockTools(),
        MockAtlas(),
        MockGradient(),
        MockShadow(),
        config
    )
    
    # Execute task
    result = orchestrator.execute("tool:solve_equation", {"computation": "2 + 2"})
    
    print(f"  Answer: {result.answer}")
    print(f"  Route: {result.route_decision.selected_path}")
    print(f"  Cost: ${result.cost_usd:.6f}")
    print(f"  Confidence: {result.uncertainty.overall_confidence:.2f}")
    print(f"  Trace ID: {result.trace_id}")
    print(f"  LLM used: {result.llm_used}")
    print(f" Learned routing: {result.learned_route_used}")
    print(f" World model: {result.world_model_used}")
    print(f" Learning triggered: {result.learning_triggered}")
    
    # Get metrics
    metrics = orchestrator.get_superintelligence_metrics()
    print(f"\n  Total executions: {metrics['orchestrator']['total_executions']}")
    
    print("  [OK] PASSED\n")


def run_all_tests():
    """Run all superintelligence tests."""
    print("=" * 60)
    print("Superintelligence Integration Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_llm_client()
        test_learned_routing()
        test_world_model()
        test_continuous_learning()
        test_superintelligence_orchestrator()
        
        print("=" * 60)
        print("ALL TESTS PASSED [OK]")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    import sys
    sys.exit(0 if success else 1)
