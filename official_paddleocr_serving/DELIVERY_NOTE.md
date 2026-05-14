# official_paddleocr_serving 交付说明

## 交付结论

当前 `official_paddleocr_serving/` 可以作为一份独立验证包交付给同事。

该目录已经完成：

1. PaddleOCR / PaddleX 官方 serving 验证
2. OCR、PP-StructureV3、Table Recognition v2、Table Cells Detection 输出结构分析
3. 未来接入 TamperShield 前的统一 JSON v0.1 草案

该目录当前不包含 TamperShield 本地业务 API，也不接入 `core/`、`main.py`、`tools/` 或现有 Document-first pipeline。

## 交付范围

交付目录：

```text
official_paddleocr_serving/
```

核心文件：

```text
README_OFFICIAL_SERVING.md
OFFICIAL_OUTPUT_ANALYSIS.md
requirements_official.txt
scripts/
samples/
results/
configs/
```

建议同事优先阅读：

```text
README_OFFICIAL_SERVING.md
OFFICIAL_OUTPUT_ANALYSIS.md
```

其中：

- `README_OFFICIAL_SERVING.md`：环境安装、服务启动、验证命令、真实运行记录、常见错误
- `OFFICIAL_OUTPUT_ANALYSIS.md`：官方输出结构分析、统一 JSON v0.1 草案、Phase 16 前置判断

## 已验证能力

| 能力 | 状态 | endpoint / 方式 | 结果文件 |
| --- | --- | --- | --- |
| OCR | 已跑通 | `/ocr` | `results/ocr_result.json` |
| PP-StructureV3 | 已跑通 | `/layout-parsing` | `results/ppstructure_result.json` |
| Table Recognition v2 | 已跑通 | `/table-recognition` | `results/table_recognition_result.json` |
| Table Cells Detection | 已跑通 | Python API | `results/table_cells.json`、`results/table_cells_visual/table_res.jpg` |

## 推荐复现环境

建议使用独立 conda 环境：

```powershell
conda create -n paddleocr_official python=3.10 -y
conda activate paddleocr_official
pip install -r requirements_official.txt
paddlex --install serving
python scripts/check_environment.py
```

本机验证时也曾复用已有环境：

```powershell
conda run -n tamper_shield python scripts/check_environment.py
```

已验证版本：

```text
paddleocr == 3.5.0
paddlex == 3.5.1
paddle == 3.2.2
```

当前本机验证为 CPU 环境：

```text
compiled_with_cuda=False
gpu_count=0
```

## 快速验收命令

以下命令均在 `official_paddleocr_serving/` 目录下执行。

### 1. 环境检查

```powershell
python scripts/check_environment.py
```

### 2. Table Cells Detection 本地验证

```powershell
python scripts/test_table_cells_detection.py --image samples/table.jpg --output-dir results --overwrite
```

预期输出：

```text
results/table_cells.json
results/table_cells_visual/table_res.jpg
```

### 3. OCR serving

启动服务：

```powershell
.\scripts\start_ocr_service.ps1
```

另开一个 PowerShell 测试：

```powershell
python scripts/test_ocr_client.py --image samples/test.jpg --timeout 300 --overwrite
```

预期输出：

```text
results/ocr_result.json
```

确认 endpoint：

```text
http://127.0.0.1:8080/docs
/ocr
```

### 4. PP-StructureV3 serving

启动服务：

```powershell
.\scripts\start_ppstructure_service.ps1
```

另开一个 PowerShell 测试：

```powershell
python scripts/test_ppstructure_client.py --image samples/test.jpg --timeout 300 --overwrite
```

预期输出：

```text
results/ppstructure_result.json
```

确认 endpoint：

```text
http://127.0.0.1:8081/docs
/layout-parsing
```

### 5. Table Recognition v2 serving

启动服务：

```powershell
.\scripts\start_table_service.ps1 -Pipeline table_recognition_v2
```

另开一个 PowerShell 测试：

```powershell
python scripts/test_ocr_client.py --base-url http://127.0.0.1:8082 --endpoint /table-recognition --image samples/table.jpg --output results/table_recognition_result.json --timeout 600 --overwrite
```

预期输出：

```text
results/table_recognition_result.json
```

确认 endpoint：

```text
http://127.0.0.1:8082/docs
/table-recognition
```

## 验收标准

同事复现时，满足以下条件即可认为交付可用：

```text
python scripts/check_environment.py
```

能显示：

```text
paddleocr: ok
paddlex: ok
paddle: ok
samples/ exists: True
results/ exists: True
```

并且至少生成以下文件：

```text
results/ocr_result.json
results/ppstructure_result.json
results/table_recognition_result.json
results/table_cells.json
results/table_cells_visual/table_res.jpg
```

JSON 顶层应包含：

```text
OCR / PP-StructureV3 / Table Recognition v2:
  logId
  result
  errorCode = 0
  errorMsg = Success

Table Cells Detection:
  image
  model_name
  threshold
  results
```

## 交付边界

本目录只做官方 PaddleOCR / PaddleX 能力验证。

明确不包含：

```text
TamperShield core 接入
main.py 接入
tools/ 改造
Document-first pipeline 改造
本地业务 FastAPI
/api/document/parse
/api/compare/document
最终审计结论
tampered / not tampered 判断
PASS / FAIL 判断
```

## 注意事项

1. CPU 环境首次启动和首次请求会比较慢。
2. OCR / PP-StructureV3 建议使用 `--timeout 300`。
3. Table Recognition v2 建议使用 `--timeout 600`。
4. 不建议同时启动多个重模型 serving，容易出现内存不足。
5. 如果提示 serving 插件缺失，执行：

```powershell
paddlex --install serving
```

6. 如果模型下载失败，先检查网络和 PaddleX 模型缓存目录的磁盘空间。
7. Table Cells Detection 当前走 Python API，不是 serving。
8. Table Recognition v2 的本地 pipeline 名称已确认：

```text
table_recognition_v2
```

## 给同事的建议阅读顺序

1. `DELIVERY_NOTE.md`
2. `README_OFFICIAL_SERVING.md`
3. `OFFICIAL_OUTPUT_ANALYSIS.md`
4. `results/*.json`
5. `scripts/*.py` 和 `scripts/*.ps1`

## 后续 Phase 16

Phase 16 再决定是否写自己的业务网关。

建议保持边界：

```text
official PaddleOCR / PaddleX serving
        ↓
TamperShield OCR adapter / gateway, optional
        ↓
Document-first parser
        ↓
EvidenceIndex
```

即使后续写业务网关，也不应绕过：

```text
DocumentPage
DocumentElement
EvidenceIndex
```

也不应直接输出：

```text
tampered / not tampered
safe / unsafe
PASS / FAIL
```
