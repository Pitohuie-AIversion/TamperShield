import os
from pathlib import Path
import pandas as pd

from core.pre_processing import remove_red_seal
from core.ocr_engine import build_pp_structure, parse_layout_to_blocks, extract_tables_to_dataframes
from core.text_parser import extract_tables_from_native_pdf
from core.align_compare import compare_cells_with_tolerance

# 目录配置
DATA_DIR = Path("data")
RAW_SCANS_DIR = DATA_DIR / "raw_scans"       # 存放扫描版总文件图片
BASE_DOCS_DIR = DATA_DIR / "base_docs"       # 存放原生电子版子文件 (PDF)
OUTPUT_DIR = DATA_DIR / "output"             # 存放结果

def run_tamper_shield_pipeline(scan_image_name: str, base_pdf_name: str, key_columns: list):
    """
    执行端到端的防篡改比对流水线
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    scan_path = RAW_SCANS_DIR / scan_image_name
    base_path = BASE_DOCS_DIR / base_pdf_name
    clean_scan_path = OUTPUT_DIR / f"cleaned_{scan_image_name}"
    report_path = OUTPUT_DIR / f"audit_report_{scan_image_name}.csv"

    print(f"🚀 [Step 1] 开始预处理，剥离红色印章: {scan_path.name}...")
    remove_red_seal(str(scan_path), str(clean_scan_path))

    print(f"🧠 [Step 2] 启动 PP-Structure 引擎提取扫描件表格...")
    engine = build_pp_structure(use_gpu=False)
    blocks = parse_layout_to_blocks(engine, str(clean_scan_path))
    scan_dfs = extract_tables_to_dataframes(blocks)
    
    if not scan_dfs:
        print("❌ 未能在扫描件中检测到表格！")
        return
    scan_df = scan_dfs[0] # 简化测试，假设单页单表

    print(f"📄 [Step 3] 解析原生电子基准文件: {base_path.name}...")
    base_dfs = extract_tables_from_native_pdf(str(base_path))
    if not base_dfs:
        print("❌ 未能在基准文件中检测到表格！")
        return
    base_df = base_dfs[0]

    print(f"⚖️ [Step 4] 执行 Pandas 锚点对齐与 Levenshtein 容错比对...")
    # 这里会自动调用 ffill 展开合并单元格，并进行容错比对
    diff_report = compare_cells_with_tolerance(
        left_df=base_df, 
        right_df=scan_df, 
        key_columns=key_columns, 
        max_distance=2 # 允许 2 个字符的 OCR 误差
    )

    print(f"📊 [Step 5] 导出审计报告...")
    if diff_report.empty:
        print("✅ 比对通过：未发现明显篡改或超出容错的差异！")
    else:
        print(f"🔴 警报：发现 {len(diff_report)} 处潜在篡改！")
        diff_report.to_csv(report_path, index=False, encoding='utf-8-sig')
        print(f"详细报告已导出至: {report_path}")

if __name__ == "__main__":
    # 【测试入口】
    # 假设你放了一张带印章的扫描截图在 data/raw_scans/test_scan.jpg
    # 假设你放了对应的原始PDF在 data/base_docs/test_base.pdf
    # 假设它们表格的锚点主键列名叫做 "项目编号"
    
    # run_tamper_shield_pipeline("test_scan.jpg", "test_base.pdf", key_columns=["项目编号"])
    print("工程代码整合完毕。请取消注释上方的函数调用并填入实际文件名进行测试。")