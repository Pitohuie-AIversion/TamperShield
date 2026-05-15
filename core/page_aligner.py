"""
Minimal page-level aligner for the Document-first TamperShield pipeline.

This module pairs candidate document pages with baseline document pages. It
does not implement content comparison, table comparison, OCR, evidence
indexing, report generation, or the main pipeline.
"""

from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib
import re
from typing import Any, Literal, Optional

from core.document_models import DocumentElement, DocumentPage


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


@dataclass(frozen=True)
class PageFingerprint:
    normalized_text: str
    text_signature: str
    token_set: set[str]
    heading_candidates: tuple[str, ...]
    paragraph_count: int
    table_count: int
    image_count: int
    element_type_counts: dict[str, int]
    table_text_signature: str
    table_text: str
    image_count_signature: str
    page_text_length: int
    page_number: int


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
    """Compute deterministic multi-factor page similarity."""
    return page_similarity_details(candidate_page, baseline_page)["match_score"]


def page_similarity_details(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_index: Optional[int] = None,
    baseline_index: Optional[int] = None,
) -> dict[str, Any]:
    """Return a traceable multi-factor page match score."""
    candidate_fingerprint = build_page_fingerprint(candidate_page)
    baseline_fingerprint = build_page_fingerprint(baseline_page)

    text_score = text_similarity(
        candidate_fingerprint.normalized_text,
        baseline_fingerprint.normalized_text,
    )
    token_score = _jaccard_similarity(
        candidate_fingerprint.token_set,
        baseline_fingerprint.token_set,
    )
    structure_score = _element_structure_similarity(
        candidate_fingerprint.element_type_counts,
        baseline_fingerprint.element_type_counts,
    )
    table_score = _count_similarity(
        candidate_fingerprint.table_count,
        baseline_fingerprint.table_count,
    )
    image_score = _count_similarity(
        candidate_fingerprint.image_count,
        baseline_fingerprint.image_count,
    )
    table_text_score = text_similarity(
        candidate_fingerprint.table_text,
        baseline_fingerprint.table_text,
    )
    page_distance_penalty = _page_distance_penalty(candidate_index, baseline_index)

    raw_score = (
        0.45 * text_score
        + 0.20 * token_score
        + 0.15 * structure_score
        + 0.05 * table_score
        + 0.05 * image_score
        + 0.10 * table_text_score
        - page_distance_penalty
    )
    match_score = _clamp_score(raw_score)

    return {
        "match_score": match_score,
        "text_score": text_score,
        "token_score": token_score,
        "structure_score": structure_score,
        "table_score": table_score,
        "image_score": image_score,
        "table_text_score": table_text_score,
        "page_distance_penalty": page_distance_penalty,
        "alignment_method": "multi_factor_fingerprint",
        "candidate_fingerprint": _fingerprint_summary(candidate_fingerprint),
        "baseline_fingerprint": _fingerprint_summary(baseline_fingerprint),
    }


def build_page_fingerprint(page: DocumentPage) -> PageFingerprint:
    """Build a deterministic structural fingerprint for one document page."""
    normalized_text = normalize_page_text(page)
    element_type_counts = Counter(element.element_type for element in page.elements)
    table_text = _table_text(page)

    return PageFingerprint(
        normalized_text=normalized_text,
        text_signature=_short_hash(normalized_text),
        token_set=set(_tokens(normalized_text)),
        heading_candidates=tuple(_heading_candidates(page, normalized_text)),
        paragraph_count=element_type_counts["paragraph"],
        table_count=element_type_counts["table"],
        image_count=element_type_counts["image"],
        element_type_counts=dict(element_type_counts),
        table_text_signature=_short_hash(table_text),
        table_text=table_text,
        image_count_signature=f"image_count:{element_type_counts['image']}",
        page_text_length=len(normalized_text),
        page_number=page.page_number,
    )


def _is_forward_sequence_match(
    best_index: int,
    expected_index: int,
) -> bool:
    """Return True when the best match keeps moving forward in baseline order."""
    return best_index >= expected_index


def align_pages(
    candidate_pages: list[DocumentPage],
    baseline_pages: list[DocumentPage],
    match_threshold: float = 0.75,
    low_confidence_threshold: float = 0.45,
    search_window: int = 2,
    adaptive_search: bool = True,
    expanded_search_window: Optional[int] = None,
) -> list[PageAlignment]:
    """Align pages in sequence with multi-factor page fingerprints."""
    alignments: list[PageAlignment] = []
    matched_baseline_indexes: set[int] = set()
    baseline_cursor = 0

    for candidate_index, candidate_page in enumerate(candidate_pages):
        best_index, best_score, score_details, search_metadata = _find_best_baseline_match(
            candidate_page=candidate_page,
            candidate_index=candidate_index,
            baseline_pages=baseline_pages,
            baseline_cursor=baseline_cursor,
            search_window=search_window,
            matched_baseline_indexes=matched_baseline_indexes,
            low_confidence_threshold=low_confidence_threshold,
            adaptive_search=adaptive_search,
            expanded_search_window=expanded_search_window,
        )

        if best_index is None or best_score < low_confidence_threshold:
            metadata = {
                "candidate_index": candidate_index,
                "candidate_page_number": candidate_page.page_number,
                "baseline_cursor": baseline_cursor,
                "search_window": search_window,
                "status_semantic": "inserted_in_candidate",
            }
            metadata.update(search_metadata)
            metadata.update(score_details)
            alignments.append(
                PageAlignment(
                    candidate_page=candidate_page,
                    baseline_page=None,
                    status="candidate_added",
                    score=best_score,
                    reason="No baseline page in the search window reached the low confidence threshold.",
                    metadata=metadata,
                )
            )
            continue

        baseline_page = baseline_pages[best_index]
        matched_baseline_indexes.add(best_index)

        expected_index = baseline_cursor
        forward_baseline_skip = max(0, best_index - expected_index)
        is_forward_sequence_match = _is_forward_sequence_match(
            best_index=best_index,
            expected_index=expected_index,
        )
        if best_score >= match_threshold:
            if best_index == expected_index:
                status: AlignmentStatus = "matched"
                reason = "Best baseline page matched the expected sequence position."
                status_semantic = "matched"
            elif is_forward_sequence_match:
                status = "matched"
                reason = "Best baseline page matched a forward sequence position after skipped baseline pages."
                status_semantic = "matched"
            else:
                status = "possible_reordered"
                reason = "Best baseline page was before the expected sequence position and may indicate reordering."
                status_semantic = "possible_moved_page"
        else:
            status = "low_confidence"
            reason = "Best baseline page only reached the low confidence threshold."
            status_semantic = "low_confidence_match"

        metadata = {
            "candidate_index": candidate_index,
            "baseline_index": best_index,
            "expected_baseline_index": expected_index,
            "candidate_page_number": candidate_page.page_number,
            "baseline_page_number": baseline_page.page_number,
            "search_window": search_window,
            "forward_baseline_skip": forward_baseline_skip,
            "is_forward_sequence_match": is_forward_sequence_match,
            "status_semantic": status_semantic,
        }
        metadata.update(search_metadata)
        metadata.update(score_details)

        alignments.append(
            PageAlignment(
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                status=status,
                score=best_score,
                reason=reason,
                metadata=metadata,
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
                    "status_semantic": "missing_in_candidate",
                    "alignment_method": "multi_factor_fingerprint",
                    "baseline_fingerprint": _fingerprint_summary(
                        build_page_fingerprint(baseline_page)
                    ),
                },
            )
        )

    return alignments


def _find_best_baseline_match(
    candidate_page: DocumentPage,
    candidate_index: int,
    baseline_pages: list[DocumentPage],
    baseline_cursor: int,
    search_window: int,
    matched_baseline_indexes: set[int],
    low_confidence_threshold: float,
    adaptive_search: bool,
    expanded_search_window: Optional[int],
) -> tuple[Optional[int], float, dict[str, Any], dict[str, Any]]:
    if not baseline_pages:
        return None, 0.0, _empty_score_details(candidate_page), {
            "effective_search_window": 0,
            "adaptive_search_used": False,
        }

    local_window = max(0, search_window)
    best_index, best_score, score_details = _search_baseline_window(
        candidate_page=candidate_page,
        candidate_index=candidate_index,
        baseline_pages=baseline_pages,
        baseline_cursor=baseline_cursor,
        search_window=local_window,
        matched_baseline_indexes=matched_baseline_indexes,
    )

    adaptive_search_used = False
    effective_search_window = local_window
    if adaptive_search and best_score < low_confidence_threshold:
        expanded_window = expanded_search_window
        if expanded_window is None:
            expanded_window = max(local_window * 3, local_window + 3)
        expanded_window = min(max(0, expanded_window), len(baseline_pages))
        if expanded_window > local_window:
            expanded_index, expanded_score, expanded_details = _search_baseline_window(
                candidate_page=candidate_page,
                candidate_index=candidate_index,
                baseline_pages=baseline_pages,
                baseline_cursor=baseline_cursor,
                search_window=expanded_window,
                matched_baseline_indexes=matched_baseline_indexes,
            )
            if expanded_index is not None and (
                best_index is None or expanded_score > best_score
            ):
                best_index = expanded_index
                best_score = expanded_score
                score_details = expanded_details
                adaptive_search_used = True
                effective_search_window = expanded_window

    search_metadata = {
        "effective_search_window": effective_search_window,
        "adaptive_search": adaptive_search,
        "adaptive_search_used": adaptive_search_used,
    }
    return best_index, best_score, score_details, search_metadata


def _search_baseline_window(
    candidate_page: DocumentPage,
    candidate_index: int,
    baseline_pages: list[DocumentPage],
    baseline_cursor: int,
    search_window: int,
    matched_baseline_indexes: set[int],
) -> tuple[Optional[int], float, dict[str, Any]]:
    start = max(0, baseline_cursor - search_window)
    end = min(len(baseline_pages), baseline_cursor + search_window + 1)

    best_index: Optional[int] = None
    best_score = 0.0
    best_details = _empty_score_details(candidate_page)
    for baseline_index in range(start, end):
        if baseline_index in matched_baseline_indexes:
            continue

        details = page_similarity_details(
            candidate_page,
            baseline_pages[baseline_index],
            candidate_index=candidate_index,
            baseline_index=baseline_index,
        )
        score = details["match_score"]
        if best_index is None or score > best_score:
            best_index = baseline_index
            best_score = score
            best_details = details

    return best_index, best_score, best_details


def _empty_score_details(candidate_page: DocumentPage) -> dict[str, Any]:
    return {
        "match_score": 0.0,
        "text_score": 0.0,
        "token_score": 0.0,
        "structure_score": 0.0,
        "table_score": 0.0,
        "image_score": 0.0,
        "table_text_score": 0.0,
        "page_distance_penalty": 0.0,
        "alignment_method": "multi_factor_fingerprint",
        "candidate_fingerprint": _fingerprint_summary(
            build_page_fingerprint(candidate_page)
        ),
    }


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _heading_candidates(page: DocumentPage, normalized_text: str) -> list[str]:
    headings = [
        element.text.strip()
        for element in page.elements
        if element.element_type in {"title", "header"} and element.text.strip()
    ]
    if headings:
        return headings[:5]

    lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
    if lines:
        return [line[:120] for line in lines[:3]]

    if normalized_text:
        return [normalized_text[:120]]

    return []


def _table_text(page: DocumentPage) -> str:
    parts: list[str] = []
    for element in page.elements:
        if element.element_type != "table":
            continue
        text = element.text.strip()
        if text:
            parts.append(text)
            continue
        parts.extend(_table_metadata_text(element))
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _table_metadata_text(element: DocumentElement) -> list[str]:
    cells = element.metadata.get("cells")
    if not isinstance(cells, list):
        return []

    parts: list[str] = []
    for row in cells:
        if not isinstance(row, list):
            continue
        for cell in row:
            cell_text = str(cell).strip()
            if cell_text:
                parts.append(cell_text)
    return parts


def _jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _element_structure_similarity(
    candidate_counts: dict[str, int],
    baseline_counts: dict[str, int],
) -> float:
    element_types = set(candidate_counts) | set(baseline_counts)
    if not element_types:
        return 1.0

    similarities = [
        _count_similarity(
            candidate_counts.get(element_type, 0),
            baseline_counts.get(element_type, 0),
        )
        for element_type in element_types
    ]
    return sum(similarities) / len(similarities)


def _count_similarity(candidate_count: int, baseline_count: int) -> float:
    if candidate_count == baseline_count == 0:
        return 1.0
    denominator = max(candidate_count, baseline_count)
    if denominator == 0:
        return 0.0
    return 1.0 - (abs(candidate_count - baseline_count) / denominator)


def _page_distance_penalty(
    candidate_index: Optional[int],
    baseline_index: Optional[int],
) -> float:
    if candidate_index is None or baseline_index is None:
        return 0.0
    distance = abs(candidate_index - baseline_index)
    return min(0.15, distance * 0.03)


def _fingerprint_summary(fingerprint: PageFingerprint) -> dict[str, Any]:
    return {
        "text_signature": fingerprint.text_signature,
        "token_count": len(fingerprint.token_set),
        "heading_candidates": list(fingerprint.heading_candidates),
        "paragraph_count": fingerprint.paragraph_count,
        "table_count": fingerprint.table_count,
        "image_count": fingerprint.image_count,
        "element_type_counts": fingerprint.element_type_counts,
        "table_text_signature": fingerprint.table_text_signature,
        "image_count_signature": fingerprint.image_count_signature,
        "page_text_length": fingerprint.page_text_length,
        "page_number": fingerprint.page_number,
    }


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _clamp_score(score: float) -> float:
    return max(0.0, min(1.0, score))
