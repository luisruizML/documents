"""Publish the Business Object pages and their diagrams to Confluence from the repository, in one command.

    python sync_confluence.py [--page Natural_Person] [--dry-run] [--no-images]

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
from pathlib import Path

import md_to_storage
import sync_confluence_images as images

PAGES_DIR = images.REPO / "Rosetta" / "Business_Objects"
MESSAGE_PREFIX = "Sync from the repository "


def build_inventory_colors():
    """(heading, fill, text colour) of the inventory tables, from build_inventory.TYPES."""
    import build_inventory
    return [(heading, fill, ink) for heading, fill, ink in build_inventory.TYPES.values()]


def point_index_at_lucid(adf: dict, document_id: str) -> int:
    """Point the Lucidchart embed of the index page at a Lucid document. Returns how many embeds changed."""
    changed = 0

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            attrs = node.get("attrs") or {}
            if node.get("type") == "extension" and attrs.get("extensionKey") == "lucidchart":
                params = attrs["parameters"]
                old = params["macroParams"]["documentId"]["value"]
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


def checksum(storage: str) -> str:
    return hashlib.sha256(storage.encode("utf-8")).hexdigest()[:16]


def page_action(current_message: str, storage: str) -> str:
    """'skip' when the last sync already published this text, else 'update'."""
    return "skip" if current_message == MESSAGE_PREFIX + checksum(storage) else "update"


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
    ap.add_argument("--lucid", help="point the Lucidchart embed of the index page at this Lucid document id")
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
    if args.lucid:
        index_id = config["index_page"]
        page = api.session.get(f"{api.base}/rest/api/content/{index_id}?expand=body.atlas_doc_format,version").json()
        adf = json.loads(page["body"]["atlas_doc_format"]["value"])
        changed = point_index_at_lucid(adf, args.lucid)
        print(f"{'would point' if args.dry_run else 'pointed'} {changed} Lucidchart embed(s) of the index at {args.lucid}")
        if changed and not args.dry_run:
            api.session.put(f"{api.base}/rest/api/content/{index_id}", {
                "id": index_id, "type": "page", "title": page["title"],
                "version": {"number": page["version"]["number"] + 1, "message": "Lucidchart embed: current diagram"},
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
    return code


if __name__ == "__main__":
    sys.exit(main())
