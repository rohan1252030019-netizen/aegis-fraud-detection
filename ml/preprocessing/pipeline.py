"""
AEGIS - Data Quality, Validation & Preprocessing Pipeline
Handles:
- Upload verification (CSV, JSON)
- Schema validation & semantic column adapter
- Duplicate detection & tracking
- Missing value profiling
- Categorical & numerical cleaning
- Timestamp parsing & ISO-8601 normalization
- Transaction window & sequence grouping
- Data quality score calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
import re
from typing import Any, Optional
import pandas as pd
import numpy as np

from ml.preprocessing.schema_adapter import (
    DatasetSchemaAdapter,
    CANONICAL_REQUIRED_COLUMNS,
    CANONICAL_OPTIONAL_COLUMNS,
    MAX_FILE_SIZE_BYTES,
    SchemaValidationResult,
)

REQUIRED_COLUMNS = set(CANONICAL_REQUIRED_COLUMNS)
OPTIONAL_COLUMNS = set(CANONICAL_OPTIONAL_COLUMNS)


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
    rejection_reason_counts: dict[str, int] = field(default_factory=lambda: {
        "invalid_timestamp": 0,
        "invalid_amount": 0,
        "invalid_currency": 0,
        "missing_transaction_id": 0,
        "missing_sender_account_id": 0,
        "missing_receiver_account_id": 0,
        "invalid_transaction_type": 0,
        "invalid_channel": 0,
        "invalid_ip_address": 0,
        "invalid_account_balance": 0,
        "schema_validation": 0,
        "duplicate_transaction_id": 0,
        "other": 0,
    })
    sample_errors: list[dict[str, Any]] = field(default_factory=list)
    schema_findings: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    processed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataQualityPipeline:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def process(
        self,
        raw_data: pd.DataFrame | list[dict[str, Any]],
        file_size_bytes: Optional[int] = None,
    ) -> tuple[pd.DataFrame, PreprocessingReport]:
        report = PreprocessingReport()

        if isinstance(raw_data, list):
            df = pd.DataFrame(raw_data)
        else:
            df = raw_data.copy()

        report.records_received = len(df)
        if df.empty:
            report.quality_score = 0.0
            report.quality_grade = "POOR"
            report.summary = "Empty dataset provided: no records found."
            report.rejection_reasons.append({"issue": "EMPTY_DATASET", "detail": "Dataset contains 0 rows."})
            report.rejection_reason_counts["other"] = 1
            return pd.DataFrame(), report

        # 1. Semantic Schema Adaptation & Validation
        inspection = DatasetSchemaAdapter.inspect_schema(
            columns=list(df.columns),
            sample_df=df,
            file_size_bytes=file_size_bytes,
        )

        report.schema_findings = inspection.to_dict()

        if not inspection.valid:
            report.records_rejected = len(df)
            report.quality_score = 0.0
            report.quality_grade = "POOR"
            report.summary = f"Schema validation failed: {'; '.join(inspection.errors)}"
            report.rejection_reasons.append({
                "issue": "SCHEMA_VALIDATION_FAILURE",
                "errors": inspection.errors,
                "missing_required_columns": inspection.missing_required_columns,
                "detected_columns": inspection.detected_columns,
                "detected_format": inspection.detected_format,
            })
            report.rejection_reason_counts["schema_validation"] = len(df)
            report.sample_errors.append({
                "field": "schema",
                "actual_value": list(df.columns)[:8],
                "expected": "Valid AEGIS Canonical or compatible mapped schema",
                "reason": f"Schema validation failed: {'; '.join(inspection.errors)}",
                "row_index": None,
            })
            return pd.DataFrame(), report

        # 2. Apply verified column renames
        rename_map = {
            m["source_column"]: m["canonical_column"]
            for m in inspection.column_mappings
            if m["source_column"] in df.columns
        }
        df = df.rename(columns=rename_map)

        # 3. Detect & Filter Duplicates on transaction_id
        if "transaction_id" in df.columns:
            dups = df[df.duplicated(subset=["transaction_id"], keep="first")]
            report.duplicates_detected = len(dups)
            if len(dups) > 0:
                report.rejection_reasons.append({
                    "issue": "DUPLICATE_TRANSACTION_ID",
                    "count": len(dups),
                    "sample_ids": dups["transaction_id"].head(5).astype(str).tolist(),
                })
                report.rejection_reason_counts["duplicate_transaction_id"] += len(dups)
                for _, dup_row in dups.head(3).iterrows():
                    if len(report.sample_errors) < 5:
                        report.sample_errors.append({
                            "field": "transaction_id",
                            "actual_value": str(dup_row.get("transaction_id", "")),
                            "expected": "Unique transaction identifier",
                            "reason": "Duplicate transaction_id detected; subsequent occurrences rejected",
                            "row_index": int(dup_row.name) if isinstance(dup_row.name, int) else None,
                        })
                # Keep first occurrence, drop duplicates
                df = df.drop_duplicates(subset=["transaction_id"], keep="first")

        # 4. Check Missing Values in Required Fields
        null_counts = df.isnull().sum().to_dict()
        report.missing_values_detected = int(sum(null_counts.values()))

        for col in ["transaction_id", "sender_account_id", "receiver_account_id"]:
            if col in df.columns:
                null_mask = df[col].isnull() | (df[col].astype(str).str.strip() == "")
                null_count = int(null_mask.sum())
                if null_count > 0:
                    report.rejection_reasons.append({
                        "issue": "NULL_REQUIRED_IDENTIFIER",
                        "field": col,
                        "count": null_count,
                    })
                    count_key = f"missing_{col}"
                    if count_key in report.rejection_reason_counts:
                        report.rejection_reason_counts[count_key] += null_count
                    else:
                        report.rejection_reason_counts["other"] += null_count
                    bad_rows = df[null_mask].head(2)
                    for _, b_row in bad_rows.iterrows():
                        if len(report.sample_errors) < 5:
                            report.sample_errors.append({
                                "field": col,
                                "actual_value": str(b_row.get(col, "")),
                                "expected": "Non-empty string identifier",
                                "reason": f"Required identifier '{col}' is missing or blank",
                                "row_index": int(b_row.name) if isinstance(b_row.name, int) else None,
                            })
                    df = df[~null_mask]

        # 5. Amount Validation & Normalization
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            invalid_amt_mask = df["amount"].isna() | (df["amount"] <= 0)
            invalid_amt_count = int(invalid_amt_mask.sum())
            report.invalid_amounts = invalid_amt_count
            if invalid_amt_count > 0:
                report.rejection_reasons.append({
                    "issue": "NON_POSITIVE_OR_NON_NUMERIC_AMOUNT",
                    "count": invalid_amt_count,
                })
                report.rejection_reason_counts["invalid_amount"] += invalid_amt_count
                bad_rows = df[invalid_amt_mask].head(3)
                for _, b_row in bad_rows.iterrows():
                    if len(report.sample_errors) < 5:
                        report.sample_errors.append({
                            "field": "amount",
                            "actual_value": str(b_row.get("amount", "")),
                            "expected": "Positive numeric decimal (> 0)",
                            "reason": "Amount must be a finite positive numeric value",
                            "row_index": int(b_row.name) if isinstance(b_row.name, int) else None,
                        })
                df = df[~invalid_amt_mask]

        # 6. Timestamp Normalization (ISO-8601 UTC)
        if "timestamp" in df.columns:
            parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
            invalid_ts_mask = parsed_ts.isna()
            invalid_ts_count = int(invalid_ts_mask.sum())
            report.timestamp_format_errors = invalid_ts_count
            if invalid_ts_count > 0:
                report.rejection_reasons.append({
                    "issue": "INVALID_TIMESTAMP_FORMAT",
                    "count": invalid_ts_count,
                })
                report.rejection_reason_counts["invalid_timestamp"] += invalid_ts_count
                bad_rows = df[invalid_ts_mask].head(3)
                for _, b_row in bad_rows.iterrows():
                    if len(report.sample_errors) < 5:
                        report.sample_errors.append({
                            "field": "timestamp",
                            "actual_value": str(b_row.get("timestamp", "")),
                            "expected": "ISO-8601 datetime (e.g. YYYY-MM-DDTHH:MM:SSZ)",
                            "reason": "Timestamp could not be parsed into a valid UTC datetime",
                            "row_index": int(b_row.name) if isinstance(b_row.name, int) else None,
                        })
                df = df[~invalid_ts_mask]
                df["timestamp"] = parsed_ts[~invalid_ts_mask].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                df["timestamp"] = parsed_ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 7. Normalize Categoricals & Optional Fields (Non-Dropping)
        if "currency" in df.columns:
            df["currency"] = df["currency"].fillna("INR").astype(str).str.upper().str.strip()
        else:
            df["currency"] = "INR"

        if "transaction_type" in df.columns:
            df["transaction_type"] = df["transaction_type"].fillna("TRANSFER").astype(str).str.upper().str.strip()
        else:
            df["transaction_type"] = "TRANSFER"

        # Optional fields: clean values without dropping records
        for opt_col in ["beneficiary_id", "merchant_id", "device_id", "ip_address", "location", "country"]:
            if opt_col in df.columns:
                df[opt_col] = df[opt_col].fillna("").astype(str).str.strip()

        if "channel" in df.columns:
            df["channel"] = df["channel"].fillna("ONLINE").astype(str).str.upper().str.strip()

        if "account_balance" in df.columns:
            df["account_balance"] = pd.to_numeric(df["account_balance"], errors="coerce").fillna(0.0)

        # 8. Sort chronologically
        if "timestamp" in df.columns:
            df = df.sort_values(by="timestamp", ascending=True)

        report.records_valid = len(df)
        report.records_rejected = report.records_received - report.records_valid

        # 9. Compute Overall Quality Score (0.0 - 100.0)
        # Consistent logic: If 0 records are valid, quality score MUST be 0.0% (POOR)
        if report.records_received == 0 or report.records_valid == 0:
            report.quality_score = 0.0
            report.quality_grade = "POOR"
        else:
            valid_pct = (report.records_valid / report.records_received) * 100.0
            col_count = max(1, len(df.columns))
            missing_penalty = (report.missing_values_detected / max(1, report.records_received * col_count)) * 20.0
            dup_penalty = (report.duplicates_detected / report.records_received) * 10.0
            score = max(0.0, valid_pct - missing_penalty - dup_penalty)
            report.quality_score = round(min(100.0, score), 1)

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

        # Filter to canonical schema fields that exist
        keep_fields = [c for c in df.columns if c in REQUIRED_COLUMNS or c in OPTIONAL_COLUMNS]
        return df[keep_fields].reset_index(drop=True), report
