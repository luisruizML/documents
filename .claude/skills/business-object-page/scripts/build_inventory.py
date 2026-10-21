"""Vault objects inventory: the Vault objects table of every Business Object page, split into one table per object
type, with Owner domain and Object as the two left columns. Prints Markdown; Rosetta/Business_Objects/Vault_Objects_Inventory.md
carries the result. On Confluence each table header takes the colour of its type (HEADER_FILL).

    python build_inventory.py [Rosetta/Business_Objects]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ORDER = ["Party", "Natural_Person", "Legal_Entity", "Code_List", "Load_Configuration"]
COLUMNS = ["Owner domain", "Object", "Name", "Definition", "Grain", "Business key"]

# (heading, fill, text) per type. Hub, Link and Satellite are the brand colours of section 3c; a Non-historized Link
# and a Satellite with row versioning are the 65 % tint of their parent colour.
TYPES = {
    "Hub": ("Hubs", "#3A0CA3", "#FFFFFF"),
    "Link": ("Links", "#45E3CD", "#000000"),
    "Non-historized Link": ("Non-historized Links", "#BEF5ED", "#000000"),
    "Satellite": ("Satellites", "#F72586", "#FFFFFF"),
    "Satellite with row versioning": ("Satellites with row versioning", "#FCB3D5", "#000000"),
}


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


def kind(type_: str, grain: str) -> str:
    return "Satellite with row versioning" if type_ == "Satellite" and "replaced in place" in grain else type_


def rows(folder: Path) -> dict[str, list[list[str]]]:
    """Rows [owner, object, name, grain, business key] grouped by type, in page order."""
    out: dict[str, list[list[str]]] = {k: [] for k in TYPES}
    for stem in ORDER:
        text = (folder / f"{stem}.md").read_text(encoding="utf-8")
        owner = re.search(r"Owner domain\*{0,2}\s*\|\s*([^|\n]+)", text)
        owner = owner.group(1).strip() if owner else "—"
        section = text.split("## Vault objects", 1)[1].split("\n## ", 1)[0]
        for line in section.splitlines():
            if line.startswith("| ") and not line.startswith(("| **", "| ---")):
                type_, name, definition, grain, key = _cells(line)
                out[kind(type_, grain)].append([owner, stem.replace("_", " "), name, definition, grain, key])
    return out


def inventory(folder: Path) -> str:
    parts = []
    for type_, (heading, _, _) in TYPES.items():
        data = rows(folder)[type_]
        parts.append(f"## {heading}\n")
        if not data:
            parts.append("None yet.\n")
            continue
        table = ["| " + " | ".join(f"**{c}**" for c in COLUMNS) + " |", "| " + " | ".join("---" for _ in COLUMNS) + " |"]
        table += ["| " + " | ".join(r) + " |" for r in data]
        parts.append("\n".join(table) + "\n")
    return "\n".join(parts)


if __name__ == "__main__":
    print(inventory(Path(sys.argv[1] if len(sys.argv) > 1 else "Rosetta/Business_Objects")))
