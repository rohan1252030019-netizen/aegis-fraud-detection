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
import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional
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
        progress_callback: Any = None,
        cancellation_check: Any = None,
    ) -> dict[str, Any]:
        """
        Runs the complete, multi-layer verified detection pipeline for an account.
        Measures monotonic duration for every pipeline step with real timestamps and counts.
        """
        trace = []
        start_total = time.monotonic()

        def _check_cancel():
            if cancellation_check and cancellation_check():
                raise asyncio.CancelledError("Investigation cancelled by user.")

        def _notify(stage_name: str, status: str, meta: dict[str, Any]):
            if progress_callback:
                try:
                    progress_callback(stage_name, status, meta)
                except Exception:
                    pass

        # Step 1: Preprocessing & Data Quality check
        _check_cancel()
        _notify("PREPROCESSING", "RUNNING", {"label": "Running Preprocessing & Data Validation...", "input_count": len(df)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        clean_df, quality_report = self.preprocessor.process(df)
        dur_prep = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        prep_meta = {
            "stage": "PREPROCESSING",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_prep,
            "input_count": len(df),
            "output_count": len(clean_df),
            "error": None,
            "quality_score": quality_report.quality_score,
        }
        trace.append(prep_meta)
        _notify("PREPROCESSING", "COMPLETED", prep_meta)

        # Step 2: Temporal Analysis (Rules: velocity, burst, passthrough, structuring)
        _check_cancel()
        acc_txs_count = len(clean_df[(clean_df["sender_account_id"] == account_id) | (clean_df["receiver_account_id"] == account_id)])
        _notify("TEMPORAL_ANALYSIS", "RUNNING", {"label": "Running Temporal Velocity & Burst Analysis...", "input_count": acc_txs_count})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        rule_score, detected_patterns, evidence_list = self.temporal_engine.analyze_rules(account_id, clean_df)
        dur_temp = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        temp_meta = {
            "stage": "TEMPORAL_ANALYSIS",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_temp,
            "input_count": acc_txs_count,
            "output_count": len(detected_patterns),
            "error": None,
            "rule_score": rule_score,
            "patterns": [p["pattern"] for p in detected_patterns],
        }
        trace.append(temp_meta)
        _notify("TEMPORAL_ANALYSIS", "COMPLETED", temp_meta)

        # Step 3: Transformer Inference (PyTorch sequence anomaly model)
        _check_cancel()
        _notify("TRANSFORMER_INFERENCE", "RUNNING", {"label": "Running Transformer Sequence Inference...", "input_count": min(50, acc_txs_count)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        trans_result = self.temporal_engine.transformer_engine.predict_account(account_id, clean_df)
        t_score = trans_result["temporal_transformer_score"]
        temp_evidence = self.temporal_engine.blend_results(account_id, rule_score, detected_patterns, evidence_list, t_score)
        dur_trans = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        trans_meta = {
            "stage": "TRANSFORMER_INFERENCE",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_trans,
            "input_count": min(50, acc_txs_count),
            "output_count": 1,
            "error": None,
            "transformer_score": t_score,
        }
        trace.append(trans_meta)
        _notify("TRANSFORMER_INFERENCE", "COMPLETED", trans_meta)

        # Step 4: Behavioral Anomaly Detection (Isolation Forest)
        _check_cancel()
        _notify("BEHAVIORAL_ANALYSIS", "RUNNING", {"label": "Running Behavioral Anomaly Profiling (Isolation Forest)...", "input_count": 8})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        behav_evidence = self.behavioral_detector.assess_account(account_id, clean_df)
        dur_behav = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        behav_meta = {
            "stage": "BEHAVIORAL_ANALYSIS",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_behav,
            "input_count": 8,
            "output_count": 1,
            "error": None,
            "score": behav_evidence.behavioral_score,
            "is_outlier": behav_evidence.is_anomalous,
        }
        trace.append(behav_meta)
        _notify("BEHAVIORAL_ANALYSIS", "COMPLETED", behav_meta)

        # Step 5: Graph Correlation (NetworkX Topology, Fan-in/out, Cycles)
        _check_cancel()
        _notify("GRAPH_CORRELATION", "RUNNING", {"label": "Running Graph Correlation & Topology Analysis...", "input_count": len(clean_df)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        graph_evidence = self.graph_engine.analyze_account(account_id, clean_df)
        dur_graph = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        graph_meta = {
            "stage": "GRAPH_CORRELATION",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_graph,
            "input_count": len(clean_df),
            "output_count": len(graph_evidence.detected_patterns),
            "error": None,
            "score": graph_evidence.network_risk_score,
            "cycles_found": len(graph_evidence.cycles_detected),
        }
        trace.append(graph_meta)
        _notify("GRAPH_CORRELATION", "COMPLETED", graph_meta)

        # Step 6: SHAP Explainability (TreeExplainer feature attribution)
        _check_cancel()
        _notify("SHAP_EXPLANATION", "RUNNING", {"label": "Computing SHAP Explainability & Risk Drivers...", "input_count": 8})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        explanation = self.shap_engine.explain_account(account_id, clean_df)
        dur_shap = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        shap_meta = {
            "stage": "SHAP_EXPLANATION",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_shap,
            "input_count": 8,
            "output_count": len(explanation.top_risk_drivers),
            "error": None,
            "top_drivers": explanation.top_risk_drivers,
        }
        trace.append(shap_meta)
        _notify("SHAP_EXPLANATION", "COMPLETED", shap_meta)

        # Collect all corroborated evidence items
        all_evidence: list[EvidenceItem] = (
            temp_evidence.evidence_items
            + behav_evidence.evidence_items
            + graph_evidence.evidence_items
        )

        # Step 7: Rule-Based Formal Verification
        _check_cancel()
        _notify("FORMAL_VERIFICATION", "RUNNING", {"label": "Executing Formal Decision Verification...", "input_count": len(all_evidence)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        verif_report = self.verifier.verify_evidence(account_id, all_evidence, clean_df)
        dur_verif = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        verif_meta = {
            "stage": "FORMAL_VERIFICATION",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_verif,
            "input_count": len(all_evidence),
            "output_count": verif_report.passed_checks,
            "error": None,
            "verification_status": verif_report.overall_status,
        }
        trace.append(verif_meta)
        _notify("FORMAL_VERIFICATION", "COMPLETED", verif_meta)

        # Step 8: Threat Memory Pattern Retrieval
        _check_cancel()
        _notify("THREAT_MEMORY", "RUNNING", {"label": "Searching Historical Threat Memory Patterns...", "input_count": 1})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
        query_sig = [behav_evidence.extracted_features.get(k, 0.0) for k in behav_evidence.extracted_features]
        t_matches = self.threat_memory.search_similar_patterns(query_sig, top_k=2)
        hist_scores = [
            m["historical_risk"] * m["similarity_score"]
            for m in t_matches
            if m.get("confirmed_status") == "TRUE_POSITIVE"
        ]
        hist_score = max(hist_scores, default=0.0)
        dur_tm = round((time.monotonic() - t0) * 1000, 2)
        t_end_iso = datetime.now(timezone.utc).isoformat()
        tm_meta = {
            "stage": "THREAT_MEMORY",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_tm,
            "input_count": 1,
            "output_count": len(t_matches),
            "error": None,
            "matches_found": len(t_matches),
        }
        trace.append(tm_meta)
        _notify("THREAT_MEMORY", "COMPLETED", tm_meta)

        # Step 9: Multi-Layer Evidence Fusion
        _check_cancel()
        _notify("EVIDENCE_FUSION", "RUNNING", {"label": "Executing Multi-Layer Evidence Fusion...", "input_count": len(all_evidence)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
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
        t_end_iso = datetime.now(timezone.utc).isoformat()
        fusion_meta = {
            "stage": "EVIDENCE_FUSION",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_fusion,
            "input_count": len(all_evidence),
            "output_count": 1,
            "error": None,
            "composite_score": fused_profile.composite_score,
            "risk_level": fused_profile.risk_level,
        }
        trace.append(fusion_meta)
        _notify("EVIDENCE_FUSION", "COMPLETED", fusion_meta)

        # Step 10: Local Ollama Investigation Narrative
        _check_cancel()
        _notify("OLLAMA_INVESTIGATION", "RUNNING", {"label": "Generating Local Investigation Intelligence (Ollama / Llama 3)...", "input_count": len(all_evidence)})
        t0 = time.monotonic()
        t_start_iso = datetime.now(timezone.utc).isoformat()
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
        t_end_iso = datetime.now(timezone.utc).isoformat()
        llm_meta = {
            "stage": "OLLAMA_INVESTIGATION",
            "status": "COMPLETED",
            "started_at": t_start_iso,
            "completed_at": t_end_iso,
            "duration_ms": dur_llm,
            "input_count": len(all_evidence),
            "output_count": 1,
            "error": None,
            "provider": brief["provider"],
        }
        trace.append(llm_meta)
        _notify("OLLAMA_INVESTIGATION", "COMPLETED", llm_meta)

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
