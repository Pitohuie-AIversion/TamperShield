# Phase 15：官方 PaddleOCR / PaddleX serving 输出结构分析与统一 JSON 草案

## 目标

本阶段只分析 `official_paddleocr_serving/` 下已经验证成功的官方 PaddleOCR / PaddleX 输出结果，并形成未来接入 TamperShield 前的统一 JSON 草案。

本阶段不做：

- 不接入 `core/`
- 不修改 `main.py`
- 不修改 `tools/`
- 不改造 Document-first pipeline
- 不封装 TamperShield 业务 API
- 不做最终审计判断

## 已分析文件

```text
official_paddleocr_serving/results/ocr_result.json
official_paddleocr_serving/results/ppstructure_result.json
official_paddleocr_serving/results/table_cells.json
official_paddleocr_serving/results/table_recognition_result.json
core/document_models.py
```

`core/document_models.py` 仅用于确认未来映射目标的数据形态：

```text
ParsedDocument
DocumentPage
DocumentElement
BoundingBox
```

## 官方 serving 顶层结构

OCR、PP-StructureV3、Table Recognition v2 的官方 serving 返回都遵循相同顶层包装：

```json
{
  "logId": "...",
  "result": {},
  "errorCode": 0,
  "errorMsg": "Success"
}
```

当前验证结果：

| 能力 | 文件 | result 主字段 | errorCode | errorMsg |
| --- | --- | --- | --- | --- |
| OCR | `ocr_result.json` | `ocrResults` | `0` | `Success` |
| PP-StructureV3 | `ppstructure_result.json` | `layoutParsingResults` | `0` | `Success` |
| Table Recognition v2 | `table_recognition_result.json` | `tableRecResults` | `0` | `Success` |

`Table Cells Detection` 当前不是 serving 输出，而是本地脚本包装输出：

```json
{
  "image": "samples/table.jpg",
  "model_name": "RT-DETR-L_wired_table_cell_det",
  "threshold": 0.3,
  "results": []
}
```

## OCR 输出结构

来源：

```text
results/ocr_result.json
```

主路径：

```text
result.ocrResults[0].prunedResult
```

已确认字段：

```text
model_settings
doc_preprocessor_res
dt_polys
text_det_params
text_type
textline_orientation_angles
text_rec_score_thresh
return_word_box
rec_texts
rec_scores
rec_polys
rec_boxes
```

页面信息：

```text
result.dataInfo.width
result.dataInfo.height
result.dataInfo.type
```

OCR 文本行对齐关系：

```text
rec_texts[i]  -> 第 i 条识别文本
rec_scores[i] -> 第 i 条文本置信度
rec_boxes[i]  -> 第 i 条轴对齐 bbox，格式 [x0, y0, x1, y1]
rec_polys[i]  -> 第 i 条四点 polygon
```

未来映射建议：

| 官方字段 | 统一 JSON 字段 | Document-first 映射 |
| --- | --- | --- |
| `rec_texts[i]` | `elements[].text` | `DocumentElement.text` |
| `rec_scores[i]` | `elements[].confidence` | `DocumentElement.metadata.ocr.confidence` |
| `rec_boxes[i]` | `elements[].bbox` | `DocumentElement.bbox` |
| `rec_polys[i]` | `elements[].polygon` | `DocumentElement.metadata.ocr.polygon` |
| `doc_preprocessor_res.angle` | `pages[].preprocessing.angle` | `DocumentPage.metadata.ocr.preprocessing.angle` |

OCR 输出不提供可靠语义块类型，因此默认映射为：

```text
element_type = "paragraph"
source_kind = "ocr_text_line"
```

后续只有在 PP-StructureV3 提供版面标签时，才升级为 `title` / `header` / `footer` / `table` / `image` 等类型。

## PP-StructureV3 输出结构

来源：

```text
results/ppstructure_result.json
```

主路径：

```text
result.layoutParsingResults[0].prunedResult
```

已确认字段：

```text
page_count
width
height
model_settings
parsing_res_list
doc_preprocessor_res
layout_det_res
overall_ocr_res
table_res_list
```

### 版面块

主路径：

```text
prunedResult.parsing_res_list[]
```

单项结构：

```json
{
  "block_label": "header",
  "block_content": "...",
  "block_bbox": [0, 0, 199, 52],
  "block_id": 0,
  "block_order": null
}
```

未来映射建议：

| 官方字段 | 统一 JSON 字段 | Document-first 映射 |
| --- | --- | --- |
| `block_label` | `elements[].type` / `elements[].source.type_label` | `DocumentElement.element_type` + metadata |
| `block_content` | `elements[].text` | `DocumentElement.text` |
| `block_bbox` | `elements[].bbox` | `DocumentElement.bbox` |
| `block_id` | `elements[].source.block_id` | `DocumentElement.metadata.source.block_id` |
| `block_order` | `elements[].reading_order` | `DocumentElement.metadata.reading_order` |

版面标签到 Document-first 类型的保守映射：

| PP-StructureV3 label | DocumentElement type |
| --- | --- |
| `doc_title`, `paragraph_title`, `figure_title`, `table_title` | `title` |
| `text`, `paragraph`, `content` | `paragraph` |
| `header`, `header_image` | `header` |
| `footer`, `footer_image` | `footer` |
| `table` | `table` |
| `image`, `figure`, `chart` | `image` |
| 其他未知标签 | `unknown` |

### layout 检测框

主路径：

```text
prunedResult.layout_det_res.boxes[]
```

单项结构：

```json
{
  "cls_id": 8,
  "label": "table",
  "score": 0.9717783331871033,
  "coordinate": [133.18, 313.18, 774.07, 504.34]
}
```

未来用途：

- 作为版面区域证据
- 补充 `DocumentElement.metadata.layout`
- 当 `parsing_res_list` 与 `layout_det_res` 可通过 bbox 匹配时，保留两者关联

### 整页 OCR

主路径：

```text
prunedResult.overall_ocr_res
```

结构与 OCR serving 的 `prunedResult` 基本一致：

```text
rec_texts
rec_scores
rec_boxes
rec_polys
```

未来用途：

- 支撑页面 `plain_text`
- 支撑 OCR text line 级证据
- 不直接进入 table compare

### 表格结果

主路径：

```text
prunedResult.table_res_list[]
```

已确认字段：

```text
cell_box_list
pred_html
table_ocr_pred
```

未来映射建议：

| 官方字段 | 统一 JSON 字段 | Document-first 映射 |
| --- | --- | --- |
| `pred_html` | `tables[].html` | `DocumentElement.metadata.table.html` |
| `cell_box_list` | `tables[].cells[].bbox` 或 `elements[].metadata.table.cell_boxes` | table metadata |
| `table_ocr_pred.rec_texts` | `tables[].ocr_texts` | table metadata |
| `table_ocr_pred.rec_scores` | `tables[].ocr_scores` | table metadata |

注意：

```text
pred_html -> pd.read_html(StringIO(pred_html)) -> DataFrame
```

DataFrame 只应在 `table_compare` 需要精查时生成，不应成为文档比较入口。

## Table Recognition v2 输出结构

来源：

```text
results/table_recognition_result.json
```

主路径：

```text
result.tableRecResults[0].prunedResult
```

已确认字段：

```text
model_settings
doc_preprocessor_res
layout_det_res
overall_ocr_res
table_res_list
```

`table_res_list[]` 与 PP-StructureV3 的表格结构一致：

```text
cell_box_list
pred_html
table_ocr_pred
```

当前验证结果包含：

```text
pred_html
cell_box_list
table_ocr_pred.rec_polys
table_ocr_pred.rec_texts
table_ocr_pred.rec_scores
```

未来用途：

- 用于单独表格结构识别
- 用于从 `pred_html` 生成 DataFrame
- 用于在 `DocumentElement(TABLE)` 内保留 HTML、cell bbox、OCR 文本与置信度
- 不作为完整文档比较入口

## Table Cells Detection 输出结构

来源：

```text
results/table_cells.json
```

当前本地包装结构：

```json
{
  "image": "samples/table.jpg",
  "model_name": "RT-DETR-L_wired_table_cell_det",
  "threshold": 0.3,
  "results": [
    {
      "res": {
        "input_path": "samples/table.jpg",
        "page_index": null,
        "boxes": []
      }
    }
  ]
}
```

单个 cell box：

```json
{
  "cls_id": 0,
  "label": "cell",
  "score": 0.9840070009231567,
  "coordinate": [248.20, 488.72, 558.06, 958.94]
}
```

未来映射建议：

| 官方/脚本字段 | 统一 JSON 字段 | 用途 |
| --- | --- | --- |
| `model_name` | `engines[].model_name` | 记录模型 |
| `threshold` | `engines[].params.threshold` | 记录检测阈值 |
| `boxes[].coordinate` | `tables[].cells[].bbox` | cell-level bbox |
| `boxes[].score` | `tables[].cells[].confidence` | cell 检测置信度 |
| `boxes[].label` | `tables[].cells[].source.label` | 检测类别 |

当前 Table Cells Detection 只给出 cell bbox，不给出行列号。后续若用于 cell-level 比对，需要确定：

- 是否由 Table Recognition v2 的 HTML / cell order 补行列
- 是否另做 deterministic cell-grid reconstruction
- 是否只作为 bbox 证据，不负责表格语义结构

## 统一 JSON v0.1 草案

统一 JSON 的目标不是替代 TamperShield `ParsedDocument`，而是作为官方 PaddleOCR / PaddleX 输出进入 TamperShield 前的中间层。

设计原则：

- 保留官方原始输出路径和关键 raw 片段
- 保留 bbox、polygon、confidence、page、engine、model、参数
- 不生成最终审计判断
- 不猜字段对应关系
- 不直接进入 `align_compare.py`
- 表格 DataFrame 只在后续 table inspection 需要时生成

### 顶层结构

```json
{
  "schema_version": "official_paddleocr_unified_v0.1",
  "source": {
    "input_path": "samples/test.jpg",
    "file_type": "image",
    "page_count": 1,
    "width": 867,
    "height": 1198
  },
  "engines": [],
  "pages": [],
  "raw_refs": []
}
```

### engine 记录

```json
{
  "engine_id": "ocr_001",
  "capability": "ocr",
  "provider": "paddle",
  "pipeline": "OCR",
  "endpoint": "/ocr",
  "status": "success",
  "error_code": 0,
  "error_message": "Success",
  "log_id": "...",
  "model_settings": {},
  "params": {}
}
```

`capability` 取值建议：

```text
ocr
layout_parsing
table_recognition
table_cells_detection
```

### page 记录

```json
{
  "page_number": 1,
  "width": 867,
  "height": 1198,
  "plain_text": "",
  "preprocessing": {
    "enabled": true,
    "angle": 0,
    "doc_orientation_classify": true,
    "doc_unwarping": true
  },
  "elements": [],
  "tables": [],
  "images": [],
  "metadata": {}
}
```

### element 记录

```json
{
  "element_id": "p1_e0001",
  "type": "paragraph",
  "source_kind": "ocr_text_line",
  "text": "华润置地",
  "confidence": 0.996994137763977,
  "bbox": {
    "page_number": 1,
    "x0": 48,
    "y0": 0,
    "x1": 204,
    "y1": 32
  },
  "polygon": [[48, 0], [204, 0], [204, 32], [48, 32]],
  "reading_order": null,
  "source": {
    "engine_id": "ocr_001",
    "official_path": "result.ocrResults[0].prunedResult.rec_texts[0]",
    "type_label": null,
    "block_id": null
  },
  "raw": {}
}
```

`type` 应对齐 `DocumentElement.element_type`：

```text
paragraph
title
table
image
header
footer
signature
blank
unknown
```

### table 记录

```json
{
  "table_id": "p1_t0001",
  "element_id": "p1_e0008",
  "source_kind": "table_recognition",
  "bbox": {
    "page_number": 1,
    "x0": 72.59,
    "y0": 97.69,
    "x1": 845.88,
    "y1": 1211.41
  },
  "html": "<html>...</html>",
  "cells": [],
  "ocr_texts": [],
  "source": {
    "engine_id": "table_recognition_001",
    "official_path": "result.tableRecResults[0].prunedResult.table_res_list[0]"
  },
  "raw": {}
}
```

### cell 记录

```json
{
  "cell_id": "p1_t0001_c0001",
  "row_index": null,
  "col_index": null,
  "rowspan": null,
  "colspan": null,
  "text": "",
  "confidence": 0.9840070009231567,
  "bbox": {
    "page_number": 1,
    "x0": 248.20,
    "y0": 488.72,
    "x1": 558.06,
    "y1": 958.94
  },
  "polygon": null,
  "source": {
    "engine_id": "table_cells_001",
    "official_path": "results[0].res.boxes[0]",
    "label": "cell"
  },
  "raw": {}
}
```

行列号默认 `null`，除非后续由 HTML 解析或确定性 grid reconstruction 得到。不得用 LLM 猜测。

## 转换优先级建议

面向未来 TamperShield 接入时，建议按以下优先级使用官方输出：

1. PP-StructureV3 `parsing_res_list` 作为文档元素主结构
2. PP-StructureV3 / OCR `overall_ocr_res` 作为 plain text 和 OCR text line 补充
3. PP-StructureV3 / Table Recognition v2 `table_res_list.pred_html` 作为表格结构来源
4. Table Cells Detection `boxes` 作为 cell-level bbox 补充证据
5. 原始官方 JSON 保留为 raw，不直接参与审计判断

## 与 Document-first 模型的映射

未来转换到 `DocumentPage` / `DocumentElement` 时建议：

```text
Unified page -> DocumentPage
Unified element -> DocumentElement
Unified table -> DocumentElement(element_type="table")
Unified bbox -> BoundingBox
Unified raw/source/confidence -> metadata
```

`DocumentPage.plain_text` 来源：

```text
优先 parsing_res_list.block_content 按 reading_order / block_id 排列
回退 overall_ocr_res.rec_texts 按出现顺序拼接
```

`DocumentElement.raw` 建议只放必要 raw 片段，不放完整 base64 图片，避免内存和报告膨胀。

## Phase 16 前置判断

进入 Phase 16 前已经具备：

1. 官方 serving 已验证：
   - OCR `/ocr`
   - PP-StructureV3 `/layout-parsing`
   - Table Recognition v2 `/table-recognition`
   - Table Cells Detection 本地 Python API
2. 官方输出结构已分析：
   - OCR text line
   - layout block
   - table HTML
   - table cell bbox
3. 统一 JSON v0.1 草案已确定。

Phase 16 可以讨论是否写自己的业务网关，但建议仍然保持两层边界：

```text
official PaddleOCR/PaddleX serving
        ↓
TamperShield OCR adapter / gateway, optional
        ↓
Document-first parser
        ↓
EvidenceIndex
```

业务网关不得直接输出：

```text
tampered / not tampered
PASS / FAIL
safe / unsafe
```

业务网关也不得绕过：

```text
DocumentPage / DocumentElement
EvidenceIndex
```

## 待确认问题

- 是否需要把 `Table Cells Detection` 也服务化，还是继续使用本地 Python API。
- 是否需要为 `table_recognition_v2` 单独写测试客户端，避免复用 `test_ocr_client.py` 的输出提示文案。
- 是否保留官方结果中的 base64 可视化图像，或只保存到文件并在统一 JSON 中记录路径。
- 是否将统一 JSON 草案固化为 JSON Schema 文件。
