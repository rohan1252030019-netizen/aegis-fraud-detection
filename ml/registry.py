"""
AEGIS - Lightweight Model Registry
Tracks versions, weights, metrics, and deployment status for:
- Temporal Transformer
- Behavioral Isolation Forest
- Graph Topology Rules
- Fusion Weights
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
from typing import Any


@dataclass
class RegisteredModel:
    model_name: str
    version: str
    model_type: str
    status: str       # "DEPLOYED", "STAGING", "ARCHIVED"
    metrics: dict[str, Any]
    feature_schema: list[str]
    training_dataset_hash: str
    deployed_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelRegistry:
    def __init__(self, registry_file: str = "ml/models/model_registry.json"):
        self.registry_file = registry_file
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        self.models: dict[str, RegisteredModel] = {}
        self._load()
        if not self.models:
            self._init_defaults()

    def _load(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    raw = json.load(f)
                    self.models = {k: RegisteredModel(**v) for k, v in raw.items()}
            except Exception:
                self.models = {}

    def _save(self):
        with open(self.registry_file, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.models.items()}, f, indent=2)

    def _init_defaults(self):
        now = datetime.now(timezone.utc).isoformat()
        self.models = {
            "temporal_transformer": RegisteredModel(
                model_name="Temporal Sequence Transformer",
                version="1.0.0",
                model_type="PyTorch-TransformerEncoder",
                status="DEPLOYED",
                metrics={"loss": 0.042, "accuracy": 0.94},
                feature_schema=["norm_amount", "log_amount", "time_gap_hrs", "is_outgoing", "is_weekend", "hour_norm"],
                training_dataset_hash="synthetic_seed_v1",
                deployed_at=now,
            ),
            "behavioral_isolation_forest": RegisteredModel(
                model_name="Unsupervised Behavioral Anomaly Detector",
                version="1.0.0",
                model_type="scikit-learn IsolationForest",
                status="DEPLOYED",
                metrics={"contamination": 0.15, "estimators": 100},
                feature_schema=["tx_count", "avg_amount", "amount_std", "send_recv_ratio", "unique_counterparties", "tx_velocity_per_day", "max_amount_ratio", "weekend_tx_ratio"],
                training_dataset_hash="synthetic_seed_v1",
                deployed_at=now,
            ),
            "graph_topology_correlator": RegisteredModel(
                model_name="Graph Topology Correlator",
                version="1.0.0",
                model_type="NetworkX Directional Topology",
                status="DEPLOYED",
                metrics={"patterns_supported": ["FAN_IN", "FAN_OUT", "RAPID_PASSTHROUGH", "CYCLES", "SHARED_DEVICE"]},
                feature_schema=["in_degree", "out_degree", "cycle_length", "device_id"],
                training_dataset_hash="rule_baseline_v1",
                deployed_at=now,
            ),
            "evidence_fusion_engine": RegisteredModel(
                model_name="Multi-Layer Biomimetic Fusion",
                version="1.0.0",
                model_type="Weighted Evidential Fusion",
                status="DEPLOYED",
                metrics={"weights": {"temporal": 0.25, "behavioral": 0.25, "graph": 0.30, "threat_memory": 0.10, "contextual": 0.10}},
                feature_schema=["T", "A", "G", "H", "C"],
                training_dataset_hash="fusion_spec_ff180",
                deployed_at=now,
            ),
        }
        self._save()

    def get_all(self) -> list[dict[str, Any]]:
        return [m.to_dict() for m in self.models.values()]
