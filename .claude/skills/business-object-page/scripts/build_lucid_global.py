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
import platform_usage as pu  # noqa: E402

REPO = HERE.parents[3]
PAGES = ["Party", "Natural_Person", "Legal_Entity", "Location", "Base_Parcel", "Built_Structure", "Code_List", "Load_Configuration"]

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
USES_COLOR = "#A6A8AB"          # the light, dashed "uses" line from the Code List and the Load Configuration

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
SIMPLIFIED = False              # True: each box holds its name and its grain ("one row per ...") instead of its definition


def _w(text: str, pt: float, em: float) -> float:
    return len(text) * pt * UNIT_PER_PT * em


def _lh(pt: float) -> float:
    return pt * UNIT_PER_PT * LINE_EM


def name_lines(name: str) -> list[str]:
    """The name of an object is always one line, however long: the box grows to fit it."""
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
    text = (node.grain or node.note) if SIMPLIFIED else node.note
    grain = wrap(text, chars) if text else []
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
    uses: list[tuple[str, str]] = field(default_factory=list)   # (Code List or Load Configuration Hub, user): gray dashed lines


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


def _location_block(L: Layout, nodes: dict[str, bd.Node], edges: list[bd.Edge], x0: float, yc: float) -> tuple[float, float, float]:
    """The Location cluster, inside the Registries band, east of the ownership group. Left to right: the umbrella Hub, the Links
    of the three views, the three description Hubs, their descriptions. The umbrella Hub is centred on `yc`, the height of the
    ownership line, so the Link from a person comes down to it and the Link from an entity comes up to it, both east of the
    ownership group. The zone Hub is the last row, so the Link of its hierarchy sits under the others.
    Returns the top edge, the bottom edge and the right edge."""
    views = [("hub_address", "sat_address__description", "lnk_address__location"),
             ("hub_geometry", "sat_geometry__shape", "lnk_geometry__location"),
             ("hub_administrative_zone", "sat_administrative_zone__description", "lnk_administrative_zone__location")]
    hier_link = "lnk_administrative_zone__administrative_zone_hierarchy"
    hier_sat = "sat_administrative_zone__administrative_zone_hierarchy__period"
    B = L.boxes
    row_hs = [max(B[h].h, B[s].h, B[k].h) for h, s, k in views]

    def col_w(names):
        return max(B[n].w for n in names)

    w2 = B["hub_location"].w
    w3 = col_w([v[2] for v in views] + [hier_link, hier_sat])
    w4 = col_w([v[0] for v in views])
    w5 = col_w([v[1] for v in views])
    x2 = x0
    x3 = x2 + w2 + GAP_X
    x4 = x3 + w3 + GAP_X
    x5 = x4 + w4 + GAP_X
    first_center = row_hs[0] / 2
    last_center = sum(row_hs[:-1]) + 110 * (len(row_hs) - 1) + row_hs[-1] / 2
    top = yc - (first_center + last_center) / 2
    y = top
    for (hub, sat, lnk), row_h in zip(views, row_hs):
        h, s_, k = B[hub], B[sat], B[lnk]
        h.x, h.y = x4, y + (row_h - h.h) / 2
        s_.x, s_.y = x5, y + (row_h - s_.h) / 2
        k.x, k.y = x3 + (w3 - k.w) / 2, y + (row_h - k.h) / 2
        _line(L, sat, hub, (0.0, 0.5), (1.0, 0.5))
        _line(L, lnk, hub, (1.0, 0.3), (0.0, 0.3))
        y += row_h + 110
    hl, hs = B[hier_link], B[hier_sat]
    hl.x = x3 + (w3 - hl.w) / 2
    hl.y = y
    hs.x = x3 + (w3 - hs.w) / 2
    hs.y = hl.y + hl.h + 110
    _line(L, hier_link, "hub_administrative_zone", (1.0, 0.3), (0.0, 0.65))
    _line(L, hier_link, "hub_administrative_zone", (1.0, 0.7), (0.0, 0.9))
    _line(L, hier_sat, hier_link, (0.5, 0.0), (0.5, 1.0))
    hub_loc = B["hub_location"]
    hub_loc.x, hub_loc.y = x2, yc - hub_loc.h / 2
    for i, (hub, sat, lnk) in enumerate(views):
        _line(L, lnk, "hub_location", (0.0, 0.5), (1.0, (i + 0.5) / len(views)))
    return top, max(hs.y + hs.h, hub_loc.y + hub_loc.h), x5 + w5


def _pair_x(a: Box, b: Box) -> tuple[float, float]:
    """The position, on `a` and on `b`, of a vertical line between two boxes that overlap in x."""
    lo, hi = max(a.x, b.x), min(a.x + a.w, b.x + b.w)
    x = (lo + hi) / 2
    return (x - a.x) / a.w, (x - b.x) / b.w


def _frac(box: Box, y: float) -> float:
    return min(0.97, max(0.03, (y - box.y) / box.h))


def _immovable_block(L: Layout, nodes: dict[str, bd.Node], edges: list[bd.Edge], cols: dict[str, float], y0: float) -> tuple[float, float]:
    """The Immovable Asset cluster, inside the Registries band, below everything else. The parcel Hub and the structure Hub
    stand in the middle column, the Link between them in between. Their Satellites are on the left. On the right, first the two
    ownership Links by a Party (left-aligned, their lines go up to hub_party along the corridor east of the chain), then, right-aligned,
    the place Links (their lines go up to hub_location) and the government Links (their lines go east to hub_government_authority),
    each Link with its Satellite under it. A Hub is as tall as the rows it serves, so the lines to it run level.
    Returns the bottom edge and the height of the middle of the government rows."""
    B = L.boxes
    xL, wL, xM, wM, xR = cols["xL"], cols["wL"], cols["xM"], cols["wM"], cols["xR"]
    P, S, GA = "hub_base_parcel", "hub_built_structure", "hub_government_authority"
    pairs = {"po": ("lnk_base_parcel__party_owner", "sat_base_parcel__party_owner__ownership"),
             "so": ("lnk_built_structure__party_owner", "sat_built_structure__party_owner__ownership"),
             "pl": ("lnk_base_parcel__location", "sat_base_parcel__location__usage"),
             "sl": ("lnk_built_structure__location", "sat_built_structure__location__usage"),
             "pg": ("lnk_base_parcel__government_authority", "sat_base_parcel__government_authority__ownership"),
             "sg": ("lnk_built_structure__government_authority", "sat_built_structure__government_authority__ownership")}
    chain_link, chain_sat = "lnk_base_parcel__built_structure", "sat_base_parcel__built_structure__period"
    hier, hier_sat = "lnk_built_structure__built_structure_hierarchy", "sat_built_structure__built_structure_hierarchy__membership"
    sat_p, sat_s = sats_of(P, nodes, edges), sats_of(S, nodes, edges)
    sat_p = [n for n in sat_p if n not in (chain_sat,)]
    sat_s = [n for n in sat_s if n not in (hier_sat,)]

    def place(name, x, y):
        B[name].x, B[name].y = x, y
        return y + B[name].h

    def stack_h(names, gap):
        return sum(B[n].h for n in names) + gap * (len(names) - 1)

    def pair_line(link, sat):
        fl, fs = _pair_x(B[link], B[sat])
        _line(L, sat, link, (fs, 0.0), (fl, 1.0))

    # ownership by a Party, at the top, left-aligned at xR, the Satellite under its Link
    y = y0
    for key in ("po", "so"):
        link, sat = pairs[key]
        y = place(link, xR, y) + 110
        y = place(sat, xR, y) + 170
    y_own_end = y - 170
    xr2 = max(B[n].x + B[n].w for k in ("po", "so") for n in pairs[k])
    # the groups of the two Hubs
    def right_rows(keys, top, height):
        rows_h = sum(B[pairs[k][0]].h + 110 + B[pairs[k][1]].h for k in keys) + 130 * (len(keys) - 1)
        yy = top + (height - rows_h) / 2
        for k in keys:
            link, sat = pairs[k]
            yy = place(link, xr2 - B[link].w, yy) + 110
            yy = place(sat, xr2 - B[sat].w, yy) + 130
    right_h = lambda keys: sum(B[pairs[k][0]].h + 110 + B[pairs[k][1]].h for k in keys) + 130 * (len(keys) - 1)  # noqa: E731

    # parcel
    hubp, hubs = B[P], B[S]
    hp = max(stack_h(sat_p, GAP_ROW), right_h(("pl", "pg")))
    top_p = y_own_end + 260
    hubp.h = hp
    hubp.x, hubp.y = xM + wM - hubp.w, top_p
    yy = top_p + (hp - stack_h(sat_p, GAP_ROW)) / 2
    for n in sat_p:
        yy = place(n, xL + wL - B[n].w, yy) + GAP_ROW
    right_rows(("pl", "pg"), top_p, hp)
    # the Link between the two Hubs, its Satellite on its left
    cl, cs = B[chain_link], B[chain_sat]
    cl.x, cl.y = xM + wM - cl.w, top_p + hp + 110
    cs.x, cs.y = xL + wL - cs.w, cl.y + (cl.h - cs.h) / 2
    # structure
    hl, hs_ = B[hier], B[hier_sat]
    left_s = stack_h(sat_s, GAP_ROW) + 110 + hl.h + 110 + hs_.h
    top_s = cl.y + cl.h + 110
    hh = max(left_s, right_h(("sl", "sg")))
    hubs.h = hh
    hubs.x, hubs.y = xM + wM - hubs.w, top_s
    yy = top_s + (hh - left_s) / 2
    for n in sat_s:
        yy = place(n, xL + wL - B[n].w, yy) + GAP_ROW
    hl_top = yy - GAP_ROW + 110
    place(hier, xL + wL - hl.w, hl_top)
    place(hier_sat, xL + wL - hs_.w, hl_top + hl.h + 110)
    right_rows(("sl", "sg"), top_s, hh)

    # ---- lines
    for hub, sats in ((hubp, sat_p), (hubs, sat_s)):
        for n in sats:
            _line(L, n, hub.name, (1.0, 0.5), (0.0, _frac(hub, B[n].cy)))
    _line(L, chain_sat, chain_link, (1.0, 0.5), (0.0, 0.5))
    _line(L, chain_link, P, (0.5, 0.0), (0.5, 1.0))
    _line(L, chain_link, S, (0.5, 1.0), (0.5, 0.0))
    _line(L, hier_sat, hier, *( (( _pair_x(hl, hs_)[1], 0.0), (_pair_x(hl, hs_)[0], 1.0)) ))
    _line(L, hier, S, (1.0, 0.3), (0.0, _frac(hubs, hl.y + 0.3 * hl.h)))
    _line(L, hier, S, (1.0, 0.7), (0.0, _frac(hubs, hl.y + 0.7 * hl.h)))
    for key in pairs:
        pair_line(*pairs[key])
    # the Links to the Hub of their own kind: level lines along the rows, the ownership Links from above
    for key, hub in (("pl", hubp), ("pg", hubp), ("sl", hubs), ("sg", hubs)):
        link = B[pairs[key][0]]
        _line(L, link.name, hub.name, (0.0, 0.5), (1.0, _frac(hub, link.cy)))
    _line(L, pairs["po"][0], P, (0.0, 0.3), (1.0, 0.03))
    _line(L, pairs["so"][0], S, (0.0, 0.3), (1.0, 0.03))
    # the Links to the Hubs defined on other pages
    _line(L, pairs["po"][0], "hub_party", (0.0, 0.6), (1.0, 0.93))
    _line(L, pairs["so"][0], "hub_party", (0.0, 0.6), (1.0, 0.98))
    _line(L, pairs["pl"][0], "hub_location", (1.0, 0.5), (0.35, 1.0))
    _line(L, pairs["sl"][0], "hub_location", (1.0, 0.5), (0.65, 1.0))
    _line(L, pairs["pg"][0], GA, (1.0, 0.5), (0.0, 0.3))
    _line(L, pairs["sg"][0], GA, (1.0, 0.5), (0.0, 0.7))
    bottom = max(hubs.y + hubs.h, hs_.y + hs_.h, max(B[pairs[k][1]].y + B[pairs[k][1]].h for k in pairs))
    gov_mid = (B[pairs["pg"][0]].cy + B[pairs["sg"][0]].cy) / 2
    return bottom, gov_mid


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
    np_loc, np_loc_sat = "lnk_location__natural_person", "sat_location__natural_person__usage"
    le_loc, le_loc_sat = "lnk_legal_entity__location", "sat_legal_entity__location__usage"
    party_sat = "sat_party__sensitivity"
    hier_link, hier_sat = "lnk_legal_entity__legal_entity_hierarchy", "sat_legal_entity__legal_entity_hierarchy__membership"

    def width(names):
        return max(L.boxes[n].w for n in names)

    imm_left = (sats_of("hub_base_parcel", nodes, edges) + sats_of("hub_built_structure", nodes, edges)
                + ["lnk_built_structure__built_structure_hierarchy", "sat_built_structure__built_structure_hierarchy__membership",
                   "sat_base_parcel__built_structure__period"])
    wL = width(np_singles + rep + [link_np_name, hier_link, hier_sat] + imm_left)
    wM = width(chain + [rel_link, "hub_base_parcel", "hub_built_structure", "lnk_base_parcel__built_structure"])
    wR = width(np_pairs + le_sats + [own_link, rel_sat, np_loc, np_loc_sat, le_loc, le_loc_sat, party_sat])
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

    y = hub_np.y + hub_np.h + GAP_CHAIN + 140     # room for the line of the place of a person, which comes up to the Hub from the east
    for n in chain[1:4]:
        b = L.boxes[n]
        b.x, b.y = xM + (wM - b.w) / 2, y
        y += b.h + GAP_CHAIN
    hub_le = L.boxes["hub_legal_entity"]
    hub_le.x = xM + (wM - hub_le.w) / 2
    # the column east of the chain, top to bottom: the Link of a person to its place and its Satellite, the sensitivity of the
    # party, the ownership group, the Link of an entity to its place and its Satellite, then the entity Satellites.
    # The Location cluster sits east of the ownership group, its Hub on the height of the ownership line, so the line of the
    # person comes down to it from above and the line of the entity comes up to it from below.
    nl, ns = L.boxes[np_loc], L.boxes[np_loc_sat]
    ps = L.boxes[party_sat]

    def column(box, y):
        box.x, box.y = xR, y
        return y + box.h

    y_col = column(nl, bottom_r + 90) + 110
    y_col = column(ns, y_col) + 110
    y_col = column(ps, y_col) + 110
    ol, os_ = L.boxes[own_link], L.boxes[own_sat]
    ol.x, ol.y = xR, y_col
    os_.x, os_.y = xS, ol.y + (ol.h - os_.h) / 2
    _line(L, own_sat, own_link, (0.0, 0.5), (1.0, 0.5))
    _line(L, own_link, "hub_party", (0.0, 0.3), (1.0, 0.9))
    _line(L, own_link, "hub_legal_entity", (0.0, 0.7), (1.0, 0.02))
    ll, ls = L.boxes[le_loc], L.boxes[le_loc_sat]
    y_col = column(ll, ol.y + ol.h + 110) + 110
    column(ls, y_col)
    loc_top, loc_bottom, loc_right = _location_block(L, nodes, edges, xS + wS + GAP_X * 1.5, ol.y + ol.h / 2)
    _line(L, np_loc_sat, np_loc, ((nl.cx - ns.x) / ns.w, 0.0), (0.5, 1.0))
    _line(L, np_loc, "hub_natural_person", (0.0, 0.5), (1.0, 0.985))
    _line(L, np_loc, "hub_location", (1.0, 0.5), (0.0, 0.1))
    _line(L, party_sat, "hub_party", (0.0, 0.5), (1.0, 0.3))
    _line(L, le_loc_sat, le_loc, ((ll.cx - ls.x) / ls.w, 0.0), (0.5, 1.0))
    _line(L, le_loc, "hub_legal_entity", (0.0, 0.5), (1.0, 0.06))
    _line(L, le_loc, "hub_location", (1.0, 0.5), (0.0, 0.9))
    le_top = max(ls.y + ls.h + 90, y + hub_le.h / 2 - ((len(le_sats) * 140) / 2))
    le_bottom = _stack(L, le_sats, xR, le_top, wR, "left")
    hub_le.y = max((le_top + le_bottom) / 2 - hub_le.h / 2, y)
    # the line from the ownership Link to hub_party leaves its right edge and must pass east of this Link
    lel = L.boxes["lnk_legal_entity__party"]
    lel.y = hub_le.y - GAP_CHAIN - 220 - lel.h      # the ownership line comes down steeply from the east
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

    # the grouping of legal entities: its Link left of the Legal Entity Hub, below the lines of the representation Link,
    # and its Satellite under it. Both lines to the Hub leave from the right edge of the Link.
    hl, hs = L.boxes[hier_link], L.boxes[hier_sat]
    hl.x = xL + wL - hl.w
    hl.y = hub_le.y + hub_le.h * 0.5
    hs.x = xL + wL - hs.w
    hs.y = hl.y + hl.h + 110
    _line(L, hier_link, "hub_legal_entity", (1.0, 0.3), (0.0, 0.65))
    _line(L, hier_link, "hub_legal_entity", (1.0, 0.7), (0.0, 0.9))
    _line(L, hier_sat, hier_link, (0.5, 0.0), (0.5, 1.0))

    _line(L, "lnk_natural_person__party", "hub_natural_person", (0.5, 0.0), (0.5, 1.0))
    _line(L, "lnk_natural_person__party", "hub_party", (0.5, 1.0), (0.5, 0.0))
    _line(L, "lnk_legal_entity__party", "hub_party", (0.5, 0.0), (0.5, 1.0))
    _line(L, "lnk_legal_entity__party", "hub_legal_entity", (0.5, 1.0), (0.5, 0.0))

    base_bottom = max(le_bottom, hub_le.y + hub_le.h, link_np.y + link_np.h, ol.y + ol.h, hs.y + hs.h, loc_bottom)
    imm_bottom, gov_mid = _immovable_block(L, nodes, edges, {"xL": xL, "wL": wL, "xM": xM, "wM": wM, "xR": xR}, base_bottom + 260)
    reg_bottom = max(base_bottom, imm_bottom) + BAND_PAD
    reg_w = max(reg_w, loc_right + BAND_PAD)
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
    ga = L.boxes["hub_government_authority"]
    ga.h = max(ga.h, 300)
    ga.x, ga.y = pxM + (pw_M - ga.w) / 2, gov_mid - ga.h / 2
    plat_bottom = max(lc_bottom, hlc.y + hlc.h, ga.y + ga.h) + BAND_PAD
    L.bands.append({"title": "Platform", "x": px, "y": by, "w": plat_w, "h": plat_bottom - by})
    L.legend_y = max(reg_bottom, plat_bottom) + 60
    L.uses = pu.uses_lines(nodes)
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


def edge_position(box: Box, toward: Box) -> tuple[float, float]:
    """Where the straight line from the centre of `box` to the centre of `toward` leaves `box`, as fractions of its size."""
    dx, dy = toward.cx - box.cx, toward.cy - box.cy
    if dx == 0 and dy == 0:
        return 0.5, 0.5
    scale = min((box.w / 2) / abs(dx) if dx else math.inf, (box.h / 2) / abs(dy) if dy else math.inf)
    return round(0.5 + dx * scale / box.w, 4), round(0.5 + dy * scale / box.h, 4)


def short_ids(L: Layout) -> dict[str, str]:
    """Lucid rejects long shape ids (a 49 character id failed the import), so each object gets a short one."""
    return {name: f"n{i}" for i, name in enumerate(L.boxes, 1)}


def to_spec(L: Layout, title: str = "PSS Data Objects") -> dict:
    ids = short_ids(L)
    shapes: list[dict] = []
    for band in L.bands:
        shapes.append({
            "id": band.get("id", "band_" + band["title"].lower()),
            "type": "roundedRectangleContainer",
            "boundingBox": {"x": round(band["x"], 1), "y": round(band["y"], 1), "w": round(band["w"], 1), "h": round(band["h"], 1)},
            "containerTitle": {"text": band.get("label", band["title"] + " (owner domain)")},
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
    for i, (src, user) in enumerate(L.uses, 1):
        s, u = L.boxes[src], L.boxes[user]
        sx, sy = edge_position(s, u)
        ux, uy = edge_position(u, s)
        lines.append({
            "id": f"u{i}",
            "lineType": "straight",
            "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[src], "position": {"x": sx, "y": sy}},
            "endpoint2": {"type": "shapeEndpoint", "style": "none", "shapeId": ids[user], "position": {"x": ux, "y": uy}},
            "stroke": {"color": USES_COLOR, "width": 1, "style": "dashed"},
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
    for label in ("Gray dashed line from hub_code_list: the object has a column whose values come from a Code List",
                  "Gray dashed line from hub_load_configuration: the Load Configuration decides which Satellite of the pair is loaded"):
        shapes.append({
            "id": f"legend_uses_box_{len([s for s in shapes if s['id'].startswith('legend_uses_box')])}", "type": "rectangle",
            "boundingBox": {"x": 60.0, "y": ly + 100 + 46 * len([s for s in shapes if s["id"].startswith("legend_uses_box")]), "w": 60, "h": 12},
            "style": {"fill": {"type": "color", "color": "#FFFFFF"}, "stroke": {"color": USES_COLOR, "width": 2, "style": "dashed"}},
        })
        shapes.append({
            "id": f"legend_uses_text_{len([s for s in shapes if s['id'].startswith('legend_uses_text')])}", "type": "text",
            "boundingBox": {"x": 132.0, "y": ly + 88 + 46 * len([s for s in shapes if s["id"].startswith("legend_uses_text")]), "w": 1800, "h": 36},
            "text": f'<p style="font-size:10pt;text-align:left">{label}</p>',
        })
    shapes.append({
        "id": "legend_note", "type": "text",
        "boundingBox": {"x": 60, "y": ly + 50, "w": 2400, "h": 36},
        "text": f'<p style="font-size:9pt;text-align:left">Arrows run from the child to its parent. A dashed line joins the two Satellites of a twin pair. {"The grain of each object, one row per ..., is" if SIMPLIFIED else "The definition of each object is"} written in its box.</p>',
    })
    return {"version": 1, "pages": [{"id": "page1", "title": title, "shapes": shapes, "lines": lines}]}


def main(argv: list[str]) -> int:
    global SIMPLIFIED
    SIMPLIFIED = "--simplified" in argv
    args = [a for a in argv if not a.startswith("--")]
    out = Path(args[0]) if args else Path("lucid_global.json")
    nodes, edges = load_all()
    L = build_layout(nodes, edges)
    out.write_text(json.dumps(to_spec(L), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", out, f"({len(L.boxes)} boxes, {len(L.lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
