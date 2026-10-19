"""Build the two cluster diagrams of a Rosetta Business Object page.

The diagrams are generated from the page itself, so the tables in the picture
are the tables of the document. Output, next to the page:

    <Page>.drawio / .png         simple version: name and grain of each object
    <Page>_Full.drawio / .png    full version: each object also shows its Fields table

Usage:
    python build_diagram.py <page.md> [--context lnk_a__b,lnk_c__d] [--no-export]

--context names objects defined on other pages that belong in the picture
(for example the Links of a Hub whose Links live on the specific pages).
"""
from __future__ import annotations

import math
import os
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
    "Reference table": {"fill": "#A6A8AB", "text": "#000000"},
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


def derive_line(fill: str) -> str:
    """A line color that contrasts with the fill: lighter on dark fills, darker on light fills."""
    r, g, b = _rgb(fill)
    if _luminance(fill) < 0.4:
        return _hex((r + (255 - r) * 0.55, g + (255 - g) * 0.55, b + (255 - b) * 0.55))
    return _hex((r * 0.6, g * 0.6, b * 0.6))


def palette_for(kind: str) -> dict:
    return PALETTE[KIND_ALIAS.get(kind, kind)]


# ---------------------------------------------------------------- model

@dataclass
class Node:
    name: str
    kind: str
    grain: str = ""
    rows: list[dict[str, str]] | None = None
    external: bool = False

    @property
    def note(self) -> str:
        return self.grain if not self.external else (self.grain or "Defined on its own page")


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
    return {"hub_": "Hub", "lnk_": "Link", "sat_": "Satellite", "ref_": "Reference table"}[name[:4]]


def _clean(cell: str) -> str:
    return vp._strip(cell)


def load_model(text: str, context: list[str] | tuple[str, ...] = ()) -> Model:
    page = vp.parse_page(text)
    model = Model(title=page.title)
    fields = vp._fields_tables(page)
    for row in page.tables("Vault objects")[0]:
        name = _clean(row["Name"])
        rows = [{k: _clean(v) for k, v in r.items()} for r in fields.get(name, [])]
        model.nodes.append(Node(name, row["Type"], _clean(row["Grain"]), rows))
    for name in context:
        if not model.has(name):
            model.nodes.append(Node(name, _kind_from_name(name), external=True))
    for n in list(model.nodes):
        if n.kind in ("Link", "Non-historized Link"):
            for part in n.name[len("lnk_"):].split("__"):
                hub = "hub_" + part
                if not model.has(hub):
                    model.nodes.append(Node(hub, "Hub", external=True))
                model.edges.append(Edge(n.name, hub))
    for n in model.nodes:
        if n.kind == "Satellite":
            parent, _, descriptor = n.name[len("sat_"):].rpartition("__")
            for prefix in ("hub_", "lnk_"):
                if model.has(prefix + parent):
                    model.edges.append(Edge(n.name, prefix + parent, descriptor))
                    break
    return model


# ---------------------------------------------------------------- layout

SIMPLE_W = 340
COL_WIDTHS = [190, 44, 96, 44, 44, 60, 320]
TABLE_W = sum(COL_WIDTHS)
FULL_W = TABLE_W + 16
HEAD_H = 28
GAP_X = 130


def _lines(text: str, width: int, char_px: float = 5.6) -> int:
    per_line = max(10, int((width - 16) / char_px))
    return max(1, math.ceil(len(text) / per_line))


def _row_h(row: dict[str, str]) -> int:
    return 20 + 13 * (_lines(row.get("Description", ""), COL_WIDTHS[-1], 5.2) - 1)


def _size(n: Node, full: bool, degree: int = 0) -> tuple[int, int]:
    w = FULL_W if (full and not n.external) else SIMPLE_W
    note_h = 14 * _lines(n.note, w) + 6
    h = HEAD_H + note_h + 8
    if full and not n.external and n.rows:
        h += 4 + 20 + sum(_row_h(r) for r in n.rows) + 4
    return w, max(h, 20 * (degree + 1))  # room to spread the arrows that meet here


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
    vgap = 40 if full else 30
    widths = [max(size(n)[0] for n in s) if s else 0 for s in stacks]
    heights = [sum(size(n)[1] for n in s) + vgap * (len(s) - 1) if s else 0 for s in stacks]
    total = max(heights)
    boxes: dict[str, tuple[float, float, float, float]] = {}
    x = 30.0
    for c, stack in enumerate(stacks):
        y = 80 + (total - heights[c]) / 2
        for n in stack:
            w, h = size(n)
            boxes[n.name] = (x, y, w, h)
            y += h + vgap
        x += widths[c] + GAP_X
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
    line = derive_line(pal["fill"])
    head_text = _contrast_text(line)
    heights = [20] + [_row_h(r) for r in rows]
    out: list[str] = []
    tid, xml = _vertex(
        ids, parent, "",
        f"shape=table;startSize=0;container=1;collapsible=0;childLayout=tableLayout;fillColor=none;strokeColor={line};",
        x, y, TABLE_W, sum(heights),
    )
    out.append(xml)
    cy = 0.0
    for r_i, h in enumerate([None] + rows):
        height = heights[r_i]
        rid, xml = _vertex(
            ids, tid, "",
            "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;"
            "collapsible=0;dropTarget=0;fillColor=none;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;",
            0, cy, TABLE_W, height,
        )
        out.append(xml)
        cx = 0.0
        for c_i, name in enumerate(FIELD_COLUMNS):
            width = COL_WIDTHS[c_i]
            if h is None:
                value, fill, color, bold = name, line, head_text, "fontStyle=1;"
                font = "Arial"
            else:
                value, fill, color, bold = r_status(rows[r_i - 1], name), "#FFFFFF", "#000000", ""
                font = "Courier New" if name in ("Column", "Type") else "Arial"
            align = "left" if name in ("Column", "Type", "Description") else "center"
            style = (
                "shape=partialRectangle;html=1;whiteSpace=wrap;connectable=0;overflow=hidden;"
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
        pal = palette_for(n.kind)
        line = derive_line(pal["fill"])
        cid, xml = _vertex(
            ids, "1", n.name,
            f"swimlane;html=1;whiteSpace=wrap;rounded=1;arcSize=6;startSize={HEAD_H};collapsible=1;"
            f"fillColor={pal['fill']};swimlaneFillColor={pal['fill']};strokeColor={line};strokeWidth=2;"
            f"fontFamily=Courier New;fontSize=12;fontStyle=1;fontColor={pal['text']};align=left;spacingLeft=8;",
            x, y, w, h,
        )
        node_id[n.name] = cid
        cells.append(xml)
        note_h = 14 * _lines(n.note, int(w)) + 6
        _, xml = _vertex(
            ids, cid, n.note,
            f"text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontFamily=Arial;fontSize=11;fontStyle=2;"
            f"fontColor={pal['text']};spacingLeft=8;spacingRight=8;",
            0, HEAD_H + 2, w, note_h,
        )
        cells.append(xml)
        if full and not n.external and n.rows:
            cells.extend(_table(ids, cid, n.rows, pal, 8, HEAD_H + 2 + note_h + 4))

    cells.extend(_edges(model, boxes, node_id, ids))

    ly = bottom + 40
    lx = 30.0
    kinds = ["Hub", "Link", "Satellite"] + (["Reference table"] if any(n.kind == "Reference table" for n in model.nodes) else [])
    for kind in kinds:
        pal = PALETTE[kind]
        _, xml = _vertex(
            ids, "1", "",
            f"rounded=1;arcSize=20;fillColor={pal['fill']};strokeColor={derive_line(pal['fill'])};strokeWidth=2;",
            lx, ly, 22, 22,
        )
        cells.append(xml)
        _, xml = _vertex(
            ids, "1", kind,
            "text;html=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=11;fontColor=#000000;",
            lx + 28, ly, 110, 22,
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

    # waypoints per gap: edges that go down and edges that go up use separate bands, ordered so they do not cross
    gaps: dict[int, list[tuple[Edge, float, float]]] = {}
    for e in model.edges:
        lo = min(col[e.child], col[e.parent])
        left, right = (e.child, e.parent) if col[e.child] < col[e.parent] else (e.parent, e.child)
        gaps.setdefault(lo, []).append((e, attach[(id(e), left, "right")], attach[(id(e), right, "left")]))
    mid_x: dict[int, float] = {}
    for e_list in gaps.values():
        for e, _, _ in e_list:
            left, right = (e.child, e.parent) if col[e.child] < col[e.parent] else (e.parent, e.child)
            lx, _, lw, _ = boxes[left]
            rx, _, _, _ = boxes[right]
            mid_x[id(e)] = (lx + lw + rx) / 2
    wx: dict[int, float] = {}
    step = 12.0
    for e_list in gaps.values():
        down = sorted([t for t in e_list if t[1] < t[2] - 0.5], key=lambda t: t[1])
        up = sorted([t for t in e_list if t[1] > t[2] + 0.5], key=lambda t: t[1])
        for j, (e, _, _) in enumerate(down):
            wx[id(e)] = mid_x[id(e)] - GAP_X / 6 + ((len(down) - 1) / 2 - j) * step
        for j, (e, _, _) in enumerate(up):
            wx[id(e)] = mid_x[id(e)] + GAP_X / 6 + (j - (len(up) - 1) / 2) * step

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
        if abs(y_left - y_right) > 0.5:
            x = wx[id(e)]
            pts = [(x, y_left), (x, y_right)]
            if e.child != left:
                pts.reverse()
            points = '<Array as="points">' + "".join(f'<mxPoint x="{px:g}" y="{py:g}"/>' for px, py in pts) + "</Array>"
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
            f'<mxGeometry x="-0.4" relative="1" as="geometry">{points}</mxGeometry></mxCell>'
        )
    return out


# ---------------------------------------------------------------- export

def find_drawio() -> str | None:
    env = os.environ.get("DRAWIO_EXE")
    candidates = [env] if env else []
    candidates += [r"C:\Program Files\draw.io\draw.io.exe", shutil.which("draw.io") or ""]
    return next((c for c in candidates if c and Path(c).is_file()), None)


def export_png(exe: str, source: Path, target: Path, scale: int) -> None:
    subprocess.run([exe, "-x", "-f", "png", "--scale", str(scale), "-b", "10", "-o", str(target), str(source)], check=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Build the simple and full diagrams of a Business Object page")
    ap.add_argument("page")
    ap.add_argument("--context", default="", help="comma-separated objects defined on other pages")
    ap.add_argument("--no-export", action="store_true", help="write the .drawio files only")
    args = ap.parse_args(argv)
    page = Path(args.page)
    context = [c.strip() for c in args.context.split(",") if c.strip()]
    model = load_model(page.read_text(encoding="utf-8"), context)
    for full, suffix, scale in ((False, "", 3), (True, "_Full", 2)):
        title = f"SILVER: {model.title} cluster (Data Vault 2.0)" + (", full" if full else "")
        drawio = page.with_name(page.stem + suffix + ".drawio")
        drawio.write_text(to_drawio(model, full, title), encoding="utf-8", newline="\n")
        print("wrote", drawio)
        if not args.no_export:
            exe = find_drawio()
            if not exe:
                print("draw.io Desktop not found; set DRAWIO_EXE or use --no-export", file=sys.stderr)
                return 1
            png = drawio.with_suffix(".png")
            export_png(exe, drawio, png, scale)
            print("wrote", png)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
