"""
AEGIS - Unsupervised Behavioral Anomaly Detection Engine
Requirement: VIT FF No. 180 Section 2.1 / Patent Cl. 2
Architecture:
- Multi-dimensional behavioral feature extraction per account
- Unsupervised Isolation Forest model (scikit-learn)
- Independent behavioral anomaly scoring
- Structured behavioral evidence emission
"""
from __future__ import annotations
from dataclasses import dataclass, field
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from ml.fusion.evidence import EvidenceItem, EvidenceSourceType, EvidenceSeverity


BEHAVIORAL_FEATURES = [
    "tx_count",
    "avg_amount",
    "amount_std",
    "send_recv_ratio",
    "unique_counterparties",
    "tx_velocity_per_day",
    "max_amount_ratio",
    "weekend_tx_ratio",
]


@dataclass
class BehavioralEvidence:
    account_id: str
    behavioral_score: float = 0.0
    is_anomalous: bool = False
    raw_anomaly_score: float = 0.0
    extracted_features: dict[str, float] = field(default_factory=dict)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    confidence: float = 0.90
    model_version: str = "1.0.0"


class BehavioralAnomalyDetector:
    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model_path = os.path.join(model_dir, "isolation_forest.joblib")
        self.version = "1.0.0"
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.15,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False
        self._load_if_exists()

    def _load_if_exists(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
            except Exception:
                pass

    def extract_features(self, account_id: str, df: pd.DataFrame) -> dict[str, float]:
        if df.empty:
            return {f: 0.0 for f in BEHAVIORAL_FEATURES}

        sends = df[df["sender_account_id"] == account_id]
        recvs = df[df["receiver_account_id"] == account_id]
        acc_txs = pd.concat([sends, recvs]).drop_duplicates(subset=["transaction_id"])

        if acc_txs.empty:
            return {f: 0.0 for f in BEHAVIORAL_FEATURES}

        amounts = acc_txs["amount"].astype(float)
        total_tx = len(acc_txs)
        total_sent = float(sends["amount"].sum()) if not sends.empty else 0.0
        total_recv = float(recvs["amount"].sum()) if not recvs.empty else 0.0

        counterparties = set(sends["receiver_account_id"]).union(set(recvs["sender_account_id"]))
        counterparties.discard(account_id)

        # Timestamps for velocity
        ts = pd.to_datetime(acc_txs["timestamp"])
        days = max(1.0, (ts.max() - ts.min()).total_seconds() / 86400.0)
        velocity = total_tx / days

        weekend_count = (ts.dt.weekday >= 5).sum()
        max_amt = float(amounts.max()) if not amounts.empty else 0.0
        mean_amt = float(amounts.mean()) if not amounts.empty else 0.0

        return {
            "tx_count": float(total_tx),
            "avg_amount": round(mean_amt, 2),
            "amount_std": round(float(amounts.std()) if total_tx > 1 else 0.0, 2),
            "send_recv_ratio": round(total_sent / (total_recv + 1.0), 3),
            "unique_counterparties": float(len(counterparties)),
            "tx_velocity_per_day": round(velocity, 2),
            "max_amount_ratio": round(max_amt / (mean_amt + 1.0), 2),
            "weekend_tx_ratio": round(weekend_count / max(1, total_tx), 3),
        }

    def train(self, df: pd.DataFrame) -> dict[str, Any]:
        accounts = list(set(df["sender_account_id"]).union(set(df["receiver_account_id"])))
        if len(accounts) < 10:
            return {"status": "SKIPPED", "reason": "Need at least 10 accounts to train Isolation Forest"}

        feat_list = []
        for acc in accounts:
            feat_dict = self.extract_features(acc, df)
            feat_list.append([feat_dict[f] for f in BEHAVIORAL_FEATURES])

        X = np.array(feat_list)
        self.model.fit(X)
        self.is_trained = True
        joblib.dump(self.model, self.model_path)

        return {
            "status": "TRAINED",
            "model": "IsolationForest",
            "samples": len(accounts),
            "features": BEHAVIORAL_FEATURES,
            "version": self.version,
        }

    def assess_account(self, account_id: str, df: pd.DataFrame) -> BehavioralEvidence:
        feat_dict = self.extract_features(account_id, df)
        vector = np.array([[feat_dict[f] for f in BEHAVIORAL_FEATURES]])

        if not self.is_trained:
            # Cold-start heuristic until dataset training runs
            self.train(df)

        raw_score = 0.0
        if self.is_trained:
            # decision_function: lower score = more abnormal
            dec = float(self.model.decision_function(vector)[0])
            # Map decision function (-0.5 to +0.5 typically) to 0 - 100 risk
            norm_anomaly = (0.3 - dec) / 0.6  # > 0 means anomalous
            score_100 = round(max(0.0, min(100.0, norm_anomaly * 100.0)), 1)
            raw_score = dec
        else:
            # Heuristic calculation based on high velocity & extreme balance
            score_100 = 65.0 if feat_dict["tx_count"] > 15 else 20.0

        is_anom = score_100 >= 60.0
        evidence_items = []
        if is_anom:
            evidence_items.append(EvidenceItem(
                source_type=EvidenceSourceType.BEHAVIORAL_ISOLATION_FOREST,
                source_record=account_id,
                entity_id=account_id,
                feature="isolation_forest_anomaly",
                observed_value=score_100,
                expected_value="< 50.0",
                severity=EvidenceSeverity.HIGH if score_100 >= 75.0 else EvidenceSeverity.MEDIUM,
                score_contribution=score_100,
                rule_or_model=f"IsolationForest_{self.version}",
                description=(
                    f"Unsupervised Isolation Forest detected severe behavioral outlier profile "
                    f"with {feat_dict['unique_counterparties']} counterparties and {feat_dict['tx_velocity_per_day']} tx/day."
                ),
            ))

        return BehavioralEvidence(
            account_id=account_id,
            behavioral_score=score_100,
            is_anomalous=is_anom,
            raw_anomaly_score=raw_score,
            extracted_features=feat_dict,
            evidence_items=evidence_items,
            confidence=0.91,
            model_version=self.version,
        )
