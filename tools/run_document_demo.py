"""Minimal CLI wrapper for the TamperShield Document-first demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import run_document_first_pipeline


EXIT_SUCCESS = 0
EXIT_INVALID_ARGUMENTS = 1
EXIT_INPUT_NOT_FOUND = 2
EXIT_OUTPUT_BLOCKED = 3
EXIT_PIPELINE_ERROR = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the TamperShield Document-first demo pipeline.",
    )
    parser.add_argument("--candidate", type=Path, help="Candidate document path.")
    parser.add_argument("--baseline", type=Path, help="Baseline document path.")
    parser.add_argument(
        "--auto-discover",
        action="store_true",
        help="Find one PDF and one DOCX under --input-dir.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/base_docs"),
        help="Input directory for --auto-discover. Default: data/base_docs.",
    )
    parser.add_argument("--report-output", type=Path, help="Markdown report output path.")
    parser.add_argument(
        "--allow-write",
        action="store_true",
        help="Allow writing the report specified by --report-output.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing report when --allow-write is set.",
    )
    parser.add_argument(
        "--show-metadata",
        action="store_true",
        help="Print EvidenceIndex metadata.",
    )
    parser.add_argument(
        "--show-records",
        type=int,
        default=0,
        metavar="N",
        help="Print the first N evidence summaries. Default: 0.",
    )
    parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="Enable OCR-backed parsing for image inputs.",
    )
    parser.add_argument(
        "--enable-preprocess",
        action="store_true",
        help="Pass preprocessing intent to OCR-backed image parsing.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Reserved output encoding option. Default: utf-8.",
    )
    return parser


def _print_file_list(label: str, files: list[Path]) -> None:
    print(f"{label}:")
    for path in files:
        print(f"  {path}")


def discover_inputs(input_dir: Path) -> tuple[Path, Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"input path is not a directory: {input_dir}")

    pdfs = sorted(input_dir.glob("*.pdf"))
    docxs = sorted(input_dir.glob("*.docx"))

    if len(pdfs) == 1 and len(docxs) == 1:
        return pdfs[0], docxs[0]

    if not pdfs:
        raise FileNotFoundError(f"no PDF file found under {input_dir}")
    if not docxs:
        raise FileNotFoundError(f"no DOCX file found under {input_dir}")

    if len(pdfs) > 1:
        _print_file_list("Multiple PDF candidates found", pdfs)
    if len(docxs) > 1:
        _print_file_list("Multiple DOCX baselines found", docxs)
    raise ValueError("multiple input candidates found; provide --candidate and --baseline explicitly")


def validate_args(args: argparse.Namespace) -> tuple[Path, Path, Path | None]:
    if args.show_records < 0:
        raise ValueError("--show-records must be non-negative")

    if args.report_output and not args.allow_write:
        print("[Output Blocked] - Permission Required")
        raise PermissionError("report output requires --allow-write")

    if args.allow_write and not args.report_output:
        raise ValueError("--allow-write requires --report-output")

    if args.overwrite and not args.allow_write:
        raise ValueError("--overwrite requires --allow-write")

    report_output: Path | None = args.report_output
    if report_output is not None and report_output.exists() and not args.overwrite:
        print("[Output Blocked] - Output Exists")
        raise PermissionError("report output already exists")

    if args.auto_discover:
        candidate, baseline = discover_inputs(args.input_dir)
    else:
        if args.candidate is None and args.baseline is None:
            raise ValueError("provide --auto-discover or both --candidate and --baseline")
        if args.candidate is None:
            raise ValueError("--baseline was provided but --candidate is missing")
        if args.baseline is None:
            raise ValueError("--candidate was provided but --baseline is missing")
        candidate, baseline = args.candidate, args.baseline

    if not candidate.exists():
        raise FileNotFoundError(f"candidate file not found: {candidate}")
    if not baseline.exists():
        raise FileNotFoundError(f"baseline file not found: {baseline}")

    return candidate, baseline, report_output


def print_summary(idx: Any) -> None:
    print("Summary:")
    summary = idx.summary() if hasattr(idx, "summary") else {}
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


def print_metadata(idx: Any) -> None:
    print("Metadata:")
    metadata = getattr(idx, "metadata", {})
    print(json.dumps(metadata, ensure_ascii=False, indent=2, default=str))


def _record_field(record: Any, name: str) -> Any:
    if hasattr(record, name):
        return getattr(record, name)
    if isinstance(record, dict):
        return record.get(name)
    return None


def print_records(idx: Any, limit: int) -> None:
    if limit <= 0:
        return
    records = list(getattr(idx, "records", []) or [])
    print(f"Evidence records (first {min(limit, len(records))} of {len(records)}):")
    for record in records[:limit]:
        difference = _record_field(record, "difference")
        diff_type = getattr(difference, "diff_type", None)
        severity = getattr(difference, "severity", None)
        if diff_type is None:
            diff_type = _record_field(record, "diff_type")
        if severity is None:
            severity = _record_field(record, "severity")
        item = {
            "evidence_id": _record_field(record, "evidence_id"),
            "diff_type": diff_type,
            "severity": severity,
            "candidate_page": _record_field(record, "candidate_page"),
            "baseline_page": _record_field(record, "baseline_page"),
            "message": _record_field(record, "message"),
        }
        print(json.dumps(item, ensure_ascii=False, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        candidate, baseline, report_output = validate_args(args)
    except PermissionError:
        return EXIT_OUTPUT_BLOCKED
    except (ValueError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_INVALID_ARGUMENTS
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_INPUT_NOT_FOUND

    mode = "report-export" if report_output is not None else "read-only"
    print("[TamperShield] Document-first demo runner")
    print(f"Candidate: {candidate}")
    print(f"Baseline: {baseline}")
    print(f"Mode: {mode}")

    try:
        idx = run_document_first_pipeline(
            candidate_file=candidate,
            baseline_file=baseline,
            enable_ocr=args.enable_ocr,
            enable_preprocess=args.enable_preprocess,
            report_output_path=report_output,
            allow_write=args.allow_write,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"Pipeline error: {exc}", file=sys.stderr)
        return EXIT_PIPELINE_ERROR

    print_summary(idx)
    if args.show_metadata:
        print_metadata(idx)
    print_records(idx, args.show_records)

    if report_output is not None:
        print(f"Report written: {report_output}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
