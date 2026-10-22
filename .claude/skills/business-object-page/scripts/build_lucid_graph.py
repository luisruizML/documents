"""Build the simplified graph of the Business Objects: Hubs as circles, Links as hexagons, Satellites as small squares,
the name of each beside it. It complements the global diagram (`build_lucid_global.py`) and is read from the same
pages, so it cannot drift from them. Gray dashed lines join the Code List and the Load Configuration to their users.

    python build_lucid_graph.py out.json [--preview out.png]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_lucid_global as g  # noqa: E402
import graph_layout as gl  # noqa: E402
import platform_usage as pu  # noqa: E402

COLORS = {
    "Hub": {"fill": "#8F63F4", "line": "#3A414A", "tag": "HUB"},
    "Link": {"fill": "#A2F1E6", "line": "#3A414A", "tag": "LINK"},
    "Satellite": {"fill": "#FCB3D5", "line": "#F72586", "tag": "SAT"},
    "Satellite (in place)": {"fill": "#FEDBEB", "line": "#FCB3D5", "tag": "SAT"},
}
EDGE = "#3A414A"


def key(item: gl.Placed) -> str:
    return "Satellite (in place)" if item.in_place else item.kind


def build(nodes=None, edges=None) -> tuple[gl.GraphLayout, list[tuple[str, str]]]:
    if nodes is None:
        nodes, edges = g.load_all()
    kinds = {n: node.kind for n, node in nodes.items()}
    in_place = {n: node.in_place for n, node in nodes.items()}
    pairs = [(e.child, e.parent) for e in edges]
    sat_order = g.twin_order([n for n, k in kinds.items() if k == "Satellite"])
    return gl.layout(kinds, in_place, pairs, sat_order), pu.uses_lines(nodes)


def preview(L: gl.GraphLayout, uses, path: Path) -> None:
    from PIL import Image, ImageDraw
    xs = [v for p in L.items.values() for v in (p.rect[0], p.rect[2], p.label_rect[0], p.label_rect[2])]
    ys = [v for p in L.items.values() for v in (p.rect[1], p.rect[3], p.label_rect[1], p.label_rect[3])]
    s = 0.5
    img = Image.new("RGB", (int(max(xs) * s) + 40, int(max(ys) * s) + 40), "white")
    d = ImageDraw.Draw(img)
    c = lambda p: (p.x * s, p.y * s)  # noqa: E731
    for a, b in uses:
        d.line([c(L.items[a]), c(L.items[b])], fill="#B8B8B8", width=1)
    for a, b in L.edges:
        d.line([c(L.items[a]), c(L.items[b])], fill=EDGE, width=2)
    for p in L.items.values():
        st = COLORS[key(p)]
        x0, y0, x1, y1 = [v * s for v in p.rect]
        if p.kind == "Hub":
            d.ellipse([x0, y0, x1, y1], fill=st["fill"], outline=st["line"], width=2)
        elif p.kind == "Link":
            d.regular_polygon(((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2), 6, fill=st["fill"], outline=st["line"])
        else:
            d.rectangle([x0, y0, x1, y1], fill=st["fill"], outline=st["line"], width=2)
        lx0, ly0, lx1, ly1 = [v * s for v in p.label_rect]
        d.rectangle([lx0, ly0, lx1, ly1], outline="#DDDDDD")
        d.text((lx0 + 2, ly0 + 1), p.name, fill="black")
    img.save(path)


# ---------------------------------------------------------------- Standard Import JSON
SHAPE_TYPE = {"Hub": "connector", "Link": "preparation", "Satellite": "process"}   # the Flowchart shapes of the hand-drawn graph
USES_COLOR = g.USES_COLOR
HEXAGON = [(0.0, 0.5), (0.25, 0.0), (0.75, 0.0), (1.0, 0.5), (0.75, 1.0), (0.25, 1.0)]


def boundary(item: gl.Placed, toward: gl.Placed) -> tuple[float, float]:
    """Where the straight line from the centre of `item` to the centre of `toward` leaves the shape, as fractions of its box."""
    dx, dy = toward.x - item.x, toward.y - item.y
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    if item.kind == "Hub":                       # circle
        return round(0.5 + 0.5 * ux, 4), round(0.5 + 0.5 * uy, 4)
    if item.kind == "Link":                      # hexagon: nearest crossing of the ray with an edge
        best = None
        for i, (x1, y1) in enumerate(HEXAGON):
            x2, y2 = HEXAGON[(i + 1) % 6]
            ex, ey = (x2 - x1) * item.w, (y2 - y1) * item.h
            ox, oy = (x1 - 0.5) * item.w, (y1 - 0.5) * item.h
            det = ux * -ey - uy * -ex
            if abs(det) < 1e-9:
                continue
            t_ray = (ox * -ey - oy * -ex) / det
            t_edge = (ux * oy - uy * ox) / det
            if t_ray > 0 and 0 <= t_edge <= 1 and (best is None or t_ray < best):
                best = t_ray
        r = best or item.w / 2
        return round(0.5 + ux * r / item.w, 4), round(0.5 + uy * r / item.h, 4)
    scale = min((item.w / 2) / abs(ux) if ux else math.inf, (item.h / 2) / abs(uy) if uy else math.inf)   # rectangle
    return round(0.5 + ux * scale / item.w, 4), round(0.5 + uy * scale / item.h, 4)


def label_html(item: gl.Placed) -> str:
    size, weight = (11, True) if item.kind == "Hub" else (7, False)
    name = f"<b>{item.name}</b>" if weight else item.name
    return f'<p style="font-size:{size}pt;text-align:{item.align};font-family:Liberation Mono">{name}</p>'


def tag_html(item: gl.Placed) -> str:
    tag = COLORS[key(item)]["tag"]
    return f'<p style="font-size:{10 if item.kind == "Hub" else 7}pt;text-align:center">{"<b>" + tag + "</b>" if item.kind == "Hub" else tag}</p>'


def to_spec(L: gl.GraphLayout, uses, title: str = "PSS Data Objects - Graph") -> dict:
    ids = {name: f"n{i}" for i, name in enumerate(L.items, 1)}
    shapes: list[dict] = []
    for name, p in L.items.items():
        st = COLORS[key(p)]
        shapes.append({
            "id": ids[name], "type": SHAPE_TYPE[p.kind],
            "customData": [{"key": "name", "value": name}],
            "boundingBox": {"x": round(p.x - p.w / 2, 1), "y": round(p.y - p.h / 2, 1), "w": round(p.w, 1), "h": round(p.h, 1)},
            "text": tag_html(p),
            "style": {"fill": {"type": "color", "color": st["fill"]}, "stroke": {"color": st["line"], "width": 2, "style": "solid"},
                      "textColor": "#000000"},
        })
    for name, p in L.items.items():
        shapes.append({
            "id": "l" + ids[name][1:], "type": "text",
            "boundingBox": {"x": round(p.lx - p.lw / 2, 1), "y": round(p.ly - p.lh / 2, 1), "w": round(p.lw, 1), "h": round(p.lh, 1)},
            "text": label_html(p),
        })
    lines = []
    for i, (src, user) in enumerate(uses, 1):
        a, b = L.items[src], L.items[user]
        (ax, ay), (bx, by) = boundary(a, b), boundary(b, a)
        lines.append({
            "id": f"u{i}", "lineType": "straight",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[src], "position": {"x": ax, "y": ay}},
            "endpoint2": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[user], "position": {"x": bx, "y": by}},
            "stroke": {"color": USES_COLOR, "width": 1, "style": "dashed"},
        })
    for i, (child, parent) in enumerate(L.edges, 1):
        a, b = L.items[child], L.items[parent]
        (ax, ay), (bx, by) = boundary(a, b), boundary(b, a)
        lines.append({
            "id": f"e{i}", "lineType": "straight",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[child], "position": {"x": ax, "y": ay}},
            "endpoint2": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[parent], "position": {"x": bx, "y": by}},
            "stroke": {"color": EDGE, "width": 2, "style": "solid"},
        })
    ly = max(p.label_rect[3] for p in L.items.values()) + 80
    lx = 80.0
    for i, (label, sk) in enumerate((("Hub", "Hub"), ("Link", "Link"), ("Satellite, history (the default)", "Satellite"),
                                      ("Satellite, in place (the exception)", "Satellite (in place)"))):
        st = COLORS[sk]
        kind = {"Hub": "connector", "Link": "preparation"}.get(sk, "process")
        shapes.append({"id": f"legend_box_{i}", "type": kind, "boundingBox": {"x": lx, "y": ly, "w": 60, "h": 40},
                       "text": "<p style=\"font-size:7pt;text-align:center\">" + st["tag"] + "</p>",
                       "style": {"fill": {"type": "color", "color": st["fill"]}, "stroke": {"color": st["line"], "width": 2, "style": "solid"}}})
        shapes.append({"id": f"legend_text_{i}", "type": "text", "boundingBox": {"x": lx + 72, "y": ly + 4, "w": 480, "h": 32},
                       "text": f'<p style="font-size:10pt;text-align:left">{label}</p>'})
        lx += 620
    lines.append({"id": "legend_uses", "lineType": "straight",
                  "endpoint1": {"type": "positionEndpoint", "style": "none", "position": {"x": 80.0, "y": ly + 80}},
                  "endpoint2": {"type": "positionEndpoint", "style": "none", "position": {"x": 140.0, "y": ly + 80}},
                  "stroke": {"color": USES_COLOR, "width": 1, "style": "dashed"}})
    shapes.append({"id": "legend_uses_text", "type": "text", "boundingBox": {"x": 152.0, "y": ly + 64, "w": 2400, "h": 32},
                   "text": '<p style="font-size:10pt;text-align:left">Gray dashed line: from hub_code_list to every object with a column whose values come '
                           'from a Code List; from hub_load_configuration to the Satellites it decides between</p>'})
    return {"version": 1, "pages": [{"id": "page1", "title": title, "shapes": shapes, "lines": lines}]}


def main(argv: list[str]) -> int:
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--preview")]
    out = Path(args[0]) if args else Path("lucid_graph.json")
    L, uses = build()
    print(f"{len(L.items)} nodes, {len(L.edges)} edges, {L.crossings} crossings, {L.overlaps} overlaps, {L.label_hits} lines through a name")
    out.write_text(json.dumps(to_spec(L, uses), ensure_ascii=False), encoding="utf-8")
    if "--preview" in argv:
        preview(L, uses, Path(argv[argv.index("--preview") + 1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
