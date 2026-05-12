"""
Unified data models for the Document-first TamperShield pipeline.

This module contains lightweight containers only. It does not implement
document parsing, page alignment, content comparison, OCR, PDF/DOCX handling,
table matching, or report generation.
"""

from dataclasses import dataclass, field
from typing import Any, Literal, Optional


ElementType = Literal[
    "paragraph",
    "title",
    "table",
    "image",
    "header",
    "footer",
    "signature",
    "blank",
    "unknown",
]

FileType = Literal["pdf", "docx", "image", "unknown"]

DiffType = Literal[
    "page_added",
    "page_deleted",
    "page_reordered",
    "text_modified",
    "paragraph_added",
    "paragraph_deleted",
    "image_modified",
    "image_replaced",
    "signature_modified",
    "table_added",
    "table_deleted",
    "table_cell_modified",
    "table_row_added",
    "table_row_deleted",
    "layout_changed",
    "unknown",
]

Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class BoundingBox:
    page_number: int
    x0: float
    y0: float
    x1: float
    y1: float

    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    def height(self) -> float:
        return max(0.0, self.y1 - self.y0)

    def area(self) -> float:
        return self.width() * self.height()


@dataclass
class DocumentElement:
    element_id: str
    element_type: ElementType
    page_number: int
    text: str = ""
    bbox: Optional[BoundingBox] = None
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentPage:
    page_number: int
    elements: list[DocumentElement] = field(default_factory=list)
    plain_text: str = ""
    page_image_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_element(self, element: DocumentElement) -> None:
        self.elements.append(element)

    def get_elements_by_type(self, element_type: ElementType) -> list[DocumentElement]:
        return [
            element
            for element in self.elements
            if element.element_type == element_type
        ]

    def has_tables(self) -> bool:
        return any(element.element_type == "table" for element in self.elements)

    def is_blank(self) -> bool:
        if self.plain_text.strip():
            return False

        if not self.elements:
            return True

        return all(element.element_type == "blank" for element in self.elements)


@dataclass
class ParsedDocument:
    file_path: str
    file_type: FileType
    pages: list[DocumentPage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def page_count(self) -> int:
        return len(self.pages)

    def get_page(self, page_number: int) -> Optional[DocumentPage]:
        for page in self.pages:
            if page.page_number == page_number:
                return page

        return None

    def all_elements(self) -> list[DocumentElement]:
        elements: list[DocumentElement] = []
        for page in self.pages:
            elements.extend(page.elements)
        return elements


@dataclass
class Difference:
    diff_type: DiffType
    severity: Severity
    candidate_page: Optional[int]
    baseline_page: Optional[int]
    candidate_element_id: Optional[str] = None
    baseline_element_id: Optional[str] = None
    message: str = ""
    location: Optional[BoundingBox] = None
    metadata: dict[str, Any] = field(default_factory=dict)
