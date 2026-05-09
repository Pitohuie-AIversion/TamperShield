import os
import cv2
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from core.pre_processing import preprocess_pipeline, estimate_skew_angle

SCAN_DIR = Path("data/raw_scans")
OUTPUT_DIR = Path("data/output/real_scan_tuning")

def run_tuning():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    valid_exts = {'.jpg', '.jpeg', '.png'}
    
    print("🔍 开始真实扫描件阈值测试...")
    print(f"{'文件名':<30} | {'初始角度':<10} | {'是否校正':<10}")
    print("-" * 55)

    for file in SCAN_DIR.iterdir():
        if file.suffix.lower() in valid_exts:
            # 【关键修复】使用 numpy 替代 cv2.imread 读取中文路径图片
            data = np.fromfile(str(file), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img is None: 
                print(f"⚠️ 无法读取图像数据: {file.name}")
                continue
            
            # 使用现有逻辑预估角度
            initial_angle = estimate_skew_angle(img, min_points=100)
            
            # 执行完整的预处理流水线
            out_path = OUTPUT_DIR / f"tuned_{file.name}"
            try:
                preprocess_pipeline(str(file), str(out_path))
                triggered = abs(initial_angle) >= 0.2
                print(f"{file.name:<30} | {initial_angle:>8.3f}° | {str(triggered):<10}")
            except Exception as e:
                print(f"❌ {file.name} 处理崩溃: {e}")

if __name__ == "__main__":
    run_tuning()