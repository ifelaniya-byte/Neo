"""
UAIR Capability Layers - Implements the 16 layer architecture.

Each layer is a single-responsibility component that can be tested independently.
For v0.1, we implement the core layers needed for the MVP.
"""

import re
import math
from typing import Optional, List, Dict, Any
from datetime import datetime

from .contracts import (
    Request, NormalizedInput, IntentReport, ComplexityReport,
    RoutePlan, EvidenceItem, TaskClass, RoutePath, Sensitivity,
    VerificationReport, SafetyReport, UncertaintyReport
)


class NormalizationLayer:
    """Layer 1: Input normalization and validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_length = config.get("max_input_length", 10000)
    
    def process(self, request: Request) -> NormalizedInput:
        """Normalize and validate input."""
        text = request.input_text.strip()
        
        # Basic normalization
        text_norm = " ".join(text.split())  # Normalize whitespace
        char_count = len(text_norm)
        
        # Simple language detection (placeholder)
        lang = "en"  # In v0.1, assume English
        
        # Check for injection patterns (basic)
        injection_flags = []
        if re.search(r"(ignore|forget|override)\s+(previous|all)\s+(instructions|rules)", text_norm, re.IGNORECASE):
            injection_flags.append("prompt_injection")
        
        # Size check
        unsupported_flags = []
        if char_count > self.max_length:
            unsupported_flags.append("too_long")
        
        return NormalizedInput(
            text_norm=text_norm,
            lang=lang,
            char_count=char_count,
            attachment_manifest=request.attachments,
            injection_flags=injection_flags,
            unsupported_flags=unsupported_flags
        )


class IntentLayer:
    """Layer 2: Intent and task classification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.confidence_threshold = config.get("intent_threshold", 0.7)
    
    def classify(self, normalized: NormalizedInput) -> IntentReport:
        """Classify intent using rules (v0.1 uses rules, not ML)."""
        text = normalized.text_norm.lower()
        
        # Rule-based classification
        scores = {
            TaskClass.ARITHMETIC: 0.0,
            TaskClass.DATA_EXTRACTION: 0.0,
            TaskClass.CODE_EXECUTION: 0.0,
            TaskClass.KNOWLEDGE_LOOKUP: 0.0,
            TaskClass.DOC_QA: 0.0,
            TaskClass.STRUCTURED_TRANSFORM: 0.0,
            TaskClass.CREATIVE_GENERATION: 0.0,
            TaskClass.PLANNING: 0.0,
            TaskClass.DEFI_ANALYSIS: 0.0,
            TaskClass.UNKNOWN: 0.0
        }
        
        # Arithmetic patterns
        if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", text):
            scores[TaskClass.ARITHMETIC] = 0.9
        
        # Question patterns
        if re.search(r"^(what|how|why|when|where|who|which)", text):
            scores[TaskClass.KNOWLEDGE_LOOKUP] = 0.7
            scores[TaskClass.DOC_QA] = 0.6
        
        # Code patterns
        if re.search(r"(code|function|class|def |import |print\()", text):
            scores[TaskClass.CODE_EXECUTION] = 0.8
        
        # DeFi patterns
        if re.search(r"(token|price|gas|liquidity|pool|swap|defi)", text):
            scores[TaskClass.DEFI_ANALYSIS] = 0.8
        
        # Extract patterns
        if re.search(r"(extract|parse|get\s+(the\s+)?(value|price|amount))", text):
            scores[TaskClass.DATA_EXTRACTION] = 0.7
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores[TaskClass.UNKNOWN] = 1.0
        
        # Get top-K
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Check if clarification needed
        max_score = top_k[0][1] if top_k else 0.0
        needs_clarification = max_score < self.confidence_threshold
        
        return IntentReport(
            intent_distribution=scores,
            top_k=top_k,
            needs_clarification=needs_clarification
        )


class ComplexityLayer:
    """Layer 3: Complexity and risk estimation."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def estimate(
        self,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> ComplexityReport:
        """Estimate complexity based on features."""
        features = {
            "length": normalized.char_count,
            "has_numbers": bool(re.search(r"\d+", normalized.text_norm)),
            "has_math": bool(re.search(r"[\+\-\*\/\^]", normalized.text_norm)),
            "injection": len(normalized.injection_flags) > 0,
            "unsupported": len(normalized.unsupported_flags) > 0
        }
        
        # Simple heuristic complexity score
        complexity = 0.0
        complexity += min(features["length"] / 1000, 0.4)
        complexity += 0.2 if features["has_numbers"] else 0
        complexity += 0.2 if features["has_math"] else 0
        complexity += 0.3 if features["injection"] else 0
        complexity += 0.3 if features["unsupported"] else 0
        
        return ComplexityReport(
            context_need=min(complexity, 1.0),
            depth=min(complexity * 0.5, 1.0),
            expected_tools=1 if features["has_math"] else 0,
            expected_out_len=int(50 + complexity * 200),
            sensitivity=Sensitivity.HIGH if features["injection"] else Sensitivity.LOW
        )


class RoutingLayer:
    """Layer 4 (combined with planning): Route planning."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def plan(
        self,
        intent_report: IntentReport,
        complexity_report: ComplexityReport,
        request: Request
    ) -> RoutePlan:
        """Plan the execution route."""
        # Route decision logic (simple for v0.1)
        top_intent = intent_report.top_k[0][0] if intent_report.top_k else TaskClass.UNKNOWN
        
        # Default route selection
        if top_intent == TaskClass.ARITHMETIC:
            selected_path = RoutePath.DETERMINISTIC
        elif top_intent == TaskClass.KNOWLEDGE_LOOKUP:
            selected_path = RoutePath.RETRIEVAL
        elif top_intent == TaskClass.DEFI_ANALYSIS:
            selected_path = RoutePath.HYBRID
        elif intent_report.needs_clarification:
            selected_path = RoutePath.CLARIFY
        elif complexity_report.sensitivity == Sensitivity.HIGH:
            selected_path = RoutePath.ABSTAIN
        else:
            selected_path = RoutePath.LLM
        
        return RoutePlan(
            intent_distribution=intent_report.intent_distribution,
            complexity_score=complexity_report.context_need,
            risk_score=complexity_report.sensitivity.value == "high",
            selected_path=selected_path,
            token_budget=1000,
            retrieval_budget=5,
            tool_budget=3
        )


class CacheLayer:
    """Layer 5: Semantic and exact caching."""
    
    def __init__(self, config: Dict[str, Any]):
        self.cache = {}  # Simple in-memory cache for v0.1
    
    def lookup(
        self,
        request: Request,
        intent_report: IntentReport,
        complexity_report: ComplexityReport
    ) -> Optional[Dict[str, Any]]:
        """Check cache for matching request."""
        # Simple exact match on input text
        cache_key = (request.input_text, intent_report.top_k[0][0] if intent_report.top_k else "unknown")
        return self.cache.get(cache_key)
    
    def store(self, request: Request, response: Any, intent: TaskClass):
        """Store result in cache."""
        cache_key = (request.input_text, intent)
        self.cache[cache_key] = response


class RetrievalLayer:
    """Layer 6: Retrieval and evidence memory."""
    
    def __init__(self, config: Dict[str, Any]):
        # Mock knowledge base for v0.1
        self.knowledge_base = [
            "Python is a programming language created by Guido van Rossum.",
            "Machine learning is a subset of artificial intelligence.",
            "DeFi stands for Decentralized Finance.",
            "Arithmetic operations include addition, subtraction, multiplication, and division.",
            "Gas fees are payments made to network validators for processing transactions."
        ]
    
    def retrieve(
        self,
        normalized: NormalizedInput,
        route_plan: RoutePlan
    ) -> List[EvidenceItem]:
        """Retrieve relevant evidence."""
        query = normalized.text_norm.lower()
        evidence = []
        
        # Simple keyword matching
        for i, doc in enumerate(self.knowledge_base):
            doc_lower = doc.lower()
            # Check if any query word appears in document
            query_words = set(query.split())
            doc_words = set(doc_lower.split())
            overlap = len(query_words & doc_words)
            
            if overlap > 0:
                relevance = overlap / len(query_words)
                evidence.append(EvidenceItem(
                    source_type="database",
                    source_uri_or_id=f"doc_{i}",
                    passage=doc,
                    relevance_score=relevance
                ))
        
        # Sort by relevance
        evidence.sort(key=lambda e: e.relevance_score, reverse=True)
        return evidence[:route_plan.retrieval_budget]


class DeterministicLayer:
    """Layer 7: Deterministic execution (calculators, parsers)."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def execute(
        self,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> Any:
        """Execute deterministic computation."""
        text = normalized.text_norm
        
        # Simple arithmetic evaluation
        try:
            # Safe eval for arithmetic only
            if re.match(r"^[\d\s\+\-\*\/\(\)\.]+$", text):
                result = eval(text)
                return str(result)
        except:
            pass
        
        return "Could not compute deterministically"


class LLMAdapter:
    """Layer 9: LLM synthesis adapter (stub for v0.1)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("llm_enabled", False)
    
    def generate(
        self,
        normalized: NormalizedInput,
        route_plan: RoutePlan,
        evidence: List[EvidenceItem]
    ) -> tuple[str, List[EvidenceItem]]:
        """Generate response using LLM (stub in v0.1)."""
        if not self.enabled:
            return "LLM not enabled in v0.1", []
        
        # In a real implementation, this would call an LLM API
        # For v0.1, return a simple response
        return f"LLM response for: {normalized.text_norm[:50]}...", evidence


class VerificationLayer:
    """Layer 10: Verification of claims."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def verify(
        self,
        answer: Any,
        evidence: List[EvidenceItem],
        route_plan: RoutePlan
    ) -> VerificationReport:
        """Verify claims against evidence."""
        # Simple verification for v0.1
        checks = []
        
        # Check if answer is based on evidence
        if evidence and isinstance(answer, str):
            answer_lower = answer.lower()
            has_evidence_support = any(
                e.passage.lower() in answer_lower or 
                any(word in e.passage.lower() for word in answer_lower.split())
                for e in evidence
            )
            checks.append(("evidence_support", has_evidence_support))
        
        passed = all(check[1] for check in checks) if checks else True
        
        return VerificationReport(
            status="passed" if passed else "partial",
            checks=[{"name": c[0], "passed": c[1]} for c in checks]
        )


class UncertaintyLayer:
    """Layer 11: Uncertainty quantification."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def quantify(
        self,
        execution_result: Dict[str, Any],
        verification: VerificationReport,
        route_plan: RoutePlan
    ) -> UncertaintyReport:
        """Quantify uncertainty."""
        # Simple uncertainty model for v0.1
        epistemic = 0.0
        aleatoric = 0.0
        retrieval = 0.0
        execution = 0.0
        
        # Evidence uncertainty
        if not execution_result.get("evidence"):
            retrieval = 0.5
        
        # Verification uncertainty
        if verification.status == "partial":
            epistemic = 0.3
        
        # Route-based uncertainty
        if route_plan.selected_path == RoutePath.ABSTAIN:
            aleatoric = 0.8
        
        overall = 1.0 - (epistemic + aleatoric + retrieval + execution) / 4
        
        return UncertaintyReport(
            overall_confidence=max(0.0, min(1.0, overall)),
            epistemic=epistemic,
            aleatoric=aleatoric,
            retrieval=retrieval,
            execution=execution,
            calibrated=False  # Not calibrated in v0.1
        )


class SafetyLayer:
    """Layer 14: Safety and policy constraints."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def check(
        self,
        answer: Any,
        uncertainty: UncertaintyReport,
        sensitivity: Sensitivity
    ) -> SafetyReport:
        """Check safety constraints."""
        reason_codes = []
        
        # High uncertainty on high sensitivity = block
        if sensitivity == Sensitivity.HIGH and uncertainty.overall_confidence < 0.5:
            reason_codes.append("high_uncertainty_high_sensitivity")
        
        # Check for unsafe content (basic)
        if isinstance(answer, str):
            unsafe_patterns = ["hack", "exploit", "bypass", "steal private key"]
            if any(pattern in answer.lower() for pattern in unsafe_patterns):
                reason_codes.append("unsafe_content")
        
        passed = len(reason_codes) == 0
        
        return SafetyReport(
            status="blocked" if not passed else "passed",
            reason_codes=reason_codes
        )


class ResponseLayer:
    """Layer 15: Response policy and rendering."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def build(
        self,
        answer: Any,
        route_used: RoutePath,
        evidence: List[EvidenceItem],
        uncertainty: UncertaintyReport,
        verification: VerificationReport,
        safety: SafetyReport,
        request: Request
    ) -> Response:
        """Build final response."""
        from .contracts import ResponseStatus, CostMetrics, SystemVersions
        
        # Determine status
        if route_used == RoutePath.ABSTAIN:
            status = ResponseStatus.ABSTAINED
        elif route_used == RoutePath.CLARIFY:
            status = ResponseStatus.CLARIFY
        else:
            status = ResponseStatus.ANSWERED
        
        # Extract evidence IDs
        evidence_ids = [e.evidence_id for e in evidence]
        
        return Response(
            answer=answer,
            status=status,
            route_used=route_used,
            evidence_ids=evidence_ids,
            uncertainty=uncertainty,
            verification=verification,
            safety=safety,
            cost=CostMetrics(),
            trace_id=request.request_id,
            version=SystemVersions()
        )
