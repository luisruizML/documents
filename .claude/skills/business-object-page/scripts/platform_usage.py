"""Which vault objects use the Code List and the Load Configuration, read from the Fields tables of the pages.

A column takes its values from a Code List when the Code List page has a row for it (`table.column`) ("Which code columns are values of a Code
List"); a closed list is not one, because logic branches on it. A Satellite is loaded as set by the Load Configuration when it is one of a twin pair (a `_history` Satellite and
its in-place twin). Nothing here is typed by hand, so a new page cannot drift from the diagrams."""
from __future__ import annotations

import re
from pathlib import Path

CODE_LIST_OWN = re.compile(r"^(hub_code_list|hub_code_value|lnk_code_list__code_value|sat_code_list__|sat_code_value__)")
HUB_CODE_LIST = "hub_code_list"
HUB_LOAD_CONFIGURATION = "hub_load_configuration"


REPO = Path(__file__).resolve().parents[4]
CODE_LIST_PAGE = REPO / "Rosetta" / "Business_Objects" / "Code_List.md"


def listed_code_columns(page: Path = CODE_LIST_PAGE) -> set[str]:
    """`table.column` of every column the Code List page names as values of a list: the rows of its table "Which code
    columns are values of a Code List", the closed lists left out. The page is the one source, so a column is added
    there and nowhere else."""
    import validate_page as vp
    rows = vp.code_list_table(page.read_text(encoding="utf-8"))
    return {key for key, cells in rows.items() if not cells[1].startswith("Closed list")}


def code_list_users(nodes: dict, listed: set[str] | None = None) -> dict[str, list[str]]:
    """`{vault object: [its Code List columns]}`, the objects of the Code List page itself left out."""
    listed = listed_code_columns() if listed is None else listed
    out: dict[str, list[str]] = {}
    for name, node in nodes.items():
        if CODE_LIST_OWN.match(name) or node.external or not node.rows:
            continue
        columns = [r["Column"] for r in node.rows if f"{name}.{r['Column']}" in listed]
        if columns:
            out[name] = columns
    return out


def load_configuration_users(nodes: dict) -> list[str]:
    """The Satellites of a twin pair: each `_history` Satellite and the in-place Satellite it is paired with."""
    names = set(nodes)
    users = []
    for name in nodes:
        if nodes[name].kind != "Satellite":
            continue
        if name.endswith("_history") and name[: -len("_history")] in names:
            users += [name, name[: -len("_history")]]
    return users


def uses_lines(nodes: dict) -> list[tuple[str, str]]:
    """`(source hub, user)` for every gray dashed line: the Code List users first, then the Load Configuration users."""
    return [(HUB_CODE_LIST, n) for n in code_list_users(nodes)] + [(HUB_LOAD_CONFIGURATION, n) for n in load_configuration_users(nodes)]
