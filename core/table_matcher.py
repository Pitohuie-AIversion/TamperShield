from typing import Any, Dict, Iterable, List, Optional, Sequence

import Levenshtein
import pandas as pd

from core.data_normalize import normalize_text_cell


METADATA_COLUMNS = {
    "_source_file",
    "_source_page",
    "_source_table",
    "_source_row",
}


def _visible_columns(df: pd.DataFrame) -> List[str]:
    return [
        normalize_text_cell(col)
        for col in df.columns
        if normalize_text_cell(col) and normalize_text_cell(col) not in METADATA_COLUMNS
    ]


def _compact_text(value: object) -> str:
    return "".join(normalize_text_cell(value).split())


def _similarity(left: str, right: str) -> float:
    if not left and not right:
        return 1.0

    if not left or not right:
        return 0.0

    distance = Levenshtein.distance(left, right)
    denominator = max(len(left), len(right), 1)
    return max(0.0, 1.0 - distance / denominator)


def _best_name_similarity(name: str, candidates: Sequence[str]) -> float:
    if not candidates:
        return 0.0

    return max(_similarity(name, candidate) for candidate in candidates)


def column_similarity(scan_df: pd.DataFrame, base_df: pd.DataFrame) -> float:
    scan_columns = _visible_columns(scan_df)
    base_columns = _visible_columns(base_df)

    if not scan_columns and not base_columns:
        return 1.0

    if not scan_columns or not base_columns:
        return 0.0

    scan_to_base = [
        _best_name_similarity(scan_col, base_columns)
        for scan_col in scan_columns
    ]
    base_to_scan = [
        _best_name_similarity(base_col, scan_columns)
        for base_col in base_columns
    ]

    return (sum(scan_to_base) + sum(base_to_scan)) / (
        len(scan_to_base) + len(base_to_scan)
    )


def _table_text_signature(
    df: pd.DataFrame,
    max_rows: int = 5,
    max_chars: int = 500,
) -> str:
    visible_columns = [
        col for col in df.columns
        if normalize_text_cell(col) not in METADATA_COLUMNS
    ]
    visible = df[visible_columns].head(max_rows) if visible_columns else df.head(max_rows)

    parts: List[str] = []
    parts.extend(_visible_columns(df))

    for row in visible.itertuples(index=False, name=None):
        parts.extend(_compact_text(value) for value in row)

    return "".join(part for part in parts if part)[:max_chars]


def text_similarity(scan_df: pd.DataFrame, base_df: pd.DataFrame) -> float:
    return _similarity(
        _table_text_signature(scan_df),
        _table_text_signature(base_df),
    )


def shape_similarity(scan_df: pd.DataFrame, base_df: pd.DataFrame) -> float:
    scan_rows, scan_cols = scan_df.shape
    base_rows, base_cols = base_df.shape

    scan_visible_cols = len(_visible_columns(scan_df))
    base_visible_cols = len(_visible_columns(base_df))

    row_score = _ratio_similarity(scan_rows, base_rows)
    col_score = _ratio_similarity(scan_visible_cols, base_visible_cols)

    return (row_score + col_score) / 2.0


def _ratio_similarity(left: int, right: int) -> float:
    if left == 0 and right == 0:
        return 1.0

    denominator = max(left, right, 1)
    return min(left, right) / denominator


def key_overlap_score(
    scan_df: pd.DataFrame,
    base_df: pd.DataFrame,
    key_columns: Optional[Iterable[str]] = None,
) -> float:
    if not key_columns:
        return 0.0

    scores: List[float] = []
    for key in key_columns:
        key_name = normalize_text_cell(key)
        if key_name not in scan_df.columns or key_name not in base_df.columns:
            scores.append(0.0)
            continue

        scan_values = {
            _compact_text(value)
            for value in scan_df[key_name].tolist()
            if _compact_text(value)
        }
        base_values = {
            _compact_text(value)
            for value in base_df[key_name].tolist()
            if _compact_text(value)
        }

        if not scan_values and not base_values:
            scores.append(1.0)
            continue

        if not scan_values or not base_values:
            scores.append(0.0)
            continue

        intersection = scan_values & base_values
        union = scan_values | base_values
        scores.append(len(intersection) / max(len(union), 1))

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


def classify_match(score: float) -> str:
    if score >= 0.75:
        return "auto_match"

    if score >= 0.45:
        return "needs_review"

    return "no_match"


def _build_reason(
    column_score: float,
    text_score: float,
    shape_score: float,
    key_score: float,
    common_columns: Sequence[str],
) -> str:
    parts = [
        f"columns={column_score:.3f}",
        f"text={text_score:.3f}",
        f"shape={shape_score:.3f}",
        f"keys={key_score:.3f}",
    ]

    if common_columns:
        parts.append("common_columns=" + ",".join(common_columns))
    else:
        parts.append("common_columns=none")

    return "; ".join(parts)


def score_table_candidate(
    scan_df: pd.DataFrame,
    base_df: pd.DataFrame,
    key_columns: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    column_score = column_similarity(scan_df, base_df)
    content_score = text_similarity(scan_df, base_df)
    table_shape_score = shape_similarity(scan_df, base_df)
    key_score = key_overlap_score(scan_df, base_df, key_columns=key_columns)

    score = (
        column_score * 0.40
        + content_score * 0.30
        + table_shape_score * 0.20
        + key_score * 0.10
    )

    scan_columns = set(_visible_columns(scan_df))
    base_columns = set(_visible_columns(base_df))
    common_columns = sorted(scan_columns & base_columns)

    return {
        "score": round(score, 6),
        "decision": classify_match(score),
        "column_score": round(column_score, 6),
        "text_score": round(content_score, 6),
        "shape_score": round(table_shape_score, 6),
        "key_overlap_score": round(key_score, 6),
        "common_columns": common_columns,
        "reason": _build_reason(
            column_score=column_score,
            text_score=content_score,
            shape_score=table_shape_score,
            key_score=key_score,
            common_columns=common_columns,
        ),
    }


def rank_base_table_candidates(
    scan_df: pd.DataFrame,
    base_tables: Sequence[Dict[str, Any]],
    key_columns: Optional[Iterable[str]] = None,
    top_k: int = 5,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for index, item in enumerate(base_tables):
        base_df = item.get("df")
        if not isinstance(base_df, pd.DataFrame):
            continue

        scored = score_table_candidate(
            scan_df=scan_df,
            base_df=base_df,
            key_columns=key_columns,
        )

        scored.update(
            {
                "base_table_index": item.get("table_index", index),
                "base_source_file": item.get("source_file", ""),
                "base_source_page": item.get("page_index", ""),
                "base_shape": tuple(base_df.shape),
            }
        )
        rows.append(scored)

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    result = result.sort_values(
        by=["score", "column_score", "text_score"],
        ascending=False,
    )
    return result.head(top_k).reset_index(drop=True)


def rank_native_table_candidates(
    scan_df: pd.DataFrame,
    file_paths: Iterable[str],
    key_columns: Optional[Iterable[str]] = None,
    top_k: int = 10,
) -> pd.DataFrame:
    from core.text_parser import (
        extract_tables_from_native_document_with_metadata,
        is_supported_native_document,
    )

    base_tables: List[Dict[str, Any]] = []
    extraction_errors: List[Dict[str, str]] = []
    source_file_count = 0

    for file_path in file_paths:
        if not is_supported_native_document(file_path):
            continue

        source_file_count += 1
        try:
            base_tables.extend(
                extract_tables_from_native_document_with_metadata(file_path)
            )
        except Exception as exc:
            extraction_errors.append(
                {
                    "source_file": file_path,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )

    ranked = rank_base_table_candidates(
        scan_df=scan_df,
        base_tables=base_tables,
        key_columns=key_columns,
        top_k=top_k,
    )
    ranked.attrs["source_file_count"] = source_file_count
    ranked.attrs["base_table_count"] = len(base_tables)
    ranked.attrs["extraction_errors"] = extraction_errors
    return ranked
