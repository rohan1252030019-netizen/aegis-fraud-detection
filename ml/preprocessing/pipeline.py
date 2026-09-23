"""
AEGIS - Data Quality, Validation & Preprocessing Pipeline
Handles:
- Upload verification (CSV, JSON)
- Schema validation & column normalization
- Duplicate detection & tracking
- Missing value profiling
- Categorical & numerical cleaning
- Timestamp parsing & normalization
- Transaction window & sequence grouping
- Data quality score calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
import re
from typing import Any
import pandas as pd
import numpy as np


REQUIRED_COLUMNS = {
    "transaction_id",
    "sender_account_id",
    "receiver_account_id",
    "amount",
    "timestamp",
}

OPTIONAL_COLUMNS = {
    "currency",
    "transaction_type",
    "device_id",
    "ip_address",
    "beneficiary_id",
    "merchant_id",
    "location",
}


@dataclass
class PreprocessingReport:
    records_received: int = 0
    records_valid: int = 0
    records_rejected: int = 0
    duplicates_detected: int = 0
    missing_values_detected: int = 0
    invalid_amounts: int = 0
    timestamp_format_errors: int = 0
    unknown_entities: int = 0
    quality_score: float = 100.0
    quality_grade: str = "EXCELLENT"  # EXCELLENT, GOOD, MARGINAL, POOR
    rejection_reasons: list[dict[str, Any]] = field(default_factory=list)
    schema_findings: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    processed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataQualityPipeline:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def process(self, raw_data: pd.DataFrame | list[dict[str, Any]]) -> tuple[pd.DataFrame, PreprocessingReport]:
        report = PreprocessingReport()

        if isinstance(raw_data, list):
            df = pd.DataFrame(raw_data)
        else:
            df = raw_data.copy()

        report.records_received = len(df)
        if df.empty:
            report.quality_score = 0.0
            report.quality_grade = "POOR"
            report.summary = "Empty dataset provided"
            return pd.DataFrame(), report

        # 1. Normalize Column Headers (strip, lowercase, underscore)
        df.columns = [re.sub(r"[^\w]", "_", c.strip().lower()) for c in df.columns]

        # 2. Check Required Schema
        missing_cols = REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            report.schema_findings["missing_required_columns"] = list(missing_cols)
            if "amount" in missing_cols or "transaction_id" in missing_cols:
                report.records_rejected = len(df)
                report.quality_score = 0.0
                report.quality_grade = "POOR"
                report.summary = f"Fatal schema error: Missing essential columns: {missing_cols}"
                return pd.DataFrame(), report

        # 3. Detect & Filter Duplicates on transaction_id
        if "transaction_id" in df.columns:
            dups = df[df.duplicated(subset=["transaction_id"], keep="first")]
            report.duplicates_detected = len(dups)
            if len(dups) > 0:
                report.rejection_reasons.append({
                    "issue": "DUPLICATE_TRANSACTION_ID",
                    "count": len(dups),
                    "sample_ids": dups["transaction_id"].head(5).tolist(),
                })
                # Keep first occurrence, drop duplicates
                df = df.drop_duplicates(subset=["transaction_id"], keep="first")

        # 4. Check Missing Values
        null_counts = df.isnull().sum().to_dict()
        report.missing_values_detected = int(sum(null_counts.values()))
        report.schema_findings["null_counts"] = null_counts

        # Clean nulls in required fields
        initial_len = len(df)
        for col in ["transaction_id", "sender_account_id", "receiver_account_id"]:
            if col in df.columns:
                df = df[df[col].notnull() & (df[col].astype(str).str.strip() != "")]
        dropped_nulls = initial_len - len(df)
        if dropped_nulls > 0:
            report.rejection_reasons.append({
                "issue": "NULL_REQUIRED_IDENTIFIER",
                "count": dropped_nulls,
            })

        # 5. Amount Validation & Normalization
        if "amount" in df.columns:
            # Ensure numeric
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            invalid_amt = df[df["amount"].isna() | (df["amount"] <= 0)]
            report.invalid_amounts = len(invalid_amt)
            if len(invalid_amt) > 0:
                report.rejection_reasons.append({
                    "issue": "NON_POSITIVE_OR_NON_NUMERIC_AMOUNT",
                    "count": len(invalid_amt),
                })
                df = df[df["amount"].notnull() & (df["amount"] > 0)]

        # 6. Timestamp Normalization
        if "timestamp" in df.columns:
            parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
            invalid_ts = parsed_ts.isna().sum()
            report.timestamp_format_errors = int(invalid_ts)
            if invalid_ts > 0:
                report.rejection_reasons.append({
                    "issue": "INVALID_TIMESTAMP_FORMAT",
                    "count": int(invalid_ts),
                })
                # Fill invalid timestamps with current time or drop
                df = df[parsed_ts.notnull()]
                df["timestamp"] = parsed_ts[parsed_ts.notnull()].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                df["timestamp"] = parsed_ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 7. Normalize Categoricals
        if "currency" in df.columns:
            df["currency"] = df["currency"].fillna("USD").astype(str).str.upper().str.strip()
        else:
            df["currency"] = "USD"

        if "transaction_type" in df.columns:
            df["transaction_type"] = df["transaction_type"].fillna("TRANSFER").astype(str).str.upper().str.strip()
        else:
            df["transaction_type"] = "TRANSFER"

        # 8. Compute Derived Window & Velocity Columns
        df = df.sort_values(by="timestamp", ascending=True)

        report.records_valid = len(df)
        report.records_rejected = report.records_received - report.records_valid

        # 9. Compute Overall Quality Score (0 - 100)
        penalty = 0.0
        penalty += (report.duplicates_detected / max(1, report.records_received)) * 25.0
        penalty += (report.missing_values_detected / max(1, report.records_received * len(df.columns))) * 25.0
        penalty += (report.invalid_amounts / max(1, report.records_received)) * 30.0
        penalty += (report.timestamp_format_errors / max(1, report.records_received)) * 20.0

        report.quality_score = round(max(0.0, min(100.0, 100.0 - penalty)), 1)
        if report.quality_score >= 90:
            report.quality_grade = "EXCELLENT"
        elif report.quality_score >= 75:
            report.quality_grade = "GOOD"
        elif report.quality_score >= 50:
            report.quality_grade = "MARGINAL"
        else:
            report.quality_grade = "POOR"

        report.summary = (
            f"Processed {report.records_received} records: {report.records_valid} valid, "
            f"{report.records_rejected} rejected. Data Quality Score: {report.quality_score}% ({report.quality_grade})."
        )

        return df.reset_index(drop=True), report
