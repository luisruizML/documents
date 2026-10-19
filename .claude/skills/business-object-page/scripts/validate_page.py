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
GRAIN_PREFIX = {
    "Hub": "one row per business key",
    "Link": "one row per distinct combination of",
    "Non-historized Link": "one row per occurrence of",
    "Satellite": "one row per parent key",
    "Reference table": "one row per code",
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
                header = _cells(block[0])
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
    "Reference table": re.compile(rf"^ref_{SNAKE}$"),
}
PREFIX = {"Hub": "hub_", "Link": "lnk_", "Non-historized Link": "lnk_", "Satellite": "sat_", "Reference table": "ref_"}
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


def _strip(cell: str) -> str:
    return cell.strip().strip("`").strip()


def _type_ok(t: str) -> bool:
    return t in TYPES or bool(DECIMAL_RE.match(t)) or bool(FIXED_RE.match(t))


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
            if parts != sorted(parts):
                errs.append(f"name: '{name}' link parts must be in alphabetical order: {'__'.join(sorted(parts))}")
        body = name[len(PREFIX[kind]):] if name.startswith(PREFIX[kind]) else name
        for token in (t for t in body.split("_") if t):
            if len(token) <= 3 and token not in ALLOWED_SHORT and token not in approved:
                errs.append(f"name: '{name}' contains '{token}', an abbreviation that is not on the approved list")
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
        for r in rows_:
            col = _strip(r.get("Column", ""))
            typ = _strip(r.get("Type", ""))
            for key in ("Null", "Personal data"):
                if r.get(key, "") not in ("Yes", "No"):
                    errs.append(f"fields: '{name}.{col}' {key} must be Yes or No, found '{r.get(key, '')}'")
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


def validate(text: str, base_dir: Path | None = None, approved: frozenset[str] = frozenset()) -> list[str]:
    page = parse_page(text)
    errs = check_sections(page)
    errs += check_header(page)
    errs += check_vault_objects(page, approved)
    return errs
