"""
AEGIS - Temporal Transaction Analysis Engine
Combines Rule-Based Velocity Pattern Matching + Transformer Sequence Anomaly Modeling.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from ml.fusion.evidence import EvidenceItem, EvidenceSourceType, EvidenceSeverity
from ml.temporal.transformer import TemporalTransformerEngine


@dataclass
class TemporalEvidence:
    account_id: str
    temporal_score: float = 0.0
    transformer_score: float = 0.0
    detected_patterns: list[dict] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    risk_level: str = "LOW"
    confidence: float = 0.90


class TemporalAnalysisEngine:
    def __init__(self):
        self.transformer_engine = TemporalTransformerEngine()

    def analyze_rules(self, account_id: str, df: pd.DataFrame) -> tuple[float, list[dict], list[EvidenceItem]]:
        if df.empty or ("sender_account_id" not in df.columns and "receiver_account_id" not in df.columns):
            return 0.0, [], []

        acc_txs = df[(df["sender_account_id"] == account_id) | (df["receiver_account_id"] == account_id)].copy()
        if acc_txs.empty:
            return 0.0, [], []

        acc_txs["ts"] = pd.to_datetime(acc_txs["timestamp"])
        acc_txs = acc_txs.sort_values(by="ts")

        detected = []
        evidence_list: list[EvidenceItem] = []
        score = 0.0

        # Pattern 1: Burst Activity (High volume in short time)
        if len(acc_txs) >= 10:
            duration_hrs = max(0.1, (acc_txs["ts"].max() - acc_txs["ts"].min()).total_seconds() / 3600.0)
            velocity = len(acc_txs) / duration_hrs
            if velocity >= 2.0 or len(acc_txs) >= 15:
                detected.append({
                    "pattern": "BURST_ACTIVITY",
                    "description": f"High volume transaction burst detected ({len(acc_txs)} transactions across {round(duration_hrs, 1)} hrs)",
                    "severity": 0.7,
                })
                score += 35.0
                evidence_list.append(EvidenceItem(
                    source_type=EvidenceSourceType.TEMPORAL_RULE,
                    source_record=str(acc_txs.iloc[-1].get("transaction_id", "")),
                    entity_id=account_id,
                    feature="transaction_velocity_burst",
                    observed_value=round(velocity, 2),
                    expected_value="< 1.0 tx/hr",
                    severity=EvidenceSeverity.HIGH,
                    score_contribution=35.0,
                    rule_or_model="Rule_TemporalBurst_v1.0",
                    description=f"Transaction velocity surged to {round(velocity, 2)} tx/hr.",
                ))

        # Pattern 2: Rapid Passthrough / Immediate cashout (Mule hallmark)
        sends = acc_txs[acc_txs["sender_account_id"] == account_id]
        receives = acc_txs[acc_txs["receiver_account_id"] == account_id]

        if not sends.empty and not receives.empty:
            total_sent = float(sends["amount"].sum())
            total_recv = float(receives["amount"].sum())
            ratio = total_sent / (total_recv + 1e-5)

            if 0.85 <= ratio <= 1.15:
                detected.append({
                    "pattern": "RAPID_PASSTHROUGH",
                    "description": f"Funds received (${round(total_recv, 2)}) dispersed in near-equal amount (${round(total_sent, 2)})",
                    "severity": 0.85,
                })
                score += 45.0
                evidence_list.append(EvidenceItem(
                    source_type=EvidenceSourceType.TEMPORAL_RULE,
                    source_record=str(sends.iloc[0].get("transaction_id", "")),
                    entity_id=account_id,
                    feature="passthrough_disbursement_ratio",
                    observed_value=round(ratio, 3),
                    expected_value="< 0.70 or > 1.30",
                    severity=EvidenceSeverity.CRITICAL,
                    score_contribution=45.0,
                    rule_or_model="Rule_MulePassThrough_v1.0",
                    description="Classic money mule signature: Funds received and rapidly flushed out in near-exact quantity.",
                ))

        # Pattern 3: Repeated Small Structuring Transactions
        small_txs = acc_txs[(acc_txs["amount"] >= 2000) & (acc_txs["amount"] <= 9999)]
        if len(small_txs) >= 3:
            detected.append({
                "pattern": "STRUCTURING_REPEATED_AMOUNTS",
                "description": f"{len(small_txs)} transactions just below threshold amount detected",
                "severity": 0.6,
            })
            score += 20.0
            evidence_list.append(EvidenceItem(
                source_type=EvidenceSourceType.TEMPORAL_RULE,
                source_record=str(small_txs.iloc[0].get("transaction_id", "")),
                entity_id=account_id,
                feature="structuring_sub_threshold",
                observed_value=len(small_txs),
                expected_value="< 2 structured transfers",
                severity=EvidenceSeverity.HIGH,
                score_contribution=20.0,
                rule_or_model="Rule_StructuringPattern_v1.0",
                description=f"Detected {len(small_txs)} clustered payments structured beneath reporting limits.",
            ))

        return score, detected, evidence_list

    def blend_results(
        self,
        account_id: str,
        rule_score: float,
        detected_patterns: list[dict],
        evidence_list: list[EvidenceItem],
        t_score: float,
    ) -> TemporalEvidence:
        ev_items = list(evidence_list)
        if t_score >= 50.0:
            ev_items.append(EvidenceItem(
                source_type=EvidenceSourceType.TEMPORAL_TRANSFORMER,
                source_record=account_id,
                entity_id=account_id,
                feature="transformer_sequence_anomaly",
                observed_value=t_score,
                expected_value="< 40.0",
                severity=EvidenceSeverity.HIGH if t_score >= 75.0 else EvidenceSeverity.MEDIUM,
                score_contribution=round(t_score * 0.3, 1),
                rule_or_model="PyTorch_TransformerSequence_v1.0",
                description=f"Neural sequence encoder flagged temporal flow anomaly score of {t_score}/100.",
            ))

        if rule_score == 0:
            final_temporal_score = min(20.0, round(t_score * 0.2, 1))
        else:
            final_temporal_score = min(100.0, round((rule_score * 0.65) + (t_score * 0.35), 1))
        risk_level = "CRITICAL" if final_temporal_score >= 80 else "HIGH" if final_temporal_score >= 60 else "MODERATE" if final_temporal_score >= 30 else "LOW"

        return TemporalEvidence(
            account_id=account_id,
            temporal_score=final_temporal_score,
            transformer_score=t_score,
            detected_patterns=detected_patterns,
            evidence_items=ev_items,
            risk_level=risk_level,
            confidence=0.92,
        )

    def analyze_account(self, account_id: str, df: pd.DataFrame) -> TemporalEvidence:
        score, detected, evidence_list = self.analyze_rules(account_id, df)
        trans_result = self.transformer_engine.predict_account(account_id, df)
        t_score = trans_result["temporal_transformer_score"]
        return self.blend_results(account_id, score, detected, evidence_list, t_score)
