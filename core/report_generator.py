"""
Minimal report generation for TamperShield EvidenceIndex objects.

This module only formats existing evidence into summary dictionaries, page
groups, Markdown text, and explicitly permitted text exports. It does not
parse documents, align pages, compare content, inspect tables, run OCR,
preprocess images, or make audit judgments.
"""

import json
import html
from pathlib import Path
from typing import Any

from core.evidence_annotation import build_evidence_annotations
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

    _append_annotations_summary_markdown(lines, index)

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


def generate_html_report(
    index: EvidenceIndex,
    annotations: Any = None,
    rendered_annotations: Any = None,
    title: str = "TamperShield Evidence Report",
) -> str:
    """Generate a lightweight standalone HTML evidence report."""
    summary_bundle = evidence_index_to_summary_dict(index)
    summary = summary_bundle["summary"]
    metadata = summary_bundle["metadata"]
    annotation_items = _annotation_dicts(annotations)
    if annotations is None:
        annotation_items = [
            make_json_safe(annotation.to_dict())
            for annotation in build_evidence_annotations(index)
        ]
    rendered_items = _rendered_annotation_dicts(rendered_annotations)

    lines: list[str] = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        f"<title>{_escape(title)}</title>",
        "<style>",
        _html_report_css(),
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        f"<h1>{_escape(title)}</h1>",
        '<section class="summary-grid">',
        _summary_card("Total differences", summary.get("total", 0)),
        _summary_card("Requires manual review", summary.get("requires_manual_review_count", 0)),
        _summary_card("Requires table compare", summary.get("requires_table_compare_count", 0)),
        "</section>",
        "<section>",
        "<h2>Summary</h2>",
        '<div class="stats">',
        _json_block("Severity", summary.get("by_severity", {})),
        _json_block("Diff type", summary.get("by_diff_type", {})),
        _json_block("Category", summary.get("by_category", {})),
        "</div>",
        "</section>",
        "<section>",
        "<h2>Metadata</h2>",
        _json_pre(metadata),
        "</section>",
        "<section>",
        "<h2>Evidence Records</h2>",
        _evidence_records_table(index),
        "</section>",
        "<section>",
        "<h2>Evidence Annotations</h2>",
        _annotations_table(annotation_items),
        "</section>",
        "<section>",
        "<h2>Rendered Annotation Images</h2>",
        _rendered_annotations_gallery(rendered_items),
        "</section>",
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(lines)


def write_html_report(
    html_text: str,
    output_path: str | Path,
    allow_write: bool = False,
    overwrite: bool = False,
    encoding: str = "utf-8",
) -> Path:
    """Write HTML report text only when explicitly permitted."""
    return write_text_report(
        html_text,
        output_path=output_path,
        allow_write=allow_write,
        overwrite=overwrite,
        encoding=encoding,
    )


def generate_report_bundle(index: EvidenceIndex) -> dict[str, Any]:
    """Return an in-memory bundle containing summary, pages, and Markdown."""
    annotations = build_evidence_annotations(index)
    return {
        "summary": evidence_index_to_summary_dict(index),
        "pages": evidence_records_to_page_dict(index),
        "annotations": make_json_safe(
            [annotation.to_dict() for annotation in annotations]
        ),
        "markdown": generate_markdown_report(index),
        "html": generate_html_report(index, annotations=annotations),
    }


def _html_report_css() -> str:
    return """
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: #1f2933;
  background: #f5f7fa;
}
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
h1, h2, h3 {
  color: #111827;
}
section {
  margin: 20px 0;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #d8dee9;
  border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th, td {
  border-bottom: 1px solid #e5e7eb;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #f3f4f6;
}
pre {
  max-height: 320px;
  overflow: auto;
  padding: 12px;
  background: #111827;
  color: #f9fafb;
  border-radius: 6px;
  white-space: pre-wrap;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  background: transparent;
  border: 0;
  padding: 0;
}
.summary-card {
  padding: 14px;
  border: 1px solid #d8dee9;
  border-radius: 8px;
  background: #ffffff;
}
.summary-card strong {
  display: block;
  font-size: 24px;
  margin-top: 8px;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}
.image-card {
  border: 1px solid #d8dee9;
  border-radius: 8px;
  padding: 12px;
}
.image-card img {
  max-width: 100%;
  border: 1px solid #e5e7eb;
}
.muted {
  color: #6b7280;
}
"""


def _summary_card(label: str, value: Any) -> str:
    return (
        '<div class="summary-card">'
        f"<span>{_escape(label)}</span>"
        f"<strong>{_escape(value)}</strong>"
        "</div>"
    )


def _json_block(label: str, value: Any) -> str:
    return (
        "<div>"
        f"<h3>{_escape(label)}</h3>"
        f"{_json_pre(value)}"
        "</div>"
    )


def _json_pre(value: Any) -> str:
    json_text = json.dumps(make_json_safe(value), ensure_ascii=False, indent=2, sort_keys=True)
    return f"<pre>{_escape(json_text)}</pre>"


def _evidence_records_table(index: EvidenceIndex) -> str:
    if not index.records:
        return '<p class="muted">No evidence records.</p>'

    rows = [
        "<table>",
        "<thead>",
        "<tr>",
        "<th>Evidence ID</th><th>Diff type</th><th>Category</th><th>Severity</th>"
        "<th>Candidate page</th><th>Baseline page</th><th>Message</th><th>Metadata</th>",
        "</tr>",
        "</thead>",
        "<tbody>",
    ]
    for record in index.records:
        record_dict = evidence_record_to_dict(record)
        rows.extend(
            [
                "<tr>",
                f"<td>{_escape(record_dict['evidence_id'])}</td>",
                f"<td>{_escape(record_dict['diff_type'])}</td>",
                f"<td>{_escape(record_dict['category'])}</td>",
                f"<td>{_escape(record_dict['severity'])}</td>",
                f"<td>{_escape(record_dict['candidate_page'])}</td>",
                f"<td>{_escape(record_dict['baseline_page'])}</td>",
                f"<td>{_escape(record_dict['message'])}</td>",
                f"<td>{_json_pre(record_dict['metadata'])}</td>",
                "</tr>",
            ]
        )
    rows.extend(["</tbody>", "</table>"])
    return "\n".join(rows)


def _annotations_table(annotations: list[dict[str, Any]]) -> str:
    if not annotations:
        return '<p class="muted">No evidence annotations.</p>'

    rows = [
        "<table>",
        "<thead>",
        "<tr>",
        "<th>Evidence ID</th><th>Label</th><th>Type</th><th>Severity</th>"
        "<th>Candidate page</th><th>Baseline page</th><th>Review status</th><th>Metadata</th>",
        "</tr>",
        "</thead>",
        "<tbody>",
    ]
    for annotation in annotations:
        rows.extend(
            [
                "<tr>",
                f"<td>{_escape(annotation.get('evidence_id'))}</td>",
                f"<td>{_escape(annotation.get('annotation_label'))}</td>",
                f"<td>{_escape(annotation.get('annotation_type'))}</td>",
                f"<td>{_escape(annotation.get('severity'))}</td>",
                f"<td>{_escape(annotation.get('candidate_page_number'))}</td>",
                f"<td>{_escape(annotation.get('baseline_page_number'))}</td>",
                f"<td>{_escape(annotation.get('review_status'))}</td>",
                f"<td>{_json_pre(annotation.get('metadata', {}))}</td>",
                "</tr>",
            ]
        )
    rows.extend(["</tbody>", "</table>"])
    return "\n".join(rows)


def _rendered_annotations_gallery(rendered_annotations: list[dict[str, Any]]) -> str:
    if not rendered_annotations:
        return '<p class="muted">No rendered annotation images.</p>'

    cards: list[str] = ['<div class="image-grid">']
    for item in rendered_annotations:
        output_image_path = item.get("output_image_path")
        cards.extend(
            [
                '<div class="image-card">',
                f"<h3>{_escape(item.get('evidence_id'))}</h3>",
                f"<p>{_escape(item.get('annotation_label'))} "
                f"({_escape(item.get('source_side'))}, page={_escape(item.get('page_number'))}, "
                f"status={_escape(item.get('render_status'))})</p>",
            ]
        )
        if output_image_path:
            cards.append(
                f'<img src="{_escape_attr(output_image_path)}" '
                f'alt="{_escape_attr(item.get("evidence_id"))}" />'
            )
            cards.append(f"<p class=\"muted\">{_escape(output_image_path)}</p>")
        else:
            cards.append('<p class="muted">No image path available.</p>')
        cards.append(_json_pre(item.get("metadata", {})))
        cards.append("</div>")

    cards.append("</div>")
    return "\n".join(cards)


def _annotation_dicts(annotations: Any) -> list[dict[str, Any]]:
    if annotations is None:
        return []

    items: list[dict[str, Any]] = []
    for annotation in annotations:
        if hasattr(annotation, "to_dict"):
            items.append(make_json_safe(annotation.to_dict()))
        elif isinstance(annotation, dict):
            items.append(make_json_safe(annotation))
        else:
            items.append({"value": make_json_safe(annotation)})
    return items


def _rendered_annotation_dicts(rendered_annotations: Any) -> list[dict[str, Any]]:
    return _annotation_dicts(rendered_annotations)


def _escape(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _escape_attr(value: Any) -> str:
    return _escape(value)


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
        ]
    )
    _append_review_context_markdown(lines, record_dict)
    lines.extend(
        [
            "Metadata:",
            "",
            "```json",
            metadata_json,
            "```",
            "",
        ]
    )


def _append_annotations_summary_markdown(
    lines: list[str],
    index: EvidenceIndex,
) -> None:
    annotations = build_evidence_annotations(index)
    lines.extend(["", "## Evidence Annotations", ""])

    if not annotations:
        lines.extend(["No evidence annotations.", ""])
        return

    for annotation in annotations[:20]:
        bbox_status = "yes" if annotation.metadata.get("bbox_available") else "no"
        lines.append(
            "- "
            f"{annotation.evidence_id}: "
            f"{annotation.annotation_label} "
            f"({annotation.annotation_type}, severity={annotation.severity}, "
            f"candidate_page={annotation.candidate_page_number}, "
            f"baseline_page={annotation.baseline_page_number}, "
            f"bbox_available={bbox_status})"
        )

    if len(annotations) > 20:
        lines.append(f"- ... {len(annotations) - 20} more annotations omitted.")

    lines.append("")


def _append_review_context_markdown(
    lines: list[str],
    record_dict: dict[str, Any],
) -> None:
    metadata = record_dict.get("metadata", {})
    if not isinstance(metadata, dict):
        return

    has_review_context = "page_issue_category" in metadata
    page_profile = metadata.get("page_profile")
    has_page_profile = isinstance(page_profile, dict)

    if not has_review_context and not has_page_profile:
        return

    if has_review_context:
        lines.extend(["Review context:", ""])
        _append_optional_metadata_line(
            lines=lines,
            label="Page issue category",
            value=metadata.get("page_issue_category"),
        )
        _append_optional_metadata_line(
            lines=lines,
            label="Suggested review severity",
            value=metadata.get("suggested_review_severity"),
        )
        _append_optional_metadata_line(
            lines=lines,
            label="Classification reason",
            value=metadata.get("classification_reason"),
        )
        lines.append("")

    if has_page_profile:
        lines.extend(["Page profile:", ""])
        _append_optional_metadata_line(
            lines=lines,
            label="Text length",
            value=page_profile.get("text_length"),
        )
        _append_optional_metadata_line(
            lines=lines,
            label="Is blank",
            value=page_profile.get("is_blank"),
        )
        _append_optional_metadata_line(
            lines=lines,
            label="Element count",
            value=page_profile.get("element_count"),
        )
        element_counts = page_profile.get("element_type_counts")
        if element_counts is not None:
            lines.append(
                "- Element type counts: "
                f"{json.dumps(element_counts, ensure_ascii=False)}"
            )
        _append_optional_metadata_line(
            lines=lines,
            label="Text preview",
            value=page_profile.get("text_preview"),
        )
        lines.append("")


def _append_optional_metadata_line(
    lines: list[str],
    label: str,
    value: Any,
) -> None:
    if value is None:
        return
    lines.append(f"- {label}: {value}")
