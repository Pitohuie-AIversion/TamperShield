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
- [x] 已确认 `扫描件/监理合同.pdf` 为图片型扫描 PDF，不能作为原生 `base_df` 来源
- [x] 已确认电子稿 PDF 可通过 `pdfplumber` 提取表格，但跨页表会被拆分，存在续页表头误识别风险
- [x] 已确认同名 DOCX 包含 5 个干净 Word 表格，更适合作为 `base_df` 优先来源
- [x] 在 `core/text_parser.py` 新增 DOCX 表格提取函数：`extract_tables_from_native_docx_with_metadata()`
- [x] 在 `core/text_parser.py` 新增兼容入口：`extract_tables_from_native_docx()`
- [x] DOCX 表格提取已保留 `_source_file`、`_source_table`、`_source_row` 元数据
- [x] 指定 DOCX 已成功提取 5 张原生表格
- [x] `normalize_dataframe()` 已支持 `promote_first_row_to_header=True`
- [x] 扫描件 DataFrame 已可通过首行提升得到 `序号`、`分项`、`澄清项`、`回复`
- [x] 已对比当前扫描件表格与指定 DOCX 5 张表的列名
- [x] 新增 `core/table_matcher.py`
- [x] 新增 `rank_base_table_candidates()`，用于对 `scan_df` 和候选 `base_df` 做确定性表级匹配排序
- [x] 匹配分数包含 `column_score`、`text_score`、`shape_score`、`key_overlap_score`
- [x] 匹配决策包含 `auto_match`、`needs_review`、`no_match`
- [x] 自测通过：同一 DOCX 表匹配自身得到 `auto_match`
- [x] 当前扫描件表 `序号/分项/澄清项/回复` 对指定 DOCX 5 张表均为 `no_match`
- [x] 新增原生文档表格统一入口：`extract_tables_from_native_document_with_metadata()`
- [x] 新增原生文档批量入口：`extract_tables_from_native_documents_with_metadata()`
- [x] 已用关键词命中文档进行批量候选排序，最高候选仍为 `no_match`
- [x] 明确当前阶段不实现 RAG
- [x] 明确当前优先方向是确定性 `table_matcher`、用户确认的 `column_mapping` 和后续 `evidence_index`

## Next

### Phase 1：项目规则与架构调整

- [ ] 更新 `PROJECT_RULES.md`
- [ ] 更新 `AGENTS.md`
- [ ] 更新 `TODO.md`
- [ ] 明确 `table_matcher.py` 和 `align_compare.py` 下沉为表格精查子模块

### Phase 2：统一文档数据结构

- [ ] 设计 `DocumentElement`
- [ ] 设计 `DocumentPage`
- [ ] 设计 `ParsedDocument`
- [ ] 元素类型支持 `paragraph`、`title`、`table`、`image`、`header`、`footer`、`signature`、`blank`、`unknown`

### Phase 3：document_parser

- [ ] 设计 `parse_document(file_path)`
- [ ] 支持 PDF 页面文本提取
- [ ] 支持 DOCX 原生段落和表格提取
- [ ] 保留原有 DOCX 表格提取逻辑，但不得让表格提取成为主入口

### Phase 4：page_aligner

- [ ] 设计 `align_pages(candidate_pages, baseline_pages)`
- [ ] 支持页面顺序对齐
- [ ] 支持新增页、缺失页、错页和空白页检测

### Phase 5：content_compare

- [ ] 设计 `compare_page(candidate_page, baseline_page)`
- [ ] 输出页面级差异
- [ ] 输出段落级差异
- [ ] 标记疑似表格区域 `requires_table_compare=True`

### Phase 6：table_compare 下沉

- [ ] `table_matcher.py` 作为表格候选匹配子模块
- [ ] `align_compare.py` 作为单元格级比对子模块
- [ ] 只有页面级比对需要精查时，才调用表格比对

### Phase 7：evidence_index

- [ ] 设计统一 `Difference` 数据结构
- [ ] 每条差异必须记录 `diff_type`、`severity`、`candidate_page`、`baseline_page`、`element_id` 和 `location`
- [ ] 表格差异必须追溯到 `source_file`、`source_page`、`source_table`、`source_row`、`column_name`
- [ ] 图片和签章差异必须追溯到页面和区域

### Phase 8：main.py pipeline

- [ ] 后续将 `main.py` 改造成宏观调度入口
- [ ] 主入口应为 `compare_documents(candidate_file, baseline_file)`
- [ ] `main.py` 不应直接堆叠 OCR、DataFrame 清洗和单元格比对细节

### Phase 9：报告输出

- [ ] 报告按页码组织
- [ ] 每页下按元素类型组织差异
- [ ] 表格单元格差异作为页面差异的子项
- [ ] 报告必须保留证据定位信息

## Current Focus

当前阶段重点从 DataFrame-first 调整为 Document-first。

当前最小目标：

```text
一份待核验文档
        vs
一份基准电子稿
        ↓
页面级文本提取
        ↓
页面顺序对齐
        ↓
页面级差异输出
        ↓
差异证据索引
```

新的主线是：

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
traceable audit report
```

`table_matcher.py` 和 `align_compare.py` 保留为 `table_compare` 层的精查能力，不再作为文档比对主入口。

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

因此，当前优先级为：

```text
document_parser
        ↓
page_aligner
        ↓
content_compare
        ↓
evidence_index.py
        ↓
report_generator.py
        ↓
optional read-only QA
```

`table_matcher.py` 和 `align_compare.py` 只在 `content_compare` 标记页面表格需要精查时进入 `table_compare` 子流程。

## Test Commands

检查 Git 冲突标记：

```powershell
Select-String -Path core/*.py,tools/*.py -Pattern "<<<<<<<|=======|>>>>>>>"
```

测试图像预处理 import：

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"
```

测试 OCR engine import：

```powershell
python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"
```

测试原生文档解析 import：

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

## Notes

如果 `scan_df` 与 `base_df` 的列名不一致，先不要修改 `align_compare.py`，应先考虑新增一个显式列名映射模块，例如：

```text
core/column_mapping.py
```

列名映射必须是确定性规则，不允许使用 LLM 猜测字段对应关系。

如果 `rank_native_table_candidates()` 的 Top-K 仍全部为 `no_match`，优先扩大 `data/base_docs/` 中的电子稿候选池，而不是调整阈值或使用 RAG。

如果真实扫描件来自附件、补遗、澄清回复文件或人工整理表，应将这些文件加入 `data/base_docs/` 后重新运行候选排序。

## Table Matcher Progress

- [x] 新增 `core/table_matcher.py`
- [x] 新增 `rank_base_table_candidates()`，用于对 `scan_df` 和候选 `base_df` 做确定性表级匹配排序
- [x] 匹配分数包含 `column_score`、`text_score`、`shape_score`、`key_overlap_score`
- [x] 匹配决策包含 `auto_match`、`needs_review`、`no_match`
- [x] 自测通过：同一 DOCX 表匹配自身得到 `auto_match`
- [x] 当前扫描件表 `序号/分项/澄清项/回复` 对指定 DOCX 5 张表均为 `no_match`
- [x] 新增原生文档表格统一入口：`extract_tables_from_native_document_with_metadata()`
- [x] 新增原生文档批量入口：`extract_tables_from_native_documents_with_metadata()`
- [x] 已用关键词命中文档进行批量候选排序，最高候选仍为 `no_match`
- [ ] 下一步：批量读取更多电子稿 DOCX/PDF 表格，使用 `rank_native_table_candidates()` 输出 Top-K 候选，定位当前扫描件表格的真实 `base_df` 来源
- [ ] 若 Top-K 仍全部为 `no_match`，排查扫描件是否来自其他电子稿、附件、补遗、澄清回复文件或人工整理表
- [ ] 暂不使用 RAG 定位表格来源；表格来源定位必须通过确定性候选排序和用户确认完成
