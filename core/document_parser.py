"""
Minimal document parser for the Document-first TamperShield pipeline.

This module converts PDF, DOCX, and image inputs into shared document models.
It does not implement page alignment, content comparison, OCR, table matching,
cell comparison, evidence indexing, or report generation.
"""

from pathlib import Path
from typing import Any

import fitz
from docx import Document

from core.document_models import (
    BoundingBox,
    DocumentElement,
    DocumentPage,
    FileType,
    ParsedDocument,
)


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def detect_file_type(file_path: str | Path) -> FileType:
    """Detect a supported document type from the filename extension only."""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    return "unknown"


def parse_document(file_path: str | Path) -> ParsedDocument:
    """Parse a file into a ParsedDocument using the minimal Phase 3 entrypoint."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(path))

    file_type = detect_file_type(path)

    if file_type == "pdf":
        return parse_pdf_document(path)
    if file_type == "docx":
        return parse_docx_document(path)
    if file_type == "image":
        return parse_image_document(path)

    return ParsedDocument(
        file_path=str(path),
        file_type="unknown",
        metadata={
            "source_file": str(path),
            "source_format": "unknown",
        },
    )


def parse_pdf_document(file_path: str | Path) -> ParsedDocument:
    """Parse PDF pages and text blocks with PyMuPDF."""
    path = Path(file_path)
    pages: list[DocumentPage] = []

    with fitz.open(str(path)) as pdf:
        for page_index, pdf_page in enumerate(pdf):
            page_number = page_index + 1
            plain_text = pdf_page.get_text("text") or ""
            document_page = DocumentPage(
                page_number=page_number,
                plain_text=plain_text,
                metadata={
                    "source_file": str(path),
                    "source_format": "pdf",
                    "page_index": page_index,
                },
            )

            blocks = pdf_page.get_text("blocks") or []
            text_block_count = 0
            for block_index, block in enumerate(blocks):
                block_text = _pdf_block_text(block)
                if not block_text.strip():
                    continue

                bbox = BoundingBox(
                    page_number=page_number,
                    x0=float(block[0]),
                    y0=float(block[1]),
                    x1=float(block[2]),
                    y1=float(block[3]),
                )
                document_page.add_element(
                    DocumentElement(
                        element_id=f"pdf-page-{page_number}-block-{block_index}",
                        element_type="paragraph",
                        page_number=page_number,
                        text=block_text,
                        bbox=bbox,
                        raw=block,
                        metadata={
                            "source_file": str(path),
                            "source_format": "pdf",
                            "page_index": page_index,
                            "block_index": block_index,
                        },
                    )
                )
                text_block_count += 1

            if text_block_count == 0:
                document_page.add_element(
                    DocumentElement(
                        element_id=f"pdf-page-{page_number}-text-0",
                        element_type="paragraph" if plain_text.strip() else "unknown",
                        page_number=page_number,
                        text=plain_text,
                        metadata={
                            "source_file": str(path),
                            "source_format": "pdf",
                            "page_index": page_index,
                        },
                    )
                )

            pages.append(document_page)

    return ParsedDocument(
        file_path=str(path),
        file_type="pdf",
        pages=pages,
        metadata={
            "source_file": str(path),
            "source_format": "pdf",
        },
    )


def parse_docx_document(file_path: str | Path) -> ParsedDocument:
    """Parse DOCX native paragraphs and tables into a single logical page."""
    path = Path(file_path)
    doc = Document(str(path))
    page = DocumentPage(
        page_number=1,
        metadata={
            "source_file": str(path),
            "source_format": "docx",
            "page_index": 0,
            "pagination": "not_available_in_phase_3",
        },
    )

    for paragraph_index, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue

        page.add_element(
            DocumentElement(
                element_id=f"docx-paragraph-{paragraph_index}",
                element_type="paragraph",
                page_number=1,
                text=text,
                metadata={
                    "source_file": str(path),
                    "source_format": "docx",
                    "paragraph_index": paragraph_index,
                },
            )
        )
    # Phase 3 minimal implementation: paragraphs and tables are extracted in
    # separate passes. Original body-order traversal can be added later.
    table_index = 0
    for table in doc.tables:
        rows = _docx_table_to_rows(table)
        table_text = _flatten_table_text(rows)

        page.add_element(
            DocumentElement(
                element_id=f"docx-table-{table_index}",
                element_type="table",
                page_number=1,
                text=table_text,
                raw=rows,
                metadata={
                    "source_file": str(path),
                    "source_format": "docx",
                    "table_index": table_index,
                },
            )
        )
        table_index += 1

    page.plain_text = "\n".join(
        element.text for element in page.elements if element.text.strip()
    )

    return ParsedDocument(
        file_path=str(path),
        file_type="docx",
        pages=[page],
        metadata={
            "source_file": str(path),
            "source_format": "docx",
        },
    )


def parse_image_document(file_path: str | Path) -> ParsedDocument:
    """Register an image as a single-page document without running OCR."""
    path = Path(file_path)
    page = DocumentPage(
        page_number=1,
        page_image_path=str(path),
        metadata={
            "source_file": str(path),
            "source_format": "image",
            "page_index": 0,
        },
    )
    page.add_element(
        DocumentElement(
            element_id="image-page-1-image-0",
            element_type="image",
            page_number=1,
            metadata={
                "source_file": str(path),
                "source_format": "image",
                "page_index": 0,
            },
        )
    )

    return ParsedDocument(
        file_path=str(path),
        file_type="image",
        pages=[page],
        metadata={
            "source_file": str(path),
            "source_format": "image",
        },
    )


def _pdf_block_text(block: Any) -> str:
    if isinstance(block, (tuple, list)) and len(block) > 4:
        return str(block[4] or "")
    return ""


def _docx_table_to_rows(table: Any) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table.rows:
        rows.append([cell.text.strip() for cell in row.cells])
    return rows


def _flatten_table_text(rows: list[list[str]]) -> str:
    parts: list[str] = []
    for row in rows:
        for cell_text in row:
            if cell_text:
                parts.append(cell_text)
    return " ".join(parts)
