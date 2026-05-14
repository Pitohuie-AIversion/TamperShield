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

## Current Focus

当前阶段已经完成真实文件验证中的主要 targeted fixes：

- DOCX 通过 LibreOffice rendered PDF 获得稳定分页
- `page_aligner` 已避免 forward skip 被误判为 reordered
- `page_added/page_deleted` 已有页面性质分类 metadata
- Markdown 报告已展示 review context 和 page profile
- 真实 Markdown 报告已完成一次受控写出验证
- 当前 page_count 稳定为 baseline 44 页
- 中文路径乱码已确认为显示/命令包装层问题，而非项目内部编码错误

当前下一步应进入：

```text
Phase 12：整理真实验证结论与准备可交付 demo 流程
```

Phase 12 的目标不是继续大规模改代码，而是整理稳定运行命令、报告查看方式、已知限制和下一轮改进清单。

## Next

### Phase 12：整理真实验证结论与 Demo 流程

- [ ] 整理推荐运行命令，优先使用 `Path.glob()` 避免中文路径命令行显示问题
- [ ] 整理推荐报告查看命令：`Get-Content -Encoding UTF8`
- [ ] 记录当前稳定 summary：candidate=39, baseline=44, difference_count=69
- [ ] 记录当前 page_added/page_deleted 分类解释
- [ ] 记录当前 known limitations：
  - rendered PDF 路径下 DOCX native table 结构不会保留为 table element
  - `requires_table_compare_count=0` 不代表原文档没有表格
  - 中文路径在某些 PowerShell / conda run stdout 场景下可能显示乱码
  - LibreOffice profile / fonts / input file version 会影响分页
- [ ] 准备一套只读 demo 命令
- [ ] 准备一套显式写报告 demo 命令，必须使用 `allow_write=True` 和明确输出路径

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
