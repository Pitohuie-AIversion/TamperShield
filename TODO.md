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

## Next

- [ ] 用 3 张真实预处理图片批量测试表格提取
- [ ] 将扫描件 DataFrame 接入 `normalize_dataframe()`
- [ ] 检查扫描件 DataFrame 的列名、行数、主键列和空白单元格
- [ ] 测试原生 PDF 的 `pdfplumber` 表格提取
- [ ] 对比 `scan_df` 与 `base_df` 的列名
- [ ] 手动确定 `key_columns` 和 `numeric_columns`
- [ ] 运行最小 `compare_cells_with_tolerance()` 对齐测试
- [ ] 根据对齐结果决定是否新增列名映射模块
- [ ] 最后再接入 `main.py` 完整 pipeline
- [ ] 完整 pipeline 稳定后，再设计报告导出格式

## Current Focus

当前阶段重点不是继续调 PaddleOCR，也不是继续优化红章参数，而是打通：

```text
scan_df / base_df
        ↓
normalize_dataframe()
        ↓
key_columns 对齐
        ↓
compare_cells_with_tolerance()
```

当前最小目标是完成扫描件表格 DataFrame 与原生 PDF 表格 DataFrame 的字段对齐测试。

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

测试扫描件表格提取：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; img = next(Path('data/output/real_scan_tuning').glob('*.png')); print('image:', img); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); print('tables:', len(tables)); print(tables[0]['source_style'] if tables else 'no table'); print(tables[0]['df'].head() if tables else 'no table')"
```

测试扫描件 DataFrame 归一化：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.data_normalize import normalize_dataframe; img = next(Path('data/output/real_scan_tuning').glob('*.png')); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); df = tables[0]['df']; ndf = normalize_dataframe(df, key_columns=['序号']); print(ndf.head()); print(ndf.columns.tolist())"
```

测试原生 PDF 表格提取：

```powershell
python -c "from pathlib import Path; from core.text_parser import extract_tables_from_native_pdf_with_metadata; pdf = next(Path('data/base_docs').glob('*.pdf')); print('pdf:', pdf); tables = extract_tables_from_native_pdf_with_metadata(str(pdf)); print('tables:', len(tables)); print(tables[0]['df'].head() if tables else 'no table'); print(tables[0]['df'].columns.tolist() if tables else 'no table')"
```

最小 scan/base 对齐测试：

```powershell
python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; from core.text_parser import extract_tables_from_native_pdf; from core.data_normalize import normalize_dataframe; from core.align_compare import compare_cells_with_tolerance; img = next(Path('data/output/real_scan_tuning').glob('*.png')); pdf = next(Path('data/base_docs').glob('*.pdf')); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); scan_df = extract_tables_with_metadata(blocks)[0]['df']; base_df = extract_tables_from_native_pdf(str(pdf))[0]; scan_df = normalize_dataframe(scan_df, key_columns=['序号']); base_df = normalize_dataframe(base_df, key_columns=['序号']); diff = compare_cells_with_tolerance(base_df, scan_df, key_columns=['序号'], max_distance=2); print('diff rows:', len(diff)); print(diff.head())"
```

## Notes

如果 `scan_df` 与 `base_df` 的列名不一致，先不要修改 `align_compare.py`，应先考虑新增一个显式列名映射模块，例如：

```text
core/column_mapping.py
```

列名映射必须是确定性规则，不允许使用 LLM 猜测字段对应关系。
