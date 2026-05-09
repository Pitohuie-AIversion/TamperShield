from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

import pandas as pd
from paddleocr import PPStructure


class HTMLTableSpanParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cells: List[Dict[str, Any]] = []

        self._row_index = -1
<<<<<<< HEAD
        self._col_index = 0

=======
>>>>>>> 7fdf9eb1729e0c4e142a1778471f4a1ca6a55d1a
        self._inside_cell = False
        self._current_cell: Optional[Dict[str, Any]] = None
        self._current_text: List[str] = []
        self._occupied: Dict[int, set[int]] = {}

    def _is_occupied(self, row: int, col: int) -> bool:
        return col in self._occupied.get(row, set())

    def _mark_occupied(self, row: int, col: int) -> None:
        self._occupied.setdefault(row, set()).add(col)

    def _next_free_col(self, row: int) -> int:
        col = 0
        while self._is_occupied(row, col):
            col += 1
        return col

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
<<<<<<< HEAD
            self._col_index = 0
            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )
=======
>>>>>>> 7fdf9eb1729e0c4e142a1778471f4a1ca6a55d1a
            return

        if tag in {"td", "th"}:
            rowspan = int(attrs_dict.get("rowspan", "1") or "1")
            colspan = int(attrs_dict.get("colspan", "1") or "1")
            start_col = self._next_free_col(self._row_index)

            for row_offset in range(rowspan):
                for col_offset in range(colspan):
                    self._mark_occupied(
                        self._row_index + row_offset,
                        start_col + col_offset,
                    )

            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )

            self._inside_cell = True
            self._current_text = []

            self._current_cell = {
                "row": self._row_index,
                "col": start_col,
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

<<<<<<< HEAD
            self._col_index = self._current_cell["col"] + int(
                self._current_cell["colspan"]
            )
            self._col_index = self._next_available_col(
                self._row_index,
                self._col_index,
            )

=======
>>>>>>> 7fdf9eb1729e0c4e142a1778471f4a1ca6a55d1a
            self._inside_cell = False
            self._current_cell = None
            self._current_text = []

def build_pp_structure(lang: str = "ch", use_gpu: bool = False) -> PPStructure:
    return PPStructure(show_log=False, lang=lang, use_gpu=use_gpu)


def parse_layout_to_blocks(engine: PPStructure, image_path: str) -> List[Dict[str, Any]]:
    return engine(image_path)


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
