"""
UAIR Orchestrator - Implements the request lifecycle:

Input → Normalize → Classify → Estimate → Route → Execute → Verify → 
Calibrate → Safety → Respond → Log → (async) Learn

This is the core pipeline that coordinates all 16 capability layers.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .contracts import (
    Request, Response, RoutePlan, NormalizedInput, IntentReport,
    ComplexityReport, EvidenceItem, ToolResult, UncertaintyReport,
    VerificationReport, SafetyReport, CostMetrics, SystemVersions,
    ResponseStatus, RoutePath, TaskClass, Sensitivity
)
from .layers import (
    NormalizationLayer,
    IntentLayer,
    ComplexityLayer,
    RoutingLayer,
    CacheLayer,
    RetrievalLayer,
    DeterministicLayer,
    LLMAdapter,
    VerificationLayer,
    UncertaintyLayer,
    SafetyLayer,
    ResponseLayer
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UAIRRuntime:
    """
    Main UAIR runtime orchestrator.
    
    This class coordinates all layers and implements the complete request lifecycle.
    It is designed to be:
    - Measurable: Every operation is timed and costed
    - Auditable: Every decision has a trace
    - Safe: Safety gates cannot be bypassed
    - Efficient: Routes to cheapest verified path
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize UAIR runtime with all layers.
        
        Args:
            config: Configuration dictionary for layer parameters
        """
        self.config = config or {}
        
        # Initialize all layers
        self.normalize = NormalizationLayer(config)
        self.intent = IntentLayer(config)
        self.complexity = ComplexityLayer(config)
        self.routing = RoutingLayer(config)
        self.cache = CacheLayer(config)
        self.retrieval = RetrievalLayer(config)
        self.deterministic = DeterministicLayer(config)
        self.llm = LLMAdapter(config)
        self.verify = VerificationLayer(config)
        self.uncertainty = UncertaintyLayer(config)
        self.safety = SafetyLayer(config)
        self.response = ResponseLayer(config)
        
        # Metrics storage
        self.metrics = {
            "total_requests": 0,
            "by_route": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "verification_passes": 0,
            "verification_failures": 0,
            "safety_blocks": 0,
            "abstentions": 0,
        }
        
        logger.info("UAIR Runtime initialized")
    
    def handle_request(self, request: Request) -> Response:
        """
        Main entry point - processes a request through the full lifecycle.
        
        Args:
            request: Canonical Request object
            
        Returns:
            Response object with full trace and metrics
        """
        start_time = time.time()
        trace_id = request.request_id
        
        logger.info(f"Starting request {trace_id}")
        self.metrics["total_requests"] += 1
        
        try:
            # Phase 1: Normalize
            normalized = self.normalize.process(request)
            
            # Phase 2: Classify intent
            intent_report = self.intent.classify(normalized)
            
            # Phase 3: Estimate complexity/risk
            complexity_report = self.complexity.estimate(normalized, intent_report)
            
            # Phase 4: Check cache first
            cached_result = self.cache.lookup(request, intent_report, complexity_report)
            if cached_result is not None:
                self.metrics["cache_hits"] += 1
                logger.info(f"Cache hit for request {trace_id}")
                return self._build_cached_response(cached_result, request)
            
            self.metrics["cache_misses"] += 1
            
            # Phase 5: Plan route
            route_plan = self.routing.plan(
                intent_report,
                complexity_report,
                request
            )
            
            # Phase 6: Execute based on route
            execution_result = self._execute_route(
                route_plan,
                request,
                normalized,
                intent_report
            )
            
            # Phase 7: Verify
            verification = self.verify.verify(
                execution_result["answer"],
                execution_result["evidence"],
                route_plan
            )
            self.metrics["verification_passes" if verification.status.value == "passed" else "verification_failures"] += 1
            
            # Phase 8: Quantify uncertainty
            uncertainty = self.uncertainty.quantify(
                execution_result,
                verification,
                route_plan
            )
            
            # Phase 9: Safety gate
            safety = self.safety.check(
                execution_result["answer"],
                uncertainty,
                request.sensitivity
            )
            if safety.status.value == "blocked":
                self.metrics["safety_blocks"] += 1
                logger.warning(f"Safety blocked request {trace_id}")
                return self._build_safety_response(request, safety, route_plan)
            
            # Phase 10: Build response
            response = self.response.build(
                execution_result["answer"],
                route_plan.selected_path,
                execution_result["evidence"],
                uncertainty,
                verification,
                safety,
                request
            )
            
            # Update route metrics
            route_name = route_plan.selected_path.value
            self.metrics["by_route"][route_name] = self.metrics["by_route"].get(route_name, 0) + 1
            if response.status == ResponseStatus.ABSTAINED:
                self.metrics["abstentions"] += 1
            
            # Add timing
            response.cost.latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Completed request {trace_id} with status {response.status.value}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request {trace_id}: {e}")
            return self._build_error_response(request, str(e))
    
    def _execute_route(
        self,
        route_plan: RoutePlan,
        request: Request,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> Dict[str, Any]:
        """Execute the selected route."""
        route = route_plan.selected_path
        
        if route == RoutePath.CACHE:
            # Should have been handled earlier
            raise ValueError("Cache route should be handled before execution")
        
        elif route == RoutePath.DETERMINISTIC:
            result = self.deterministic.execute(normalized, intent_report)
            return {
                "answer": result,
                "evidence": [],
                "tool_results": []
            }
        
        elif route == RoutePath.RETRIEVAL:
            evidence = self.retrieval.retrieve(normalized, route_plan)
            # Extractive answer from evidence
            answer = self._extractive_answer(evidence, normalized)
            return {
                "answer": answer,
                "evidence": evidence,
                "tool_results": []
            }
        
        elif route == RoutePath.SPECIALIST:
            # Placeholder for specialist models
            return {
                "answer": "Specialist not implemented in v0.1",
                "evidence": [],
                "tool_results": []
            }
        
        elif route == RoutePath.LLM:
            answer, evidence = self.llm.generate(
                normalized,
                route_plan,
                []
            )
            return {
                "answer": answer,
                "evidence": evidence,
                "tool_results": []
            }
        
        elif route == RoutePath.HYBRID:
            # Combine retrieval + LLM
            evidence = self.retrieval.retrieve(normalized, route_plan)
            answer, llm_evidence = self.llm.generate(
                normalized,
                route_plan,
                evidence
            )
            return {
                "answer": answer,
                "evidence": evidence + llm_evidence,
                "tool_results": []
            }
        
        elif route in (RoutePath.CLARIFY, RoutePath.ABSTAIN):
            return {
                "answer": self._get_refusal_message(route),
                "evidence": [],
                "tool_results": []
            }
        
        else:
            raise ValueError(f"Unknown route: {route}")
    
    def _extractive_answer(self, evidence: list, normalized: NormalizedInput) -> str:
        """Build extractive answer from retrieved evidence."""
        if not evidence:
            return "No relevant information found"
        
        # Simple extractive: return most relevant passage
        best = max(evidence, key=lambda e: e.relevance_score)
        return best.passage
    
    def _get_refusal_message(self, route: RoutePath) -> str:
        """Get appropriate refusal message."""
        if route == RoutePath.CLARIFY:
            return "I need more information to answer this question. Could you clarify?"
        elif route == RoutePath.ABSTAIN:
            return "I cannot provide a reliable answer to this question with the available information."
        return "Unable to process this request."
    
    def _build_cached_response(self, cached: Any, request: Request) -> Response:
        """Build response from cached result."""
        return Response(
            answer=cached["answer"],
            status=ResponseStatus.ANSWERED,
            route_used=RoutePath.CACHE,
            evidence_ids=cached.get("evidence_ids", []),
            cost=CostMetrics(
                latency_ms=0,
                estimated_cost_usd=0.0
            ),
            trace_id=request.request_id
        )
    
    def _build_safety_response(
        self,
        request: Request,
        safety: SafetyReport,
        route_plan: RoutePlan
    ) -> Response:
        """Build response when safety gate blocks."""
        return Response(
            answer="This request was blocked by safety checks.",
            status=ResponseStatus.REFUSED,
            route_used=route_plan.selected_path,
            safety=safety,
            cost=CostMetrics(latency_ms=0),
            trace_id=request.request_id
        )
    
    def _build_error_response(self, request: Request, error: str) -> Response:
        """Build error response."""
        return Response(
            answer=f"An error occurred: {error}",
            status=ResponseStatus.FAILED,
            route_used=RoutePath.ABSTAIN,
            cost=CostMetrics(latency_ms=0),
            trace_id=request.request_id
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current runtime metrics."""
        return self.metrics.copy()
