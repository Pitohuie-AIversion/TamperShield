from pathlib import Path
from typing import List, Optional, Sequence

import pandas as pd

from core.align_compare import compare_cells_with_tolerance
from core.data_normalize import normalize_dataframe
from core.evidence_index import EvidenceIndex
from core.ocr_engine import (
    build_pp_structure,
    extract_tables_to_dataframes,
    parse_layout_to_blocks,
)
from core.pre_processing import preprocess_pipeline
from core.text_parser import extract_tables_from_native_pdf


DATA_DIR = Path("data")
RAW_SCANS_DIR = DATA_DIR / "raw_scans"
BASE_DOCS_DIR = DATA_DIR / "base_docs"


def ensure_write_allowed(
    path: Path,
    allow_write: bool,
    overwrite: bool,
) -> None:
    if not allow_write:
        raise PermissionError("[Output Blocked] - Permission Required")

    if path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists and overwrite=False: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)


def run_tamper_shield_pipeline(
    scan_image_name: str,
    base_pdf_name: str,
    key_columns: List[str],
    clean_scan_output_path: str,
    report_output_path: str,
    numeric_columns: Optional[Sequence[str]] = None,
    allow_write: bool = False,
    overwrite: bool = False,
    write_empty_report: bool = True,
) -> Optional[pd.DataFrame]:
    """
    End-to-end tamper comparison pipeline.

    No output path is generated automatically.
    Writing is allowed only when allow_write=True.
    """
    scan_path = RAW_SCANS_DIR / scan_image_name
    base_path = BASE_DOCS_DIR / base_pdf_name

    clean_scan_path = Path(clean_scan_output_path)
    report_path = Path(report_output_path)

    ensure_write_allowed(clean_scan_path, allow_write=allow_write, overwrite=overwrite)
    ensure_write_allowed(report_path, allow_write=allow_write, overwrite=overwrite)

    print(f"[Step 1] Preprocess scan: {scan_path.name}")
    preprocess_pipeline(
        image_path=str(scan_path),
        output_path=str(clean_scan_path),
        mode="gray",
        enable_deskew=True,
    )

    print("[Step 2] Parse scan layout with PP-Structure")
    engine = build_pp_structure(use_gpu=False)
    blocks = parse_layout_to_blocks(engine, str(clean_scan_path))
    scan_dfs = extract_tables_to_dataframes(blocks)

    if not scan_dfs:
        print("[Abort] No table found in scan file.")
        return None

    scan_df = normalize_dataframe(
        scan_dfs[0],
        key_columns=key_columns,
        numeric_columns=numeric_columns,
    )

    print(f"[Step 3] Parse base document: {base_path.name}")
    base_dfs = extract_tables_from_native_pdf(str(base_path))

    if not base_dfs:
        print("[Abort] No table found in base file.")
        return None

    base_df = normalize_dataframe(
        base_dfs[0],
        key_columns=key_columns,
        numeric_columns=numeric_columns,
    )

    print("[Step 4] Align and compare with tolerance")
    diff_report = compare_cells_with_tolerance(
        left_df=base_df,
        right_df=scan_df,
        key_columns=key_columns,
        max_distance=2,
        numeric_columns=numeric_columns,
        numeric_tolerance="0.01",
    )

    if diff_report.empty:
        print("[PASS] No significant mismatch found.")

        if write_empty_report:
            diff_report.to_csv(report_path, index=False, encoding="utf-8-sig")
            print(f"PASS report saved to: {report_path}")

        return diff_report

    print("[Step 5] Export report")
    diff_report.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[ALERT] Found {len(diff_report)} potential mismatches.")
    print(f"Report saved to: {report_path}")

    return diff_report


def run_document_first_pipeline(
    candidate_file: str,
    baseline_file: str,
    key_columns: Optional[Sequence[str]] = None,
    numeric_columns: Optional[Sequence[str]] = None,
    page_match_threshold: float = 0.75,
    page_low_confidence_threshold: float = 0.45,
    page_search_window: int = 2,
    page_text_similarity_threshold: float = 0.98,
    report_output_path: Optional[str] = None,
    allow_write: bool = False,
    overwrite: bool = False,
    enable_ocr: bool = False,
    enable_preprocess: bool = False,
) -> EvidenceIndex:
    """
    Run the Document-first comparison pipeline.

    By default, this function only returns an EvidenceIndex and does not write
    files. If report_output_path is provided, a Markdown report is generated and
    written only when allow_write=True.
    """
    from core.document_pipeline import compare_documents

    index = compare_documents(
        candidate_file=candidate_file,
        baseline_file=baseline_file,
        key_columns=key_columns,
        numeric_columns=numeric_columns,
        enable_ocr=enable_ocr,
        enable_preprocess=enable_preprocess,
        page_match_threshold=page_match_threshold,
        page_low_confidence_threshold=page_low_confidence_threshold,
        page_search_window=page_search_window,
        page_text_similarity_threshold=page_text_similarity_threshold,
    )

    if report_output_path is not None:
        from core.report_generator import generate_markdown_report, write_text_report

        report_text = generate_markdown_report(index)
        write_text_report(
            report_text,
            output_path=report_output_path,
            allow_write=allow_write,
            overwrite=overwrite,
        )

    return index


if __name__ == "__main__":
    print(
        "Pipeline entries are ready. "
        "Use run_tamper_shield_pipeline(...) for the legacy table-first flow, "
        "or run_document_first_pipeline(...) for the Document-first flow."
    )
