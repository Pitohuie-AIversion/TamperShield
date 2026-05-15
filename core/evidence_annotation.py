"""
Evidence annotation data layer for TamperShield.

This module converts existing EvidenceIndex records into JSON-friendly
annotation objects for later red-box rendering and audit report composition.
It does not draw annotations, generate PDFs, run OCR, compare content, or make
audit conclusions.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from core.document_models import BoundingBox, Difference
from core.evidence_index import EvidenceIndex, EvidenceRecord


TEXT_BLOCK_DIFF_TYPES = {
    "paragraph_added",
    "paragraph_deleted",
    "paragraph_modified",
    "low_confidence_element_match",
}
TABLE_BLOCK_DIFF_TYPES = {
    "table_added",
    "table_deleted",
    "table_modified",
    "table_cell_modified",
    "table_row_added",
    "table_row_deleted",
}
IMAGE_BLOCK_DIFF_TYPES = {
    "image_added",
    "image_deleted",
    "image_modified",
    "image_replaced",
    "image_modified_candidate",
}
PAGE_LEVEL_DIFF_TYPES = {
    "page_added",
    "page_deleted",
    "page_reordered",
    "text_modified",
}
LAYOUT_STRUCTURE_DIFF_TYPES = {
    "layout_changed",
    "layout_structure_changed",
}

ANNOTATION_LABELS = {
    "paragraph_added": "新增段落",
    "paragraph_deleted": "删除段落",
    "paragraph_modified": "段落修改",
    "table_added": "新增表格",
    "table_deleted": "删除表格",
    "table_modified": "表格修改",
    "image_added": "新增图片",
    "image_deleted": "删除图片",
    "image_modified_candidate": "疑似图片变化",
    "layout_structure_changed": "版面结构变化",
    "text_modified": "页面文本变化",
    "page_added": "新增页面",
    "page_deleted": "删除页面",
    "page_reordered": "页面顺序变化",
    "layout_changed": "版面变化",
    "low_confidence_element_match": "低置信度元素匹配",
}


@dataclass
class EvidenceAnnotation:
    evidence_id: str
    diff_index: int
    diff_type: str
    severity: str
    candidate_page_number: Optional[int]
    baseline_page_number: Optional[int]
    candidate_bbox: Optional[dict[str, Any]] = None
    baseline_bbox: Optional[dict[str, Any]] = None
    candidate_element_id: Optional[str] = None
    baseline_element_id: Optional[str] = None
    candidate_text_preview: str = ""
    baseline_text_preview: str = ""
    annotation_type: str = "unknown"
    annotation_label: str = ""
    review_status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly annotation dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "diff_index": self.diff_index,
            "diff_type": self.diff_type,
            "severity": self.severity,
            "candidate_page_number": self.candidate_page_number,
            "baseline_page_number": self.baseline_page_number,
            "candidate_bbox": self.candidate_bbox,
            "baseline_bbox": self.baseline_bbox,
            "candidate_element_id": self.candidate_element_id,
            "baseline_element_id": self.baseline_element_id,
            "candidate_text_preview": self.candidate_text_preview,
            "baseline_text_preview": self.baseline_text_preview,
            "annotation_type": self.annotation_type,
            "annotation_label": self.annotation_label,
            "review_status": self.review_status,
            "metadata": self.metadata,
        }


def build_evidence_annotations(index: EvidenceIndex) -> list[EvidenceAnnotation]:
    """Build annotation records from an EvidenceIndex without mutating it."""
    return [
        evidence_record_to_annotation(record, diff_index=diff_index)
        for diff_index, record in enumerate(index.records, start=1)
    ]


def annotation_to_dict(annotation: EvidenceAnnotation) -> dict[str, Any]:
    """Convert one EvidenceAnnotation into a JSON-friendly dictionary."""
    return annotation.to_dict()


def annotations_to_dicts(
    annotations: list[EvidenceAnnotation],
) -> list[dict[str, Any]]:
    """Convert annotation objects into JSON-friendly dictionaries."""
    return [annotation.to_dict() for annotation in annotations]


def evidence_record_to_annotation(
    record: EvidenceRecord,
    diff_index: int,
) -> EvidenceAnnotation:
    """Convert one evidence record into an annotation data object."""
    diff = record.difference
    metadata = dict(record.metadata)
    candidate_bbox = _candidate_bbox(diff)
    baseline_bbox = _baseline_bbox(diff)
    selected_bbox_source = _selected_bbox_source(candidate_bbox, baseline_bbox)
    bbox_available = selected_bbox_source is not None

    annotation_type = _annotation_type(diff.diff_type)
    if not bbox_available:
        annotation_type = "page_level"

    metadata.update(
        {
            "bbox_available": bbox_available,
            "selected_bbox_source": selected_bbox_source,
        }
    )

    return EvidenceAnnotation(
        evidence_id=record.evidence_id,
        diff_index=diff_index,
        diff_type=diff.diff_type,
        severity=record.severity,
        candidate_page_number=record.candidate_page,
        baseline_page_number=record.baseline_page,
        candidate_bbox=candidate_bbox,
        baseline_bbox=baseline_bbox,
        candidate_element_id=record.candidate_element_id,
        baseline_element_id=record.baseline_element_id,
        candidate_text_preview=str(metadata.get("candidate_text_preview", "")),
        baseline_text_preview=str(metadata.get("baseline_text_preview", "")),
        annotation_type=annotation_type,
        annotation_label=_annotation_label(diff.diff_type),
        review_status="pending",
        metadata=metadata,
    )


def _annotation_type(diff_type: str) -> str:
    if diff_type in TEXT_BLOCK_DIFF_TYPES:
        return "text_block"
    if diff_type in TABLE_BLOCK_DIFF_TYPES:
        return "table_block"
    if diff_type in IMAGE_BLOCK_DIFF_TYPES:
        return "image_block"
    if diff_type in LAYOUT_STRUCTURE_DIFF_TYPES:
        return "layout_structure"
    if diff_type in PAGE_LEVEL_DIFF_TYPES:
        return "page_level"
    return "unknown"


def _annotation_label(diff_type: str) -> str:
    return ANNOTATION_LABELS.get(diff_type, "未知证据")


def _candidate_bbox(diff: Difference) -> Optional[dict[str, Any]]:
    metadata_bbox = diff.metadata.get("candidate_bbox")
    if metadata_bbox is not None:
        return _bbox_to_dict(metadata_bbox)
    if diff.location is not None and diff.candidate_page is not None:
        return _bbox_to_dict(diff.location)
    return None


def _baseline_bbox(diff: Difference) -> Optional[dict[str, Any]]:
    metadata_bbox = diff.metadata.get("baseline_bbox")
    if metadata_bbox is not None:
        return _bbox_to_dict(metadata_bbox)
    return None


def _selected_bbox_source(
    candidate_bbox: Optional[dict[str, Any]],
    baseline_bbox: Optional[dict[str, Any]],
) -> Optional[str]:
    if candidate_bbox is not None:
        return "candidate_bbox"
    if baseline_bbox is not None:
        return "baseline_bbox"
    return None


def _bbox_to_dict(value: Any) -> Optional[dict[str, Any]]:
    if value is None:
        return None

    if isinstance(value, BoundingBox):
        return {
            "page_number": value.page_number,
            "x0": value.x0,
            "y0": value.y0,
            "x1": value.x1,
            "y1": value.y1,
            "width": value.width(),
            "height": value.height(),
        }

    if isinstance(value, dict):
        return dict(value)

    return None
