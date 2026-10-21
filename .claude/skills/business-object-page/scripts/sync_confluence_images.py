"""Upload the PNG files of the Business Object pages to Confluence, as new versions of the attachments the pages show.

    python sync_confluence_images.py [--page Natural_Person] [--dry-run]

The Atlassian connector of the assistant cannot upload files, so this script uses the Confluence REST API with the
credentials of the person who runs it. Set two environment variables once (the token is made at
https://id.atlassian.com/manage-profile/security/api-tokens and is never written in a file or in a chat):

    CONFLUENCE_EMAIL        the Atlassian account e-mail
    CONFLUENCE_API_TOKEN    the API token

For every image of every page (Rosetta/Business_Objects/images/Diagrams_<Object>_<Simplified|Full>.png):
  * if the page has no attachment with that file name, the file is attached;
  * if it has one, a new version of the same attachment is uploaded, so the picture on the page changes and the
    reference in the page body stays valid;
  * the SHA-256 of the file is kept in the attachment comment, and an image that has not changed is skipped, so the
    script can be run after every change and only uploads what is new.
A page body that refers to an attachment by its file id keeps working, because a new version keeps the file id.
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
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
IMAGES = REPO / "Rosetta" / "Business_Objects" / "images"
PAGES_FILE = Path(__file__).resolve().parent.parent / "assets" / "confluence_pages.json"
KINDS = ("Simplified", "Full")
COMMENT_PREFIX = "sha256:"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pages(path: Path = PAGES_FILE) -> dict:
    """{"base_url": ..., "pages": {"Natural_Person": "1996029956", ...}}"""
    return json.loads(path.read_text(encoding="utf-8"))


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
        url = f"{self.base}/rest/api/content/{page_id}/child/attachment?limit=200&expand=metadata"
        while url:
            data = self.session.get(url).json()
            for item in data.get("results", []):
                found[item["title"]] = {"id": item["id"], "comment": (item.get("metadata") or {}).get("comment", "")}
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
    missing = [s for s in steps if s["action"] == "missing"]
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
