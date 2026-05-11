from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

import pandas as pd
import importlib



class HTMLTableSpanParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cells: List[Dict[str, Any]] = []

        self._row_index = -1
        self._col_index = 0

        self._inside_cell = False
        self._current_cell: Optional[Dict[str, Any]] = None
        self._current_text: List[str] = []

        # Occupied positions caused by previous rowspan / colspan.
        self._occupied: set[tuple[int, int]] = set()

    def _next_available_col(self, row: int, start_col: int) -> int:
        col = start_col
        while (row, col) in self._occupied:
            col += 1
        return col

    def _mark_occupied(
        self,
        row: int,
        col: int,
        rowspan: int,
        colspan: int,
    ) -> None:
        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                self._occupied.add((r, c))

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = dict(attrs)

        if tag == "tr":
            self._row_index += 1
            self._col_index = 0
            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )
            return

        if tag in {"td", "th"}:
            rowspan = int(attrs_dict.get("rowspan", "1") or "1")
            colspan = int(attrs_dict.get("colspan", "1") or "1")

            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )

            self._inside_cell = True
            self._current_text = []

            self._current_cell = {
                "row": self._row_index,
                "col": self._col_index,
                "rowspan": rowspan,
                "colspan": colspan,
                "tag": tag,
                "text": "",
            }

            self._mark_occupied(
                row=self._row_index,
                col=self._col_index,
                rowspan=rowspan,
                colspan=colspan,
            )

    def handle_data(self, data: str) -> None:
        if self._inside_cell:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None:
            text = " ".join(" ".join(self._current_text).split())
            self._current_cell["text"] = text
            self.cells.append(self._current_cell)

            self._col_index = self._current_cell["col"] + int(
                self._current_cell["colspan"]
            )
            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )

            self._inside_cell = False
            self._current_cell = None
            self._current_text = []


def _load_pp_structure_class():
    """
    Load PP-Structure class from different PaddleOCR versions.

    PaddleOCR 2.x commonly exposes:
        from paddleocr import PPStructure

    Some environments may not expose PPStructure at top level.
    This function avoids failing when importing core.ocr_engine.
    """
    candidates = [
        ("paddleocr", "PPStructure"),
        ("paddleocr", "PPStructureV3"),
        ("paddleocr.ppstructure", "PPStructure"),
        ("paddleocr.ppstructure.predict_system", "PPStructure"),
    ]

    errors = []

    for module_name, class_name in candidates:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls
        except Exception as exc:
            errors.append(f"{module_name}.{class_name}: {exc}")

    raise ImportError(
        "Cannot locate PPStructure in the installed paddleocr package. "
        "Please check your PaddleOCR version. Run:\n"
        "python -c \"import paddleocr; print(paddleocr.__file__); print(dir(paddleocr))\"\n"
        "pip show paddleocr\n\n"
        "Tried:\n" + "\n".join(errors)
    )


def build_pp_structure(lang: str = "ch", use_gpu: bool = False):
    """
    Create PP-Structure engine lazily.

    This keeps `from core.ocr_engine import HTMLTableSpanParser, build_pp_structure`
    importable even when PaddleOCR API differs across versions.
    """
    pp_structure_cls = _load_pp_structure_class()

    init_candidates = [
        {"show_log": False, "lang": lang, "use_gpu": use_gpu},
        {"show_log": False, "lang": lang},
        {"lang": lang, "use_gpu": use_gpu},
        {"lang": lang},
        {},
    ]

    last_exc: Exception | None = None
    for kwargs in init_candidates:
        try:
            return pp_structure_cls(**kwargs)
        except (TypeError, ValueError) as exc:
            last_exc = exc
            continue

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Failed to initialize PPStructure engine.")


def parse_layout_to_blocks(engine, image_path: str) -> List[Dict[str, Any]]:
    """
    Run structure parser.

    Supports both old callable PPStructure and newer PPStructureV3-style engines.
    """
    if callable(engine):
        result = engine(image_path)
    elif hasattr(engine, "predict"):
        result = engine.predict(image_path)
    else:
        raise TypeError(
            "Unsupported PaddleOCR structure engine. "
            "Expected callable engine or engine with .predict()."
        )

    if result is None:
        return []

    return list(result)


def inspect_structure_output(blocks, max_items: int = 3):
    print("blocks type:", type(blocks))
    print("blocks len:", len(blocks))
    for i, block in enumerate(blocks[:max_items]):
        print(f"[{i}] type:", type(block))
        if isinstance(block, dict):
            print("keys:", block.keys())
            print(block)
        else:
            print("attrs:", [x for x in dir(block) if not x.startswith("_")][:50])
            print(block)


def parse_html_table_spans(html_content: str) -> List[Dict[str, Any]]:
    parser = HTMLTableSpanParser()
    parser.feed(html_content)
    return parser.cells


def html_to_dataframes(html_content: str) -> List[pd.DataFrame]:
    try:
        parsed_dfs = pd.read_html(html_content)
    except ImportError as exc:
        raise ImportError(
            "pd.read_html requires an HTML parser dependency such as lxml. "
            "Please install lxml or add it to requirements.txt after confirmation."
        ) from exc

    result: List[pd.DataFrame] = []
    for df in parsed_dfs:
        df = df.fillna("").astype(str)
        df.columns = [str(col).strip() for col in df.columns]
        result.append(df)

    return result


def extract_tables_with_metadata(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tables: List[Dict[str, Any]] = []

    for block_index, block in enumerate(blocks):
        if block.get("type") != "table":
            continue

        res = block.get("res", {})
        html_content = res.get("html", "")

        if not html_content:
            continue

        try:
            dataframes = html_to_dataframes(html_content)
            spans = parse_html_table_spans(html_content)

            for table_index, df in enumerate(dataframes):
                tables.append(
                    {
                        "df": df,
                        "html": html_content,
                        "spans": spans,
                        "block_index": block_index,
                        "table_index": table_index,
                        "bbox": block.get("bbox", None),
                        "raw_block": block,
                    }
                )

        except Exception as exc:
            print(f"[Warning] Failed to parse PP-Structure HTML table: {exc}")

    return tables


def extract_tables_to_dataframes(blocks: List[Dict[str, Any]]) -> List[pd.DataFrame]:
    tables = extract_tables_with_metadata(blocks)
    return [item["df"] for item in tables]
