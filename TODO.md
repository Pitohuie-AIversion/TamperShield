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
- [x] Phase 11e：验证 LibreOffice DOCX 渲染分页路径
- [x] 找到 LibreOffice：`X:\Program Files\LibreOffice\program\soffice.exe`
- [x] `soffice --version` 验证通过：LibreOffice 26.2.3.2
- [x] DOCX 手动转换为 PDF 成功
- [x] DOCX 临时 PDF 页数为 45
- [x] `parse_docx_document(...)` 已成功走 `rendered_pdf`
- [x] DOCX baseline page_count 从原先 native fallback 的 1 页改善为 rendered PDF 的 45 页
- [x] 真实 PDF vs DOCX 验证结果改善：candidate_page_count=39，baseline_page_count=45，difference_count=69
- [x] Phase 11e 未写入真实报告，未运行 `allow_write=True`
- [x] Phase 11i：最小修复 `core/page_aligner.py`
- [x] 新增 `_is_forward_sequence_match(...)`
- [x] forward baseline skip 不再误判为 `possible_reordered`
- [x] 真实文件中 `page_reordered` 从 3 降为 0
- [x] Phase 11j：只读分析剩余 `page_added/page_deleted`
- [x] 判断剩余页面差异主要来自目录/封面格式差异、页码残留、短签章页、附件起始页和少量人工复核正文页
- [x] Phase 11k：为 `page_added/page_deleted` 增加页面性质分类 metadata
- [x] 新增 `page_profile`
- [x] 新增 `page_issue_category`
- [x] 新增 `suggested_review_severity`
- [x] 新增 `classification_reason`
- [x] 保持 `Difference.severity` 原值，不把 suggested severity 写入主 severity
- [x] Phase 11l：让 Markdown 报告显示 review context 和 page profile
- [x] 报告保留完整 Metadata JSON 区块
- [x] Phase 11m：真实 Markdown 报告写出验证
- [x] 使用 `allow_write=True` 写出唯一文件 `data/output/phase11m_report.md`
- [x] 使用 `overwrite=False`
- [x] 报告包含 `Review context`、`Page issue category`、`Suggested review severity`、`Classification reason`、`Page profile`
- [x] Phase 11n/11o：确认当前 DOCX rendered PDF page_count 稳定为 44
- [x] 当前真实 pipeline 稳定为 `candidate_page_count=39`、`baseline_page_count=44`、`difference_count=69`
- [x] Phase 11p：确认 metadata 中文路径不是项目内部乱码
- [x] 确认 report 文件实际为 UTF-8 正常内容
- [x] 确认乱码主要来自 PowerShell 默认显示 / conda run stdout 包装层显示编码
- [x] Phase 12a：新增 `DEMO_WORKFLOW.md`
- [x] `DEMO_WORKFLOW.md` 已记录 Document-first demo 的只读运行命令
- [x] `DEMO_WORKFLOW.md` 已记录显式 Markdown 报告导出命令模板
- [x] `DEMO_WORKFLOW.md` 已记录 `Get-Content -Encoding UTF8` 报告查看方式
- [x] `DEMO_WORKFLOW.md` 已记录 known limitations 和 next improvement backlog
- [x] Phase 12b：增强 `DEMO_WORKFLOW.md` 的可交付质量
- [x] 新增 Quick Start / Expected Read-Only Output / Report Export Safety Notes / Evidence Interpretation Notes / Troubleshooting
- [x] Phase 12c：新增 `DEMO_CHECKLIST.md`
- [x] `DEMO_CHECKLIST.md` 已覆盖环境、输入、只读运行、报告导出、报告审阅、证据解释、安全边界、已知限制和 demo pass criteria
- [x] Phase 12d：新增 `README.md`
- [x] `README.md` 已作为项目根目录入口说明
- [x] `README.md` 已链接 Demo Workflow、Demo Checklist、Project Rules、Agent Instructions 和 TODO
- [x] Phase 13c：新增 `tools/run_document_demo.py`
- [x] CLI wrapper 只调用 `main.py::run_document_first_pipeline(...)`
- [x] CLI 默认只读
- [x] CLI 支持 `--candidate` / `--baseline` / `--auto-discover` / `--input-dir`
- [x] CLI 支持 `--report-output` / `--allow-write` / `--overwrite`
- [x] CLI 支持 `--show-metadata` / `--show-records`
- [x] CLI 参数校验已覆盖无输入、缺少 allow-write、overwrite 未授权、show-records 非法值
- [x] Phase 13d：CLI wrapper 只读真实运行验证通过
- [x] `--auto-discover` 真实只读运行成功
- [x] 显式路径真实只读运行成功
- [x] `--show-metadata` 和 `--show-records 5` 验证通过
- [x] `--report-output` 无 `--allow-write` 正确阻断
- [x] CLI 真实验证稳定输出 `candidate_page_count=39`、`baseline_page_count=44`、`difference_count=69`
- [x] Phase 13e：修复 LibreOffice subprocess 解码异常
- [x] `core/document_parser.py` 的 LibreOffice subprocess 调用已加入 `encoding="utf-8", errors="replace"`
- [x] 修复后 DOCX rendered PDF parse 仍稳定为 `page_count=44`
- [x] CLI 只读运行不再出现 UnicodeDecodeError traceback

## Current Focus

当前阶段：

```text
Phase 14a：Inventory existing OCR and preprocessing capabilities
```

Phase 14a 目标：

* 只读盘点 `core/pre_processing.py`
* 只读盘点 `core/ocr_engine.py`
* 梳理可复用的 OCR / preprocessing 能力
* 识别哪些函数可以迁入 Document-first parser
* 识别 OCR 输出如何映射到 `DocumentPage` / `DocumentElement`
* 不实现 OCR
* 不修改 core 代码
* 不运行真实 OCR
* 不写入 `data/output`

当前已经完成：

```text
Document-first pipeline
真实 PDF vs DOCX 验证
Markdown report export
Demo workflow / checklist / README
CLI wrapper
CLI read-only validation
LibreOffice subprocess decode fix
OCR Integration Rules
```

当前可用入口：

```text
README.md
DEMO_WORKFLOW.md
DEMO_CHECKLIST.md
CLI_DESIGN.md
tools/run_document_demo.py
```

当前 CLI 稳定只读验证基线：

```text
candidate_page_count = 39
baseline_page_count = 44
difference_count = 69
page_reordered = 0
requires_table_compare_count = 0
```

Phase 14 总目标：

```text
OCR integration into Document-first pipeline
```

Phase 14 的目标是把现有 legacy OCR 能力从 table-first 旁路迁入 Document-first parser，使扫描件、图片页、扫描 PDF、红章页和 OCR 表格都能进入统一 EvidenceIndex。

## Next

### Phase 14：OCR integration into Document-first pipeline

- [ ] Phase 14a：Inventory existing OCR and preprocessing capabilities（current）
  - [ ] Review `core/pre_processing.py`
  - [ ] Review `core/ocr_engine.py`
  - [ ] Identify reusable preprocessing functions: red seal suppression, deskew, gray enhancement, binarization
  - [ ] Identify reusable OCR functions: PPStructure engine, layout blocks, table HTML, table metadata

- [ ] Phase 14b：Design OCR-backed document parser
  - [ ] Define how OCR output maps to `DocumentPage`
  - [ ] Define how OCR text blocks map to `DocumentElement`
  - [ ] Define how OCR tables map to `DocumentElement(TABLE)`
  - [ ] Define metadata fields for OCR confidence, bbox, engine, preprocessing mode

- [ ] Phase 14c：Add optional OCR path for `parse_image_document(...)`
  - [ ] Keep OCR disabled by default unless explicitly requested
  - [ ] Return `ParsedDocument` with OCR-backed pages and elements
  - [ ] Preserve image page metadata

- [ ] Phase 14d：Design scanned PDF OCR path
  - [ ] Detect pages without reliable native text
  - [ ] Render page image only when OCR is explicitly enabled
  - [ ] Convert OCR results to Document-first elements

- [ ] Phase 14e：Map OCR text and layout blocks to `DocumentElement`
  - [ ] paragraph / title / header / footer / figure caption when available
  - [ ] preserve bbox and OCR confidence

- [ ] Phase 14f：Map OCR table results to `DocumentElement(TABLE)`
  - [ ] preserve table HTML where available
  - [ ] preserve cell spans / bbox / table metadata
  - [ ] allow downstream `table_compare` to run only when needed

- [ ] Phase 14g：Connect OCR evidence to `EvidenceIndex`
  - [ ] include OCR source metadata in Difference metadata
  - [ ] add review context for OCR-derived evidence
  - [ ] avoid final audit conclusions

- [ ] Phase 14h：Validate with scan samples
  - [ ] red seal over table text
  - [ ] horizontal clean scan
  - [ ] visibly skewed scan
  - [ ] scanned PDF if available

- [ ] Phase 14i：Update reports and demo docs after OCR integration
  - [ ] document OCR limitations
  - [ ] document how to enable OCR
  - [ ] document expected evidence categories

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
