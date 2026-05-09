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

    print("开始真实扫描件阈值测试")
    print(f"{'文件名':<30} | {'初始角度':<10} | {'是否写出':<10}")
    print("-" * 60)

    for file in SCAN_DIR.iterdir():
        if file.suffix.lower() not in valid_exts:
            continue

        image = read_image_unicode(file)

        if image is None:
            print(f"无法读取图像数据: {file.name}")
            continue

        initial_angle = estimate_skew_angle(image, min_points=100)

        try:
            if write_enabled:
                out_path = output_dir / f"tuned_{file.name}"

                if out_path.exists() and not overwrite:
                    print(f"{file.name:<30} | {initial_angle:>8.3f}° | skipped")
                    continue

                preprocess_pipeline(
                    image_path=str(file),
                    output_path=str(out_path),
                    mode="gray",
                    enable_deskew=True,
                )
                wrote = True

            else:
                preprocess_pipeline(
                    image_path=str(file),
                    output_path=None,
                    mode="gray",
                    enable_deskew=True,
                )
                wrote = False

            print(f"{file.name:<30} | {initial_angle:>8.3f}° | {str(wrote):<10}")

        except Exception as exc:
            print(f"{file.name} 处理崩溃: {exc}")


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