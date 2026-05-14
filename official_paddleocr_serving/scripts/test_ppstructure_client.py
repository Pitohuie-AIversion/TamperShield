"""HTTP client for the official PaddleX PP-StructureV3 serving endpoint."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from urllib.parse import urljoin

import requests


def build_api_url(base_url: str, endpoint: str) -> str:
    if base_url.rstrip("/").endswith(endpoint.strip("/")):
        return base_url.rstrip("/")
    return urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))


def infer_file_type(path: Path) -> int:
    return 0 if path.suffix.lower() == ".pdf" else 1


def write_json(path: Path, data: object, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {path}. Pass --overwrite to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test official PaddleX PP-StructureV3 serving.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8081", help="Service base URL.")
    parser.add_argument("--endpoint", default="/layout-parsing", help="PP-StructureV3 REST endpoint.")
    parser.add_argument("--image", default="samples/test.jpg", help="Input image or PDF path.")
    parser.add_argument("--output", default="results/ppstructure_result.json", help="Output JSON path.")
    parser.add_argument("--timeout", type=float, default=300.0, help="HTTP timeout in seconds.")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.image)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    api_url = build_api_url(args.base_url, args.endpoint)
    file_data = base64.b64encode(input_path.read_bytes()).decode("ascii")
    payload = {"file": file_data, "fileType": infer_file_type(input_path)}

    response = requests.post(api_url, json=payload, timeout=args.timeout)
    response.raise_for_status()
    result = response.json()

    write_json(output_path, result, overwrite=args.overwrite)
    print(f"PP-StructureV3 response saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
