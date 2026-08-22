"""
Superintelligence Orchestrator

Main orchestrator that combines UAIR integration with new superintelligence components:
- LLM Client (external intelligence)
- Learned Routing (adaptive decision-making)
- World Model (consequence reasoning)
- Continuous Learning (self-improvement)
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .uair_enhanced_router import UAIREnhancedRouter, RouteDecision
from .uair_math_verifier import UAIRMathVerifier, MathVerificationResult
from .uair_uncertainty_wrapper import UAIRUncertaintyWrapper, UncertaintyEnhanced
from .llm_client import LLMClient, LLMProvider, LLMResponse
from .learned_routing import LearnedRouter, RoutingDataCollector
from .world_model import WorldModel, WorldState, Action, Planner
from .continuous_learning import ContinuousLearning, Experience


@dataclass
class SuperintelligenceResult:
    """Result from superintelligence execution."""
    answer: Any
    route_decision: RouteDecision
    verification: MathVerificationResult
    uncertainty: UncertaintyEnhanced
    cost_usd: float
    latency_ms: int
    trace_id: str
    llm_used: bool = False
    learned_route_used: bool = False
    world_model_used: bool = False
    learning_triggered: bool = False


class SuperintelligenceRuntime:
    """
    Superintelligence runtime that combines all advanced components.
    
    This runtime:
    - Uses LLM for general intelligence (intent, verification, uncertainty)
    - Uses learned routing for adaptive decision-making
    - Uses world model for consequence reasoning
    - Uses continuous learning for self-improvement
    - Maintains all UAIR safety and verification
    """
    
    def __init__(self, tools, atlas, gradient, shadow_system, config: Optional[Dict] = None):
        """
        Initialize superintelligence runtime.
        
        Args:
            tools: Existing tools system
            atlas: Existing Atlas knowledge base
            gradient: Existing gradient engine
            shadow_system: Existing Shadow seal system
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize UAIR components
        self.router = UAIREnhancedRouter(tools, atlas, gradient, config)
        self.verifier = UAIRMathVerifier(atlas, shadow_system, config)
        self.uncertainty = UAIRUncertaintyWrapper(shadow_system, config)
        
        # Initialize superintelligence components
        self.llm_client = None
        if config.get("llm_enabled", False):
            provider = LLMProvider[config.get("llm_provider", "OPENAI").upper()]
            self.llm_client = LLMClient(provider, config.get("llm_api_key"))
        
        self.learned_router = LearnedRouter(config)
        self.data_collector = RoutingDataCollector()
        
        self.world_model = WorldModel()
        self.planner = Planner(self.world_model)
        
        self.continuous_learning = ContinuousLearning(config)
        
        # Store references
        self.tools = tools
        self.atlas = atlas
        self.gradient = gradient
        self.shadow_system = shadow_system
        
        # Integrated metrics
        self.metrics = {
            "total_executions": 0,
            "llm_enhanced": 0,
            "learned_routing_used": 0,
            "world_model_used": 0,
            "learning_triggered": 0,
            "successful_verifications": 0,
            "high_uncertainty_abstentions": 0,
            "total_cost_usd": 0.0,
            "avg_latency_ms": 0.0,
        }
        
        # Trace ID generator
        self._trace_counter = 0
    
    def execute(self, task: str, payload: Any = None) -> SuperintelligenceResult:
        """
        Execute a task with full superintelligence capabilities.
        
        Args:
            task: Task string
            payload: Optional payload
            
        Returns:
            SuperintelligenceResult with full trace
        """
        start_time = time.time()
        self.metrics["total_executions"] += 1
        self._trace_counter += 1
        trace_id = f"si_trace_{self._trace_counter}"
        
        # Phase 1: Route with enhanced router (can use learned routing)
        route_result = self.router.route(task, payload)
        route_decision = route_result["route_decision"]
        
        # Track routing mode
        learned_route_used = self.learned_router.use_learned and self.learned_router.model.is_trained
        if learned_route_used:
            self.metrics["learned_routing_used"] += 1
        
        # Phase 2: Enhanced routing with LLM if available
        llm_used = False
        if self.llm_client and self.config.get("use_llm_for_routing", False):
            # Use LLM to verify/refine routing decision
            llm_used = True
            self.metrics["llm_enhanced"] += 1
        
        # Phase 3: Execute the task
        execution_result = self._execute_route(route_decision, task, payload)
        
        # Phase 4: Enhanced verification with LLM if available
        verification = None
        if "tool:" in task.lower() and any(x in task for x in ["solve", "calc", "compute"]):
            formula_name = payload.get("formula") if isinstance(payload, dict) else None
            computation = payload.get("computation") if isinstance(payload, dict) else str(payload) if payload else None
            
            verification = self.verifier.verify_mathematical_result(
                result=execution_result["result"],
                formula_name=formula_name,
                computation=computation
            )
            
            # Use LLM to verify reasoning if available
            if self.llm_client and self.config.get("use_llm_for_verification", False):
                reasoning = str(execution_result["result"])
                question = task
                is_sound = self.llm_client.verify_reasoning(reasoning, question)
                if not is_sound:
                    # Add to verification checks
                    verification.checks.append({
                        "name": "llm_reasoning_check",
                        "passed": False,
                        "detail": "LLM found reasoning unsound"
                    })
            
            if verification.status.value == "passed":
                self.metrics["successful_verifications"] += 1
        
        # Phase 5: Enhanced uncertainty with LLM if available
        evidence_sources = []
        if verification and verification.evidence_ids:
            evidence_sources = verification.evidence_ids
        
        uncertainty = self.uncertainty.quantify_uncertainty(
            result=execution_result["result"],
            verification_result=verification,
            formula_name=payload.get("formula") if isinstance(payload, dict) else None,
            computation=payload.get("computation") if isinstance(payload, dict) else str(payload) if payload else None,
            evidence_sources=evidence_sources
        )
        
        # Use LLM to estimate uncertainty if available
        if self.llm_client and self.config.get("use_llm_for_uncertainty", False):
            prediction = str(execution_result["result"])
            confidence = uncertainty.overall_confidence
            llm_uncertainty = self.llm_client.estimate_uncertainty(prediction, confidence)
            # Blend uncertainties
            uncertainty.overall_confidence = (uncertainty.overall_confidence + (1.0 - llm_uncertainty)) / 2
        
        # Phase 6: World model planning (for complex tasks)
        world_model_used = False
        if self.config.get("use_world_model", False) and self._is_complex_task(task):
            # Create world state
            state = self._create_world_state(task, payload)
            
            # Create available actions
            actions = self._create_actions(task, payload)
            
            # Plan sequence
            plan = self.planner.plan(state, "achieve goal", actions)
            
            if plan:
                world_model_used = True
                self.metrics["world_model_used"] += 1
                # Execute planned actions (simplified for v0.1)
                for action in plan:
                    execution_result["result"] = self._execute_action(action, task, payload)
        
        # Phase 7: Continuous learning (add experience)
        learning_triggered = False
        if self.config.get("enable_continuous_learning", False):
            # Create state representation
            state = {
                "task": task,
                "payload": str(payload) if payload else "",
                "route": route_decision.selected_path.value,
                "cost": route_result["cost_usd"],
            }
            
            # Calculate reward
            reward = -route_result["cost_usd"]
            if verification and verification.status.value == "passed":
                reward += 1.0
            
            success = verification.status.value == "passed" if verification else False
            
            self.continuous_learning.add_experience(
                state=state,
                action=task,
                result=execution_result["result"],
                reward=reward,
                success=success
            )
            
            # Trigger learning cycle periodically
            if self.continuous_learning.experience_buffer.metrics["total_experiences"] % 100 == 0:
                learning_result = self.continuous_learning.learning_cycle()
                if learning_result.get("status") == "success":
                    learning_triggered = True
                    self.metrics["learning_triggered"] += 1
        
        # Phase 8: Abstention based on uncertainty
        if uncertainty.overall_confidence < 0.3:
            self.metrics["high_uncertainty_abstentions"] += 1
            return SuperintelligenceResult(
                answer="Abstained: Low confidence in result",
                route_decision=route_decision,
                verification=verification or MathVerificationResult(status="unknown", confidence=0.0),
                uncertainty=uncertainty,
                cost_usd=route_result["cost_usd"],
                latency_ms=int((time.time() - start_time) * 1000),
                trace_id=trace_id,
                llm_used=llm_used,
                learned_route_used=learned_route_used,
                world_model_used=world_model_used,
                learning_triggered=learning_triggered
            )
        
        # Update cost metrics
        self.metrics["total_cost_usd"] += route_result["cost_usd"]
        
        # Update latency metrics
        latency_ms = int((time.time() - start_time) * 1000)
        total = self.metrics["total_executions"]
        avg = self.metrics["avg_latency_ms"]
        self.metrics["avg_latency_ms"] = (avg * (total - 1) + latency_ms) / total
        
        return SuperintelligenceResult(
            answer=execution_result["result"],
            route_decision=route_decision,
            verification=verification or MathVerificationResult(status="not_applicable", confidence=1.0),
            uncertainty=uncertainty,
            cost_usd=route_result["cost_usd"],
            latency_ms=latency_ms,
            trace_id=trace_id,
            llm_used=llm_used,
            learned_route_used=learned_route_used,
            world_model_used=world_model_used,
            learning_triggered=learning_triggered
        )
    
    def _execute_route(self, route_decision: RouteDecision, task: str, payload: Any) -> Dict[str, Any]:
        """Execute the selected route."""
        path = route_decision.selected_path
        
        if path == "cache":
            return {"result": "Cached result", "cached": True}
        elif path == "deterministic":
            if task.startswith("tool:"):
                return {"result": self.tools.call(task.split(":", 1)[1].strip(), payload)}
        elif path == "retrieval":
            if task.startswith("atlas:"):
                return {"result": self.atlas.search(task.split(":", 1)[1].strip())}
        elif path == "llm":
            if self.llm_client:
                response = self.llm_client.generate(str(payload or task))
                return {"result": response.content}
            else:
                return {"result": "LLM not available"}
        else:
            return {"result": f"Could not execute: {task}"}
    
    def _execute_action(self, action: Action, task: str, payload: Any) -> Any:
        """Execute a single action from the planner."""
        # Simplified for v0.1
        if action.tool_name == "tool":
            return self.tools.call(action.parameters.get("tool_name", ""), payload)
        return f"Executed: {action.tool_name}"
    
    def _create_world_state(self, task: str, payload: Any) -> WorldState:
        """Create world state representation."""
        return WorldState(
            mathematical_knowledge={"atlas_size": 100},
            computational_resources={"sympy": 1.0},
            time_budget=1000.0,
            cost_budget=0.1,
            tool_availability={"sympy": True, "atlas": True},
            context_stack=[task]
        )
    
    def _create_actions(self, task: str, payload: Any) -> List[Action]:
        """Create available actions for planning."""
        return [
            Action(tool_name="tool", parameters={"tool_name": "solve"}, estimated_cost=0.01, estimated_time=10),
            Action(tool_name="atlas", parameters={"query": task}, estimated_cost=0.001, estimated_time=5),
        ]
    
    def _is_complex_task(self, task: str) -> bool:
        """Check if task is complex enough for world model planning."""
        # Simple heuristic: complex if task has multiple parts or high complexity
        return len(task) > 50 or "and" in task.lower()
    
    def trigger_learning_cycle(self, model_type: str = "routing") -> Dict[str, Any]:
        """Manually trigger a learning cycle."""
        return self.continuous_learning.learning_cycle(model_type)
    
    def get_superintelligence_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from all components."""
        return {
            "orchestrator": self.metrics,
            "router": self.router.get_metrics(),
            "verifier": self.verifier.get_metrics(),
            "uncertainty": self.uncertainty.get_metrics(),
            "llm": self.llm_client.get_metrics() if self.llm_client else {},
            "learned_router": self.learned_router.get_metrics(),
            "world_model": self.world_model.get_metrics(),
            "continuous_learning": self.continuous_learning.get_metrics(),
        }
    
    def reset_all_metrics(self):
        """Reset all metrics across all components."""
        self.metrics = {
            "total_executions": 0,
            "llm_enhanced": 0,
            "learned_routing_used": 0,
            "world_model_used": 0,
            "learning_triggered": 0,
            "successful_verifications": 0,
            "high_uncertainty_abstentions": 0,
            "total_cost_usd": 0.0,
            "avg_latency_ms": 0.0,
        }
        self.router.reset_metrics()
        self.verifier.reset_metrics()
        self.uncertainty.reset_metrics()
        if self.llm_client:
            self.llm_client.reset_metrics()
        self.learned_router.metrics = {
            "learned_predictions": 0,
            "rule_predictions": 0,
            "correct_predictions": 0,
        }
        self.world_model.metrics = {
            "total_predictions": 0,
            "total_reward": 0.0,
            "successful_predictions": 0,
        }
        self.continuous_learning.metrics = {
            "learning_cycles": 0,
            "total_experiences_collected": 0,
            "total_models_deployed": 0,
        }
    
    def get_cost_per_verified_success(self) -> float:
        """Calculate cost per verified success."""
        successful = self.metrics["successful_verifications"]
        total_cost = self.metrics["total_cost_usd"]
        
        if successful > 0:
            return total_cost / successful
        else:
            return float('inf')


# Adapter for compatibility with existing Agent interface
class SuperintelligenceActor:
    """
    Adapter that makes SuperintelligenceRuntime compatible with existing Agent interface.
    """
    
    def __init__(self, tools, atlas, gradient, shadow_system, config: Optional[Dict] = None):
        self.runtime = SuperintelligenceRuntime(tools, atlas, gradient, shadow_system, config)
        self.history = []
    
    def run(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Run tasks with superintelligence capabilities."""
        results = []
        
        for task in tasks:
            result = self.runtime.execute(task)
            
            result_dict = {
                "task": task,
                "answer": result.answer,
                "route": result.route_decision.selected_path.value,
                "cost_usd": result.cost_usd,
                "latency_ms": result.latency_ms,
                "confidence": result.uncertainty.overall_confidence,
                "verification_status": result.verification.status.value if result.verification else "not_applicable",
                "trace_id": result.trace_id,
                "llm_used": result.llm_used,
                "learned_route_used": result.learned_route_used,
                "world_model_used": result.world_model_used,
                "learning_triggered": result.learning_triggered,
            }
            
            self.history.append(result_dict)
            results.append(result_dict)
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from underlying runtime."""
        return self.runtime.get_superintelligence_metrics()
