from pathlib import Path

from core.pre_processing import remove_red_seal


RAW_SCANS_DIR = Path("data/raw_scans")
OUTPUT_DIR = Path("data/output")


def run_preprocess_pipeline() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image_suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    for file_path in RAW_SCANS_DIR.glob("*"):
        if file_path.suffix.lower() not in image_suffixes:
            continue
        output_path = OUTPUT_DIR / f"{file_path.stem}_clean.png"
        remove_red_seal(str(file_path), str(output_path))
        print(f"[OK] cleaned: {file_path.name} -> {output_path.name}")


if __name__ == "__main__":
    run_preprocess_pipeline()

