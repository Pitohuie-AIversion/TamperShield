import os
from typing import Optional

import cv2
import numpy as np


def remove_red_seal(
    image_path: str,
    output_path: Optional[str] = None,
    lower_sat: int = 45,
    lower_val: int = 45,
    dilate_iterations: int = 1,
) -> np.ndarray:
    """
    Use OpenCV + HSV to remove red seal regions from a scan image.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red_1 = np.array([0, lower_sat, lower_val], dtype=np.uint8)
    upper_red_1 = np.array([10, 255, 255], dtype=np.uint8)
    lower_red_2 = np.array([170, lower_sat, lower_val], dtype=np.uint8)
    upper_red_2 = np.array([180, 255, 255], dtype=np.uint8)

    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    red_mask = cv2.bitwise_or(mask_1, mask_2)

    kernel = np.ones((3, 3), dtype=np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    if dilate_iterations > 0:
        red_mask = cv2.dilate(red_mask, kernel, iterations=dilate_iterations)

    result = image.copy()
    result[red_mask > 0] = (255, 255, 255)

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(output_path, result)

    return result

