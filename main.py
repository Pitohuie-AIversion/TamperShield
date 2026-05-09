from pathlib import Path
from typing import List

import pandas as pd

from core.align_compare import compare_cells_with_tolerance
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
OUTPUT_DIR = DATA_DIR / "output"


def run_tamper_shield_pipeline(
    scan_image_name: str,
    base_pdf_name: str,
    key_columns: List[str],
) -> None:
    """
    End-to-end tamper comparison pipeline.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scan_path = RAW_SCANS_DIR / scan_image_name
    base_path = BASE_DOCS_DIR / base_pdf_name
    clean_scan_path = OUTPUT_DIR / f"cleaned_{scan_path.stem}.png"
    report_path = OUTPUT_DIR / f"audit_report_{scan_path.stem}.csv"

    print(f"[Step 1] Preprocess scan: {scan_path.name}")
    preprocess_pipeline(str(scan_path), str(clean_scan_path))

    print("[Step 2] Parse scan layout with PP-Structure")
    engine = build_pp_structure(use_gpu=False)
    blocks = parse_layout_to_blocks(engine, str(clean_scan_path))
    scan_dfs = extract_tables_to_dataframes(blocks)
    if not scan_dfs:
        print("[Abort] No table found in scan file.")
        return
    scan_df = scan_dfs[0]

    print(f"[Step 3] Parse base document: {base_path.name}")
    base_dfs = extract_tables_from_native_pdf(str(base_path))
    if not base_dfs:
        print("[Abort] No table found in base file.")
        return
    base_df = base_dfs[0]

    print("[Step 4] Align and compare with tolerance")
    diff_report = compare_cells_with_tolerance(
        left_df=base_df,
        right_df=scan_df,
        key_columns=key_columns,
        max_distance=2,
    )

    print("[Step 5] Export report")
    if diff_report.empty:
        print("[PASS] No significant mismatch found.")
        return

    diff_report.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[ALERT] Found {len(diff_report)} potential mismatches.")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    print("Pipeline entry is ready. Call run_tamper_shield_pipeline(...) to run.")

