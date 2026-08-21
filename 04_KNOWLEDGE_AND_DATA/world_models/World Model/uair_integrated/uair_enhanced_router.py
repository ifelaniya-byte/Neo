"""
UAIR-Enhanced Router for Stationary System

Phase 1 Integration: Replace current router with UAIR RoutingLayer
- Routes to cheapest verified execution path
- Adds cost metrics to Actor operations
- Supports cache, deterministic, retrieval, specialist, LLM paths
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import UAIR contracts
import sys
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")
from uair.contracts import (
    TaskClass, RoutePath, Sensitivity, ComplexityReport, IntentReport
)


@dataclass
class RouteDecision:
    """Enhanced route decision with cost estimation."""
    selected_path: RoutePath
    confidence: float
    estimated_cost_usd: float
    estimated_latency_ms: int
    reason_codes: List[str] = field(default_factory=list)
    cache_key: Optional[str] = None


class UAIREnhancedRouter:
    """
    UAIR-enhanced router that replaces the simple router in the stationary system.
    
    This router:
    - Uses UAIR's routing logic (intent-based, complexity-aware)
    - Adds cost accounting to all routing decisions
    - Supports multi-path escalation (cache → deterministic → retrieval → LLM)
    - Integrates with existing tool system
    """
    
    def __init__(self, tools, atlas, gradient, config: Optional[Dict] = None):
        self.tools = tools
        self.atlas = atlas
        self.gradient = gradient
        self.config = config or {}
        
        # Cost tracking
        self.route_costs = {
            RoutePath.CACHE: 0.000001,
            RoutePath.DETERMINISTIC: 0.00001,
            RoutePath.RETRIEVAL: 0.0001,
            RoutePath.SPECIALIST: 0.0005,
            RoutePath.LLM: 0.001,
            RoutePath.HYBRID: 0.0015,
        }
        
        # Simple cache for v0.1
        self.cache = {}
        
        # Metrics
        self.metrics = {
            "total_routes": 0,
            "by_path": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_cost_usd": 0.0,
        }
    
    def route(self, task: str, payload: Any = None) -> Dict[str, Any]:
        """
        Enhanced routing with UAIR logic.
        
        Args:
            task: Task string (e.g., "tool:solve_equation", "atlas:search")
            payload: Optional payload for the task
            
        Returns:
            Dict with engine, result, and cost metrics
        """
        start_time = time.time()
        self.metrics["total_routes"] += 1
        
        # Parse task
        task_lower = task.lower().strip()
        
        # Classify intent (simplified for integration)
        intent = self._classify_intent(task_lower, payload)
        
        # Estimate complexity
        complexity = self._estimate_complexity(task_lower, payload)
        
        # Check cache first
        cache_key = self._make_cache_key(task, payload)
        if cache_key in self.cache:
            self.metrics["cache_hits"] += 1
            cached_result = self.cache[cache_key]
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "engine": "cache",
                "result": cached_result,
                "cost_usd": self.route_costs[RoutePath.CACHE],
                "latency_ms": latency_ms,
                "route_decision": RouteDecision(
                    selected_path=RoutePath.CACHE,
                    confidence=1.0,
                    estimated_cost_usd=self.route_costs[RoutePath.CACHE],
                    estimated_latency_ms=0,
                    cache_key=cache_key
                )
            }
        
        self.metrics["cache_misses"] += 1
        
        # Make routing decision based on UAIR logic
        route_decision = self._plan_route(intent, complexity, task_lower)
        
        # Execute based on route
        result = self._execute_route(route_decision, task, payload)
        
        # Cache result if appropriate
        if route_decision.selected_path in [RoutePath.DETERMINISTIC, RoutePath.RETRIEVAL]:
            self.cache[cache_key] = result
        
        # Update metrics
        path_name = route_decision.selected_path.value
        self.metrics["by_path"][path_name] = self.metrics["by_path"].get(path_name, 0) + 1
        self.metrics["total_cost_usd"] += route_decision.estimated_cost_usd
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "engine": route_decision.selected_path.value,
            "result": result,
            "cost_usd": route_decision.estimated_cost_usd,
            "latency_ms": latency_ms,
            "route_decision": route_decision
        }
    
    def _classify_intent(self, task: str, payload: Any) -> TaskClass:
        """Classify task intent (simplified for integration)."""
        if task.startswith("tool:"):
            tool_name = task.split(":", 1)[1].strip()
            if "solve" in tool_name or "calc" in tool_name:
                return TaskClass.ARITHMETIC
            elif "verify" in tool_name:
                return TaskClass.DATA_EXTRACTION
            else:
                return TaskClass.CODE_EXECUTION
        elif task.startswith("atlas:"):
            return TaskClass.KNOWLEDGE_LOOKUP
        elif task.startswith("gradient:"):
            return TaskClass.STRUCTURED_TRANSFORM
        else:
            return TaskClass.UNKNOWN
    
    def _estimate_complexity(self, task: str, payload: Any) -> ComplexityReport:
        """Estimate task complexity."""
        # Simple heuristic complexity estimation
        complexity_score = 0.5
        
        if payload and isinstance(payload, (list, dict)):
            complexity_score += 0.2
        
        if "search" in task or "query" in task:
            complexity_score += 0.3
        
        return ComplexityReport(
            context_need=min(complexity_score, 1.0),
            depth=min(complexity_score * 0.5, 1.0),
            expected_tools=1 if "tool:" in task else 0,
            expected_out_len=100
        )
    
    def _plan_route(self, intent: TaskClass, complexity: ComplexityReport, task: str) -> RouteDecision:
        """Plan route using UAIR logic."""
        # Route decision logic (matches UAIR RoutingLayer)
        if intent == TaskClass.ARITHMETIC:
            selected_path = RoutePath.DETERMINISTIC
        elif intent == TaskClass.KNOWLEDGE_LOOKUP:
            selected_path = RoutePath.RETRIEVAL
        elif complexity.context_need > 0.7:
            selected_path = RoutePath.LLM
        else:
            selected_path = RoutePath.LLM  # Default for unknown
        
        return RouteDecision(
            selected_path=selected_path,
            confidence=0.8,
            estimated_cost_usd=self.route_costs[selected_path],
            estimated_latency_ms=100
        )
    
    def _execute_route(self, route_decision: RouteDecision, task: str, payload: Any) -> Any:
        """Execute the selected route."""
        path = route_decision.selected_path
        
        if path == RoutePath.DETERMINISTIC:
            # Use existing tools for deterministic execution
            if task.startswith("tool:"):
                return self.tools.call(task.split(":", 1)[1].strip(), payload)
        
        elif path == RoutePath.RETRIEVAL:
            # Use atlas for retrieval
            if task.startswith("atlas:"):
                return self.atlas.search(task.split(":", 1)[1].strip())
        
        elif path == RoutePath.LLM:
            # For v0.1, fall back to tools (LLM not integrated yet)
            if task.startswith("tool:"):
                return self.tools.call(task.split(":", 1)[1].strip(), payload)
            elif task.startswith("atlas:"):
                return self.atlas.search(task.split(":", 1)[1].strip())
        
        # Default fallback
        return f"Could not execute: {task}"
    
    def _make_cache_key(self, task: str, payload: Any) -> str:
        """Create cache key from task and payload."""
        import hashlib
        key_str = f"{task}:{str(payload)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "total_routes": 0,
            "by_path": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_cost_usd": 0.0,
        }
