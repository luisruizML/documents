"""Build the two cluster diagrams of a Rosetta Business Object page.

The diagrams are generated from the page itself, so the tables in the picture
are the tables of the document. Output, next to the page:

    Diagrams_<Page>_Simplified.drawio / .png   simple version: name and definition of each object
    Diagrams_<Page>_Full.drawio / .png         full version: each object also shows its Fields table

Every object is as wide as its own content: the simple version from the name (250 minimum),
the full version from the Fields table (see column_widths).

Usage:
    python build_diagram.py <page.md> [--context lnk_a__b,lnk_c__d] [--no-export]

--context names objects defined on other pages that belong in the picture
(for example the Links of a Hub whose Links live on the specific pages).
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
import validate_page as vp  # noqa: E402

FIELD_COLUMNS = vp.FIELD_COLUMNS

# Data Vault object colors. text follows the brand contrast rule.
PALETTE = {
    "Hub": {"fill": "#3A0CA3", "text": "#FFFFFF"},
    "Link": {"fill": "#45E3CD", "text": "#000000"},
    "Satellite": {"fill": "#F72586", "text": "#FFFFFF"},
}
KIND_ALIAS = {"Non-historized Link": "Link"}
EDGE_COLOR = "#A6A8AB"


def _rgb(h: str) -> tuple[int, int, int]:
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def _hex(c: tuple[float, float, float]) -> str:
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


def _luminance(h: str) -> float:
    def lin(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_text(h: str) -> str:
    lum = _luminance(h)
    return "#000000" if (lum + 0.05) / 0.05 >= 1.05 / (lum + 0.05) else "#FFFFFF"


def _tint(fill: str, amount: float) -> str:
    """The fill moved toward white by `amount`."""
    r, g, b = _rgb(fill)
    return _hex((r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount))


# A Satellite updated in place is the exception to the history default: the same color, lighter.
PALETTE["Satellite (in place)"] = {"fill": _tint(PALETTE["Satellite"]["fill"], 0.65), "text": "#000000"}


def derive_line(fill: str) -> str:
    """A line color that contrasts with the fill: lighter on dark fills, darker on light fills."""
    r, g, b = _rgb(fill)
    if _luminance(fill) < 0.4:
        return _hex((r + (255 - r) * 0.55, g + (255 - g) * 0.55, b + (255 - b) * 0.55))
    return _hex((r * 0.6, g * 0.6, b * 0.6))


def palette_for(kind: str, in_place: bool = False) -> dict:
    if in_place and kind == "Satellite":
        return PALETTE["Satellite (in place)"]
    return PALETTE[KIND_ALIAS.get(kind, kind)]


# ---------------------------------------------------------------- model

@dataclass
class Node:
    name: str
    kind: str
    grain: str = ""
    rows: list[dict[str, str]] | None = None
    external: bool = False
    definition: str = ""

    @property
    def in_place(self) -> bool:
        return self.kind == "Satellite" and "replaced in place" in self.grain

    @property
    def note(self) -> str:
        """The text under the name on the Simplified and the Lucid diagram: the Definition (the grain when there is none)."""
        if self.external:
            return self.grain or "Defined on its own page"
        return self.definition or self.grain

    def paragraphs(self, full: bool) -> list[str]:
        """The Full version shows the Definition, then the grain; the other versions show `note` only."""
        if full and not self.external and self.definition and self.grain:
            return [self.definition, self.grain]
        return [self.note]


@dataclass
class Edge:
    child: str
    parent: str
    label: str = ""


@dataclass
class Model:
    title: str = ""
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def node(self, name: str) -> Node:
        return next(n for n in self.nodes if n.name == name)

    def has(self, name: str) -> bool:
        return any(n.name == name for n in self.nodes)


def _kind_from_name(name: str) -> str:
    return {"hub_": "Hub", "lnk_": "Link", "sat_": "Satellite"}[name[:4]]


def _clean(cell: str) -> str:
    return cell.replace(chr(96), "").strip()


def _link_hubs(name: str, business_key: str) -> list[tuple[str, str]]:
    """The Hubs a Link joins, with the role each plays when the Business key cell names one, as in
    `hub_natural_person` (subject), `hub_natural_person` (related). Without Hubs in the cell, the parts of the name."""
    found = []
    for piece in business_key.replace(chr(96), "").split(","):
        hub = re.search(r"hub_[a-z0-9_]+", piece)
        if hub:
            role = re.search(r"[(]([^)]+)[)]", piece)
            found.append((hub.group(0), role.group(1).strip() if role else ""))
    if found:
        repeated = len({h for h, _ in found}) < len(found)  # a role label is only needed to tell two edges apart
        return [(h, r if repeated else "") for h, r in found]
    return [("hub_" + part, "") for part in name[len("lnk_"):].split("__")]


def merge_family(text: str, folder: Path) -> str:
    """The text of a family page followed by the Vault objects and the Fields of the pages that define its objects,
    as one page, so that one picture can show them together. An ordinary page is returned as it is."""
    page = vp.parse_page(text)
    members = vp.family_members(page)
    if members is None:
        return text
    head: list[str] = []
    rows: list[str] = []
    fields: list[str] = []
    seen: set[str] = set()
    for member in dict.fromkeys(members):
        part = vp.parse_page((folder / f"{member}.md").read_text(encoding="utf-8"))
        table = [l for l in part.sections["Vault objects"] if l.lstrip().startswith("|")]
        head = head or table[:2]
        rows += [l for l in table[2:] if l not in seen and not seen.add(l)]
        body = part.sections["Fields"]
        fields += body[next(i for i, l in enumerate(body) if l.startswith("### ")):]
    return (f"# {page.title}\n\n## Vault objects\n\n" + "\n".join(head + rows)
            + "\n\n## Fields\n\n" + "\n".join(fields) + "\n")


def load_model(text: str, context: list[str] | tuple[str, ...] = ()) -> Model:
    page = vp.parse_page(text)
    model = Model(title=page.title)
    fields = vp._fields_tables(page)
    for row in page.tables("Vault objects")[0]:
        name = _clean(row["Name"])
        rows = [{k: _clean(v) for k, v in r.items()} for r in fields.get(name, [])]
        model.nodes.append(Node(name, row["Type"], _clean(row["Grain"]), rows, definition=_clean(row.get("Definition", ""))))
    for name in context:
        if not model.has(name):
            model.nodes.append(Node(name, _kind_from_name(name), external=True))
    business_keys = {_clean(r["Name"]): r.get("Business key", "") for r in page.tables("Vault objects")[0]}
    for n in list(model.nodes):
        if n.kind in ("Link", "Non-historized Link"):
            for hub, role in _link_hubs(n.name, business_keys.get(n.name, "")):
                if not model.has(hub):
                    model.nodes.append(Node(hub, "Hub", external=True))
                model.edges.append(Edge(n.name, hub, role))
    for n in model.nodes:
        if n.kind == "Satellite":
            parent, _, descriptor = n.name[len("sat_"):].rpartition("__")
            for prefix in ("hub_", "lnk_"):
                if model.has(prefix + parent):
                    model.edges.append(Edge(n.name, prefix + parent, descriptor))
                    break
    return model


# ---------------------------------------------------------------- layout

SIMPLE_MIN_W = 250      # the narrowest simple object
NAME_PAD = 10           # the name's width plus this is the object width when it is wider than the minimum
HEAD_INSET = 24         # 8 pt left spacing + the collapse arrow, both inside the header
DESC_W = 250            # Description column of the full table, word wrap on
CELL_PAD = 14           # 4 pt spacing each side of a cell + 6 pt slack, draw.io renders text slightly wider than Pillow measures it
FRAME_PAD = 16          # 8 pt margin each side of the table inside its object
HEAD_H = 28
GAP_X = 130             # the narrowest gap between two columns
LABEL_PAD = 10          # free line on each side of a connector label
EDGE_STEP = 12.0        # distance between two neighbouring vertical bands

# Pillow measures text with the fonts draw.io renders; without them the per-character widths below are used.
FONT_FILES = {"mono": "cour.ttf", "mono_bold": "courbd.ttf", "sans": "arial.ttf", "sans_bold": "arialbd.ttf", "sans_italic": "ariali.ttf"}
FALLBACK_EM = {"mono": 0.6, "mono_bold": 0.6, "sans": 0.52, "sans_bold": 0.56, "sans_italic": 0.52}
_FONT_DIRS = [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts", Path("/usr/share/fonts/truetype/msttcorefonts")]
_fonts: dict[tuple[str, int], object] = {}


def _font(kind: str, size: int):
    key = (kind, size)
    if key not in _fonts:
        font = None
        try:
            from PIL import ImageFont
            for d in _FONT_DIRS:
                if (d / FONT_FILES[kind]).is_file():
                    font = ImageFont.truetype(str(d / FONT_FILES[kind]), size)
                    break
        except ImportError:
            pass
        _fonts[key] = font
    return _fonts[key]


def measure(text: str, kind: str, size: int) -> float:
    """Width in points of the text on one line."""
    font = _font(kind, size)
    return font.getlength(text) if font else len(text) * size * FALLBACK_EM[kind]


def wrap(text: str, kind: str, size: int, width: float) -> list[str]:
    """Greedy word wrap; a word wider than the width stays whole on its own line."""
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and measure(trial, kind, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line or not lines else lines


SMALL = ("Role", "Null", "PII")


def _cell_font(name: str, header: bool) -> tuple[str, int]:
    if header:
        return "sans_bold", 10
    if name in ("Column", "Type"):
        return "mono", 10
    return "sans", 12 if name == "Role" else 10


def column_widths(rows: list[dict[str, str]]) -> list[int]:
    """Widths of the seven Fields columns: Description is fixed, Role, Null and PII share the smallest width that
    fits the widest of them, and Column, Type and Default fit their longest text."""
    def fit(name: str) -> int:
        texts = [(name, True)] + [(r.get(name, ""), False) for r in rows]
        return math.ceil(max(measure(t, *_cell_font(name, h)) for t, h in texts)) + CELL_PAD

    small = max(fit(n) for n in SMALL)
    return [DESC_W if n == "Description" else small if n in SMALL else fit(n) for n in FIELD_COLUMNS]


def _row_h(row: dict[str, str]) -> int:
    return 20 + 13 * (len(wrap(row.get("Description", ""), "sans", 10, DESC_W - CELL_PAD)) - 1)


def _note_h(n: Node, w: float, full: bool = False) -> int:
    paragraphs = n.paragraphs(full)
    lines = sum(len(wrap(p, "sans_italic", 11, w - 16)) for p in paragraphs)
    return 14 * lines + 14 * (len(paragraphs) - 1) + 6  # a blank line between two paragraphs


def _simple_w(n: Node) -> int:
    return max(SIMPLE_MIN_W, math.ceil(measure(n.name, "mono_bold", 12) + HEAD_INSET + NAME_PAD))


def _has_table(n: Node, full: bool) -> bool:
    return full and not n.external and bool(n.rows)


def _size(n: Node, full: bool, degree: int = 0) -> tuple[int, int]:
    w = _simple_w(n)
    if _has_table(n, full):
        w = max(w, sum(column_widths(n.rows)) + FRAME_PAD)
    h = HEAD_H + _note_h(n, w, full) + 8
    if _has_table(n, full):
        h += 4 + 20 + sum(_row_h(r) for r in n.rows) + 4
    return w, max(h, 20 * (degree + 1))  # room to spread the arrows that meet here


def label_w(label: str) -> float:
    """Width a connector label needs on its line: Courier New 11 plus slack for the white background."""
    return measure(label, "mono", 11) + 6 if label else 0.0


def gap_widths(model: "Model", col: dict[str, int]) -> dict[int, int]:
    """Width of the gap after each column: the label of every connector must fit on its first horizontal
    segment, with the vertical bands of the group beyond it."""
    need: dict[int, float] = {}
    groups: dict[tuple[int, bool], list[Edge]] = {}
    for e in model.edges:
        groups.setdefault((min(col[e.child], col[e.parent]), col[e.child] < col[e.parent]), []).append(e)
    for (lo, _), es in groups.items():
        z = max(label_w(e.label) for e in es) + 2 * LABEL_PAD
        need[lo] = need.get(lo, 0.0) + z + len(es) * EDGE_STEP + 10
    return {lo: max(GAP_X, math.ceil(n + 20)) for lo, n in need.items()}


def _columns(model: Model) -> dict[str, int]:
    col: dict[str, int] = {}
    for n in model.nodes:
        if n.kind == "Hub" and not n.external:
            col[n.name] = 1
    for n in model.nodes:
        if n.kind in ("Link", "Non-historized Link"):
            col[n.name] = 2
    for n in model.nodes:
        if n.kind == "Hub" and n.external:
            col[n.name] = 3
    for n in model.nodes:
        if n.kind == "Satellite":
            parent = next((e.parent for e in model.edges if e.child == n.name), None)
            col[n.name] = 3 if col.get(parent) == 2 else 0
        elif n.name not in col:
            col[n.name] = 0
    used = sorted(set(col.values()))
    return {k: used.index(v) for k, v in col.items()}


def place(model: Model, full: bool) -> dict[str, tuple[float, float, float, float]]:
    col = _columns(model)
    deg = {n.name: sum(1 for e in model.edges if n.name in (e.child, e.parent)) for n in model.nodes}
    size = lambda n: _size(n, full, deg[n.name])  # noqa: E731
    ncols = max(col.values()) + 1
    stacks: list[list[Node]] = [[] for _ in range(ncols)]
    for n in model.nodes:
        stacks[col[n.name]].append(n)
    order = {n.name: i for i, n in enumerate(model.nodes)}
    parent_of = {e.child: e.parent for e in model.edges}
    for stack in stacks:  # satellites follow the order of their parents, so arrows do not cross
        stack.sort(key=lambda n: order.get(parent_of.get(n.name, ""), order[n.name]) if n.kind == "Satellite" else 0)
    vgap = 40 if full else 30
    widths = [max(size(n)[0] for n in s) if s else 0 for s in stacks]
    heights = [sum(size(n)[1] for n in s) + vgap * (len(s) - 1) if s else 0 for s in stacks]
    total = max(heights)
    gaps = gap_widths(model, col)
    hub_col = next((c for c, s in enumerate(stacks) if any(n.kind == "Hub" and not n.external for n in s)), 0)
    boxes: dict[str, tuple[float, float, float, float]] = {}
    x = 30.0
    for c, stack in enumerate(stacks):
        y = 80 + (total - heights[c]) / 2
        for n in stack:
            w, h = size(n)
            # every object keeps its own width; the column lines its boxes up toward the Hubs
            dx = widths[c] - w if c < hub_col else (widths[c] - w) / 2 if c == hub_col else 0
            boxes[n.name] = (x + dx, y, w, h)
            y += h + vgap
        x += widths[c] + gaps.get(c, GAP_X)
    return boxes


# ---------------------------------------------------------------- drawio

class _Ids:
    def __init__(self) -> None:
        self.n = 1

    def next(self) -> str:
        self.n += 1
        return f"c{self.n}"


def _q(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def _vertex(ids: _Ids, parent: str, value: str, style: str, x: float, y: float, w: float, h: float) -> tuple[str, str]:
    cid = ids.next()
    xml = (
        f'<mxCell id="{cid}" value="{_q(value)}" style="{style}" vertex="1" parent="{parent}">'
        f'<mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" as="geometry"/></mxCell>'
    )
    return cid, xml


def _table(ids: _Ids, parent: str, rows: list[dict[str, str]], pal: dict, x: float, y: float) -> list[str]:
    col_w = column_widths(rows)
    table_w = sum(col_w)
    line = derive_line(pal["fill"])
    head_fill = pal["fill"] if pal is PALETTE["Satellite (in place)"] else line  # the lighter table stays light
    head_text = _contrast_text(head_fill)
    heights = [20] + [_row_h(r) for r in rows]
    out: list[str] = []
    tid, xml = _vertex(
        ids, parent, "",
        f"shape=table;startSize=0;container=1;collapsible=0;childLayout=tableLayout;fillColor=none;strokeColor={line};",
        x, y, table_w, sum(heights),
    )
    out.append(xml)
    cy = 0.0
    for r_i, h in enumerate([None] + rows):
        height = heights[r_i]
        rid, xml = _vertex(
            ids, tid, "",
            "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;"
            "collapsible=0;dropTarget=0;fillColor=none;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;",
            0, cy, table_w, height,
        )
        out.append(xml)
        cx = 0.0
        for c_i, name in enumerate(FIELD_COLUMNS):
            width = col_w[c_i]
            if h is None:
                value, fill, color, bold = name, head_fill, head_text, "fontStyle=1;"
                font = "Arial"
            else:
                value, fill, color, bold = r_status(rows[r_i - 1], name), "#FFFFFF", "#000000", ""
                font = "Courier New" if name in ("Column", "Type") else "Arial"
            align = "left" if name in ("Column", "Type", "Description") else "center"
            style = (
                f"shape=partialRectangle;html=1;whiteSpace={'wrap' if name == 'Description' else 'nowrap'};connectable=0;overflow=hidden;"
                f"fillColor={fill};strokeColor={line};top=1;left=1;bottom=1;right=1;"
                f"fontFamily={font};fontSize={12 if name == 'Role' and h is not None else 10};fontColor={color};{bold}align={align};spacingLeft=4;spacingRight=4;"
            )
            _, xml = _vertex(ids, rid, value, style, cx, 0, width, height)
            out.append(xml)
            cx += width
        cy += height
    return out


def r_status(row: dict[str, str], name: str) -> str:
    return row.get(name, "")


def to_drawio(model: Model, full: bool, title: str = "") -> str:
    ids = _Ids()
    boxes = place(model, full)
    cells: list[str] = []
    right = max(x + w for x, _, w, _ in boxes.values())
    bottom = max(y + h for _, y, _, h in boxes.values())

    _, xml = _vertex(
        ids, "1", title or model.title,
        "text;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;fontFamily=Mulish;fontStyle=1;fontSize=16;fontColor=#3A0CA3;",
        30, 14, right - 30, 30,
    )
    cells.append(xml)

    node_id: dict[str, str] = {}
    for n in model.nodes:
        x, y, w, h = boxes[n.name]
        pal = palette_for(n.kind, n.in_place)
        border = derive_line(pal["fill"]) if n.in_place else pal["fill"]
        dashed = "dashed=1;" if n.in_place else ""
        cid, xml = _vertex(
            ids, "1", n.name,
            f"swimlane;html=1;whiteSpace=wrap;rounded=1;arcSize=6;startSize={HEAD_H};collapsible=1;{dashed}"
            f"fillColor={pal['fill']};swimlaneFillColor=#FFFFFF;strokeColor={border};strokeWidth=2;"
            f"fontFamily=Courier New;fontSize=12;fontStyle=1;fontColor={pal['text']};align=left;spacingLeft=8;",
            x, y, w, h,
        )
        node_id[n.name] = cid
        cells.append(xml)
        note_h = _note_h(n, w, full)
        _, xml = _vertex(
            ids, cid, "<br><br>".join(escape(p) for p in n.paragraphs(full)),
            f"text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontFamily=Arial;fontSize=11;fontStyle=2;"
            "fontColor=#000000;spacingLeft=8;spacingRight=8;",
            0, HEAD_H + 2, w, note_h,
        )
        cells.append(xml)
        if full and not n.external and n.rows:
            cells.extend(_table(ids, cid, n.rows, pal, 8, HEAD_H + 2 + note_h + 4))

    cells.extend(_edges(model, boxes, node_id, ids))

    ly = bottom + 40
    lx = 30.0
    legend = [("Hub", "Hub"), ("Link", "Link"), ("Satellite", "Satellite")]
    if any(n.in_place for n in model.nodes):
        legend.append(("Satellite, in place (exception)", "Satellite (in place)"))
    for label, key in legend:
        pal = PALETTE[key]
        dashed = "dashed=1;" if key.endswith("(in place)") else ""
        _, xml = _vertex(
            ids, "1", "",
            f"rounded=1;arcSize=20;{dashed}fillColor={pal['fill']};strokeColor={derive_line(pal['fill'])};strokeWidth=2;",
            lx, ly, 22, 22,
        )
        cells.append(xml)
        width = 190 if len(label) > 12 else 110
        _, xml = _vertex(
            ids, "1", label,
            "text;html=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=11;fontColor=#000000;",
            lx + 28, ly, width, 22,
        )
        cells.append(xml)
        lx += 150

    body = "".join(cells)
    return (
        '<mxfile host="app.diagrams.net"><diagram id="d1" name="Page-1">'
        '<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
        'fold="1" page="0" pageScale="1" background="#FFFFFF" math="0" shadow="0"><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>' + body + "</root></mxGraphModel></diagram></mxfile>"
    )


def _edges(model: Model, boxes: dict, node_id: dict[str, str], ids: _Ids) -> list[str]:
    col = _columns(model)

    def centre(name: str) -> float:
        _, y, _, h = boxes[name]
        return y + h / 2

    # attachment points: per node side, spread by the vertical order of the far end
    side_edges: dict[tuple[str, str], list[Edge]] = {}
    for e in model.edges:
        left, right = (e.child, e.parent) if col[e.child] < col[e.parent] else (e.parent, e.child)
        side_edges.setdefault((left, "right"), []).append(e)
        side_edges.setdefault((right, "left"), []).append(e)
    attach: dict[tuple[int, str, str], float] = {}
    for (name, side), edges in side_edges.items():
        _, y, _, h = boxes[name]
        far = lambda e: centre(e.parent if e.child == name else e.child)  # noqa: E731
        for i, e in enumerate(sorted(edges, key=far)):
            attach[(id(e), name, side)] = y + (i + 1) * h / (len(edges) + 1)

    # Each group is the connectors that leave boxes on the same side of one gap. The label sits on the first
    # horizontal segment, just after the box; the vertical bands start beyond the longest label and are nested
    # (outermost = the connector farthest from the Hub), so no line crosses a label.
    groups: dict[tuple[int, bool], list[Edge]] = {}
    for e in model.edges:
        groups.setdefault((min(col[e.child], col[e.parent]), col[e.child] < col[e.parent]), []).append(e)
    wx: dict[int, float] = {}
    for (lo, child_left), es in groups.items():
        sign = 1 if child_left else -1
        side = "right" if child_left else "left"
        far_side = "left" if child_left else "right"
        edge_x = {id(e): boxes[e.child][0] + (boxes[e.child][2] if child_left else 0) for e in es}
        ref = max(edge_x.values()) if child_left else min(edge_x.values())
        z = max(label_w(e.label) for e in es) + 2 * LABEL_PAD
        y_near = {id(e): attach[(id(e), e.child, side)] for e in es}
        y_far = {id(e): attach[(id(e), e.parent, far_side)] for e in es}
        down = sorted([e for e in es if y_near[id(e)] < y_far[id(e)] - 0.5], key=lambda e: y_near[id(e)])
        up = sorted([e for e in es if y_near[id(e)] > y_far[id(e)] + 0.5], key=lambda e: -y_near[id(e)])
        for j, e in enumerate(down):
            wx[id(e)] = ref + sign * (z + (len(down) - 1 - j) * EDGE_STEP)
        base = z + (len(down) * EDGE_STEP + 10 if down else 0)
        for j, e in enumerate(up):
            wx[id(e)] = ref + sign * (base + (len(up) - 1 - j) * EDGE_STEP)

    out: list[str] = []
    for e in model.edges:
        left, right = (e.child, e.parent) if col[e.child] < col[e.parent] else (e.parent, e.child)
        y_left = attach[(id(e), left, "right")]
        y_right = attach[(id(e), right, "left")]

        def frac(name: str, y: float) -> float:
            _, by, _, bh = boxes[name]
            return round((y - by) / bh, 4)

        if e.child == left:
            exit_x, exit_y, entry_x, entry_y = 1, frac(left, y_left), 0, frac(right, y_right)
        else:
            exit_x, exit_y, entry_x, entry_y = 0, frac(right, y_right), 1, frac(left, y_left)
        points = ""
        bend = abs(y_left - y_right) > 0.5
        if bend:
            x = wx[id(e)]
            pts = [(x, y_left), (x, y_right)]
            if e.child != left:
                pts.reverse()
            points = '<Array as="points">' + "".join(f'<mxPoint x="{px:g}" y="{py:g}"/>' for px, py in pts) + "</Array>"
        # the label centre is LABEL_PAD + half its width along the path from the child, on the first segment
        cx, cw = boxes[e.child][0], boxes[e.child][2]
        px, pw = boxes[e.parent][0], boxes[e.parent][2]
        x_out = cx + cw if e.child == left else cx
        x_in = px if e.child == left else px + pw
        length = (abs(wx[id(e)] - x_out) + abs(y_left - y_right) + abs(x_in - wx[id(e)])) if bend else abs(x_in - x_out)
        along = LABEL_PAD + label_w(e.label) / 2
        label_x = round(max(-1.0, min(1.0, 2 * along / length - 1)), 4) if length else 0
        style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=1;jumpStyle=arc;jumpSize=8;html=1;"
            f"strokeColor={EDGE_COLOR};strokeWidth=2;endArrow=block;endFill=1;"
            f"exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;"
            "labelBackgroundColor=#FFFFFF;fontFamily=Courier New;fontSize=11;fontColor=#000000;"
        )
        eid = ids.next()
        out.append(
            f'<mxCell id="{eid}" value="{_q(e.label)}" style="{style}" edge="1" parent="1" '
            f'source="{node_id[e.child]}" target="{node_id[e.parent]}">'
            f'<mxGeometry x="{label_x:g}" relative="1" as="geometry">{points}</mxGeometry></mxCell>'
        )
    return out


# ---------------------------------------------------------------- export

def find_drawio() -> str | None:
    env = os.environ.get("DRAWIO_EXE")
    candidates = [env] if env else []
    candidates += [r"C:\Program Files\draw.io\draw.io.exe", shutil.which("draw.io") or ""]
    return next((c for c in candidates if c and Path(c).is_file()), None)


MAX_PNG_HEIGHT = 4500  # draw.io cuts off the bottom of a taller render
GEOMETRY_RE = re.compile(r'<mxGeometry x="[-0-9.]+" y="([-0-9.]+)" width="[-0-9.]+" height="([0-9.]+)"')


def fit_scale(xml: str, wanted: float, limit: int = MAX_PNG_HEIGHT) -> float:
    """The wanted export scale, lowered so the picture is not taller than the limit."""
    bottoms = [float(y) + float(h) for y, h in GEOMETRY_RE.findall(xml)]
    height = max(bottoms, default=0.0) + 20
    return min(wanted, round(limit / height, 2)) if height else wanted


def export_png(exe: str, source: Path, target: Path, scale: float) -> None:
    subprocess.run([exe, "-x", "-f", "png", "--scale", f"{scale:g}", "-b", "10", "-o", str(target), str(source)], check=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Build the simple and full diagrams of a Business Object page")
    ap.add_argument("page")
    ap.add_argument("--context", default="", help="comma-separated objects defined on other pages")
    ap.add_argument("--no-export", action="store_true", help="write the .drawio files only")
    args = ap.parse_args(argv)
    page = Path(args.page)
    context = [c.strip() for c in args.context.split(",") if c.strip()]
    model = load_model(merge_family(page.read_text(encoding="utf-8"), page.parent), context)
    for full, kind, scale in ((False, "Simplified", 3), (True, "Full", 2)):
        title = f"SILVER: {model.title} cluster (Data Vault 2.0)" + (", full" if full else "")
        drawio = page.parent / "drawio" / f"Diagrams_{page.stem}_{kind}.drawio"
        drawio.parent.mkdir(exist_ok=True)
        xml = to_drawio(model, full, title)
        drawio.write_text(xml, encoding="utf-8", newline="\n")
        print("wrote", drawio)
        if not args.no_export:
            exe = find_drawio()
            if not exe:
                print("draw.io Desktop not found; set DRAWIO_EXE or use --no-export", file=sys.stderr)
                return 1
            png = page.parent / "images" / f"{drawio.stem}.png"
            png.parent.mkdir(exist_ok=True)
            export_png(exe, drawio, png, fit_scale(xml, scale))
            print("wrote", png)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
