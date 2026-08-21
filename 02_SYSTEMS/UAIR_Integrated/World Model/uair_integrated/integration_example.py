"""
UAIR Integration Example

Shows how to integrate UAIR components with the existing stationary system.

This example demonstrates:
- Replacing the simple router with UAIREnhancedRouter
- Adding UAIRMathVerifier for mathematical verification
- Adding UAIRUncertaintyWrapper for uncertainty quantification
- Using UAIRIntegratedActor as a drop-in replacement for the Agent
"""

import sys
import os

# Add paths
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")
sys.path.append("C:/Users/AIAli/Downloads/stationary_system/SECRET_ZIP")

# Import UAIR components
from uair_integrated import UAIRIntegratedActor, UAIRIntegratedRuntime

# For this example, we'll create mock objects since we don't have the full stationary system
class MockTools:
    """Mock tools system for demonstration."""
    def call(self, tool_name, payload):
        if "solve" in tool_name:
            if isinstance(payload, dict):
                computation = payload.get("computation", "0")
                try:
                    result = eval(computation)
                    return str(result)
                except:
                    return "Error in computation"
        return f"Mock result for {tool_name}"

class MockAtlas:
    """Mock Atlas for demonstration."""
    def search(self, query):
        return [f"Mock result for {query}"]

class MockGradient:
    """Mock gradient engine for demonstration."""
    pass

class MockShadowSystem:
    """Mock Shadow system for demonstration."""
    def verify_all(self, force=False):
        return {
            "pythagorean_theorem": {"status": "INTACT"},
            "euler_formula": {"status": "INTACT"}
        }


def demonstrate_integration():
    """Demonstrate UAIR integration with stationary system."""
    
    print("=" * 60)
    print("UAIR Integration Demonstration")
    print("=" * 60)
    print()
    
    # Create mock systems
    tools = MockTools()
    atlas = MockAtlas()
    gradient = MockGradient()
    shadow_system = MockShadowSystem()
    
    # Create UAIR-integrated actor
    config = {
        "llm_enabled": False,  # v0.1 doesn't use LLM
        "intent_threshold": 0.7,
    }
    
    actor = UAIRIntegratedActor(tools, atlas, gradient, shadow_system, config)
    
    print("UAIR-Integrated Actor initialized")
    print()
    
    # Run some tasks
    tasks = [
        "tool:solve_equation",
        "atlas:search pythagorean theorem",
        "tool:verify_integrity"
    ]
    
    payloads = [
        {"computation": "2 + 2"},
        None,
        {"formula": "pythagorean_theorem"}
    ]
    
    print("Executing tasks with UAIR integration:")
    print()
    
    for i, (task, payload) in enumerate(zip(tasks, payloads)):
        # We need to adapt the task format for our simplified example
        if payload:
            full_task = f"{task} with payload {payload}"
        else:
            full_task = task
        
        print(f"Task {i+1}: {full_task}")
        
        # Execute
        results = actor.run([task])
        result = results[0]
        
        print(f"  Answer: {result['answer']}")
        print(f"  Route: {result['route']}")
        print(f"  Cost: ${result['cost_usd']:.6f}")
        print(f"  Latency: {result['latency_ms']}ms")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Verification: {result['verification_status']}")
        print(f"  Trace ID: {result['trace_id']}")
        print()
    
    # Show integrated metrics
    print("=" * 60)
    print("Integrated Metrics")
    print("=" * 60)
    
    metrics = actor.get_metrics()
    
    print("\nOrchestrator Metrics:")
    for key, value in metrics["orchestrator"].items():
        print(f"  {key}: {value}")
    
    print("\nRouter Metrics:")
    for key, value in metrics["router"].items():
        print(f"  {key}: {value}")
    
    print("\nVerifier Metrics:")
    for key, value in metrics["verifier"].items():
        print(f"  {key}: {value}")
    
    print("\nUncertainty Metrics:")
    for key, value in metrics["uncertainty"].items():
        print(f"  {key}: {value}")
    
    print("\nCost per Verified Success:")
    cost_per_success = actor.runtime.get_cost_per_verified_success()
    print(f"  ${cost_per_success:.6f}")
    
    print()
    print("=" * 60)
    print("Integration demonstration complete")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_integration()
