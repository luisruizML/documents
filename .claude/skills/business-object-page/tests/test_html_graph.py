import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_html_graph as hg  # noqa: E402
import build_lucid_global as g  # noqa: E402


class HtmlGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.edges = g.load_all()
        cls.data = hg.build_data(cls.nodes, cls.edges)
        cls.items = cls.data["items"]
        cls.index = {it["name"]: i for i, it in enumerate(cls.items)}

    def test_every_vault_object_is_in_the_file_hubs_then_links_then_satellites(self):
        self.assertEqual({it["name"] for it in self.items}, set(self.nodes))
        ranks = [hg.KIND_ORDER[it["kind"]] for it in self.items]
        self.assertEqual(ranks, sorted(ranks))

    def test_each_object_carries_what_the_info_panel_shows(self):
        for it in self.items:
            self.assertTrue(it["definition"], it["name"])
            self.assertTrue(it["grain"], it["name"])
            self.assertTrue(it["fields"], it["name"])
            self.assertTrue(it["page"], it["name"])
        hub = self.items[self.index["hub_natural_person"]]
        self.assertIn("natural_person_bk", hub["businessKey"])
        self.assertIn("Code List", hub["fields"][0])

    def test_clicking_a_hub_keeps_its_links_and_satellites_and_the_satellites_of_those_links(self):
        focus = self.data["focus"]["hub_natural_person"]
        names = {self.items[i]["name"] for i in focus["nodes"]}
        self.assertIn("hub_natural_person", names)
        self.assertIn("sat_natural_person__name", names)
        self.assertIn("lnk_natural_person__party", names)
        self.assertIn("sat_natural_person__natural_person_relation__relationship", names)
        self.assertNotIn("hub_legal_entity", names)       # the other Hub of a Link is not directly related
        self.assertNotIn("hub_rrr", names)

    def test_the_lines_kept_belong_to_the_selection(self):
        for name, focus in self.data["focus"].items():
            keep = set(focus["nodes"])
            for e in focus["edges"]:
                a, b = self.data["edges"][e]
                self.assertTrue(a in keep and b in keep, name)

    def test_a_satellite_of_a_selected_hub_is_not_expanded(self):
        sat = self.data["focus"]["hub_party"]["nodes"]
        names = {self.items[i]["name"] for i in sat}
        self.assertIn("sat_party__sensitivity", names)

    def test_the_file_is_self_contained_and_its_data_is_valid_json(self):
        html = hg.render(self.data)
        self.assertNotRegex(html, r'(src|href)="https?://')
        self.assertNotIn("@import", html)
        payload = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
        self.assertEqual(len(json.loads(payload)["items"]), len(self.items))
        self.assertNotIn("/*DATA*/", html)

    def test_the_file_is_not_a_confluence_page(self):
        pages = json.loads((Path(hg.HERE.parent / "assets" / "confluence_pages.json")).read_text(encoding="utf-8"))["pages"]
        self.assertNotIn("Vault_Graph", pages)


if __name__ == "__main__":
    unittest.main()
