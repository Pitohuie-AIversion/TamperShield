from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from core.pre_processing import estimate_skew_angle, preprocess_pipeline


OUTPUT_DIR = Path("data/output/preprocess_checks")


def _draw_demo_document(width: int = 1400, height: int = 1000) -> np.ndarray:
    image = np.full((height, width, 3), 255, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for row in range(12):
        y = 90 + row * 65
        cv2.putText(
            image,
            f"Project Item {row + 1:02d}  Qty 100  Price 200",
            (80, y),
            font,
            1.0,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
    # Add a red seal-like filled circle.
    cv2.circle(image, (1080, 220), 95, (0, 0, 255), -1)
    return image


def _rotate(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def _write_case(name: str, image: np.ndarray) -> Tuple[Path, Path]:
    raw_path = OUTPUT_DIR / f"{name}_raw.png"
    out_path = OUTPUT_DIR / f"{name}_processed.png"
    cv2.imwrite(str(raw_path), image)
    return raw_path, out_path


def run_validation() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cases = {
        "case_skew_plus3_red": _rotate(_draw_demo_document(), 3.0),
        "case_no_skew_red": _draw_demo_document(),
        "case_white_page": np.full((1000, 1400, 3), 255, dtype=np.uint8),
    }

    print("=== Preprocess Validation ===")
    for name, image in cases.items():
        raw_path, out_path = _write_case(name, image)
        estimated_before = estimate_skew_angle(image)
        triggered = abs(estimated_before) >= 0.2
        preprocess_pipeline(str(raw_path), str(out_path))
        after_image = cv2.imread(str(out_path))
        estimated_after = estimate_skew_angle(after_image) if after_image is not None else 0.0
        print(
            f"{name}: "
            f"angle_before={estimated_before:.3f}, "
            f"deskew_triggered={triggered}, "
            f"angle_after={estimated_after:.3f}, "
            f"output={out_path}"
        )

    print("Validation images and logs are generated under data/output/preprocess_checks")


if __name__ == "__main__":
    run_validation()

