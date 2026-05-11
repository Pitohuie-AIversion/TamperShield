# TamperShield（防篡改之盾）AI 研发约束指南

## 项目定位与核心原则

TamperShield 的目标是构建“一对多”跨模态工程文档防篡改比对流水线，处理对象是扫描件总文件与原生电子件子文件之间的结构化比对关系。项目主要面向工程造价清单、工程量清单、结算书、审计附件、报价单、合同清单以及其他复杂表格型工程文档。系统目标不是普通 OCR，而是完成从结构化提取、表格对齐、字段比对、篡改定位到可追溯报告生成的完整流程。

工程审计容不得任何幻觉。所有数据提取、表格结构恢复、字段补全、金额比对、数量比对、逻辑判断和篡改判定环节，严禁引入大语言模型进行语义猜测、表格脑补、字段补全或内容修正。所有最终结果必须严格基于视觉坐标、OCR 输出、原生 PDF 内部结构、图像处理结果、表格物理结构、确定性规则和 DataFrame 比对逻辑。大语言模型只能用于代码辅助、错误分析、流程设计、规则整理、报告文字润色和开发说明，不得参与最终审计数据的生成、修正、补全或判断。

## 强制技术栈架构

任何新增代码必须遵循本项目指定的库使用规范，不得擅自引入功能重叠的第三方包。图像预处理统一使用 `opencv-python` 和 `numpy`。表格与结构提取统一使用 `paddlepaddle` 和 `paddleocr`。原生文档解析统一使用 `PyMuPDF` 和 `pdfplumber`。数据对齐与比对统一使用 `pandas` 和 `python-Levenshtein`。

图像预处理环节严禁使用 HSV 掩码直接去红章。禁止使用 `cv2.cvtColor(image, cv2.COLOR_BGR2HSV)`、`cv2.inRange()` 生成红色区域掩码后，再执行 `result[red_mask > 0] = (255, 255, 255)` 这一类整块白化操作。原因是 HSV 红色掩码会破坏红章覆盖下的黑色笔画，当红章和黑色文字重叠时，直接白化红色掩码区域会导致文字断裂、缺失或消失。红章处理必须采用 RGB 或 R 通道分离策略，并通过反色形态学方法提取和保护黑色笔画区域。红章处理目标是红章抑制与黑色笔画保护，而不是整块擦除印章。处理优先级必须始终遵循保护黑色文字优先于保护表格线，保护表格线优先于压淡红章，压淡红章优先于图像视觉美观。

红章处理推荐以 R 通道作为文档灰度基础。因为在 R 通道中，红章通常会自然变亮，而黑色文字仍然保持较暗。处理时应先提取 R 通道，再对 R 通道进行反色，通过二值化、开运算、闭运算和连通域筛选提取 `black_text_mask`。后续任何红章抑制、背景增强或局部提亮操作，都不得破坏 `black_text_mask` 区域。处理结束后，必须通过 `processed[black_text_mask > 0] = protected_gray[black_text_mask > 0]` 或等价逻辑恢复黑色笔画区域。

Deskew 倾斜校正必须使用几何估计方法。允许使用 `HoughLinesP` 或 `cv2.minAreaRect`。`HoughLinesP` 适合表格线、边框线和长文本行明显的文档，`cv2.minAreaRect` 适合正文区域明显但无明显表格线的文档。禁止使用固定角度旋转，例如禁止直接设定 `angle = 2.0` 后旋转图像。Deskew 过程必须基于灰度化、二值化或边缘检测结果提取文本线、表格线或前景像素，再估计倾斜角并旋转校正。旋转边界必须使用白色填充，校正过程不得裁掉正文或表格主体，倾斜角必须能够打印或返回。

表格与结构提取默认采用已验证可运行的 PaddleOCR 3.x 路线。当前项目基准组合为 `paddle==3.2.2`、`paddleocr==3.5.0`、`paddlex==3.5.1`。扫描件表格结构识别默认使用 `PPStructureV3`，其输出对象为 `LayoutParsingResultV2`。表格结果必须优先从 `table_res_list` 中读取，并从每个 table item 的 `pred_html` 字段提取 HTML 表格，再通过 `pd.read_html(StringIO(pred_html))` 转换为 `pandas.DataFrame`。

代码必须保留对旧版 PaddleOCR 2.x `PPStructure` dict 输出格式的兼容层，即兼容 `block["type"] == "table"` 和 `block["res"]["html"]`。但默认开发、测试和生产路线以 PaddleOCR 3.x / `PPStructureV3.predict()` 为准。

禁止在模块顶层直接 `from paddleocr import PPStructure`。必须通过懒加载函数创建结构化解析引擎，避免不同 PaddleOCR 版本 API 差异导致 import 失败。`parse_layout_to_blocks()` 必须同时兼容旧版 callable engine 和新版带 `.predict()` 方法的 `PPStructureV3`。

从 `PPStructureV3` 获得的 `pred_html` 是 HTML 字符串。解析时必须使用：

```python
from io import StringIO
pd.read_html(StringIO(pred_html))
```

不得直接使用：

```python
pd.read_html(pred_html)
```

原因是 pandas 后续版本将弃用直接传入 literal HTML string 的行为。

Windows 中文路径测试时，优先使用 Python 内部 `Path.glob()` 获取真实路径，避免 PowerShell 手写中文路径导致转码、空格或文件名匹配问题。

原生电子件必须优先直接解析 PDF 内部结构。`PyMuPDF` 用于提取 PDF 文本、页面、坐标和块信息，`pdfplumber` 用于无损提取原生 PDF 表格结构。除非用户明确要求，否则不得无故将原生 PDF 转换为图片后再 OCR，也不得无故丢弃 PDF 原生文本和表格结构。能够从 PDF 内部对象直接提取的信息，不得降级为图像 OCR 处理。

数据对齐与比对必须统一进入 `pandas.DataFrame`。所有提取数据进入 `align_compare.py` 前，必须完成 DataFrame 化、列名标准化、合并单元格展开、空白字符清洗、数值字段格式清洗和主键字段明确。面对合并单元格，必须使用 `df.ffill()` 或等价显式逻辑展开主键。文本容错必须基于 Levenshtein 编辑距离，禁止用大语言模型语义相似度或自然语言判断替代确定性比对。金额、数量、单价和合价等字段必须先去除逗号、人民币符号和异常空白，统一负号格式和小数位，再转换为 `float` 或 `Decimal` 进行比较。金额字段推荐使用 `Decimal`，金额比对必须设置明确误差阈值，例如 0.01 元。

## 代码规范与目录约束

项目必须保持统一数据流。扫描件或原生 PDF 首先进入图像预处理模块或原生 PDF 解析模块，随后进入结构提取模块，再进入数据标准化模块，最终以 `pandas.DataFrame` 形式进入 `align_compare.py`，最后由报告模块生成结果。不得将 OCR 原始 list、dict 或纯文本结果直接送入比对模块。

项目必须保持模块化。`main.py` 只能作为 Pipeline 宏观调度中心，不能堆叠图像预处理细节、OCR 解析细节、DataFrame 清洗细节、比对算法细节或报告生成细节。推荐模块包括 `core/pre_processing.py`、`core/structure_extract.py`、`core/native_pdf_parser.py`、`core/data_normalize.py`、`core/align_compare.py` 和 `core/report_generator.py`。模块之间必须通过明确数据结构传递，不允许依赖全局变量传递状态。

测试扫描件输入应放入 `data/raw_scans/`。原生电子件输入应放入 `data/base_docs/`。导出报告、中间清洗图、结构化表格和比对结果应输出到 `data/output/`。未经用户明确确认，不得主动创建、覆盖、删除、移动或重命名任何文件。

## AI 助手行为准则

在修改或新增代码前，必须先阅读本规则文件、`core/` 目录下的现有代码逻辑、相关 `tools/` 脚本以及 `main.py` 中的调用关系。不得在不了解现有工程结构的情况下直接给出覆盖式代码。不得删除兼容接口，不得随意修改函数名、参数名或返回值格式。

绝对禁止在未经明确许可的情况下执行任何写入、修改或覆盖操作。禁止行为包括 save、write、export、overwrite、delete、move、rename 和 commit。如果任务需要写入文件，必须先确认输出目录、文件名和是否允许覆盖。如果无法确认，必须输出 `[Output Blocked] - Permission Required` 并停止操作。不要主动创建、覆盖或删除文件。如果完成任务需要中间文件，必须先询问用户是否允许创建该文件。不得自动生成最终保存路径或文件名。

助手不是决策者。不要替用户决定使用哪个算法、哪个库、哪条技术路线、是否覆盖文件或是否生成报告，除非用户已经明确指定。当存在多个可行方案时，必须列出可选方案、适用场景、风险以及是否符合当前规则，再等待用户选择。如果用户要求列出已安装库，应优先通过环境检查命令获得，不得凭空假设。

遇到跨行、跨列表格处理请求时，首选 PP-Structure HTML 结构解析、pandas DataFrame 对齐、`df.ffill()` 和主键列规则化。不得优先在物理图像层级强行像素切割复杂表格，除非用户明确要求进行图像级表格线分析。

除非用户要求详细解释，否则输出应保持简洁。优先输出结论、代码、修改点和下一步命令，避免添加无关背景说明。

## 红章处理专项规则

红章处理的总目标是 Red Seal Suppression with Black Stroke Preservation，即红章抑制与黑色笔画保护。红章处理不是简单擦除印章，而是在尽量压淡红章干扰的同时，最大限度保留红章覆盖区域下方的黑色文字、表格线和签字笔画。

必须通过 R 通道反色和形态学操作提取 `black_text_mask`。推荐流程是先提取 R 通道，再进行反色 `inv = 255 - r`，随后二值化提取黑色文字前景，通过开运算清理噪声，通过闭运算连接轻微断裂笔画，再通过连通域筛选去除孤立噪点，最终得到 `black_text_mask`。红章处理后必须恢复或保护黑色笔画区域。

禁止对 `red_mask` 区域整块置白，禁止对 `dilated_red_mask` 区域整块置白，禁止大范围 dilation 后整体置白，禁止为了去章牺牲黑色文字，禁止为了去章破坏表格线。允许使用 R 通道自然削弱红章，允许对非黑字区域温和提亮，允许进行背景光照归一化，允许使用 CLAHE 温和增强，允许恢复 `black_text_mask` 区域。

## 输出模式与接口要求

`core/pre_processing.py` 必须保留 `preprocess_pipeline(...)`、`remove_red_seal(...)`、`estimate_skew_angle(...)` 和 `deskew_image(...)` 接口。其中 `remove_red_seal(...)` 只是兼容旧函数名，内部不得再使用 HSV 白化策略。预处理模块至少应支持 `gray`、`binary` 和 `color` 三种输出模式。默认推荐输出 `gray`，因为强二值化容易造成字迹粘连或断裂，灰度增强图通常更适合 OCR 和人工复核。

图像读取和保存必须支持中文路径、空格路径和 Windows 路径。推荐使用 `np.fromfile(...)` 与 `cv2.imdecode(...)` 读取图像，使用 `cv2.imencode(...)` 与 `encoded.tofile(...)` 保存图像。应避免直接依赖 `cv2.imread(...)` 和 `cv2.imwrite(...)`，因为它们在部分 Windows 中文路径下可能失败。

## 修改考核标准

任何修改必须满足可复现、可追溯、可解释、可比对的要求，视觉美观只能排在最后。凡是引入 LLM 猜测数据、破坏黑色文字或表格线、使用 HSV 掩码直接白化红章、无法追溯字段来源、输出结果无法复现、未经许可写入覆盖或删除文件的修改，均直接判定为不通过。

修改前必须检查项目规则文件、`core/` 目录相关模块、`tools/` 目录中调用该模块的脚本，以及当前函数接口是否被其他脚本依赖。未检查现有调用关系就直接改函数名、删参数或删接口，判定为不通过。`preprocess_pipeline(...)`、`remove_red_seal(...)`、`estimate_skew_angle(...)` 和 `deskew_image(...)` 必须保留。允许内部实现更新，但不允许删除旧接口。如果必须改变参数，必须通过 `**kwargs` 或显式保留旧参数来保证兼容。

图像预处理修改必须使用 RGB 或 R 通道分离作为主流程，必须使用 R 通道削弱红章，必须使用反色形态学提取 `black_text_mask`，必须在红章抑制后恢复或保护 `black_text_mask`，不得对红色掩码区域整块置白。只要生产流程中出现 HSV mask 直接白化红章，直接判定为不通过。

黑字保护必须同时通过肉眼和程序检查。肉眼检查要求红章覆盖区域下方文字不能断裂，黑色表格线不能明显缺失，数字、金额和小数点不能被抹掉，字迹不能严重粘连。程序检查要求 `black_text_mask` 必须存在，`black_text_mask` 区域处理前后不能被大面积置白，处理后文字前景面积不能异常下降。建议将黑字前景面积下降超过 15% 判定为警告，将下降超过 25% 判定为不通过。

Deskew 必须使用 `HoughLinesP` 或 `cv2.minAreaRect`。固定角度旋转直接判定为不通过。Deskew 输出必须满足倾斜角可打印或可返回，小角度可跳过旋转，旋转边界用白色填充，不得裁掉正文或表格主体。

所有进入 `align_compare.py` 的数据必须是 `pandas.DataFrame`。DataFrame 必须完成列名标准化、合并单元格展开、空白字符清洗、数字字段格式转换和主键字段明确。不允许把 list、dict 或 OCR 原始文本直接送入比对模块。文本字段比对必须输出原始文本 A、原始文本 B、编辑距离、相似度和是否超过阈值。数值字段比对必须输出原始数值 A、原始数值 B、清洗后数值 A、清洗后数值 B、差值和是否超过阈值。所有比对结果必须可追溯到原始字段来源。

## 最低测试验收标准

每次修改至少必须保证相关模块可以正常 import，`tools` 脚本不因函数名变化报 `ImportError`，红章覆盖文字区域没有明显断笔，表格线没有明显缺失，Deskew 后正文基本水平，输出 DataFrame 行列结构合理，合并单元格已正确展开，比对结果可追溯到原始字段。

最低运行检查命令为 `python tools/batch_tune_thresholds.py`。核心模块导入检查命令为 `python -c "from core.pre_processing import preprocess_pipeline, remove_red_seal, estimate_skew_angle, deskew_image; print('import ok')"`。

PaddleOCR 结构化表格最低测试命令：

```powershell
python -c "from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata, inspect_structure_output; print('ocr_engine import ok')"

python -c "from pathlib import Path; from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_with_metadata; img = next(Path('data/output/real_scan_tuning').glob('*.png')); print('image:', img); engine = build_pp_structure(use_gpu=False); blocks = parse_layout_to_blocks(engine, str(img)); tables = extract_tables_with_metadata(blocks); print('tables:', len(tables)); print(tables[0]['source_style'] if tables else 'no table'); print(tables[0]['df'].head() if tables else 'no table')"
```

## 判定等级

Pass 表示修改不违反禁止项，接口兼容，输出可复现，文字和表格线保护良好，DataFrame 流程完整，比对结果可追溯。Warning 表示存在轻微问题但不影响主流程，例如红章残留偏多、字迹略灰、个别边界区域有噪声或参数仍需继续调优。Fail 表示出现任一严重问题，例如 HSV mask 直接白化红章、黑色文字被抹掉、表格线被破坏、使用 LLM 猜测字段、原生 PDF 被无故转图片 OCR、进入 `align_compare.py` 前未 DataFrame 化、未经许可写入或覆盖文件、删除兼容接口导致 `ImportError`，或使用固定角度 deskew。

## 禁止项总结

项目严禁使用 HSV 掩码直接白化红章，严禁对红色掩码区域整块置白，严禁为了去章破坏黑色文字，严禁为了去章破坏表格线，严禁使用固定角度 deskew，严禁用 LLM 猜测表格内容，严禁用 LLM 补全缺失字段，严禁用 LLM 判断金额是否一致，严禁把所有逻辑塞入 `main.py`，严禁未经许可写入、覆盖或删除文件，严禁默认生成保存路径和文件名，严禁无故把原生 PDF 转图片 OCR，严禁把 OCR 原始文本直接送入 `align_compare.py`，严禁删除兼容接口导致工具脚本失效。
