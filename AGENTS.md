# AGENTS.md

## Required Reading

Before making any code change, every AI agent must read:

1. `PROJECT_RULES.md`
2. `TODO.md`
3. Relevant files under `core/`
4. Relevant scripts under `tools/`
5. `main.py` if the task touches the pipeline entrypoint

Do not modify code before understanding the existing pipeline, public interfaces, and dependency relationships.

## Project Mission

TamperShield is a Document-first deterministic anti-tampering comparison system for engineering documents. It is not a table comparison tool.

The project compares:

```text
candidate document
        vs
baseline document
```

The main pipeline is:

```text
candidate document
        vs
baseline document
        ↓
document_parser
        ↓
page_aligner
        ↓
content_compare
        ↓
table_compare, only when needed
        ↓
evidence_index
        ↓
traceable report
```

The system must extract, normalize, align, compare, and report differences across complete engineering documents, including pages, paragraphs, titles, tables, images, signatures, headers, footers, attachments, blank pages, and layout regions.

This is not a general OCR project. It is an audit-oriented, deterministic document comparison system.

Tables are document elements, not the primary pipeline. Do not treat table extraction, table matching, or `scan_df` / `base_df` comparison as the document comparison entrypoint. `core/table_matcher.py` and `core/align_compare.py` are table inspection capabilities under `table_compare`, not the main document comparison flow.

## Absolute Truthfulness Rule

Engineering audit does not tolerate hallucination.

Do not use LLMs for:

```text
data extraction
table completion
field guessing
field matching
amount judgment
quantity judgment
audit decision-making
tamper classification
missing cell completion
semantic correction
```

All final extracted data and comparison results must come from:

```text
visual coordinates
OCR outputs
native PDF structures
image processing
physical table structure
pandas DataFrame logic
deterministic comparison rules
```

LLMs may only be used for:

```text
code assistance
debugging
workflow design
rule writing
documentation
test-command generation
report wording
```

LLMs must not participate in final audit data generation or audit judgment.

## Current Development Focus

The Document-first core pipeline and optional `main.py` integration have been implemented.

Completed core modules and entrypoints:

```text
core/document_models.py
core/document_parser.py
core/page_aligner.py
core/content_compare.py
core/table_compare.py
core/evidence_index.py
core/document_pipeline.py
main.py::run_document_first_pipeline(...)
```

The current focus is Phase 9:

```text
report generation from EvidenceIndex
```

Rules for Phase 9:

```text
- Add a report generation layer only when explicitly asked.
- The report generator must take EvidenceIndex as input.
- Do not re-run document parsing inside the report generator.
- Do not re-run page alignment inside the report generator.
- Do not re-run content comparison inside the report generator.
- Do not re-run table comparison inside the report generator.
- Reports must be organized by page and evidence category.
- File writing must be explicit and permission-gated.
- Do not generate default output paths.
```

Do not recreate already completed modules unless explicitly asked.

Before changing code, classify the change as one of:

```text
document_parser
page_aligner
content_compare
table_compare
evidence_index
document_pipeline
report_generator
main.py integration
```

If a task involves complete document comparison, prioritize page-level and element-level evidence chains before table matching or cell comparison. Do not continue tuning PaddleOCR, red seal preprocessing, table matching, or report export unless explicitly requested.

## Hard Technical Rules

### Image Preprocessing

Use only:

```text
opencv-python
numpy
```

Never use HSV masks to directly whiten red seals.

Forbidden pattern:

```python
result[red_mask > 0] = 255
```

Forbidden strategy:

```text
HSV red mask
        ↓
dilate red mask
        ↓
set masked pixels to white
```

Red seal suppression must use:

```text
RGB / R-channel separation
R-channel document gray
inverted morphology
black_text_mask
black stroke restoration
```

Black text protection has higher priority than red seal removal.

Deskew must use:

```text
HoughLinesP
or
cv2.minAreaRect
```

Fixed-angle rotation is forbidden.

### OCR and Table Structure

The default OCR structure route is the verified PaddleOCR 3.x stack:

```text
paddle == 3.2.2
paddleocr == 3.5.0
paddlex == 3.5.1
```

Default structure engine:

```text
PPStructureV3
```

Default output object:

```text
LayoutParsingResultV2
```

Table extraction route:

```text
PPStructureV3.predict()
        ↓
LayoutParsingResultV2
        ↓
table_res_list
        ↓
pred_html
        ↓
pd.read_html(StringIO(pred_html))
        ↓
pandas.DataFrame
```

Do not import PaddleOCR structure classes at module top level.

Forbidden:

```python
from paddleocr import PPStructure
```

Use lazy loading in `core/ocr_engine.py`.

`parse_layout_to_blocks()` must support both:

```text
old callable PPStructure engine
new PPStructureV3 engine with .predict()
```

Keep compatibility with old PaddleOCR 2.x dict output:

```text
block["type"] == "table"
block["res"]["html"]
```

But default development and testing must follow the PaddleOCR 3.x / PPStructureV3 route.

### HTML Table Parsing

When parsing HTML strings from `pred_html`, use:

```python
from io import StringIO
pd.read_html(StringIO(pred_html))
```

Do not use:

```python
pd.read_html(pred_html)
```

The direct literal HTML string form is deprecated by pandas.

### Native PDF Parsing

Native electronic PDFs must be parsed directly.

Use:

```text
PyMuPDF
pdfplumber
```

Do not convert native PDFs to images for OCR unless the user explicitly asks.

If native text or native table structure is available, use it before OCR.

### Table DataFrame Rule

Complete document comparison must start from pages and document elements, not from DataFrames.

Only table elements that need table inspection should become `pandas.DataFrame` before entering `table_compare`.

Do not send raw OCR outputs, dicts, lists, or plain text directly into `align_compare.py`.

Before table comparison, each DataFrame must complete:

```text
column name normalization
text cleanup
merged cell expansion
blank cell cleanup
numeric field cleanup
key column confirmation
source metadata preservation
```

Merged cells must be expanded with deterministic logic such as:

```python
df.ffill()
```

Text tolerance must use Levenshtein edit distance.

Numeric comparison must use cleaned numeric values. Amount-like fields should use `Decimal` and an explicit tolerance such as `0.01`.

## Column Mapping Rule

If `scan_df` and `base_df` column names do not match, do not modify `align_compare.py` first.

Use a deterministic column mapping layer.

Suggested future module, only after user confirmation:

```text
core/column_mapping.py
```

Do not create this file unless the user explicitly allows file creation.

Possible function:

```python
def normalize_column_aliases(df: pd.DataFrame, column_aliases: dict[str, str]) -> pd.DataFrame:
    ...
```

Column aliases must be explicitly provided or confirmed by the user.

Example:

```python
column_aliases = {
    "项目名称": "分项",
    "澄清内容": "澄清项",
    "答复": "回复",
}
```

Do not use an LLM to guess field correspondence.

## Write Restrictions

By default, an agent may:

```text
read files
inspect code
analyze errors
propose patches
provide replacement code blocks
provide test commands
summarize findings
```

By default, an agent may not:

```text
create files
modify files
overwrite files
delete files
move files
rename files
export files
save files
commit changes
```

If writing is required and permission is not explicit, stop and output:

```text
[Output Blocked] - Permission Required
```

Do not invent output paths or filenames. Ask for explicit path and overwrite permission first.

## Files That Must Not Be Broken

Keep these public interfaces stable unless the user explicitly approves a breaking change:

```text
core/pre_processing.py
    preprocess_pipeline(...)
    remove_red_seal(...)
    estimate_skew_angle(...)
    deskew_image(...)

core/ocr_engine.py
    build_pp_structure(...)
    parse_layout_to_blocks(...)
    extract_tables_with_metadata(...)
    extract_tables_to_dataframes(...)
    inspect_structure_output(...)

core/data_normalize.py
    normalize_dataframe(...)
    expand_merged_cells(...)
    attach_source_metadata(...)

core/align_compare.py
    compare_cells_with_tolerance(...)

core/document_pipeline.py
    collect_document_differences(...)
    compare_parsed_documents(...)
    compare_documents(...)

main.py
    run_tamper_shield_pipeline(...)
    run_document_first_pipeline(...)
```

Do not remove backward-compatible entrypoints.

If parameters must change, preserve old parameters through explicit compatibility arguments or `**kwargs`.

## Current Test Commands

Check Git conflict markers:

```powershell
Select-String -Path core/*.py,tools/*.py -Pattern "<<<<<<<|=======|>>>>>>>"
```

Import checks:

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"

python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"

python -c "from core.data_normalize import normalize_dataframe, expand_merged_cells, attach_source_metadata; print('data_normalize import ok')"

python -c "from core.text_parser import extract_tables_from_native_pdf_with_metadata; print('text_parser import ok')"

python -c "from core.align_compare import compare_cells_with_tolerance; print('align_compare import ok')"
```

Test scanned table extraction:

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; img = next(Path('data/output/real_scan_tuning').glob('*.png')); print('image:', img); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); print('tables:', len(tables)); print(tables[0]['source_style'] if tables else 'no table'); print(tables[0]['df'].head() if tables else 'no table')"
```

Test scanned DataFrame normalization:

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; img = next(Path('data/output/real_scan_tuning').glob('*.png')); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); df = tables[0]['df']; ndf = normalize_dataframe(df, key_columns=['序号']); print(ndf.head()); print(ndf.columns.tolist())"
```

Test native PDF table extraction:

Before running native PDF extraction, check whether `data/base_docs/` contains at least one PDF.

```powershell
python -c "from pathlib import Path; from core.text_parser import extract_tables_from_native_pdf_with_metadata; pdfs = list(Path('data/base_docs').glob('*.pdf')); print('pdf_count:', len(pdfs)); assert pdfs, 'No PDF found in data/base_docs/'; pdf = pdfs[0]; print('pdf:', pdf); tables = extract_tables_from_native_pdf_with_metadata(str(pdf)); print('tables:', len(tables)); print(tables[0]['df'].head() if tables else 'no table'); print(tables[0]['df'].columns.tolist() if tables else 'no table')"
```

Minimal scan/base comparison test:

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.text_parser import extract_tables_from_native_pdf; from core.data_normalize import normalize_dataframe; from core.align_compare import compare_cells_with_tolerance; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); pdfs = list(Path('data/base_docs').glob('*.pdf')); print('image_count:', len(imgs)); print('pdf_count:', len(pdfs)); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; assert pdfs, 'No PDF found in data/base_docs/'; img = imgs[0]; pdf = pdfs[0]; engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); scan_df = extract_tables_with_metadata(blocks)[0]['df']; base_df = extract_tables_from_native_pdf(str(pdf))[0]; scan_df = normalize_dataframe(scan_df, key_columns=['序号']); base_df = normalize_dataframe(base_df, key_columns=['序号']); diff = compare_cells_with_tolerance(base_df, scan_df, key_columns=['序号'], max_distance=2); print('diff rows:', len(diff)); print(diff.head())"
```

## Decision Rules

If scan table extraction fails, inspect:

```text
core/ocr_engine.py
extract_tables_with_metadata()
pred_html
table_res_list
```

If scanned DataFrame is malformed, inspect:

```text
PPStructureV3 pred_html
HTML rowspan / colspan
normalize_dataframe()
```

If native PDF extraction fails, inspect:

```text
core/text_parser.py
pdfplumber extraction
native PDF table structure
```

If scan/base columns do not match, do not guess. Ask the user to confirm `column_aliases`.

If key columns are missing, stop and ask the user to confirm `key_columns`.

If numeric columns are unclear, stop and ask the user to confirm `numeric_columns`.

## Prohibited Actions

Never:

```text
use HSV red seal whitening
destroy black text to remove red seal
use fixed-angle deskew
use LLMs to guess table values
use LLMs to complete missing cells
use LLMs to match fields
use LLMs to judge amount equality
send raw OCR text directly into comparison
modify files without permission
commit changes without permission
```

## Expected Agent Output Style

When responding to development tasks:

1. State the current phase.
2. State the files inspected.
3. State the issue found.
4. Give minimal patch or exact code block.
5. Give test commands.
6. Do not add unrelated explanations.

When blocked by missing permission, output only:

```text
[Output Blocked] - Permission Required
```
