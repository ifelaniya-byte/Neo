"""
UAIR-Integrated Stationary System

Combines UAIR (UniCompact Adaptive Intelligence Runtime) with the
stationary/non-stationary mathematical and knowledge system.

Integration Phases:
- Phase 1: UAIR Routing Integration
- Phase 2: UAIR Verification Enhancement  
- Phase 3: MegaCompact16 Decision Layer (optional)

Superintelligence Components:
- Phase 1A: External LLM Integration
- Phase 1B: Learned Routing
- Phase 2A: World Model with Simulation
- Phase 2B: Continuous Learning
"""

__version__ = "2.0.0"
__author__ = "UAIR + Stationary + Superintelligence Integration"

from .uair_orchestrator import UAIRIntegratedRuntime
from .uair_enhanced_router import UAIREnhancedRouter
from .uair_math_verifier import UAIRMathVerifier
from .uair_uncertainty_wrapper import UAIRUncertaintyWrapper

# Superintelligence components
from .llm_client import LLMClient, LLMProvider, LLMResponse
from .learned_routing import LearnedRouter, RoutingDataCollector, RoutingModel, RoutingFeatures
from .world_model import WorldModel, WorldState, Action, Planner
from .continuous_learning import ContinuousLearning, Experience, ExperienceBuffer
from .superintelligence_orchestrator import SuperintelligenceRuntime, SuperintelligenceActor

__all__ = [
    # UAIR Integration
    "UAIRIntegratedRuntime",
    "UAIREnhancedRouter",
    "UAIRMathVerifier",
    "UAIRUncertaintyWrapper",
    # Superintelligence
    "LLMClient",
    "LLMProvider",
    "LLMResponse",
    "LearnedRouter",
    "RoutingDataCollector",
    "RoutingModel",
    "WorldModel",
    "WorldState",
    "Action",
    "Planner",
    "ContinuousLearning",
    "Experience",
    "ExperienceBuffer",
    "SuperintelligenceRuntime",
    "SuperintelligenceActor",
]
