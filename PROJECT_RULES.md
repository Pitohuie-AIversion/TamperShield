# TamperShield（防篡改之盾）AI 研发约束指南

## 项目定位与核心原则

TamperShield 是 Document-first 的工程文档防篡改比对系统，不是表格比对工具。处理对象是一份待核验工程文档 vs 一份或多份基准电子稿。

系统应对完整文档进行核验，包括页面、段落、标题、表格、图片、签章、页眉页脚、附件页、空白页和版式区域，并生成可追溯的审计证据链。

表格只是文档中的一种元素，必须作为子能力下沉到 `table_compare` 层，不得作为主流程入口。`core/table_matcher.py` 和 `core/align_compare.py` 仍然有价值，但只能作为 `table_compare` 层的子模块。最终报告必须基于页面、区域、元素和证据链，而不是只输出 DataFrame 差异。

工程审计不允许幻觉。所有数据提取、字段匹配、金额比对、数量比对、逻辑判断和篡改判定，严禁引入大语言模型进行语义猜测、表格脑补、字段补全或内容修正。最终结果必须基于视觉坐标、OCR 输出、原生 PDF/DOCX 结构、图像处理结果、物理表格结构、确定性规则和 DataFrame 比对逻辑。

## Document-first 架构规则

项目主流程必须遵循：

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

严禁使用以下主线：

```text
Table compare
  ↓
Document conclusion
```

必须使用以下主线：

```text
Document compare
  ↓
Page compare
    ↓
Element compare
      ↓
Table compare, if needed
```

模块职责：

```text
document_parser
  解析 DOCX / PDF 的全文内容、页面、段落、表格、图片、页眉页脚、签章和区域信息

page_aligner
  将待核验文档页面与基准电子稿页面进行顺序对齐、错页检测、缺页检测和新增页检测

content_compare
  比较页面级文本、段落级文本、标题、页眉页脚、图片、签章、空白页状态和版式变化

table_compare
  只在页面中存在表格且需要精查时调用，用于表格级匹配、行列对齐和单元格级比对

evidence_index
  记录每个差异来自哪个文件、哪一页、哪个段落、哪个表格、哪个单元格、哪个图片区域或哪个页面区域

report_generator
  只消费 EvidenceIndex，将已有证据组织成摘要、页面分组和可读报告
```

## Pipeline 迁移规则

当前项目允许旧版 `main.py::run_tamper_shield_pipeline(...)` 与新版 Document-first pipeline 并存。

新版 Document-first pipeline 的独立调度入口位于：

```text
core/document_pipeline.py
```

其中：

```text
collect_document_differences(...)
compare_parsed_documents(...)
compare_documents(...)
```

代表新的文档级核验主线。

Phase 8b 已完成后，`main.py` 允许同时暴露两个入口：

```text
run_tamper_shield_pipeline(...)
  Legacy table-first flow

run_document_first_pipeline(...)
  Document-first flow
```

`run_document_first_pipeline(...)` 必须默认返回 `EvidenceIndex`，不得默认写文件或生成报告。

在旧流程完全废弃前，禁止删除或破坏 `main.py::run_tamper_shield_pipeline(...)`。如果需要让 `main.py` 支持 Document-first pipeline，只能新增并行入口，不得直接把旧 table-first pipeline 改写成新流程，也不得破坏现有参数、返回值和写入权限控制。

## 报告导出规则

Phase 9 已完成后，报告生成能力位于：

```text
core/report_generator.py
```

报告生成入口包括：

```text
generate_markdown_report(...)
write_text_report(...)
generate_report_bundle(...)
```

报告生成模块必须以 `EvidenceIndex` 为输入，不得重新执行文档解析、页面对齐、内容比对、表格精查、OCR、预处理或 LLM 判断。

`main.py::run_document_first_pipeline(...)` 可以通过可选参数导出 Markdown 报告：

```text
report_output_path
allow_write
overwrite
```

默认情况下，`report_output_path=None`，函数只返回 `EvidenceIndex`，不得生成报告文件。

只有当用户显式传入 `report_output_path` 且 `allow_write=True` 时，才允许写出 Markdown 报告。

报告不得生成 `tampered / not tampered`、`safe / unsafe`、`PASS / FAIL` 等最终审计结论；报告只能呈现 `EvidenceIndex` 中已有的差异、证据位置、严重程度、metadata、人工复核标记和表格精查标记。

## OCR Integration Rules

OCR is a supporting parser capability, not a separate table-first product flow.

Existing OCR-related modules include:

```text
core/pre_processing.py
core/ocr_engine.py
```

These legacy OCR capabilities may remain for compatibility, but new OCR development must integrate with the Document-first architecture.

The required OCR integration path is:

```text
image / scanned PDF
        ↓
preprocess_pipeline(...)
        ↓
OCR layout / OCR text / OCR table extraction
        ↓
DocumentPage / DocumentElement
        ↓
page_aligner
        ↓
content_compare
        ↓
table_compare, only when needed
        ↓
EvidenceIndex
        ↓
report_generator
```

Rules:

* OCR must not directly produce final audit conclusions.
* OCR must not bypass `EvidenceIndex`.
* OCR table extraction must not become the main product flow.
* OCR text blocks should become `DocumentElement` text-like elements, such as paragraph / title / header / footer when possible.
* OCR table results should become `DocumentElement(TABLE)` when possible.
* OCR image / seal / figure regions should become image-like `DocumentElement` records when possible.
* OCR confidence, bounding box, page number, source image path, preprocessing parameters, and OCR engine metadata should be preserved in evidence metadata where available.
* OCR-backed parsing should be optional and explicit at first, not enabled silently for all documents.
* Legacy OCR table-first functions may remain for compatibility, but new product features should enter through the Document-first parser and EvidenceIndex.

### OCR Development Do Not

- Do not route OCR results directly to DataFrame comparison as the main product path.
- Do not make OCR table extraction the primary business workflow.
- Do not use OCR output to claim final document status automatically.
- Do not discard OCR bounding boxes or confidence scores.
- Do not modify existing Document-first API unless explicitly planned.

## 强制技术栈架构

任何新增代码必须遵循本项目指定的库使用规范，不得擅自引入功能重叠的第三方包。

- 图像预处理统一使用 `opencv-python` 和 `numpy`
- 表格与结构提取统一使用 `paddlepaddle` 和 `paddleocr`
- 原生文档解析统一使用 `PyMuPDF`、`python-docx` 和必要时的 `pdfplumber`
- 数据对齐与比对统一使用 `pandas`、`Decimal`、编辑距离和确定性规则

表格与结构提取默认采用已验证可运行的 PaddleOCR 3.x 路线：

```text
paddle == 3.2.2
paddleocr == 3.5.0
paddlex == 3.5.1
```

默认结构化识别路线：

```text
PPStructureV3.predict()
        ↓
LayoutParsingResultV2
        ↓
table_res_list
        ↓
pred_html
        ↓
pd.read_html(StringIO(pred_html))
        ↓
pandas.DataFrame
```

禁止在模块顶层直接 `from paddleocr import PPStructure`。必须通过懒加载函数创建结构化解析引擎，避免不同 PaddleOCR 版本 API 差异导致 import 失败。`parse_layout_to_blocks()` 必须同时兼容旧版 callable engine 和新版带 `.predict()` 方法的 `PPStructureV3`。

解析 HTML 字符串时必须使用：

```python
from io import StringIO
pd.read_html(StringIO(pred_html))
```

不得直接使用：

```python
pd.read_html(pred_html)
```

## 红章处理专项规则

红章处理的目标是红章抑制与黑色笔画保护，不是整块擦除印章。

图像预处理环节严禁使用 HSV 掩码直接去红章。禁止使用 `cv2.cvtColor(image, cv2.COLOR_BGR2HSV)`、`cv2.inRange()` 生成红色区域掩码后，再执行 `result[red_mask > 0] = (255, 255, 255)` 这一类整块白化操作。

红章处理必须采用 RGB 或 R 通道分离策略，并通过反色形态学方法提取和保护黑色笔画区域。处理优先级必须始终遵循：

```text
保护黑色文字
        ↓
保护表格线
        ↓
压淡红章
        ↓
图像视觉美观
```

必须通过 R 通道反色和形态学操作提取 `black_text_mask`。后续任何红章抑制、背景增强或局部提亮操作，都不得破坏 `black_text_mask` 区域。

Deskew 倾斜校正必须使用几何估计方法，允许使用 `HoughLinesP` 或 `cv2.minAreaRect`。禁止固定角度旋转，例如直接设定 `angle = 2.0` 后旋转图像。

## 原生文档规则

原生电子件必须优先直接解析内部结构。对于 `.docx` 原生电子稿，应优先使用 `python-docx` 提取段落、标题、表格和可识别结构。对于 `.pdf` 原生电子稿，`PyMuPDF` 用于提取页面、文本、坐标、块信息和图片区域，`pdfplumber` 可用于提取 PDF 表格结构。

对于 DOCX 文档，如果系统环境存在 LibreOffice / soffice，应优先尝试将 DOCX 渲染为临时 PDF，以获得更接近发布态的页码和页面布局。渲染 PDF 仅用于页面级对齐和文本块定位；原生 DOCX 表格结构仍可作为后续表格精查的辅助来源。若 LibreOffice 不可用，才回退到 DOCX native single-page parsing。

除非用户明确要求，否则不得无故将原生 PDF 或 DOCX 转换为图片后再 OCR，也不得无故丢弃原生文本、页面结构和表格结构。

DOCX 和 PDF 同时存在时，应先进入文档级对齐。不得默认只把 DOCX 表格作为 `base_df` 并跳过逐页内容核验。

## Windows / Chinese Path / LibreOffice Notes

For command-line validation on Windows, prefer discovering input files with `Path.glob()` instead of embedding long Chinese paths directly inside `python -c` strings.

Recommended pattern:

```powershell
conda run -n tamper_shield python -c "from pathlib import Path; from main import run_document_first_pipeline; pdf=list(Path('data/base_docs').glob('*.pdf'))[0]; docx=list(Path('data/base_docs').glob('*.docx'))[0]; idx=run_document_first_pipeline(candidate_file=pdf, baseline_file=docx); print(idx.summary()); print(idx.metadata)"
```

When viewing Markdown reports in PowerShell, use:

```powershell
Get-Content data/output/<report>.md -Encoding UTF8
```

Do not prepend LibreOffice's program directory to PATH before running `conda run ... python`; doing so may cause `python` to resolve to LibreOffice's bundled python-core. If LibreOffice is needed, append its path or call `soffice.exe` explicitly.

Current validated baseline:

```text
candidate_page_count=39
baseline_page_count=44
difference_count=69
page_reordered=0
```

The observed Chinese-path mojibake in earlier report viewing was a display/command-wrapper issue, not a confirmed internal Unicode bug.

## CLI / Demo Runner Rules

A future CLI or demo runner may be added under `tools/`, for example:

```text
tools/run_document_demo.py
```

The CLI must be a thin wrapper around:

```text
main.py::run_document_first_pipeline(...)
```

The CLI must not directly orchestrate:

```text
document_parser
page_aligner
content_compare
table_compare
report_generator internals
```

The CLI must preserve the same safety model:

```text
default = read-only
report writing requires explicit --allow-write
report_output_path must be explicit
overwrite defaults to false
```

The CLI must not output final audit judgments:

```text
tampered / not tampered
safe / unsafe
PASS / FAIL
篡改 / 未篡改
安全 / 不安全
```

The CLI may print:

```text
EvidenceIndex.summary()
EvidenceIndex.metadata
report path when explicitly written
```

The CLI should prefer `Path.glob()` or explicit path arguments to avoid Windows Chinese-path command-line display issues.

Current CLI wrapper:

```text
tools/run_document_demo.py
```

The CLI has been implemented as a thin wrapper around:

```text
main.py::run_document_first_pipeline(...)
```

Validated behavior:

```text
default read-only execution
--auto-discover read-only run works with one PDF and one DOCX
--report-output without --allow-write is blocked
--show-metadata works
--show-records N works
no direct core parser / aligner / compare imports
```

LibreOffice subprocess decoding note:

```text
core/document_parser.py should keep explicit encoding/error handling for LibreOffice subprocess output:
encoding="utf-8"
errors="replace"
```

## 表格子能力规则

文档级对齐与比对必须先形成可追溯的页面、区域和元素结构，再根据元素类型进入段落、图片、签章、空白页或表格比对。

表格元素进入 `align_compare.py` 前，必须完成 DataFrame 化、列名标准化、合并单元格展开、空白字符清洗、数值字段格式清洗和主键字段明确。面对合并单元格，必须使用 `df.ffill()` 或等价显式逻辑展开主键。

页面内表格元素进入单元格比对前，必须先进行表级候选匹配。表级匹配应使用确定性特征打分，例如列名相似度、表头/前几行文本相似度、行列结构相似度、主键候选值重合度，并输出可解释的候选排序结果。

表级匹配不得使用 LLM 猜测表格对应关系。只有当候选分数达到明确阈值，或页面级证据和用户确认已锁定对应表格时，才允许进入 `compare_cells_with_tolerance()`。

## 代码规范与目录约束

项目必须保持统一数据流。待核验文档和基准电子稿首先进入 `document_parser`，形成可追溯的页面和元素结构；随后进入 `page_aligner` 完成页面顺序对齐、缺页、新增页和错页检测；再进入 `content_compare` 做页面级和元素级比对；只有页面内表格需要精查时，才进入 `table_compare`。

`main.py` 只能作为 pipeline 宏观调度中心，不能堆叠图像预处理细节、OCR 解析细节、文档解析细节、页面对齐细节、DataFrame 清洗细节、比对算法细节或报告生成细节。

测试扫描件输入应放入 `data/raw_scans/`。原生电子件输入应放入 `data/base_docs/`。导出报告、中间清洗图、结构化表格和比对结果应输出到 `data/output/`。

未经用户明确确认，不得主动创建、覆盖、删除、移动或重命名任何文件。

## 写入限制

绝对禁止在未经明确许可的情况下执行任何写入、修改或覆盖操作。禁止行为包括 save、write、export、overwrite、delete、move、rename 和 commit。

如果任务需要写入文件，必须先确认输出目录、文件名和是否允许覆盖。如果无法确认，必须输出：

```text
[Output Blocked] - Permission Required
```

不得自动生成最终保存路径或文件名。报告导出必须显式传入输出路径，且写文件必须要求 `allow_write=True`；不得覆盖已有文件，除非 `overwrite=True`。

## AI 助手行为准则

在修改或新增代码前，必须先阅读本规则文件、`AGENTS.md`、`TODO.md`、相关 `core/` 模块、相关 `tools/` 脚本，以及任务涉及入口时的 `main.py` 调用关系。

不得删除兼容接口，不得随意修改函数名、参数名或返回值格式。不得把所有逻辑塞入 `main.py`。

大语言模型只能用于代码辅助、错误分析、流程设计、规则整理、报告文字润色和开发说明，不得参与最终审计数据的生成、修正、补全或判断。

## 最低测试验收标准

每次修改至少必须保证相关模块可以正常 import，`tools` 脚本不因函数名变化报 `ImportError`，输出结果可复现、可追溯、可解释。

核心模块导入检查示例：

```powershell
python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('pre_processing import ok')"

python -c "from core.document_pipeline import compare_documents, compare_parsed_documents, collect_document_differences; print('document_pipeline import ok')"

python -c "from core.report_generator import generate_markdown_report, write_text_report, generate_report_bundle; print('report_generator import ok')"
```

## 禁止项总结

项目严禁使用 HSV 掩码直接白化红章，严禁对红色掩码区域整块置白，严禁为了去章破坏黑色文字，严禁为了去章破坏表格线，严禁使用固定角度 deskew，严禁用 LLM 猜测表格内容，严禁用 LLM 补全缺失字段，严禁用 LLM 判断金额是否一致，严禁把所有逻辑塞入 `main.py`，严禁未经许可写入、覆盖或删除文件，严禁默认生成保存路径和文件名，严禁无故把原生 PDF 转图片 OCR，严禁把 OCR 原始文本直接送入 `align_compare.py`，严禁删除兼容接口导致工具脚本失效。
