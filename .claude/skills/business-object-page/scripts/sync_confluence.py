"""Publish the Business Object pages and their diagrams to Confluence from the repository, in one command.

    python sync_confluence.py [--page Natural_Person] [--dry-run] [--no-images] [--lucid <full model id>] [--lucid-graph <graph id>]

For each page (the ids are in assets/confluence_pages.json; `text_only_pages` have no pictures, such as the inventory):
  1. the Markdown page is converted to Confluence storage format (md_to_storage.py) and saved as a new version of the
     page. A page whose repository text has not changed since the last sync is skipped: the version message carries
     a checksum of the converted text;
  2. the PNG files are uploaded as new versions of the attachments (sync_confluence_images.py). The pictures on the
     page are references to the attachments by file name, so they show the new files with no change to the page.

Credentials: CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN, from the environment or from the `.env` file in the
repository root (git ignores it). Not handled here: the index page, which holds a Lucidchart embed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from email.utils import formatdate
from pathlib import Path
from urllib.parse import quote_plus

import md_to_storage
import sync_confluence_images as images

PAGES_DIR = images.REPO / "Rosetta" / "Business_Objects"
MESSAGE_PREFIX = "Sync from the repository "


def build_inventory_colors():
    """(heading, fill, text colour) of the inventory tables, from build_inventory.TYPES."""
    import build_inventory
    return [(heading, fill, ink) for heading, fill, ink in build_inventory.TYPES.values()]


def point_index_at_lucid(adf: dict, document_id: str, snapshot: str | None = None) -> int:
    """Point the Lucidchart embed of the index page at a Lucid document, and with `snapshot` (an HTTP date such as
    "Wed, 21 Oct 2026 10:00:00 GMT") move its last snapshot date, which Confluence shows as the picture until the viewer
    loads the live diagram. Returns how many embeds changed."""
    changed = 0

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            attrs = node.get("attrs") or {}
            if node.get("type") == "extension" and attrs.get("extensionKey") == "lucidchart":
                params = attrs["parameters"]
                old = params["macroParams"]["documentId"]["value"]
                if snapshot and params["macroParams"]["lastSnapshotDate"]["value"] != snapshot:
                    previous = params["macroParams"]["lastSnapshotDate"]["value"]
                    params["macroParams"]["lastSnapshotDate"]["value"] = snapshot
                    for item in params.get("macroMetadata", {}).get("placeholder", []):
                        url = item.get("data", {}).get("url")
                        if url:
                            item["data"]["url"] = url.replace(quote_plus(previous), quote_plus(snapshot))
                    changed += 1
                if old != document_id:
                    params["macroParams"]["documentId"]["value"] = document_id
                    for item in params.get("macroMetadata", {}).get("placeholder", []):
                        url = item.get("data", {}).get("url")
                        if url:
                            item["data"]["url"] = url.replace(old, document_id)
                    changed += 1
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(adf)
    return changed


GRAPH_TITLE = "Simplified graph"
FULL_TITLE = "Full model"
PICTURES_INTRO = ("The same Hubs, Links and Satellites in two pictures drawn in Lucidchart: first the simplified graph, to see the "
                  "shape, then the full model, to read the definition of each object.")
GRAPH_TEXT = ("Hubs are circles, Links are hexagons and Satellites are small squares, each with its name beside it. A gray dashed "
              "line joins the Code List and the Load Configuration to every object that uses them.")
FULL_TEXT = ("Every object with its definition written in its box. Registries and Platform are drawn as separate bands, and arrows "
             "run from the child to its parent. The same gray dashed lines show who uses the Code List and the Load Configuration.")


def _lucid_embeds(adf: dict) -> list[int]:
    """Positions, among the top-level nodes of the page, of the Lucidchart embeds, in order."""
    return [i for i, n in enumerate(adf["content"])
            if n.get("type") == "extension" and (n.get("attrs") or {}).get("extensionKey") == "lucidchart"]


def _node(kind: str, text: str, **attrs) -> dict:
    node = {"type": kind, "content": [{"type": "text", "text": text}]}
    if attrs:
        node["attrs"] = attrs
    return node


def _clone_embed(node: dict) -> dict:
    """A copy of a Lucidchart embed with its own macro ids, so Confluence treats it as another macro."""
    import copy
    import uuid
    new = copy.deepcopy(node)
    params = new["attrs"]["parameters"]
    old_macro = params["macroParams"]["macroId"]["value"]
    fresh = str(uuid.uuid4())
    params["macroParams"]["macroId"]["value"] = fresh
    params.get("macroMetadata", {}).get("macroId", {})["value"] = str(uuid.uuid4())
    old_embed = params["macroParams"]["embedId"]["value"]
    fresh_embed = str(uuid.uuid4())                 # two embeds sharing one embedId can show the same picture
    params["macroParams"]["embedId"]["value"] = fresh_embed
    for item in params.get("macroMetadata", {}).get("placeholder", []):
        url = item.get("data", {}).get("url")
        if url:
            item["data"]["url"] = url.replace(old_macro, fresh).replace(old_embed, fresh_embed)
    return new


def point_index_at_pictures(adf: dict, graph_id: str | None, global_id: str | None, snapshot: str | None = None) -> int:
    """The index shows two Lucidchart pictures under "The full picture": the simplified graph, then the full model, each
    under its own title. With one embed on the page, the graph's title, text and embed are added before it. Then each
    embed is pointed at its document. Returns how many changes were made."""
    changed = 0
    embeds = _lucid_embeds(adf)
    if len(embeds) == 1 and graph_id:
        at = embeds[0]
        content = adf["content"]
        if at > 0 and content[at - 1].get("type") == "paragraph":
            content[at - 1] = _node("paragraph", PICTURES_INTRO)      # the old sentence spoke of one diagram
            at -= 1
            content.insert(at + 1, _node("heading", GRAPH_TITLE, level=3))
            content.insert(at + 2, _node("paragraph", GRAPH_TEXT))
            content.insert(at + 3, _clone_embed(content[at + 3]))
            content.insert(at + 4, _node("heading", FULL_TITLE, level=3))
            content.insert(at + 5, _node("paragraph", FULL_TEXT))
            changed += 1
        embeds = _lucid_embeds(adf)
    for position, document_id in zip(embeds, (graph_id, global_id) if len(embeds) == 2 else (global_id,)):
        if document_id:
            changed += point_index_at_lucid({"content": [adf["content"][position]]}, document_id, snapshot)
    return changed


def checksum(storage: str) -> str:
    return hashlib.sha256(storage.encode("utf-8")).hexdigest()[:16]


def page_action(current_message: str, storage: str) -> str:
    """'skip' when the last sync already published this text, else 'update'."""
    return "skip" if current_message == MESSAGE_PREFIX + checksum(storage) else "update"


APPEARANCE_KEYS = ("content-appearance-draft", "content-appearance-published")
APPEARANCE = "full-width"  # the editor calls it Wide


def appearance_changes(properties: list[dict]) -> list[tuple[str, int | None]]:
    """The appearance properties of a page that are not Wide yet, as (key, current version or None when missing)."""
    found = {p["key"]: p for p in properties}
    return [(key, found[key]["version"]["number"] if key in found else None)
            for key in APPEARANCE_KEYS if key not in found or found[key]["value"] != APPEARANCE]


def set_wide(api: images.Confluence, page_id: str, dry_run: bool) -> int:
    """Set the page to the wide appearance, so the tables can cover its width. Returns how many properties changed."""
    url = f"{api.base}/rest/api/content/{page_id}/property"
    changes = appearance_changes(api.session.get(url + "?expand=version").json()["results"])
    for key, version in changes:
        if dry_run:
            continue
        if version is None:
            api.session.post_json(url, {"key": key, "value": APPEARANCE})
        else:
            api.session.put(f"{url}/{key}", {"key": key, "value": APPEARANCE, "version": {"number": version + 1}})
    return len(changes)


def publish(api: images.Confluence, page_id: str, storage: str) -> None:
    current = api.session.get(f"{api.base}/rest/api/content/{page_id}?expand=version").json()
    api.session.put(f"{api.base}/rest/api/content/{page_id}", {
        "id": page_id,
        "type": "page",
        "title": current["title"],
        "version": {"number": current["version"]["number"] + 1, "message": MESSAGE_PREFIX + checksum(storage)},
        "body": {"storage": {"value": storage, "representation": "storage"}},
    })


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", help="only this page, for example Natural_Person")
    ap.add_argument("--dry-run", action="store_true", help="say what would change and change nothing")
    ap.add_argument("--no-images", action="store_true", help="publish the text only")
    ap.add_argument("--lucid", help="point the full model embed of the index page at this Lucid document id")
    ap.add_argument("--lucid-graph", help="the simplified graph: its embed (added before the full model on the first run) points at this Lucid document id")
    args = ap.parse_args(argv)

    config = images.load_pages()
    pages = {k: v for k, v in config["pages"].items() if not args.page or k == args.page}
    if not pages and args.page not in config.get("text_only_pages", {}):
        print(f"no page named {args.page}", file=sys.stderr)
        return 2
    images.load_env()
    email, token = os.environ.get("CONFLUENCE_EMAIL"), os.environ.get("CONFLUENCE_API_TOKEN")
    if not email or not token:
        print("Set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN (environment or .env).", file=sys.stderr)
        return 2
    api = images.Confluence(config["base_url"], images.Session(email, token))

    code = 0
    if not args.no_images:  # pictures first, so a page never refers to a file that is not there yet
        existing = {page_id: api.attachments(page_id) for page_id in pages.values()}
        for step in images.plan(pages, existing):
            print(f"{step['action']:8} {step['page']:20} {step['file']}")
            if step["action"] in ("attach", "update") and not args.dry_run:
                api.upload(step)
            if step["action"] == "missing":
                code = 1
    if args.lucid or args.lucid_graph:
        index_id = config["index_page"]
        page = api.session.get(f"{api.base}/rest/api/content/{index_id}?expand=body.atlas_doc_format,version").json()
        adf = json.loads(page["body"]["atlas_doc_format"]["value"])
        changed = point_index_at_pictures(adf, args.lucid_graph, args.lucid, formatdate(usegmt=True))
        print(f"{'would make' if args.dry_run else 'made'} {changed} change(s) to the Lucidchart pictures of the index "
              f"(graph {args.lucid_graph or 'unchanged'}, full model {args.lucid or 'unchanged'})")
        if changed and not args.dry_run:
            api.session.put(f"{api.base}/rest/api/content/{index_id}", {
                "id": index_id, "type": "page", "title": page["title"],
                "version": {"number": page["version"]["number"] + 1, "message": "Lucidchart pictures: simplified graph and full model"},
                "body": {"atlas_doc_format": {"value": json.dumps(adf, ensure_ascii=False), "representation": "atlas_doc_format"}},
            })
    texts = dict(pages)
    if not args.page or args.page in config.get("text_only_pages", {}):
        texts.update({k: v for k, v in config.get("text_only_pages", {}).items() if not args.page or k == args.page})
    for stem, page_id in texts.items():
        colors = {heading: (fill, ink) for heading, fill, ink in build_inventory_colors()} if stem == "Vault_Objects_Inventory" else None
        storage = md_to_storage.convert((PAGES_DIR / f"{stem}.md").read_text(encoding="utf-8"), colors)
        message = api.session.get(f"{api.base}/rest/api/content/{page_id}?expand=version").json()["version"].get("message", "")
        action = page_action(message, storage)
        print(f"{action:8} {stem}")
        if action == "update" and not args.dry_run:
            publish(api, page_id, storage)
        changed = set_wide(api, page_id, args.dry_run)
        if changed:
            print(f"{'would set' if args.dry_run else 'set'} {changed} appearance propert(ies) of {stem} to Wide")
    return code


if __name__ == "__main__":
    sys.exit(main())
