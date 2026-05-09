import os
from typing import Optional, Literal, Tuple

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


def create_red_mask(
    image: np.ndarray,
    lower_sat: int = 45,
    lower_val: int = 45,
    red_threshold: int = 120,
    red_ratio: float = 1.15,
    kernel_size: int = 3,
    open_iterations: int = 1,
    dilate_iterations: int = 0,
) -> np.ndarray:
    """
    Detect red stamp pixels.

    Important:
    This mask is only used as an auxiliary mask.
    Do NOT directly set all masked pixels to white, otherwise black text covered
    by the stamp may be erased.
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    b, g, r = cv2.split(image)

    b_f = b.astype(np.float32)
    g_f = g.astype(np.float32)
    r_f = r.astype(np.float32)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red_1 = np.array([0, lower_sat, lower_val], dtype=np.uint8)
    upper_red_1 = np.array([12, 255, 255], dtype=np.uint8)

    lower_red_2 = np.array([168, lower_sat, lower_val], dtype=np.uint8)
    upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)

    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    hsv_red = (mask_1 > 0) | (mask_2 > 0)

    red_dominance = (
        (r > red_threshold)
        & (r_f > red_ratio * g_f)
        & (r_f > red_ratio * b_f)
    )

    mask = (hsv_red & red_dominance).astype(np.uint8) * 255

    if kernel_size > 1:
        k = make_odd(kernel_size)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

        if open_iterations > 0:
            mask = cv2.morphologyEx(
                mask,
                cv2.MORPH_OPEN,
                kernel,
                iterations=open_iterations,
            )

        if dilate_iterations > 0:
            mask = cv2.dilate(mask, kernel, iterations=dilate_iterations)

    return mask


def create_bright_red_mask(
    image: np.ndarray,
    lower_sat: int = 45,
    lower_val: int = 120,
    red_threshold: int = 150,
    red_ratio: float = 1.20,
) -> np.ndarray:
    """
    Detect only bright red stamp pixels.

    This is safer than a general red mask.
    Dark-red pixels may contain black text covered by the stamp,
    so they should not be removed aggressively.
    """
    return create_red_mask(
        image=image,
        lower_sat=lower_sat,
        lower_val=lower_val,
        red_threshold=red_threshold,
        red_ratio=red_ratio,
        kernel_size=3,
        open_iterations=1,
        dilate_iterations=0,
    )


def red_channel_document_gray(
    image: np.ndarray,
    lower_sat: int = 45,
    lower_val: int = 120,
    red_threshold: int = 150,
    clean_bright_red: bool = True,
) -> np.ndarray:
    """
    Convert document image to grayscale while suppressing red stamps.

    Core idea:
    - Use R channel as grayscale base.
    - Red stamp becomes naturally bright in R channel.
    - Black text remains dark in R channel.
    - Only very bright red stamp pixels are forced to white.

    This avoids the main problem of HSV white-out:
    black text under the red stamp is better preserved.
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    _, _, r = cv2.split(image)
    gray = r.copy()

    if clean_bright_red:
        bright_red_mask = create_bright_red_mask(
            image=image,
            lower_sat=lower_sat,
            lower_val=lower_val,
            red_threshold=red_threshold,
            red_ratio=1.20,
        )

        # Only clean bright red stamp pixels.
        # Do not clean all red pixels, otherwise text under seal may disappear.
        gray[bright_red_mask > 0] = 255

    return gray


def normalize_illumination(
    gray: np.ndarray,
    background_kernel_size: int = 35,
) -> np.ndarray:
    """
    Reduce uneven lighting and background shadow.
    """
    k = make_odd(background_kernel_size, min_value=15)

    background = cv2.GaussianBlur(gray, (k, k), 0)
    background = np.maximum(background, 1)

    normalized = cv2.divide(gray, background, scale=255)
    return normalized


def enhance_gray_document(
    gray: np.ndarray,
    clahe_clip_limit: float = 1.8,
    clahe_tile_grid_size: Tuple[int, int] = (8, 8),
    gamma: float = 0.90,
    sharpen: bool = False,
) -> np.ndarray:
    """
    Enhance grayscale document.

    Settings are conservative to avoid sticky text.
    """
    gray = normalize_illumination(gray, background_kernel_size=35)

    clahe = cv2.createCLAHE(
        clipLimit=clahe_clip_limit,
        tileGridSize=clahe_tile_grid_size,
    )
    enhanced = clahe.apply(gray)

    if gamma != 1.0:
        table = np.array(
            [((i / 255.0) ** gamma) * 255 for i in range(256)],
            dtype=np.uint8,
        )
        enhanced = cv2.LUT(enhanced, table)

    if sharpen:
        blur = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=1.0)
        enhanced = cv2.addWeighted(enhanced, 1.10, blur, -0.10, 0)

    return enhanced


def adaptive_binarize(
    gray: np.ndarray,
    block_size: int = 41,
    c_value: int = 18,
    thin_text: bool = True,
) -> np.ndarray:
    """
    Adaptive binarization.

    Larger c_value gives thinner black strokes.
    """
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
    """
    Rotate image without cropping.
    """
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


def binarize_for_skew(gray: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    _, binary_inv = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary_inv = cv2.morphologyEx(binary_inv, cv2.MORPH_OPEN, kernel, iterations=1)

    return binary_inv


def estimate_skew_angle(
    image: np.ndarray,
    min_points: int = 100,
) -> float:
    """
    Estimate correction angle using horizontal projection.

    The returned angle can be directly used for rotation.
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    small, _ = resize_for_estimation(image, max_side=1200)

    gray = red_channel_document_gray(
        small,
        lower_sat=45,
        lower_val=120,
        red_threshold=150,
        clean_bright_red=True,
    )

    binary_inv = binarize_for_skew(gray)

    foreground_count = int(np.count_nonzero(binary_inv))
    if foreground_count < min_points:
        return 0.0

    max_angle = 10.0
    angle_step = 0.25

    angles = np.arange(-max_angle, max_angle + angle_step * 0.5, angle_step)

    best_angle = 0.0
    best_score = -1.0

    for angle in angles:
        rotated = rotate_keep_size(
            binary_inv,
            angle,
            border_value=0,
            interpolation=cv2.INTER_NEAREST,
        )

        row_sum = np.sum(rotated > 0, axis=1).astype(np.float32)
        nonzero_rows = row_sum[row_sum > 0]

        if nonzero_rows.size < 5:
            continue

        score = float(np.var(nonzero_rows))

        if score > best_score:
            best_score = score
            best_angle = float(angle)

    if abs(best_angle) < 0.15:
        return 0.0

    return best_angle


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
    red_threshold: int = 150,
    gamma: float = 0.90,
    binary_block_size: int = 41,
    binary_c_value: int = 18,
    thin_text: bool = True,
    clean_bright_red: bool = True,
) -> np.ndarray:
    """
    Remove red seal using red-channel separation.

    mode:
    - gray: recommended for visual inspection and OCR
    - binary: stronger OCR-style output
    - color: red-removed grayscale image in BGR format
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty.")

    gray = red_channel_document_gray(
        image,
        lower_sat=lower_sat,
        lower_val=lower_val,
        red_threshold=red_threshold,
        clean_bright_red=clean_bright_red,
    )

    enhanced = enhance_gray_document(
        gray,
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
    red_threshold: int = 150,
    gamma: float = 0.90,
    binary_block_size: int = 41,
    binary_c_value: int = 18,
    thin_text: bool = True,
    clean_bright_red: bool = True,
    close_kernel_size: int = 2,
    close_iterations: int = 1,
    dilate_iterations: int = 0,
    **kwargs,
) -> np.ndarray:
    """
    Full preprocessing pipeline.

    close_kernel_size, close_iterations, and dilate_iterations are kept only for
    backward compatibility with old scripts.
    """
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
    red_threshold: int = 150,
) -> np.ndarray:
    """
    Backward-compatible entrypoint.

    This replaces the old HSV white-out method.
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


if __name__ == "__main__":
    input_path = r"input.jpg"

    preprocess_pipeline(
    image_path=r"your_input.jpg",
    output_path=r"your_output_gray.png",
    mode="gray",
    enable_deskew=True,
    red_threshold=135,
    lower_sat=35,
    lower_val=80,
    gamma=1.05,
    clean_bright_red=True,
)

    preprocess_pipeline(
        image_path=input_path,
        output_path=r"output_binary.png",
        mode="binary",
        enable_deskew=True,
        red_threshold=150,
        lower_sat=45,
        lower_val=120,
        gamma=0.90,
        binary_block_size=41,
        binary_c_value=18,
        thin_text=True,
        clean_bright_red=True,
    )