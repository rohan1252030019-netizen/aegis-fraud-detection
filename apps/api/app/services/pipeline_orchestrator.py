"""
AEGIS - End-to-End Detection Pipeline Orchestrator
Connects:
DATA PREPROCESSING
       ↓
┌──────────────┬───────────────┬───────────────┐
│              │               │
TEMPORAL       BEHAVIORAL      GRAPH
ANALYSIS       ANOMALY         CORRELATION
│              │               │
└──────────────┴───────────────┘
       ↓
EVIDENCE FUSION
       ↓
SHAP EXPLAINABILITY
       ↓
FORMAL VERIFICATION
       ↓
THREAT MEMORY RETRIEVAL
       ↓
LOCAL OLLAMA INTELLIGENCE
       ↓
VERIFIED REPORT ARTIFACT
"""
from __future__ import annotations
import time
from typing import Any
import pandas as pd
from ml.preprocessing.pipeline import DataQualityPipeline, PreprocessingReport
from ml.temporal.engine import TemporalAnalysisEngine
from ml.behavioral.detector import BehavioralAnomalyDetector
from ml.graph.engine import FinancialGraphEngine
from ml.fusion.engine import EvidenceFusionEngine
from ml.fusion.evidence import UnifiedRiskProfile, EvidenceItem
from ml.explainability.engine import SHAPExplainabilityEngine
from ml.verification.engine import FormalVerificationEngine
from ml.threat_memory.store import ThreatMemoryStore
from ml.llm.client import OllamaIntelligenceClient


class AegisPipelineOrchestrator:
    def __init__(self):
        self.preprocessor = DataQualityPipeline()
        self.temporal_engine = TemporalAnalysisEngine()
        self.behavioral_detector = BehavioralAnomalyDetector()
        self.graph_engine = FinancialGraphEngine()
        self.fusion_engine = EvidenceFusionEngine()
        self.shap_engine = SHAPExplainabilityEngine(self.behavioral_detector)
        self.verifier = FormalVerificationEngine()
        self.threat_memory = ThreatMemoryStore()
        self.ollama_client = OllamaIntelligenceClient()

    def run_account_investigation(
        self,
        account_id: str,
        df: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Runs the complete, multi-layer verified detection pipeline for an account.
        Measures monotonic duration for every pipeline step.
        """
        trace = []
        start_total = time.monotonic()

        # Step 1: Preprocessing & Data Quality check
        t0 = time.monotonic()
        clean_df, quality_report = self.preprocessor.process(df)
        dur_prep = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "PREPROCESSING",
            "duration_ms": dur_prep,
            "status": "COMPLETED",
            "quality_score": quality_report.quality_score,
        })

        # Step 2: Temporal Analysis (Rule + Transformer)
        t0 = time.monotonic()
        temp_evidence = self.temporal_engine.analyze_account(account_id, clean_df)
        dur_temp = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "TEMPORAL_ANALYSIS",
            "duration_ms": dur_temp,
            "status": "COMPLETED",
            "score": temp_evidence.temporal_score,
            "patterns": [p["pattern"] for p in temp_evidence.detected_patterns],
        })

        # Step 3: Behavioral Anomaly Detection (Isolation Forest)
        t0 = time.monotonic()
        behav_evidence = self.behavioral_detector.assess_account(account_id, clean_df)
        dur_behav = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "BEHAVIORAL_ANOMALY",
            "duration_ms": dur_behav,
            "status": "COMPLETED",
            "score": behav_evidence.behavioral_score,
            "is_outlier": behav_evidence.is_anomalous,
        })

        # Step 4: Graph Correlation (NetworkX Topology)
        t0 = time.monotonic()
        graph_evidence = self.graph_engine.analyze_account(account_id, clean_df)
        dur_graph = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "GRAPH_CORRELATION",
            "duration_ms": dur_graph,
            "status": "COMPLETED",
            "score": graph_evidence.network_risk_score,
            "patterns": [p["pattern"] for p in graph_evidence.detected_patterns],
        })

        # Step 5: Threat Memory Pattern Retrieval
        t0 = time.monotonic()
        query_sig = [behav_evidence.extracted_features.get(k, 0.0) for k in behav_evidence.extracted_features]
        t_matches = self.threat_memory.search_similar_patterns(query_sig, top_k=2)
        hist_scores = [
            m["historical_risk"] * m["similarity_score"]
            for m in t_matches
            if m.get("confirmed_status") == "TRUE_POSITIVE"
        ]
        hist_score = max(hist_scores, default=0.0)
        dur_tm = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "THREAT_MEMORY_RETRIEVAL",
            "duration_ms": dur_tm,
            "status": "COMPLETED",
            "matches_found": len(t_matches),
        })

        # Step 6: SHAP Explainability
        t0 = time.monotonic()
        explanation = self.shap_engine.explain_account(account_id, clean_df)
        dur_shap = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "SHAP_EXPLAINABILITY",
            "duration_ms": dur_shap,
            "status": "COMPLETED",
            "top_drivers": explanation.top_risk_drivers,
        })

        # Collect all corroborated evidence items
        all_evidence: list[EvidenceItem] = (
            temp_evidence.evidence_items
            + behav_evidence.evidence_items
            + graph_evidence.evidence_items
        )

        # Step 7: Rule-Based Formal Verification
        t0 = time.monotonic()
        verif_report = self.verifier.verify_evidence(account_id, all_evidence, clean_df)
        dur_verif = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "FORMAL_VERIFICATION",
            "duration_ms": dur_verif,
            "status": verif_report.overall_status,
            "checks_passed": verif_report.passed_checks,
        })

        # Step 8: Multi-Layer Evidence Fusion
        t0 = time.monotonic()
        fused_profile = self.fusion_engine.fuse(
            account_id=account_id,
            temporal_score=temp_evidence.temporal_score,
            behavioral_score=behav_evidence.behavioral_score,
            graph_score=graph_evidence.network_risk_score,
            historical_score=hist_score,
            evidence_items=all_evidence,
            threat_memory_matches=t_matches,
            shap_contributions=explanation.to_dict(),
            verification_status=verif_report.overall_status,
        )
        dur_fusion = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "EVIDENCE_FUSION",
            "duration_ms": dur_fusion,
            "status": "COMPLETED",
            "composite_score": fused_profile.composite_score,
            "risk_level": fused_profile.risk_level,
        })

        # Step 9: Local Ollama Investigation Narrative
        t0 = time.monotonic()
        evidence_descriptions = [e.description for e in all_evidence]
        brief = self.ollama_client.generate_investigation_brief(
            account_id=account_id,
            composite_score=fused_profile.composite_score,
            risk_level=fused_profile.risk_level,
            classification=fused_profile.classification,
            evidence_descriptions=evidence_descriptions,
            top_shap_factors=explanation.top_risk_drivers,
            threat_memory_matches=t_matches,
            formal_verification_status=verif_report.overall_status,
        )
        dur_llm = round((time.monotonic() - t0) * 1000, 2)
        trace.append({
            "stage": "LOCAL_INVESTIGATION_INTELLIGENCE",
            "duration_ms": dur_llm,
            "status": "COMPLETED",
            "provider": brief["provider"],
        })

        dur_total = round((time.monotonic() - start_total) * 1000, 2)

        return {
            "account_id": account_id,
            "risk_profile": fused_profile.to_dict(),
            "temporal_evidence": {
                "score": temp_evidence.temporal_score,
                "transformer_score": temp_evidence.transformer_score,
                "patterns": temp_evidence.detected_patterns,
            },
            "behavioral_evidence": {
                "score": behav_evidence.behavioral_score,
                "raw_score": behav_evidence.raw_anomaly_score,
                "features": behav_evidence.extracted_features,
            },
            "graph_evidence": {
                "score": graph_evidence.network_risk_score,
                "patterns": graph_evidence.detected_patterns,
                "fan_in": graph_evidence.fan_in_degree,
                "fan_out": graph_evidence.fan_out_degree,
                "cycles": graph_evidence.cycles_detected,
                "shared_device_accounts": graph_evidence.shared_device_accounts,
            },
            "explainability": explanation.to_dict(),
            "formal_verification": verif_report.to_dict(),
            "threat_memory_matches": t_matches,
            "investigation_brief": brief,
            "data_quality": quality_report.to_dict(),
            "pipeline_trace": trace,
            "total_execution_ms": dur_total,
        }


pipeline_orchestrator = AegisPipelineOrchestrator()
