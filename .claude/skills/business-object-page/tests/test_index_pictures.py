import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import sync_confluence as sc  # noqa: E402


def embed(document_id="old", macro="m1"):
    return {"type": "extension", "attrs": {"extensionKey": "lucidchart", "parameters": {
        "macroParams": {"documentId": {"value": document_id}, "macroId": {"value": macro}, "embedId": {"value": "shared-embed"},
                        "lastSnapshotDate": {"value": "Thu, 22 Oct 2026 18:13:08 GMT"}},
        "macroMetadata": {"macroId": {"value": "meta"},
                          "placeholder": [{"data": {"url": f"https://l/ac?macroId={macro}&documentId={document_id}&embedId=shared-embed"}}]}}}}


def page():
    return {"type": "doc", "content": [
        {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "The full picture"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "Every Hub of the five pages in one diagram"}]},
        embed(), {"type": "table"}]}


def kinds(adf):
    return [n["type"] for n in adf["content"]]


def doc_ids(adf):
    return [n["attrs"]["parameters"]["macroParams"]["documentId"]["value"] for n in adf["content"] if n["type"] == "extension"]


def text(node):
    return "".join(c["text"] for c in node["content"])


class PictureSectionTests(unittest.TestCase):
    def test_the_graph_goes_before_the_full_model_each_under_its_title(self):
        adf = page()
        changed = sc.point_index_at_pictures(adf, "graph", "full")
        self.assertGreaterEqual(changed, 1)
        self.assertEqual(kinds(adf), ["heading", "paragraph", "heading", "paragraph", "extension", "heading", "paragraph", "extension", "table"])
        self.assertEqual(doc_ids(adf), ["graph", "full"])
        self.assertEqual(text(adf["content"][2]), sc.GRAPH_TITLE)
        self.assertEqual(text(adf["content"][5]), sc.FULL_TITLE)
        self.assertEqual(adf["content"][2]["attrs"], {"level": 3})
        self.assertEqual(text(adf["content"][1]), sc.PICTURES_INTRO)

    def test_the_copied_embed_has_its_own_macro_ids_and_placeholder(self):
        adf = page()
        sc.point_index_at_pictures(adf, "graph", "full")
        graph, full = adf["content"][4]["attrs"]["parameters"], adf["content"][7]["attrs"]["parameters"]
        self.assertNotEqual(graph["macroParams"]["macroId"]["value"], full["macroParams"]["macroId"]["value"])
        self.assertNotEqual(graph["macroMetadata"]["macroId"]["value"], full["macroMetadata"]["macroId"]["value"])
        self.assertNotEqual(graph["macroParams"]["embedId"]["value"], full["macroParams"]["embedId"]["value"])
        self.assertNotIn("shared-embed", graph["macroMetadata"]["placeholder"][0]["data"]["url"])
        url = graph["macroMetadata"]["placeholder"][0]["data"]["url"]
        self.assertIn("documentId=graph", url)
        self.assertIn(graph["macroParams"]["macroId"]["value"], url)
        self.assertNotIn("m1", url)

    def test_a_second_run_changes_nothing(self):
        adf = page()
        sc.point_index_at_pictures(adf, "graph", "full")
        before = copy.deepcopy(adf)
        self.assertEqual(sc.point_index_at_pictures(adf, "graph", "full"), 0)
        self.assertEqual(adf, before)

    def test_with_two_embeds_each_is_pointed_at_its_own_document(self):
        adf = page()
        sc.point_index_at_pictures(adf, "graph", "full")
        sc.point_index_at_pictures(adf, "graph2", "full2")
        self.assertEqual(doc_ids(adf), ["graph2", "full2"])

    def test_without_a_graph_id_only_the_full_model_is_pointed(self):
        adf = page()
        sc.point_index_at_pictures(adf, None, "full")
        self.assertEqual(doc_ids(adf), ["full"])
        self.assertEqual(kinds(adf), ["heading", "paragraph", "extension", "table"])


if __name__ == "__main__":
    unittest.main()
