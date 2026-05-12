# TamperShield TODO

## Done

- [x] 清理 Git 冲突标记，确保 `core/*.py` 和 `tools/*.py` 中不再出现 `<<<<<<<`、`=======`、`>>>>>>>`
- [x] `core/pre_processing.py` 移除 HSV 红章白化流程
- [x] `core/pre_processing.py` 改为 RGB/R 通道红章抑制
- [x] `core/pre_processing.py` 增加 `black_text_mask` 黑字保护逻辑
- [x] `core/pre_processing.py` 的 `binary` 模式保持严格二值输出
- [x] `core/pre_processing.py` 使用 `HoughLinesP` + `cv2.minAreaRect` 进行 Deskew
- [x] `tools/batch_tune_thresholds.py` 恢复完整批处理逻辑
- [x] `tools/batch_tune_thresholds.py` 默认不写文件，仅在显式传入 `--output-dir` 时输出
- [x] `core/ocr_engine.py` 删除顶层 `from paddleocr import PPStructure`
- [x] `core/ocr_engine.py` 改为 PaddleOCR 结构化引擎懒加载
- [x] `core/ocr_engine.py::parse_layout_to_blocks()` 已兼容 callable engine 和 `.predict()` engine
- [x] PaddleOCR 3.x 组合测试完成：`paddle==3.2.2`、`paddleocr==3.5.0`、`paddlex==3.5.1`
- [x] `PPStructureV3` engine 创建成功
- [x] `PPStructureV3.predict()` 真实图片测试成功
- [x] 输出对象确认为 `LayoutParsingResultV2`
- [x] 成功读取 `table_res_list`
- [x] 成功读取 `pred_html`
- [x] 成功通过 `pd.read_html(StringIO(pred_html))` 转为 DataFrame
- [x] `extract_tables_with_metadata()` 已支持 PPStructureV3 输出
- [x] `extract_tables_with_metadata()` 保留旧版 PPStructure dict 兼容层
- [x] 已确认扫描 PDF 不能作为原生 `base_df` 来源
- [x] 已确认电子稿 PDF 可通过 `pdfplumber` 提取表格，但跨页表会被拆分
- [x] 已确认同名 DOCX 包含 5 个原生 Word 表格，更适合作为 `base_df` 优先来源
- [x] 在 `core/text_parser.py` 新增 DOCX 表格提取函数：`extract_tables_from_native_docx_with_metadata()`
- [x] 在 `core/text_parser.py` 新增兼容入口：`extract_tables_from_native_docx()`
- [x] DOCX 表格提取已保留 `_source_file`、`_source_table`、`_source_row` 元数据
- [x] 指定 DOCX 已成功提取 5 张原生表格
- [x] `normalize_dataframe()` 已支持 `promote_first_row_to_header=True`
- [x] 扫描件 DataFrame 已可通过首行提升得到 `序号`、`分项`、`澄清项`、`回复`
- [x] 新增 `core/table_matcher.py`
- [x] 新增 `rank_base_table_candidates()`
- [x] 新增 `rank_native_table_candidates()`
- [x] 表级匹配评分包含 `column_score`、`text_score`、`shape_score`、`key_overlap_score`
- [x] 表级匹配决策包含 `auto_match`、`needs_review`、`no_match`
- [x] 自测通过：同一 DOCX 表匹配自身得到 `auto_match`
- [x] 新增原生文档表格统一入口：`extract_tables_from_native_document_with_metadata()`
- [x] 新增原生文档批量入口：`extract_tables_from_native_documents_with_metadata()`
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
- [x] 旧 `main.py::run_tamper_shield_pipeline(...)` 暂时保留

## Current Focus

当前阶段已完成 Document-first 核心内存 pipeline。

当前已完成主线：

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
core/document_pipeline.py
        ↓
EvidenceIndex
```

当前重点不是继续新建核心模块，而是进入：

```text
Phase 8b：main.py 可选接入 Document-first pipeline
```

注意：旧的 `main.py::run_tamper_shield_pipeline(...)` 暂时保留，不得删除。

## Next

### Phase 8b：main.py 可选接入 Document-first pipeline

- [ ] 保留旧的 `run_tamper_shield_pipeline(...)`
- [ ] 在 `main.py` 中新增并行入口 `run_document_first_pipeline(...)`
- [ ] 新入口调用 `core.document_pipeline.compare_documents(...)`
- [ ] 新入口默认不写文件，只返回 `EvidenceIndex`
- [ ] 如需写入结果，必须继续遵守 `allow_write` 和 `overwrite` 规则
- [ ] 不得删除或破坏旧 table-first pipeline

### Phase 9：报告导出

- [ ] 新增报告导出模块，例如 `core/report_generator.py`
- [ ] 报告输入应为 `EvidenceIndex`
- [ ] 报告应按页码组织
- [ ] 每页下按元素类型组织差异
- [ ] 表格单元格差异作为页面差异的子项
- [ ] 报告必须保留证据定位信息
- [ ] 报告导出必须显式传入输出路径
- [ ] 写文件必须要求 `allow_write=True`

### Phase 10：真实文档验证

- [ ] 使用一组真实 candidate document 和 baseline document 做端到端测试
- [ ] 验证 PDF 文本页解析
- [ ] 验证 DOCX 近似单页解析
- [ ] 验证 `page_aligner` 对新增页、缺页、错页的表现
- [ ] 验证 `content_compare` 的文本差异和元素差异输出
- [ ] 验证 `table_compare` 在 DataFrame payload 可用和不可用场景下的表现
- [ ] 验证 `EvidenceIndex` summary、filter 和 group by page

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

测试图像预处理 import：

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"
```

测试 OCR engine import：

```powershell
python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"
```

测试原生文档表格解析 import：

```powershell
python -c "from core.text_parser import extract_tables_from_native_document_with_metadata, extract_tables_from_native_documents_with_metadata; print('text_parser import ok')"
```

测试 table matcher import：

```powershell
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

测试候选电子稿表格批量提取：

```powershell
python -c "from pathlib import Path; from core.text_parser import extract_tables_from_native_documents_with_metadata; files = list(Path('data/base_docs').glob('*.docx')) + list(Path('data/base_docs').glob('*.pdf')); print('files:', len(files)); assert files, 'No DOCX/PDF found in data/base_docs/'; tables = extract_tables_from_native_documents_with_metadata([str(p) for p in files]); print('base tables:', len(tables)); [print(i, t['df'].shape, t.get('source_file',''), t.get('table_index',''), t['df'].columns.tolist()) for i,t in enumerate(tables[:10])]"
```

测试 Top-K 表格候选匹配：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; from core.table_matcher import rank_native_table_candidates; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); files = list(Path('data/base_docs').glob('*.docx')) + list(Path('data/base_docs').glob('*.pdf')); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; assert files, 'No DOCX/PDF found in data/base_docs/'; img = imgs[0]; engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); scan_df = extract_tables_with_metadata(blocks)[0]['df']; scan_df = normalize_dataframe(scan_df, key_columns=['序号'], promote_first_row_to_header=True); ranked = rank_native_table_candidates(scan_df, [str(p) for p in files], key_columns=['序号'], top_k=10); cols = ['score','decision','column_score','text_score','shape_score','key_overlap_score','base_source_file','base_table_index','base_shape']; print(ranked[cols] if not ranked.empty else 'no candidates')"
```

最小 scan/base 对齐测试：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.text_parser import extract_tables_from_native_documents_with_metadata; from core.data_normalize import normalize_dataframe; from core.table_matcher import rank_base_table_candidates; from core.align_compare import compare_cells_with_tolerance; imgs = list(Path('data/output/real_scan_tuning').glob('*.png')); files = list(Path('data/base_docs').glob('*.docx')) + list(Path('data/base_docs').glob('*.pdf')); assert imgs, 'No PNG found in data/output/real_scan_tuning/'; assert files, 'No DOCX/PDF found in data/base_docs/'; img = imgs[0]; engine = build_pp_structure(use_gpu=False); scan_df = extract_tables_with_metadata(parse_layout_to_blocks(engine, str(img)))[0]['df']; scan_df = normalize_dataframe(scan_df, key_columns=['序号'], promote_first_row_to_header=True); base_tables = extract_tables_from_native_documents_with_metadata([str(p) for p in files]); ranked = rank_base_table_candidates(scan_df, base_tables, key_columns=['序号'], top_k=1); assert not ranked.empty, 'No ranked base candidate'; print(ranked[['score','decision','base_source_file','base_table_index','base_shape']]); source = ranked.iloc[0]['base_source_file']; idx = int(ranked.iloc[0]['base_table_index']); candidates = [t for t in base_tables if t.get('source_file') == source and int(t.get('table_index', -1)) == idx]; assert candidates, 'Matched base table not found'; base_df = normalize_dataframe(candidates[0]['df'], key_columns=['序号']); diff = compare_cells_with_tolerance(base_df, scan_df, key_columns=['序号'], max_distance=2); print('matched source:', source); print('matched table:', idx); print('diff rows:', len(diff)); print(diff.head())"
```

## RAG Decision

当前阶段不实现 RAG。

原因：

- 当前项目核心任务是确定性工程审计比对，不是知识问答生成
- RAG 容易引入字段语义猜测、表格内容补全和不可追溯判断
- `PROJECT_RULES.md` 和 `AGENTS.md` 已明确禁止 LLM 参与最终审计数据生成、字段匹配、金额判断和篡改判定
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
