import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from core.pre_processing import estimate_skew_angle, preprocess_pipeline


SCAN_DIR = Path("data/raw_scans")


def read_image_unicode(image_path: Path):
    data = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return image


def run_tuning(
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> None:
    write_enabled = output_dir is not None

    if not SCAN_DIR.exists():
        print(f"Scan directory not found: {SCAN_DIR}")
        return

    if not SCAN_DIR.is_dir():
        print(f"Scan path is not a directory: {SCAN_DIR}")
        return

    if write_enabled:
        output_dir.mkdir(parents=True, exist_ok=True)

    valid_exts = {".jpg", ".jpeg", ".png"}

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Explicit output directory. If omitted, no files are written.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing files.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None

    run_tuning(
        output_dir=output_dir,
        overwrite=args.overwrite,
    )