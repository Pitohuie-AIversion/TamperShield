from pathlib import Path
from typing import List

import docx
import fitz
import pdfplumber


def extract_text_from_pdf_pymupdf(pdf_path: str) -> str:
    """
    Extract text from editable PDF with PyMuPDF.
    """
    texts: List[str] = []
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            texts.append(page.get_text("text"))
    return "\n".join(texts).strip()


def extract_text_from_pdf_pdfplumber(pdf_path: str) -> str:
    """
    Extract text from PDF with pdfplumber as fallback.
    """
    texts: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return "\n".join(texts).strip()


def extract_text_from_docx(docx_path: str) -> str:
    """
    Extract text from Word document.
    """
    document = docx.Document(docx_path)
    return "\n".join(p.text for p in document.paragraphs).strip()


def detect_file_type(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    raise ValueError(f"Unsupported file type: {suffix}")

