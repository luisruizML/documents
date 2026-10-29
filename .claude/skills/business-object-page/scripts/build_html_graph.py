"""Build the interactive graph of the Business Objects: one self-contained HTML file (inline SVG and JavaScript, no
server, no external file) that shows the same picture as the Lucid graph. The right panel lists the Hubs, then the Links,
then the Satellites; clicking one fades everything but the objects directly related to it and opens the Vault Info
panel on the left (Definition, Grain, Business key, Fields).

    python build_html_graph.py [out.html]

The layout is the one of `graph_layout.py` and the texts are read from the pages, so the file cannot drift from them.
It is kept in the repository only; nothing here talks to Confluence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_diagram as bd  # noqa: E402
import build_lucid_global as g  # noqa: E402
import build_lucid_graph as lg  # noqa: E402
import validate_page as vp  # noqa: E402

REPO = HERE.parents[3]
PAGES_DIR = REPO / "Rosetta" / "Business_Objects"
TEMPLATE = HERE.parent / "assets" / "graph_template.html"
DEFAULT_OUT = PAGES_DIR / "html" / "Vault_Graph.html"
MARKER = "/*DATA*/null"
KIND_ORDER = {"Hub": 0, "Link": 1, "Satellite": 2}


# The areas drawn behind the picture: name, fill colour, ink colour of its name, radius of the blob around each object, and the
# pages whose Vault objects belong to it. "Assets" surrounds the two kinds of asset, so its blob is wider. The first areas are
# drawn first, so they are at the back.
AREAS = [
    ("Assets", "#F2C94C", "#7A5F00", 470, ["Base Parcel", "Built Structure", "Base Asset", "Swappable Component", "Model Catalog"]),
    ("Immovable Assets", "#F2994A", "#8A4A0F", 290, ["Base Parcel", "Built Structure"]),
    ("Movable Assets", "#6FCF97", "#1F6B40", 290, ["Base Asset", "Swappable Component", "Model Catalog"]),
    ("Parties", "#4F9DDE", "#1B4F80", 380, ["Party", "Natural Person", "Legal Entity"]),
    ("Natural Persons", "#6C63E0", "#2F2A8C", 240, ["Natural Person"]),
    ("Legal Entities", "#C75FB4", "#7A1F68", 240, ["Legal Entity"]),
    ("Legal", "#EB5757", "#8F1F1F", 290, ["Entitlement", "Credential", "RRR"]),
    ("Contact Point", "#A67C52", "#5E4126", 290, ["Contact Point"]),
    ("Location", "#2BB5A8", "#145F58", 290, ["Location"]),
    ("Platform", "#9AA5B1", "#44505C", 290, ["Code List", "Load Configuration"]),
]


def areas_of(items: list[dict], edges: list[list[int]]) -> list[dict]:
    """`[{name, color, ink, radius, items, edges}]`: the objects of each area and the lines between them. The blob is drawn by the page
    as a circle around each object and a thick line along each of these lines, so it follows the objects and does not cover the gaps."""
    out = []
    for name, color, ink, radius, pages in AREAS:
        inside = {i for i, it in enumerate(items) if it["page"] in pages}
        if not inside:
            continue
        # a Link that reaches a Hub of the area belongs to it too, whatever its page, and so do the Satellites of that Link:
        # this is how the area of the Parties holds the Link and the Satellite that tie an Entitlement or an RRR to a Party
        hubs = {i for i in inside if items[i]["kind"] == "Hub"}
        inside |= {c for c, p in edges if items[c]["kind"] == "Link" and p in hubs}
        inside |= {c for c, p in edges if items[c]["kind"] == "Satellite" and p in inside}
        members = sorted(inside)
        out.append({"name": name, "color": color, "ink": ink, "radius": radius, "items": members,
                    "edges": [k for k, (a, b) in enumerate(edges) if a in inside and b in inside]})
    return out


def page_title(stem: str) -> str:
    return stem.replace("_", " ")


def vault_rows(pages_dir: Path = PAGES_DIR) -> dict[str, dict]:
    """`{vault object: {page, business_key}}` from the Vault objects table of each page."""
    out: dict[str, dict] = {}
    for stem in g.PAGES:
        page = vp.parse_page((pages_dir / f"{stem}.md").read_text(encoding="utf-8"))
        tables = page.tables("Vault objects")
        for row in tables[0] if tables else []:
            name = bd._clean(row.get("Name", ""))
            out.setdefault(name, {"page": page_title(stem), "business_key": bd._clean(row.get("Business key", "")),
                                  "definition": bd._clean(row.get("Definition", ""))})
    return out


def code_list_examples(pages_dir: Path = PAGES_DIR) -> dict[str, dict]:
    """`{"<vault table>.<column>": {where, why, examples}}` from the Code List table "Which code columns are values of a
    Code List", the texts as written on the page."""
    rows = vp.code_list_table((pages_dir / "Code_List.md").read_text(encoding="utf-8"))
    return {key: {"where": cells[1], "why": cells[2], "examples": cells[3]} for key, cells in rows.items()}


def code_lists_of(name: str, fields: list[dict], examples: dict[str, dict]) -> list[dict]:
    """The fields of `name` that are linked to the Code List, each with where its values live and examples."""
    out = []
    for f in fields:
        flag = f.get("Code List", "—")
        row = examples.get(f"{name}.{f.get('Column', '')}")
        if flag in ("List", "Closed") and row:
            out.append({"column": f["Column"], "flag": flag, **row})
    return out


def focus_of(name: str, kinds: dict[str, str], edges: list[tuple[str, str]]) -> dict:
    """What stays visible when `name` is selected: the objects directly related to it, and when one of those is a Link,
    the Satellites of that Link. For a Hub, the Hubs on the other side of each of its Links are visible too, with the
    line of the Link to them. `edges` are the indexes of the lines drawn between the visible objects that belong to
    the selection (the lines of the selected object, the line of each such Link to its Satellites and, for a Hub, to
    the other Hubs)."""
    near = {name}
    for child, parent in edges:
        if child == name:
            near.add(parent)
        elif parent == name:
            near.add(child)
    visible = set(near)
    links = {n for n in near if n != name and kinds[n] == "Link"}
    for n in links:
        visible |= {c for c, p in edges if p == n and kinds[c] == "Satellite"}
    across = kinds[name] == "Hub"
    if across:
        for child, parent in edges:
            if child in links and kinds[parent] == "Hub":
                visible.add(parent)
    shown = []
    for i, (child, parent) in enumerate(edges):
        if child not in visible or parent not in visible:
            continue
        if (name in (child, parent) or (kinds[parent] == "Link" and kinds[child] == "Satellite" and parent in near)
                or (across and child in links and kinds[parent] == "Hub")):
            shown.append(i)
    return {"nodes": sorted(visible), "edges": shown}


def build_data(nodes=None, edges=None) -> dict:
    if nodes is None:
        nodes, edges = g.load_all()
    L, uses = lg.build(nodes, edges)
    meta = vault_rows()
    examples = code_list_examples()
    kinds = {n: p.kind for n, p in L.items.items()}
    order = sorted(L.items, key=lambda n: (KIND_ORDER[kinds[n]], n))
    xs = [v for p in L.items.values() for v in (p.rect[0], p.rect[2], p.label_rect[0], p.label_rect[2])]
    ys = [v for p in L.items.values() for v in (p.rect[1], p.rect[3], p.label_rect[1], p.label_rect[3])]
    items = []
    for name in order:
        p, node = L.items[name], nodes[name]
        fields = [{k: bd._clean(v) for k, v in r.items()} for r in (node.rows or [])]
        items.append({
            "name": name, "kind": p.kind, "inPlace": p.in_place,
            "x": round(p.x, 1), "y": round(p.y, 1), "w": round(p.w, 1), "h": round(p.h, 1),
            "lx": round(p.lx, 1), "ly": round(p.ly, 1), "lw": round(p.lw, 1), "lh": round(p.lh, 1), "align": p.align,
            "page": meta.get(name, {}).get("page", ""),
            "definition": meta.get(name, {}).get("definition") or node.definition, "grain": node.grain,
            "businessKey": meta.get(name, {}).get("business_key", ""),
            "fields": fields,
            "codeLists": code_lists_of(name, fields, examples),
        })
    index = {n: i for i, n in enumerate(order)}
    edge_list = [[index[c], index[p]] for c, p in L.edges]
    areas = areas_of(items, edge_list)
    reach = max([a["radius"] for a in areas] or [0]) - 60
    return {
        "items": items,
        "edges": edge_list,
        "areas": areas,
        "uses": [[index[a], index[b]] for a, b in uses],
        "focus": {n: {"nodes": [index[x] for x in f["nodes"]], "edges": f["edges"]}
                  for n in order for f in [focus_of(n, kinds, L.edges)]},
        "box": [round(min(xs) - 60 - reach, 1), round(min(ys) - 60 - reach, 1), round(max(xs) + 60 + reach, 1), round(max(ys) + 60 + reach, 1)],
        "charWidth": {"Hub": 15.1, "Link": 9.6, "Satellite": 9.6},
    }


def render(data: dict, template: Path = TEMPLATE) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.read_text(encoding="utf-8")
    assert MARKER in html, "the template has no data marker"
    return html.replace(MARKER, payload, 1)


def main(argv: list[str]) -> int:
    out = Path(argv[0]) if argv else DEFAULT_OUT
    data = build_data()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print(f"wrote {out} ({len(data['items'])} objects, {len(data['edges'])} lines, {out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
