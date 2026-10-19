"""Build the full model of Business Object pages as a Lucid Standard Import document.

Same model and layout idea as build_diagram.py (the page is the source), one
Lucid page per Business Object page. Write the JSON, then create the document
with the Lucid MCP tool lucid_create_diagram_from_specification
(use_assisted_layout false: the positions here are meaningful).

Usage:
    python build_lucid.py out.json <page.md>[@ctx1,ctx2] [<page.md>[@ctx...] ...]

The optional @ctx list names objects defined on other pages, like --context
of build_diagram.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_diagram as bd  # noqa: E402

# Table column widths in units: Column, Role, Type, Null, PII, Default, Description.
# Lucid flags the diamond, circle, square and delta symbols as emoji, so the Role column uses letters there.
LUCID_ROLE = {"◆": "HK", "◇": "FK", "●": "BK", "▪": "LD", "Δ": "HD"}
# The importer rejects a table whose grid (rows x columns) is larger than about 140 cells: 52 columns failed,
# 20 columns failed from 9 rows. 14 columns keeps a 10-row table at 140.
UNITS = [3, 1, 2, 1, 1, 1, 5]
U = 74
TABLE_W = sum(UNITS) * U
NODE_W = TABLE_W + 24
EXT_W = 360
HEAD_H = 32
GAP_X = 160
GAP_Y = 40
DESC_CHARS = int(UNITS[-1] * U / 7)


def _tint(h: str, amount: float = 0.6) -> str:
    r, g, b = bd._rgb(h)
    return bd._hex((r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount))


def _lines(text: str, width: float) -> int:
    return max(1, math.ceil(len(text) / max(10, (width - 24) / 7)))


def _row_h(rows: list[dict[str, str]]) -> int:
    longest = max([len(r.get("Description", "")) for r in rows] + [1])
    return 12 + 16 * max(1, math.ceil(longest / DESC_CHARS))


def _dims(n: bd.Node, degree: int, with_table: bool) -> tuple[float, float, float, float]:
    """width, height, note height, table height"""
    full = with_table and not n.external and bool(n.rows)
    w = NODE_W if full else EXT_W
    note_h = 20 * _lines(n.note, w) + 6
    table_h = _row_h(n.rows) * (len(n.rows) + math.ceil(len(n.rows) / (MAX_ROWS - 1))) if full else 0
    h = HEAD_H + note_h + 8 + (table_h + 16 if full else 8)
    return w, max(h, 26 * (degree + 1)), note_h, table_h


def _page(model: bd.Model, index: int, with_tables: bool, title: str, page_title: str) -> dict:
    sfx = f"-p{index}"  # ids are unique across the whole document
    col = bd._columns(model)
    degree = {n.name: sum(1 for e in model.edges if n.name in (e.child, e.parent)) for n in model.nodes}
    dims = {n.name: _dims(n, degree[n.name], with_tables) for n in model.nodes}
    ncols = max(col.values()) + 1
    stacks: list[list[bd.Node]] = [[] for _ in range(ncols)]
    for n in model.nodes:
        stacks[col[n.name]].append(n)
    heights = [sum(dims[n.name][1] for n in s) + GAP_Y * (len(s) - 1) if s else 0 for s in stacks]
    total = max(heights)
    boxes: dict[str, dict] = {}
    x = 40.0
    for c, stack in enumerate(stacks):
        y = 90 + (total - heights[c]) / 2
        for n in stack:
            w, h, _, _ = dims[n.name]
            boxes[n.name] = {"x": x, "y": y, "w": w, "h": h}
            y += h + GAP_Y
        x += (max(dims[n.name][0] for n in stack) if stack else 0) + GAP_X

    shapes: list[dict] = [{
        "id": f"title{sfx}", "type": "text",
        "boundingBox": {"x": 40, "y": 20, "w": max(600, x - GAP_X - 40), "h": 40},
        "text": f'<p style="text-align:center;font-family:Arial;font-size:24px;color:#3A0CA3"><b>{_esc(title)}</b></p>',
    }]
    for n in model.nodes:
        pal = bd.palette_for(n.kind)
        w, h, note_h, table_h = dims[n.name]
        b = boxes[n.name]
        shapes.append({
            "id": f"body_{n.name}{sfx}", "type": "rectangle", "boundingBox": dict(b),
            "style": {"fill": {"type": "color", "color": "#FFFFFF"}, "stroke": {"color": pal["fill"], "width": 3, "style": "solid"}},
        })
        shapes.append({
            "id": f"head_{n.name}{sfx}", "type": "rectangle",
            "boundingBox": {"x": b["x"], "y": b["y"], "w": w, "h": HEAD_H},
            "text": f'<p style="font-family:Cousine;font-size:16px;text-align:left">&nbsp;<b>{n.name}</b></p>',
            "style": {"fill": {"type": "color", "color": pal["fill"]}, "stroke": {"color": pal["fill"], "width": 1, "style": "solid"}, "textColor": pal["text"]},
        })
        shapes.append({
            "id": f"note_{n.name}{sfx}", "type": "text",
            "boundingBox": {"x": b["x"] + 8, "y": b["y"] + HEAD_H + 2, "w": w - 16, "h": note_h},
            "text": f'<p style="font-family:Arial;font-size:14px;text-align:left"><i>{_esc(n.note)}</i></p>',
        })
        if table_h:
            shapes.extend(_table(n, pal, b["x"] + 12, b["y"] + HEAD_H + note_h + 8, table_h, sfx))

    bottom = max(b["y"] + b["h"] for b in boxes.values())
    shapes.append({
        "id": f"legend{sfx}", "type": "text",
        "boundingBox": {"x": 40, "y": bottom + 40, "w": 1600, "h": 30},
        "text": '<p style="font-family:Arial;font-size:14px;text-align:left">Role: HK own hash key · FK hash key of another object · BK business key · LD load metadata · HD hashdiff. Default: — means no default.</p>',
    })
    return {"id": f"page{index}", "title": page_title, "shapes": shapes, "lines": _lines_for(model, col, boxes, sfx)}


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


MAX_ROWS = 7  # the importer rejects a table with more than about 50 cells (49 passed, 56 failed): 7 rows of 7


def _table(n: bd.Node, pal: dict, x: float, y: float, h: float, sfx: str) -> list[dict]:
    """The Fields table of an object as stacked Lucid tables of at most MAX_ROWS rows, each with the header row."""
    head_fill = _tint(pal["fill"], 0.6)
    starts = [sum(UNITS[:i]) for i in range(len(UNITS))]
    per_chunk = MAX_ROWS - 1
    out = []
    for c, first in enumerate(range(0, len(n.rows), per_chunk)):
        rows = n.rows[first:first + per_chunk]
        cells = []
        for ci, name in enumerate(bd.FIELD_COLUMNS):
            cells.append({"xPosition": starts[ci], "yPosition": 0, "text": name, "mergeCellsRight": UNITS[ci] - 1,
                          "style": {"fill": {"type": "color", "color": head_fill}}})
        for ri, row in enumerate(rows, start=1):
            for ci, name in enumerate(bd.FIELD_COLUMNS):
                cell = {"xPosition": starts[ci], "yPosition": ri, "mergeCellsRight": UNITS[ci] - 1}
                text = LUCID_ROLE.get(row.get(name), row.get(name)) if name == "Role" else row.get(name)
                cell["text"] = text or " "  # the importer rejects a cell without text
                cells.append(cell)
        height = _row_h(n.rows) * (len(rows) + 1)
        out.append({
            "id": f"table_{n.name}-c{c}{sfx}", "type": "table",
            "boundingBox": {"x": x, "y": y, "w": TABLE_W, "h": height},
            "rowCount": len(rows) + 1, "colCount": sum(UNITS), "cells": cells,
        })
        y += height
    return out


def _lines_for(model: bd.Model, col: dict[str, int], boxes: dict[str, dict], sfx: str) -> list[dict]:
    def centre(name: str) -> float:
        return boxes[name]["y"] + boxes[name]["h"] / 2

    sides: dict[tuple[str, str], list[bd.Edge]] = {}
    for e in model.edges:
        left, right = (e.child, e.parent) if col[e.child] < col[e.parent] else (e.parent, e.child)
        sides.setdefault((left, "right"), []).append(e)
        sides.setdefault((right, "left"), []).append(e)
    frac: dict[tuple[int, str], float] = {}
    for (name, side), edges in sides.items():
        far = lambda e: centre(e.parent if e.child == name else e.child)  # noqa: E731
        for i, e in enumerate(sorted(edges, key=far)):
            frac[(id(e), name)] = round((i + 1) / (len(edges) + 1), 4)

    out = []
    for i, e in enumerate(model.edges):
        child_left = col[e.child] < col[e.parent]
        line = {
            "id": f"line{i}{sfx}", "lineType": "elbow",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": f"body_{e.child}{sfx}",
                          "position": {"x": 1 if child_left else 0, "y": frac[(id(e), e.child)]}},
            "endpoint2": {"type": "shapeEndpoint", "style": "arrow", "shapeId": f"body_{e.parent}{sfx}",
                          "position": {"x": 0 if child_left else 1, "y": frac[(id(e), e.parent)]}},
            "stroke": {"color": bd.EDGE_COLOR, "width": 2, "style": "solid"},
        }
        if e.label:
            line["text"] = [{"text": e.label, "position": 0.3, "side": "top"}]
        out.append(line)
    return out


def build_document(models: list[bd.Model]) -> dict:
    """Per business object page: an overview page (objects and arrows, no tables), then one page for each
    vault object with its Fields table. One big page failed to import; small pages import."""
    pages = []
    for m in models:
        pages.append(_page(m, len(pages) + 1, False, f"SILVER: {m.title} cluster (Data Vault 2.0), overview", f"{m.title} (overview)"))
        for n in m.nodes:
            if n.rows and not n.external:
                single = bd.Model(m.title, [n], [])
                pages.append(_page(single, len(pages) + 1, True, f"{m.title}: {n.name}", n.name))
    return {"version": 1, "pages": pages}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print(__doc__)
        return 2
    out, specs = Path(args[0]), args[1:]
    models = []
    for spec in specs:
        path, _, ctx = spec.partition("@")
        models.append(bd.load_model(Path(path).read_text(encoding="utf-8"), [c for c in ctx.split(",") if c]))
    out.write_text(json.dumps(build_document(models), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
