"""Upload the PNG files of the Business Object pages to Confluence, as new versions of the attachments the pages show.

    python sync_confluence_images.py [--page Natural_Person] [--dry-run]

The Atlassian connector of the assistant cannot upload files, so this script uses the Confluence REST API with the
credentials of the person who runs it. They are read from the environment or from the `.env` file in the repository
root, which git ignores (the token is made at https://id.atlassian.com/manage-profile/security/api-tokens):

    CONFLUENCE_EMAIL        the Atlassian account e-mail
    CONFLUENCE_API_TOKEN    the API token

For every image of every page (Rosetta/Business_Objects/images/Diagrams_<Object>_<Simplified|Full>.png):
  * if the page has no attachment with that file name, the file is attached;
  * if it has one, a new version of the same attachment is uploaded, so the picture on the page changes and the
    reference in the page body stays valid;
  * the SHA-256 of the file is kept in the attachment comment, and an image that has not changed is skipped, so the
    script can be run after every change and only uploads what is new.
A new version of an attachment gets a NEW file id, and the picture on a page points at a file id. So after the
upload the script reads the page body, points every picture whose file name matches at the current file id (and the
size of the new PNG), and saves the page. That step also runs when nothing was uploaded, so a page whose body was
rewritten with an older id is put right.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.request
import uuid
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
IMAGES = REPO / "Rosetta" / "Business_Objects" / "images"
PAGES_FILE = Path(__file__).resolve().parent.parent / "assets" / "confluence_pages.json"
KINDS = ("Simplified", "Full")
COMMENT_PREFIX = "sha256:"


def load_env(path: Path = REPO / ".env") -> None:
    """Read KEY=VALUE lines of the repository .env (which git ignores) into the environment, without overriding it."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pages(path: Path = PAGES_FILE) -> dict:
    """{"base_url": ..., "pages": {"Natural_Person": "1996029956", ...}}"""
    return json.loads(path.read_text(encoding="utf-8"))


def png_size(path: Path) -> tuple[int, int]:
    """Width and height of a PNG, read from its header."""
    return struct.unpack(">II", path.read_bytes()[16:24])


def retarget_media(adf: dict, file_ids: dict[str, str], sizes: dict[str, tuple[int, int]]) -> int:
    """Point every `media` node whose alt text is a known file name at that file's current id and size.
    Returns how many nodes changed."""
    changed = 0

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            attrs = node.get("attrs")
            if node.get("type") == "media" and isinstance(attrs, dict) and attrs.get("alt") in file_ids:
                name = attrs["alt"]
                width, height = sizes[name]
                new = {"id": file_ids[name], "width": width, "height": height}
                if any(attrs.get(k) != v for k, v in new.items()):
                    attrs.update(new)
                    changed += 1
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(adf)
    return changed


def plan(pages: dict[str, str], existing: dict[str, dict[str, dict]], images: Path = IMAGES) -> list[dict]:
    """What to do for each image: attach, update or skip. `existing[page_id][file_name]` is the attachment, if any."""
    steps = []
    for stem, page_id in pages.items():
        for kind in KINDS:
            name = f"Diagrams_{stem}_{kind}.png"
            path = images / name
            if not path.is_file():
                steps.append({"page": stem, "file": name, "action": "missing", "path": path})
                continue
            current = existing.get(page_id, {}).get(name)
            digest_now = digest(path)
            if current is None:
                action = "attach"
            elif (current.get("comment") or "") == COMMENT_PREFIX + digest_now:
                action = "skip"
            else:
                action = "update"
            steps.append({"page": stem, "file": name, "page_id": page_id, "action": action, "path": path,
                          "attachment_id": (current or {}).get("id"), "digest": digest_now})
    return steps


class Session:
    """Just enough HTTP for the two calls, with no dependency: Basic authentication, JSON replies, multipart upload."""

    def __init__(self, email: str, token: str):
        self.auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()

    class Reply:
        def __init__(self, body: bytes):
            self.body = body

        def json(self):
            return json.loads(self.body or b"{}")

        def raise_for_status(self):
            pass  # urllib already raised for an error status

    def _open(self, request: urllib.request.Request):
        request.add_header("Authorization", self.auth)
        with urllib.request.urlopen(request) as response:
            return self.Reply(response.read())

    def get(self, url: str):
        return self._open(urllib.request.Request(url, headers={"Accept": "application/json"}))

    def put(self, url: str, body: dict):
        request = urllib.request.Request(url, data=json.dumps(body).encode(), method="PUT",
                                         headers={"Content-Type": "application/json", "Accept": "application/json"})
        return self._open(request)

    def post_json(self, url: str, body: dict):
        request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                         headers={"Content-Type": "application/json", "Accept": "application/json"})
        return self._open(request)

    def post(self, url: str, headers=None, files=None, data=None):
        boundary = uuid.uuid4().hex
        crlf = chr(13) + chr(10)
        parts: list[bytes] = []
        for key, value in (data or {}).items():
            head = f"--{boundary}" + crlf + f'Content-Disposition: form-data; name="{key}"' + crlf + crlf
            parts.append(head.encode() + str(value).encode() + crlf.encode())
        for key, (name, handle, mime) in (files or {}).items():
            head = (f"--{boundary}" + crlf + f'Content-Disposition: form-data; name="{key}"; filename="{name}"' + crlf
                    + f"Content-Type: {mime}" + crlf + crlf)
            parts.append(head.encode() + handle.read() + crlf.encode())
        parts.append((f"--{boundary}--" + crlf).encode())
        request = urllib.request.Request(url, data=b"".join(parts), method="POST", headers=dict(headers or {}))
        request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        return self._open(request)


class Confluence:
    """The few REST calls needed; `session` is a requests.Session (or a stand-in in the tests)."""

    def __init__(self, base_url: str, session):
        self.base = base_url.rstrip("/")
        self.session = session

    def attachments(self, page_id: str) -> dict[str, dict]:
        found: dict[str, dict] = {}
        url = f"{self.base}/rest/api/content/{page_id}/child/attachment?limit=200&expand=metadata,extensions"
        while url:
            data = self.session.get(url).json()
            for item in data.get("results", []):
                found[item["title"]] = {"id": item["id"], "comment": (item.get("metadata") or {}).get("comment", ""),
                                        "file_id": (item.get("extensions") or {}).get("fileId")}
            nxt = data.get("_links", {}).get("next")
            url = (self.base.rsplit("/wiki", 1)[0] + nxt) if nxt else None
        return found

    def upload(self, step: dict) -> None:
        page_id, name, path = step["page_id"], step["file"], step["path"]
        url = f"{self.base}/rest/api/content/{page_id}/child/attachment"
        if step["action"] == "update":
            url += f"/{step['attachment_id']}/data"
        with path.open("rb") as handle:
            response = self.session.post(
                url,
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (name, handle, "image/png")},
                data={"comment": COMMENT_PREFIX + step["digest"], "minorEdit": "true"},
            )
        response.raise_for_status()


def retarget_page(api: Confluence, page_id: str, attachments: dict[str, dict], images: Path, names: list[str],
                  dry_run: bool) -> int:
    """Point the pictures of one page at the current attachments. Returns the number of pictures changed."""
    file_ids = {n: attachments[n]["file_id"] for n in names if n in attachments and attachments[n].get("file_id")}
    sizes = {n: png_size(images / n) for n in file_ids}
    page = api.session.get(f"{api.base}/rest/api/content/{page_id}?expand=body.atlas_doc_format,version").json()
    adf = json.loads(page["body"]["atlas_doc_format"]["value"])
    changed = retarget_media(adf, file_ids, sizes)
    if changed and not dry_run:
        api.session.put(f"{api.base}/rest/api/content/{page_id}", {
            "id": page_id, "type": "page", "title": page["title"],
            "version": {"number": page["version"]["number"] + 1, "message": "Pictures: current versions of the diagrams"},
            "body": {"atlas_doc_format": {"value": json.dumps(adf, ensure_ascii=False), "representation": "atlas_doc_format"}},
        })
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", help="only this page, for example Natural_Person")
    ap.add_argument("--dry-run", action="store_true", help="say what would be uploaded and upload nothing")
    args = ap.parse_args(argv)

    config = load_pages()
    pages = {k: v for k, v in config["pages"].items() if not args.page or k == args.page}
    if not pages:
        print(f"no page named {args.page}", file=sys.stderr)
        return 2
    load_env()
    email, token = os.environ.get("CONFLUENCE_EMAIL"), os.environ.get("CONFLUENCE_API_TOKEN")
    if not email or not token:
        print("Set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN first (see the top of this file).", file=sys.stderr)
        return 2
    api = Confluence(config["base_url"], Session(email, token))
    existing = {page_id: api.attachments(page_id) for page_id in pages.values()}
    steps = plan(pages, existing)
    for step in steps:
        print(f"{step['action']:8} {step['page']:20} {step['file']}")
        if step["action"] in ("attach", "update") and not args.dry_run:
            api.upload(step)
    for stem, page_id in pages.items():
        attachments = api.attachments(page_id)
        names = [f"Diagrams_{stem}_{kind}.png" for kind in KINDS]
        changed = retarget_page(api, page_id, attachments, IMAGES, names, args.dry_run)
        print(f"{'would point' if args.dry_run else 'pointed'} {changed} picture(s) of {stem} at the current files")
    missing = [s for s in steps if s["action"] == "missing"]
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
