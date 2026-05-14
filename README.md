# TamperShield

TamperShield 是一个 Document-first 的工程文档防篡改比对系统。

它比较的是：

```text
candidate document
        vs
baseline document
```

TamperShield 不是表格比对软件。表格只是文档中的一种元素，必须放在完整文档证据链中理解。

## Core Workflow

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
report_generator
```

`table_compare` 只是子能力，只在页面内表格需要精查时触发。主入口始终是完整文档比较。

## Current Status

当前状态：

```text
Document-first pipeline 已建立
main.py::run_document_first_pipeline(...) 已可运行
Markdown report export 已实现
Demo workflow 文档已完成
Demo checklist 文档已完成
```

当前真实 PDF vs DOCX 验证样例的稳定 baseline：

```text
candidate_page_count = 39
baseline_page_count = 44
difference_count = 69
page_reordered = 0
requires_table_compare_count = 0
```

该 baseline 来自当前真实 PDF vs DOCX 验证样例，不是所有文件的固定输出。

## Quick Links

- [Demo Workflow](DEMO_WORKFLOW.md)
- [Demo Checklist](DEMO_CHECKLIST.md)
- CLI runner: `tools/run_document_demo.py`
- [CLI Design](CLI_DESIGN.md)
- [Project Rules](PROJECT_RULES.md)
- [Agent Instructions](AGENTS.md)
- [TODO](TODO.md)

## Environment

```text
Conda environment: tamper_shield
LibreOffice: 26.2.3.2 或兼容版本
Recommended command style: conda run -n tamper_shield python ...
```

Windows 注意事项：

- 不要把 LibreOffice `program` 目录前置到 `PATH`。
- 如需使用 LibreOffice，追加到 `PATH` 后面，或显式调用 `soffice.exe`。
- 如果把 LibreOffice 路径前置，`python` 可能解析到 LibreOffice 自带的 `python-core`。

## Read-Only Demo Command

Preferred CLI command after Phase 13c:

```powershell
conda run -n tamper_shield python tools/run_document_demo.py --auto-discover --input-dir data/base_docs
```

This is the preferred demo command after Phase 13c. The long `python -c` command remains useful for debugging.

```powershell
conda run -n tamper_shield python -c "from pathlib import Path; from main import run_document_first_pipeline; pdf=list(Path('data/base_docs').glob('*.pdf'))[0]; docx=list(Path('data/base_docs').glob('*.docx'))[0]; idx=run_document_first_pipeline(candidate_file=pdf, baseline_file=docx); print(idx.summary()); print(idx.metadata)"
```

该命令不写文件。推荐使用 `Path.glob()` 自动发现输入文件，避免中文长路径直接穿过 `python -c`。

## Markdown Report Export

Only run this command when report writing is explicitly allowed.

```powershell
conda run -n tamper_shield python -c "from pathlib import Path; from main import run_document_first_pipeline; pdf=list(Path('data/base_docs').glob('*.pdf'))[0]; docx=list(Path('data/base_docs').glob('*.docx'))[0]; idx=run_document_first_pipeline(candidate_file=pdf, baseline_file=docx, report_output_path=r'data/output/demo_report.md', allow_write=True, overwrite=False); print(idx.summary())"
```

报告写出要求：

- 必须显式传入 `report_output_path`
- 必须显式传入 `allow_write=True`
- 默认使用 `overwrite=False`
- 不要覆盖已有报告

## View Markdown Report

```powershell
Get-Content data/output/demo_report.md -Encoding UTF8 -TotalCount 120
```

PowerShell 默认显示可能出现中文乱码，优先使用 `-Encoding UTF8`。

## Report Content

Markdown report 包含：

```text
Summary
Metadata
Evidence by Candidate Page
Evidence Without Candidate Page
Review context
Page profile
Full Metadata JSON
```

`Difference.severity` 是主证据等级。

`suggested_review_severity` 只是页面性质分类建议，用于辅助人工复核。

## Known Limitations

1. rendered PDF 路径下，DOCX native table 结构不会保留为 `table` element。
2. `requires_table_compare_count=0` 不代表原文档没有表格。
3. LibreOffice profile、字体、输入文件版本可能影响 DOCX 渲染分页。
4. 中文路径在 PowerShell / `conda run` stdout 中可能显示乱码。
5. 当前系统输出 evidence，不输出最终审计结论。

## Do Not

- 不要用 LLM 判断文档是否被篡改。
- 不要用 LLM 补全文档内容。
- 不要把表格比对作为主入口。
- 不要默认写报告。
- 不要自动覆盖报告。
- 不要把 LibreOffice 路径前置到 `PATH`。
- 不要把 `requires_table_compare_count=0` 理解为没有表格。

## Next Improvements

- rendered PDF 页面中识别 table-like blocks
- 保留 DOCX native table metadata 作为辅助结构
- 改进目录页 / 封面页 / 签章页分类规则
- 增加 CLI wrapper
- 增加 HTML / PDF 报告导出，但仍必须基于 `EvidenceIndex`
