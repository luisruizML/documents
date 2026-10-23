"""Convert a Business Object page (Markdown) to Confluence storage format (XHTML).

Only what the pages use is handled: headings, paragraphs, bold, italic, inline code, links, bullet and numbered
lists, tables, and images. An image `![alt](images/Diagrams_X_Full.png)` becomes a reference to the attachment of
the same file name, so a new version of the attachment shows on the page with no change to the page body.
A link to another page of the set (`[Natural Person](Natural_Person.md)`) becomes a Confluence page link by title.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import table_layout as layout

# Page file -> title in Confluence
TITLES = {
    "Natural_Person.md": "Natural Person",
    "Party.md": "Party",
    "Legal_Entity.md": "Legal Entity",
    "Location.md": "Location",
    "Immovable_Assets.md": "Immovable Assets",
    "Movable_Assets.md": "Movable Assets",
    "Base_Asset.md": "Base Asset",
    "Swappable_Component.md": "Swappable Component",
    "Model_Catalog.md": "Model Catalog",
    "Base_Parcel.md": "Base Parcel",
    "Built_Structure.md": "Built Structure",
    "Code_List.md": "Code List",
    "Load_Configuration.md": "Load Configuration",
    "Platform.md": "Platform",
    "Index.md": "Business Objects",
    "Vault_Objects_Inventory.md": "Vault Objects Inventory",
}
IMAGE_WIDTH = 1449


def _escape(text: str) -> str:
    return html.escape(text, quote=False)


def inline(text: str) -> str:
    """Markdown inline syntax to storage XHTML. Code spans are cut out first so their content is not touched."""
    spans: list[str] = []

    def keep_code(match):
        spans.append(f"<code>{_escape(match.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = _escape(text)

    def link(match):
        label, target = match.group(1), match.group(2)
        if target in TITLES:
            return f'<ac:link><ri:page ri:content-title="{html.escape(TITLES[target])}"/></ac:link>'
        return f'<a href="{html.escape(target)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub("\x00(\\d+)\x00", lambda m: spans[int(m.group(1))], text)


def image(alt: str, src: str) -> str:
    name = src.rsplit("/", 1)[-1]
    return (f'<p><ac:image ac:align="center" ac:width="{IMAGE_WIDTH}" ac:alt="{html.escape(alt)}">'
            f'<ri:attachment ri:filename="{html.escape(name)}"/></ac:image></p>')


VALIGN = ' style="vertical-align: middle;"'


def table_xml(head: list[str], body: list[list[str]], heading_text: str, header_colors, widths: dict[str, list[int]]) -> str:
    """One table. The Header, Vault objects and Fields tables get column widths (table_layout.py); long Definition and
    Description cells are split into paragraphs."""
    k = layout.kind(head)
    names = [layout.plain(h).strip() for h in head]
    fill, ink = (header_colors or {}).get(heading_text, (None, None))
    if fill:
        cells = "".join(f'<th data-highlight-colour="{fill}"{VALIGN}><p><span style="color: {ink};">{inline(c)}</span></p></th>' for c in head)
    else:
        cells = "".join(f"<th{VALIGN}><p>{inline(c)}</p></th>" for c in head)
    if k == "header":
        opening = f'<table data-layout="default" data-table-width="{layout.HEADER_WIDTH}">' + layout.colgroup(widths["header"])
    elif k in ("vault", "fields"):
        opening = f'<table data-layout="full-width" data-table-width="{layout.PAGE_WIDTH}">' + layout.colgroup(widths[k])
    else:
        opening = "<table>"
    xml = opening + "<tbody><tr>" + cells + "</tr>"
    for row in body:
        tds = ""
        for name, cell in zip(names, row):
            parts = layout.paragraphs(cell) if k in ("vault", "fields") and name in layout.PARAGRAPH_COLUMNS else [cell]
            tds += f"<td{VALIGN}>" + "".join(f"<p>{inline(x)}</p>" for x in parts) + "</td>"
        xml += "<tr>" + tds + "</tr>"
    return xml + "</tbody></table>"


def convert(markdown: str, header_colors: dict[str, tuple[str, str]] | None = None) -> str:
    """`header_colors` maps the text of a heading to (fill, text colour) for the header row of the table that follows."""
    widths = layout.document_widths(markdown)
    lines = markdown.split("\n")
    out: list[str] = []
    heading_text = ""
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\r")
        if not line.strip() or line.startswith("# "):
            i += 1
            continue
        heading = re.match(r"^(#{2,4}) (.*)$", line)
        if heading:
            level = len(heading.group(1))
            heading_text = heading.group(2).replace("**", "")
            out.append(f"<h{level}>{inline(heading.group(2).replace('**', ''))}</h{level}>")
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].rstrip("\r").strip()[1:-1].split("|")])  # an empty cell stays a cell
                i += 1
            head, body = rows[0], rows[2:]
            out.append(table_xml(head, body, heading_text, header_colors, widths))
            continue
        if re.match(r"^(\*|-|\d+\.) ", line):
            ordered = line[0].isdigit()
            items = []
            while i < len(lines) and re.match(r"^(\*|-|\d+\.) ", lines[i]):
                items.append(re.sub(r"^(\*|-|\d+\.) ", "", lines[i].rstrip("\r")))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li><p>{inline(x)}</p></li>" for x in items) + f"</{tag}>")
            continue
        picture = re.match(r"^!\[(.*?)\]\((.+?)\)$", line)
        if picture:
            out.append(image(picture.group(1), picture.group(2)))
            i += 1
            continue
        if line.startswith("<!--"):
            i += 1
            continue
        out.append(f"<p>{inline(line)}</p>")
        i += 1
    return "".join(out)


def main(argv: list[str]) -> int:
    source = Path(argv[0]).read_text(encoding="utf-8")
    sys.stdout.write(convert(source))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
