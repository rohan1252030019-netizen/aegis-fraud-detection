"""
AEGIS - Multi-Layer Evidence Fusion Engine
Extensible formula:
R = f(T, A, G, H, C)
Where:
- T: Temporal Anomaly Score
- A: Behavioral Anomaly Score (Isolation Forest)
- G: Graph Correlation Score (Network topology)
- H: Historical Threat Memory Match Score
- C: Contextual / Entity Risk Score
Computes composite risk, confidence factors, and generates UnifiedRiskProfile.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from ml.fusion.evidence import EvidenceItem, LayerScore, UnifiedRiskProfile


class EvidenceFusionEngine:
    def __init__(
        self,
        weight_temporal: float = 0.25,
        weight_behavioral: float = 0.25,
        weight_graph: float = 0.30,
        weight_historical: float = 0.10,
        weight_contextual: float = 0.10,
    ):
        # Configurable weights summing to 1.0
        self.w_t = weight_temporal
        self.w_a = weight_behavioral
        self.w_g = weight_graph
        self.w_h = weight_historical
        self.w_c = weight_contextual

    def fuse(
        self,
        account_id: str,
        temporal_score: float = 0.0,
        behavioral_score: float = 0.0,
        graph_score: float = 0.0,
        historical_score: float = 0.0,
        contextual_score: float = 0.0,
        evidence_items: Optional[list[EvidenceItem]] = None,
        threat_memory_matches: Optional[list[dict[str, Any]]] = None,
        shap_contributions: Optional[dict[str, Any]] = None,
        verification_status: str = "VERIFIED",
    ) -> UnifiedRiskProfile:
        all_evidence = evidence_items or []
        t_matches = threat_memory_matches or []

        # 1. Compute Composite Risk Score R = f(T, A, G, H, C)
        composite = (
            (temporal_score * self.w_t)
            + (behavioral_score * self.w_a)
            + (graph_score * self.w_g)
            + (historical_score * self.w_h)
            + (contextual_score * self.w_c)
        )
        composite = round(min(100.0, max(0.0, composite)), 1)

        # 2. Derive Structured Confidence
        signals_triggered = sum(1 for s in [temporal_score, behavioral_score, graph_score, historical_score] if s >= 40.0)
        signal_agreement = signals_triggered / 4.0

        confidence_factors = {
            "signal_agreement": round(signal_agreement, 2),
            "evidence_volume": round(min(1.0, len(all_evidence) / 5.0), 2),
            "verification_confidence": 1.0 if verification_status == "VERIFIED" else 0.7,
            "threat_memory_relevance": 0.95 if t_matches else 0.85,
        }

        derived_confidence = round(
            (confidence_factors["signal_agreement"] * 0.35)
            + (confidence_factors["evidence_volume"] * 0.25)
            + (confidence_factors["verification_confidence"] * 0.25)
            + (confidence_factors["threat_memory_relevance"] * 0.15),
            2
        )
        derived_confidence = max(0.50, min(0.99, derived_confidence))

        conf_exp = (
            f"Confidence calculated at {round(derived_confidence * 100)}% based on {signals_triggered}/4 "
            f"converging detection layers, {len(all_evidence)} corroborated evidence items, and {verification_status} audit trail."
        )

        # 3. Classify Account Risk & Typology
        if composite >= 80.0:
            risk_level = "CRITICAL"
            classification = "CONFIRMED_MULE" if signals_triggered >= 2 else "POTENTIAL_MULE"
        elif composite >= 60.0:
            risk_level = "HIGH"
            classification = "POTENTIAL_MULE"
        elif composite >= 40.0:
            risk_level = "ELEVATED"
            classification = "UNUSUAL"
        elif composite >= 20.0:
            risk_level = "MODERATE"
            classification = "NORMAL"
        else:
            risk_level = "LOW"
            classification = "NORMAL"

        # 4. Construct Layer Summaries
        layer_scores = {
            "temporal": LayerScore(
                source="Temporal Analysis (Rules + Transformer)",
                score=temporal_score,
                confidence=0.92,
                weight=self.w_t,
                model_version="1.0.0",
                evidence_count=sum(1 for e in all_evidence if "TEMPORAL" in str(e.source_type)),
                summary=f"Temporal score: {temporal_score}/100",
            ),
            "behavioral": LayerScore(
                source="Behavioral Outlier (Isolation Forest)",
                score=behavioral_score,
                confidence=0.91,
                weight=self.w_a,
                model_version="1.0.0",
                evidence_count=sum(1 for e in all_evidence if "BEHAVIORAL" in str(e.source_type)),
                summary=f"Behavioral score: {behavioral_score}/100",
            ),
            "graph": LayerScore(
                source="Graph Topology (NetworkX)",
                score=graph_score,
                confidence=0.94,
                weight=self.w_g,
                model_version="1.0.0",
                evidence_count=sum(1 for e in all_evidence if "GRAPH" in str(e.source_type)),
                summary=f"Network score: {graph_score}/100",
            ),
            "threat_memory": LayerScore(
                source="Historical Threat Memory",
                score=historical_score,
                confidence=0.95,
                weight=self.w_h,
                model_version="1.0.0",
                evidence_count=len(t_matches),
                summary=f"Historical match score: {historical_score}/100",
            ),
            "contextual": LayerScore(
                source="Contextual / Entity Risk",
                score=contextual_score,
                confidence=0.90,
                weight=self.w_c,
                model_version="1.0.0",
                evidence_count=0,
                summary=f"Contextual score: {contextual_score}/100",
            ),
        }

        return UnifiedRiskProfile(
            account_id=account_id,
            composite_score=composite,
            risk_level=risk_level,
            classification=classification,
            confidence=derived_confidence,
            confidence_factors=confidence_factors,
            confidence_explanation=conf_exp,
            layer_scores=layer_scores,
            evidence_items=all_evidence,
            shap_contributions=shap_contributions,
            verification_status=verification_status,
            threat_memory_matches=t_matches,
        )
