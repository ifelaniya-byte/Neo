"""
UAIR-Integrated Stationary System

Combines UAIR (UniCompact Adaptive Intelligence Runtime) with the
stationary/non-stationary mathematical and knowledge system.

Integration Phases:
- Phase 1: UAIR Routing Integration
- Phase 2: UAIR Verification Enhancement  
- Phase 3: MegaCompact16 Decision Layer (optional)
"""

__version__ = "1.0.0"
__author__ = "UAIR + Stationary Integration"

from .uair_orchestrator import UAIRIntegratedRuntime
from .uair_enhanced_router import UAIREnhancedRouter
from .uair_math_verifier import UAIRMathVerifier
from .uair_uncertainty_wrapper import UAIRUncertaintyWrapper

__all__ = [
    "UAIRIntegratedRuntime",
    "UAIREnhancedRouter",
    "UAIRMathVerifier",
    "UAIRUncertaintyWrapper",
]
