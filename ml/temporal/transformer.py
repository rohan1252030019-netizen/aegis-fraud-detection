"""
AEGIS - Transformer-Based Temporal Sequence Model (PyTorch)
Requirement: VIT FF No. 180 Section 2.2 / Patent Cl. 1
Architecture:
- Feature Embedding & Projection
- Sinusoidal Temporal / Positional Encoding
- Multi-Head Transformer Encoder
- Sequence Aggregation & Anomaly Classification Head
- Lightweight, CPU/GPU local execution
"""
from __future__ import annotations
import math
import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional
import numpy as np
import pandas as pd
import torch
import torch.nn as nn


class TemporalPositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch_size, seq_len, d_model]
        return x + self.pe[:, :x.size(1)]


class TransformerSequenceModel(nn.Module):
    def __init__(
        self,
        input_dim: int = 6,      # [norm_amount, log_amount, time_gap_sec, is_outgoing, is_weekend, hour_norm]
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = TemporalPositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # x: [batch_size, seq_len, input_dim]
        h = self.input_proj(x)
        h = self.pos_encoder(h)
        encoded = self.transformer_encoder(h, src_key_padding_mask=mask)
        # Sequence pooling: Mean representation over non-padded elements
        if mask is not None:
            mask_expanded = (~mask).unsqueeze(-1).float()
            pooled = (encoded * mask_expanded).sum(dim=1) / mask_expanded.sum(dim=1).clamp(min=1.0)
        else:
            pooled = encoded.mean(dim=1)
        anomaly_prob = self.classifier(pooled)
        return anomaly_prob.squeeze(-1)


class TemporalTransformerEngine:
    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model_path = os.path.join(model_dir, "temporal_transformer.pt")
        self.meta_path = os.path.join(model_dir, "temporal_transformer_meta.json")
        self.model = TransformerSequenceModel()
        self.model.eval()
        self.version = "1.0.0"
        self._load_or_initialize()

    def _load_or_initialize(self):
        if os.path.exists(self.model_path):
            try:
                state_dict = torch.load(self.model_path, map_location="cpu")
                self.model.load_state_dict(state_dict)
                self.model.eval()
            except Exception:
                pass

    def extract_sequence_features(self, account_id: str, df: pd.DataFrame, max_seq_len: int = 50) -> np.ndarray:
        """
        Extract numerical sequence tensor for an account's recent transactions.
        Features per tx:
        0: Normalized amount (amount / 10000)
        1: Log amount: log1p(amount) / 10.0
        2: Delta time in hours since previous tx (normalized)
        3: Is outgoing transaction (1.0 if sender else 0.0)
        4: Is weekend (1.0 or 0.0)
        5: Normalized hour of day (hour / 24.0)
        """
        if df.empty:
            return np.zeros((1, max_seq_len, 6), dtype=np.float32)

        acc_txs = df[
            (df["sender_account_id"] == account_id) |
            (df["receiver_account_id"] == account_id)
        ].copy()

        if acc_txs.empty:
            return np.zeros((1, max_seq_len, 6), dtype=np.float32)

        acc_txs["ts"] = pd.to_datetime(acc_txs["timestamp"])
        acc_txs = acc_txs.sort_values(by="ts")

        # Time delta
        acc_txs["time_gap_hrs"] = acc_txs["ts"].diff().dt.total_seconds().fillna(0) / 3600.0

        features = []
        for _, row in acc_txs.tail(max_seq_len).iterrows():
            amt = float(row.get("amount", 0.0))
            is_outgoing = 1.0 if str(row.get("sender_account_id")) == account_id else 0.0
            ts = row["ts"]
            feat = [
                min(1.0, amt / 10000.0),
                min(1.0, np.log1p(amt) / 10.0),
                min(1.0, float(row.get("time_gap_hrs", 0.0)) / 24.0),
                is_outgoing,
                1.0 if ts.weekday() >= 5 else 0.0,
                float(ts.hour) / 24.0,
            ]
            features.append(feat)

        # Pad to max_seq_len
        seq_len = len(features)
        if seq_len < max_seq_len:
            pad = [[0.0] * 6 for _ in range(max_seq_len - seq_len)]
            features = pad + features

        return np.array([features], dtype=np.float32)

    def predict_account(self, account_id: str, df: pd.DataFrame) -> dict[str, Any]:
        """Runs temporal sequence inference via Transformer."""
        feats = self.extract_sequence_features(account_id, df)
        tensor_x = torch.from_numpy(feats)
        with torch.no_grad():
            score_tensor = self.model(tensor_x)
            prob = float(score_tensor.item())

        score_100 = round(prob * 100.0, 1)
        return {
            "account_id": account_id,
            "temporal_transformer_score": score_100,
            "model_version": self.version,
            "model_type": "TransformerSequenceModel",
            "sequence_length_evaluated": min(50, len(df)),
            "is_anomalous": score_100 >= 60.0,
        }

    def train_baseline(self, df: pd.DataFrame, epochs: int = 5) -> dict[str, Any]:
        """Lightweight training loop on observed sequences."""
        accounts = list(set(df["sender_account_id"]).union(set(df["receiver_account_id"])))
        if len(accounts) < 4:
            return {"status": "SKIPPED", "reason": "Insufficient accounts to train"}

        X_list, y_list = [], []
        for acc in accounts:
            feats = self.extract_sequence_features(acc, df)
            # Label heuristic: high volume passthrough accounts have label 1
            acc_txs = df[(df["sender_account_id"] == acc) | (df["receiver_account_id"] == acc)]
            label = 1.0 if len(acc_txs) >= 15 else 0.0
            X_list.append(feats[0])
            y_list.append(label)

        X = torch.tensor(np.array(X_list), dtype=torch.float32)
        y = torch.tensor(y_list, dtype=torch.float32)

        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.BCELoss()

        total_loss = 0.0
        for _ in range(epochs):
            optimizer.zero_grad()
            preds = self.model(X)
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()
            total_loss = float(loss.item())

        self.model.eval()
        torch.save(self.model.state_dict(), self.model_path)

        meta = {
            "version": self.version,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "samples_trained": len(X_list),
            "final_loss": round(total_loss, 4),
            "hash": hashlib.sha256(X.numpy().tobytes()).hexdigest()[:16],
        }
        with open(self.meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        return meta
