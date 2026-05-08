from typing import Dict, List

import Levenshtein
import pandas as pd


def normalize_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill merged-cell gaps to align row semantics.
    """
    normalized = df.copy()
    normalized = normalized.ffill(axis=0)
    return normalized


def compare_cells_with_tolerance(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    key_columns: List[str],
    max_distance: int = 1,
) -> pd.DataFrame:
    """
    Align two tables by keys and compare text with Levenshtein tolerance.
    """
    left_n = normalize_table(left_df)
    right_n = normalize_table(right_df)
    merged = left_n.merge(right_n, on=key_columns, how="outer", suffixes=("_scan", "_base"))

    diffs: List[Dict[str, object]] = []
    for _, row in merged.iterrows():
        for column in left_n.columns:
            if column in key_columns:
                continue
            scan_col = f"{column}_scan"
            base_col = f"{column}_base"
            if scan_col not in merged.columns or base_col not in merged.columns:
                continue

            scan_text = "" if pd.isna(row[scan_col]) else str(row[scan_col])
            base_text = "" if pd.isna(row[base_col]) else str(row[base_col])
            distance = Levenshtein.distance(scan_text, base_text)
            if distance > max_distance:
                diffs.append(
                    {
                        "keys": {k: row[k] for k in key_columns},
                        "column": column,
                        "scan_text": scan_text,
                        "base_text": base_text,
                        "distance": distance,
                    }
                )

    return pd.DataFrame(diffs)

