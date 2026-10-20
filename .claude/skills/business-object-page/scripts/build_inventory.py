"""Vault objects inventory: the Vault objects table of every Business Object page, with Owner domain and Object
added as the two left columns. Prints Markdown; the Index carries the result under "## Vault objects inventory".

    python build_inventory.py [Rosetta/Business_Objects]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ORDER = ["Party", "Natural_Person", "Legal_Entity", "Code_List", "Load_Configuration"]


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


def inventory(folder: Path) -> str:
    out = ["| **Owner domain** | **Object** | **Type** | **Name** | **Grain** | **Business key** |", "| --- | --- | --- | --- | --- | --- |"]
    for stem in ORDER:
        text = (folder / f"{stem}.md").read_text(encoding="utf-8")
        owner = re.search(r"Owner domain\*{0,2}\s*\|\s*([^|\n]+)", text)
        owner = owner.group(1).strip() if owner else "—"
        section = text.split("## Vault objects", 1)[1].split("\n## ", 1)[0]
        for line in section.splitlines():
            if line.startswith("| ") and not line.startswith(("| **", "| ---")):
                out.append("| " + " | ".join([owner, stem.replace("_", " "), *_cells(line)]) + " |")
    return "\n".join(out)


if __name__ == "__main__":
    print(inventory(Path(sys.argv[1] if len(sys.argv) > 1 else "Rosetta/Business_Objects")))
