"""
Independent in-memory Document-first pipeline dispatcher.

This module connects parsing, page alignment, content comparison, optional
table-level refinement, and evidence indexing. It does not replace main.py,
call OCR or preprocessing, write files, export reports, or make audit
judgments.
"""

from pathlib import Path
from typing import Optional, Sequence

from core.content_compare import compare_page
from core.document_models import Difference, ParsedDocument
from core.evidence_index import EvidenceIndex, build_evidence_index
from core.page_aligner import align_pages
from core.table_compare import compare_page_tables_if_needed


def collect_document_differences(
    candidate_doc: ParsedDocument,
    baseline_doc: ParsedDocument,
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Sequence[str]] = None,
    page_match_threshold: float = 0.75,
    page_low_confidence_threshold: float = 0.45,
    page_search_window: int = 2,
    page_text_similarity_threshold: float = 0.98,
) -> list[Difference]:
    """Collect deterministic page, element, and optional table differences."""
    alignments = align_pages(
        candidate_doc.pages,
        baseline_doc.pages,
        match_threshold=page_match_threshold,
        low_confidence_threshold=page_low_confidence_threshold,
        search_window=page_search_window,
    )

    differences: list[Difference] = []
    for alignment in alignments:
        page_differences = compare_page(
            alignment,
            page_text_similarity_threshold=page_text_similarity_threshold,
        )
        differences.extend(page_differences)

        if alignment.candidate_page is None or alignment.baseline_page is None:
            continue

        table_differences = compare_page_tables_if_needed(
            alignment.candidate_page,
            alignment.baseline_page,
            page_differences,
            key_columns=key_columns,
            numeric_columns=numeric_columns,
        )
        differences.extend(table_differences)

    return differences


def compare_parsed_documents(
    candidate_doc: ParsedDocument,
    baseline_doc: ParsedDocument,
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Sequence[str]] = None,
    page_match_threshold: float = 0.75,
    page_low_confidence_threshold: float = 0.45,
    page_search_window: int = 2,
    page_text_similarity_threshold: float = 0.98,
) -> EvidenceIndex:
    """Compare two already parsed documents and return an evidence index."""
    differences = collect_document_differences(
        candidate_doc,
        baseline_doc,
        key_columns=key_columns,
        numeric_columns=numeric_columns,
        page_match_threshold=page_match_threshold,
        page_low_confidence_threshold=page_low_confidence_threshold,
        page_search_window=page_search_window,
        page_text_similarity_threshold=page_text_similarity_threshold,
    )

    metadata = {
        "candidate_file": candidate_doc.file_path,
        "baseline_file": baseline_doc.file_path,
        "candidate_file_type": candidate_doc.file_type,
        "baseline_file_type": baseline_doc.file_type,
        "candidate_page_count": candidate_doc.page_count(),
        "baseline_page_count": baseline_doc.page_count(),
        "difference_count": len(differences),
    }

    return build_evidence_index(differences, metadata=metadata)


def compare_documents(
    candidate_file: str | Path,
    baseline_file: str | Path,
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Sequence[str]] = None,
    page_match_threshold: float = 0.75,
    page_low_confidence_threshold: float = 0.45,
    page_search_window: int = 2,
    page_text_similarity_threshold: float = 0.98,
    enable_ocr: bool = False,
    enable_preprocess: bool = False,
) -> EvidenceIndex:
    """Parse and compare two document files through the Document-first pipeline."""
    from core.document_parser import parse_document

    candidate_doc = parse_document(
        candidate_file,
        enable_ocr=enable_ocr,
        enable_preprocess=enable_preprocess,
    )
    baseline_doc = parse_document(
        baseline_file,
        enable_ocr=enable_ocr,
        enable_preprocess=enable_preprocess,
    )

    return compare_parsed_documents(
        candidate_doc,
        baseline_doc,
        key_columns=key_columns,
        numeric_columns=numeric_columns,
        page_match_threshold=page_match_threshold,
        page_low_confidence_threshold=page_low_confidence_threshold,
        page_search_window=page_search_window,
        page_text_similarity_threshold=page_text_similarity_threshold,
    )
