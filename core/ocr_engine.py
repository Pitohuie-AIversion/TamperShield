from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

import importlib
import pandas as pd


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

    Preferred:
    - PaddleOCR 3.x: PPStructureV3
    Fallback:
    - PaddleOCR 2.x: PPStructure
    """
    candidates = [
        ("paddleocr", "PPStructureV3"),
        ("paddleocr", "PPStructure"),
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
        "Cannot locate PPStructure / PPStructureV3 in the installed paddleocr package. "
        "Please check your PaddleOCR version. Run:\n"
        "python -c \"import paddleocr; print(paddleocr.__file__); print(dir(paddleocr))\"\n"
        "pip show paddleocr\n\n"
        "Tried:\n" + "\n".join(errors)
    )


def build_pp_structure(lang: str = "ch", use_gpu: bool = False):
    """
    Create PaddleOCR structure engine lazily.

    Supports:
    - PaddleOCR 3.x PPStructureV3
    - PaddleOCR 2.x PPStructure
    """
    pp_structure_cls = _load_pp_structure_class()

    init_candidates = [
        {"lang": lang, "use_gpu": use_gpu},
        {"lang": lang},
        {},
        {"show_log": False, "lang": lang, "use_gpu": use_gpu},
        {"show_log": False, "lang": lang},
    ]

    last_exc: Optional[Exception] = None
    for kwargs in init_candidates:
        try:
            return pp_structure_cls(**kwargs)
        except (TypeError, ValueError) as exc:
            last_exc = exc
            continue

    if last_exc is not None:
        raise last_exc

    raise RuntimeError("Failed to initialize PPStructure engine.")


def parse_layout_to_blocks(engine, image_path: str) -> List[Any]:
    """
    Run structure parser.

    Supports:
    - old callable PPStructure
    - newer PPStructureV3 with .predict()
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


def _safe_get(obj, key: str, default=None):
    """
    Safely get a field from dict-like or object-like PaddleOCR results.

    Supports:
    - dict
    - object attribute
    - object __getitem__
    """
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(key, default)

    if hasattr(obj, key):
        return getattr(obj, key)

    try:
        return obj[key]
    except Exception:
        return default


def _extract_html_from_table_item(table_item) -> str:
    """
    Extract HTML from one table result item.

    Supports:
    - PPStructureV3 table item with pred_html
    - object-like result with pred_html
    - old PPStructure dict style with res.html
    - possible fields: html, table_html, pred_html
    """
    html_candidates = [
        _safe_get(table_item, "pred_html", ""),
        _safe_get(table_item, "html", ""),
        _safe_get(table_item, "table_html", ""),
    ]

    res = _safe_get(table_item, "res", None)
    if res is not None:
        html_candidates.extend(
            [
                _safe_get(res, "html", ""),
                _safe_get(res, "pred_html", ""),
                _safe_get(res, "table_html", ""),
            ]
        )

    for html in html_candidates:
        if isinstance(html, str) and html.strip():
            return html

    return ""


def _iter_table_html_candidates(block) -> List[Dict[str, Any]]:
    """
    Convert different PaddleOCR output styles into unified table records.

    Output record format:
    {
        "html": str,
        "bbox": optional,
        "cell_box_list": optional,
        "table_ocr_pred": optional,
        "raw_table": original table object,
        "source_style": str,
    }
    """
    records: List[Dict[str, Any]] = []

    # Case 1: old PPStructure dict block:
    # {"type": "table", "res": {"html": "..."}}
    if isinstance(block, dict):
        block_type = block.get("type", "")
        res = block.get("res", {})

        if block_type == "table":
            html = _extract_html_from_table_item(block)
            if not html and isinstance(res, dict):
                html = _extract_html_from_table_item(res)

            if html:
                records.append(
                    {
                        "html": html,
                        "bbox": block.get("bbox", None),
                        "cell_box_list": _safe_get(block, "cell_box_list", None),
                        "table_ocr_pred": _safe_get(block, "table_ocr_pred", None),
                        "raw_table": block,
                        "source_style": "ppstructure_v2_dict",
                    }
                )

        # Case 1b: PaddleOCR 3.x result converted to dict.
        table_res_list = block.get("table_res_list", [])
        if table_res_list:
            for table_item in table_res_list:
                html = _extract_html_from_table_item(table_item)

                if html:
                    records.append(
                        {
                            "html": html,
                            "bbox": _safe_get(table_item, "bbox", None),
                            "cell_box_list": _safe_get(table_item, "cell_box_list", None),
                            "table_ocr_pred": _safe_get(table_item, "table_ocr_pred", None),
                            "raw_table": table_item,
                            "source_style": "ppstructure_v3_dict",
                        }
                    )

        return records

    # Case 2: PaddleOCR 3.x LayoutParsingResultV2 object.
    table_res_list = _safe_get(block, "table_res_list", [])
    if table_res_list:
        for table_item in table_res_list:
            html = _extract_html_from_table_item(table_item)

            if html:
                records.append(
                    {
                        "html": html,
                        "bbox": _safe_get(table_item, "bbox", None),
                        "cell_box_list": _safe_get(table_item, "cell_box_list", None),
                        "table_ocr_pred": _safe_get(table_item, "table_ocr_pred", None),
                        "raw_table": table_item,
                        "source_style": "ppstructure_v3_object",
                    }
                )

    # Case 3: direct object has html / pred_html.
    html = _extract_html_from_table_item(block)
    if html:
        records.append(
            {
                "html": html,
                "bbox": _safe_get(block, "bbox", None),
                "cell_box_list": _safe_get(block, "cell_box_list", None),
                "table_ocr_pred": _safe_get(block, "table_ocr_pred", None),
                "raw_table": block,
                "source_style": "direct_object_html",
            }
        )

    return records


def inspect_structure_output(blocks, max_items: int = 3) -> None:
    """
    Print compact diagnostics for PPStructure / PPStructureV3 outputs.
    """
    print("blocks type:", type(blocks))
    print("blocks len:", len(blocks))

    for i, block in enumerate(blocks[:max_items]):
        print("=" * 80)
        print(f"[{i}] block type:", type(block))

        if isinstance(block, dict):
            print("keys:", list(block.keys()))
            table_res_list = block.get("table_res_list", [])
        else:
            attrs = [x for x in dir(block) if not x.startswith("_")]
            print("attrs:", attrs[:80])
            table_res_list = getattr(block, "table_res_list", [])

        print("table_res_list type:", type(table_res_list))
        print(
            "table_res_list len:",
            len(table_res_list) if table_res_list is not None else 0,
        )

        if table_res_list:
            first_table = table_res_list[0]
            print("first table type:", type(first_table))

            if isinstance(first_table, dict):
                print("first table keys:", list(first_table.keys()))
                html = first_table.get("pred_html", "")
                print("has pred_html:", "pred_html" in first_table)
            else:
                table_attrs = [x for x in dir(first_table) if not x.startswith("_")]
                print("first table attrs:", table_attrs[:80])
                html = getattr(first_table, "pred_html", "")

            if isinstance(html, str):
                print("pred_html length:", len(html))
                print("pred_html preview:", html[:500])


def extract_tables_with_metadata(blocks: List[Any]) -> List[Dict[str, Any]]:
    """
    Extract table DataFrames and metadata from PaddleOCR structure outputs.

    Supports:
    - PaddleOCR 2.x PPStructure dict output
    - PaddleOCR 3.x PPStructureV3 LayoutParsingResultV2 output
    """
    tables: List[Dict[str, Any]] = []

    for block_index, block in enumerate(blocks):
        table_records = _iter_table_html_candidates(block)

        for record_index, record in enumerate(table_records):
            html_content = record.get("html", "")

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
                            "record_index": record_index,
                            "table_index": table_index,
                            "bbox": record.get("bbox", None),
                            "cell_box_list": record.get("cell_box_list", None),
                            "table_ocr_pred": record.get("table_ocr_pred", None),
                            "raw_block": block,
                            "raw_table": record.get("raw_table", None),
                            "source_style": record.get("source_style", ""),
                        }
                    )

            except Exception as exc:
                print(f"[Warning] Failed to parse structure table HTML: {exc}")

    return tables


def extract_tables_to_dataframes(blocks: List[Any]) -> List[pd.DataFrame]:
    tables = extract_tables_with_metadata(blocks)
    return [item["df"] for item in tables]