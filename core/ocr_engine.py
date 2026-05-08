from typing import Any, Dict, List

from paddleocr import PPStructure


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

