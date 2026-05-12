from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional, Sequence

import pandas as pd


def normalize_column_name(column: object) -> str:
    text = "" if column is None else str(column)
    text = text.replace("\u3000", " ")
    text = " ".join(text.split())
    return text.strip()


def normalize_text_cell(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value)
    text = text.replace("\u3000", " ")
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text.strip()


def normalize_numeric_cell(value: object) -> object:
    text = normalize_text_cell(value)

    if not text:
        return ""

    cleaned = text
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("，", "")
    cleaned = cleaned.replace("￥", "")
    cleaned = cleaned.replace("¥", "")
    cleaned = cleaned.replace("元", "")
    cleaned = cleaned.replace("−", "-")
    cleaned = cleaned.replace("—", "-")
    cleaned = cleaned.replace("－", "-")
    cleaned = cleaned.strip()

    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return text


def normalize_dataframe(
    df: pd.DataFrame,
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Iterable[str]] = None,
    ffill_keys: bool = True,
    promote_first_row_to_header: bool = False,
) -> pd.DataFrame:
    normalized = df.copy()

    normalized.columns = [normalize_column_name(col) for col in normalized.columns]
    normalized = normalized.fillna("")

    if promote_first_row_to_header and not normalized.empty:
        header = [
            normalize_column_name(value)
            for value in normalized.iloc[0].tolist()
        ]
        normalized = normalized.iloc[1:].copy()
        normalized.columns = header
        normalized = normalized.reset_index(drop=True)

    for col in normalized.columns:
        normalized[col] = normalized[col].map(normalize_text_cell)

    if key_columns and ffill_keys:
        existing_keys = [col for col in key_columns if col in normalized.columns]
        if existing_keys:
            normalized[existing_keys] = normalized[existing_keys].replace("", pd.NA)
            normalized[existing_keys] = normalized[existing_keys].ffill(axis=0)
            normalized[existing_keys] = normalized[existing_keys].fillna("")

    if numeric_columns:
        for col in numeric_columns:
            if col in normalized.columns:
                normalized[col] = normalized[col].map(normalize_numeric_cell)

    return normalized


def expand_merged_cells(
    df: pd.DataFrame,
    axis: int = 0,
) -> pd.DataFrame:
    expanded = df.copy()
    expanded = expanded.replace("", pd.NA)
    expanded = expanded.ffill(axis=axis)
    expanded = expanded.fillna("")
    return expanded


def attach_source_metadata(
    df: pd.DataFrame,
    source_file: str,
    page_index: Optional[int] = None,
    table_index: Optional[int] = None,
) -> pd.DataFrame:
    result = df.copy()
    result["_source_file"] = source_file

    if page_index is not None:
        result["_source_page"] = page_index

    if table_index is not None:
        result["_source_table"] = table_index

    result["_source_row"] = range(len(result))

    return result
