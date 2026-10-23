"""Place the Hubs, Links and Satellites of the simplified graph.

The structure is hub and spoke: Hubs and Links form a skeleton, and each Satellite hangs off one of them. So the
skeleton is placed first with a force-directed layout (networkx `spring_layout`, Fruchterman-Reingold), the Satellites
are fanned out in the free angles around their parent, and each name is put in the free spot around its shape. The
skeleton is spread out (dilated) until nothing overlaps (the smallest such scale, found by bisection), and of the several
fixed seeds the smallest picture is kept among those with at most CROSSING_TOLERANCE crossings more than the best one.
The spacing is set by EDGE_LENGTH, SCALES, FAN_SPREAD and CROSSING_TOLERANCE; the Hub is twice the size of a Link.
Everything is deterministic: the same pages give the same picture.

No Lucid here: positions in, positions out. `build_lucid_graph.py` writes the Lucid JSON.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

try:
    import networkx as nx
except ImportError:  # pragma: no cover - reported by the caller
    nx = None

# ---------------------------------------------------------------- sizes, from the hand-drawn Lucid graph
SIZE = {"Hub": (160.0, 160.0), "Link": (80.0, 80.0), "Satellite": (92.376, 69.282)}   # the Hub is twice the Link: the shape that stands out
LABEL_H = {"Hub": 37.701, "Link": 27.632, "Satellite": 27.632}
LABEL_CHAR = {"Hub": 15.1, "Link": 9.6, "Satellite": 9.6}   # width of a character: 11 pt bold and 7 pt Liberation Mono
LABEL_GAP = 6.0
PAD = 8.0                  # clear space asked between two shapes
EDGE_LENGTH = 430.0        # mean length of a skeleton edge at scale 1
SEEDS = tuple(range(24))
SCALES = tuple(round(0.5 * 1.07 ** i, 3) for i in range(40))     # from 0.5 to about 7.4: how far the skeleton is spread
FAN_SPREAD = 1.0           # the Satellites of a shape sit at a fixed distance from it, not at one that grows with the scale
CROSSING_TOLERANCE = 2     # of the layouts with at most this many crossings more than the best one, the smallest is kept
COMPONENT_GAP = 220.0
MARGIN = 80.0


def label_size(kind: str, name: str) -> tuple[float, float]:
    return LABEL_CHAR[kind] * len(name) + 6.0, LABEL_H[kind]


@dataclass
class Placed:
    name: str
    kind: str
    in_place: bool
    x: float = 0.0            # centre
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    lx: float = 0.0           # label centre
    ly: float = 0.0
    lw: float = 0.0
    lh: float = 0.0
    align: str = "center"     # text alignment inside the label block

    @property
    def rect(self) -> tuple[float, float, float, float]:
        return self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2

    @property
    def label_rect(self) -> tuple[float, float, float, float]:
        return self.lx - self.lw / 2, self.ly - self.lh / 2, self.lx + self.lw / 2, self.ly + self.lh / 2


@dataclass
class GraphLayout:
    items: dict[str, Placed] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)      # (child, parent), one per pair
    crossings: int = 0
    overlaps: int = 0
    label_hits: int = 0


# ---------------------------------------------------------------- geometry
def _overlap(a, b, pad: float = 0.0) -> bool:
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def _ccw(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _cross(p1, p2, p3, p4) -> bool:
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return d1 * d2 < 0 and d3 * d4 < 0


def _segment_hits(p1, p2, rect, shrink: float = 0.0) -> bool:
    """Liang-Barsky: does the segment pass through the rectangle (shrunk by `shrink` on every side)?"""
    x0, y0, x1, y1 = rect[0] + shrink, rect[1] + shrink, rect[2] - shrink, rect[3] - shrink
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p1[0] - x0), (dx, x1 - p1[0]), (-dy, p1[1] - y0), (dy, y1 - p1[1])):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


# ---------------------------------------------------------------- one component at one seed and scale
def _fan_satellites(centre, radius, neighbours, sats, spread: float):
    """Angles for `sats` around `centre`: in the largest free gaps between the lines to `neighbours`, growing the
    radius until they fit. Returns [(x, y)] in the order of `sats`."""
    m = len(sats)
    if m == 0:
        return []
    angles = sorted(math.atan2(n[1] - centre[1], n[0] - centre[0]) for n in neighbours)
    if not angles:
        gaps = [(-math.pi, 2 * math.pi)]
    elif len(angles) == 1:
        gaps = [(angles[0], 2 * math.pi)]
    else:
        gaps = [(angles[i], (angles[(i + 1) % len(angles)] - angles[i]) % (2 * math.pi) or 2 * math.pi) for i in range(len(angles))]
    r = (radius + 45 + SIZE["Satellite"][0] / 2) * spread
    while True:
        half = math.asin(min(0.99, 64 / r))
        margin = math.asin(min(0.99, 78 / r)) if angles else 0.0
        capacity = [max(0, int((g - 2 * margin) / (2 * half)) + 1) if g - 2 * margin >= 0 else 0 for _, g in gaps]
        if sum(capacity) >= m:
            break
        r += 24
    take = [0] * len(gaps)
    left = m
    for i in sorted(range(len(gaps)), key=lambda i: -gaps[i][1]):
        take[i] = min(capacity[i], left)
        left -= take[i]
    out = []
    for i, (start, g) in enumerate(gaps):
        k = take[i]
        if not k:
            continue
        spacing = 0.0 if k == 1 else min(2 * half * 1.5, (g - 2 * margin) / (k - 1))
        mid = start + g / 2
        for j in range(k):
            a = mid + (j - (k - 1) / 2) * spacing
            out.append((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)))
    return out


def _gap_candidates(p: Placed, incident: list[float]):
    """Label spots in the middle of the free angles between the lines that leave the shape (the largest four)."""
    if not incident:
        return []
    angles = sorted(incident)
    gaps = [(angles[i], (angles[(i + 1) % len(angles)] - angles[i]) % (2 * math.pi) or 2 * math.pi) for i in range(len(angles))]
    out = []
    for start, size in sorted(gaps, key=lambda g_: -g_[1])[:4]:
        a = start + size / 2
        ux, uy = math.cos(a), math.sin(a)
        hw, hh = p.w / 2 + LABEL_GAP, p.h / 2 + LABEL_GAP
        t = min((hw + p.lw / 2) / abs(ux) if abs(ux) > 1e-6 else math.inf, (hh + p.lh / 2) / abs(uy) if abs(uy) > 1e-6 else math.inf)
        out.append((p.x + ux * t, p.y + uy * t, "left" if ux > 0.35 else "right" if ux < -0.35 else "center"))
    return out


def _label_candidates(p: Placed, incident: list[float] | None = None):
    x0, y0, x1, y1 = p.rect
    cx, cy, lw, lh = p.x, p.y, p.lw, p.lh
    g = LABEL_GAP
    return _gap_candidates(p, incident or []) + [  # (label centre x, y, text alignment)
        (x1 + g + lw / 2, cy, "left"),
        (x0 - g - lw / 2, cy, "right"),
        (cx, y0 - g - lh / 2, "center"),
        (cx, y1 + g + lh / 2, "center"),
        (cx + lw / 2, y0 - g - lh / 2, "left"),
        (cx - lw / 2, y0 - g - lh / 2, "right"),
        (cx + lw / 2, y1 + g + lh / 2, "left"),
        (cx - lw / 2, y1 + g + lh / 2, "right"),
    ]


def _place_labels(items: dict[str, Placed], segs: list[tuple[str, str]]) -> None:
    """Greedy, hubs first, then two refinement rounds: each label takes the free spot with the fewest clashes."""
    order = sorted(items, key=lambda n: (items[n].kind != "Hub", items[n].kind != "Link", n))
    lines = [((items[a].x, items[a].y), (items[b].x, items[b].y), a, b) for a, b in segs]
    chosen: dict[str, tuple] = {}
    incident: dict[str, list[float]] = {n: [] for n in items}
    for a, b in segs:
        pa, pb = items[a], items[b]
        incident[a].append(math.atan2(pb.y - pa.y, pb.x - pa.x))
        incident[b].append(math.atan2(pa.y - pb.y, pa.x - pb.x))

    def cost(name: str, cand) -> float:
        p = items[name]
        rect = (cand[0] - p.lw / 2, cand[1] - p.lh / 2, cand[0] + p.lw / 2, cand[1] + p.lh / 2)
        c = 0.0
        for n, q in items.items():
            if _overlap(rect, q.rect, PAD):
                c += 1000
            if n != name and n in chosen and _overlap(rect, (chosen[n][0] - q.lw / 2, chosen[n][1] - q.lh / 2,
                                                              chosen[n][0] + q.lw / 2, chosen[n][1] + q.lh / 2), 2):
                c += 1000
        for p1, p2, a, b in lines:
            if _segment_hits(p1, p2, rect):
                c += 250
        return c

    for round_ in range(2):
        for name in order:
            p = items[name]
            cands = _label_candidates(p, incident[name])
            best = min(range(len(cands)), key=lambda i: (cost(name, cands[i]), i))
            chosen[name] = cands[best]
    for name, (lx, ly, align) in chosen.items():
        p = items[name]
        p.lx, p.ly, p.align = lx, ly, align


def _metrics(items: dict[str, Placed], segs: list[tuple[str, str]]) -> tuple[int, int, int]:
    """(overlaps, crossings, label hits): shapes or names that touch, or a line through a shape; lines that cross; lines that
    run through a name (allowed, but fewer is better)."""
    overlaps = label_hits = 0
    names = list(items)
    rects = {n: items[n].rect for n in names}
    labels = {n: items[n].label_rect for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            overlaps += _overlap(rects[a], rects[b], PAD) + _overlap(labels[a], labels[b], 2) \
                + _overlap(labels[a], rects[b], 2) + _overlap(labels[b], rects[a], 2)
        overlaps += _overlap(labels[a], rects[a], 0)
    pts = [((items[a].x, items[a].y), (items[b].x, items[b].y), a, b) for a, b in segs]
    for p1, p2, a, b in pts:
        for n in names:
            if n not in (a, b) and _segment_hits(p1, p2, rects[n], 3):
                overlaps += 1
            if _segment_hits(p1, p2, labels[n]):
                label_hits += 1
    crossings = 0
    for i, (p1, p2, a, b) in enumerate(pts):
        for q1, q2, c, d in pts[i + 1:]:
            if {a, b} & {c, d}:
                continue
            crossings += _cross(p1, p2, q1, q2)
    return overlaps, crossings, label_hits


def _skeleton(skeleton, edges, seed: int):
    """The force-directed layout of the skeleton at one seed, with a mean edge length of 1 (cached by the caller)."""
    G = nx.Graph()
    G.add_nodes_from(sorted(skeleton))      # a set iterates in hash order, which changes from run to run
    G.add_edges_from((a, b) for a, b in edges if a in skeleton and b in skeleton)
    if len(G) == 1:
        return G, {next(iter(G)): (0.0, 0.0)}
    raw = nx.spring_layout(G, seed=seed, iterations=300, scale=1.0)
    lengths = [math.dist(raw[a], raw[b]) for a, b in G.edges] or [1.0]
    mean = sum(lengths) / len(lengths)
    return G, {n: (raw[n][0] / mean, raw[n][1] / mean) for n in G}


def _layout_component(kinds, in_place, G, unit, sats_of, scale: float) -> dict[str, Placed]:
    """Positions of one connected component: the skeleton scaled up, the Satellites in the free angles."""
    pos = {n: (x * EDGE_LENGTH * scale, y * EDGE_LENGTH * scale) for n, (x, y) in unit.items()}
    items: dict[str, Placed] = {}

    def add(name, x, y):
        w, h = SIZE[kinds[name]]
        lw, lh = label_size(kinds[name], name)
        items[name] = Placed(name, kinds[name], in_place.get(name, False), x, y, w, h, lw=lw, lh=lh)

    for n, (x, y) in pos.items():
        add(n, x, y)
    for n in sorted(pos):
        near = [pos[m] for m in G.neighbors(n)]
        radius = SIZE[kinds[n]][0] / 2
        spots = _fan_satellites(pos[n], radius, near, sats_of.get(n, []), FAN_SPREAD)
        for s, (x, y) in zip(sats_of.get(n, []), spots):
            add(s, x, y)
    return items


def _component_edges(members: set[str], edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(a, b) for a, b in edges if a in members and b in members]


def layout(kinds: dict[str, str], in_place: dict[str, bool], edges: list[tuple[str, str]], sat_order: list[str]) -> GraphLayout:
    """`kinds` name -> Hub, Link or Satellite; `edges` (child, parent) of the structure; `sat_order` the order in which
    Satellites are fanned (a history Satellite right before its in-place twin)."""
    if nx is None:
        raise SystemExit("networkx is not installed: pip install -r .claude/skills/business-object-page/requirements.txt")
    pairs = list(dict.fromkeys(edges))
    parent_of = {a: b for a, b in pairs if kinds[a] == "Satellite"}
    sats_of: dict[str, list[str]] = {}
    for s in sat_order:
        if s in parent_of:
            sats_of.setdefault(parent_of[s], []).append(s)
    skeleton_nodes = [n for n in kinds if kinds[n] != "Satellite"]
    skeleton_edges = [(a, b) for a, b in pairs if kinds[a] != "Satellite"]
    G = nx.Graph()
    G.add_nodes_from(skeleton_nodes)
    G.add_edges_from(skeleton_edges)
    components = sorted((set(c) for c in nx.connected_components(G)), key=lambda c: (-len(c), sorted(c)[0]))
    placed: list[tuple[dict[str, Placed], list[tuple[str, str]], int, int]] = []
    for comp in components:
        members = set(comp) | {s for n in comp for s in sats_of.get(n, [])}
        segs = _component_edges(members, pairs)
        candidates = []
        for seed in SEEDS:
            G_c, unit = _skeleton(comp, skeleton_edges, seed)

            def attempt(scale):
                items = _layout_component(kinds, in_place, G_c, unit, sats_of, scale)
                if any(_overlap(a.rect, b.rect, PAD) for i, a in enumerate(items.values()) for b in list(items.values())[i + 1:]):
                    return None      # shapes touch: spread the skeleton out before spending time on the names
                _place_labels(items, segs)
                overlaps, crossings, label_hits = _metrics(items, segs)
                return (items, overlaps, crossings, label_hits) if overlaps == 0 else None

            # the smallest scale without overlaps, by bisection (a larger scale never makes shapes touch)
            found = attempt(SCALES[-1])
            if found is None:
                continue
            lo, hi = 0, len(SCALES) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                r = attempt(SCALES[mid])
                if r is not None:
                    found, hi = r, mid
                else:
                    lo = mid + 1
            items, overlaps, crossings, label_hits = found
            xs = [v for p in items.values() for v in (p.rect[0], p.rect[2], p.label_rect[0], p.label_rect[2])]
            ys = [v for p in items.values() for v in (p.rect[1], p.rect[3], p.label_rect[1], p.label_rect[3])]
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            candidates.append((crossings, label_hits, area, items, overlaps))
        if not candidates:
            raise SystemExit("no layout without overlaps found; raise SCALES")
        fewest = min(c[0] for c in candidates)
        eligible = [c for c in candidates if c[0] <= fewest + CROSSING_TOLERANCE]
        crossings, label_hits, area, items, overlaps = min(eligible, key=lambda c: (c[2], c[0], c[1]))
        best = (None, items, overlaps, crossings, label_hits)
        placed.append((best[1], segs, best[2], best[3], best[4]))
    result = GraphLayout()
    x_cursor, y_cursor = MARGIN, MARGIN
    for index, (items, segs, overlaps, crossings, label_hits) in enumerate(placed):
        x0 = min(min(p.rect[0], p.label_rect[0]) for p in items.values())
        y0 = min(min(p.rect[1], p.label_rect[1]) for p in items.values())
        x1 = max(max(p.rect[2], p.label_rect[2]) for p in items.values())
        y1 = max(max(p.rect[3], p.label_rect[3]) for p in items.values())
        if index == 0:
            dx, dy = MARGIN - x0, MARGIN - y0
            x_cursor = MARGIN + (x1 - x0) + COMPONENT_GAP
        else:
            dx, dy = x_cursor - x0, y_cursor - y0
            y_cursor += (y1 - y0) + COMPONENT_GAP
        for p in items.values():
            p.x, p.y, p.lx, p.ly = p.x + dx, p.y + dy, p.lx + dx, p.ly + dy
        result.items.update(items)
        result.edges.extend(segs)
        result.crossings += crossings
        result.overlaps += overlaps
        result.label_hits += label_hits
    return result
