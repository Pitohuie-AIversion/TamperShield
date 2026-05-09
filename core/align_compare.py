from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Optional, Sequence

import Levenshtein
import pandas as pd


NUMERIC_KEYWORDS = (
    "金额",
    "单价",
    "数量",
    "合价",
    "总价",
    "小计",
    "合计",
    "价款",
    "amount",
    "price",
    "qty",
    "quantity",
    "total",
    "subtotal",
)


def normalize_table(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).strip() for col in normalized.columns]
    normalized = normalized.ffill(axis=0)
    normalized = normalized.fillna("")
    return normalized


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value)
    text = text.replace("\u3000", " ")
    text = " ".join(text.split())
    return text.strip()


def normalize_numeric_value(value: object) -> Optional[Decimal]:
    text = normalize_text(value)

    if not text:
        return None

    text = text.replace(",", "")
    text = text.replace("，", "")
    text = text.replace("￥", "")
    text = text.replace("¥", "")
    text = text.replace("元", "")
    text = text.replace("−", "-")
    text = text.replace("—", "-")
    text = text.replace("－", "-")
    text = text.strip()

    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def is_numeric_column(
    column: str,
    numeric_columns: Optional[Iterable[str]] = None,
) -> bool:
    col = str(column).strip().lower()

    if numeric_columns is not None:
        return str(column) in set(str(c) for c in numeric_columns)

    return any(keyword.lower() in col for keyword in NUMERIC_KEYWORDS)


def compare_text_values(
    base_text: str,
    scan_text: str,
    max_distance: int,
) -> Optional[Dict[str, object]]:
    distance = Levenshtein.distance(base_text, scan_text)
    denominator = max(len(base_text), len(scan_text), 1)
    similarity = 1.0 - distance / denominator

    if distance <= max_distance:
        return None

    return {
        "comparison_type": "text",
        "base_text": base_text,
        "scan_text": scan_text,
        "distance": distance,
        "similarity": round(similarity, 6),
        "threshold": max_distance,
        "passed": False,
    }


def compare_numeric_values(
    base_raw: object,
    scan_raw: object,
    tolerance: Decimal,
) -> Optional[Dict[str, object]]:
    base_value = normalize_numeric_value(base_raw)
    scan_value = normalize_numeric_value(scan_raw)

    base_text = normalize_text(base_raw)
    scan_text = normalize_text(scan_raw)

    if base_value is None or scan_value is None:
        fallback = compare_text_values(
            base_text=base_text,
            scan_text=scan_text,
            max_distance=1,
        )
        if fallback is None:
            return None

        fallback["comparison_type"] = "numeric_parse_failed"
        fallback["base_value"] = str(base_value) if base_value is not None else ""
        fallback["scan_value"] = str(scan_value) if scan_value is not None else ""
        return fallback

    diff = abs(base_value - scan_value)

    if diff <= tolerance:
        return None

    return {
        "comparison_type": "numeric",
        "base_text": base_text,
        "scan_text": scan_text,
        "base_value": str(base_value),
        "scan_value": str(scan_value),
        "numeric_diff": str(diff),
        "threshold": str(tolerance),
        "passed": False,
    }


def compare_cells_with_tolerance(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    key_columns: List[str],
    max_distance: int = 1,
    numeric_columns: Optional[Sequence[str]] = None,
    numeric_tolerance: str = "0.01",
) -> pd.DataFrame:
    """
    Backward-compatible comparison function.

    Parameter convention:
    - left_df  = base_df
    - right_df = scan_df
    """
    base_df = normalize_table(left_df)
    scan_df = normalize_table(right_df)

    key_columns = [str(col).strip() for col in key_columns]

    for key in key_columns:
        if key not in base_df.columns:
            raise ValueError(f"Key column not found in base_df: {key}")
        if key not in scan_df.columns:
            raise ValueError(f"Key column not found in scan_df: {key}")

    merged = base_df.merge(
        scan_df,
        on=key_columns,
        how="outer",
        suffixes=("_base", "_scan"),
        indicator=True,
    )

    tolerance = Decimal(str(numeric_tolerance))

    diffs: List[Dict[str, object]] = []

    comparable_columns = [
        col for col in base_df.columns
        if col not in key_columns and col in scan_df.columns
    ]

    for row_index, row in merged.iterrows():
        keys = {k: row.get(k, "") for k in key_columns}
        merge_status = row.get("_merge", "")

        if merge_status != "both":
            diffs.append(
                {
                    "row_index": row_index,
                    "keys": keys,
                    "column": "",
                    "comparison_type": "row_presence",
                    "base_text": "",
                    "scan_text": "",
                    "merge_status": merge_status,
                    "passed": False,
                }
            )
            continue

        for column in comparable_columns:
            base_col = f"{column}_base"
            scan_col = f"{column}_scan"

            if base_col not in merged.columns or scan_col not in merged.columns:
                continue

            base_raw = row[base_col]
            scan_raw = row[scan_col]

            if is_numeric_column(column, numeric_columns=numeric_columns):
                result = compare_numeric_values(
                    base_raw=base_raw,
                    scan_raw=scan_raw,
                    tolerance=tolerance,
                )
            else:
                result = compare_text_values(
                    base_text=normalize_text(base_raw),
                    scan_text=normalize_text(scan_raw),
                    max_distance=max_distance,
                )

            if result is not None:
                result.update(
                    {
                        "row_index": row_index,
                        "keys": keys,
                        "column": column,
                        "merge_status": merge_status,
                    }
                )
                diffs.append(result)

    return pd.DataFrame(diffs)