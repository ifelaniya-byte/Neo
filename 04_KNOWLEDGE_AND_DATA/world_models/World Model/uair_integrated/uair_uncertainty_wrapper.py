"""
UAIR Uncertainty Wrapper - Phase 2 Integration

Enhances uncertainty quantification with UAIR UncertaintyLayer:
- Epistemic uncertainty (model uncertainty)
- Aleatoric uncertainty (inherent ambiguity)
- Retrieval uncertainty (evidence quality)
- Execution uncertainty (tool errors)
- Integration with Shadow seal confidence
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import UAIR contracts
import sys
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")
from uair.contracts import UncertaintyReport


@dataclass
class UncertaintyEnhanced:
    """Enhanced uncertainty with system-specific context."""
    overall_confidence: float
    epistemic: float
    aleatoric: float
    retrieval: float
    execution: float
    ood_score: float
    calibrated: bool
    seal_confidence: float = 0.0  # Confidence in Shadow seal
    source_count: int = 0  # Number of evidence sources
    computation_complexity: float = 0.0  # Complexity of computation
    reason_codes: List[str] = field(default_factory=list)


class UAIRUncertaintyWrapper:
    """
    UAIR-enhanced uncertainty quantification for the stationary system.
    
    This wrapper:
    - Decomposes uncertainty into multiple sources
    - Integrates with Shadow seal confidence
    - Tracks evidence source count
    - Measures computation complexity
    - Provides actionable uncertainty signals
    """
    
    def __init__(self, shadow_system, config: Optional[Dict] = None):
        self.shadow_system = shadow_system
        self.config = config or {}
        
        # Uncertainty metrics
        self.metrics = {
            "total_uncertainty_estimates": 0,
            "avg_confidence": 0.0,
            "high_uncertainty_count": 0,  # confidence < 0.5
            "low_uncertainty_count": 0,   # confidence > 0.8
        }
    
    def quantify_uncertainty(
        self,
        result: Any,
        verification_result: Optional[Any] = None,
        formula_name: Optional[str] = None,
        computation: Optional[str] = None,
        evidence_sources: Optional[List] = None
    ) -> UncertaintyEnhanced:
        """
        Quantify uncertainty for a mathematical operation or result.
        
        Args:
            result: The result to quantify uncertainty for
            verification_result: Optional verification result
            formula_name: Optional name of formula used
            computation: Optional computation string
            evidence_sources: Optional list of evidence sources
            
        Returns:
            UncertaintyEnhanced with decomposed uncertainty
        """
        self.metrics["total_uncertainty_estimates"] += 1
        
        # Initialize uncertainty components
        epistemic = 0.0
        aleatoric = 0.0
        retrieval = 0.0
        execution = 0.0
        ood_score = 0.0
        
        reason_codes = []
        
        # Epistemic uncertainty (model/knowledge uncertainty)
        if verification_result:
            if hasattr(verification_result, 'status'):
                if verification_result.status.value == "failed":
                    epistemic += 0.5
                    reason_codes.append("verification_failed")
                elif verification_result.status.value == "partial":
                    epistemic += 0.2
                    reason_codes.append("verification_partial")
        
        # Shadow seal confidence
        seal_confidence = 0.0
        if formula_name and self.shadow_system:
            if hasattr(self.shadow_system, 'verify_all'):
                verification = self.shadow_system.verify_all(force=False)
                formula_status = verification.get(formula_name, {}).get('status', 'UNKNOWN')
                if formula_status == 'INTACT':
                    seal_confidence = 0.9
                elif formula_status == 'COMPROMISED':
                    seal_confidence = 0.1
                    epistemic += 0.4
                    reason_codes.append("compromised_seal")
                else:
                    seal_confidence = 0.5
                    epistodic += 0.2
                    reason_codes.append("unknown_seal_status")
        
        # Aleatoric uncertainty (inherent ambiguity)
        if computation:
            # More complex computations have higher aleatoric uncertainty
            complexity = self._measure_computation_complexity(computation)
            aleatoric = min(complexity * 0.3, 0.5)
        
        # Retrieval uncertainty (evidence quality)
        if evidence_sources:
            source_count = len(evidence_sources)
            if source_count == 0:
                retrieval = 0.5
                reason_codes.append("no_evidence")
            elif source_count < 2:
                retrieval = 0.2
                reason_codes.append("limited_evidence")
            else:
                retrieval = 0.0
        else:
            retrieval = 0.3
            reason_codes.append("no_sources_provided")
        
        # Execution uncertainty (tool errors)
        if result is None:
            execution = 0.5
            reason_codes.append("null_result")
        elif isinstance(result, str) and "error" in result.lower():
            execution = 0.7
            reason_codes.append("error_in_result")
        
        # OOD score (out-of-distribution)
        # Simplified: high uncertainty = high OOD
        ood_score = (epistemic + aleatoric + retrieval + execution) / 4
        
        # Calculate overall confidence
        total_uncertainty = (epistemic + aleatoric + retrieval + execution) / 4
        overall_confidence = 1.0 - total_uncertainty
        
        # Clamp to [0, 1]
        overall_confidence = max(0.0, min(1.0, overall_confidence))
        
        # Update metrics
        if overall_confidence < 0.5:
            self.metrics["high_uncertainty_count"] += 1
        elif overall_confidence > 0.8:
            self.metrics["low_uncertainty_count"] += 1
        
        # Update average confidence
        total = self.metrics["total_uncertainty_estimates"]
        avg = self.metrics["avg_confidence"]
        self.metrics["avg_confidence"] = (avg * (total - 1) + overall_confidence) / total
        
        computation_complexity = self._measure_computation_complexity(computation) if computation else 0.0
        
        return UncertaintyEnhanced(
            overall_confidence=overall_confidence,
            epistemic=epistemic,
            aleatoric=aleatoric,
            retrieval=retrieval,
            execution=execution,
            ood_score=ood_score,
            calibrated=False,  # Not calibrated in v0.1
            seal_confidence=seal_confidence,
            source_count=len(evidence_sources) if evidence_sources else 0,
            computation_complexity=computation_complexity,
            reason_codes=reason_codes
        )
    
    def _measure_computation_complexity(self, computation: str) -> float:
        """Measure computational complexity of a computation string."""
        if not computation:
            return 0.0
        
        complexity = 0.0
        
        # Count operators
        operators = len(re.findall(r"[\+\-\*\/\^]", computation))
        complexity += operators * 0.1
        
        # Count parentheses (nesting depth)
        max_nesting = 0
        current_nesting = 0
        for char in computation:
            if char == "(":
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif char == ")":
                current_nesting -= 1
        complexity += max_nesting * 0.15
        
        # Count functions
        functions = len(re.findall(r"(sin|cos|tan|log|exp|sqrt|abs)", computation, re.IGNORECASE))
        complexity += functions * 0.2
        
        return min(complexity, 1.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get uncertainty metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "total_uncertainty_estimates": 0,
            "avg_confidence": 0.0,
            "high_uncertainty_count": 0,
            "low_uncertainty_count": 0,
        }
    
    def to_uair_report(self, enhanced: UncertaintyEnhanced) -> UncertaintyReport:
        """Convert UncertaintyEnhanced to UAIR UncertaintyReport."""
        return UncertaintyReport(
            overall_confidence=enhanced.overall_confidence,
            epistemic=enhanced.epistemic,
            aleatoric=enhanced.aleatoric,
            retrieval=enhanced.retrieval,
            execution=enhanced.execution,
            ood_score=enhanced.ood_score,
            calibrated=enhanced.calibrated,
            reason_codes=enhanced.reason_codes
        )
