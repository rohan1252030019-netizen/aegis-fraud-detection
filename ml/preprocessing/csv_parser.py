"""
AEGIS - Enterprise Robust CSV Parser
Handles:
- Header vs Data Row column-count discrepancies
- Prevents Pandas from silently treating column 0 as an unnamed index column (R-style index)
- Semantic alignment of header tokens to data columns when headers are missing/shifted
- Safe byte-stream, string buffer, and file-path ingestion
- Memory-efficient streaming peek for lightweight pre-validation
"""
from __future__ import annotations
import csv
import io
import re
from typing import Any, Optional, Sequence
import pandas as pd


def is_country_code(val: str) -> bool:
    """Check if value looks like a 2-letter ISO country code (e.g. IN, US, GB)."""
    s = val.strip()
    return len(s) == 2 and s.isupper() and s.isalpha()


def is_channel_token(val: str) -> bool:
    """Check if value is a known or plausible payment channel identifier."""
    known_channels = {
        "UPI", "ATM", "NET_BANKING", "CARD", "ONLINE_NETBANKING",
        "MOBILE", "WEB", "BRANCH", "POS", "TRANSFER", "CHECK", "DEBIT", "CREDIT"
    }
    return val.strip().upper() in known_channels


def is_numeric_token(val: str) -> bool:
    """Check if value can be parsed as a float."""
    try:
        float(val.strip())
        return True
    except (ValueError, AttributeError):
        return False


def is_datetime_token(val: str) -> bool:
    """Check if value matches ISO-like date/time."""
    s = val.strip()
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}", s))


def align_csv_headers(header_tokens: list[str], sample_rows: list[list[str]]) -> list[str]:
    """
    Given header tokens from CSV line 1 and sample data rows, resolve the true column names
    when row column count does not match header column count.
    """
    if not sample_rows:
        return list(header_tokens)

    # Filter out empty sample rows
    valid_samples = [r for r in sample_rows if r and len(r) > 0]
    if not valid_samples:
        return list(header_tokens)

    header_len = len(header_tokens)
    row_lens = [len(r) for r in valid_samples]
    # Dominant row length
    row_len = max(set(row_lens), key=row_lens.count)

    if header_len == row_len:
        return list(header_tokens)

    # Check if column 0 is an unnamed sequential index (0, 1, 2... or 1, 2, 3...)
    col0_vals = [r[0].strip() for r in valid_samples if len(r) > 0]
    is_col0_index = False
    try:
        nums = [int(v) for v in col0_vals]
        if nums == list(range(nums[0], nums[0] + len(nums))):
            is_col0_index = True
    except (ValueError, TypeError):
        pass

    if is_col0_index and row_len == header_len + 1:
        return ["_row_index"] + list(header_tokens)

    # Case: Row length > Header length (e.g. 15 data values vs 14 headers)
    # Trace semantic correspondence between data values and expected headers
    aligned_headers: list[str] = []
    h_idx = 0

    for col_idx in range(row_len):
        col_vals = [r[col_idx].strip() for r in valid_samples if len(r) > col_idx and r[col_idx].strip()]

        if h_idx < header_len:
            h_name = header_tokens[h_idx]

            # Scenario A: 'channel' is expected next, but column contains ISO country codes (e.g. 'IN')
            # and next column contains actual payment channel (e.g. 'UPI')
            if h_name == "channel" and col_vals and all(is_country_code(v) for v in col_vals):
                aligned_headers.append("country")
                continue

            # Scenario B: 'account_balance' is expected next, but column contains payment channel strings
            # and the subsequent column contains numeric balance
            if h_name == "account_balance" and col_vals and all(is_channel_token(v) for v in col_vals):
                aligned_headers.append("channel")
                continue

            aligned_headers.append(h_name)
            h_idx += 1
        else:
            # Trailing extra data column without header
            aligned_headers.append(f"unnamed_column_{col_idx}")

    return aligned_headers


def robust_read_csv(
    source: bytes | bytearray | io.IOBase | str,
    nrows: Optional[int] = None,
    dtype: Any = None,
) -> pd.DataFrame:
    """
    Enterprise-grade CSV loader that safely parses transaction files into DataFrames.
    Guarantees:
    - Never converts column 0 into a DataFrame index (enforces index_col=False)
    - Detects and aligns mismatched header tokens with data rows
    - Preserves all transaction rows and columns without silent column-shifting
    """
    if isinstance(source, (bytes, bytearray)):
        stream: io.IOBase = io.BytesIO(source)
    elif isinstance(source, str) and not source.startswith(("http://", "https://")) and "\n" not in source:
        stream = open(source, "rb")
    elif isinstance(source, str):
        stream = io.BytesIO(source.encode("utf-8"))
    else:
        stream = source

    if hasattr(stream, "seek"):
        stream.seek(0)

    # Use TextIOWrapper to inspect first lines
    text_stream = io.TextIOWrapper(stream, encoding="utf-8", errors="replace")
    reader = csv.reader(text_stream)
    try:
        header_row = next(reader)
    except StopIteration:
        return pd.DataFrame()

    sample_rows = []
    for _ in range(50):
        try:
            r = next(reader)
            if r:
                sample_rows.append(r)
        except StopIteration:
            break

    # Detach wrapper so the underlying stream is preserved
    text_stream.detach()
    if hasattr(stream, "seek"):
        stream.seek(0)

    if not sample_rows:
        return pd.read_csv(stream, nrows=nrows, index_col=False, dtype=dtype)

    header_tokens = [col.strip() for col in header_row]
    valid_samples = [r for r in sample_rows if r and len(r) > 0]
    if not valid_samples:
        return pd.read_csv(stream, nrows=nrows, index_col=False, dtype=dtype)

    header_len = len(header_tokens)
    row_lens = [len(r) for r in valid_samples]
    dominant_row_len = max(set(row_lens), key=row_lens.count)

    if header_len == dominant_row_len:
        # Standard 1:1 matching
        return pd.read_csv(stream, nrows=nrows, index_col=False, dtype=dtype)

    # Mismatched lengths: compute aligned headers
    resolved_headers = align_csv_headers(header_tokens, valid_samples)
    df = pd.read_csv(
        stream,
        skiprows=1,
        names=resolved_headers,
        nrows=nrows,
        index_col=False,
        dtype=dtype,
    )
    return df
