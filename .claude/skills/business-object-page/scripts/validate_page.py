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


def validate(text: str, base_dir: Path | None = None, approved: frozenset[str] = frozenset()) -> list[str]:
    page = parse_page(text)
    errs = check_sections(page)
    errs += check_header(page)
    return errs
