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
- [x] `extract_tables_with_metadata()` 保留旧版 PPStructure dict 兼容层
- [x] 原生 DOCX/PDF 表格提取已支持
- [x] `normalize_dataframe()` 已支持 `promote_first_row_to_header=True`
- [x] 扫描件 DataFrame 已可通过首行提升得到 `序号`、`分项`、`澄清项`、`回复`
- [x] 新增 `core/table_matcher.py`
- [x] 新增 `rank_base_table_candidates()`
- [x] 新增 `rank_native_table_candidates()`
- [x] 表级匹配评分包含 `column_score`、`text_score`、`shape_score`、`key_overlap_score`
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

## Current Focus

当前阶段已完成 Document-first pipeline 与 `main.py` 的可选接入。

当前已完成主线：

```text
candidate document
        vs
baseline document
        ↓
core/document_pipeline.py
        ↓
main.py::run_document_first_pipeline(...)
        ↓
EvidenceIndex
```

当前重点进入：

```text
Phase 9：报告导出
```

Phase 9 的目标是新增报告导出能力，但报告必须以 `EvidenceIndex` 为输入，不能重新执行解析、对齐、比对或表格精查。

注意：旧的 `main.py::run_tamper_shield_pipeline(...)` 仍然保留，不得删除。

## Next

### Phase 9：报告导出

- [ ] 新增报告导出模块，例如 `core/report_generator.py`
- [ ] 报告输入必须是 `EvidenceIndex`
- [ ] 报告生成模块不得重新调用 `document_parser`
- [ ] 报告生成模块不得重新调用 `page_aligner`
- [ ] 报告生成模块不得重新调用 `content_compare`
- [ ] 报告生成模块不得重新调用 `table_compare`
- [ ] 报告应按页码组织
- [ ] 每页下按元素类型组织差异
- [ ] 表格单元格差异作为页面差异的子项
- [ ] 报告必须保留证据定位信息
- [ ] 报告导出必须显式传入输出路径
- [ ] 写文件必须要求 `allow_write=True`
- [ ] 不得默认生成保存路径
- [ ] 不得覆盖已有文件，除非 `overwrite=True`

### Phase 10：真实文档验证

- [ ] 使用一组真实 candidate document 和 baseline document 做端到端测试
- [ ] 验证 `run_document_first_pipeline(...)`
- [ ] 验证 PDF 文本页解析
- [ ] 验证 DOCX 近似单页解析
- [ ] 验证 `page_aligner` 对新增页、缺页、错页的表现
- [ ] 验证 `content_compare` 的文本差异和元素差异输出
- [ ] 验证 `table_compare` 在 DataFrame payload 可用和不可用场景下的表现
- [ ] 验证 `EvidenceIndex` summary、filter 和 group by page
- [ ] 验证 Phase 9 报告导出结果

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

python -c "from main import run_tamper_shield_pipeline, run_document_first_pipeline; print('main pipeline imports ok')"

python -c "import inspect; from main import run_document_first_pipeline; print(inspect.signature(run_document_first_pipeline))"

python -c "from main import run_tamper_shield_pipeline; print(run_tamper_shield_pipeline.__name__)"
```

内存 pipeline 测试：

```powershell
python -c "from core.document_models import ParsedDocument, DocumentPage; from core.document_pipeline import compare_parsed_documents; c=ParsedDocument(file_path='candidate.docx', file_type='docx', pages=[DocumentPage(page_number=1, plain_text='工程合同 金额 100')]); b=ParsedDocument(file_path='baseline.docx', file_type='docx', pages=[DocumentPage(page_number=1, plain_text='工程合同 金额 200')]); idx=compare_parsed_documents(c,b); print(idx.summary())"
```

检查 Git 冲突标记：

```powershell
Select-String -Path core/*.py,tools/*.py -Pattern "<<<<<<<|=======|>>>>>>>"
```

## Legacy Table-first / Table Submodule Test Commands

以下命令用于兼容旧 OCR / DataFrame / 表格子模块流程。它们不是新的文档级主流程。

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"

python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"

python -c "from core.text_parser import extract_tables_from_native_document_with_metadata, extract_tables_from_native_documents_with_metadata; print('text_parser import ok')"

python -c "from core.table_matcher import rank_base_table_candidates, rank_native_table_candidates; print('table_matcher import ok')"
```

检查实际输入文件：

```powershell
Get-ChildItem data/output/real_scan_tuning
Get-ChildItem data/base_docs
```

测试扫描件表格提取：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); print('image_count:', len(imgs)); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; img = imgs[0]; print('image:', img); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); print('scan tables:', len(tables)); print(tables[0]['df'].shape if tables else 'no table'); print(tables[0]['df'].head() if tables else 'no table')"
```

测试扫描件 DataFrame 首行表头提升：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; img = imgs[0]; engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); df = extract_tables_with_metadata(blocks)[0]['df']; promoted = normalize_dataframe(df, key_columns=['序号'], promote_first_row_to_header=True); print(promoted.columns.tolist()); print(promoted.shape); print(promoted.head())"
```

测试 Top-K 表格候选匹配：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; from core.table_matcher import rank_native_table_candidates; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); files = list(Path('data/base_docs').glob('*.docx')) + list(Path('data/base_docs').glob('*.pdf')); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; assert files, 'No DOCX/PDF found in data/base_docs/'; img = imgs[0]; engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); scan_df = extract_tables_with_metadata(blocks)[0]['df']; scan_df = normalize_dataframe(scan_df, key_columns=['序号'], promote_first_row_to_header=True); ranked = rank_native_table_candidates(scan_df, [str(p) for p in files], key_columns=['序号'], top_k=10); cols = ['score','decision','column_score','text_score','shape_score','key_overlap_score','base_source_file','base_table_index','base_shape']; print(ranked[cols] if not ranked.empty else 'no candidates')"
```

## RAG Decision

当前阶段不实现 RAG。

原因：

- 当前项目核心任务是确定性工程审计比对，不是知识问答生成
- RAG 容易引入字段语义猜测、表格内容补全和不可追溯判断
- 禁止 LLM 参与最终审计数据生成、字段匹配、金额判断和篡改判定
- 当前真正需要的是确定性证据链索引，而不是生成式检索问答

允许的未来方向是：

```text
compare result
        ↓
evidence_index
        ↓
read-only QA / explanation layer
```

禁止的方向是：

```text
OCR / PDF extraction
        ↓
RAG
        ↓
LLM decides field matching, missing values, amount equality, or tampering
```

## Notes

如果 `scan_df` 与 `base_df` 的列名不一致，先不要修改 `align_compare.py`，应先考虑新增一个显式列名映射模块，例如：

```text
core/column_mapping.py
```

列名映射必须是确定性规则，不允许使用 LLM 猜测字段对应关系。

如果后续对真实文档执行 Document-first pipeline，应优先验证页面级解析、页面对齐、元素级差异和证据索引，再进入表格精查。
