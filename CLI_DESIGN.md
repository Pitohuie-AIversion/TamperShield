# TamperShield CLI Design

## Design Goals

CLI 的目标是把当前 `README.md` / `DEMO_WORKFLOW.md` 中的长 `python -c` demo 命令封装成稳定、可复制、可审计的命令行入口。

CLI 不是新的核心 pipeline。

CLI 只是 `main.py::run_document_first_pipeline(...)` 的薄 wrapper。

## Non-Goals

- 不重写 `document_parser` / `page_aligner` / `content_compare` / `table_compare`
- 不绕过 `EvidenceIndex`
- 不直接调用 `report_generator` internals
- 不引入 LLM
- 不输出最终审计结论
- 不默认写文件
- 不默认覆盖报告
- 不替代 `README.md` / `DEMO_WORKFLOW.md` / `DEMO_CHECKLIST.md`

## Call Flow

```text
CLI arguments
        ↓
tools/run_document_demo.py
        ↓
main.py::run_document_first_pipeline(...)
        ↓
EvidenceIndex
        ↓
print summary / metadata
        ↓
optional Markdown report, only when explicitly allowed
```

CLI 不得直接调用 parser / aligner / content_compare / table_compare。

## Implementation Boundary

The future CLI must only import and call:

```text
main.py::run_document_first_pipeline(...)
```

It must not import or call:

```text
core.document_parser
core.page_aligner
core.content_compare
core.table_compare
core.report_generator internals
core.table_matcher
core.align_compare
core.ocr_engine
core.pre_processing
```

Allowed imports:

```text
argparse
pathlib.Path
sys
json, optional
main.run_document_first_pipeline
```

## Proposed Arguments

```text
--candidate PATH
--baseline PATH
--auto-discover
--input-dir data/base_docs
--report-output PATH
--allow-write
--overwrite
--show-metadata
--show-records N
--encoding utf-8
```

Argument meanings:

- `--candidate`: candidate document 路径
- `--baseline`: baseline document 路径
- `--auto-discover`: 自动从 `input-dir` 中查找一个 PDF 和一个 DOCX
- `--input-dir`: 输入目录，默认 `data/base_docs`
- `--report-output`: Markdown 报告输出路径
- `--allow-write`: 只有出现该参数才允许写报告
- `--overwrite`: 允许覆盖已有报告，默认 `False`
- `--show-metadata`: 打印 `EvidenceIndex.metadata`
- `--show-records N`: 打印前 N 条 evidence 摘要
- `--encoding`: 保留参数，默认 `utf-8`，主要用于未来报告查看或输出控制

## Argument Validation Rules

1. If `--auto-discover` is used, `--candidate` and `--baseline` should not be required.
2. If `--auto-discover` is not used, both `--candidate` and `--baseline` are required.
3. If `--candidate` is provided but `--baseline` is missing, fail with clear error.
4. If `--baseline` is provided but `--candidate` is missing, fail with clear error.
5. If `--report-output` is provided without `--allow-write`, block writing and print:

```text
[Output Blocked] - Permission Required
```

6. If `--allow-write` is provided without `--report-output`, fail with clear error.
7. If report path exists and `--overwrite` is not provided, print:

```text
[Output Blocked] - Output Exists
```

8. If `--overwrite` is provided without `--allow-write`, fail with clear error.
9. `--show-records` must be a non-negative integer.

## Default Behavior

- 默认只读。
- 默认不写报告。
- 默认不覆盖文件。
- 默认打印 `EvidenceIndex.summary()`。
- 默认不输出最终审计结论。

## Input Discovery

推荐使用 `--auto-discover` 配合 `--input-dir`。

默认从 `data/base_docs` 中查找：

- 第一个 `*.pdf` 作为 candidate
- 第一个 `*.docx` 作为 baseline

This avoids passing long Chinese paths directly through Windows PowerShell / `conda run` / `python -c`, where stdout display can become confusing.

If the directory contains multiple PDF or DOCX files, the safer behavior is:

- Do not guess automatically.
- Print candidate lists.
- Ask the user to pass `--candidate` and `--baseline` explicitly.

If a future demo mode intentionally uses sorted first files, it must print the selected files before running.

## Auto-Discover Rules

When `--auto-discover` is used:

- Search `--input-dir` for `*.pdf` files.
- Search `--input-dir` for `*.docx` files.
- If exactly one PDF and exactly one DOCX exist, use them.
- If zero PDF or zero DOCX exists, fail with clear error.
- If multiple PDF or multiple DOCX files exist, do not guess.
- Print candidate file list and ask user to pass `--candidate` / `--baseline` explicitly.

Do not silently choose the first file when multiple files exist.

This is safer than the early demo pattern that used `Path.glob()[0]`.

## Report Writing Rules

Only write a Markdown report when all conditions are true:

1. `--report-output` is provided.
2. `--allow-write` is provided.
3. The target file does not exist, or `--overwrite` is explicitly provided.

Failure messages:

```text
[Output Blocked] - Permission Required
[Output Blocked] - Output Exists
```

CLI 不得自动生成默认报告路径。

## Exit Code Design

Suggested exit codes:

```text
0 = success
1 = invalid arguments
2 = input file not found
3 = output blocked / permission issue
4 = pipeline runtime error
```

Exact exit codes can be adjusted during implementation, but the CLI should return non-zero for configuration or runtime errors.

## Output Design

Allowed output:

```text
EvidenceIndex.summary()
EvidenceIndex.metadata, optional
first N Evidence summaries, optional
report path when explicitly written
```

Forbidden output:

```text
tampered / not tampered
safe / unsafe
PASS / FAIL
篡改 / 未篡改
安全 / 不安全
```

## Console Output Format

Suggested console output:

```text
[TamperShield] Document-first demo runner
Candidate: <path>
Baseline: <path>
Mode: read-only / report-export
Summary:
  total: ...
  by_severity: ...
  by_diff_type: ...
Metadata:
  candidate_page_count: ...
  baseline_page_count: ...
  difference_count: ...
Report written: <path>
```

Do not print final audit judgment.

Do not print full evidence records by default.

Only print first N records if `--show-records N` is provided.

## Example Commands

只读自动发现：

```powershell
python tools/run_document_demo.py --auto-discover --input-dir data/base_docs
```

显式路径只读：

```powershell
python tools/run_document_demo.py --candidate "data/base_docs/sample.pdf" --baseline "data/base_docs/sample.docx"
```

写 Markdown 报告：

```powershell
python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --report-output data/output/demo_report.md --allow-write
```

允许覆盖：

```powershell
python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --report-output data/output/demo_report.md --allow-write --overwrite
```

These are future CLI design examples only. Do not run them until the CLI is implemented.

## Future Test Commands

Future CLI implementation test commands:

```powershell
python tools/run_document_demo.py --help

python tools/run_document_demo.py --auto-discover --input-dir data/base_docs

python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --show-metadata

python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --show-records 5

python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --report-output data/output/demo_report.md

python tools/run_document_demo.py --auto-discover --input-dir data/base_docs --report-output data/output/demo_report.md --allow-write
```

The command with `--report-output` but without `--allow-write` should be blocked.

The command with `--allow-write` may write only the specified report path.

## Error Handling

Expected configuration and runtime errors:

- missing candidate
- missing baseline
- multiple candidate files under auto-discover
- multiple baseline files under auto-discover
- report output path missing
- `--allow-write` missing
- output file already exists
- pipeline exception

错误信息应该清晰，但不应吞掉 traceback；demo 模式可打印简洁错误，debug 模式未来再考虑。

## Future Implementation Sketch

```text
parse args
resolve candidate/baseline
validate write permission
call run_document_first_pipeline(...)
print summary
optionally print metadata
optionally print first N records
exit with code 0 on success
exit with non-zero code on configuration or runtime error
```

This is pseudocode only, not a complete Python implementation.

## Future Acceptance Tests

- `python tools/run_document_demo.py --help` works.
- Read-only auto-discover run prints `EvidenceIndex` summary.
- Read-only run does not create files.
- `--report-output` without `--allow-write` is blocked.
- `--allow-write` with explicit report output writes exactly one Markdown file.
- Existing output file is not overwritten unless `--overwrite` is passed.
- Multiple PDF/DOCX inputs under auto-discover cause a clear error instead of silent selection.
- CLI does not import core parser / aligner / compare modules directly.
- CLI does not output final audit judgments.

## Acceptance Criteria

- CLI 默认只读
- CLI 只调用 `run_document_first_pipeline(...)`
- CLI 不直接调用 core parser / aligner / compare 模块
- CLI 不输出最终审计结论
- CLI 显式 `--allow-write` 后才写报告
- CLI 不覆盖已有文件，除非 `overwrite=True`
- CLI 支持 `Path.glob` 或 `--auto-discover` 来避免中文长路径问题
- CLI 不改变现有 core API
