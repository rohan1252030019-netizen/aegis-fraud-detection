"""AEGIS - Temporal Transaction Analysis Engine"""
from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass
class TemporalEvidence:
    account_id: str
    temporal_score: float = 0.0
    detected_patterns: list[dict] = field(default_factory=list)
    risk_level: str = "LOW"


class TemporalAnalysisEngine:
    def analyze_account(self, account_id: str, df: pd.DataFrame) -> TemporalEvidence:
        if df.empty or ("sender_account_id" not in df.columns and "receiver_account_id" not in df.columns):
            return TemporalEvidence(account_id=account_id)

        acc_txs = df[(df["sender_account_id"] == account_id) | (df["receiver_account_id"] == account_id)]
        if acc_txs.empty:
            return TemporalEvidence(account_id=account_id)

        detected = []
        score = 0.0

        # Pattern: Burst Activity (High volume in short time)
        if len(acc_txs) >= 10:
            detected.append({
                "pattern": "BURST_ACTIVITY",
                "description": f"High volume transaction burst detected ({len(acc_txs)} transactions)",
                "severity": 0.6,
            })
            score += 35.0

        # Pattern: Rapid Passthrough / Immediate cashout
        sends = acc_txs[acc_txs["sender_account_id"] == account_id]
        receives = acc_txs[acc_txs["receiver_account_id"] == account_id]

        if not sends.empty and not receives.empty:
            ratio = float(sends["amount"].sum() / (receives["amount"].sum() + 1e-5))
            if 0.85 <= ratio <= 1.15:
                detected.append({
                    "pattern": "RAPID_PASSTHROUGH",
                    "description": "Funds received are quickly dispersed in equivalent amounts (Mule signature)",
                    "severity": 0.8,
                })
                score += 45.0

        temporal_score = min(100.0, score)
        risk_level = "HIGH" if temporal_score >= 70 else "MODERATE" if temporal_score >= 30 else "LOW"

        return TemporalEvidence(
            account_id=account_id,
            temporal_score=temporal_score,
            detected_patterns=detected,
            risk_level=risk_level,
        )
