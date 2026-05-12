from typing import Dict, List, Sequence

import cv2
import fitz
import numpy as np
import pandas as pd


def imread_unicode_gray(image_path: str) -> np.ndarray:
    data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    return image


def render_pdf_page_to_bgr(
    pdf_path: str,
    page_index: int,
    zoom: float = 2.0,
) -> np.ndarray:
    with fitz.open(pdf_path) as document:
        page = document[page_index]
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(zoom, zoom),
            alpha=False,
        )

    image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height,
        pixmap.width,
        pixmap.n,
    )

    if pixmap.n == 1:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def _normalized_thumbnail(
    gray: np.ndarray,
    size: int = 64,
) -> np.ndarray:
    thumb = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    thumb = thumb.astype(np.float32)
    return (thumb - thumb.mean()) / (thumb.std() + 1e-6)


def _edge_thumbnail(
    gray: np.ndarray,
    size: int = 96,
) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 50, 150)
    return _normalized_thumbnail(edges, size=size)


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    return float((left * right).mean())


def rank_similar_pdf_pages(
    target_image_path: str,
    pdf_path: str,
    top_k: int = 10,
    render_zoom: float = 0.10,
    thumb_size: int = 64,
) -> pd.DataFrame:
    target_gray = imread_unicode_gray(target_image_path)
    target_thumb = _normalized_thumbnail(target_gray, size=thumb_size)
    target_edge = _edge_thumbnail(target_gray, size=thumb_size)

    rows: List[Dict[str, object]] = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(render_zoom, render_zoom),
                alpha=False,
            )
            page_image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
                pixmap.height,
                pixmap.width,
                pixmap.n,
            )

            if pixmap.n == 1:
                page_gray = page_image
            else:
                page_gray = cv2.cvtColor(page_image, cv2.COLOR_RGB2GRAY)

            page_thumb = _normalized_thumbnail(page_gray, size=thumb_size)
            page_edge = _edge_thumbnail(page_gray, size=thumb_size)

            image_score = _correlation(target_thumb, page_thumb)
            edge_score = _correlation(target_edge, page_edge)
            score = image_score * 0.70 + edge_score * 0.30

            rows.append(
                {
                    "page_index": page_index,
                    "page_number": page_index + 1,
                    "score": round(score, 6),
                    "image_score": round(image_score, 6),
                    "edge_score": round(edge_score, 6),
                    "render_width": pixmap.width,
                    "render_height": pixmap.height,
                }
            )

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    return result.sort_values(
        by=["score", "image_score", "edge_score"],
        ascending=False,
    ).head(top_k).reset_index(drop=True)


def extract_tables_from_scan_pdf_pages(
    engine,
    pdf_path: str,
    page_numbers: Sequence[int],
    zoom: float = 2.0,
) -> List[Dict[str, object]]:
    from core.ocr_engine import extract_tables_with_metadata, parse_layout_to_blocks

    tables: List[Dict[str, object]] = []
    for page_number in page_numbers:
        image = render_pdf_page_to_bgr(
            pdf_path=pdf_path,
            page_index=page_number - 1,
            zoom=zoom,
        )
        blocks = parse_layout_to_blocks(engine, image)
        page_tables = extract_tables_with_metadata(blocks)

        for table in page_tables:
            table["scan_pdf_path"] = pdf_path
            table["scan_page_number"] = page_number
            table["scan_page_index"] = page_number - 1
            tables.append(table)

    return tables
