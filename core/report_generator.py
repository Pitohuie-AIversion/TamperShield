"""
Minimal report generation for TamperShield EvidenceIndex objects.

This module only formats existing evidence into summary dictionaries, page
groups, Markdown text, and explicitly permitted text exports. It does not
parse documents, align pages, compare content, inspect tables, run OCR,
preprocess images, or make audit judgments.
"""

import json
from pathlib import Path
from typing import Any

from core.evidence_index import (
    EvidenceIndex,
    EvidenceRecord,
    group_records_by_page,
)


def make_json_safe(value: Any) -> Any:
    """Convert nested values into JSON-safe primitives."""
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def evidence_index_to_summary_dict(index: EvidenceIndex) -> dict[str, Any]:
    """Return a serializable summary object for an EvidenceIndex."""
    return {
        "summary": make_json_safe(index.summary()),
        "metadata": make_json_safe(index.metadata),
    }


def evidence_record_to_dict(record: EvidenceRecord) -> dict[str, Any]:
    """Convert an EvidenceRecord to a plain dict without mutating it."""
    return {
        "evidence_id": record.evidence_id,
        "diff_type": record.difference.diff_type,
        "category": record.category,
        "severity": record.severity,
        "candidate_page": record.candidate_page,
        "baseline_page": record.baseline_page,
        "candidate_element_id": record.candidate_element_id,
        "baseline_element_id": record.baseline_element_id,
        "message": record.message,
        "metadata": make_json_safe(record.metadata),
    }


def evidence_records_to_page_dict(index: EvidenceIndex) -> dict[str, Any]:
    """Group evidence records by candidate and baseline page."""
    grouped = group_records_by_page(index)

    return {
        "candidate": {
            str(page_number): [
                evidence_record_to_dict(record) for record in records
            ]
            for page_number, records in grouped["candidate"].items()
        },
        "baseline": {
            str(page_number): [
                evidence_record_to_dict(record) for record in records
            ]
            for page_number, records in grouped["baseline"].items()
        },
    }


def generate_markdown_report(
    index: EvidenceIndex,
    title: str = "TamperShield Evidence Report",
) -> str:
    """Generate a Markdown report string from an EvidenceIndex."""
    summary_bundle = evidence_index_to_summary_dict(index)
    summary = summary_bundle["summary"]
    metadata = summary_bundle["metadata"]
    grouped = group_records_by_page(index)
    candidate_records = grouped["candidate"]
    without_candidate_page = [
        record for record in index.records if record.candidate_page is None
    ]

    lines: list[str] = [
        f"# {title}",
        "",
        "## Summary",
        "",
        f"- Total differences: {summary.get('total', 0)}",
        f"- By severity: {json.dumps(summary.get('by_severity', {}), ensure_ascii=False)}",
        f"- By category: {json.dumps(summary.get('by_category', {}), ensure_ascii=False)}",
        f"- By diff type: {json.dumps(summary.get('by_diff_type', {}), ensure_ascii=False)}",
        f"- Requires manual review: {summary.get('requires_manual_review_count', 0)}",
        f"- Requires table compare: {summary.get('requires_table_compare_count', 0)}",
        "",
        "## Metadata",
        "",
    ]

    if metadata:
        for key in sorted(metadata):
            lines.append(f"- {key}: {metadata[key]}")
    else:
        lines.append("- None")

    lines.extend(["", "## Evidence by Candidate Page", ""])

    if candidate_records:
        for page_number in sorted(candidate_records):
            lines.extend([f"### Candidate Page {page_number}", ""])
            for record in candidate_records[page_number]:
                _append_record_markdown(lines, record)
    else:
        lines.extend(["No candidate-page evidence records.", ""])

    if without_candidate_page:
        lines.extend(["## Evidence Without Candidate Page", ""])
        for record in without_candidate_page:
            _append_record_markdown(lines, record)

    return "\n".join(lines).rstrip() + "\n"


def write_text_report(
    report_text: str,
    output_path: str | Path,
    allow_write: bool = False,
    overwrite: bool = False,
    encoding: str = "utf-8",
) -> Path:
    """Write report text only when explicitly permitted."""
    if not allow_write:
        raise PermissionError("[Output Blocked] - Permission Required")

    path = Path(output_path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists and overwrite=False: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text, encoding=encoding)
    return path


def generate_report_bundle(index: EvidenceIndex) -> dict[str, Any]:
    """Return an in-memory bundle containing summary, pages, and Markdown."""
    return {
        "summary": evidence_index_to_summary_dict(index),
        "pages": evidence_records_to_page_dict(index),
        "markdown": generate_markdown_report(index),
    }


def _append_record_markdown(lines: list[str], record: EvidenceRecord) -> None:
    record_dict = evidence_record_to_dict(record)
    metadata_json = json.dumps(
        record_dict["metadata"],
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    lines.extend(
        [
            f"#### {record.evidence_id}",
            "",
            f"- Diff type: {record_dict['diff_type']}",
            f"- Category: {record.category}",
            f"- Severity: {record.severity}",
            f"- Candidate page: {record.candidate_page}",
            f"- Baseline page: {record.baseline_page}",
            f"- Candidate element: {record.candidate_element_id}",
            f"- Baseline element: {record.baseline_element_id}",
            f"- Message: {record.message}",
            "",
            "Metadata:",
            "",
            "```json",
            metadata_json,
            "```",
            "",
        ]
    )
