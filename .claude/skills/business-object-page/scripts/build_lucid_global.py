"""Build the global Hubs + Links + Satellites diagram of the Business Objects as Lucid Standard Import JSON.

The model comes from the page markdown (the same `load_model` the drawio builder uses), so the picture cannot drift
from the pages. Lucid draws straight lines only, so the layout is arranged to keep them from crossing, and every box
is sized from its text: text width/height plus PAD.

    python build_lucid_global.py out.json
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_diagram as bd  # noqa: E402

REPO = HERE.parents[3]
PAGES = ["Party", "Natural_Person", "Legal_Entity", "Code_List", "Load_Configuration"]

# ---------------------------------------------------------------- style (from the Lucid proposal and the drawio files)
# Same hues as the drawio files. The background is lighter; the border is the drawio fill.
# The in-place Satellite is lighter again; its border is the drawio in-place fill.
STYLE = {
    "Hub": {"fill": "#8F63F4", "line": "#3A0CA3"},
    "Link": {"fill": "#A2F1E6", "line": "#45E3CD"},
    "Satellite": {"fill": "#FCB3D5", "line": "#F72586"},
    "Satellite (in place)": {"fill": "#FEDBEB", "line": "#FCB3D5"},
}
TEXT_COLOR = "#000000"
EDGE_COLOR = "#3A414A"
BAND_FILL = "#F6F4FC"
BAND_LINE = "#A6A8AB"

# ---------------------------------------------------------------- text measurement
UNIT_PER_PT = 160 / 72          # Lucid's coordinate system is 160 dpi
NAME_PT = 11
GRAIN_PT = 8
BOLD_EM = 0.57                  # average character width of Mulish bold, in em (measured on an export; a box that is too tight wraps its last word)
ITALIC_EM = 0.54                # average character width of Mulish italic, in em (measured on an export)
LINE_EM = 1.30
PAD = 10 * UNIT_PER_PT          # "text size + 10 pt" for width and height
LINE_W = 2
GAP_X = 170
GAP_ROW = 26
GAP_CHAIN = 80
HUB_PER_EDGE = 20
BAND_PAD = 80


def _w(text: str, pt: float, em: float) -> float:
    return len(text) * pt * UNIT_PER_PT * em


def _lh(pt: float) -> float:
    return pt * UNIT_PER_PT * LINE_EM


def name_lines(name: str) -> list[str]:
    """A long name is broken after its double underscore, so the box stays narrow."""
    if name.startswith(("sat_", "lnk_")) and "__" in name:
        head, _, tail = name.rpartition("__")
        return [head + "__", tail]
    return [name]


def wrap(text: str, chars: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > chars:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


@dataclass
class Box:
    name: str
    kind: str
    in_place: bool
    name_lines: list[str]
    grain_lines: list[str]
    w: float = 0.0
    h: float = 0.0
    x: float = 0.0
    y: float = 0.0
    text_w: float = 0.0
    text_h: float = 0.0

    @property
    def style(self) -> dict:
        return STYLE["Satellite (in place)" if self.in_place else self.kind]

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


def measure(node: bd.Node) -> Box:
    kind = "Link" if node.kind == "Non-historized Link" else node.kind
    names = name_lines(node.name)
    name_w = max(_w(line, NAME_PT, BOLD_EM) for line in names)
    chars = max(24, int(max(name_w, 250) / (GRAIN_PT * UNIT_PER_PT * ITALIC_EM)))
    grain = wrap(node.note, chars) if node.note else []
    grain_w = max((_w(line, GRAIN_PT, ITALIC_EM) for line in grain), default=0.0)
    box = Box(node.name, kind, node.in_place, names, grain)
    box.text_w = max(name_w, grain_w)
    box.text_h = len(names) * _lh(NAME_PT) + len(grain) * _lh(GRAIN_PT)
    box.w = box.text_w + PAD
    box.h = box.text_h + PAD
    return box


def box_html(box: Box) -> str:
    name = "<br>".join(box.name_lines)
    parts = f'<b>{name}</b>'
    if box.grain_lines:
        grain = "<br>".join(box.grain_lines)
        parts += f'<br><span style="font-size:{GRAIN_PT}pt"><i>{grain}</i></span>'
    return f'<p style="font-size:{NAME_PT}pt;text-align:center">{parts}</p>'


# ---------------------------------------------------------------- model of the five pages
def load_all(pages_dir: Path | None = None) -> tuple[dict[str, bd.Node], list[bd.Edge]]:
    pages_dir = pages_dir or REPO / "Rosetta" / "Business_Objects"
    nodes: dict[str, bd.Node] = {}
    edges: dict[tuple[str, str, str], bd.Edge] = {}
    for page in PAGES:
        model = bd.load_model((pages_dir / f"{page}.md").read_text(encoding="utf-8"))
        for n in model.nodes:
            if n.name not in nodes or (nodes[n.name].external and not n.external):
                nodes[n.name] = n
        for e in model.edges:
            edges[(e.child, e.parent, e.label)] = e
    return nodes, list(edges.values())


def twin_order(names: list[str]) -> list[str]:
    """The default (history) Satellite first, its in-place twin right under it."""
    out: list[str] = []
    for n in names:
        if n in out:
            continue
        hist = n + "_history"
        if hist in names:
            out += [hist, n]
        elif not n.endswith("_history") or n[: -len("_history")] not in names:
            out.append(n)
    return out


def sats_of(parent: str, nodes: dict[str, bd.Node], edges: list[bd.Edge]) -> list[str]:
    names = [e.child for e in edges if e.parent == parent and nodes[e.child].kind == "Satellite"]
    order = [n for n in nodes if n in names]
    return twin_order(order)


# ---------------------------------------------------------------- layout
@dataclass
class Layout:
    boxes: dict[str, Box] = field(default_factory=dict)
    lines: list[dict] = field(default_factory=list)
    bands: list[dict] = field(default_factory=list)
    twins: list[tuple[str, str]] = field(default_factory=list)


def _stack(layout: Layout, names: list[str], x: float, y: float, width: float, align: str = "left") -> float:
    """Stack boxes top to bottom. Each box keeps its own size (text + PAD); the two Satellites of a twin pair share
    the wider width so the dashed line between them is straight. `x`/`width` is the column, `align` where a box sits in it.
    Returns the bottom edge."""
    for n in names:
        b = layout.boxes[n]
        partner = n[: -len("_history")] if n.endswith("_history") else n + "_history"
        if partner in names:
            w = max(b.w, layout.boxes[partner].w)
            b.w = layout.boxes[partner].w = w
    for n in names:
        b = layout.boxes[n]
        b.x = x if align == "left" else x + width - b.w if align == "right" else x + (width - b.w) / 2
        b.y = y
        y += b.h + GAP_ROW
    return y - GAP_ROW


def _line(layout: Layout, child: str, parent: str, c_pos: tuple[float, float], p_pos: tuple[float, float], dashed=False, arrow=True):
    layout.lines.append({"child": child, "parent": parent, "c": c_pos, "p": p_pos, "dashed": dashed, "arrow": arrow})


def _fan(layout: Layout, sats: list[str], hub: str, side: str):
    """Each satellite meets the hub at its own point, in the order of the satellites, so straight lines do not cross."""
    hubbox = layout.boxes[hub]
    n = len(sats)
    for i, s in enumerate(sats):
        frac = (i + 0.5) / n
        if side == "left":
            _line(layout, s, hub, (1.0, 0.5), (0.0, frac))
        else:
            _line(layout, s, hub, (0.0, 0.5), (1.0, frac))


def build_layout(nodes: dict[str, bd.Node], edges: list[bd.Edge]) -> Layout:
    L = Layout()
    for name, node in nodes.items():
        L.boxes[name] = measure(node)
    degree = {n: sum(1 for e in edges if n in (e.child, e.parent)) for n in nodes}
    for name, box in L.boxes.items():
        if box.kind == "Hub":
            box.h = max(box.h, HUB_PER_EDGE * (degree[name] + 1))

    np_all = sats_of("hub_natural_person", nodes, edges)
    np_pairs = [n for n in np_all if n.endswith("_history") or n + "_history" in np_all]
    np_singles = [n for n in np_all if n not in np_pairs]
    le_all = sats_of("hub_legal_entity", nodes, edges)
    rep = [n for n in nodes if n.startswith("sat_legal_entity__natural_person__")]
    le_sats = [n for n in le_all if n not in rep]
    cl_hub = sats_of("hub_code_list", nodes, edges)
    cv_hub = sats_of("hub_code_value", nodes, edges)
    lc_sats = sats_of("hub_load_configuration", nodes, edges)
    chain = ["hub_natural_person", "lnk_natural_person__party", "hub_party", "lnk_legal_entity__party", "hub_legal_entity"]
    link_np_name = "lnk_legal_entity__natural_person"
    rel_link, rel_sat = "lnk_natural_person__natural_person_relation", "sat_natural_person__natural_person_relation__relationship"
    own_link, own_sat = "lnk_legal_entity__party_owner", "sat_legal_entity__party_owner__ownership"

    def width(names):
        return max(L.boxes[n].w for n in names)

    wL = width(np_singles + rep + [link_np_name])
    wM = width(chain + [rel_link])
    wR = width(np_pairs + le_sats + [own_link, rel_sat])
    wS = width([own_sat])
    xL = BAND_PAD
    xM = xL + wL + GAP_X
    xR = xM + wM + GAP_X
    xS = xR + wR + GAP_X
    reg_w = BAND_PAD * 2 + wL + wM + wR + wS + 3 * GAP_X

    # ---- Registries band
    by = 60.0
    # first row: the relationship between two people, above the Natural Person Hub
    rl, rs = L.boxes[rel_link], L.boxes[rel_sat]
    row_top = by + 110
    row_h = max(rl.h, rs.h)
    rl.x, rl.y = xM + (wM - rl.w) / 2, row_top + (row_h - rl.h) / 2
    rs.x, rs.y = xR, row_top + (row_h - rs.h) / 2
    _line(L, rel_sat, rel_link, (0.0, 0.5), (1.0, 0.5))
    top = row_top + row_h + 110
    bottom_r = _stack(L, np_pairs, xR, top, wR, "left")
    h_l = sum(L.boxes[n].h for n in np_singles) + GAP_ROW * (len(np_singles) - 1)
    l_top = top + ((bottom_r - top) - h_l) / 2
    bottom_l = _stack(L, np_singles, xL, l_top, wL, "right")
    hub_np = L.boxes["hub_natural_person"]
    hub_np.x = xM + (wM - hub_np.w) / 2
    hub_np.y = (top + bottom_r) / 2 - hub_np.h / 2
    for dx, label_x in ((-40, "subject"), (40, "related")):
        ax = hub_np.cx + dx
        _line(L, rel_link, "hub_natural_person", ((ax - rl.x) / rl.w, 1.0), ((ax - hub_np.x) / hub_np.w, 0.0))
    n_left = len(np_singles) + 1
    for i, s in enumerate(np_singles):
        _line(L, s, "hub_natural_person", (1.0, 0.5), (0.0, (i + 0.5) / n_left))
    for i, s in enumerate(np_pairs):
        _line(L, s, "hub_natural_person", (0.0, 0.5), (1.0, (i + 0.5) / len(np_pairs)))
    for a in np_pairs:
        if a.endswith("_history") and a[: -len("_history")] in np_pairs:
            L.twins.append((a, a[: -len("_history")]))

    y = hub_np.y + hub_np.h + GAP_CHAIN
    for n in chain[1:4]:
        b = L.boxes[n]
        b.x, b.y = xM + (wM - b.w) / 2, y
        y += b.h + GAP_CHAIN
    hub_le = L.boxes["hub_legal_entity"]
    hub_le.x = xM + (wM - hub_le.w) / 2
    ol, os_ = L.boxes[own_link], L.boxes[own_sat]
    ol.x, ol.y = xR, bottom_r + 90
    os_.x, os_.y = xS, ol.y + (ol.h - os_.h) / 2
    _line(L, own_sat, own_link, (0.0, 0.5), (1.0, 0.5))
    _line(L, own_link, "hub_party", (0.0, 0.3), (1.0, 0.5))
    _line(L, own_link, "hub_legal_entity", (0.0, 0.7), (1.0, 0.02))
    le_top = max(ol.y + ol.h + 90, y + hub_le.h / 2 - ((len(le_sats) * 140) / 2))
    le_bottom = _stack(L, le_sats, xR, le_top, wR, "left")
    hub_le.y = max((le_top + le_bottom) / 2 - hub_le.h / 2, y)
    for i, s in enumerate(le_sats):
        _line(L, s, "hub_legal_entity", (0.0, 0.5), (1.0, (i + 0.5) / len(le_sats)))

    rep_box = L.boxes[rep[0]]
    link_np = L.boxes[link_np_name]
    rep_box.x = xL + wL - rep_box.w
    link_np.x = xL + wL - link_np.w
    rep_box.y = bottom_l + 110
    link_np.y = rep_box.y + rep_box.h + GAP_CHAIN
    _line(L, rep[0], link_np_name, (0.5, 1.0), (0.5, 0.0))
    _line(L, link_np_name, "hub_natural_person", (1.0, 0.25), (0.0, (n_left - 0.5) / n_left))
    _line(L, link_np_name, "hub_legal_entity", (1.0, 0.75), (0.0, 0.5))

    _line(L, "lnk_natural_person__party", "hub_natural_person", (0.5, 0.0), (0.5, 1.0))
    _line(L, "lnk_natural_person__party", "hub_party", (0.5, 1.0), (0.5, 0.0))
    _line(L, "lnk_legal_entity__party", "hub_party", (0.5, 0.0), (0.5, 1.0))
    _line(L, "lnk_legal_entity__party", "hub_legal_entity", (0.5, 1.0), (0.5, 0.0))

    reg_bottom = max(le_bottom, hub_le.y + hub_le.h, link_np.y + link_np.h, ol.y + ol.h) + BAND_PAD
    L.bands.append({"title": "Registries", "x": 0.0, "y": by, "w": reg_w, "h": reg_bottom - by})

    # ---- Platform band, to the right of the Registries band
    pw_L = width(cl_hub + cv_hub + lc_sats)
    pw_M = width(["hub_code_list", "hub_code_value", "lnk_code_list__code_value", "hub_load_configuration"])
    px = reg_w + 130
    pxL = px + BAND_PAD
    pxM = pxL + pw_L + GAP_X
    plat_w = BAND_PAD * 2 + pw_L + pw_M + GAP_X
    cl_bottom = _stack(L, cl_hub, pxL, top, pw_L, "right")
    hcl = L.boxes["hub_code_list"]
    hcl.x = pxM + (pw_M - hcl.w) / 2
    hcl.y = (top + cl_bottom) / 2 - hcl.h / 2
    cv_top = cl_bottom + 90
    cv_bottom = _stack(L, cv_hub, pxL, cv_top, pw_L, "right")
    hcv = L.boxes["hub_code_value"]
    hcv.x = pxM + (pw_M - hcv.w) / 2
    hcv.y = (cv_top + cv_bottom) / 2 - hcv.h / 2
    lcv = L.boxes["lnk_code_list__code_value"]
    lcv.x = pxM + (pw_M - lcv.w) / 2
    lcv.y = (hcl.y + hcl.h + hcv.y) / 2 - lcv.h / 2
    for i, s in enumerate(cl_hub):
        _line(L, s, "hub_code_list", (1.0, 0.5), (0.0, (i + 0.5) / len(cl_hub)))
    for i, s in enumerate(cv_hub):
        _line(L, s, "hub_code_value", (1.0, 0.5), (0.0, (i + 0.5) / len(cv_hub)))
    _line(L, "lnk_code_list__code_value", "hub_code_list", (0.5, 0.0), (0.5, 1.0))
    _line(L, "lnk_code_list__code_value", "hub_code_value", (0.5, 1.0), (0.5, 0.0))
    lc_top = max(cv_bottom, hcv.y + hcv.h) + 130
    lc_bottom = _stack(L, lc_sats, pxL, lc_top, pw_L, "right")
    hlc = L.boxes["hub_load_configuration"]
    hlc.x = pxM + (pw_M - hlc.w) / 2
    hlc.y = (lc_top + lc_bottom) / 2 - hlc.h / 2
    for i, s in enumerate(lc_sats):
        _line(L, s, "hub_load_configuration", (1.0, 0.5), (0.0, (i + 0.5) / len(lc_sats)))
    plat_bottom = max(lc_bottom, hlc.y + hlc.h) + BAND_PAD
    L.bands.append({"title": "Platform", "x": px, "y": by, "w": plat_w, "h": plat_bottom - by})
    L.legend_y = max(reg_bottom, plat_bottom) + 60
    L.band_w = px + plat_w
    return L


# ---------------------------------------------------------------- Standard Import JSON
def _abs(box: Box, pos: tuple[float, float]) -> tuple[float, float]:
    return box.x + pos[0] * box.w, box.y + pos[1] * box.h


def segments(L: Layout) -> list[tuple[dict, tuple[float, float], tuple[float, float]]]:
    out = []
    for ln in L.lines:
        out.append((ln, _abs(L.boxes[ln["child"]], ln["c"]), _abs(L.boxes[ln["parent"]], ln["p"])))
    return out


def short_ids(L: Layout) -> dict[str, str]:
    """Lucid rejects long shape ids (a 49 character id failed the import), so each object gets a short one."""
    return {name: f"n{i}" for i, name in enumerate(L.boxes, 1)}


def to_spec(L: Layout, title: str = "PSS Data Objects") -> dict:
    ids = short_ids(L)
    shapes: list[dict] = []
    for band in L.bands:
        shapes.append({
            "id": "band_" + band["title"].lower(),
            "type": "roundedRectangleContainer",
            "boundingBox": {"x": round(band["x"], 1), "y": round(band["y"], 1), "w": round(band["w"], 1), "h": round(band["h"], 1)},
            "containerTitle": {"text": band["title"] + " (owner domain)"},
            "style": {"fill": {"type": "color", "color": BAND_FILL}, "stroke": {"color": BAND_LINE, "width": 2, "style": "solid"}},
        })
    for box in L.boxes.values():
        shapes.append({
            "id": ids[box.name],
            "type": "rectangle",
            "customData": [{"key": "name", "value": box.name}],
            "boundingBox": {"x": round(box.x, 1), "y": round(box.y, 1), "w": round(box.w, 1), "h": round(box.h, 1)},
            "text": box_html(box),
            "style": {
                "fill": {"type": "color", "color": box.style["fill"]},
                "stroke": {"color": box.style["line"], "width": 3, "style": "solid"},
                "textColor": TEXT_COLOR,
            },
        })
    lines = []
    for i, ln in enumerate(L.lines, 1):
        lines.append({
            "id": f"e{i}",
            "lineType": "straight",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[ln["child"]], "position": {"x": ln["c"][0], "y": ln["c"][1]}},
            "endpoint2": {"type": "shapeEndpoint", "style": "arrow" if ln["arrow"] else "none", "shapeId": ids[ln["parent"]], "position": {"x": ln["p"][0], "y": ln["p"][1]}},
            "stroke": {"color": EDGE_COLOR, "width": 1, "style": "dashed" if ln["dashed"] else "solid"},
        })
    for i, (a, b) in enumerate(L.twins, 1):
        lines.append({
            "id": f"t{i}",
            "lineType": "straight",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[a], "position": {"x": 0.5, "y": 1.0}},
            "endpoint2": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[b], "position": {"x": 0.5, "y": 0.0}},
            "stroke": {"color": EDGE_COLOR, "width": 1, "style": "dashed"},
        })
    # legend
    lx, ly = 60.0, L.legend_y
    entries = [("Hub", "Hub"), ("Link", "Link"), ("Satellite, history (the default)", "Satellite"), ("Satellite, in place (the exception)", "Satellite (in place)")]
    for i, (label, key) in enumerate(entries):
        shapes.append({
            "id": f"legend_box_{i}", "type": "rectangle",
            "boundingBox": {"x": lx, "y": ly, "w": 60, "h": 36},
            "style": {"fill": {"type": "color", "color": STYLE[key]["fill"]}, "stroke": {"color": STYLE[key]["line"], "width": 3, "style": "solid"}},
        })
        shapes.append({
            "id": f"legend_text_{i}", "type": "text",
            "boundingBox": {"x": lx + 72, "y": ly, "w": 560, "h": 36},
            "text": f'<p style="font-size:10pt;text-align:left">{label}</p>',
        })
        lx += 660
    shapes.append({
        "id": "legend_note", "type": "text",
        "boundingBox": {"x": 60, "y": ly + 50, "w": 2400, "h": 36},
        "text": '<p style="font-size:9pt;text-align:left">Arrows run from the child to its parent. A dashed line joins the two Satellites of a twin pair. The grain, one row per ..., is written in each box.</p>',
    })
    return {"version": 1, "pages": [{"id": "page1", "title": title, "shapes": shapes, "lines": lines}]}


def main(argv: list[str]) -> int:
    out = Path(argv[0]) if argv else Path("lucid_global.json")
    nodes, edges = load_all()
    L = build_layout(nodes, edges)
    out.write_text(json.dumps(to_spec(L), ensure_ascii=False), encoding="utf-8")
    print("wrote", out, f"({len(L.boxes)} boxes, {len(L.lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
