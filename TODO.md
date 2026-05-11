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

## Next

- [ ] 修改 `core/ocr_engine.py::parse_layout_to_blocks()`，兼容 callable engine 和 `.predict()` engine
- [ ] 测试 `build_pp_structure(use_gpu=False)` 是否能成功创建 `PPStructureV3`
- [ ] 测试 `PPStructureV3` 实际输出格式，确认是否仍包含 `type == "table"`、`res["html"]`
- [ ] 如果 `PPStructureV3` 输出格式变化，适配 `extract_tables_with_metadata()`
- [ ] 检查 `pd.read_html()` 是否可用；如果缺少解析器，再决定是否把 `lxml` 加入 `requirements.txt`
- [ ] 使用真实扫描件测试 `preprocess_pipeline(mode="gray")`
- [ ] 使用真实扫描件测试 `preprocess_pipeline(mode="binary")`
- [ ] 对比红章覆盖文字区域，检查黑色笔画是否断裂
- [ ] 检查 Deskew 后正文和表格线是否水平
- [ ] 测试完整 pipeline：扫描件预处理 → PPStructureV3 表格解析 → 原生 PDF 表格解析 → DataFrame 对齐 → 差异报告

## Test Commands

```powershell
Select-String -Path core/*.py,tools/*.py -Pattern "<<<<<<<|=======|>>>>>>>"

python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"

python -c "from core.ocr_engine import HTMLTableSpanParser, build_pp_structure; print('ocr_engine import ok')"

python -c "from core.ocr_engine import build_pp_structure; engine = build_pp_structure(use_gpu=False); print(type(engine)); print('callable:', callable(engine)); print('has predict:', hasattr(engine, 'predict'))"

python tools/batch_tune_thresholds.py

python tools/batch_tune_thresholds.py --output-dir data/output/real_scan_tuning --overwrite