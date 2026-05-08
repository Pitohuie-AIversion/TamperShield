from typing import Any, Dict, List

from paddleocr import PPStructure
import pandas as pd
from bs4 import BeautifulSoup


def build_pp_structure(lang: str = "ch", use_gpu: bool = False) -> PPStructure:
    """
    Create PP-Structure engine for layout and table parsing.
    """
    return PPStructure(show_log=False, lang=lang, use_gpu=use_gpu)


def parse_layout_to_blocks(engine: PPStructure, image_path: str) -> List[Dict[str, Any]]:
    """
    Parse scanned page into PP-Structure blocks.
    """
    return engine(image_path)


def extract_tables_to_dataframes(blocks: List[Dict[str, Any]]) -> List[pd.DataFrame]:
    """
    遍历 PP-Structure 的输出区块，提取类型为 'table' 的块，
    并将其 HTML 解析为 Pandas DataFrame。
    """
    dfs = []
    for block in blocks:
        if block.get('type') == 'table' and 'res' in block and 'html' in block['res']:
            html_content = block['res']['html']
            try:
                # 使用 pandas 直接解析 HTML 表格
                parsed_dfs = pd.read_html(html_content)
                if parsed_dfs:
                    # 获取第一张表（通常一个块只有一个 HTML 表）
                    df = parsed_dfs[0]
                    # 清理表头和空值，统一为字符串以便比对
                    df = df.fillna("").astype(str)
                    dfs.append(df)
            except Exception as e:
                print(f"[Warning] Failed to parse HTML table: {e}")
    return dfs