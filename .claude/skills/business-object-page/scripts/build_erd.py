"""Build the full model of Business Object pages as the input of the Lucid ERD tool.

Lucid imports big hand-built tables unreliably (see build_lucid.py), but its ERD tool is made for many
entities with many columns. Each vault object becomes an entity, each hash key of a child becomes a
foreign key to its parent. The ERD shows name, type, nullability and PII; the descriptions stay on the page.

Usage:
    python build_erd.py out.json <page.md>[@ctx1,ctx2] [<page.md>[@ctx...] ...]
Then pass "entities" and "relationships" of out.json to lucid_create_erd.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_diagram as bd  # noqa: E402

KEY = {"◆": "PK", "◇": "FK"}


def _attribute(row: dict[str, str]) -> dict[str, str]:
    flags = ("" if row.get("Null") == "Yes" else " NOT NULL") + (" PII" if row.get("PII") == "Yes" else "")
    attr = {"name": row["Column"], "type": row["Type"] + flags}
    if row.get("Role") in KEY:
        attr["key"] = KEY[row["Role"]]
    elif row.get("Role") == "●":
        attr["key"] = "BK"
    return attr


def _external_attributes(name: str) -> list[dict[str, str]]:
    body = name.split("_", 1)[1]
    if name.startswith("hub_"):
        return [{"name": f"{body}_hk", "type": "string NOT NULL", "key": "PK"}]
    return [{"name": f"{p}_hk", "type": "string NOT NULL", "key": "FK"} for p in body.split("__")]


def build_erd(models: list[bd.Model]) -> dict:
    nodes: dict[str, bd.Node] = {}
    edges: list[bd.Edge] = []
    for m in models:
        for n in m.nodes:
            if n.name not in nodes or (nodes[n.name].external and not n.external):
                nodes[n.name] = n
        edges += [e for e in m.edges if e not in edges]
    entities = []
    for name, n in nodes.items():
        attrs = [_attribute(r) for r in n.rows] if n.rows else _external_attributes(name)
        entities.append({"id": name, "name": name, "attributes": attrs})
    relationships = []
    seen = set()
    for e in edges:
        if (e.child, e.parent) in seen:
            continue
        seen.add((e.child, e.parent))
        parent_hk = e.parent.split("_", 1)[1] + "_hk"
        relationships.append({
            "from": e.child, "to": e.parent, "fromAttribute": parent_hk, "toAttribute": parent_hk,
            "fromCardinality": "many", "toCardinality": "one",
        })
    return {"entities": entities, "relationships": relationships}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print(__doc__)
        return 2
    models = []
    for spec in args[1:]:
        path, _, ctx = spec.partition("@")
        models.append(bd.load_model(Path(path).read_text(encoding="utf-8"), [c for c in ctx.split(",") if c]))
    Path(args[0]).write_text(json.dumps(build_erd(models), ensure_ascii=False), encoding="utf-8")
    print("wrote", args[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
