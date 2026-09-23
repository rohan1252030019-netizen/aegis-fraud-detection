"""
AEGIS - Standardized Evidence Object Model
Unified schema for evidence generated across Temporal, Behavioral, Graph, Threat Memory, and Verification layers.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


class EvidenceSourceType(str, Enum):
    TEMPORAL_RULE = "TEMPORAL_RULE"
    TEMPORAL_TRANSFORMER = "TEMPORAL_TRANSFORMER"
    BEHAVIORAL_ISOLATION_FOREST = "BEHAVIORAL_ISOLATION_FOREST"
    GRAPH_TOPOLOGY = "GRAPH_TOPOLOGY"
    THREAT_MEMORY = "THREAT_MEMORY"
    CONTEXTUAL = "CONTEXTUAL"
    FORMAL_VERIFICATION = "FORMAL_VERIFICATION"


class EvidenceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class EvidenceItem:
    evidence_id: str = field(default_factory=lambda: f"EVID_{uuid.uuid4().hex[:12].upper()}")
    source_type: EvidenceSourceType = EvidenceSourceType.TEMPORAL_RULE
    source_record: str = ""  # ID of primary transaction, account, or graph cluster
    entity_id: str = ""       # Account ID being analyzed
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    feature: str = ""         # Feature or pattern name (e.g. 'burst_frequency', 'passthrough_ratio')
    observed_value: Any = None
    expected_value: Any = None
    severity: EvidenceSeverity = EvidenceSeverity.MEDIUM
    score_contribution: float = 0.0  # Points contributed to the composite score
    confidence: float = 0.9          # Measurable confidence of this specific observation (0.0 - 1.0)
    rule_or_model: str = ""          # e.g., 'IsolationForest_v1.1', 'TransformerSequence_v1.0'
    model_version: str = "1.0.0"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["source_type"] = self.source_type.value if hasattr(self.source_type, "value") else str(self.source_type)
        d["severity"] = self.severity.value if hasattr(self.severity, "value") else str(self.severity)
        return d


@dataclass
class LayerScore:
    source: str
    score: float
    confidence: float
    weight: float
    model_version: str
    evidence_count: int
    summary: str


@dataclass
class UnifiedRiskProfile:
    account_id: str
    composite_score: float
    risk_level: str
    classification: str
    confidence: float
    confidence_factors: dict[str, float]
    confidence_explanation: str
    layer_scores: dict[str, LayerScore]
    evidence_items: list[EvidenceItem]
    shap_contributions: Optional[dict[str, Any]] = None
    verification_status: str = "PENDING"
    threat_memory_matches: list[dict[str, Any]] = field(default_factory=list)
    computed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "composite_score": self.composite_score,
            "risk_level": self.risk_level,
            "classification": self.classification,
            "confidence": self.confidence,
            "confidence_factors": self.confidence_factors,
            "confidence_explanation": self.confidence_explanation,
            "layer_scores": {k: asdict(v) for k, v in self.layer_scores.items()},
            "evidence_items": [e.to_dict() for e in self.evidence_items],
            "shap_contributions": self.shap_contributions,
            "verification_status": self.verification_status,
            "threat_memory_matches": self.threat_memory_matches,
            "computed_at": self.computed_at,
        }
