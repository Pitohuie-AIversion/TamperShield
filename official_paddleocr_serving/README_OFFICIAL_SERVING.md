# PaddleOCR / PaddleX 官方服务化验证目录

## 目录目的

`official_paddleocr_serving/` 是 TamperShield 仓库内的独立官方 PaddleOCR / PaddleX serving 验证目录，用于整理和验证官方 OCR、PP-StructureV3、Table Recognition v2、Table Cells Detection 能力。

本目录不接入 TamperShield 的 `core/` 业务代码，不修改 `main.py`，不改造现有 Document-first pipeline，也不封装本地 FastAPI 业务接口。

## 为什么暂时不新开 repo

当前阶段只是官方服务化方案验证。把验证脚本、样例、结果和说明放在 `official_paddleocr_serving/` 中，更方便和 TamperShield 当前 OCR 集成阶段一起追踪。等官方 pipeline、服务 endpoint、GPU/Docker 部署方式都验证稳定后，再决定是否拆成独立 repo。

## 当前验证能力

| 能力 | 当前用途 | TamperShield 未来用途 |
| --- | --- | --- |
| OCR | 普通文字识别服务验证 | 普通文本识别 |
| PP-StructureV3 | 文档版面解析服务验证 | 文档版面解析，包含标题、段落、表格、图片、页眉页脚等结构化区域 |
| Table Recognition v2 | 表格结构识别服务验证 | 工程文档表格结构解析 |
| Table Cells Detection | 本地 Python API 验证 | 单元格 bbox 检测，用于 cell-level 比对 |

## Conda 环境

```powershell
conda create -n paddleocr_official python=3.10 -y
conda activate paddleocr_official
```

## 依赖安装

```powershell
pip install -r requirements_official.txt
paddlex --install serving
```

建议从本目录运行命令：

```powershell
cd official_paddleocr_serving
python scripts/check_environment.py
```

## OCR 服务启动

Linux / macOS:

```bash
bash scripts/start_ocr_service.sh
```

Windows PowerShell:

```powershell
.\scripts\start_ocr_service.ps1
```

默认启动：

```text
paddlex --serve --pipeline OCR --host 0.0.0.0 --port 8080
```

测试：

```powershell
python scripts/test_ocr_client.py --image samples/test.jpg
```

默认访问：

```text
http://127.0.0.1:8080/ocr
```

默认输出：

```text
results/ocr_result.json
```

如果服务启动后的 Swagger / docs / 控制台输出显示 endpoint 不同，请用 `--endpoint` 覆盖：

```powershell
python scripts/test_ocr_client.py --endpoint /your-official-endpoint
```

## PP-StructureV3 服务启动

Linux / macOS:

```bash
bash scripts/start_ppstructure_service.sh
```

Windows PowerShell:

```powershell
.\scripts\start_ppstructure_service.ps1
```

默认尝试：

```text
paddlex --serve --pipeline PP-StructureV3 --host 0.0.0.0 --port 8081
```

测试：

```powershell
python scripts/test_ppstructure_client.py --image samples/test.jpg
```

默认访问：

```text
http://127.0.0.1:8081/layout-parsing
```

默认输出：

```text
results/ppstructure_result.json
```

如果本地 PaddleX 对 PP-StructureV3 的 pipeline 注册名不同，请按官方命令确认可用 pipeline 名称，或导出官方 pipeline YAML，然后传入脚本。

Linux / macOS:

```bash
PADDLEX_PIPELINE=/path/to/ppstructure_pipeline.yaml bash scripts/start_ppstructure_service.sh
```

Windows PowerShell:

```powershell
.\scripts\start_ppstructure_service.ps1 -Pipeline C:\path\to\ppstructure_pipeline.yaml
```

## Table Recognition v2 服务启动

Table Recognition v2 的 PaddleOCR CLI 名称通常写作 `table_recognition_v2`，但 PaddleX serving 的 `--pipeline` 注册名需要以本地安装版本的官方输出为准。本目录不强行写死不确定名称。

请先用 PaddleX / PaddleOCR 官方命令或官方配置文件确认 pipeline 名称，也可以导出官方 pipeline YAML，然后启动：

Linux / macOS:

```bash
PADDLEX_PIPELINE=<official-name-or-yaml-path> bash scripts/start_table_service.sh
```

Windows PowerShell:

```powershell
.\scripts\start_table_service.ps1 -Pipeline <official-name-or-yaml-path>
```

目标服务默认端口：

```text
8082
```

官方文档中 Table Recognition v2 serving endpoint 为：

```text
/table-recognition
```

如果服务启动后的 Swagger / docs / 控制台输出显示 endpoint 不同，请以本地服务输出为准。

## Table Cells Detection 本地测试

默认模型：

```text
RT-DETR-L_wired_table_cell_det
```

测试命令：

```powershell
python scripts/test_table_cells_detection.py --image samples/table.jpg --output-dir results
```

可选无线表格模型预留：

```powershell
python scripts/test_table_cells_detection.py --image samples/table.jpg --output-dir results --model-name RT-DETR-L_wireless_table_cell_det
```

默认输出：

```text
results/table_cells.json
results/table_cells_visual/
```

脚本默认不覆盖已有结果。如需重新生成：

```powershell
python scripts/test_table_cells_detection.py --image samples/table.jpg --output-dir results --overwrite
```

## 当前阶段不做的事情

- 不接入 `core/`
- 不写本地 FastAPI
- 不做 `/api/document/parse`
- 不做 `/api/compare/document`
- 不做 document compare
- 不做 TamperShield 主流程改造
- 不修改现有 table compare / document compare 逻辑

## 后续阶段计划

1. 阶段 1：官方 PaddleOCR serving 验证
2. 阶段 2：确定需要保留的 pipeline
3. 阶段 3：再决定是否封装 TamperShield 业务 API
4. 阶段 4：再考虑 Docker / Nginx / GPU 部署

## 需要本地确认的 pipeline 名称

以下名称需要根据本地 PaddleX / PaddleOCR 版本确认：

- PP-StructureV3 的 PaddleX serving pipeline 注册名
- Table Recognition v2 的 PaddleX serving pipeline 注册名
- Table Cells Detection 是否需要 serving 化，或继续使用 Python API 本地调用

确认方式：

- 查看 `paddlex --serve --pipeline ...` 启动失败或成功时的控制台输出
- 查看服务启动后的 Swagger / docs endpoint
- 使用 PaddleOCR 官方文档中的 pipeline usage 示例导出配置文件
- 将官方 YAML 配置文件路径传给 `--pipeline`

## 官方参考

- PaddleX 服务化部署：`paddlex --install serving` 与 `paddlex --serve --pipeline ...`  
  https://paddlepaddle.github.io/PaddleX/3.5/en/pipeline_deploy/serving.html
- PaddleOCR OCR serving：默认 endpoint `/ocr`  
  https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html
- PaddleOCR PP-StructureV3 serving：默认 endpoint `/layout-parsing`  
  https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/PP-StructureV3.html
- PaddleOCR Table Recognition v2 serving：默认 endpoint `/table-recognition`  
  https://www.paddleocr.ai/v3.4.1/version3.x/pipeline_usage/table_recognition_v2.html
- PaddleOCR Table Cells Detection：默认模型可使用 `RT-DETR-L_wired_table_cell_det`  
  https://www.paddleocr.ai/main/en/version3.x/module_usage/table_cells_detection.html
