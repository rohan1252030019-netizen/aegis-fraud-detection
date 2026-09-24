"""
AEGIS - Data Ingestion & Schema Validation Test Suite
Validates:
1. Valid AEGIS CSV passes validation and normalization.
2. Missing required columns (transaction_id, sender_account_id, receiver_account_id, timestamp) are rejected with structured reporting.
3. Strict 250 MB file size boundary (249MB accepted, 250MB accepted, >250MB rejected).
4. Invalid data reporting (malformed timestamps, non-positive amounts, empty IDs).
5. External dataset format detection (PaySim detected and safely handled; compatible banking aliases mapped with recorded confidence).
6. Security checks (rejection of oversized content, safe schema enforcement).
"""
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd

from ml.preprocessing.schema_adapter import (
    DatasetSchemaAdapter,
    MAX_FILE_SIZE_BYTES,
    CANONICAL_REQUIRED_COLUMNS,
    CANONICAL_OPTIONAL_COLUMNS,
)
from ml.preprocessing.pipeline import DataQualityPipeline


# Sample valid AEGIS dataframe
def make_valid_df(n_rows=5):
    rows = []
    for i in range(1, n_rows + 1):
        rows.append({
            "transaction_id": f"TX_{i:04d}",
            "sender_account_id": f"ACC_{1000 + i}",
            "receiver_account_id": f"ACC_{2000 + i}",
            "amount": 1000.0 * i,
            "currency": "INR",
            "timestamp": f"2026-09-14T10:{i:02d}:00Z",
            "transaction_type": "TRANSFER",
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 1. VALID AEGIS CSV TESTS
# ==============================================================================
def test_valid_aegis_csv_passes():
    df = make_valid_df(5)
    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(df, file_size_bytes=1024)

    assert not clean_df.empty
    assert len(clean_df) == 5
    assert report.records_valid == 5
    assert report.records_rejected == 0
    assert report.quality_score >= 90.0
    assert report.schema_findings["valid"] is True
    assert report.schema_findings["detected_format"] == "AEGIS_CANONICAL"
    assert len(report.schema_findings["missing_required_columns"]) == 0


# ==============================================================================
# 2. MISSING REQUIRED COLUMNS TESTS
# ==============================================================================
@pytest.mark.parametrize("missing_col", [
    "transaction_id",
    "sender_account_id",
    "receiver_account_id",
    "timestamp",
    "amount",
])
def test_missing_required_column_rejected(missing_col):
    df = make_valid_df(5)
    df = df.drop(columns=[missing_col])

    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(df, file_size_bytes=1024)

    assert clean_df.empty, f"Expected empty clean_df when {missing_col} is missing"
    assert report.schema_findings["valid"] is False
    assert missing_col in report.schema_findings["missing_required_columns"]
    assert report.quality_score == 0.0
    assert any("SCHEMA_VALIDATION_FAILURE" == r["issue"] for r in report.rejection_reasons)


# ==============================================================================
# 3. FILE SIZE BOUNDARY TESTS (250 MB Limit)
# ==============================================================================
def test_file_size_249mb_accepted():
    size_249mb = 249 * 1024 * 1024
    inspection = DatasetSchemaAdapter.inspect_schema(
        columns=CANONICAL_REQUIRED_COLUMNS,
        file_size_bytes=size_249mb,
    )
    assert inspection.valid is True
    assert len(inspection.errors) == 0


def test_file_size_exact_250mb_accepted():
    size_250mb = MAX_FILE_SIZE_BYTES  # exactly 250 MB
    inspection = DatasetSchemaAdapter.inspect_schema(
        columns=CANONICAL_REQUIRED_COLUMNS,
        file_size_bytes=size_250mb,
    )
    assert inspection.valid is True
    assert len(inspection.errors) == 0


def test_file_size_exceeding_250mb_rejected():
    # 250.01 MB
    size_over = MAX_FILE_SIZE_BYTES + 1024 * 1024
    inspection = DatasetSchemaAdapter.inspect_schema(
        columns=CANONICAL_REQUIRED_COLUMNS,
        file_size_bytes=size_over,
    )
    assert inspection.valid is False
    assert any("exceeds the 250 MB AEGIS ingestion limit" in err for err in inspection.errors)


def test_file_size_470mb_rejected():
    # The user's exact uploaded file size: 470.67 MB
    size_470mb = int(470.67 * 1024 * 1024)
    inspection = DatasetSchemaAdapter.inspect_schema(
        columns=CANONICAL_REQUIRED_COLUMNS,
        file_size_bytes=size_470mb,
    )
    assert inspection.valid is False
    assert any("470.67 MB" in err for err in inspection.errors)


# ==============================================================================
# 4. INVALID DATA DETECTION TESTS
# ==============================================================================
def test_malformed_timestamp_detected_and_filtered():
    df = make_valid_df(5)
    # Corrupt 2 timestamps
    df.loc[1, "timestamp"] = "NOT_A_DATE"
    df.loc[3, "timestamp"] = "2026/99/99 99:99"

    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(df, file_size_bytes=1024)

    assert report.timestamp_format_errors == 2
    assert len(clean_df) == 3  # 2 malformed rows dropped
    assert any(r["issue"] == "INVALID_TIMESTAMP_FORMAT" for r in report.rejection_reasons)


def test_non_numeric_and_negative_amounts():
    df = make_valid_df(5)
    df["amount"] = df["amount"].astype(object)
    df.loc[0, "amount"] = -500.0  # negative
    df.loc[2, "amount"] = "INVALID_AMT"  # non-numeric

    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(df, file_size_bytes=1024)

    assert report.invalid_amounts == 2
    assert len(clean_df) == 3
    assert any(r["issue"] == "NON_POSITIVE_OR_NON_NUMERIC_AMOUNT" for r in report.rejection_reasons)


def test_empty_and_null_transaction_ids():
    df = make_valid_df(5)
    df.loc[1, "transaction_id"] = ""
    df.loc[3, "transaction_id"] = None

    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(df, file_size_bytes=1024)

    assert len(clean_df) == 3
    assert any(r["issue"] == "NULL_REQUIRED_IDENTIFIER" for r in report.rejection_reasons)


# ==============================================================================
# 5. EXTERNAL DATASET FORMAT DETECTION & SAFE ADAPTER TESTS
# ==============================================================================
def test_paysim_dataset_detection_and_rejection():
    """
    PaySim dataset (e.g. PS_20174392719_1491204439457_log.csv):
    Contains step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud.
    Must be detected as PAYSIM_SYNTHETIC_AML, must not be blindly renamed,
    and must be rejected with explicit explanation of missing transaction_id and timestamp.
    """
    paysim_cols = [
        "step", "type", "amount", "nameOrig", "oldbalanceOrg",
        "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest",
        "isFraud", "isFlaggedFraud"
    ]
    paysim_df = pd.DataFrame([{
        "step": 1,
        "type": "TRANSFER",
        "amount": 181.0,
        "nameOrig": "C1231006815",
        "oldbalanceOrg": 181.0,
        "newbalanceOrig": 0.0,
        "nameDest": "C553264065",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "isFraud": 1,
        "isFlaggedFraud": 0
    }])

    inspection = DatasetSchemaAdapter.inspect_schema(columns=paysim_cols, sample_df=paysim_df)

    assert inspection.valid is False
    assert inspection.detected_format == "PAYSIM_SYNTHETIC_AML"
    assert "transaction_id" in inspection.missing_required_columns
    assert "timestamp" in inspection.missing_required_columns
    assert any("PaySim" in err for err in inspection.errors)
    assert any("transaction_id" in err for err in inspection.errors)

    # Verify column mappings recorded
    mappings = {m["canonical_column"]: m["source_column"] for m in inspection.column_mappings}
    assert mappings.get("sender_account_id") == "nameOrig"
    assert mappings.get("receiver_account_id") == "nameDest"
    assert mappings.get("amount") == "amount"
    assert mappings.get("transaction_type") == "type"


def test_compatible_external_banking_dataset_safely_mapped():
    """
    External dataset using standard banking aliases:
    'TxID', 'from_account', 'to_account', 'transfer_amount', 'datetime'
    Must be detected, mapped with documented confidence and reasons, and succeed.
    """
    external_cols = ["TxID", "from_account", "to_account", "transfer_amount", "datetime"]
    external_df = pd.DataFrame([{
        "TxID": "BNK_99182",
        "from_account": "ACC_DEBIT_11",
        "to_account": "ACC_CREDIT_22",
        "transfer_amount": 54000.0,
        "datetime": "2026-09-14T12:00:00Z",
    }])

    adapted_df, inspection = DatasetSchemaAdapter.adapt_dataframe(external_df)

    assert inspection.valid is True
    assert not adapted_df.empty
    assert "transaction_id" in adapted_df.columns
    assert "sender_account_id" in adapted_df.columns
    assert "receiver_account_id" in adapted_df.columns
    assert "amount" in adapted_df.columns
    assert "timestamp" in adapted_df.columns
    assert adapted_df["transaction_id"].iloc[0] == "BNK_99182"
    assert adapted_df["sender_account_id"].iloc[0] == "ACC_DEBIT_11"
    assert adapted_df["amount"].iloc[0] == 54000.0

    # Ensure all mappings have reasons and confidence
    for m in inspection.column_mappings:
        assert m["confidence"] > 0.90
        assert len(m["mapping_reason"]) > 0


# ==============================================================================
# 6. SECURITY & BOUNDARY TESTS
# ==============================================================================
def test_empty_dataset_rejection():
    empty_df = pd.DataFrame()
    preprocessor = DataQualityPipeline()
    clean_df, report = preprocessor.process(empty_df)

    assert clean_df.empty
    assert report.quality_score == 0.0
    assert report.records_received == 0
    assert any("EMPTY_DATASET" == r["issue"] for r in report.rejection_reasons)


# ==============================================================================
# 7. ROBUST CSV PARSER & HEADER ALIGNMENT TESTS
# ==============================================================================
def test_robust_csv_parser_mismatched_14_headers_15_columns():
    """
    Test CSV where header has 14 columns (country missing between location and channel)
    and rows have 15 values. Ensures robust_read_csv preserves transaction_id in col 0
    and does not shift columns or guess index_col=0.
    """
    from ml.preprocessing.csv_parser import robust_read_csv

    csv_data = b"""transaction_id,sender_account_id,receiver_account_id,amount,currency,timestamp,transaction_type,beneficiary_id,merchant_id,device_id,ip_address,location,channel,account_balance
TXN000000000001,ACC00001640,ACC00048599,1813.76,USD,2026-01-25T19:41:00Z,TRANSFER,BEN0001042,MER0000977,DEV0001536,10.111.119.130,Hyderabad,IN,UPI,221912.39
TXN000000000002,ACC00046926,ACC00042591,5404.50,INR,2026-01-27T19:38:00Z,DEBIT,BEN0024865,MER0005232,DEV0006925,10.174.142.40,Mumbai,IN,NET_BANKING,699085.82
"""
    df = robust_read_csv(csv_data)
    assert len(df) == 2
    assert "transaction_id" in df.columns
    assert "amount" in df.columns
    assert "country" in df.columns
    assert df["transaction_id"].iloc[0] == "TXN000000000001"
    assert df["amount"].iloc[0] == 1813.76 or str(df["amount"].iloc[0]) == "1813.76"
    assert df["currency"].iloc[0] == "USD"
    assert df["country"].iloc[0] == "IN"
    assert df["channel"].iloc[0] == "UPI"

    # Process through pipeline
    clean_df, report = DataQualityPipeline().process(df)
    assert len(clean_df) == 2
    assert report.records_valid == 2
    assert report.records_rejected == 0
    assert report.quality_score == 100.0


def test_rejection_reason_counts_and_sample_errors():
    """
    Test that invalid rows produce structured rejection_reason_counts and sample_errors.
    """
    df = make_valid_df(5)
    # Row 0: invalid amount
    df.loc[0, "amount"] = -500.0
    # Row 1: invalid timestamp
    df.loc[1, "timestamp"] = "not_a_valid_timestamp"
    # Row 2: duplicate transaction_id of Row 4
    df.loc[2, "transaction_id"] = df.loc[4, "transaction_id"]

    clean_df, report = DataQualityPipeline().process(df)
    assert report.records_valid < 5
    assert report.records_rejected > 0
    assert report.rejection_reason_counts["invalid_amount"] >= 1
    assert report.rejection_reason_counts["invalid_timestamp"] >= 1
    assert report.rejection_reason_counts["duplicate_transaction_id"] >= 1

    # Verify sample errors structure
    assert len(report.sample_errors) > 0
    first_err = report.sample_errors[0]
    assert "field" in first_err
    assert "actual_value" in first_err
    assert "expected" in first_err
    assert "reason" in first_err


def test_synthetic_dataset_sample_if_present():
    """
    Test first 10 and 1000 rows of actual aegis_100mb_synthetic_transactions.csv
    if present on disk.
    """
    import os
    from ml.preprocessing.csv_parser import robust_read_csv

    test_path = r"C:\Users\ADMIN\Downloads\aegis_100mb_synthetic_transactions.csv"
    if not os.path.exists(test_path):
        pytest.skip("Synthetic transactions file not present on this machine")

    # Test 10 rows
    df_10 = robust_read_csv(test_path, nrows=10)
    clean_10, rep_10 = DataQualityPipeline().process(df_10)
    assert rep_10.records_valid == 10
    assert rep_10.records_rejected == 0
    assert rep_10.quality_score == 100.0

    # Test 1000 rows
    df_1000 = robust_read_csv(test_path, nrows=1000)
    clean_1000, rep_1000 = DataQualityPipeline().process(df_1000)
    assert rep_1000.records_valid == 1000
    assert rep_1000.records_rejected == 0
    assert rep_1000.quality_score == 100.0

