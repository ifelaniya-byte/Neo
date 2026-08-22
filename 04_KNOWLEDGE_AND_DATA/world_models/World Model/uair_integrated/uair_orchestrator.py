"""
UAIR Integrated Orchestrator

Main integration point that combines:
- UAIR routing (Phase 1)
- UAIR verification (Phase 2)
- UAIR uncertainty (Phase 2)
- Existing stationary system
- Existing Shadow seal system
- Existing Atlas, tools, gradient

This orchestrator replaces the simple Actor with a UAIR-enhanced version.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .uair_enhanced_router import UAIREnhancedRouter, RouteDecision
from .uair_math_verifier import UAIRMathVerifier, MathVerificationResult
from .uair_uncertainty_wrapper import UAIRUncertaintyWrapper, UncertaintyEnhanced


@dataclass
class IntegratedExecutionResult:
    """Result from UAIR-integrated execution."""
    answer: Any
    route_decision: RouteDecision
    verification: MathVerificationResult
    uncertainty: UncertaintyEnhanced
    cost_usd: float
    latency_ms: int
    trace_id: str


class UAIRIntegratedRuntime:
    """
    UAIR-integrated runtime that replaces the simple Actor.
    
    This runtime:
    - Uses UAIR-enhanced routing for all operations
    - Applies UAIR verification to mathematical results
    - Quantifies uncertainty using UAIR methods
    - Integrates with existing Shadow seal system
    - Provides full cost accounting
    """
    
    def __init__(self, tools, atlas, gradient, shadow_system, config: Optional[Dict] = None):
        """
        Initialize UAIR-integrated runtime.
        
        Args:
            tools: Existing tools system
            atlas: Existing Atlas knowledge base
            gradient: Existing gradient engine
            shadow_system: Existing Shadow seal system
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize UAIR components
        self.router = UAIREnhancedRouter(tools, atlas, gradient, config)
        self.verifier = UAIRMathVerifier(atlas, shadow_system, config)
        self.uncertainty = UAIRUncertaintyWrapper(shadow_system, config)
        
        # Store references to existing systems
        self.tools = tools
        self.atlas = atlas
        self.gradient = gradient
        self.shadow_system = shadow_system
        
        # Integrated metrics
        self.metrics = {
            "total_executions": 0,
            "successful_verifications": 0,
            "failed_verifications": 0,
            "high_uncertainty_abstentions": 0,
            "total_cost_usd": 0.0,
            "avg_latency_ms": 0.0,
        }
        
        # Trace ID generator
        import uuid
        self._trace_counter = 0
    
    def execute(self, task: str, payload: Any = None) -> IntegratedExecutionResult:
        """
        Execute a task with full UAIR integration.
        
        Args:
            task: Task string (e.g., "tool:solve_equation", "atlas:search")
            payload: Optional payload for the task
            
        Returns:
            IntegratedExecutionResult with full trace
        """
        start_time = time.time()
        self.metrics["total_executions"] += 1
        self._trace_counter += 1
        trace_id = f"trace_{self._trace_counter}"
        
        # Phase 1: Route with UAIR-enhanced router
        route_result = self.router.route(task, payload)
        route_decision = route_result["route_decision"]
        
        # Phase 2: Verify the result (if mathematical)
        verification = None
        if "tool:" in task.lower() and any(x in task for x in ["solve", "calc", "compute"]):
            formula_name = payload.get("formula") if isinstance(payload, dict) else None
            computation = payload.get("computation") if isinstance(payload, dict) else str(payload) if payload else None
            
            verification = self.verifier.verify_mathematical_result(
                result=route_result["result"],
                formula_name=formula_name,
                computation=computation
            )
            
            if verification.status.value == "passed":
                self.metrics["successful_verifications"] += 1
            else:
                self.metrics["failed_verifications"] += 1
        
        # Phase 3: Quantify uncertainty
        evidence_sources = []
        if verification and verification.evidence_ids:
            evidence_sources = verification.evidence_ids
        
        uncertainty = self.uncertainty.quantify_uncertainty(
            result=route_result["result"],
            verification_result=verification,
            formula_name=payload.get("formula") if isinstance(payload, dict) else None,
            computation=payload.get("computation") if isinstance(payload, dict) else str(payload) if payload else None,
            evidence_sources=evidence_sources
        )
        
        # Phase 4: Abstention based on uncertainty (UAIR safety gate)
        if uncertainty.overall_confidence < 0.3:
            self.metrics["high_uncertainty_abstentions"] += 1
            # Return abstention result
            return IntegratedExecutionResult(
                answer="Abstained: Low confidence in result",
                route_decision=route_decision,
                verification=verification or MathVerificationResult(
                    status="unknown",
                    confidence=0.0
                ),
                uncertainty=uncertainty,
                cost_usd=route_result["cost_usd"],
                latency_ms=int((time.time() - start_time) * 1000),
                trace_id=trace_id
            )
        
        # Update cost metrics
        self.metrics["total_cost_usd"] += route_result["cost_usd"]
        
        # Update latency metrics
        latency_ms = int((time.time() - start_time) * 1000)
        total = self.metrics["total_executions"]
        avg = self.metrics["avg_latency_ms"]
        self.metrics["avg_latency_ms"] = (avg * (total - 1) + latency_ms) / total
        
        return IntegratedExecutionResult(
            answer=route_result["result"],
            route_decision=route_decision,
            verification=verification or MathVerificationResult(
                status="not_applicable",
                confidence=1.0
            ),
            uncertainty=uncertainty,
            cost_usd=route_result["cost_usd"],
            latency_ms=latency_ms,
            trace_id=trace_id
        )
    
    def get_integrated_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from all UAIR components."""
        return {
            "orchestrator": self.metrics,
            "router": self.router.get_metrics(),
            "verifier": self.verifier.get_metrics(),
            "uncertainty": self.uncertainty.get_metrics(),
        }
    
    def reset_all_metrics(self):
        """Reset all metrics across all components."""
        self.metrics = {
            "total_executions": 0,
            "successful_verifications": 0,
            "failed_verifications": 0,
            "high_uncertainty_abstentions": 0,
            "total_cost_usd": 0.0,
            "avg_latency_ms": 0.0,
        }
        self.router.reset_metrics()
        self.verifier.reset_metrics()
        self.uncertainty.reset_metrics()
    
    def get_cost_per_verified_success(self) -> float:
        """
        Calculate cost per verified success.
        
        This is the key metric from UAIR: cost / (verified successes)
        """
        successful = self.metrics["successful_verifications"]
        total_cost = self.metrics["total_cost_usd"]
        
        if successful > 0:
            return total_cost / successful
        else:
            return float('inf')  # Infinite cost if no successes yet


# Adapter class to make this compatible with existing Agent interface
class UAIRIntegratedActor:
    """
    Adapter that makes UAIRIntegratedRuntime compatible with existing Agent interface.
    
    This allows dropping UAIR integration into the existing stationary system
    without changing the Agent code.
    """
    
    def __init__(self, tools, atlas, gradient, shadow_system, config: Optional[Dict] = None):
        self.runtime = UAIRIntegratedRuntime(tools, atlas, gradient, shadow_system, config)
        self.history = []
    
    def run(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """
        Run a list of tasks using UAIR-integrated runtime.
        
        Args:
            tasks: List of task strings
            
        Returns:
            List of result dictionaries compatible with existing Agent interface
        """
        results = []
        
        for task in tasks:
            # Execute with UAIR integration
            result = self.runtime.execute(task)
            
            # Convert to existing interface format
            result_dict = {
                "task": task,
                "answer": result.answer,
                "route": result.route_decision.selected_path.value,
                "cost_usd": result.cost_usd,
                "latency_ms": result.latency_ms,
                "confidence": result.uncertainty.overall_confidence,
                "verification_status": result.verification.status.value if result.verification else "not_applicable",
                "trace_id": result.trace_id
            }
            
            self.history.append(result_dict)
            results.append(result_dict)
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from the underlying runtime."""
        return self.runtime.get_integrated_metrics()
