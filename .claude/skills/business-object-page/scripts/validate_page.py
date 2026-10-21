"""Validate the form of a Rosetta Business Object page.

Checks sections, header values, vault-object names, types and grains.
It checks form only; whether the model is right stays a human review.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SECTIONS = [
    "Header",
    "Definition",
    "Why it is its own object",
    "Vault objects",
    "Fields",
    "Sources and mapping",
    "Jurisdictions map",
    "Examples",
    "Modeling considerations",
    "Diagram",
    "Open decisions",
]
DOMAINS = [
    "Platform",
    "Registries",
    "Taxation Contributions and Licences",
    "Finance",
    "Compliance",
    "Benefits",
    "AEOI",
]
SCOPES = ["Domain", "Shared", "Global"]
STATUSES = ["Draft", "Reviewed", "Agreed"]
HEADER_FIELDS = [
    "Object",
    "Parent object",
    "Owner domain",
    "Shared with",
    "Scope",
    "Status",
    "Version",
    "Last updated",
]
TYPES = [
    "boolean", "int", "long", "double", "float", "decimal(P,S)", "date", "time",
    "timestamptz", "timestamp", "timestamptz_ns", "timestamp_ns", "string", "uuid",
    "fixed(L)", "binary", "variant", "geometry", "geography", "unknown",
    "struct", "list", "map",
]
# The business meaning of each Vault object. The column is optional while the pages are being written one by one;
# when it is present every row is checked, and REQUIRE_DEFINITION makes it mandatory.
REQUIRE_DEFINITION = False
DEFINITION_START = "The table that"
DEFINITION_MAX = 400
DEFINITION_BANNED = ("hash",)
GRAIN_PREFIX = {
    "Hub": "one row per business key",
    "Link": "one row per distinct combination of",
    "Non-historized Link": "one row per occurrence of",
    "Satellite": "one row per parent key",
}


@dataclass
class Page:
    title: str = ""
    sections: dict[str, list[str]] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    def tables(self, section: str) -> list[list[dict[str, str]]]:
        return _tables(self.sections.get(section, []))


def _cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def _plain(cell: str) -> str:
    """A header cell without its bold markers."""
    c = cell.strip()
    return c[2:-2].strip() if len(c) > 4 and c.startswith("**") and c.endswith("**") else c


def _tables(lines: list[str]) -> list[list[dict[str, str]]]:
    result: list[list[dict[str, str]]] = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            if len(block) >= 2:
                header = [_plain(c) for c in _cells(block[0])]
                rows = [dict(zip(header, _cells(r))) for r in block[2:]]
                result.append(rows)
        else:
            i += 1
    return result


def parse_page(text: str) -> Page:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    page = Page()
    current: str | None = None
    for line in text.split("\n"):
        if line.startswith("# ") and not page.title:
            page.title = line[2:].strip()
        elif line.startswith("## "):
            current = line[3:].strip()
            page.order.append(current)
            page.sections[current] = []
        elif current is not None:
            page.sections[current].append(line)
    return page


def _body_is_blank(lines: list[str]) -> bool:
    return not any(l.strip() for l in lines)


def check_sections(page: Page) -> list[str]:
    errs: list[str] = []
    for name in SECTIONS:
        if name not in page.sections:
            errs.append(f"section: missing section '{name}'")
    present = [s for s in page.order if s in SECTIONS]
    expected = [s for s in SECTIONS if s in present]
    if present != expected:
        errs.append("section: sections are out of order; expected " + ", ".join(SECTIONS))
    for name in SECTIONS:
        if name in page.sections and _body_is_blank(page.sections[name]):
            errs.append(f"section: section '{name}' is blank; state explicitly that there is nothing to say")
    return errs


def check_header(page: Page) -> list[str]:
    errs: list[str] = []
    tables = page.tables("Header")
    if not tables:
        return ["header: the Header section needs a Field / Value table"]
    values = {row.get("Field", ""): row.get("Value", "") for row in tables[0]}
    for name in HEADER_FIELDS:
        if name not in values:
            errs.append(f"header: missing field '{name}'")
    owner = values.get("Owner domain")
    if owner is not None and owner not in DOMAINS:
        errs.append(f"header: owner domain '{owner}' is not one of: {', '.join(DOMAINS)}")
    shared = values.get("Shared with")
    if shared is not None and shared not in ("—", "None", ""):
        for item in (s.strip() for s in shared.split(",")):
            if item not in DOMAINS:
                errs.append(f"header: shared-with domain '{item}' is not one of: {', '.join(DOMAINS)}")
    scope = values.get("Scope")
    if scope is not None and scope not in SCOPES:
        errs.append(f"header: scope '{scope}' is not one of: {', '.join(SCOPES)}")
    status = values.get("Status")
    if status is not None and status not in STATUSES:
        errs.append(f"header: status '{status}' is not one of: {', '.join(STATUSES)}")
    return errs


SNAKE = r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*"
NAME_RE = {
    "Hub": re.compile(rf"^hub_{SNAKE}$"),
    "Link": re.compile(rf"^lnk_{SNAKE}__{SNAKE}$"),
    "Non-historized Link": re.compile(rf"^lnk_{SNAKE}__{SNAKE}$"),
    "Satellite": re.compile(rf"^sat_{SNAKE}(?:__{SNAKE})+$"),
}
PREFIX = {"Hub": "hub_", "Link": "lnk_", "Non-historized Link": "lnk_", "Satellite": "sat_"}
ALLOWED_SHORT = {"id", "hk", "bk", "dts", "of", "to", "by", "in", "on", "no", "is"}
DECIMAL_RE = re.compile(r"^decimal\(\d+,\d+\)$")
FIXED_RE = re.compile(r"^fixed\(\d+\)$")
TERM_TYPES = {
    "_id": {"string", "uuid"},
    "_code": {"string"},
    "_name": {"string"},
    "_date": {"date"},
    "_dts": {"timestamptz"},
    "_flag": {"boolean"},
    "_count": {"int", "long"},
}


def link_objects(parts: list[str], business_key: str) -> list[str]:
    """The object each link part stands for. A part may carry a role suffix (`party_owner` is the object `party`
    in the role of owner); the Hubs listed in the Business key cell say which prefix is the object."""
    hubs = [h[len("hub_"):] for h in re.findall(rf"hub_{SNAKE}", business_key)]
    out = []
    for part in parts:
        match = [h for h in hubs if part == h or part.startswith(h + "_")]
        out.append(max(match, key=len) if match else part)
    return out


def _strip(cell: str) -> str:
    return cell.strip().strip("`").strip()


def _type_ok(t: str) -> bool:
    return t in TYPES or bool(DECIMAL_RE.match(t)) or bool(FIXED_RE.match(t))


def _check_examples(table: str, col: str, desc: str) -> list[str]:
    """A _code column says what values look like: e.g. with three or more, or a closed list."""
    if "e.g." in desc:
        values = [v for v in re.split(r",| or ", desc.split("e.g.", 1)[1]) if v.strip(" .`")]
        if len(values) < 3:
            return [f"fields: '{table}.{col}' lists {len(values)} example values; give at least three"]
        return []
    if desc.startswith(("One of", "Only")) or ". One of" in desc or ". Only" in desc:
        return []
    return [f"fields: '{table}.{col}' Description needs example values: e.g. `a`, `b`, `c`; or One of `a`, `b` for a closed list"]


def _expected_role(col: str, kind: str, table: str) -> str:
    if col.endswith("_hk"):
        own = kind == "Hub" and col == table[len("hub_"):] + "_hk"
        return "◆" if own else "◇"
    if col.endswith("_bk"):
        return "●"
    if col in ("load_dts", "record_source"):
        return "▪"
    if col == "hashdiff":
        return "Δ"
    return ""


def _fields_tables(page: Page) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    name: str | None = None
    block: list[str] = []

    def flush():
        if name is not None:
            tables = _tables(block)
            out[name] = tables[0] if tables else []

    for line in page.sections.get("Fields", []):
        if line.startswith("### "):
            flush()
            name = line[4:].strip()
            block = []
        else:
            block.append(line)
    flush()
    return out


def _check_definition(name: str, row: dict[str, str]) -> list[str]:
    """The Definition says in business words what the table is for."""
    if "Definition" not in row:
        return [f"definition: '{name}' needs a Definition; the Vault objects table needs the column"] if REQUIRE_DEFINITION else []
    text = _strip(row["Definition"])
    if not text:
        return [f"definition: '{name}' has an empty Definition"]
    errs = []
    if not text.startswith(DEFINITION_START):
        errs.append(f"definition: '{name}' Definition must start with '{DEFINITION_START}'")
    if not text.endswith("."):
        errs.append(f"definition: '{name}' Definition must end with a full stop")
    if len(text) > DEFINITION_MAX:
        errs.append(f"definition: '{name}' Definition is {len(text)} characters; keep it to {DEFINITION_MAX} or fewer")
    for word in DEFINITION_BANNED:
        if word in text.lower():
            errs.append(f"definition: '{name}' Definition uses '{word}', a technical word; say it in business words")
    return errs


def check_vault_objects(page: Page, approved: frozenset[str]) -> list[str]:
    errs: list[str] = []
    tables = page.tables("Vault objects")
    if not tables:
        return ["name: the Vault objects section needs a table with Type, Name, Grain and Business key"]
    rows = tables[0]
    names: dict[str, str] = {}  # name -> type
    for row in rows:
        kind = row.get("Type", "")
        name = _strip(row.get("Name", ""))
        names[name] = kind
        if kind not in NAME_RE:
            errs.append(f"name: '{name}' has unknown type '{kind}'; use one of: {', '.join(NAME_RE)}")
            continue
        if not NAME_RE[kind].match(name):
            hint = f" (lowercase form: {name.lower()})" if name != name.lower() else ""
            msg = f"name: '{name}' does not match the {kind} pattern"
            if kind in ("Link", "Non-historized Link"):
                msg += " lnk_<a>__<b>"
            errs.append(msg + hint)
        if len(name) > 63:
            errs.append(f"name: '{name}' is longer than 63 characters")
        if kind in ("Link", "Non-historized Link") and NAME_RE[kind].match(name):
            parts = name[len("lnk_"):].split("__")
            bases = link_objects(parts, row.get("Business key", ""))
            if bases != sorted(bases):
                order = "__".join(p for _, p in sorted(zip(bases, parts), key=lambda bp: bp[0]))
                errs.append(f"name: '{name}' link parts must be in alphabetical order: {order}")
        body = name[len(PREFIX[kind]):] if name.startswith(PREFIX[kind]) else name
        for token in (t for t in body.split("_") if t):
            if len(token) <= 3 and token not in ALLOWED_SHORT and token not in approved:
                errs.append(f"name: '{name}' contains '{token}', an abbreviation that is not on the approved list")
        errs += _check_definition(name, row)
        grain = _strip(row.get("Grain", ""))
        if not grain.startswith(GRAIN_PREFIX[kind]):
            errs.append(f"grain: '{name}' grain must start with '{GRAIN_PREFIX[kind]}'")
    parents = {
        n[len("hub_"):] for n in names if n.startswith("hub_")
    } | {n[len("lnk_"):] for n in names if n.startswith("lnk_")}
    for name, kind in names.items():
        if kind == "Satellite" and NAME_RE["Satellite"].match(name):
            parent = name[len("sat_"):].rsplit("__", 1)[0]
            if parent not in parents:
                errs.append(f"name: '{name}' parent '{parent}' is not a Hub or Link on this page")

    fields = _fields_tables(page)
    for name in names:
        if name not in fields:
            errs.append(f"fields: vault object '{name}' has no Fields table")
    for name in fields:
        if name not in names:
            errs.append(f"fields: Fields table '{name}' is not in the Vault objects table")
    for name, rows_ in fields.items():
        kind = names.get(name, "")
        cols = [_strip(r.get("Column", "")) for r in rows_]
        if rows_:
            have = list(rows_[0].keys())
            if have != FIELD_COLUMNS:
                missing = [c for c in FIELD_COLUMNS if c not in have]
                errs.append(f"fields: table '{name}' must have columns {', '.join(FIELD_COLUMNS)}; missing {', '.join(missing) or 'none'}")
                continue
        for r in rows_:
            col = _strip(r.get("Column", ""))
            typ = _strip(r.get("Type", ""))
            for key in ("Null", "PII"):
                if r.get(key, "") not in ("Yes", "No"):
                    errs.append(f"fields: '{name}.{col}' {key} must be Yes or No, found '{r.get(key, '')}'")
            if not r.get("Default", "").strip():
                errs.append(f"fields: '{name}.{col}' Default must not be empty; write — when there is no default")
            if col.endswith("_code"):
                errs += _check_examples(name, col, r.get("Description", ""))
            expected = _expected_role(col, kind, name)
            if r.get("Role", "").strip() != expected:
                want = f"'{expected}' ({ROLES[expected]})" if expected else "no indicator"
                errs.append(f"fields: '{name}.{col}' Role must be {want}, found '{r.get('Role', '').strip()}'")
            if not _type_ok(typ):
                errs.append(f"type: '{name}.{col}' type '{typ}' is not on the allowed list (decimal needs decimal(P,S), fixed needs fixed(L))")
                continue
            if col.endswith("_amount"):
                if not DECIMAL_RE.match(typ):
                    errs.append(f"type: '{name}.{col}' ends in _amount, so its type must be decimal(P,S), found '{typ}'")
                continue
            if col.endswith("_hk") or col == "hashdiff":
                if typ != "string" and not FIXED_RE.match(typ):
                    errs.append(f"type: '{name}.{col}' must be string or fixed(L), found '{typ}'")
                continue
            for term, allowed in TERM_TYPES.items():
                if col.endswith(term) and typ not in allowed:
                    errs.append(f"type: '{name}.{col}' ends in {term}, so its type must be {' or '.join(sorted(allowed))}, found '{typ}'")
        if kind == "Hub":
            obj = name[len("hub_"):]
            for needed in (f"{obj}_hk", f"{obj}_bk"):
                if needed not in cols:
                    errs.append(f"fields: Hub '{name}' must have column '{needed}'")
        if kind == "Satellite":
            if any(c.endswith("_bk") for c in cols):
                errs.append(f"fields: Satellite '{name}' must not carry a business key (_bk); it carries only the parent's hash key")
            if not any(c.endswith("_hk") for c in cols):
                errs.append(f"fields: Satellite '{name}' must carry the parent's hash key (_hk)")
    return errs


def parse_lines(text: str) -> list[str]:
    cr, lf = chr(13), chr(10)
    return text.replace(cr + lf, lf).replace(cr, lf).split(lf)


def check_bold_headers(text: str) -> list[str]:
    errs: list[str] = []
    lines = parse_lines(text)
    for i in range(len(lines) - 1):
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]) and not re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
            for cell in _cells(lines[i]):
                if cell and _plain(cell) == cell:
                    errs.append(f"format: table header '{cell}' must be bold, write **{cell}**")
    return errs


def validate(text: str, base_dir: Path | None = None, approved: frozenset[str] = frozenset()) -> list[str]:
    page = parse_page(text)
    errs = check_sections(page)
    errs += check_bold_headers(text)
    errs += check_header(page)
    errs += check_vault_objects(page, approved)
    errs += check_sources(page)
    errs += check_jurisdictions(page)
    errs += check_diagram(page, base_dir)
    errs += check_decisions(page)
    return errs

SOURCES_EMPTY = "No endpoints declared yet"
JURISDICTIONS_EMPTY = "No jurisdiction differences known"
DECISIONS_EMPTY = "None open"
SOURCE_COLUMNS = ["Source", "Endpoint", "Bronze table", "Provides"]
JURISDICTION_COLUMNS = ["Edge case", "Where it happens", "Approach", "Vault effect"]
DECISION_COLUMNS = ["Decision", "Owner", "How it is decided", "Decide by"]
BRONZE_RE = re.compile(r"^bronze\.[a-z0-9_]+__[a-z0-9_]+$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+\.png)\)")
FIELD_COLUMNS = ["Column", "Role", "Type", "Null", "PII", "Default", "Description"]
ROLES = {"◆": "own hash key", "◇": "hash key of another object", "●": "business key", "▪": "load metadata", "Δ": "hashdiff"}


def _prose(lines: list[str]) -> list[str]:
    return [l.strip() for l in lines if l.strip() and not l.lstrip().startswith("|")]


def _table_or_statement(page: Page, section: str, statement: str, columns: list[str], tag: str) -> list[str]:
    lines = page.sections.get(section, [])
    if _body_is_blank(lines):
        return []  # reported by check_sections
    tables = _tables(lines)
    if not tables and [l for l in _prose(lines)] == [statement]:
        return []
    if not tables:
        return [f"{tag}: section '{section}' must be a table with columns {', '.join(columns)} or the exact statement '{statement}'"]
    header = list(tables[0][0].keys()) if tables[0] else []
    if header != columns:
        missing = [c for c in columns if c not in header]
        return [f"{tag}: section '{section}' table must have columns {', '.join(columns)}; missing {', '.join(missing) or 'none'}"]
    return []


def check_sources(page: Page) -> list[str]:
    errs = _table_or_statement(page, "Sources and mapping", SOURCES_EMPTY, SOURCE_COLUMNS, "sources")
    if errs:
        return errs
    lines = page.sections.get("Sources and mapping", [])
    tables = _tables(lines)
    declared = bool(tables) and list(tables[0][0].keys()) == SOURCE_COLUMNS if tables and tables[0] else False
    for row in (tables[0] if declared else []):
        bt = _strip(row.get("Bronze table", ""))
        if not BRONZE_RE.match(bt):
            errs.append(f"sources: Bronze table '{bt}' must look like bronze.<source>__<endpoint>, lowercase")
    if not declared and tables:
        errs.append("sources: a mapping record needs declared endpoints; the section says no endpoints are declared")
    if not declared and _prose(lines) == [SOURCES_EMPTY] and tables:
        errs.append("sources: a mapping record cannot exist while no endpoints are declared")
    return errs


def check_jurisdictions(page: Page) -> list[str]:
    return _table_or_statement(page, "Jurisdictions map", JURISDICTIONS_EMPTY, JURISDICTION_COLUMNS, "jurisdictions")


def check_decisions(page: Page) -> list[str]:
    return _table_or_statement(page, "Open decisions", DECISIONS_EMPTY, DECISION_COLUMNS, "decisions")


def check_diagram(page: Page, base_dir: Path | None) -> list[str]:
    body = chr(10).join(page.sections.get("Diagram", []))
    images = IMAGE_RE.findall(body)
    if not images:
        return ["diagram: the Diagram section needs an image link like ![text](images/Diagrams_Name_Simplified.png)"]
    full = [i for i in images if i.endswith("_Full.png")]
    simple = [i for i in images if i.endswith("_Simplified.png")]
    errs: list[str] = []
    if not simple or not full:
        errs.append(
            "diagram: the Diagram section needs the simplified image (images/Diagrams_Name_Simplified.png) "
            "and the full image (images/Diagrams_Name_Full.png)"
        )
    lines = body.splitlines()
    heads = {h: next((i for i, l in enumerate(lines) if l.strip() == h), -1) for h in ("### Simplified version", "### Full version")}
    pos = {k: next((i for i, l in enumerate(lines) if f"_{k}.png" in l), -1) for k in ("Simplified", "Full")}
    s_h, f_h = heads["### Simplified version"], heads["### Full version"]
    if min(s_h, f_h) < 0 or not s_h < pos["Simplified"] < f_h < pos["Full"]:
        errs.append("diagram: divide the section into '### Simplified version' and '### Full version', each heading before its own image")
    for image in images:
        if not image.startswith("images/Diagrams_"):
            errs.append(f"diagram: image '{image}' must be images/Diagrams_<Object>_<Simplified|Full>.png")
    if base_dir is not None:
        for image in images:
            if not (base_dir / image).is_file():
                errs.append(f"diagram: image file '{image}' not found next to the page")
    return errs


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Validate a Business Object page")
    ap.add_argument("page")
    ap.add_argument("--approved", default="", help="comma-separated approved abbreviations")
    args = ap.parse_args(argv)
    path = Path(args.page)
    approved = frozenset(a.strip() for a in args.approved.split(",") if a.strip())
    errs = validate(path.read_text(encoding="utf-8"), base_dir=path.parent, approved=approved)
    for e in errs:
        print(f"{path}: {e}")
    return 1 if errs else 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))

