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

## Next

- [ ] 保持现有 PDF 表格提取函数不变，避免影响已验证路径
- [ ] 确认当前扫描件表格对应的原生电子稿表格来源
- [ ] 将匹配的 DOCX/PDF 表格作为 `base_df` 接入 `normalize_dataframe()`
- [ ] 对比匹配后的 `scan_df` 与 `base_df` 的列名、行数、主键列和空白单元格
- [ ] 手动确认 `key_columns` 和 `numeric_columns`
- [ ] 运行最小 `compare_cells_with_tolerance()` 对齐测试
- [ ] 如果列名不一致，优先设计确定性 `core/column_mapping.py`，不要修改 `align_compare.py`
- [ ] PDF 跨页续表合并逻辑后置处理，不阻塞当前 DOCX base 路线
- [ ] 最后再接入 `main.py` 完整 pipeline
- [ ] 完整 pipeline 稳定后，再设计报告导出格式

## Current Focus

当前阶段重点是把原生电子稿 DOCX 作为稳定 `base_df` 来源，先打通：

```text
DOCX table
        ↓
extract_tables_from_native_docx_with_metadata()
        ↓
base_df
        ↓
normalize_dataframe()
        ↓
scan_df / base_df key_columns 对齐
        ↓
compare_cells_with_tolerance()
```

PDF 原生表格提取当前作为诊断和追溯参考。由于 PDF 跨页表会被拆成多个片段，续页表头继承和同结构续表合并暂不作为当前最小通路的阻塞项。

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

测试 DOCX 文件是否含表格：

```powershell
python -c "import docx; p=r'E:\2026huinengyousuan\东生活1号监理\电子稿\1.-合同协议书-宁波东方理工大学（暂名）校园建设项目永久校区1号地块及2号地块-二期（东生活组团-1）工程监理2023.8.17.docx'; d=docx.Document(p); print('tables:', len(d.tables)); [print(i, len(t.rows), max((len(r.cells) for r in t.rows), default=0), [c.text.strip().replace('\n',' ')[:30] for c in t.rows[0].cells] if t.rows else []) for i,t in enumerate(d.tables)]"
```

测试扫描件表格提取：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; img = next(Path('data/output/real_scan_tuning').glob('*.png')); print('image:', img); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); print('tables:', len(tables)); print(tables[0]['source_style'] if tables else 'no table'); print(tables[0]['df'].head() if tables else 'no table')"
```

测试扫描件 DataFrame 首行表头提升：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; img = next(Path('data/output/real_scan_tuning').glob('*.png')); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); df = extract_tables_with_metadata(blocks)[0]['df']; promoted = df.iloc[1:].copy(); promoted.columns = [str(x).strip() for x in df.iloc[0].tolist()]; promoted = normalize_dataframe(promoted, key_columns=['序号']); print(promoted.columns.tolist()); print(promoted.head())"
```

后续实现 DOCX 表格提取后，测试命令应使用：

```powershell
python -c "from core.text_parser import extract_tables_from_native_docx_with_metadata; p=r'E:\2026huinengyousuan\东生活1号监理\电子稿\1.-合同协议书-宁波东方理工大学（暂名）校园建设项目永久校区1号地块及2号地块-二期（东生活组团-1）工程监理2023.8.17.docx'; tables = extract_tables_from_native_docx_with_metadata(p); print('tables:', len(tables)); [print(i, t['df'].shape, t['df'].columns.tolist(), t['df'].head(2)) for i,t in enumerate(tables)]"
```

## Notes

如果 `scan_df` 与 `base_df` 的列名不一致，先不要修改 `align_compare.py`，应先考虑新增一个显式列名映射模块，例如：

```text
core/column_mapping.py
```

列名映射必须是确定性规则，不允许使用 LLM 猜测字段对应关系。

当前已验证：PDF 版本可提取大量表格片段，但跨页续表会造成假差异；DOCX 版本表格结构更干净，因此下一阶段优先实现 DOCX 表格提取。

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
- [ ] 下一步：批量读取更多电子稿表格，使用 `rank_base_table_candidates()` 定位扫描件表格来源
