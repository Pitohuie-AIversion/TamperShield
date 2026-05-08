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

import pandas as pd

def extract_tables_from_native_pdf(pdf_path: str) -> List[pd.DataFrame]:
    """
    使用 pdfplumber 从原生可编辑 PDF 中提取表格并转换为 DataFrame。
    作为我们比对的“绝对正确基准”。
    """
    dfs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                # 将二维列表转为 DataFrame，假设第一行是表头
                # 清理 None 值为 空字符串
                cleaned_table = [[cell if cell is not None else "" for cell in row] for row in table]
                if len(cleaned_table) > 1:
                    df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                    dfs.append(df)
    return dfs