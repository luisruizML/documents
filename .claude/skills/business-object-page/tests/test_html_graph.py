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

    def test_every_field_linked_to_the_code_list_carries_its_examples(self):
        flagged = 0
        for it in self.items:
            cols = [c["column"] for c in it["codeLists"]]
            expect = [f["Column"] for f in it["fields"] if f.get("Code List") in ("List", "Closed")]
            self.assertEqual(cols, expect, it["name"])
            flagged += len(cols)
            for c in it["codeLists"]:
                self.assertTrue(c["where"] and c["why"] and c["examples"], (it["name"], c["column"]))
        self.assertGreater(flagged, 150)
        ident = self.items[self.index["sat_natural_person__identification"]]["codeLists"][0]
        self.assertEqual(ident["column"], "identification_type_code")
        self.assertIn("passport", ident["examples"])

    def test_the_template_selects_on_a_click_in_the_picture_like_in_the_list(self):
        html = hg.TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("elementFromPoint", html)   # the svg captures the pointer, so event.target is the svg
        self.assertIn('"data-i": i, x: lx', html)  # the names are clickable too
        self.assertIn("hotUse", html)              # the dashed lines of the selection are drawn

    def test_a_dashed_line_belongs_to_the_object_it_touches(self):
        sat = self.index["sat_natural_person__identification"]
        touching = [u for u in self.data["uses"] if sat in u]
        self.assertEqual(len(touching), 1)
        self.assertEqual(self.items[touching[0][0]]["name"], "hub_code_list")

    def test_clicking_a_hub_keeps_its_links_and_satellites_and_the_satellites_of_those_links(self):
        focus = self.data["focus"]["hub_natural_person"]
        names = {self.items[i]["name"] for i in focus["nodes"]}
        self.assertIn("hub_natural_person", names)
        self.assertIn("sat_natural_person__name", names)
        self.assertIn("lnk_natural_person__party", names)
        self.assertIn("sat_natural_person__natural_person_relation__relationship", names)
        self.assertIn("hub_party", names)                 # the Hub on the other side of a Link is kept too
        self.assertIn("hub_legal_entity", names)          # across lnk_legal_entity__natural_person
        self.assertNotIn("hub_rrr", names)                # but not the Hubs two Links away
        self.assertNotIn("sat_party__sensitivity", names) # nor what hangs from the other Hub

    def test_a_selected_hub_reaches_the_hubs_across_its_links_with_the_connector(self):
        d = self.data
        focus = d["focus"]["hub_natural_person"]
        link = next(i for i, it in enumerate(self.items) if it["name"] == "lnk_natural_person__party")
        party = next(i for i, it in enumerate(self.items) if it["name"] == "hub_party")
        self.assertTrue(any(d["edges"][e] == [link, party] for e in focus["edges"]))

    def test_selecting_a_link_or_a_satellite_does_not_reach_further_hubs(self):
        names = {self.items[i]["name"] for i in self.data["focus"]["sat_natural_person__name"]["nodes"]}
        self.assertEqual(names, {"sat_natural_person__name", "hub_natural_person"})

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

    def test_the_areas_group_the_pages_and_the_assets_area_surrounds_the_two_kinds_of_asset(self):
        areas = {a["name"]: a for a in self.data["areas"]}
        self.assertEqual(list(areas), ["Assets", "Immovable Assets", "Movable Assets", "Parties", "Legal", "Contact Point"])
        names = lambda a: {self.items[i]["name"] for i in areas[a]["items"]}  # noqa: E731
        self.assertTrue(names("Immovable Assets") <= names("Assets") and names("Movable Assets") <= names("Assets"))
        self.assertIn("hub_base_parcel", names("Immovable Assets"))
        self.assertIn("hub_swappable_component", names("Movable Assets"))
        self.assertTrue({"hub_party", "hub_natural_person", "hub_legal_entity"} <= names("Parties"))
        self.assertTrue({"hub_rrr", "hub_entitlement", "hub_credential"} <= names("Legal"))
        self.assertEqual(len(names("Contact Point")), 7)
        self.assertGreater(areas["Assets"]["radius"], areas["Immovable Assets"]["radius"])

    def test_an_area_line_joins_two_objects_of_the_area(self):
        for a in self.data["areas"]:
            members = set(a["items"])
            for e in a["edges"]:
                x, y = self.data["edges"][e]
                self.assertTrue(x in members and y in members, a["name"])

    def test_the_template_draws_the_areas_behind_and_lets_the_clicks_through(self):
        html = hg.TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("gArea", html)
        self.assertIn("#gArea { pointer-events: none; }", html)
        self.assertLess(html.index('var gArea = el("g"'), html.index('var gUse = el("g"'))

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
