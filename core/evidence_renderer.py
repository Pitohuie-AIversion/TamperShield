"""
Evidence annotation rendering for TamperShield.

This module renders page-level images and draws simple red-box annotations from
EvidenceAnnotation records. It does not generate final PDF/Word reports, run
OCR, compare content, perform image authenticity checks, or orchestrate the
main pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Iterable, Literal, Optional

import cv2
import fitz
import numpy as np

from core.evidence_annotation import EvidenceAnnotation


SourceSide = Literal["candidate", "baseline"]
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


@dataclass
class RenderedAnnotation:
    evidence_id: str
    diff_type: str
    annotation_type: str
    annotation_label: str
    severity: str
    source_side: SourceSide
    page_number: Optional[int]
    bbox: Optional[dict[str, Any]]
    output_image_path: Optional[str]
    render_status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly rendered annotation dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "diff_type": self.diff_type,
            "annotation_type": self.annotation_type,
            "annotation_label": self.annotation_label,
            "severity": self.severity,
            "source_side": self.source_side,
            "page_number": self.page_number,
            "bbox": self.bbox,
            "output_image_path": self.output_image_path,
            "render_status": self.render_status,
            "metadata": self.metadata,
        }


def render_evidence_annotations(
    annotations: Iterable[EvidenceAnnotation],
    candidate_file_path: str | Path,
    baseline_file_path: str | Path,
    output_dir: str | Path,
    overwrite: bool = False,
    render_scale: float = 2.0,
) -> list[RenderedAnnotation]:
    """Render red-box annotation images for candidate and baseline sides."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    rendered: list[RenderedAnnotation] = []
    for annotation in annotations:
        side_jobs = _annotation_side_jobs(annotation)
        if not side_jobs:
            rendered.append(
                _skipped_render(
                    annotation=annotation,
                    source_side="candidate",
                    page_number=annotation.candidate_page_number,
                    status="skipped_no_bbox",
                    metadata={"bbox_available": False},
                )
            )
            continue

        for source_side, bbox, page_number in side_jobs:
            source_file = (
                Path(candidate_file_path)
                if source_side == "candidate"
                else Path(baseline_file_path)
            )
            rendered.append(
                render_annotation(
                    annotation=annotation,
                    source_file_path=source_file,
                    source_side=source_side,
                    page_number=page_number,
                    bbox=bbox,
                    output_dir=output_path,
                    overwrite=overwrite,
                    render_scale=render_scale,
                )
            )

    return rendered


def render_annotation(
    annotation: EvidenceAnnotation,
    source_file_path: str | Path,
    source_side: SourceSide,
    page_number: Optional[int],
    bbox: dict[str, Any],
    output_dir: str | Path,
    overwrite: bool = False,
    render_scale: float = 2.0,
) -> RenderedAnnotation:
    """Render one annotation on one side of the source document."""
    source_path = Path(source_file_path)
    output_path = Path(output_dir)

    if page_number is None:
        return _skipped_render(
            annotation=annotation,
            source_side=source_side,
            page_number=page_number,
            bbox=bbox,
            status="skipped_no_page_number",
        )

    output_image_path = output_path / _annotation_output_name(
        annotation=annotation,
        source_side=source_side,
        page_number=page_number,
    )
    if output_image_path.exists() and not overwrite:
        return _skipped_render(
            annotation=annotation,
            source_side=source_side,
            page_number=page_number,
            bbox=bbox,
            status="skipped_output_exists",
            output_image_path=output_image_path,
        )

    try:
        page_image, coordinate_system = render_source_page(
            source_file_path=source_path,
            page_number=page_number,
            render_scale=render_scale,
        )
    except Exception as exc:
        return _skipped_render(
            annotation=annotation,
            source_side=source_side,
            page_number=page_number,
            bbox=bbox,
            status="unsupported_source",
            metadata={
                "error_type": type(exc).__name__,
                "error": str(exc),
                "source_file": str(source_path),
            },
        )

    scaled_bbox = scale_bbox(bbox, render_scale=render_scale)
    draw_annotation_box(
        image=page_image,
        scaled_bbox=scaled_bbox,
        label=_label_for_drawing(annotation),
        severity=annotation.severity,
    )
    cv2.imwrite(str(output_image_path), page_image)

    return RenderedAnnotation(
        evidence_id=annotation.evidence_id,
        diff_type=annotation.diff_type,
        annotation_type=annotation.annotation_type,
        annotation_label=annotation.annotation_label,
        severity=annotation.severity,
        source_side=source_side,
        page_number=page_number,
        bbox=bbox,
        output_image_path=str(output_image_path),
        render_status="rendered",
        metadata={
            "source_file": str(source_path),
            "original_bbox": dict(bbox),
            "scaled_bbox": scaled_bbox,
            "render_scale": render_scale,
            "page_number": page_number,
            "source_side": source_side,
            "coordinate_system": coordinate_system,
        },
    )


def render_source_page(
    source_file_path: str | Path,
    page_number: int,
    render_scale: float,
) -> tuple[np.ndarray, str]:
    """Render a PDF page or image file into an OpenCV BGR image."""
    source_path = Path(source_file_path)
    suffix = source_path.suffix.lower()

    if suffix == ".pdf":
        return render_pdf_page(
            pdf_path=source_path,
            page_number=page_number,
            render_scale=render_scale,
        ), "pdf_points"

    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Unable to read image file: {source_path}")
        if render_scale != 1.0:
            image = cv2.resize(
                image,
                dsize=None,
                fx=render_scale,
                fy=render_scale,
                interpolation=cv2.INTER_LINEAR,
            )
        return image, "image_pixels"

    raise ValueError(f"Unsupported source type for annotation rendering: {suffix}")


def render_pdf_page(
    pdf_path: str | Path,
    page_number: int,
    render_scale: float = 2.0,
) -> np.ndarray:
    """Render a 1-based PDF page into an OpenCV BGR image."""
    page_index = page_number - 1
    if page_index < 0:
        raise ValueError(f"Invalid PDF page number: {page_number}")

    with fitz.open(str(pdf_path)) as pdf:
        if page_index >= len(pdf):
            raise IndexError(
                f"PDF page number out of range: {page_number}; page_count={len(pdf)}"
            )
        page = pdf[page_index]
        matrix = fitz.Matrix(render_scale, render_scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height,
        pixmap.width,
        pixmap.n,
    )
    if pixmap.n == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR).copy()
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR).copy()


def draw_annotation_box(
    image: np.ndarray,
    scaled_bbox: dict[str, int],
    label: str,
    severity: str,
) -> None:
    """Draw a simple red rectangle and label on an image in-place."""
    height, width = image.shape[:2]
    x0 = _clamp_int(scaled_bbox["x0"], 0, max(0, width - 1))
    y0 = _clamp_int(scaled_bbox["y0"], 0, max(0, height - 1))
    x1 = _clamp_int(scaled_bbox["x1"], 0, max(0, width - 1))
    y1 = _clamp_int(scaled_bbox["y1"], 0, max(0, height - 1))

    if x1 <= x0:
        x1 = min(width - 1, x0 + 1)
    if y1 <= y0:
        y1 = min(height - 1, y0 + 1)

    color = (0, 0, 255)
    thickness = 3 if severity in {"high", "critical"} else 2
    cv2.rectangle(image, (x0, y0), (x1, y1), color, thickness)

    label_text = label[:80] if label else "annotation"
    label_y = max(16, y0 - 8)
    cv2.putText(
        image,
        label_text,
        (x0, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
        cv2.LINE_AA,
    )


def scale_bbox(bbox: dict[str, Any], render_scale: float) -> dict[str, int]:
    """Scale a document bbox into rendered image pixel coordinates."""
    return {
        "x0": round(float(bbox["x0"]) * render_scale),
        "y0": round(float(bbox["y0"]) * render_scale),
        "x1": round(float(bbox["x1"]) * render_scale),
        "y1": round(float(bbox["y1"]) * render_scale),
    }


def _annotation_side_jobs(
    annotation: EvidenceAnnotation,
) -> list[tuple[SourceSide, dict[str, Any], Optional[int]]]:
    jobs: list[tuple[SourceSide, dict[str, Any], Optional[int]]] = []
    if annotation.candidate_bbox is not None:
        jobs.append(
            (
                "candidate",
                annotation.candidate_bbox,
                _page_number(annotation.candidate_page_number, annotation.candidate_bbox),
            )
        )
    if annotation.baseline_bbox is not None:
        jobs.append(
            (
                "baseline",
                annotation.baseline_bbox,
                _page_number(annotation.baseline_page_number, annotation.baseline_bbox),
            )
        )
    return jobs


def _page_number(
    annotation_page_number: Optional[int],
    bbox: dict[str, Any],
) -> Optional[int]:
    if annotation_page_number is not None:
        return annotation_page_number
    bbox_page_number = bbox.get("page_number")
    if bbox_page_number is None:
        return None
    return int(bbox_page_number)


def _annotation_output_name(
    annotation: EvidenceAnnotation,
    source_side: SourceSide,
    page_number: int,
) -> str:
    evidence_id = _safe_filename_part(annotation.evidence_id)
    annotation_type = _safe_filename_part(annotation.annotation_type)
    return f"{evidence_id}_{source_side}_p{page_number}_{annotation_type}.png"


def _safe_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_")
    return cleaned or "annotation"


def _label_for_drawing(annotation: EvidenceAnnotation) -> str:
    if _is_ascii(annotation.annotation_label):
        return annotation.annotation_label
    return annotation.diff_type


def _is_ascii(value: str) -> bool:
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True


def _skipped_render(
    annotation: EvidenceAnnotation,
    source_side: SourceSide,
    page_number: Optional[int],
    status: str,
    bbox: Optional[dict[str, Any]] = None,
    output_image_path: Optional[Path] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> RenderedAnnotation:
    return RenderedAnnotation(
        evidence_id=annotation.evidence_id,
        diff_type=annotation.diff_type,
        annotation_type=annotation.annotation_type,
        annotation_label=annotation.annotation_label,
        severity=annotation.severity,
        source_side=source_side,
        page_number=page_number,
        bbox=bbox,
        output_image_path=str(output_image_path) if output_image_path else None,
        render_status=status,
        metadata=dict(metadata or {}),
    )


def _clamp_int(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, int(value)))
