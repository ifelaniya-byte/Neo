"""
Data contracts for UAIR - typed interfaces between components.

All cross-module communication uses these contracts to ensure type safety,
provenance tracking, and auditable traces.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid


class Sensitivity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskClass(Enum):
    ARITHMETIC = "arithmetic"
    DATA_EXTRACTION = "data_extraction"
    CODE_EXECUTION = "code_execution"
    KNOWLEDGE_LOOKUP = "knowledge_lookup"
    DOC_QA = "doc_qa"
    STRUCTURED_TRANSFORM = "structured_transform"
    CREATIVE_GENERATION = "creative_generation"
    PLANNING = "planning"
    DEFI_ANALYSIS = "defi_analysis"
    UNKNOWN = "unknown"


class RoutePath(Enum):
    CACHE = "cache"
    DETERMINISTIC = "deterministic"
    RETRIEVAL = "retrieval"
    SPECIALIST = "specialist"
    LLM = "llm"
    HYBRID = "hybrid"
    CLARIFY = "clarify"
    ABSTAIN = "abstain"


class ResponseStatus(Enum):
    ANSWERED = "answered"
    CLARIFY = "clarify"
    ABSTAINED = "abstained"
    REFUSED = "refused"
    FAILED = "failed"


class VerificationStatus(Enum):
    PASSED = "passed"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class SafetyStatus(Enum):
    PASSED = "passed"
    BLOCKED = "blocked"
    REVIEW = "review"


class TrustTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceType(Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    TOOL = "tool"
    USER = "user"
    MODEL = "model"


@dataclass
class Request:
    """Canonical request object from user to UAIR."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id_hash: Optional[str] = None
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    input_text: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    session_context_ids: List[str] = field(default_factory=list)
    task_hint: Optional[str] = None
    sensitivity: Sensitivity = Sensitivity.LOW
    max_latency_ms: int = 5000
    max_cost_usd: float = 0.10
    allow_external_tools: bool = False
    allow_memory: bool = False
    locale: str = "en"


@dataclass
class NormalizedInput:
    """Normalized and validated input from Request."""
    text_norm: str = ""
    lang: str = "en"
    char_count: int = 0
    attachment_manifest: List[Dict[str, Any]] = field(default_factory=list)
    pii_flags: List[str] = field(default_factory=list)
    injection_flags: List[str] = field(default_factory=list)
    unsupported_flags: List[str] = field(default_factory=list)
    canonical_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentReport:
    """Intent classification with confidence distribution."""
    intent_distribution: Dict[TaskClass, float] = field(default_factory=dict)
    top_k: List[tuple[TaskClass, float]] = field(default_factory=list)
    classifier_version: str = "v0.1"
    needs_clarification: bool = False
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class ComplexityReport:
    """Complexity and risk estimation for routing."""
    context_need: float = 0.5
    depth: float = 0.5
    expected_tools: int = 0
    expected_out_len: int = 100
    sensitivity: Sensitivity = Sensitivity.LOW
    verification_burden: float = 0.5
    estimator_version: str = "v0.1"


@dataclass
class RoutePlan:
    """Planned execution route with budgets."""
    intent_distribution: Dict[TaskClass, float] = field(default_factory=dict)
    complexity_score: float = 0.5
    risk_score: float = 0.5
    selected_path: RoutePath = RoutePath.ABSTAIN
    token_budget: int = 1000
    retrieval_budget: int = 5
    tool_budget: int = 3
    verification_plan: List[str] = field(default_factory=list)
    fallback_path: RoutePath = RoutePath.ABSTAIN
    reason_codes: List[str] = field(default_factory=list)
    predicted_cost_usd: float = 0.01
    predicted_latency_ms: int = 100


@dataclass
class EvidenceItem:
    """Retrieved evidence with provenance."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType = SourceType.DOCUMENT
    source_uri_or_id: str = ""
    source_timestamp: str = ""
    content_hash: str = ""
    passage: str = ""
    relevance_score: float = 0.0
    trust_tier: TrustTier = TrustTier.MEDIUM
    license_status: str = "unknown"
    retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_name: str = ""
    version: str = "v0.1"
    args_hash: str = ""
    ok: bool = False
    output: Any = None
    error: Optional[str] = None
    latency_ms: int = 0


@dataclass
class UncertaintyReport:
    """Decomposed uncertainty with calibration status."""
    overall_confidence: float = 0.5
    epistemic: float = 0.0  # Model uncertainty
    aleatoric: float = 0.0  # Inherent ambiguity
    retrieval: float = 0.0  # Evidence uncertainty
    execution: float = 0.0  # Tool failure uncertainty
    ood_score: float = 0.0  # Out-of-distribution score
    calibrated: bool = False
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class VerificationCheck:
    """Single verification check result."""
    name: str = ""
    passed: bool = False
    detail: str = ""


@dataclass
class VerificationReport:
    """Aggregated verification results."""
    status: VerificationStatus = VerificationStatus.NOT_APPLICABLE
    checks: List[VerificationCheck] = field(default_factory=list)


@dataclass
class SafetyCheck:
    """Single safety check result."""
    name: str = ""
    passed: bool = False
    reason_code: str = ""


@dataclass
class SafetyReport:
    """Aggregated safety check results."""
    status: SafetyStatus = SafetyStatus.PASSED
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class CostMetrics:
    """Cost breakdown for the request."""
    input_tokens: int = 0
    output_tokens: int = 0
    retrieval_tokens: int = 0
    tool_calls: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class SystemVersions:
    """Version tracking for all components."""
    router: str = "v0.1"
    models: Dict[str, str] = field(default_factory=dict)
    prompts: Dict[str, str] = field(default_factory=dict)
    index: str = "v0.1"
    policy: str = "v0.1"


@dataclass
class Response:
    """Canonical response from UAIR to user."""
    answer: Any = None
    status: ResponseStatus = ResponseStatus.FAILED
    route_used: RoutePath = RoutePath.ABSTAIN
    evidence_ids: List[str] = field(default_factory=list)
    uncertainty: UncertaintyReport = field(default_factory=UncertaintyReport)
    verification: VerificationReport = field(default_factory=VerificationReport)
    safety: SafetyReport = field(default_factory=SafetyReport)
    cost: CostMetrics = field(default_factory=CostMetrics)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: SystemVersions = field(default_factory=SystemVersions)
