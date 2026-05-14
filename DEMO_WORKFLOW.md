# TamperShield Demo Workflow

This document describes the validated Document-first demo workflow for comparing a candidate PDF against a baseline DOCX and exporting an evidence-based Markdown report. The report presents evidence and review context; it is not a final tamper judgement.

## Demo Goal

This demo validates the TamperShield Document-first workflow for:

```text
one candidate PDF
        vs
one baseline DOCX
```

The workflow runs:

```text
document parsing
page alignment
content comparison
evidence indexing
optional Markdown report export
```

Table comparison is not the main entrypoint. `table_compare` is a document sub-capability and is only triggered when page-level evidence indicates that table inspection is needed.

## Current Validated Baseline

```text
candidate_page_count = 39
baseline_page_count = 44
difference_count = 69
page_reordered = 0
requires_table_compare_count = 0
```

The baseline DOCX is parsed as 44 pages through LibreOffice rendered PDF pagination.

## Environment Requirements

```text
Conda environment: tamper_shield
LibreOffice: 26.2.3.2
LibreOffice path: X:\Program Files\LibreOffice\program\soffice.exe
Python command should be run through conda run -n tamper_shield
```

Do not prepend LibreOffice's `program` directory to `PATH` before running `conda run ... python`. If it is prepended, `python` may resolve to LibreOffice's bundled `python-core` instead of the Conda environment Python.

If LibreOffice needs to be added to `PATH`, append it to the end of `PATH`, or call `soffice.exe` explicitly.

## Quick Start

1. Run the read-only pipeline command first.
2. Export a Markdown report only after confirming the output path and write permission.

Use the command in [Read-Only Run Command](#read-only-run-command).

Use the command in [Explicit Markdown Report Export Command](#explicit-markdown-report-export-command) only when writing is permitted.

## Input Files

Use the standard input directory:

```text
data/base_docs/*.pdf
data/base_docs/*.docx
```

Prefer discovering input files with `Path.glob()` instead of embedding long Chinese file names directly inside `python -c` strings. This avoids confusing stdout display behavior in some PowerShell / `conda run` environments.

## Preferred CLI Demo Command

```powershell
conda run -n tamper_shield python tools/run_document_demo.py --auto-discover --input-dir data/base_docs
```

This command is read-only by default and does not write a report.

## Read-Only Run Command

This command runs the Document-first pipeline and prints the in-memory `EvidenceIndex` summary and metadata.

```powershell
conda run -n tamper_shield python -c "from pathlib import Path; from main import run_document_first_pipeline; pdf=list(Path('data/base_docs').glob('*.pdf'))[0]; docx=list(Path('data/base_docs').glob('*.docx'))[0]; idx=run_document_first_pipeline(candidate_file=pdf, baseline_file=docx); print(idx.summary()); print(idx.metadata)"
```

This command does not write files. `report_output_path` defaults to `None`.

## Expected Read-Only Output

Current validated reference:

```text
candidate_page_count = 39
baseline_page_count = 44
difference_count = 69
page_reordered = 0
requires_table_compare_count = 0
```

Exact difference subtype counts may change if the parser, aligner, or input files change, but this baseline is the currently validated reference.

## Explicit Markdown Report Export Command

Only run this command when the user explicitly allows writing a report file.

```powershell
conda run -n tamper_shield python -c "from pathlib import Path; from main import run_document_first_pipeline; pdf=list(Path('data/base_docs').glob('*.pdf'))[0]; docx=list(Path('data/base_docs').glob('*.docx'))[0]; idx=run_document_first_pipeline(candidate_file=pdf, baseline_file=docx, report_output_path=r'data/output/demo_report.md', allow_write=True, overwrite=False); print(idx.summary())"
```

Report export requirements:

- Always pass an explicit `report_output_path`.
- Always pass `allow_write=True` when writing is intended.
- Keep `overwrite=False` by default.
- Do not overwrite existing reports unless the user explicitly asks for overwrite behavior.

## Report Export Safety Notes

- `allow_write=True` is required for writing.
- `overwrite=False` prevents accidental overwrite.
- If the output file already exists, choose a new path or explicitly decide whether overwrite is acceptable.
- Do not write reports into source directories.
- Recommended output directory: `data/output/`.

## View Markdown Report

Use explicit UTF-8 decoding in PowerShell:

```powershell
Get-Content data/output/demo_report.md -Encoding UTF8 -TotalCount 120
```

If `-Encoding UTF8` is omitted, Chinese paths or Chinese document text may display incorrectly in some PowerShell environments. That is usually a display-layer issue and does not mean the Markdown file is internally encoded incorrectly.

## Report Contents

The Markdown report includes:

```text
Summary
Metadata
Evidence by Candidate Page
Evidence Without Candidate Page
Review context
Page profile
Full Metadata JSON
```

Page-level review metadata may include:

```text
page_issue_category
suggested_review_severity
classification_reason
page_profile
```

`Difference.severity` is the primary evidence severity. `suggested_review_severity` is a page-profile suggestion for manual review context only. It does not replace the primary severity.

## Evidence Interpretation Notes

- `Difference.severity` is the primary evidence severity.
- `suggested_review_severity` is only a review-context hint.
- `page_issue_category` explains the likely nature of unmatched pages.
- The report does not decide whether the document is tampered.
- Human review is required for high-risk or unknown evidence.

## Current Page Added / Page Deleted Review Examples

Current real-document validation includes these representative page-level classifications:

```text
C2  page_added   likely_toc_or_cover_format_noise / medium
C39 page_added   likely_page_number_residue / low

B2/B3 page_deleted likely_toc_or_cover_format_noise / medium
B14   page_deleted unknown_needs_manual_review / high
B22   page_deleted likely_pagination_split_noise / medium
B27/B45 page_deleted likely_short_signature_or_date_page / low
B33/B42 page_deleted likely_attachment_start_page_needs_manual_review / high
```

These classifications are not final audit conclusions. They only help reviewers understand the likely page nature behind `page_added` and `page_deleted` evidence.

## Troubleshooting

### Chinese Text Displays Incorrectly

Use `Get-Content -Encoding UTF8` when viewing Markdown reports in PowerShell.

Prefer `Path.glob()` in demo commands instead of embedding long Chinese paths directly inside `python -c` strings.

This is usually a console display / command-wrapper issue, not necessarily a file encoding bug.

### LibreOffice / soffice Not Found

Check `where soffice`.

Check `soffice --version`.

Do not prepend LibreOffice to `PATH` before `conda run`.

Append the LibreOffice path or call `soffice.exe` explicitly.

### report_output_path Write Fails

Check whether `allow_write=True` was provided.

Check whether the output file already exists.

Check `overwrite=False`.

## Known Limitations

1. In the rendered PDF path, DOCX native table structure is not preserved as `table` elements.
2. `requires_table_compare_count=0` does not mean the original document has no tables.
3. LibreOffice profile, fonts, and input file version may affect DOCX rendered pagination.
4. Chinese paths may display incorrectly in PowerShell / `conda run` stdout even when Python strings and Markdown files are valid Unicode / UTF-8.
5. The current report does not output `tampered / not tampered / safe / unsafe / PASS / FAIL` conclusions.
6. The current system outputs evidence; final review still requires manual review.

## Do Not

- Do not use an LLM to decide whether a document is tampered.
- Do not use an LLM to complete document content.
- Do not write reports by default.
- Do not automatically overwrite reports.
- Do not use table comparison as the main entrypoint.
- Do not prepend the LibreOffice path to `PATH`.
- Do not interpret `requires_table_compare_count=0` as proof that the document has no tables.

## Next Improvement Backlog

- Identify table-like blocks in rendered PDF pages.
- Preserve DOCX native table metadata as auxiliary structure.
- Improve classification rules for table-of-contents pages, cover pages, and signature pages.
- Add demo dataset management.
- Add a friendlier CLI wrapper.
- Add HTML / PDF report export, still based only on `EvidenceIndex`.
