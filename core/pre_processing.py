import os
import math
from typing import Literal, Optional, Tuple

import cv2
import numpy as np


OutputMode = Literal["gray", "binary", "color"]


def imread_unicode(image_path: str) -> np.ndarray:
    data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    return image


def imwrite_unicode(output_path: str, image: np.ndarray) -> None:
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()
    if not ext:
        ext = ".png"

    ok, encoded = cv2.imencode(ext, image)
    if not ok:
        raise ValueError(f"Cannot encode image with extension: {ext}")

    encoded.tofile(output_path)


def make_odd(value: int, min_value: int = 3) -> int:
    value = max(int(value), min_value)
    if value % 2 == 0:
        value += 1
    return value


def resize_for_estimation(
    image: np.ndarray,
    max_side: int = 1200,
) -> Tuple[np.ndarray, float]:
    h, w = image.shape[:2]
    long_side = max(h, w)

    if long_side <= max_side:
        return image.copy(), 1.0

    scale = max_side / long_side
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    return resized, scale


def extract_r_channel_gray(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    _, _, r = cv2.split(image)
    return r.copy()


def extract_black_text_mask(
    gray: np.ndarray,
    min_area: int = 2,
    max_area_ratio: float = 0.08,
    open_kernel_size: int = 1,
    close_kernel_size: int = 2,
) -> np.ndarray:
    """
    Extract black stroke protection mask from R-channel grayscale image.

    Foreground logic:
    - black text is dark in R channel
    - after inversion, black text becomes bright
    """
    if gray is None or gray.size == 0:
        raise ValueError("Input gray image is empty.")

    inv = 255 - gray

    blur = cv2.GaussianBlur(inv, (3, 3), 0)
    _, mask = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    if open_kernel_size > 1:
        k = make_odd(open_kernel_size)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    if close_kernel_size > 1:
        k = make_odd(close_kernel_size)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    h, w = gray.shape[:2]
    max_area = int(h * w * max_area_ratio)

    cleaned = np.zeros_like(mask)
    for label_id in range(1, num_labels):
        area = int(stats[label_id, cv2.CC_STAT_AREA])
        if min_area <= area <= max_area:
            cleaned[labels == label_id] = 255

    return cleaned


def suppress_red_stamp_rgb(
    image: np.ndarray,
    red_threshold: int = 135,
    red_delta: int = 25,
    lift_alpha: float = 0.45,
    protect_black: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Suppress red stamp using RGB/R-channel logic only.

    No HSV mask is used.

    Strategy:
    - use R channel as document gray
    - detect red-dominant non-black pixels by RGB relation
    - gently lift red-dominant non-black pixels
    - restore black_text_mask after suppression
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    b, g, r = cv2.split(image)

    gray = r.copy()
    protected_gray = gray.copy()

    black_text_mask = extract_black_text_mask(gray)

    b_i = b.astype(np.int16)
    g_i = g.astype(np.int16)
    r_i = r.astype(np.int16)

    max_gb = np.maximum(g_i, b_i)
    red_dominance = (r_i - max_gb) >= red_delta
    red_bright_enough = r_i >= red_threshold

    not_black_text = black_text_mask == 0

    red_candidate = red_dominance & red_bright_enough & not_black_text

    processed = gray.astype(np.float32)

    lifted = processed * (1.0 - lift_alpha) + 255.0 * lift_alpha
    processed[red_candidate] = np.maximum(processed[red_candidate], lifted[red_candidate])

    processed = np.clip(processed, 0, 255).astype(np.uint8)

    if protect_black:
        processed[black_text_mask > 0] = protected_gray[black_text_mask > 0]

    return processed, black_text_mask


def normalize_illumination(
    gray: np.ndarray,
    background_kernel_size: int = 35,
) -> np.ndarray:
    k = make_odd(background_kernel_size, min_value=15)

    background = cv2.GaussianBlur(gray, (k, k), 0)
    background = np.maximum(background, 1)

    normalized = cv2.divide(gray, background, scale=255)
    return normalized


def enhance_gray_document(
    gray: np.ndarray,
    black_text_mask: Optional[np.ndarray] = None,
    clahe_clip_limit: float = 1.8,
    clahe_tile_grid_size: Tuple[int, int] = (8, 8),
    gamma: float = 0.95,
    sharpen: bool = False,
) -> np.ndarray:
    protected_gray = gray.copy()

    enhanced = normalize_illumination(gray, background_kernel_size=35)

    clahe = cv2.createCLAHE(
        clipLimit=clahe_clip_limit,
        tileGridSize=clahe_tile_grid_size,
    )
    enhanced = clahe.apply(enhanced)

    if gamma != 1.0:
        table = np.array(
            [((i / 255.0) ** gamma) * 255 for i in range(256)],
            dtype=np.uint8,
        )
        enhanced = cv2.LUT(enhanced, table)

    if sharpen:
        blur = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=1.0)
        enhanced = cv2.addWeighted(enhanced, 1.10, blur, -0.10, 0)

    if black_text_mask is not None:
        enhanced[black_text_mask > 0] = protected_gray[black_text_mask > 0]

    return enhanced


def adaptive_binarize(
    gray: np.ndarray,
    block_size: int = 41,
    c_value: int = 18,
    thin_text: bool = True,
) -> np.ndarray:
    block_size = make_odd(block_size, min_value=15)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_value,
    )

    if thin_text:
        inv = 255 - binary
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        inv = cv2.morphologyEx(inv, cv2.MORPH_OPEN, kernel, iterations=1)
        binary = 255 - inv

    return binary


def binarize_for_skew(gray: np.ndarray) -> np.ndarray:
    black_text_mask = extract_black_text_mask(gray)
    return black_text_mask


def estimate_skew_angle_hough(
    image: np.ndarray,
    min_points: int = 100,
    max_angle: float = 15.0,
) -> Optional[float]:
    small, _ = resize_for_estimation(image, max_side=1200)
    gray = extract_r_channel_gray(small)

    binary = binarize_for_skew(gray)

    if int(np.count_nonzero(binary)) < min_points:
        return None

    edges = cv2.Canny(binary, 50, 150, apertureSize=3)

    _, w = edges.shape[:2]
    min_line_length = max(40, int(w * 0.18))

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=min_line_length,
        maxLineGap=20,
    )

    if lines is None:
        return None

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            continue

        angle = math.degrees(math.atan2(dy, dx))

        if -max_angle <= angle <= max_angle:
            angles.append(angle)

    if not angles:
        return None

    median_angle = float(np.median(angles))

    if abs(median_angle) < 0.15:
        return 0.0

    return median_angle


def estimate_skew_angle_min_area_rect(
    image: np.ndarray,
    min_points: int = 100,
    max_angle: float = 15.0,
) -> Optional[float]:
    small, _ = resize_for_estimation(image, max_side=1200)
    gray = extract_r_channel_gray(small)

    binary = binarize_for_skew(gray)
    ys, xs = np.where(binary > 0)

    if len(xs) < min_points:
        return None

    points = np.column_stack((xs, ys)).astype(np.float32)
    rect = cv2.minAreaRect(points)

    raw_angle = float(rect[-1])

    if raw_angle < -45:
        correction_angle = -(90 + raw_angle)
    else:
        correction_angle = -raw_angle

    if abs(correction_angle) > max_angle:
        return None

    if abs(correction_angle) < 0.15:
        return 0.0

    return float(correction_angle)


def estimate_skew_angle(
    image: np.ndarray,
    min_points: int = 100,
) -> float:
    """
    Estimate correction angle.

    Priority:
    1. HoughLinesP
    2. cv2.minAreaRect fallback
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    hough_angle = estimate_skew_angle_hough(
        image,
        min_points=min_points,
        max_angle=15.0,
    )

    if hough_angle is not None:
        return hough_angle

    rect_angle = estimate_skew_angle_min_area_rect(
        image,
        min_points=min_points,
        max_angle=15.0,
    )

    if rect_angle is not None:
        return rect_angle

    return 0.0


def rotate_keep_size(
    image: np.ndarray,
    angle: float,
    border_value,
    interpolation=cv2.INTER_LINEAR,
) -> np.ndarray:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )

    return rotated


def rotate_bound(
    image: np.ndarray,
    angle: float,
    border_value,
    interpolation=cv2.INTER_LINEAR,
) -> np.ndarray:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos_value = abs(matrix[0, 0])
    sin_value = abs(matrix[0, 1])

    new_w = int((h * sin_value) + (w * cos_value))
    new_h = int((h * cos_value) + (w * sin_value))

    matrix[0, 2] += (new_w / 2.0) - center[0]
    matrix[1, 2] += (new_h / 2.0) - center[1]

    rotated = cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )

    return rotated


def deskew_image(
    image: np.ndarray,
    expand: bool = True,
) -> Tuple[np.ndarray, float]:
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    h, w = image.shape[:2]
    if h < 2 or w < 2:
        return image.copy(), 0.0

    angle = estimate_skew_angle(image)

    if abs(angle) < 0.15:
        return image.copy(), 0.0

    if expand:
        rotated = rotate_bound(
            image,
            angle,
            border_value=(255, 255, 255),
            interpolation=cv2.INTER_CUBIC,
        )
    else:
        rotated = rotate_keep_size(
            image,
            angle,
            border_value=(255, 255, 255),
            interpolation=cv2.INTER_CUBIC,
        )

    return rotated, angle


def remove_red_seal_from_array(
    image: np.ndarray,
    mode: OutputMode = "gray",
    lower_sat: int = 45,
    lower_val: int = 120,
    red_threshold: int = 135,
    gamma: float = 0.95,
    binary_block_size: int = 41,
    binary_c_value: int = 18,
    thin_text: bool = True,
    clean_bright_red: bool = True,
    red_delta: int = 25,
    lift_alpha: float = 0.45,
) -> np.ndarray:
    """
    Red seal suppression based on RGB/R-channel separation.

    lower_sat and lower_val are kept only for backward compatibility.
    No HSV operation is used.
    """
    _ = lower_sat
    _ = lower_val

    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    gray, black_text_mask = suppress_red_stamp_rgb(
        image,
        red_threshold=red_threshold,
        red_delta=red_delta,
        lift_alpha=lift_alpha,
        protect_black=clean_bright_red,
    )

    enhanced = enhance_gray_document(
        gray,
        black_text_mask=black_text_mask,
        clahe_clip_limit=1.8,
        clahe_tile_grid_size=(8, 8),
        gamma=gamma,
        sharpen=False,
    )

    if mode == "gray":
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    if mode == "binary":
        binary = adaptive_binarize(
            enhanced,
            block_size=binary_block_size,
            c_value=binary_c_value,
            thin_text=thin_text,
        )

        # Keep binary output strictly binary while protecting black strokes.
        binary[black_text_mask > 0] = 0

        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    if mode == "color":
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    raise ValueError(f"Unsupported mode: {mode}")


def preprocess_pipeline(
    image_path: str,
    output_path: Optional[str] = None,
    mode: OutputMode = "gray",
    enable_deskew: bool = True,
    expand_after_rotation: bool = True,
    lower_sat: int = 45,
    lower_val: int = 120,
    red_threshold: int = 135,
    gamma: float = 0.95,
    binary_block_size: int = 41,
    binary_c_value: int = 18,
    thin_text: bool = True,
    clean_bright_red: bool = True,
    close_kernel_size: int = 2,
    close_iterations: int = 1,
    dilate_iterations: int = 0,
    red_delta: int = 25,
    lift_alpha: float = 0.45,
    **kwargs,
) -> np.ndarray:
    """
    Full preprocessing pipeline.

    Compatibility parameters:
    - lower_sat
    - lower_val
    - close_kernel_size
    - close_iterations
    - dilate_iterations

    These are kept to avoid breaking existing tools.
    """
    _ = close_kernel_size
    _ = close_iterations
    _ = dilate_iterations
    _ = kwargs

    image = imread_unicode(image_path)

    if enable_deskew:
        image, angle = deskew_image(
            image,
            expand=expand_after_rotation,
        )
        print(f"Deskew correction angle: {angle:.3f} degrees")

    result = remove_red_seal_from_array(
        image,
        mode=mode,
        lower_sat=lower_sat,
        lower_val=lower_val,
        red_threshold=red_threshold,
        gamma=gamma,
        binary_block_size=binary_block_size,
        binary_c_value=binary_c_value,
        thin_text=thin_text,
        clean_bright_red=clean_bright_red,
        red_delta=red_delta,
        lift_alpha=lift_alpha,
    )

    if output_path:
        imwrite_unicode(output_path, result)

    return result


def remove_red_seal(
    image_path: str,
    output_path: Optional[str] = None,
    lower_sat: int = 45,
    lower_val: int = 120,
    dilate_iterations: int = 0,
    mode: OutputMode = "gray",
    red_threshold: int = 135,
) -> np.ndarray:
    """
    Backward-compatible entrypoint.

    Internally uses RGB/R-channel red seal suppression.
    No HSV white-out is used.
    """
    return preprocess_pipeline(
        image_path=image_path,
        output_path=output_path,
        mode=mode,
        lower_sat=lower_sat,
        lower_val=lower_val,
        red_threshold=red_threshold,
        dilate_iterations=dilate_iterations,
    )