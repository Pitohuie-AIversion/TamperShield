# OCR-backed Document Parser Design

Design document for integrating OCR-backed parsing into the existing Document-first TamperShield pipeline.

## Design Goals

本设计的目标不是重写 OCR，也不是重写 Document-first pipeline。

目标是把现有 `core/pre_processing.py` 和 `core/ocr_engine.py` 中已经验证过的 preprocessing / OCR 能力，作为可选 parser capability 接入现有 Document-first 数据模型：

```text
image / scanned PDF
        ↓
preprocess_pipeline(...)
        ↓
OCR layout / OCR text / OCR table extraction
        ↓
DocumentPage / DocumentElement
        ↓
page_aligner
        ↓
content_compare
        ↓
table_compare, only when needed
        ↓
EvidenceIndex
        ↓
report_generator
```

核心约束：

- OCR output must enter `DocumentPage` / `DocumentElement` before comparison.
- OCR must not directly enter DataFrame-first comparison.
- OCR-backed parsing must be optional and explicit at first.
- OCR-backed parser must preserve evidence metadata where available.

## Non-Goals

- 不重写 `core/pre_processing.py`
- 不重写 `core/ocr_engine.py`
- 不删除 legacy table-first OCR flow
- 不默认启用 OCR
- 不默认把 PDF 转图片 OCR
- 不直接输出最终审计结论
- 不让 OCR result 直接进入 `align_compare.py`
- 不绕过 `EvidenceIndex`

## Existing Reusable Capabilities

### Preprocessing

当前可复用能力：

- `imread_unicode(...)`
- `preprocess_pipeline(..., output_path=None)`
- `deskew_image(...)`
- `remove_red_seal_from_array(...)`
- `extract_black_text_mask(...)`
- `suppress_red_stamp_rgb(...)`
- `enhance_gray_document(...)`
- `adaptive_binarize(...)`

设计约束：

- `preprocess_pipeline(...)` must be called with `output_path=None` in parser path to avoid file writes.
- `imwrite_unicode(...)` 是底层写文件函数，不应在 OCR-backed parser 默认路径中调用。
- `deskew_image(...)` 可保留 `deskew_angle` metadata。
- 红章抑制相关参数应记录到 page 或 element metadata，便于审计复核。

### OCR / PPStructure

当前可复用能力：

- `build_pp_structure(...)`
- `parse_layout_to_blocks(...)`
- `extract_tables_with_metadata(...)`
- `parse_html_table_spans(...)`
- `_safe_get(...)`
- `_extract_html_from_table_item(...)`
- `_iter_table_html_candidates(...)`

设计约束：

- `parse_layout_to_blocks(...)` is the point that actually runs OCR / structure parsing.
- `extract_tables_with_metadata(...)` processes existing OCR blocks and preserves table metadata.
- `extract_tables_to_dataframes(...)` should not be used in the new parser path because it drops metadata.
- `inspect_structure_output(...)` 只适合调试，不适合作为 parser 主路径输出。

## Proposed Parser API

### Option 1: Extend `parse_image_document(...)`

建议签名：

```python
def parse_image_document(
    file_path: str | Path,
    enable_ocr: bool = False,
    ocr_lang: str = "ch",
    ocr_use_gpu: bool = False,
    enable_preprocess: bool = True,
    preprocess_mode: str = "gray",
    enable_deskew: bool = True,
    preserve_ocr_blocks: bool = True,
) -> ParsedDocument:
    ...
```

行为说明：

- 默认 `enable_ocr=False`，保持现有行为不变。
- 当 `enable_ocr=False` 时，仍然只注册 single-page image document 和 image element。
- 当 `enable_ocr=True` 时，进入 OCR-backed parser path，并返回包含 OCR-backed pages / elements 的 `ParsedDocument`。
- OCR-backed path 不写文件，不生成报告，不产生最终审计结论。

### Option 2: Add Internal Helper

建议新增内部 helper：

```python
def _parse_image_document_with_ocr(
    file_path: Path,
    ocr_lang: str = "ch",
    ocr_use_gpu: bool = False,
    enable_preprocess: bool = True,
    preprocess_mode: str = "gray",
    enable_deskew: bool = True,
    preserve_ocr_blocks: bool = True,
) -> ParsedDocument:
    ...
```

职责划分：

- `parse_image_document(...)` 负责兼容旧行为和参数分派。
- `_parse_image_document_with_ocr(...)` 负责 OCR-backed path。
- OCR-backed helper 内部应先生成 `DocumentPage` / `DocumentElement`，再交给后续 Document-first pipeline。

## Scanned PDF Design

PDF 默认仍优先 native text parsing。

不得默认把 native PDF 转图片 OCR。只有当 `enable_ocr=True` 且页面无可靠 native text 时，才考虑 per-page rendering + OCR。

建议未来参数：

```python
def parse_pdf_document(
    file_path: str | Path,
    enable_ocr: bool = False,
    ocr_for_empty_pages_only: bool = True,
    ocr_lang: str = "ch",
    ocr_use_gpu: bool = False,
    enable_preprocess: bool = True,
    preprocess_mode: str = "gray",
    enable_deskew: bool = True,
) -> ParsedDocument:
    ...
```

设计说明：

- `enable_ocr=False` 时，PDF parser 行为保持不变。
- `ocr_for_empty_pages_only=True` 时，只对无可靠 native text 的页面考虑 OCR。
- 有 native text / native block / native table structure 的页面，仍应优先使用原生结构。
- Phase 14 初期可以先只支持 image OCR path，scanned PDF OCR path 后续再做。

## OCR Block to DocumentElement Mapping

| OCR output | Document-first target |
| --- | --- |
| OCR page/image | `DocumentPage` |
| text block | `DocumentElement(element_type="paragraph")` |
| title block | `DocumentElement(element_type="title")` |
| table block / table html | `DocumentElement(element_type="table")` |
| figure/image region | `DocumentElement(element_type="image")` |
| seal/signature-like region | `DocumentElement(element_type="signature")` if detectable, otherwise `"image"` or `"unknown"` |
| bbox | `BoundingBox` |
| confidence | `DocumentElement.metadata["ocr_confidence"]` |
| raw OCR block | `DocumentElement.raw` or `metadata["raw_ocr_block"]` |
| OCR table HTML | `metadata["html"]` |
| OCR DataFrame | `raw` or `metadata["df"]` |
| table spans | `metadata["spans"]` |
| cell boxes | `metadata["cell_box_list"]` |

现有 `ElementType` 已支持 `paragraph`、`title`、`table`、`image`、`header`、`footer`、`signature`、`blank`、`unknown`。Phase 14 初期不建议先扩展数据模型。

## Metadata Design

### `ParsedDocument.metadata`

建议保留：

```text
source_file
source_format
ocr_enabled
ocr_engine
ocr_lang
ocr_use_gpu
preprocess_enabled
preprocess_mode
deskew_enabled
```

### `DocumentPage.metadata`

建议保留：

```text
page_index
source_image_path
ocr_page_index
native_text_available
ocr_applied
preprocess
deskew_angle
```

### `DocumentElement.metadata`

建议保留：

```text
source_file
source_format
page_index
ocr_block_index
ocr_block_type
ocr_confidence
bbox_source
preprocess
table_html
table_spans
cell_box_list
table_ocr_pred
source_style
```

序列化约束：

- 不要把不可序列化对象直接塞进 metadata，尤其是 DataFrame / raw OCR object。
- 如果需要保留 DataFrame，可优先放在 `DocumentElement.raw`。
- 如果需要保留 raw OCR object，可优先放在 `DocumentElement.raw`，或只保留 JSON-serializable 摘要到 metadata。
- report generator 应继续保持 JSON-serializable 转换策略。

## Table Handling

OCR table result should become DocumentElement(TABLE), not immediate DataFrame comparison.

目标流程：

```text
OCR table block
        ↓
extract_tables_with_metadata(...)
        ↓
DocumentElement(TABLE)
        ↓
content_compare marks requires_table_compare if needed
        ↓
table_compare
        ↓
EvidenceIndex
```

设计说明：

- `extract_tables_with_metadata(...)` 可作为 OCR table block 到 table metadata 的桥接层。
- table HTML、spans、bbox、cell boxes、table OCR prediction、source style 都应尽量保留。
- DataFrame 可以作为 `DocumentElement.raw` 的一部分，供 `table_compare` 在需要精查时使用。
- `extract_tables_to_dataframes(...)` should remain legacy convenience only.
- 新 OCR parser 不应把 table DataFrame 直接送入 `align_compare.py`。

## Write Safety

OCR parser path must be in-memory by default.

写入约束：

- `preprocess_pipeline(...)` must use `output_path=None`.
- No intermediate image should be written unless user explicitly requests it.
- No report writing happens inside parser.
- OCR parser 不应创建 `data/output` 文件。
- OCR parser 不应调用 `allow_write=True` 相关写报告路径。
- 如果未来需要导出中间图，必须是显式参数、显式路径、显式写入许可。

## Backward Compatibility

兼容性要求：

- Existing `parse_image_document(file_path)` behavior must remain unchanged when `enable_ocr=False`.
- Existing `core/pre_processing.py` public functions must remain stable.
- Existing `core/ocr_engine.py` public functions must remain stable.
- Existing legacy table-first pipeline may remain for compatibility.
- `main.py::run_document_first_pipeline(...)` should not be broken.
- `tools/run_document_demo.py` should remain a thin wrapper around `main.py::run_document_first_pipeline(...)`.
- New OCR parser parameters should have compatibility defaults.

## Future Implementation Plan

```text
Phase 14c: Add optional OCR path for parse_image_document(...)
Phase 14d: Design / implement scanned PDF OCR path
Phase 14e: Map OCR text/layout blocks to DocumentElement
Phase 14f: Map OCR table results to DocumentElement(TABLE)
Phase 14g: Connect OCR-derived evidence metadata to EvidenceIndex
Phase 14h: Validate with scan samples
```

Implementation order should keep the smallest controlled path first:

1. Preserve current image parser behavior by default.
2. Add explicit `enable_ocr=True` image path.
3. Convert OCR blocks into `DocumentElement` records.
4. Convert OCR tables into `DocumentElement(TABLE)` records.
5. Preserve metadata for later EvidenceIndex/report review.
6. Add scanned PDF OCR only after image OCR path is stable.

## Acceptance Criteria for Phase 14c

- `parse_image_document(path)` without OCR behaves exactly as before.
- `parse_image_document(path, enable_ocr=True)` returns `ParsedDocument` with OCR-backed elements.
- No files are written by default.
- `preprocess_pipeline(...)` is called with `output_path=None`.
- OCR blocks are converted to `DocumentElement` records.
- OCR tables become `DocumentElement(TABLE)`, not direct DataFrame comparison.
- OCR metadata is preserved.
- No final audit conclusion is produced.
- Existing import checks still succeed.
