import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import sync_confluence_images as sync  # noqa: E402


class FakeResponse:
    def __init__(self, data=None):
        self._data = data or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, pages=None):
        self.posts = []
        self.pages = pages or []

    def get(self, url):
        return FakeResponse(self.pages.pop(0))

    def post(self, url, headers=None, files=None, data=None):
        self.posts.append({"url": url, "headers": headers, "name": files["file"][0], "data": data})
        return FakeResponse()


def make_images(folder: Path, names):
    for name in names:
        (folder / name).write_bytes(b"png:" + name.encode())


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        make_images(self.dir, ["Diagrams_Sample_Simplified.png", "Diagrams_Sample_Full.png"])
        self.pages = {"Sample": "42"}

    def actions(self, existing):
        return {s["file"]: s["action"] for s in sync.plan(self.pages, existing, self.dir)}

    def test_an_image_without_an_attachment_is_attached(self):
        self.assertEqual(set(self.actions({}).values()), {"attach"})

    def test_an_image_with_another_digest_is_updated(self):
        existing = {"42": {"Diagrams_Sample_Full.png": {"id": "att1", "comment": "sha256:old"}}}
        actions = self.actions(existing)
        self.assertEqual(actions["Diagrams_Sample_Full.png"], "update")
        self.assertEqual(actions["Diagrams_Sample_Simplified.png"], "attach")

    def test_an_unchanged_image_is_skipped(self):
        digest = sync.digest(self.dir / "Diagrams_Sample_Full.png")
        existing = {"42": {"Diagrams_Sample_Full.png": {"id": "att1", "comment": "sha256:" + digest}}}
        self.assertEqual(self.actions(existing)["Diagrams_Sample_Full.png"], "skip")

    def test_a_missing_file_is_reported(self):
        (self.dir / "Diagrams_Sample_Full.png").unlink()
        self.assertEqual(self.actions({})["Diagrams_Sample_Full.png"], "missing")

    def test_the_real_pages_file_names_all_the_pages(self):
        pages = sync.load_pages()["pages"]
        self.assertEqual(sorted(pages), ["Code_List", "Immovable_Asset", "Legal_Entity", "Load_Configuration", "Location", "Natural_Person", "Party"])

    def test_every_real_image_exists(self):
        steps = sync.plan(sync.load_pages()["pages"], {})
        self.assertEqual([s["file"] for s in steps if s["action"] == "missing"], [])


class RetargetTests(unittest.TestCase):
    def adf(self):
        media = {"type": "media", "attrs": {"id": "old", "alt": "a.png", "width": 1, "height": 1, "collection": "c"}}
        return {"type": "doc", "content": [{"type": "mediaSingle", "content": [media]}]}

    def test_a_picture_is_pointed_at_the_current_file_and_size(self):
        adf = self.adf()
        self.assertEqual(sync.retarget_media(adf, {"a.png": "new"}, {"a.png": (30, 20)}), 1)
        attrs = adf["content"][0]["content"][0]["attrs"]
        self.assertEqual((attrs["id"], attrs["width"], attrs["height"]), ("new", 30, 20))

    def test_a_picture_that_is_already_current_is_left_alone(self):
        adf = self.adf()
        sync.retarget_media(adf, {"a.png": "new"}, {"a.png": (30, 20)})
        self.assertEqual(sync.retarget_media(adf, {"a.png": "new"}, {"a.png": (30, 20)}), 0)

    def test_a_picture_with_another_name_is_not_touched(self):
        adf = self.adf()
        self.assertEqual(sync.retarget_media(adf, {"b.png": "new"}, {"b.png": (1, 1)}), 0)

    def test_png_size_is_read_from_the_header(self):
        import struct
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.png"
            path.write_bytes(bytes.fromhex("89504e470d0a1a0a") + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 640, 480))
            self.assertEqual(sync.png_size(path), (640, 480))


class UploadTests(unittest.TestCase):
    def test_attach_posts_to_the_page_and_update_posts_to_the_attachment(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Diagrams_Sample_Full.png"
            path.write_bytes(b"x")
            session = FakeSession()
            api = sync.Confluence("https://x.atlassian.net/wiki/", session)
            api.upload({"page_id": "42", "file": path.name, "path": path, "action": "attach", "digest": "d"})
            api.upload({"page_id": "42", "file": path.name, "path": path, "action": "update", "attachment_id": "att9", "digest": "d"})
        self.assertEqual(session.posts[0]["url"], "https://x.atlassian.net/wiki/rest/api/content/42/child/attachment")
        self.assertEqual(session.posts[1]["url"], "https://x.atlassian.net/wiki/rest/api/content/42/child/attachment/att9/data")
        self.assertEqual(session.posts[0]["headers"], {"X-Atlassian-Token": "no-check"})
        self.assertEqual(session.posts[0]["data"]["comment"], "sha256:d")

    def test_attachments_are_listed_by_file_name_with_their_comment(self):
        page = {"results": [{"id": "att1", "title": "a.png", "metadata": {"comment": "sha256:1"}}], "_links": {}}
        api = sync.Confluence("https://x.atlassian.net/wiki", FakeSession([page]))
        self.assertEqual(api.attachments("42"), {"a.png": {"id": "att1", "comment": "sha256:1", "file_id": None}})


if __name__ == "__main__":
    unittest.main()
