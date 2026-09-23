"""
AEGIS - Comprehensive Architecture & Pipeline Test Suite
Tests every core component of the biomimetic multi-layer detection architecture:
1. Data Quality Preprocessing
2. Temporal Analysis & Neural Sequence Transformer
3. Behavioral Anomaly Engine (Isolation Forest)
4. Graph Correlation Engine (NetworkX)
5. Multi-Layer Evidence Fusion
6. SHAP Explainability
7. Formal Verification & Anti-Hallucination Guardrails
8. Threat Memory Vector Store
9. End-to-End Orchestrator Pipeline
"""
import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta

from ml.preprocessing.pipeline import DataQualityPipeline
from ml.temporal.engine import TemporalAnalysisEngine
from ml.temporal.transformer import TemporalTransformerEngine
from ml.behavioral.detector import BehavioralAnomalyDetector
from ml.graph.engine import FinancialGraphEngine
from ml.fusion.engine import EvidenceFusionEngine
from ml.fusion.evidence import EvidenceItem, EvidenceSourceType, EvidenceSeverity
from ml.explainability.engine import SHAPExplainabilityEngine
from ml.verification.engine import FormalVerificationEngine
from ml.threat_memory.store import ThreatMemoryStore, ThreatPatternRecord
from apps.api.app.services.pipeline_orchestrator import AegisPipelineOrchestrator


def test_data_quality_preprocessing():
    pipeline = DataQualityPipeline()
    raw_data = [
        {"transaction_id": "TX_001", "sender_account_id": "ACC_1", "receiver_account_id": "ACC_2", "amount": 100.0, "timestamp": "2026-03-20T10:00:00Z"},
        {"transaction_id": "TX_001", "sender_account_id": "ACC_1", "receiver_account_id": "ACC_2", "amount": 100.0, "timestamp": "2026-03-20T10:00:00Z"}, # Duplicate
        {"transaction_id": "TX_002", "sender_account_id": "ACC_1", "receiver_account_id": "ACC_3", "amount": -50.0, "timestamp": "2026-03-20T10:05:00Z"}, # Invalid negative
        {"transaction_id": "TX_003", "sender_account_id": "", "receiver_account_id": "ACC_3", "amount": 250.0, "timestamp": "2026-03-20T10:10:00Z"}, # Missing sender
        {"transaction_id": "TX_004", "sender_account_id": "ACC_2", "receiver_account_id": "ACC_4", "amount": 500.0, "timestamp": "2026-03-20T10:15:00Z"},
    ]
    cleaned_df, report = pipeline.process(raw_data)
    
    assert report.records_received == 5
    assert report.duplicates_detected == 1
    assert report.invalid_amounts == 1
    assert len(cleaned_df) == 2  # Only TX_001 (deduped) and TX_004 are fully valid
    assert 0.0 <= report.quality_score <= 100.0


def test_temporal_and_transformer_engine():
    temporal_engine = TemporalAnalysisEngine()
    now = datetime.now(timezone.utc)
    
    # Rapid pass-through scenario: money in, money out immediately with minimal retention
    txs = [
        {"transaction_id": "T1", "sender_account_id": "SRC_1", "receiver_account_id": "MULE_1", "amount": 10000.0, "timestamp": (now - timedelta(minutes=5)).isoformat(), "device_id": "D1"},
        {"transaction_id": "T2", "sender_account_id": "MULE_1", "receiver_account_id": "DST_1", "amount": 9950.0, "timestamp": now.isoformat(), "device_id": "D1"},
    ]
    df = pd.DataFrame(txs)
    evidence = temporal_engine.analyze_account("MULE_1", df)
    
    assert evidence.account_id == "MULE_1"
    assert evidence.temporal_score >= 35.0
    assert any(p["pattern"] == "RAPID_PASSTHROUGH" for p in evidence.detected_patterns)
    assert 0.0 <= evidence.transformer_score <= 100.0


def test_behavioral_detector():
    detector = BehavioralAnomalyDetector()
    now = datetime.now(timezone.utc)
    
    # 10 transactions in quick succession
    txs = [
        {"transaction_id": f"BTX_{i}", "sender_account_id": "MULE_B", "receiver_account_id": f"DST_{i}", "amount": float(500 * (i + 1)), "timestamp": (now - timedelta(seconds=i * 20)).isoformat()}
        for i in range(10)
    ]
    df = pd.DataFrame(txs)
    evidence = detector.assess_account("MULE_B", df)
    
    assert evidence.account_id == "MULE_B"
    assert evidence.extracted_features["tx_count"] == 10.0
    assert 0.0 <= evidence.behavioral_score <= 100.0
    assert evidence.extracted_features["unique_counterparties"] == 10.0


def test_graph_correlation_engine():
    graph_engine = FinancialGraphEngine()
    
    # Multi-hop conduit and Fan-In pattern (4 feeder accounts into HUB_1)
    txs = [
        {"transaction_id": "G1", "sender_account_id": "FEEDER_1", "receiver_account_id": "HUB_1", "amount": 2000.0, "timestamp": "2026-03-20T12:00:00Z", "device_id": "DEV_A"},
        {"transaction_id": "G2", "sender_account_id": "FEEDER_2", "receiver_account_id": "HUB_1", "amount": 2000.0, "timestamp": "2026-03-20T12:01:00Z", "device_id": "DEV_B"},
        {"transaction_id": "G3", "sender_account_id": "FEEDER_3", "receiver_account_id": "HUB_1", "amount": 2000.0, "timestamp": "2026-03-20T12:02:00Z", "device_id": "DEV_C"},
        {"transaction_id": "G4", "sender_account_id": "FEEDER_4", "receiver_account_id": "HUB_1", "amount": 2000.0, "timestamp": "2026-03-20T12:03:00Z", "device_id": "DEV_D"},
        {"transaction_id": "G5", "sender_account_id": "HUB_1", "receiver_account_id": "EXIT_1", "amount": 7900.0, "timestamp": "2026-03-20T12:05:00Z", "device_id": "DEV_A"},
    ]
    df = pd.DataFrame(txs)
    graph_evidence = graph_engine.analyze_account("HUB_1", df)
    
    assert graph_evidence.in_degree == 4
    assert graph_evidence.out_degree == 1
    assert graph_evidence.network_risk_score > 0.0
    assert any(p["pattern"] == "FAN_IN" for p in graph_evidence.detected_patterns)


def test_evidence_fusion_mathematics():
    fusion_engine = EvidenceFusionEngine()
    
    profile = fusion_engine.fuse(
        account_id="ACC_FUSION_TEST",
        temporal_score=80.0,
        behavioral_score=70.0,
        graph_score=90.0,
        historical_score=40.0,
        contextual_score=85.0,
    )
    
    assert profile.risk_level in ["CRITICAL", "HIGH"]
    assert profile.composite_score > 70.0
    assert 0.0 <= profile.confidence <= 1.0
    assert len(profile.layer_scores) == 5
    
    # Assert sum of weights = 1.0
    weight_sum = (
        fusion_engine.w_t + fusion_engine.w_a + fusion_engine.w_g +
        fusion_engine.w_h + fusion_engine.w_c
    )
    assert abs(weight_sum - 1.0) < 1e-4


def test_shap_explainability():
    detector = BehavioralAnomalyDetector()
    shap_engine = SHAPExplainabilityEngine(detector)
    
    sample_txs = [
        {"transaction_id": f"STX_{i}", "sender_account_id": "ACC_SHAP", "receiver_account_id": f"DST_{i}", "amount": float(1000 + i * 200), "timestamp": "2026-03-20T10:00:00Z"}
        for i in range(12)
    ]
    df = pd.DataFrame(sample_txs)
    
    explanation = shap_engine.explain_account("ACC_SHAP", df)
    assert len(explanation.contributions) == 8
    assert len(explanation.top_risk_drivers) >= 1
    assert len(explanation.narrative) > 20


def test_formal_verification_and_hallucination_detection():
    verifier = FormalVerificationEngine()
    
    known_txs = [
        {"transaction_id": "TX_REAL_1", "sender_account_id": "ACC_A", "receiver_account_id": "ACC_B", "amount": 5000.0, "timestamp": "2026-03-20T10:00:00Z"},
        {"transaction_id": "TX_REAL_2", "sender_account_id": "ACC_B", "receiver_account_id": "ACC_C", "amount": 4900.0, "timestamp": "2026-03-20T10:05:00Z"},
    ]
    df = pd.DataFrame(known_txs)
    valid_accs = {"ACC_A", "ACC_B", "ACC_C"}
    
    # 1. Grounded honest text matching real transactions
    honest_text = "Account ACC_B received funds in TX_REAL_1 and disbursed funds to ACC_C via TX_REAL_2."
    v_report_honest = verifier.verify_llm_claims(honest_text, df, valid_accs)
    assert v_report_honest["is_grounded"] is True
    assert len(v_report_honest["unverified_transactions"]) == 0
    
    # 2. Adversarial hallucinated text claiming non-existent TX_FAKE_999 and non-existent ACC_99999
    fake_text = "Account ACC_B engaged in laundering via TX_FAKE_999 transfer of ₹9999999 to foreign account ACC_99999."
    v_report_fake = verifier.verify_llm_claims(fake_text, df, valid_accs)
    assert v_report_fake["is_grounded"] is False
    assert "TX_FAKE_999" in v_report_fake["unverified_transactions"]
    assert "ACC_99999" in v_report_fake["unverified_accounts"]


def test_threat_memory_vector_store():
    store = ThreatMemoryStore()
    
    # Create pattern
    record = ThreatPatternRecord(
        pattern_id="TEST_CYCLIC_MULE",
        pattern_type="CYCLIC_TRANSFER",
        account_id="ACC_CYCLIC_01",
        risk_score=92.0,
        confirmed_status="TRUE_POSITIVE",
        feature_signature=[25.0, 5500.0, 1200.0, 0.98, 8.0, 14.5, 3.2, 0.45],
        topology_description="Cyclic flow between 3 accounts",
        analyst_notes="Cycle detected",
    )
    store.records.append(record)
    
    # Query with similar embedding
    query_vec = [24.0, 5400.0, 1150.0, 0.97, 8.0, 14.0, 3.1, 0.44]
    matches = store.search_similar_patterns(query_vec, top_k=2, threshold=0.70)
    
    assert len(matches) > 0
    assert any(m["pattern_id"] == "TEST_CYCLIC_MULE" for m in matches)
    assert matches[0]["similarity_score"] > 0.95


def test_end_to_end_orchestrator():
    orchestrator = AegisPipelineOrchestrator()
    now = datetime.now(timezone.utc)
    
    sample_txs = [
        {"transaction_id": "E2E_1", "sender_account_id": "FEED_A", "receiver_account_id": "E2E_ACC", "amount": 10000.0, "timestamp": (now - timedelta(minutes=10)).isoformat(), "device_id": "DEV_1"},
        {"transaction_id": "E2E_2", "sender_account_id": "FEED_B", "receiver_account_id": "E2E_ACC", "amount": 15000.0, "timestamp": (now - timedelta(minutes=8)).isoformat(), "device_id": "DEV_2"},
        {"transaction_id": "E2E_3", "sender_account_id": "E2E_ACC", "receiver_account_id": "EXIT_Z", "amount": 24800.0, "timestamp": now.isoformat(), "device_id": "DEV_1"},
    ]
    df = pd.DataFrame(sample_txs)
    
    result = orchestrator.run_account_investigation("E2E_ACC", df)
    
    assert result["account_id"] == "E2E_ACC"
    assert "risk_profile" in result
    assert "temporal_evidence" in result
    assert "behavioral_evidence" in result
    assert "graph_evidence" in result
    assert "explainability" in result
    assert "formal_verification" in result
    assert "threat_memory_matches" in result
    assert "investigation_brief" in result
    assert len(result["pipeline_trace"]) == 9
    assert result["total_execution_ms"] > 0
