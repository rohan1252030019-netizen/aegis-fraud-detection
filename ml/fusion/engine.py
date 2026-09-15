"""AEGIS - Multi-Layer Evidence Fusion Engine"""
from dataclasses import dataclass, field
from app.models.enums import RiskLevel, AccountClassification


@dataclass
class FusionResult:
    account_id: str
    composite_score: float
    risk_level: str
    classification: str
    temporal_score: float = 0.0
    behavioral_score: float = 0.0
    graph_score: float = 0.0
    confidence: float = 0.95


class EvidenceFusionEngine:
    def __init__(
        self,
        weight_temporal: float = 0.35,
        weight_behavioral: float = 0.35,
        weight_graph: float = 0.30,
    ):
        self.w_t = weight_temporal
        self.w_b = weight_behavioral
        self.w_g = weight_graph

    def fuse(
        self,
        account_id: str,
        temporal_score: float = 0.0,
        behavioral_score: float = 0.0,
        graph_score: float = 0.0,
    ) -> FusionResult:
        composite = (
            temporal_score * self.w_t
            + behavioral_score * self.w_b
            + graph_score * self.w_g
        )
        composite = round(min(100.0, max(0.0, composite)), 2)

        if composite >= 80:
            risk_level = RiskLevel.CRITICAL
            classification = AccountClassification.CONFIRMED_MULE
        elif composite >= 60:
            risk_level = RiskLevel.HIGH
            classification = AccountClassification.POTENTIAL_MULE
        elif composite >= 40:
            risk_level = RiskLevel.ELEVATED
            classification = AccountClassification.UNUSUAL
        elif composite >= 20:
            risk_level = RiskLevel.MODERATE
            classification = AccountClassification.NORMAL
        else:
            risk_level = RiskLevel.LOW
            classification = AccountClassification.NORMAL

        return FusionResult(
            account_id=account_id,
            composite_score=composite,
            risk_level=risk_level,
            classification=classification,
            temporal_score=temporal_score,
            behavioral_score=behavioral_score,
            graph_score=graph_score,
        )
