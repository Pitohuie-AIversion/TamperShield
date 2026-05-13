"""
Minimal page and element content comparison for TamperShield.

This module detects page-level and element-level differences from page
alignments. It does not perform table cell comparison, table matching, OCR,
report generation, evidence storage, or main pipeline orchestration.
"""

from collections import Counter
from difflib import SequenceMatcher
import re

from core.document_models import Difference, DocumentPage
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
    differences.extend(compare_element_counts(candidate_page, baseline_page))
    differences.extend(detect_table_compare_need(candidate_page, baseline_page))
    return differences


def compare_aligned_pages(
    alignments: list[PageAlignment],
    page_text_similarity_threshold: float = 0.98,
) -> list[Difference]:
    """Compare all page alignments and return a flat list of differences."""
    differences: list[Difference] = []
    for alignment in alignments:
        differences.extend(
            compare_page(
                alignment=alignment,
                page_text_similarity_threshold=page_text_similarity_threshold,
            )
        )
    return differences


def _page_text(page: DocumentPage) -> str:
    text = page.plain_text
    if not text:
        text = "\n".join(
            element.text for element in page.elements if element.text
        )
    return normalize_text(text)


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
