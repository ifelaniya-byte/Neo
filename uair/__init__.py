"""
UniCompact Adaptive Intelligence Runtime (UAIR)

A modular, measurable adaptive intelligence runtime that routes requests
to the cheapest verified execution path capable of meeting quality and safety contracts.

This is NOT an LLM replacement. It is an orchestrator that:
- Uses deterministic solvers when possible
- Uses retrieval for factual tasks
- Uses LLMs only when language synthesis is necessary
- Measures cost per verified success
- Enforces uncertainty quantification and safety gates
"""

__version__ = "0.1.0"
__author__ = "UAIR Development Team"

from .contracts import Request, Response, RoutePlan, EvidenceItem, UncertaintyReport, Sensitivity, TaskClass, RoutePath
from .orchestrator import UAIRRuntime

__all__ = [
    "Request",
    "Response", 
    "RoutePlan",
    "EvidenceItem",
    "UncertaintyReport",
    "UAIRRuntime",
    "Sensitivity",
    "TaskClass",
    "RoutePath",
]
