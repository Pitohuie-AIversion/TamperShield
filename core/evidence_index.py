"""
Evidence indexing utilities for the Document-first TamperShield pipeline.

This module organizes Difference objects into an in-memory traceable evidence
index. It does not generate reports, run OCR, compare tables, call comparison
modules, write files, or orchestrate the main pipeline.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from core.document_models import Difference


PAGE_DIFF_TYPES = {"page_added", "page_deleted", "page_reordered"}
PARAGRAPH_DIFF_TYPES = {
    "paragraph_added",
    "paragraph_deleted",
    "paragraph_modified",
    "low_confidence_element_match",
}
TABLE_DIFF_TYPES = {
    "table_added",
    "table_deleted",
    "table_modified",
    "table_cell_modified",
    "table_row_added",
    "table_row_deleted",
}
IMAGE_DIFF_TYPES = {
    "image_added",
    "image_deleted",
    "image_modified",
    "image_replaced",
    "image_modified_candidate",
}


@dataclass
class EvidenceRecord:
    evidence_id: str
    difference: Difference
    category: str
    severity: str
    candidate_page: Optional[int]
    baseline_page: Optional[int]
    candidate_element_id: Optional[str] = None
    baseline_element_id: Optional[str] = None
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceIndex:
    records: list[EvidenceRecord] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_record(self, record: EvidenceRecord) -> None:
        self.records.append(record)

    def by_severity(self, severity: str) -> list[EvidenceRecord]:
        return [record for record in self.records if record.severity == severity]

    def by_category(self, category: str) -> list[EvidenceRecord]:
        return [record for record in self.records if record.category == category]

    def by_candidate_page(self, page_number: int) -> list[EvidenceRecord]:
        return [
            record
            for record in self.records
            if record.candidate_page == page_number
        ]

    def by_baseline_page(self, page_number: int) -> list[EvidenceRecord]:
        return [
            record
            for record in self.records
            if record.baseline_page == page_number
        ]

    def critical_records(self) -> list[EvidenceRecord]:
        return self.by_severity("critical")

    def high_records(self) -> list[EvidenceRecord]:
        return self.by_severity("high")

    def summary(self) -> dict[str, Any]:
        by_severity = Counter(record.severity for record in self.records)
        by_category = Counter(record.category for record in self.records)
        by_diff_type = Counter(
            record.difference.diff_type for record in self.records
        )
        candidate_pages = sorted(
            {
                record.candidate_page
                for record in self.records
                if record.candidate_page is not None
            }
        )
        baseline_pages = sorted(
            {
                record.baseline_page
                for record in self.records
                if record.baseline_page is not None
            }
        )

        return {
            "total": len(self.records),
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "by_diff_type": dict(by_diff_type),
            "candidate_pages": candidate_pages,
            "baseline_pages": baseline_pages,
            "requires_manual_review_count": sum(
                1
                for record in self.records
                if record.metadata.get("requires_manual_review") is True
            ),
            "requires_table_compare_count": sum(
                1
                for record in self.records
                if record.metadata.get("requires_table_compare") is True
            ),
        }


def categorize_difference(diff: Difference) -> str:
    """Map a Difference to an evidence category."""
    if diff.metadata.get("requires_table_compare") is True:
        return "table"

    if diff.diff_type in PAGE_DIFF_TYPES:
        return "page"
    if diff.diff_type == "text_modified":
        return "text"
    if diff.diff_type in PARAGRAPH_DIFF_TYPES:
        return "paragraph"
    if diff.diff_type in TABLE_DIFF_TYPES:
        return "table"
    if diff.diff_type in IMAGE_DIFF_TYPES:
        return "image"
    if diff.diff_type == "signature_modified":
        return "signature"
    if diff.diff_type in {"layout_changed", "layout_structure_changed"}:
        return "layout"

    return "unknown"


def make_evidence_id(index: int, diff: Difference) -> str:
    """Create a stable evidence id from record order and diff type."""
    return f"ev-{index:05d}-{diff.diff_type}"


def difference_to_record(diff: Difference, index: int) -> EvidenceRecord:
    """Convert a Difference into an EvidenceRecord without mutating it."""
    return EvidenceRecord(
        evidence_id=make_evidence_id(index, diff),
        difference=diff,
        category=categorize_difference(diff),
        severity=diff.severity,
        candidate_page=diff.candidate_page,
        baseline_page=diff.baseline_page,
        candidate_element_id=diff.candidate_element_id,
        baseline_element_id=diff.baseline_element_id,
        message=diff.message,
        metadata=dict(diff.metadata),
    )


def build_evidence_index(
    differences: list[Difference],
    metadata: Optional[dict[str, Any]] = None,
) -> EvidenceIndex:
    """Build an in-memory evidence index from deterministic differences."""
    evidence_index = EvidenceIndex(metadata=dict(metadata or {}))
    for index, diff in enumerate(differences, start=1):
        evidence_index.add_record(difference_to_record(diff, index))
    return evidence_index


def group_records_by_page(
    index: EvidenceIndex,
) -> dict[str, dict[int, list[EvidenceRecord]]]:
    """Group evidence records by candidate and baseline page number."""
    grouped: dict[str, dict[int, list[EvidenceRecord]]] = {
        "candidate": defaultdict(list),
        "baseline": defaultdict(list),
    }

    for record in index.records:
        if record.candidate_page is not None:
            grouped["candidate"][record.candidate_page].append(record)
        if record.baseline_page is not None:
            grouped["baseline"][record.baseline_page].append(record)

    return {
        "candidate": dict(grouped["candidate"]),
        "baseline": dict(grouped["baseline"]),
    }


def filter_records(
    index: EvidenceIndex,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    diff_type: Optional[str] = None,
    requires_manual_review: Optional[bool] = None,
    requires_table_compare: Optional[bool] = None,
) -> list[EvidenceRecord]:
    """Filter evidence records by stable fields and metadata flags."""
    records = index.records

    if severity is not None:
        records = [record for record in records if record.severity == severity]
    if category is not None:
        records = [record for record in records if record.category == category]
    if diff_type is not None:
        records = [
            record
            for record in records
            if record.difference.diff_type == diff_type
        ]
    if requires_manual_review is not None:
        records = [
            record
            for record in records
            if (
                record.metadata.get("requires_manual_review") is True
            ) == requires_manual_review
        ]
    if requires_table_compare is not None:
        records = [
            record
            for record in records
            if (
                record.metadata.get("requires_table_compare") is True
            ) == requires_table_compare
        ]

    return records
