# TamperShield TODO

## Done

- [x] 清理 Git 冲突标记，确保 `core/*.py` 和 `tools/*.py` 中不再出现 `<<<<<<<`、`=======`、`>>>>>>>`
- [x] `core/pre_processing.py` 移除 HSV 红章白化流程
- [x] `core/pre_processing.py` 改为 RGB/R 通道红章抑制
- [x] `core/pre_processing.py` 增加 `black_text_mask` 黑字保护逻辑
- [x] `core/pre_processing.py` 使用 `HoughLinesP` + `cv2.minAreaRect` 进行 Deskew
- [x] `core/ocr_engine.py` 删除顶层 `from paddleocr import PPStructure`
- [x] `core/ocr_engine.py` 改为 PaddleOCR 结构化引擎懒加载
- [x] `core/ocr_engine.py::parse_layout_to_blocks()` 已兼容 callable engine 和 `.predict()` engine
- [x] PaddleOCR 3.x 组合测试完成：`paddle==3.2.2`、`paddleocr==3.5.0`、`paddlex==3.5.1`
- [x] `PPStructureV3.predict()` 真实图片测试成功
- [x] `extract_tables_with_metadata()` 已支持 `LayoutParsingResultV2 → table_res_list → pred_html → DataFrame`
- [x] 原生 DOCX/PDF 表格提取已支持
- [x] `normalize_dataframe()` 已支持 `promote_first_row_to_header=True`
- [x] 扫描件 DataFrame 已可通过首行提升得到 `序号`、`分项`、`澄清项`、`回复`
- [x] 新增 `core/table_matcher.py`
- [x] 新增 `rank_base_table_candidates()`
- [x] 新增 `rank_native_table_candidates()`
- [x] 表级匹配决策包含 `auto_match`、`needs_review`、`no_match`
- [x] 明确当前阶段不实现 RAG
- [x] Phase 1：完成 Document-first 项目规则与架构调整
- [x] 更新 `PROJECT_RULES.md`，明确 TamperShield 是工程文档防篡改比对系统，不是表格比对工具
- [x] 更新 `AGENTS.md`，要求后续 AI agent 遵循 Document-first 架构
- [x] 更新 `TODO.md`，将主线从 DataFrame-first 调整为 Document-first
- [x] Phase 2：新增 `core/document_models.py`
- [x] 定义 `ElementType`、`FileType`、`DiffType`、`Severity`
- [x] 定义 `BoundingBox`、`DocumentElement`、`DocumentPage`、`ParsedDocument`、`Difference`
- [x] Phase 3：新增 `core/document_parser.py`
- [x] 实现 `detect_file_type()`
- [x] 实现 `parse_document()`
- [x] 实现 `parse_pdf_document()`
- [x] 实现 `parse_docx_document()`
- [x] 实现 `parse_image_document()`
- [x] Phase 4：新增 `core/page_aligner.py`
- [x] 定义 `AlignmentStatus`、`PageAlignment`
- [x] 实现 `normalize_page_text()`
- [x] 实现 `text_similarity()`
- [x] 实现 `page_similarity()`
- [x] 实现 `align_pages()`
- [x] Phase 5：新增 `core/content_compare.py`
- [x] 实现页面级文本差异检测
- [x] 实现空白页状态差异检测
- [x] 实现元素数量差异检测
- [x] 实现 `requires_table_compare` 标记
- [x] Phase 6：新增 `core/table_compare.py`
- [x] 将 `table_matcher.py` 和 `align_compare.py` 下沉为 `table_compare` 层子能力
- [x] 实现 `compare_page_tables_if_needed()`
- [x] 表格精查仅在 `requires_table_compare=True` 时触发
- [x] Phase 7：新增 `core/evidence_index.py`
- [x] 定义 `EvidenceRecord`、`EvidenceIndex`
- [x] 实现 `build_evidence_index()`
- [x] 实现 `group_records_by_page()`
- [x] 实现 `filter_records()`
- [x] Phase 8a：新增 `core/document_pipeline.py`
- [x] 实现 `collect_document_differences()`
- [x] 实现 `compare_parsed_documents()`
- [x] 实现 `compare_documents()`
- [x] 新 Document-first pipeline 已可在内存中返回 `EvidenceIndex`
- [x] Phase 8b：`main.py` 可选接入 Document-first pipeline
- [x] 保留旧入口 `main.py::run_tamper_shield_pipeline(...)`
- [x] 新增并行入口 `main.py::run_document_first_pipeline(...)`
- [x] `run_document_first_pipeline(...)` 调用 `core.document_pipeline.compare_documents(...)`
- [x] `run_document_first_pipeline(...)` 默认返回 `EvidenceIndex`
- [x] `run_document_first_pipeline(...)` 不写文件、不生成报告、不调用 `ensure_write_allowed()`
- [x] 旧 table-first pipeline 与新 Document-first pipeline 已可并存
- [x] Phase 9a：新增 `core/report_generator.py`
- [x] 实现 `make_json_safe(...)`
- [x] 实现 `evidence_index_to_summary_dict(...)`
- [x] 实现 `evidence_record_to_dict(...)`
- [x] 实现 `evidence_records_to_page_dict(...)`
- [x] 实现 `generate_markdown_report(...)`
- [x] 实现 `write_text_report(...)`
- [x] 实现 `generate_report_bundle(...)`
- [x] 报告生成模块只消费 `EvidenceIndex`
- [x] 报告生成模块不重新执行解析、对齐、内容比对、表格精查、OCR 或 LLM
- [x] `write_text_report(...)` 默认阻断写入，只有 `allow_write=True` 才写文件
- [x] Phase 9b：`main.py::run_document_first_pipeline(...)` 可选接入报告导出
- [x] `run_document_first_pipeline(...)` 新增 `report_output_path`
- [x] `run_document_first_pipeline(...)` 新增 `allow_write`
- [x] `run_document_first_pipeline(...)` 新增 `overwrite`
- [x] `report_output_path is None` 时仍只返回 `EvidenceIndex`，不写文件
- [x] `report_output_path` 非空时生成 Markdown 报告
- [x] 报告写入仍由 `write_text_report(...)` 执行权限控制

## Current Focus

当前阶段已完成 Document-first pipeline、`main.py` 可选接入，以及基于 `EvidenceIndex` 的 Markdown 报告导出能力。

当前已完成主线：

```text
candidate document
        vs
baseline document
        ↓
main.py::run_document_first_pipeline(...)
        ↓
EvidenceIndex
        ↓
core/report_generator.py
        ↓
optional Markdown report
```

当前重点进入：

```text
Phase 10：真实文档验证
```

Phase 10 的目标是使用真实 candidate document 和 baseline document 验证端到端流程，包括解析、页面对齐、内容差异、表格精查触发、证据索引和可选报告导出。

注意：Phase 10 是验证阶段，不应优先重构核心架构。

## Next

### Phase 10：真实文档验证

- [ ] 准备一组真实 candidate document 和 baseline document
- [ ] 验证 `run_document_first_pipeline(...)`
- [ ] 验证默认不写文件行为
- [ ] 验证 `report_output_path=None` 时只返回 `EvidenceIndex`
- [ ] 验证 `report_output_path` 非空但 `allow_write=False` 时阻断写入
- [ ] 验证 `report_output_path` 非空且 `allow_write=True` 时写出 Markdown 报告
- [ ] 验证 PDF 文本页解析
- [ ] 验证 DOCX 近似单页解析
- [ ] 验证 `page_aligner` 对新增页、缺页、错页的表现
- [ ] 验证 `content_compare` 的文本差异和元素差异输出
- [ ] 验证 `table_compare` 在 DataFrame payload 可用和不可用场景下的表现
- [ ] 验证 `EvidenceIndex` summary、filter 和 group by page
- [ ] 验证 Markdown 报告是否按页面和证据类别组织
- [ ] 记录 Phase 10 验证中发现的问题，后续再进入 targeted fix

### Phase 11：真实问题修复与增强

- [ ] 根据 Phase 10 验证结果修复 parser / aligner / compare / report 的具体问题
- [ ] 优先修复阻断端到端流程的问题
- [ ] 不做大规模重构，除非 Phase 10 证明当前架构无法支撑真实数据

## Test Commands

### Document-first Core Test Commands

```powershell
python -c "from core.document_models import ParsedDocument, DocumentPage, Difference; print('document_models import ok')"

python -c "from core.document_parser import detect_file_type, parse_document, parse_pdf_document, parse_docx_document, parse_image_document; print('document_parser import ok')"

python -c "from core.page_aligner import align_pages, PageAlignment; print('page_aligner import ok')"

python -c "from core.content_compare import compare_page, compare_aligned_pages; print('content_compare import ok')"

python -c "from core.table_compare import compare_page_tables_if_needed; print('table_compare import ok')"

python -c "from core.evidence_index import build_evidence_index, EvidenceIndex; print('evidence_index import ok')"

python -c "from core.document_pipeline import compare_documents, compare_parsed_documents, collect_document_differences; print('document_pipeline import ok')"

python -c "from core.report_generator import generate_markdown_report, write_text_report, generate_report_bundle; print('report_generator import ok')"

python -c "from main import run_tamper_shield_pipeline, run_document_first_pipeline; print('main pipeline imports ok')"

python -c "import inspect; from main import run_document_first_pipeline; print(inspect.signature(run_document_first_pipeline))"
```

签名应包含：

```text
report_output_path
allow_write
overwrite
```

写入阻断测试：

```powershell

python -c "from core.report_generator import write_text_report; import tempfile; from pathlib import Path; p=Path(tempfile.gettempdir())/'tamper_report_test.md';\
try:\
    write_text_report('test', p, allow_write=False)\
except PermissionError as e:\
    print(str(e))"
```

预期：

```text
[Output Blocked] - Permission Required
```

检查 Git 冲突标记：

```powershell
Select-String -Path core/*.py,tools/*.py -Pattern "<<<<<<<|=======|>>>>>>>"
```

### Legacy Table-first / Table Submodule Test Commands

以下命令用于兼容旧 OCR / DataFrame / 表格子模块流程。它们不是新的文档级主流程。

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"

python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"

python -c "from core.text_parser import extract_tables_from_native_document_with_metadata, extract_tables_from_native_documents_with_metadata; print('text_parser import ok')"

python -c "from core.table_matcher import rank_base_table_candidates, rank_native_table_candidates; print('table_matcher import ok')"
```

## RAG Decision

当前阶段不实现 RAG。

禁止的方向是：

```text
OCR / PDF extraction
        ↓
RAG
        ↓
LLM decides field matching, missing values, amount equality, or tampering
```

允许的未来方向是：

```text
compare result
        ↓
evidence_index
        ↓
read-only QA / explanation layer
```
