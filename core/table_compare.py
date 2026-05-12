"""
Table inspection dispatcher for the Document-first TamperShield pipeline.

This module is a thin table_compare layer. It is not the document comparison
entrypoint, and it does not rewrite table matching or cell comparison logic.
"""

from typing import Any, Optional, Sequence

from core.document_models import Difference, DocumentElement, DocumentPage


def extract_table_elements(page: DocumentPage) -> list[DocumentElement]:
    """Return table elements already present on a parsed document page."""
    return [
        element
        for element in page.elements
        if element.element_type == "table"
    ]


def element_to_table_item(element: DocumentElement) -> Optional[dict[str, Any]]:
    """Convert a table element with a DataFrame payload into a matcher item."""
    pd = _pandas()

    df = None
    if isinstance(element.raw, pd.DataFrame):
        df = element.raw
    elif isinstance(element.raw, dict) and isinstance(element.raw.get("df"), pd.DataFrame):
        df = element.raw["df"]

    if df is None:
        return None

    return {
        "df": df,
        "source_file": element.metadata.get("source_file", ""),
        "page_index": element.metadata.get("page_index", ""),
        "table_index": element.metadata.get("table_index", ""),
        "element_id": element.element_id,
    }


def should_run_table_compare(page_differences: Sequence[Difference]) -> bool:
    """Return True when content_compare flagged table inspection as needed."""
    return any(
        difference.metadata.get("requires_table_compare") is True
        for difference in page_differences
    )


def compare_page_tables_if_needed(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    page_differences: Sequence[Difference],
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Sequence[str]] = None,
    top_k: int = 3,
    max_distance: int = 1,
    numeric_tolerance: str = "0.01",
) -> list[Difference]:
    """Run table-level inspection only when page differences request it."""
    if not should_run_table_compare(page_differences):
        return []

    candidate_elements = extract_table_elements(candidate_page)
    baseline_elements = extract_table_elements(baseline_page)

    if not candidate_elements and not baseline_elements:
        return []

    if candidate_elements and not baseline_elements:
        return [
            _table_presence_difference(
                diff_type="table_added",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_count=len(candidate_elements),
                baseline_count=0,
            )
        ]

    if baseline_elements and not candidate_elements:
        return [
            _table_presence_difference(
                diff_type="table_deleted",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_count=0,
                baseline_count=len(baseline_elements),
            )
        ]

    candidate_items = _elements_to_table_items(candidate_elements)
    baseline_items = _elements_to_table_items(baseline_elements)

    if not candidate_items or not baseline_items:
        return [
            _manual_review_difference(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                message="Table elements detected, but DataFrame payload is unavailable for table comparison.",
                metadata={
                    "candidate_table_count": len(candidate_elements),
                    "baseline_table_count": len(baseline_elements),
                    "candidate_dataframe_count": len(candidate_items),
                    "baseline_dataframe_count": len(baseline_items),
                },
            )
        ]

    differences: list[Difference] = []
    for candidate_index, candidate_item in enumerate(candidate_items):
        try:
            differences.extend(
                _compare_one_candidate_table(
                    candidate_item=candidate_item,
                    candidate_index=candidate_index,
                    baseline_items=baseline_items,
                    candidate_page=candidate_page,
                    baseline_page=baseline_page,
                    key_columns=key_columns,
                    numeric_columns=numeric_columns,
                    top_k=top_k,
                    max_distance=max_distance,
                    numeric_tolerance=numeric_tolerance,
                )
            )
        except Exception as exc:
            differences.append(
                _manual_review_difference(
                    candidate_page=candidate_page,
                    baseline_page=baseline_page,
                    candidate_element_id=candidate_item.get("element_id"),
                    message="Table comparison failed for one candidate table.",
                    metadata={
                        "candidate_table_index": candidate_item.get("table_index", candidate_index),
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    },
                )
            )

    return differences


def table_diff_dataframe_to_differences(
    diff_df: Any,
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_element_id: str,
    baseline_element_id: str,
    candidate_table_index: Any = None,
    baseline_table_index: Any = None,
) -> list[Difference]:
    """Translate deterministic cell-diff rows into Document-first Difference items."""
    if diff_df is None or getattr(diff_df, "empty", True):
        return []

    differences: list[Difference] = []
    for row_index, row in diff_df.iterrows():
        row_data = row.to_dict()
        comparison_type = row_data.get("comparison_type", "")
        column = row_data.get("column", "")
        severity = "high" if comparison_type == "numeric" else "medium"

        differences.append(
            Difference(
                diff_type="table_cell_modified",
                severity=severity,
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                candidate_element_id=candidate_element_id,
                baseline_element_id=baseline_element_id,
                message=(
                    f"Table cell difference detected in column '{column}' "
                    f"with comparison_type '{comparison_type}'."
                ),
                metadata={
                    "row_index": row_data.get("row_index", row_index),
                    "keys": row_data.get("keys", {}),
                    "column": column,
                    "comparison_type": comparison_type,
                    "base_text": row_data.get("base_text", ""),
                    "scan_text": row_data.get("scan_text", ""),
                    "merge_status": row_data.get("merge_status", ""),
                    "candidate_table_index": candidate_table_index,
                    "baseline_table_index": baseline_table_index,
                },
            )
        )

    return differences


def _compare_one_candidate_table(
    candidate_item: dict[str, Any],
    candidate_index: int,
    baseline_items: list[dict[str, Any]],
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    key_columns: Optional[Sequence[str]],
    numeric_columns: Optional[Sequence[str]],
    top_k: int,
    max_distance: int,
    numeric_tolerance: str,
) -> list[Difference]:
    candidate_df = candidate_item["df"]
    ranked = _rank_base_table_candidates()(
        candidate_df,
        baseline_items,
        key_columns=key_columns,
        top_k=top_k,
    )

    if ranked.empty:
        return [
            _manual_review_difference(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element_id=candidate_item.get("element_id"),
                message="No baseline table candidates were produced for candidate table.",
                metadata={
                    "candidate_table_index": candidate_item.get("table_index", candidate_index),
                },
            )
        ]

    top_candidate = ranked.iloc[0].to_dict()
    decision = top_candidate.get("decision", "")
    baseline_item = _find_baseline_item(
        baseline_items=baseline_items,
        ranked_row=top_candidate,
    )
    metadata = _match_metadata(
        ranked_row=top_candidate,
        candidate_item=candidate_item,
        baseline_item=baseline_item,
        candidate_index=candidate_index,
    )

    if decision in {"no_match", "needs_review"}:
        return [
            _manual_review_difference(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element_id=candidate_item.get("element_id"),
                baseline_element_id=baseline_item.get("element_id") if baseline_item else None,
                message=f"Table candidate ranking returned {decision}; manual review is required.",
                metadata=metadata,
            )
        ]

    if decision != "auto_match":
        return [
            _manual_review_difference(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element_id=candidate_item.get("element_id"),
                baseline_element_id=baseline_item.get("element_id") if baseline_item else None,
                message="Table candidate ranking returned an unknown decision.",
                metadata=metadata,
            )
        ]

    if not baseline_item:
        return [
            _manual_review_difference(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element_id=candidate_item.get("element_id"),
                message="Auto-matched baseline table item could not be resolved.",
                metadata=metadata,
            )
        ]

    if not key_columns:
        metadata["cell_compare_skipped"] = True
        return [
            Difference(
                diff_type="unknown",
                severity="low",
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                candidate_element_id=candidate_item.get("element_id"),
                baseline_element_id=baseline_item.get("element_id"),
                message="Table matched, but key_columns are not provided; cell-level comparison skipped.",
                metadata=metadata,
            )
        ]

    diff_df = _compare_cells_with_tolerance()(
        left_df=baseline_item["df"],
        right_df=candidate_df,
        key_columns=list(key_columns),
        max_distance=max_distance,
        numeric_columns=numeric_columns,
        numeric_tolerance=numeric_tolerance,
    )
    return table_diff_dataframe_to_differences(
        diff_df=diff_df,
        candidate_page=candidate_page,
        baseline_page=baseline_page,
        candidate_element_id=str(candidate_item.get("element_id", "")),
        baseline_element_id=str(baseline_item.get("element_id", "")),
        candidate_table_index=candidate_item.get("table_index", candidate_index),
        baseline_table_index=baseline_item.get("table_index"),
    )


def _elements_to_table_items(elements: Sequence[DocumentElement]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for element in elements:
        item = element_to_table_item(element)
        if item is not None:
            items.append(item)
    return items


def _find_baseline_item(
    baseline_items: Sequence[dict[str, Any]],
    ranked_row: dict[str, Any],
) -> Optional[dict[str, Any]]:
    ranked_table_index = ranked_row.get("base_table_index")
    ranked_source_file = ranked_row.get("base_source_file")
    ranked_page_index = ranked_row.get("base_source_page")

    for fallback_index, item in enumerate(baseline_items):
        if item.get("table_index", fallback_index) != ranked_table_index:
            continue
        if ranked_source_file not in ("", None) and item.get("source_file", "") != ranked_source_file:
            continue
        if ranked_page_index not in ("", None) and item.get("page_index", "") != ranked_page_index:
            continue
        return item

    if isinstance(ranked_table_index, int) and 0 <= ranked_table_index < len(baseline_items):
        return baseline_items[ranked_table_index]

    return None


def _table_presence_difference(
    diff_type: str,
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_count: int,
    baseline_count: int,
) -> Difference:
    return Difference(
        diff_type=diff_type,
        severity="high",
        candidate_page=candidate_page.page_number,
        baseline_page=baseline_page.page_number,
        message=f"Table presence changed: candidate={candidate_count}, baseline={baseline_count}.",
        metadata={
            "candidate_table_count": candidate_count,
            "baseline_table_count": baseline_count,
            "requires_table_compare": True,
        },
    )


def _manual_review_difference(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    message: str,
    candidate_element_id: Optional[str] = None,
    baseline_element_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Difference:
    merged_metadata = {
        "requires_manual_review": True,
    }
    if metadata:
        merged_metadata.update(metadata)

    return Difference(
        diff_type="unknown",
        severity="medium",
        candidate_page=candidate_page.page_number,
        baseline_page=baseline_page.page_number,
        candidate_element_id=candidate_element_id,
        baseline_element_id=baseline_element_id,
        message=message,
        metadata=merged_metadata,
    )


def _match_metadata(
    ranked_row: dict[str, Any],
    candidate_item: dict[str, Any],
    baseline_item: Optional[dict[str, Any]],
    candidate_index: int,
) -> dict[str, Any]:
    return {
        "table_match_decision": ranked_row.get("decision", ""),
        "table_match_score": ranked_row.get("score", ""),
        "table_match_reason": ranked_row.get("reason", ""),
        "candidate_table_index": candidate_item.get("table_index", candidate_index),
        "baseline_table_index": baseline_item.get("table_index") if baseline_item else ranked_row.get("base_table_index", ""),
        "candidate_element_id": candidate_item.get("element_id", ""),
        "baseline_element_id": baseline_item.get("element_id", "") if baseline_item else "",
        "base_source_file": ranked_row.get("base_source_file", ""),
        "base_source_page": ranked_row.get("base_source_page", ""),
        "base_shape": ranked_row.get("base_shape", ""),
    }


def _pandas() -> Any:
    import pandas as pd

    return pd


def _rank_base_table_candidates() -> Any:
    from core.table_matcher import rank_base_table_candidates

    return rank_base_table_candidates


def _compare_cells_with_tolerance() -> Any:
    from core.align_compare import compare_cells_with_tolerance

    return compare_cells_with_tolerance
