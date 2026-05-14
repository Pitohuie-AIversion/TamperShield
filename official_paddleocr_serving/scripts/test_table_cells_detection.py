"""Local official PaddleOCR Table Cells Detection smoke test."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test PaddleOCR TableCellsDetection locally.")
    parser.add_argument("--image", default="samples/table.jpg", help="Input table image path.")
    parser.add_argument("--output-dir", default="results", help="Output directory for JSON and visualization.")
    parser.add_argument("--model-name", default="RT-DETR-L_wired_table_cell_det", help="Official table cell detection model name.")
    parser.add_argument("--threshold", type=float, default=0.3, help="Detection threshold.")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing result files.")
    return parser.parse_args()


def ensure_can_write(target: Path, overwrite: bool) -> None:
    if target.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {target}. Pass --overwrite to replace it.")


def normalize_result_json(value: Any) -> Any:
    if callable(value):
        value = value()
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return value
    return {"raw": str(value)}


def main() -> int:
    args = parse_args()
    image_path = Path(args.image)
    output_dir = Path(args.output_dir)
    json_path = output_dir / "table_cells.json"
    visual_dir = output_dir / "table_cells_visual"

    if not image_path.exists():
        raise FileNotFoundError(f"Input table image not found: {image_path}")

    ensure_can_write(json_path, args.overwrite)
    if visual_dir.exists() and any(visual_dir.iterdir()) and not args.overwrite:
        raise FileExistsError(f"Visualization directory is not empty: {visual_dir}. Pass --overwrite to replace it.")

    output_dir.mkdir(parents=True, exist_ok=True)
    if visual_dir.exists() and args.overwrite:
        shutil.rmtree(visual_dir)
    visual_dir.mkdir(parents=True, exist_ok=True)

    try:
        from paddleocr import TableCellsDetection
    except Exception as exc:
        raise ImportError(
            "Cannot import TableCellsDetection from paddleocr. "
            "Install the official environment first: pip install -r requirements_official.txt"
        ) from exc

    model = TableCellsDetection(model_name=args.model_name)
    results = model.predict(str(image_path), threshold=args.threshold, batch_size=1)

    payload = {
        "image": str(image_path),
        "model_name": args.model_name,
        "threshold": args.threshold,
        "results": [],
    }

    for index, res in enumerate(results):
        if hasattr(res, "save_to_img"):
            res.save_to_img(str(visual_dir))

        if hasattr(res, "json"):
            payload["results"].append(normalize_result_json(getattr(res, "json")))
        else:
            payload["results"].append({"index": index, "raw": str(res)})

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Table cells JSON saved to: {json_path}")
    print(f"Visualization saved under: {visual_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
