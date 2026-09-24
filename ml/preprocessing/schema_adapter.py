"""
AEGIS - Dataset Schema Detection & Semantic Adapter Layer
Handles:
- Canonical AEGIS schema definition & validation
- Source dataset format detection (AEGIS, PaySim, Banking/ISO, Generic)
- Safe semantic column mapping with recorded confidence, rationale & transformations
- Critical field protection (never fabricates transaction_id, sender, receiver, timestamp)
- File size boundary enforcement (250 MB limit)
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
import re
import pandas as pd

# Canonical 250 MB limit in bytes (250 * 1024 * 1024)
MAX_FILE_SIZE_BYTES = 250 * 1024 * 1024  # 262,144,000 bytes

CANONICAL_REQUIRED_COLUMNS = [
    "transaction_id",
    "sender_account_id",
    "receiver_account_id",
    "amount",
    "timestamp",
]

CANONICAL_OPTIONAL_COLUMNS = [
    "currency",
    "transaction_type",
    "beneficiary_id",
    "merchant_id",
    "device_id",
    "ip_address",
    "location",
    "country",
    "channel",
    "account_balance",
]

# High-confidence semantic aliases for banking / AML data
SEMANTIC_ALIASES: dict[str, list[tuple[str, str, float]]] = {
    # target_field: [(source_pattern, rationale, confidence)]
    "transaction_id": [
        (r"^(txn?_?id|transaction_?id|tx_?ref|reference_?no|trans_?id|transfer_?id)$", "Standard transaction reference identifier", 0.98),
    ],
    "sender_account_id": [
        (r"^(sender(_account)?(_id)?|source(_account)?(_id)?|from_account|originator(_account)?|from_acc|debit_account)$", "Originator / debtor account identifier", 0.95),
        (r"^nameorig$", "PaySim mobile money originator account identifier", 0.98),
    ],
    "receiver_account_id": [
        (r"^(receiver(_account)?(_id)?|destination(_account)?(_id)?|to_account|beneficiary(_account)?(_id)?|to_acc|credit_account)$", "Recipient / creditor account identifier", 0.95),
        (r"^namedest$", "PaySim mobile money destination account identifier", 0.98),
    ],
    "amount": [
        (r"^(amount|txn?_?amount|trans_?amount|sum|value|transfer_?amount)$", "Primary transaction currency amount", 0.99),
    ],
    "timestamp": [
        (r"^(timestamp|trans?_?date_?time|datetime|tx_?date|trans_?date|created_?at|time_?stamp|date_?time)$", "Transaction occurrence timestamp", 0.98),
    ],
    "currency": [
        (r"^(currency|curr|ccy|currency_?code)$", "ISO currency code", 0.95),
    ],
    "transaction_type": [
        (r"^(type|transaction_?type|txn?_?type|trans_?type|payment_?type|action_?type)$", "Transaction classification / payment method", 0.95),
    ],
    "account_balance": [
        (r"^(oldbalanceorg|balance|account_?balance|sender_?balance)$", "Pre-transaction account balance", 0.90),
    ],
    "country": [
        (r"^(country|country_?code|iso_?country|nation)$", "ISO country code or transaction country", 0.95),
    ],
    "channel": [
        (r"^(channel|payment_?channel|transaction_?channel|payment_?method)$", "Payment delivery channel", 0.95),
    ],
    "location": [
        (r"^(location|city|region|geo|place)$", "Geographic location or city", 0.95),
    ],
}


@dataclass
class ColumnMappingRecord:
    source_column: str
    canonical_column: str
    mapping_reason: str
    confidence: float
    transformation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaValidationResult:
    valid: bool
    file_size_bytes: Optional[int] = None
    max_file_size_bytes: int = MAX_FILE_SIZE_BYTES
    detected_format: str = "UNKNOWN"
    detected_columns: list[str] = field(default_factory=list)
    required_columns: list[str] = field(default_factory=lambda: list(CANONICAL_REQUIRED_COLUMNS))
    missing_required_columns: list[str] = field(default_factory=list)
    optional_columns: list[str] = field(default_factory=list)
    unexpected_columns: list[str] = field(default_factory=list)
    column_mappings: list[dict[str, Any]] = field(default_factory=list)
    inferred_types: dict[str, str] = field(default_factory=dict)
    sample_preview: list[dict[str, Any]] = field(default_factory=list)
    row_count: Optional[int] = None
    null_counts: dict[str, int] = field(default_factory=dict)
    invalid_values: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rejection_reason_counts: dict[str, int] = field(default_factory=dict)
    sample_errors: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DatasetSchemaAdapter:
    """
    Analyzes uploaded datasets, identifies format signatures, safely maps compatible
    semantic columns, and enforces rigorous AEGIS canonical requirements.
    """

    @staticmethod
    def detect_format(columns: list[str]) -> str:
        clean_cols = [c.lower().strip() for c in columns]
        col_set = set(clean_cols)

        # Check for PaySim signature: step, type, amount, nameOrig, nameDest...
        paysim_markers = {"nameorig", "namedest", "step", "amount"}
        if paysim_markers.issubset(col_set):
            return "PAYSIM_SYNTHETIC_AML"

        # Check for AEGIS Canonical
        aegis_canonical_markers = {"transaction_id", "sender_account_id", "receiver_account_id", "amount", "timestamp"}
        if aegis_canonical_markers.issubset(col_set):
            return "AEGIS_CANONICAL"

        # Check for ISO 20022 / Swift banking alias format
        banking_sender = any(re.match(r"^(sender|from_account|debtor)", c) for c in clean_cols)
        banking_receiver = any(rematch := re.match(r"^(receiver|to_account|creditor|beneficiary)", c) for c in clean_cols)
        if banking_sender and banking_receiver:
            return "EXTERNAL_BANKING_LEDGER"

        return "CUSTOM_OR_UNSTRUCTURED_CSV"

    @classmethod
    def inspect_schema(
        cls,
        columns: list[str],
        sample_df: Optional[pd.DataFrame] = None,
        file_size_bytes: Optional[int] = None,
    ) -> SchemaValidationResult:
        detected_format = cls.detect_format(columns)
        clean_cols = [c.strip() for c in columns]
        norm_map = {c: re.sub(r"[^\w]", "_", c.lower()) for c in clean_cols}

        mappings: list[ColumnMappingRecord] = []
        mapped_canonical: set[str] = set()
        source_mapped: set[str] = set()

        errors: list[str] = []
        warnings: list[str] = []

        # 1. Enforce 250 MB File Size Boundary
        if file_size_bytes is not None:
            if file_size_bytes > MAX_FILE_SIZE_BYTES:
                size_mb = file_size_bytes / (1024 * 1024)
                errors.append(
                    f"File exceeds the 250 MB AEGIS ingestion limit. "
                    f"Uploaded size: {size_mb:.2f} MB, Maximum allowed: 250.00 MB."
                )

        # 2. Check exact canonical matches first
        for orig_c, norm_c in norm_map.items():
            if norm_c in CANONICAL_REQUIRED_COLUMNS or norm_c in CANONICAL_OPTIONAL_COLUMNS:
                mappings.append(
                    ColumnMappingRecord(
                        source_column=orig_c,
                        canonical_column=norm_c,
                        mapping_reason="Direct canonical column match",
                        confidence=1.0,
                        transformation="exact_canonical_match",
                    )
                )
                mapped_canonical.add(norm_c)
                source_mapped.add(orig_c)

        # 3. For unmapped canonical fields, check safe semantic aliases
        unresolved_canonical = (set(CANONICAL_REQUIRED_COLUMNS) | set(CANONICAL_OPTIONAL_COLUMNS)) - mapped_canonical
        for target_field in unresolved_canonical:
            rules = SEMANTIC_ALIASES.get(target_field, [])
            for orig_c, norm_c in norm_map.items():
                if orig_c in source_mapped:
                    continue
                for pattern, rationale, conf in rules:
                    if re.match(pattern, norm_c, re.IGNORECASE):
                        mappings.append(
                            ColumnMappingRecord(
                                source_column=orig_c,
                                canonical_column=target_field,
                                mapping_reason=rationale,
                                confidence=conf,
                                transformation="semantic_alias_cast",
                            )
                        )
                        mapped_canonical.add(target_field)
                        source_mapped.add(orig_c)
                        break
                if target_field in mapped_canonical:
                    break

        # 4. Identify missing required columns
        missing_req = [c for c in CANONICAL_REQUIRED_COLUMNS if c not in mapped_canonical]

        # 5. Specialized checks for known incompatible formats (e.g. PaySim)
        if detected_format == "PAYSIM_SYNTHETIC_AML":
            if "transaction_id" in missing_req or "timestamp" in missing_req:
                errors.append(
                    "PaySim synthetic financial log detected. While sender ('nameOrig') and receiver ('nameDest') "
                    "can be mapped, PaySim lacks immutable 'transaction_id' references and real-world 'timestamp' provenance. "
                    "AEGIS does not fabricate critical transaction identifiers or dates."
                )

        if missing_req and not (detected_format == "PAYSIM_SYNTHETIC_AML" and errors):
            errors.append(
                f"Missing required AEGIS canonical columns: {missing_req}. "
                f"Every ingested dataset must supply verifiable transaction identifiers, accounts, amount, and timestamps."
            )

        # 6. Categorize optional and unexpected columns
        optional_found = [c for c in CANONICAL_OPTIONAL_COLUMNS if c in mapped_canonical]
        unexpected = [c for c in clean_cols if c not in source_mapped]

        # 7. Inferred types and sample validation
        inferred_types: dict[str, str] = {}
        null_counts: dict[str, int] = {}
        invalid_vals: list[dict[str, Any]] = []
        row_count: Optional[int] = None
        preview: list[dict[str, Any]] = []

        if sample_df is not None and not sample_df.empty:
            row_count = len(sample_df)
            import json as _json
            preview = _json.loads(sample_df.head(5).to_json(orient="records"))

            for c in sample_df.columns:
                inferred_types[c] = str(sample_df[c].dtype)
                null_counts[c] = int(sample_df[c].isnull().sum())

            # Check amounts if amount column resolved
            amt_map = next((m for m in mappings if m.canonical_column == "amount"), None)
            if amt_map and amt_map.source_column in sample_df.columns:
                amt_col = amt_map.source_column
                numeric_amts = pd.to_numeric(sample_df[amt_col], errors="coerce")
                bad_amts = sample_df[numeric_amts.isna() | (numeric_amts <= 0)]
                if len(bad_amts) > 0:
                    invalid_vals.append({
                        "field": amt_col,
                        "issue": "NON_POSITIVE_OR_NON_NUMERIC_AMOUNT",
                        "count": len(bad_amts),
                    })
                    warnings.append(f"Found {len(bad_amts)} non-positive or non-numeric amounts in '{amt_col}'.")

            # Check timestamps if timestamp column resolved
            ts_map = next((m for m in mappings if m.canonical_column == "timestamp"), None)
            if ts_map and ts_map.source_column in sample_df.columns:
                ts_col = ts_map.source_column
                parsed_ts = pd.to_datetime(sample_df[ts_col], errors="coerce", utc=True)
                bad_ts = sample_df[parsed_ts.isna()]
                if len(bad_ts) > 0:
                    invalid_vals.append({
                        "field": ts_col,
                        "issue": "MALFORMED_TIMESTAMP",
                        "count": len(bad_ts),
                    })
                    warnings.append(f"Found {len(bad_ts)} malformed timestamp values in '{ts_col}'.")

        is_valid = len(errors) == 0 and len(missing_req) == 0

        return SchemaValidationResult(
            valid=is_valid,
            file_size_bytes=file_size_bytes,
            max_file_size_bytes=MAX_FILE_SIZE_BYTES,
            detected_format=detected_format,
            detected_columns=clean_cols,
            required_columns=CANONICAL_REQUIRED_COLUMNS,
            missing_required_columns=missing_req,
            optional_columns=optional_found,
            unexpected_columns=unexpected,
            column_mappings=[m.to_dict() for m in mappings],
            inferred_types=inferred_types,
            sample_preview=preview,
            row_count=row_count,
            null_counts=null_counts,
            invalid_values=invalid_vals,
            errors=errors,
            warnings=warnings,
        )

    @classmethod
    def adapt_dataframe(cls, df: pd.DataFrame) -> tuple[pd.DataFrame, SchemaValidationResult]:
        """
        Applies verified semantic mappings to convert source dataframe into AEGIS canonical schema.
        Rejects immediately if required canonical columns cannot be resolved.
        """
        inspection = cls.inspect_schema(list(df.columns), sample_df=df)
        if not inspection.valid:
            return pd.DataFrame(), inspection

        # Rename columns according to mapping
        rename_dict = {
            m["source_column"]: m["canonical_column"]
            for m in inspection.column_mappings
        }
        adapted_df = df.rename(columns=rename_dict)

        # Keep canonical columns present in the adapted dataframe
        keep_cols = [c for c in adapted_df.columns if c in CANONICAL_REQUIRED_COLUMNS or c in CANONICAL_OPTIONAL_COLUMNS]
        return adapted_df[keep_cols].copy(), inspection
