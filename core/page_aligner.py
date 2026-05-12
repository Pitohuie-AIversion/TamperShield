"""
Minimal page-level aligner for the Document-first TamperShield pipeline.

This module pairs candidate document pages with baseline document pages. It
does not implement content comparison, table comparison, OCR, evidence
indexing, report generation, or the main pipeline.
"""

from dataclasses import dataclass, field
from difflib import SequenceMatcher
import re
from typing import Any, Literal, Optional

from core.document_models import DocumentPage


AlignmentStatus = Literal[
    "matched",
    "candidate_added",
    "baseline_deleted",
    "possible_reordered",
    "low_confidence",
]


@dataclass
class PageAlignment:
    candidate_page: Optional[DocumentPage]
    baseline_page: Optional[DocumentPage]
    status: AlignmentStatus
    score: float
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def normalize_page_text(page: DocumentPage) -> str:
    """Return deterministic normalized page text for page-level alignment."""
    text = page.plain_text
    if not text:
        text = "\n".join(
            element.text for element in page.elements if element.text
        )

    return re.sub(r"\s+", " ", text).strip()


def text_similarity(a: str, b: str) -> float:
    """Compare two strings with standard-library edit similarity."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    return SequenceMatcher(None, a, b).ratio()


def page_similarity(candidate_page: DocumentPage, baseline_page: DocumentPage) -> float:
    """Compute deterministic text-only page similarity."""
    candidate_text = normalize_page_text(candidate_page)
    baseline_text = normalize_page_text(baseline_page)
    return text_similarity(candidate_text, baseline_text)


def align_pages(
    candidate_pages: list[DocumentPage],
    baseline_pages: list[DocumentPage],
    match_threshold: float = 0.75,
    low_confidence_threshold: float = 0.45,
    search_window: int = 2,
) -> list[PageAlignment]:
    """Align pages in sequence with a small local search window."""
    alignments: list[PageAlignment] = []
    matched_baseline_indexes: set[int] = set()
    baseline_cursor = 0

    for candidate_index, candidate_page in enumerate(candidate_pages):
        best_index, best_score = _find_best_baseline_match(
            candidate_page=candidate_page,
            baseline_pages=baseline_pages,
            baseline_cursor=baseline_cursor,
            search_window=search_window,
            matched_baseline_indexes=matched_baseline_indexes,
        )

        if best_index is None or best_score < low_confidence_threshold:
            alignments.append(
                PageAlignment(
                    candidate_page=candidate_page,
                    baseline_page=None,
                    status="candidate_added",
                    score=best_score,
                    reason="No baseline page in the search window reached the low confidence threshold.",
                    metadata={
                        "candidate_index": candidate_index,
                        "candidate_page_number": candidate_page.page_number,
                        "baseline_cursor": baseline_cursor,
                        "search_window": search_window,
                    },
                )
            )
            continue

        baseline_page = baseline_pages[best_index]
        matched_baseline_indexes.add(best_index)

        expected_index = baseline_cursor
        if best_score >= match_threshold:
            if best_index == expected_index:
                status: AlignmentStatus = "matched"
                reason = "Best baseline page matched the expected sequence position."
            else:
                status = "possible_reordered"
                reason = "Best baseline page was outside the expected sequence position."
        else:
            status = "low_confidence"
            reason = "Best baseline page only reached the low confidence threshold."

        alignments.append(
            PageAlignment(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                status=status,
                score=best_score,
                reason=reason,
                metadata={
                    "candidate_index": candidate_index,
                    "baseline_index": best_index,
                    "expected_baseline_index": expected_index,
                    "candidate_page_number": candidate_page.page_number,
                    "baseline_page_number": baseline_page.page_number,
                    "search_window": search_window,
                },
            )
        )

        if best_index >= baseline_cursor:
            baseline_cursor = best_index + 1

    for baseline_index, baseline_page in enumerate(baseline_pages):
        if baseline_index in matched_baseline_indexes:
            continue

        alignments.append(
            PageAlignment(
                candidate_page=None,
                baseline_page=baseline_page,
                status="baseline_deleted",
                score=0.0,
                reason="Baseline page was not matched by any candidate page.",
                metadata={
                    "baseline_index": baseline_index,
                    "baseline_page_number": baseline_page.page_number,
                },
            )
        )

    return alignments


def _find_best_baseline_match(
    candidate_page: DocumentPage,
    baseline_pages: list[DocumentPage],
    baseline_cursor: int,
    search_window: int,
    matched_baseline_indexes: set[int],
) -> tuple[Optional[int], float]:
    if not baseline_pages:
        return None, 0.0

    window = max(0, search_window)
    start = max(0, baseline_cursor - window)
    end = min(len(baseline_pages), baseline_cursor + window + 1)

    best_index: Optional[int] = None
    best_score = 0.0
    for baseline_index in range(start, end):
        if baseline_index in matched_baseline_indexes:
            continue

        score = page_similarity(candidate_page, baseline_pages[baseline_index])
        if best_index is None or score > best_score:
            best_index = baseline_index
            best_score = score

    return best_index, best_score
