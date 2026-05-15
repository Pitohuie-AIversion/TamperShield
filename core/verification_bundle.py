"""
End-to-end verification bundle composition for TamperShield.

This module wraps the existing Document-first pipeline, evidence annotations,
optional annotation rendering, and lightweight reports into one in-memory
result object. It does not change the underlying pipeline return value, write
files by default, generate PDF/Word reports, run a web service, or make audit
judgments.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Optional

from core.document_pipeline import compare_documents
from core.evidence_annotation import (
    EvidenceAnnotation,
    annotations_to_dicts,
    build_evidence_annotations,
)
from core.evidence_index import EvidenceIndex
from core.evidence_renderer import RenderedAnnotation, render_evidence_annotations
from core.report_generator import (
    evidence_index_to_summary_dict,
    generate_html_report,
    generate_markdown_report,
    make_json_safe,
    write_html_report,
    write_text_report,
)


@dataclass
class VerificationBundle:
    evidence_index: EvidenceIndex
    annotations: list[EvidenceAnnotation] = field(default_factory=list)
    rendered_annotations: list[RenderedAnnotation] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    markdown: str = ""
    html: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly bundle without embedding raw model objects."""
        return {
            "summary": make_json_safe(self.summary),
            "metadata": make_json_safe(self.metadata),
            "annotations": make_json_safe(annotations_to_dicts(self.annotations)),
            "rendered_annotations": make_json_safe(
                [
                    rendered_annotation.to_dict()
                    for rendered_annotation in self.rendered_annotations
                ]
            ),
        }


def build_verification_bundle(
    candidate_path: str | Path,
    baseline_path: str | Path,
    enable_ocr: bool = False,
    enable_preprocess: bool = False,
    render_annotations: bool = False,
    annotation_output_dir: Optional[str | Path] = None,
    overwrite: bool = False,
    render_scale: float = 2.0,
) -> VerificationBundle:
    """Build an in-memory verification bundle from existing pipeline outputs."""
    if render_annotations and annotation_output_dir is None:
        raise ValueError(
            "annotation_output_dir is required when render_annotations=True"
        )

    candidate_file = Path(candidate_path)
    baseline_file = Path(baseline_path)

    index = compare_documents(
        candidate_file=candidate_file,
        baseline_file=baseline_file,
        enable_ocr=enable_ocr,
        enable_preprocess=enable_preprocess,
    )
    annotations = build_evidence_annotations(index)

    rendered_annotations: list[RenderedAnnotation] = []
    if render_annotations:
        rendered_annotations = render_evidence_annotations(
            annotations=annotations,
            candidate_file_path=candidate_file,
            baseline_file_path=baseline_file,
            output_dir=annotation_output_dir,
            overwrite=overwrite,
            render_scale=render_scale,
        )

    summary = evidence_index_to_summary_dict(index)
    metadata = {
        "candidate_path": str(candidate_file),
        "baseline_path": str(baseline_file),
        "enable_ocr": enable_ocr,
        "enable_preprocess": enable_preprocess,
        "render_annotations": render_annotations,
        "annotation_output_dir": (
            str(annotation_output_dir) if annotation_output_dir is not None else None
        ),
        "rendered_annotation_count": len(rendered_annotations),
        "annotation_count": len(annotations),
        "difference_total": index.summary().get("total", 0),
        "pipeline_stage": "verification_bundle",
    }

    markdown = generate_markdown_report(index)
    html = generate_html_report(
        index,
        annotations=annotations,
        rendered_annotations=rendered_annotations,
    )

    return VerificationBundle(
        evidence_index=index,
        annotations=annotations,
        rendered_annotations=rendered_annotations,
        summary=summary,
        markdown=markdown,
        html=html,
        metadata=metadata,
    )


def write_verification_bundle(
    bundle: VerificationBundle,
    output_dir: str | Path,
    write_html: bool = True,
    write_markdown: bool = True,
    allow_write: bool = False,
    overwrite: bool = False,
) -> dict[str, str]:
    """Write selected bundle artifacts only when explicitly permitted."""
    if not allow_write:
        raise PermissionError("[Output Blocked] - Permission Required")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    written_paths: dict[str, str] = {}
    html_output_path = output_path / "verification_report.html"
    markdown_output_path = output_path / "verification_report.md"
    summary_path = output_path / "verification_summary.json"
    _ensure_outputs_available(
        [
            html_output_path if write_html else None,
            markdown_output_path if write_markdown else None,
            summary_path,
        ],
        overwrite=overwrite,
    )

    if write_html:
        html_path = write_html_report(
            bundle.html,
            output_path=html_output_path,
            allow_write=allow_write,
            overwrite=overwrite,
        )
        written_paths["html"] = str(html_path)

    if write_markdown:
        markdown_path = write_text_report(
            bundle.markdown,
            output_path=markdown_output_path,
            allow_write=allow_write,
            overwrite=overwrite,
        )
        written_paths["markdown"] = str(markdown_path)

    summary_path.write_text(
        json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    written_paths["summary_json"] = str(summary_path)

    return written_paths


def _ensure_outputs_available(
    output_paths: list[Optional[Path]],
    overwrite: bool,
) -> None:
    for output_path in output_paths:
        if output_path is None:
            continue
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists and overwrite=False: {output_path}"
            )
