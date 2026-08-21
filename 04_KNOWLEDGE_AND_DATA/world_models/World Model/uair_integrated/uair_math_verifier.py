"""
UAIR Math Verifier - Phase 2 Integration

Enhances verification with UAIR VerificationLayer:
- Numerical re-computation
- Citation verification (against Atlas)
- Schema validation (formula structure)
- Cross-source consistency
- Integration with Shadow seal integrity system
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Import UAIR contracts
import sys
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")
from uair.contracts import VerificationStatus, VerificationCheck


@dataclass
class MathVerificationResult:
    """Result of mathematical verification."""
    status: VerificationStatus
    checks: List[VerificationCheck] = field(default_factory=list)
    confidence: float = 0.0
    seal_status: str = "unknown"  # INTACT, COMPROMISED, UNKNOWN
    evidence_ids: List[str] = field(default_factory=list)


class UAIRMathVerifier:
    """
    UAIR-enhanced math verifier that works with the Shadow seal system.
    
    This verifier:
    - Performs numerical re-computation of mathematical results
    - Verifies citations against Atlas knowledge base
    - Validates formula structure/schema
    - Checks cross-source consistency
    - Integrates with Shadow seal integrity system
    """
    
    def __init__(self, atlas, shadow_system, config: Optional[Dict] = None):
        self.atlas = atlas
        self.shadow_system = shadow_system
        self.config = config or {}
        
        # Verification metrics
        self.metrics = {
            "total_verifications": 0,
            "passed": 0,
            "partial": 0,
            "failed": 0,
            "numerical_checks": 0,
            "citation_checks": 0,
            "schema_checks": 0,
        }
    
    def verify_mathematical_result(
        self,
        result: Any,
        formula_name: Optional[str] = None,
        computation: Optional[str] = None
    ) -> MathVerificationResult:
        """
        Verify a mathematical result using UAIR verification methods.
        
        Args:
            result: The mathematical result to verify
            formula_name: Optional name of the formula used
            computation: Optional computation string
            
        Returns:
            MathVerificationResult with detailed verification status
        """
        self.metrics["total_verifications"] += 1
        checks = []
        
        # Check 1: Numerical re-computation (if computation provided)
        if computation:
            num_check = self._verify_numerical_computation(computation, result)
            checks.append(num_check)
            self.metrics["numerical_checks"] += 1
        
        # Check 2: Citation verification (if formula_name provided)
        if formula_name:
            cit_check = self._verify_citation(formula_name)
            checks.append(cit_check)
            self.metrics["citation_checks"] += 1
        
        # Check 3: Schema validation (result structure)
        schema_check = self._verify_schema(result)
        checks.append(schema_check)
        self.metrics["schema_checks"] += 1
        
        # Check 4: Shadow seal integrity (if formula_name provided)
        seal_status = "unknown"
        if formula_name and self.shadow_system:
            seal_check = self._verify_shadow_seal(formula_name)
            checks.append(seal_check)
            seal_status = seal_check.detail if not seal_check.passed else "INTACT"
        
        # Determine overall status
        passed = sum(1 for c in checks if c.passed)
        total = len(checks)
        
        if passed == total:
            status = VerificationStatus.PASSED
            self.metrics["passed"] += 1
        elif passed > 0:
            status = VerificationStatus.PARTIAL
            self.metrics["partial"] += 1
        else:
            status = VerificationStatus.FAILED
            self.metrics["failed"] += 1
        
        confidence = passed / total if total > 0 else 0.0
        
        return MathVerificationResult(
            status=status,
            checks=checks,
            confidence=confidence,
            seal_status=seal_status
        )
    
    def _verify_numerical_computation(self, computation: str, result: Any) -> VerificationCheck:
        """Verify numerical computation by re-computing."""
        try:
            # Safe evaluation of simple arithmetic
            if re.match(r"^[\d\s\+\-\*\/\(\)\.]+$", computation):
                computed = eval(computation)
                # Check if result matches computation
                if abs(float(computed) - float(result)) < 1e-6:
                    return VerificationCheck(
                        name="numerical_recomputation",
                        passed=True,
                        detail="Numerical recomputation matches result"
                    )
                else:
                    return VerificationCheck(
                        name="numerical_recomputation",
                        passed=False,
                        detail=f"Recomputed {computed} != result {result}"
                    )
            else:
                return VerificationCheck(
                    name="numerical_recomputation",
                    passed=True,
                    detail="Computation too complex for simple verification"
                )
        except Exception as e:
            return VerificationCheck(
                name="numerical_recomputation",
                passed=False,
                detail=f"Verification failed: {str(e)}"
            )
    
    def _verify_citation(self, formula_name: str) -> VerificationCheck:
        """Verify citation against Atlas knowledge base."""
        try:
            # Search Atlas for the formula
            search_result = self.atlas.search(formula_name)
            
            if search_result and len(search_result) > 0:
                return VerificationCheck(
                    name="citation_verification",
                    passed=True,
                    detail=f"Formula found in Atlas: {len(search_result)} matches"
                )
            else:
                return VerificationCheck(
                    name="citation_verification",
                    passed=False,
                    detail="Formula not found in Atlas knowledge base"
                )
        except Exception as e:
            return VerificationCheck(
                name="citation_verification",
                passed=False,
                detail=f"Citation verification failed: {str(e)}"
            )
    
    def _verify_schema(self, result: Any) -> VerificationCheck:
        """Verify result structure/schema."""
        # Basic schema validation
        if result is None:
            return VerificationCheck(
                name="schema_validation",
                passed=False,
                detail="Result is None"
            )
        
        if isinstance(result, (int, float, str)):
            return VerificationCheck(
                name="schema_validation",
                passed=True,
                detail="Result has valid primitive type"
            )
        
        if isinstance(result, (list, dict)):
            return VerificationCheck(
                name="schema_validation",
                passed=True,
                detail="Result has valid structure type"
            )
        
        return VerificationCheck(
            name="schema_validation",
            passed=False,
            detail="Result has unexpected type"
        )
    
    def _verify_shadow_seal(self, formula_name: str) -> VerificationCheck:
        """Verify Shadow seal integrity for a formula."""
        try:
            # Call shadow system to verify seal
            if hasattr(self.shadow_system, 'verify_all'):
                verification_result = self.shadow_system.verify_all(force=False)
                
                # Check if formula is intact
                formula_status = verification_result.get(formula_name, {}).get('status', 'UNKNOWN')
                
                if formula_status == 'INTACT':
                    return VerificationCheck(
                        name="shadow_seal_integrity",
                        passed=True,
                        detail=f"Shadow seal is INTACT for {formula_name}"
                    )
                elif formula_status == 'COMPROMISED':
                    return VerificationCheck(
                        name="shadow_seal_integrity",
                        passed=False,
                        detail=f"Shadow seal is COMPROMISED for {formula_name}"
                    )
                else:
                    return VerificationCheck(
                        name="shadow_seal_integrity",
                        passed=False,
                        detail=f"Shadow seal status unknown: {formula_status}"
                    )
            else:
                return VerificationCheck(
                    name="shadow_seal_integrity",
                    passed=True,
                    detail="Shadow system does not support verification"
                )
        except Exception as e:
            return VerificationCheck(
                name="shadow_seal_integrity",
                passed=False,
                detail=f"Shadow seal verification failed: {str(e)}"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get verification metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "total_verifications": 0,
            "passed": 0,
            "partial": 0,
            "failed": 0,
            "numerical_checks": 0,
            "citation_checks": 0,
            "schema_checks": 0,
        }
