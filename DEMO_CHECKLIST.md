# TamperShield Demo Checklist

This checklist is used before and during a TamperShield Document-first demo. It verifies environment readiness, input files, command safety, expected outputs, and known limitations.

## Environment Checklist

- [ ] Conda environment `tamper_shield` is available.
- [ ] `conda run -n tamper_shield python` can start Python.
- [ ] LibreOffice is installed.
- [ ] `soffice --version` returns LibreOffice version.
- [ ] LibreOffice path is not prepended before Conda Python in `PATH`.
- [ ] If LibreOffice path is needed, it is appended or `soffice.exe` is called explicitly.

## Input Files Checklist

- [ ] `data/base_docs/` exists.
- [ ] At least one `.pdf` file exists in `data/base_docs/`.
- [ ] At least one `.docx` file exists in `data/base_docs/`.
- [ ] Input files are not modified during the demo.
- [ ] Input file discovery uses `Path.glob()` in demo commands.
- [ ] Long Chinese paths are not embedded directly in `python -c` commands.

## Read-Only Pipeline Checklist

- [ ] Preferred CLI command `python tools/run_document_demo.py --auto-discover --input-dir data/base_docs` is available.
- [ ] The read-only command from `DEMO_WORKFLOW.md` is run first.
- [ ] No `report_output_path` is passed in the read-only command.
- [ ] No files are written during the read-only run.
- [ ] `EvidenceIndex.summary()` is printed.
- [ ] `EvidenceIndex.metadata` is printed.
- [ ] The current validated reference is approximately:
  - `candidate_page_count = 39`
  - `baseline_page_count = 44`
  - `difference_count = 69`
  - `page_reordered = 0`
  - `requires_table_compare_count = 0`

## Report Export Checklist

- [ ] Report export is performed only after explicit write permission.
- [ ] `report_output_path` is explicitly provided.
- [ ] `allow_write=True` is explicitly provided.
- [ ] CLI report export uses `--report-output` and `--allow-write`.
- [ ] `overwrite=False` is used by default.
- [ ] The target report file does not already exist before writing.
- [ ] The report is written under `data/output/`.
- [ ] No source file or input file is overwritten.

## Report Review Checklist

- [ ] Report is viewed with `Get-Content -Encoding UTF8`.
- [ ] Report contains `Summary`.
- [ ] Report contains `Metadata`.
- [ ] Report contains `Evidence by Candidate Page`.
- [ ] Report contains `Evidence Without Candidate Page` when applicable.
- [ ] Report contains `Review context` for page-level evidence.
- [ ] Report contains `Page profile` for page-level evidence.
- [ ] Full Metadata JSON block is preserved.

## Evidence Interpretation Checklist

- [ ] `Difference.severity` is treated as the primary evidence severity.
- [ ] `suggested_review_severity` is treated only as review context.
- [ ] `page_issue_category` is used to understand unmatched page nature.
- [ ] `requires_table_compare_count=0` is not interpreted as proof that the original document has no tables.
- [ ] High or unknown evidence is marked for manual review.
- [ ] The report is not used as an automatic tamper decision.

## Safety / Do Not Checklist

- [ ] Do not use an LLM to decide whether a document is tampered.
- [ ] Do not use an LLM to complete missing document content.
- [ ] Do not use table comparison as the main entrypoint.
- [ ] Do not write reports by default.
- [ ] Do not overwrite existing reports without explicit permission.
- [ ] Do not prepend LibreOffice's program directory before Conda Python in `PATH`.
- [ ] Do not treat console mojibake as an internal encoding bug without checking UTF-8 file content.

## Known Limitations Checklist

- [ ] DOCX rendered PDF pagination depends on LibreOffice, fonts, profile, and input file version.
- [ ] Rendered PDF parsing does not preserve native DOCX table structure as `table` elements.
- [ ] Native DOCX table metadata should be considered as a future auxiliary source.
- [ ] Current report is Markdown only.
- [ ] HTML / PDF report export is a future improvement.
- [ ] Current demo uses one PDF and one DOCX from `data/base_docs/`.

## Demo Pass Criteria

The demo is considered successful when:

- [ ] Read-only pipeline runs without errors.
- [ ] `EvidenceIndex.summary()` is produced.
- [ ] Metadata includes candidate and baseline file information.
- [ ] Optional report export writes exactly one Markdown file when explicitly allowed.
- [ ] Markdown report can be viewed with UTF-8 encoding.
- [ ] Report includes evidence records with page-level review context.
- [ ] No source files are modified.
- [ ] No code files are modified.
