"""Check the official PaddleOCR/PaddleX serving demo environment."""

from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path


def import_status(module_name: str) -> tuple[bool, str]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - diagnostic script
        return False, str(exc)

    version = getattr(module, "__version__", "unknown")
    return True, str(version)


def detect_paddle_gpu() -> str:
    try:
        import paddle
    except Exception as exc:  # pragma: no cover - diagnostic script
        return f"paddle import failed: {exc}"

    try:
        compiled_with_cuda = paddle.device.is_compiled_with_cuda()
        device_count = paddle.device.cuda.device_count() if compiled_with_cuda else 0
        return f"compiled_with_cuda={compiled_with_cuda}, gpu_count={device_count}"
    except Exception as exc:  # pragma: no cover - diagnostic script
        return f"gpu detection failed: {exc}"


def main() -> int:
    cwd = Path.cwd()
    samples_dir = cwd / "samples"
    results_dir = cwd / "results"

    print("Python:", sys.version.replace("\n", " "))
    print("Platform:", platform.platform())
    print("Current working directory:", cwd)

    for module_name in ["paddleocr", "paddlex", "paddle"]:
        ok, detail = import_status(module_name)
        status = "ok" if ok else "failed"
        print(f"{module_name}: {status} ({detail})")

    print("Paddle GPU:", detect_paddle_gpu())
    print("samples/ exists:", samples_dir.exists())
    print("results/ exists:", results_dir.exists())

    if not samples_dir.exists() or not results_dir.exists():
        print("Warning: run this script from official_paddleocr_serving/ or create samples/ and results/.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
