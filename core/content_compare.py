"""
Minimal page and element content comparison for TamperShield.

This module detects page-level and element-level differences from page
alignments. It does not perform table cell comparison, table matching, OCR,
report generation, evidence storage, or main pipeline orchestration.
"""

from collections import Counter
from difflib import SequenceMatcher
import re
from typing import Callable, Optional

from core.document_models import BoundingBox, Difference, DocumentElement, DocumentPage
from core.page_aligner import PageAlignment


ELEMENT_TYPES_TO_COUNT = (
    "paragraph",
    "table",
    "image",
    "signature",
    "header",
    "footer",
)

TEXT_PREVIEW_LENGTH = 120
ELEMENT_TYPES_FOR_BLOCK_COMPARE = ("paragraph", "table", "image", "unknown")
PARAGRAPH_UNCHANGED_THRESHOLD = 0.98
PARAGRAPH_MODIFIED_THRESHOLD = 0.65
TABLE_UNCHANGED_THRESHOLD = 0.95
TABLE_MODIFIED_THRESHOLD = 0.55
IMAGE_UNCHANGED_THRESHOLD = 0.90
IMAGE_MODIFIED_THRESHOLD = 0.45


def normalize_text(text: str) -> str:
    """Normalize whitespace without semantic rewriting."""
    return re.sub(r"\s+", " ", text).strip()


def text_similarity(a: str, b: str) -> float:
    """Return deterministic string similarity using SequenceMatcher."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    return SequenceMatcher(None, a, b).ratio()


def compare_page_text(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    similarity_threshold: float = 0.98,
) -> list[Difference]:
    """Compare normalized page text and return a page-level text difference."""
    candidate_text = _page_text(candidate_page)
    baseline_text = _page_text(baseline_page)
    similarity = text_similarity(candidate_text, baseline_text)

    if similarity >= similarity_threshold:
        return []

    return [
        Difference(
            diff_type="text_modified",
            severity="medium",
            candidate_page=candidate_page.page_number,
            baseline_page=baseline_page.page_number,
            message=(
                f"Page text similarity {similarity:.4f} is below "
                f"threshold {similarity_threshold:.4f}."
            ),
            metadata={
                "similarity": similarity,
                "threshold": similarity_threshold,
                "candidate_text_preview": _preview(candidate_text),
                "baseline_text_preview": _preview(baseline_text),
            },
        )
    ]


def compare_blank_status(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> list[Difference]:
    """Detect whether a page changed between blank and non-blank state."""
    candidate_is_blank = candidate_page.is_blank()
    baseline_is_blank = baseline_page.is_blank()

    if candidate_is_blank == baseline_is_blank:
        return []

    return [
        Difference(
            diff_type="layout_changed",
            severity="high",
            candidate_page=candidate_page.page_number,
            baseline_page=baseline_page.page_number,
            message="Blank status changed between candidate and baseline page.",
            metadata={
                "candidate_is_blank": candidate_is_blank,
                "baseline_is_blank": baseline_is_blank,
            },
        )
    ]


def compare_element_counts(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> list[Difference]:
    """Compare counts of key document element types on aligned pages."""
    candidate_counts = _element_type_counts(candidate_page)
    baseline_counts = _element_type_counts(baseline_page)
    differences: list[Difference] = []

    for element_type in ELEMENT_TYPES_TO_COUNT:
        candidate_count = candidate_counts[element_type]
        baseline_count = baseline_counts[element_type]
        if candidate_count == baseline_count:
            continue

        diff_type, severity = _element_count_diff_type(
            element_type=element_type,
            candidate_count=candidate_count,
            baseline_count=baseline_count,
        )
        metadata = {
            "element_type": element_type,
            "candidate_count": candidate_count,
            "baseline_count": baseline_count,
        }
        if element_type == "table":
            metadata["requires_table_compare"] = True

        differences.append(
            Difference(
                diff_type=diff_type,
                severity=severity,
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                message=(
                    f"{element_type} element count changed: candidate="
                    f"{candidate_count}, baseline={baseline_count}."
                ),
                metadata=metadata,
            )
        )

    return differences


def detect_table_compare_need(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> list[Difference]:
    """Flag aligned pages that contain tables for later table_compare work."""
    candidate_table_count = len(candidate_page.get_elements_by_type("table"))
    baseline_table_count = len(baseline_page.get_elements_by_type("table"))

    if candidate_table_count == 0 and baseline_table_count == 0:
        return []

    return [
        Difference(
            diff_type="unknown",
            severity="low",
            candidate_page=candidate_page.page_number,
            baseline_page=baseline_page.page_number,
            message="Table elements detected; table_compare may be required.",
            metadata={
                "requires_table_compare": True,
                "candidate_table_count": candidate_table_count,
                "baseline_table_count": baseline_table_count,
            },
        )
    ]


def compare_page(
    alignment: PageAlignment,
    page_text_similarity_threshold: float = 0.98,
    enable_element_compare: bool = True,
) -> list[Difference]:
    """Compare one aligned page pair and return detected differences."""
    candidate_page = alignment.candidate_page
    baseline_page = alignment.baseline_page

    if alignment.status == "candidate_added" and candidate_page is not None:
        metadata = _alignment_metadata(alignment)
        metadata.update(_page_profile(candidate_page))
        metadata.update(_classify_unmatched_page(candidate_page))
        return [
            Difference(
                diff_type="page_added",
                severity="high",
                candidate_page=candidate_page.page_number,
                baseline_page=None,
                message=(
                    "Candidate document contains an added page; see "
                    "page_issue_category metadata for review context."
                ),
                metadata=metadata,
            )
        ]

    if alignment.status == "baseline_deleted" and baseline_page is not None:
        metadata = _alignment_metadata(alignment)
        metadata.update(_page_profile(baseline_page))
        metadata.update(_classify_unmatched_page(baseline_page))
        return [
            Difference(
                diff_type="page_deleted",
                severity="high",
                candidate_page=None,
                baseline_page=baseline_page.page_number,
                message=(
                    "Baseline page is missing from the candidate document; see "
                    "page_issue_category metadata for review context."
                ),
                metadata=metadata,
            )
        ]

    if alignment.status == "possible_reordered":
        return [
            Difference(
                diff_type="page_reordered",
                severity="high",
                candidate_page=_page_number(candidate_page),
                baseline_page=_page_number(baseline_page),
                message="Page may be reordered relative to the baseline document.",
                metadata=_alignment_metadata(alignment),
            )
        ]

    if alignment.status == "low_confidence":
        return [
            Difference(
                diff_type="layout_changed",
                severity="medium",
                candidate_page=_page_number(candidate_page),
                baseline_page=_page_number(baseline_page),
                message="Page alignment confidence is low and needs review.",
                metadata=_alignment_metadata(alignment),
            )
        ]

    if alignment.status != "matched" or candidate_page is None or baseline_page is None:
        return []

    differences: list[Difference] = []
    differences.extend(compare_blank_status(candidate_page, baseline_page))
    differences.extend(
        compare_page_text(
            candidate_page=candidate_page,
            baseline_page=baseline_page,
            similarity_threshold=page_text_similarity_threshold,
        )
    )
    differences.extend(compare_layout_structure(candidate_page, baseline_page))
    if enable_element_compare:
        differences.extend(compare_document_elements(candidate_page, baseline_page))
    return differences


def compare_aligned_pages(
    alignments: list[PageAlignment],
    page_text_similarity_threshold: float = 0.98,
    enable_element_compare: bool = True,
) -> list[Difference]:
    """Compare all page alignments and return a flat list of differences."""
    differences: list[Difference] = []
    for alignment in alignments:
        differences.extend(
            compare_page(
                alignment=alignment,
                page_text_similarity_threshold=page_text_similarity_threshold,
                enable_element_compare=enable_element_compare,
            )
        )
    return differences


def compare_layout_structure(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> list[Difference]:
    """Emit a page-level layout summary when element type counts changed."""
    summary = _layout_summary(candidate_page, baseline_page)
    if (
        summary["paragraph_count_delta"] == 0
        and summary["table_count_delta"] == 0
        and summary["image_count_delta"] == 0
    ):
        return []

    severity = "high" if summary["table_count_delta"] or summary["image_count_delta"] else "medium"
    return [
        Difference(
            diff_type="layout_structure_changed",
            severity=severity,
            candidate_page=candidate_page.page_number,
            baseline_page=baseline_page.page_number,
            message="Page element structure changed between candidate and baseline page.",
            metadata={
                **summary,
                "comparison_method": "element_type_count_summary",
            },
        )
    ]


def compare_document_elements(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> list[Difference]:
    """Compare paragraph, table, image, and unknown elements at block level."""
    candidate_groups = _group_elements_by_type(candidate_page)
    baseline_groups = _group_elements_by_type(baseline_page)

    differences: list[Difference] = []
    differences.extend(
        compare_paragraph_elements(
            candidate_page,
            baseline_page,
            candidate_groups["paragraph"],
            baseline_groups["paragraph"],
        )
    )
    differences.extend(
        compare_table_elements(
            candidate_page,
            baseline_page,
            candidate_groups["table"],
            baseline_groups["table"],
        )
    )
    differences.extend(
        compare_image_elements(
            candidate_page,
            baseline_page,
            candidate_groups["image"],
            baseline_groups["image"],
        )
    )
    differences.extend(
        compare_unknown_elements(
            candidate_page,
            baseline_page,
            candidate_groups["unknown"],
            baseline_groups["unknown"],
        )
    )
    return differences


def compare_paragraph_elements(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_elements: list[DocumentElement],
    baseline_elements: list[DocumentElement],
) -> list[Difference]:
    """Compare paragraph elements with deterministic block text similarity."""
    matches, added, deleted = _match_elements(
        candidate_elements,
        baseline_elements,
        similarity_func=_paragraph_similarity,
        minimum_match_score=0.01,
    )

    differences: list[Difference] = []
    for candidate_element, baseline_element, similarity in matches:
        metadata = _element_pair_metadata(
            candidate_element=candidate_element,
            baseline_element=baseline_element,
            element_type="paragraph",
            comparison_method="paragraph_block_similarity",
        )
        metadata["element_similarity"] = similarity
        metadata["candidate_text_preview"] = _preview(_element_text(candidate_element))
        metadata["baseline_text_preview"] = _preview(_element_text(baseline_element))

        if similarity >= PARAGRAPH_UNCHANGED_THRESHOLD:
            continue
        if similarity >= PARAGRAPH_MODIFIED_THRESHOLD:
            differences.append(
                Difference(
                    diff_type="paragraph_modified",
                    severity="medium",
                    candidate_page=candidate_page.page_number,
                    baseline_page=baseline_page.page_number,
                    candidate_element_id=candidate_element.element_id,
                    baseline_element_id=baseline_element.element_id,
                    location=candidate_element.bbox,
                    message="Paragraph block text changed between aligned pages.",
                    metadata=metadata,
                )
            )
            continue

        metadata["requires_manual_review"] = True
        differences.append(
            Difference(
                diff_type="low_confidence_element_match",
                severity="medium",
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                candidate_element_id=candidate_element.element_id,
                baseline_element_id=baseline_element.element_id,
                location=candidate_element.bbox,
                message="Paragraph block match is low confidence and needs review.",
                metadata=metadata,
            )
        )

    for candidate_element in added:
        differences.append(
            _single_element_difference(
                diff_type="paragraph_added",
                severity="medium",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=candidate_element,
                baseline_element=None,
                message="Paragraph element exists only in candidate page.",
                comparison_method="paragraph_block_similarity",
            )
        )

    for baseline_element in deleted:
        differences.append(
            _single_element_difference(
                diff_type="paragraph_deleted",
                severity="medium",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=None,
                baseline_element=baseline_element,
                message="Paragraph element from baseline page is missing in candidate page.",
                comparison_method="paragraph_block_similarity",
            )
        )

    return differences


def compare_table_elements(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_elements: list[DocumentElement],
    baseline_elements: list[DocumentElement],
) -> list[Difference]:
    """Compare table elements at block level without cell-level inspection."""
    matches, added, deleted = _match_elements(
        candidate_elements,
        baseline_elements,
        similarity_func=_table_similarity,
        minimum_match_score=0.01,
    )

    differences: list[Difference] = []
    for candidate_element, baseline_element, similarity in matches:
        metadata = _element_pair_metadata(
            candidate_element=candidate_element,
            baseline_element=baseline_element,
            element_type="table",
            comparison_method="table_block_similarity",
        )
        metadata.update(_table_pair_metadata(candidate_element, baseline_element))
        metadata["table_similarity"] = similarity
        metadata["requires_table_compare"] = similarity < TABLE_UNCHANGED_THRESHOLD

        if similarity >= TABLE_UNCHANGED_THRESHOLD:
            continue
        if similarity >= TABLE_MODIFIED_THRESHOLD:
            differences.append(
                Difference(
                    diff_type="table_modified",
                    severity="high",
                    candidate_page=candidate_page.page_number,
                    baseline_page=baseline_page.page_number,
                    candidate_element_id=candidate_element.element_id,
                    baseline_element_id=baseline_element.element_id,
                    location=candidate_element.bbox,
                    message="Table block text or structure changed between aligned pages.",
                    metadata=metadata,
                )
            )
            continue

        metadata["requires_manual_review"] = True
        differences.append(
            Difference(
                diff_type="low_confidence_element_match",
                severity="high",
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                candidate_element_id=candidate_element.element_id,
                baseline_element_id=baseline_element.element_id,
                location=candidate_element.bbox,
                message="Table block match is low confidence and needs review.",
                metadata=metadata,
            )
        )

    for candidate_element in added:
        differences.append(
            _single_element_difference(
                diff_type="table_added",
                severity="high",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=candidate_element,
                baseline_element=None,
                message="Table element exists only in candidate page.",
                comparison_method="table_block_similarity",
                extra_metadata={
                    "requires_table_compare": True,
                    **_table_metadata(candidate_element, prefix="candidate"),
                },
            )
        )

    for baseline_element in deleted:
        differences.append(
            _single_element_difference(
                diff_type="table_deleted",
                severity="high",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=None,
                baseline_element=baseline_element,
                message="Table element from baseline page is missing in candidate page.",
                comparison_method="table_block_similarity",
                extra_metadata={
                    "requires_table_compare": True,
                    **_table_metadata(baseline_element, prefix="baseline"),
                },
            )
        )

    return differences


def compare_image_elements(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_elements: list[DocumentElement],
    baseline_elements: list[DocumentElement],
) -> list[Difference]:
    """Compare image elements with bbox and parser metadata only."""
    matches, added, deleted = _match_elements(
        candidate_elements,
        baseline_elements,
        similarity_func=_image_similarity,
        minimum_match_score=0.01,
    )

    differences: list[Difference] = []
    for candidate_element, baseline_element, similarity in matches:
        metadata = _element_pair_metadata(
            candidate_element=candidate_element,
            baseline_element=baseline_element,
            element_type="image",
            comparison_method="image_block_metadata_similarity",
        )
        metadata.update(_image_pair_metadata(candidate_element, baseline_element))
        metadata["image_similarity"] = similarity

        if similarity >= IMAGE_UNCHANGED_THRESHOLD:
            continue
        if similarity >= IMAGE_MODIFIED_THRESHOLD:
            differences.append(
                Difference(
                    diff_type="image_modified_candidate",
                    severity="high",
                    candidate_page=candidate_page.page_number,
                    baseline_page=baseline_page.page_number,
                    candidate_element_id=candidate_element.element_id,
                    baseline_element_id=baseline_element.element_id,
                    location=candidate_element.bbox,
                    message="Image block bbox or parser metadata changed between aligned pages.",
                    metadata=metadata,
                )
            )
            continue

        metadata["requires_manual_review"] = True
        differences.append(
            Difference(
                diff_type="low_confidence_element_match",
                severity="high",
                candidate_page=candidate_page.page_number,
                baseline_page=baseline_page.page_number,
                candidate_element_id=candidate_element.element_id,
                baseline_element_id=baseline_element.element_id,
                location=candidate_element.bbox,
                message="Image block match is low confidence and needs review.",
                metadata=metadata,
            )
        )

    for candidate_element in added:
        differences.append(
            _single_element_difference(
                diff_type="image_added",
                severity="high",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=candidate_element,
                baseline_element=None,
                message="Image element exists only in candidate page.",
                comparison_method="image_block_metadata_similarity",
                extra_metadata=_image_metadata(candidate_element, prefix="candidate"),
            )
        )

    for baseline_element in deleted:
        differences.append(
            _single_element_difference(
                diff_type="image_deleted",
                severity="high",
                candidate_page=candidate_page,
                baseline_page=baseline_page,
                candidate_element=None,
                baseline_element=baseline_element,
                message="Image element from baseline page is missing in candidate page.",
                comparison_method="image_block_metadata_similarity",
                extra_metadata=_image_metadata(baseline_element, prefix="baseline"),
            )
        )

    return differences


def compare_unknown_elements(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_elements: list[DocumentElement],
    baseline_elements: list[DocumentElement],
) -> list[Difference]:
    """Preserve unknown element count changes for manual review."""
    if len(candidate_elements) == len(baseline_elements):
        return []

    return [
        Difference(
            diff_type="layout_structure_changed",
            severity="medium",
            candidate_page=candidate_page.page_number,
            baseline_page=baseline_page.page_number,
            message="Unknown element count changed between aligned pages.",
            metadata={
                "element_type": "unknown",
                "candidate_count": len(candidate_elements),
                "baseline_count": len(baseline_elements),
                "comparison_method": "unknown_element_count_summary",
                "requires_manual_review": True,
            },
        )
    ]


def _page_text(page: DocumentPage) -> str:
    text = page.plain_text
    if not text:
        text = "\n".join(
            element.text for element in page.elements if element.text
        )
    return normalize_text(text)


def _group_elements_by_type(page: DocumentPage) -> dict[str, list[DocumentElement]]:
    groups = {element_type: [] for element_type in ELEMENT_TYPES_FOR_BLOCK_COMPARE}
    for element in page.elements:
        if element.element_type in groups:
            groups[element.element_type].append(element)
            continue
        groups["unknown"].append(element)
    return groups


def _match_elements(
    candidate_elements: list[DocumentElement],
    baseline_elements: list[DocumentElement],
    similarity_func: Callable[[DocumentElement, DocumentElement], float],
    minimum_match_score: float,
) -> tuple[
    list[tuple[DocumentElement, DocumentElement, float]],
    list[DocumentElement],
    list[DocumentElement],
]:
    candidates = list(candidate_elements)
    baselines = list(baseline_elements)
    possible_matches: list[tuple[float, int, int]] = []

    for candidate_index, candidate_element in enumerate(candidates):
        for baseline_index, baseline_element in enumerate(baselines):
            score = similarity_func(candidate_element, baseline_element)
            if score >= minimum_match_score:
                possible_matches.append((score, candidate_index, baseline_index))

    possible_matches.sort(reverse=True, key=lambda item: item[0])
    matched_candidate_indexes: set[int] = set()
    matched_baseline_indexes: set[int] = set()
    matches: list[tuple[DocumentElement, DocumentElement, float]] = []

    for score, candidate_index, baseline_index in possible_matches:
        if candidate_index in matched_candidate_indexes:
            continue
        if baseline_index in matched_baseline_indexes:
            continue

        matched_candidate_indexes.add(candidate_index)
        matched_baseline_indexes.add(baseline_index)
        matches.append((candidates[candidate_index], baselines[baseline_index], score))

    added = [
        element
        for index, element in enumerate(candidates)
        if index not in matched_candidate_indexes
    ]
    deleted = [
        element
        for index, element in enumerate(baselines)
        if index not in matched_baseline_indexes
    ]
    return matches, added, deleted


def _paragraph_similarity(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> float:
    return text_similarity(
        normalize_text(_element_text(candidate_element)),
        normalize_text(_element_text(baseline_element)),
    )


def _table_similarity(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> float:
    candidate_text = normalize_text(_element_text(candidate_element))
    baseline_text = normalize_text(_element_text(baseline_element))
    text_score = text_similarity(candidate_text, baseline_text)
    shape_score = _table_shape_similarity(candidate_element, baseline_element)
    detection_score = _metadata_value_similarity(
        candidate_element.metadata.get("detection_method"),
        baseline_element.metadata.get("detection_method"),
    )

    return (0.60 * text_score) + (0.30 * shape_score) + (0.10 * detection_score)


def _image_similarity(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> float:
    bbox_score = _bbox_similarity(candidate_element.bbox, baseline_element.bbox)
    size_score = _image_size_similarity(candidate_element, baseline_element)
    metadata_score = _metadata_value_similarity(
        candidate_element.metadata.get("extension"),
        baseline_element.metadata.get("extension"),
    )
    return (0.50 * bbox_score) + (0.40 * size_score) + (0.10 * metadata_score)


def _element_text(element: DocumentElement) -> str:
    if element.text:
        return element.text

    cells = element.metadata.get("cells")
    if isinstance(cells, list):
        parts: list[str] = []
        for row in cells:
            if not isinstance(row, list):
                continue
            parts.extend(str(cell).strip() for cell in row if str(cell).strip())
        return " ".join(parts)

    return ""


def _layout_summary(
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
) -> dict[str, object]:
    candidate_counts = _element_type_counts(candidate_page)
    baseline_counts = _element_type_counts(baseline_page)
    return {
        "candidate_element_type_counts": dict(candidate_counts),
        "baseline_element_type_counts": dict(baseline_counts),
        "paragraph_count_delta": candidate_counts["paragraph"] - baseline_counts["paragraph"],
        "table_count_delta": candidate_counts["table"] - baseline_counts["table"],
        "image_count_delta": candidate_counts["image"] - baseline_counts["image"],
    }


def _element_pair_metadata(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
    element_type: str,
    comparison_method: str,
) -> dict[str, object]:
    return {
        "candidate_element_id": candidate_element.element_id,
        "baseline_element_id": baseline_element.element_id,
        "candidate_bbox": _bbox_to_metadata(candidate_element.bbox),
        "baseline_bbox": _bbox_to_metadata(baseline_element.bbox),
        "candidate_page_number": candidate_element.page_number,
        "baseline_page_number": baseline_element.page_number,
        "element_type": element_type,
        "comparison_method": comparison_method,
    }


def _single_element_difference(
    diff_type: str,
    severity: str,
    candidate_page: DocumentPage,
    baseline_page: DocumentPage,
    candidate_element: Optional[DocumentElement],
    baseline_element: Optional[DocumentElement],
    message: str,
    comparison_method: str,
    extra_metadata: Optional[dict[str, object]] = None,
) -> Difference:
    element = candidate_element or baseline_element
    metadata: dict[str, object] = {
        "candidate_element_id": candidate_element.element_id if candidate_element else None,
        "baseline_element_id": baseline_element.element_id if baseline_element else None,
        "candidate_bbox": _bbox_to_metadata(candidate_element.bbox) if candidate_element else None,
        "baseline_bbox": _bbox_to_metadata(baseline_element.bbox) if baseline_element else None,
        "candidate_page_number": candidate_page.page_number,
        "baseline_page_number": baseline_page.page_number,
        "element_type": element.element_type if element else "",
        "comparison_method": comparison_method,
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    return Difference(
        diff_type=diff_type,
        severity=severity,
        candidate_page=candidate_page.page_number,
        baseline_page=baseline_page.page_number,
        candidate_element_id=candidate_element.element_id if candidate_element else None,
        baseline_element_id=baseline_element.element_id if baseline_element else None,
        location=candidate_element.bbox if candidate_element else None,
        message=message,
        metadata=metadata,
    )


def _table_pair_metadata(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> dict[str, object]:
    return {
        **_table_metadata(candidate_element, prefix="candidate"),
        **_table_metadata(baseline_element, prefix="baseline"),
        "table_index": candidate_element.metadata.get("table_index"),
    }


def _table_metadata(element: DocumentElement, prefix: str) -> dict[str, object]:
    return {
        f"{prefix}_table_index": element.metadata.get("table_index"),
        f"{prefix}_rows": element.metadata.get("rows"),
        f"{prefix}_cols": element.metadata.get("cols"),
        f"{prefix}_detection_method": element.metadata.get("detection_method"),
    }


def _image_pair_metadata(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> dict[str, object]:
    return {
        "image_index": candidate_element.metadata.get("image_index"),
        **_image_metadata(candidate_element, prefix="candidate"),
        **_image_metadata(baseline_element, prefix="baseline"),
    }


def _image_metadata(element: DocumentElement, prefix: str) -> dict[str, object]:
    return {
        f"{prefix}_image_metadata": {
            "image_index": element.metadata.get("image_index"),
            "width": element.metadata.get("width"),
            "height": element.metadata.get("height"),
            "extension": element.metadata.get("extension"),
            "detection_method": element.metadata.get("detection_method"),
        }
    }


def _table_shape_similarity(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> float:
    row_score = _count_similarity(
        _metadata_int(candidate_element.metadata.get("rows")),
        _metadata_int(baseline_element.metadata.get("rows")),
    )
    col_score = _count_similarity(
        _metadata_int(candidate_element.metadata.get("cols")),
        _metadata_int(baseline_element.metadata.get("cols")),
    )
    return (row_score + col_score) / 2


def _image_size_similarity(
    candidate_element: DocumentElement,
    baseline_element: DocumentElement,
) -> float:
    width_score = _count_similarity(
        _metadata_int(candidate_element.metadata.get("width")),
        _metadata_int(baseline_element.metadata.get("width")),
    )
    height_score = _count_similarity(
        _metadata_int(candidate_element.metadata.get("height")),
        _metadata_int(baseline_element.metadata.get("height")),
    )
    return (width_score + height_score) / 2


def _bbox_similarity(
    candidate_bbox: Optional[BoundingBox],
    baseline_bbox: Optional[BoundingBox],
) -> float:
    if candidate_bbox is None and baseline_bbox is None:
        return 1.0
    if candidate_bbox is None or baseline_bbox is None:
        return 0.5

    candidate_area = candidate_bbox.area()
    baseline_area = baseline_bbox.area()
    area_score = _float_ratio_similarity(candidate_area, baseline_area)
    width_score = _float_ratio_similarity(candidate_bbox.width(), baseline_bbox.width())
    height_score = _float_ratio_similarity(candidate_bbox.height(), baseline_bbox.height())
    center_score = _bbox_center_similarity(candidate_bbox, baseline_bbox)
    return (0.30 * area_score) + (0.20 * width_score) + (0.20 * height_score) + (0.30 * center_score)


def _bbox_center_similarity(candidate_bbox: BoundingBox, baseline_bbox: BoundingBox) -> float:
    candidate_center_x = (candidate_bbox.x0 + candidate_bbox.x1) / 2
    candidate_center_y = (candidate_bbox.y0 + candidate_bbox.y1) / 2
    baseline_center_x = (baseline_bbox.x0 + baseline_bbox.x1) / 2
    baseline_center_y = (baseline_bbox.y0 + baseline_bbox.y1) / 2
    dx = abs(candidate_center_x - baseline_center_x)
    dy = abs(candidate_center_y - baseline_center_y)
    page_span = max(candidate_bbox.x1, baseline_bbox.x1, candidate_bbox.y1, baseline_bbox.y1, 1.0)
    return max(0.0, 1.0 - ((dx + dy) / page_span))


def _metadata_value_similarity(candidate_value: object, baseline_value: object) -> float:
    if candidate_value == baseline_value:
        return 1.0
    if candidate_value in (None, "") and baseline_value in (None, ""):
        return 1.0
    return 0.0


def _count_similarity(candidate_count: int, baseline_count: int) -> float:
    if candidate_count == baseline_count == 0:
        return 1.0
    denominator = max(candidate_count, baseline_count)
    if denominator == 0:
        return 0.0
    return 1.0 - (abs(candidate_count - baseline_count) / denominator)


def _float_ratio_similarity(candidate_value: float, baseline_value: float) -> float:
    if candidate_value == baseline_value == 0:
        return 1.0
    denominator = max(candidate_value, baseline_value)
    if denominator == 0:
        return 0.0
    return max(0.0, 1.0 - (abs(candidate_value - baseline_value) / denominator))


def _metadata_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _bbox_to_metadata(bbox: Optional[BoundingBox]) -> Optional[dict[str, float]]:
    if bbox is None:
        return None
    return {
        "page_number": bbox.page_number,
        "x0": bbox.x0,
        "y0": bbox.y0,
        "x1": bbox.x1,
        "y1": bbox.y1,
        "width": bbox.width(),
        "height": bbox.height(),
    }


def _preview(text: str) -> str:
    return text[:TEXT_PREVIEW_LENGTH]


def _element_type_counts(page: DocumentPage) -> Counter[str]:
    return Counter(element.element_type for element in page.elements)


def _page_profile(page: DocumentPage) -> dict[str, object]:
    text = _page_text(page)
    return {
        "page_profile": {
            "text_length": len(text),
            "is_blank": page.is_blank(),
            "element_count": len(page.elements),
            "element_type_counts": dict(_element_type_counts(page)),
            "text_preview": _preview(text),
        }
    }


def _classify_unmatched_page(page: DocumentPage) -> dict[str, object]:
    text = _page_text(page)
    text_length = len(text)

    if _looks_like_page_number_residue(text, text_length):
        return {
            "page_issue_category": "likely_page_number_residue",
            "suggested_review_severity": "low",
            "classification_reason": "Short page text appears to contain only page-number residue.",
        }

    if _looks_like_toc_or_cover(page, text):
        return {
            "page_issue_category": "likely_toc_or_cover_format_noise",
            "suggested_review_severity": "medium",
            "classification_reason": "Page text and page position suggest table-of-contents or cover formatting differences.",
        }

    if _looks_like_short_signature_or_date_page(text, text_length):
        return {
            "page_issue_category": "likely_short_signature_or_date_page",
            "suggested_review_severity": "low",
            "classification_reason": "Short page text contains signature, stamp, representative, or date markers.",
        }

    if page.is_blank() or text_length <= 5:
        return {
            "page_issue_category": "likely_blank_or_near_blank",
            "suggested_review_severity": "low",
            "classification_reason": "Page is blank or contains near-blank normalized text.",
        }

    if _looks_like_attachment_start_page(text):
        return {
            "page_issue_category": "likely_attachment_start_page_needs_manual_review",
            "suggested_review_severity": "high",
            "classification_reason": "Page text suggests an attachment or commitment document start.",
        }

    if text_length <= 150:
        return {
            "page_issue_category": "likely_pagination_split_noise",
            "suggested_review_severity": "medium",
            "classification_reason": "Short unmatched page may be caused by pagination splitting.",
        }

    return {
        "page_issue_category": "unknown_needs_manual_review",
        "suggested_review_severity": "high",
        "classification_reason": "Unmatched page does not match deterministic low-noise page categories.",
    }


def _looks_like_page_number_residue(text: str, text_length: int) -> bool:
    if text_length > 30:
        return False

    lowered = text.lower()
    if "page" in lowered:
        return True

    if re.search(r"第\s*\d+\s*页", text):
        return True

    return "第" in text and "页" in text and "共" in text


def _looks_like_toc_or_cover(page: DocumentPage, text: str) -> bool:
    keywords = ("目录", "合同协议书", "监理人", "代建人", "发包人")
    if "目录" in text:
        return True

    return page.page_number <= 3 and any(keyword in text for keyword in keywords)


def _looks_like_short_signature_or_date_page(text: str, text_length: int) -> bool:
    if text_length > 80:
        return False

    keywords = (
        "签字",
        "盖章",
        "日期",
        "年",
        "月",
        "日",
        "法定代表人",
        "授权代表",
        "监理人",
        "代建人",
    )
    return any(keyword in text for keyword in keywords)


def _looks_like_attachment_start_page(text: str) -> bool:
    leading_text = text[:160]
    keywords = ("附件", "承诺书", "职责", "EHS", "诚信")
    return any(keyword in leading_text for keyword in keywords)


def _element_count_diff_type(
    element_type: str,
    candidate_count: int,
    baseline_count: int,
) -> tuple[str, str]:
    if element_type == "paragraph":
        if candidate_count > baseline_count:
            return "paragraph_added", "medium"
        return "paragraph_deleted", "medium"

    if element_type == "table":
        if candidate_count > baseline_count:
            return "table_added", "high"
        return "table_deleted", "high"

    if element_type == "image":
        if candidate_count == 0 or baseline_count == 0:
            return "image_modified", "high"
        return "image_replaced", "high"

    if element_type == "signature":
        return "signature_modified", "critical"

    return "layout_changed", "medium"


def _alignment_metadata(alignment: PageAlignment) -> dict[str, object]:
    metadata: dict[str, object] = {
        "alignment_score": alignment.score,
        "alignment_reason": alignment.reason,
    }
    metadata.update(alignment.metadata)
    return metadata


def _page_number(page: DocumentPage | None) -> int | None:
    if page is None:
        return None
    return page.page_number
