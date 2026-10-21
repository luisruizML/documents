"""Column widths and cell paragraphs of the tables of a Business Object page, for Confluence.

Three tables have a layout of their own (the others keep Confluence's default):

  Header         Field is as narrow as its widest text and Value takes the rest; the table keeps the default width.
  Vault objects  Type and Name fit their texts on one line. Definition and Business key have the same width, and
                 Grain is the wildcard: table width - Definition - Business key - Type - Name.
  Fields         Every Fields table of the page shares the same widths. Column and Type fit their texts on one line,
                 Role, Null, PII and Default share one narrow width, and Description takes the rest.

Vault objects and Fields cover the whole width of a page that is set to the wide appearance (PAGE_WIDTH). Widths are
measured with Pillow in Arial and Courier New, then scaled, because the fonts of Confluence are wider.
"""
from __future__ import annotations

import math
import re

PAGE_WIDTH = 1800       # width of a table on a page in the wide appearance, in px (a screenshot of such a table was 1800 px wide)
HEADER_WIDTH = 760      # width of the Header table (default layout), in px
FONT_SCALE = 1.15       # Confluence's text is wider than Arial; "Owner domain" wrapped at 1.0 and at 1.12
MONO_CHAR = 8.2         # width of one character of code in Confluence, in px, read from a screenshot
CODE_PADDING = 8        # the box around a code span adds 4 px on each side
CELL_PADDING = 20       # 8 px of padding on each side of a cell, the border and a little slack
SANS_PX = 14

HEADER = ["Field", "Value"]
VAULT = ["Type", "Name", "Definition", "Grain", "Business key"]
FIELDS = ["Column", "Role", "Type", "Null", "PII", "Default", "Description"]
SHARED = ("Role", "Null", "PII", "Default")  # the four Fields columns that share one width
PARAGRAPH_COLUMNS = ("Definition", "Description")


def plain(cell: str) -> str:
    return re.sub(r"[*`]", "", cell)


def text_width(cell: str, bold: bool = False) -> float:
    import build_diagram as bd
    if "`" in cell:
        return len(plain(cell)) * MONO_CHAR + CODE_PADDING * cell.count("`") / 2
    return bd.measure(plain(cell), "sans_bold" if bold else "sans", SANS_PX) * FONT_SCALE


def fit(head: str, cells: list[str]) -> int:
    """Width in px of a column whose texts must stay on one line."""
    widest = max([text_width(head, bold=True)] + [text_width(c) for c in cells])
    return math.ceil(widest) + CELL_PADDING


def kind(head: list[str]) -> str | None:
    names = [plain(h).strip() for h in head]
    return {tuple(HEADER): "header", tuple(VAULT): "vault", tuple(FIELDS): "fields"}.get(tuple(names))


def split_tables(markdown: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every Markdown table of the page as (header cells, body rows)."""
    out, rows = [], []
    for line in markdown.split("\n") + [""]:
        line = line.rstrip("\r")
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip()[1:-1].split("|")])
        elif rows:
            out.append((rows[0], rows[2:]))
            rows = []
    return out


def header_widths(body: list[list[str]]) -> list[int]:
    field = fit("Field", [r[0] for r in body])
    return [field, HEADER_WIDTH - field]


def vault_widths(body: list[list[str]], total: int = PAGE_WIDTH) -> list[int]:
    type_w = fit("Type", [r[0] for r in body])
    name_w = fit("Name", [r[1] for r in body])
    definition = math.ceil((total - type_w - name_w) / 3)  # Definition = Business key, as wide as Grain at most; rounding goes to Definition
    business = definition
    grain = total - type_w - name_w - definition - business
    return [type_w, name_w, definition, grain, business]


def fields_widths(bodies: list[list[list[str]]], total: int = PAGE_WIDTH) -> list[int]:
    """One set of widths for every Fields table of the page."""
    rows = [r for body in bodies for r in body]
    col = {name: [r[i] for r in rows] for i, name in enumerate(FIELDS)}
    shared = max(fit(name, col[name]) for name in SHARED)
    column_w, type_w = fit("Column", col["Column"]), fit("Type", col["Type"])
    description = total - column_w - type_w - 4 * shared
    return [column_w, shared, type_w, shared, shared, shared, description]


def document_widths(markdown: str) -> dict[str, list[int]]:
    """The widths of the three tables for this page. The Fields widths come from every Fields table of the page."""
    tables = split_tables(markdown)
    out: dict[str, list[int]] = {}
    fields = [body for head, body in tables if kind(head) == "fields"]
    if fields:
        out["fields"] = fields_widths(fields)
    for head, body in tables:
        k = kind(head)
        if k == "vault" and "vault" not in out:
            out["vault"] = vault_widths(body)
        if k == "header" and "header" not in out:
            out["header"] = header_widths([head] + body)
    return out


def paragraphs(text: str) -> list[str]:
    """A long cell is split into paragraphs: one for each sentence, and the `e.g.` list of examples on its own."""
    spans: list[str] = []

    def keep(match):
        spans.append(match.group(0))
        return f"\x00{len(spans) - 1}\x00"

    masked = re.sub(r"`[^`]+`", keep, text)
    parts = re.split(r"(?<!e\.g\.)(?<=\.)\s+(?=[A-Z])|\s+(?=e\.g\.\s)", masked)
    return [re.sub("\x00(\\d+)\x00", lambda m: spans[int(m.group(1))], p).strip() for p in parts if p.strip()]


def colgroup(widths: list[int]) -> str:
    return "<colgroup>" + "".join(f'<col style="width: {w}px;"/>' for w in widths) + "</colgroup>"
