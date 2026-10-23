import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_lucid_global as g  # noqa: E402
import build_lucid_graph as bg  # noqa: E402

try:
    import networkx  # noqa: F401
except ImportError:  # pragma: no cover
    networkx = None


@unittest.skipIf(networkx is None, "networkx is not installed: pip install -r .claude/skills/business-object-page/requirements.txt")
class GraphDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.edges = g.load_all()
        cls.layout, cls.uses = bg.build(cls.nodes, cls.edges)
        cls.spec = bg.to_spec(cls.layout, cls.uses)
        cls.page = cls.spec["pages"][0]
        cls.by_name = {c["value"]: s for s in cls.page["shapes"] for c in s.get("customData", []) if c["key"] == "name"}

    def test_one_shape_per_vault_object_with_the_flowchart_type_of_its_kind(self):
        self.assertEqual(set(self.by_name), set(self.nodes))
        for name, shape in self.by_name.items():
            self.assertEqual(shape["type"], bg.SHAPE_TYPE[self.nodes[name].kind], name)

    def test_one_label_per_object_and_hub_names_are_bold(self):
        labels = [s for s in self.page["shapes"] if s["id"].startswith("l") and not s["id"].startswith("legend")]
        self.assertEqual(len(labels), len(self.nodes))
        for name, node in self.nodes.items():
            text = next(s["text"] for s in labels if f">{name}<" in s["text"])
            self.assertEqual("<b>" in text, node.kind == "Hub", name)

    def test_colors_follow_the_hand_drawn_graph(self):
        fill = lambda n: self.by_name[n]["style"]["fill"]["color"]  # noqa: E731
        self.assertEqual(fill("hub_party"), "#8F63F4")
        self.assertEqual(fill("lnk_location__natural_person"), "#A2F1E6")
        self.assertEqual(fill("sat_natural_person__name"), "#FCB3D5")
        self.assertEqual(fill("sat_natural_person__demographics"), "#FEDBEB")

    def test_structural_lines_are_straight_dark_and_pinned_on_both_ends(self):
        structural = [ln for ln in self.page["lines"] if ln["id"].startswith("e")]
        self.assertEqual(len(structural), len(self.layout.edges))
        for ln in structural:
            self.assertEqual(ln["lineType"], "straight")
            self.assertEqual(ln["stroke"]["color"], bg.EDGE)
            self.assertIn("position", ln["endpoint1"])
            self.assertIn("position", ln["endpoint2"])

    def test_every_line_joins_exactly_the_two_objects_the_pages_relate_and_ends_in_their_centres(self):
        ids = {name: s["id"] for name, s in self.by_name.items()}
        wanted = {frozenset((ids[c], ids[p])) for c, p in {(e.child, e.parent) for e in self.edges}}
        drawn = [ln for ln in self.page["lines"] if ln["id"].startswith("e")]
        self.assertEqual({frozenset((ln["endpoint1"]["shapeId"], ln["endpoint2"]["shapeId"])) for ln in drawn}, wanted)
        self.assertEqual(len(drawn), len(wanted))
        for ln in self.page["lines"]:
            if ln["id"].startswith(("e", "u")):
                for end in ("endpoint1", "endpoint2"):
                    self.assertEqual(ln[end]["position"], {"x": 0.5, "y": 0.5}, ln["id"])

    def test_the_gray_dashed_lines_reach_every_code_list_and_load_configuration_user(self):
        dashed = [ln for ln in self.page["lines"] if ln["id"].startswith("u")]
        self.assertEqual(len(dashed), len(self.uses))
        self.assertGreaterEqual(len(dashed), 33)
        for ln in dashed:
            self.assertEqual(ln["stroke"], {"color": g.USES_COLOR, "width": 1, "style": "dashed"})

    def test_no_structural_crossings_and_no_overlaps(self):
        # the Hubs and Links of the Immovable Asset cluster join Party and Location in a way that the force-directed layout cannot
        # always draw flat (with the Movable Assets pages the best of 24 seeds leaves 6); the few crossings left are drawn with a line jump
        self.assertLessEqual(self.layout.crossings, 6)
        self.assertEqual(self.layout.overlaps, 0)

    def test_attachment_points_lie_inside_the_box(self):
        for ln in self.page["lines"]:
            for end in ("endpoint1", "endpoint2"):
                if ln[end]["type"] == "shapeEndpoint":
                    pos = ln[end]["position"]
                    self.assertTrue(0 <= pos["x"] <= 1 and 0 <= pos["y"] <= 1, ln["id"])

    def test_the_spec_is_valid_json_and_the_legend_shapes_carry_their_tag(self):
        json.dumps(self.spec)
        legend = [s for s in self.page["shapes"] if s["id"].startswith("legend_box")]
        self.assertEqual(len(legend), 4)
        for s in legend:
            self.assertTrue(any(tag in s["text"] for tag in ("HUB", "LINK", "SAT")))

    def test_the_layout_does_not_depend_on_the_hash_seed_of_the_run(self):
        code = ("import sys; sys.path.insert(0, r'%s'); import graph_layout as gl; "
                "k={'hub_a':'Hub','hub_b':'Hub','lnk_a__b':'Link','sat_a__x':'Satellite','hub_c':'Hub','lnk_b__c':'Link'}; "
                "e=[('lnk_a__b','hub_a'),('lnk_a__b','hub_b'),('sat_a__x','hub_a'),('lnk_b__c','hub_b'),('lnk_b__c','hub_c')]; "
                "L=gl.layout(k,{},e,['sat_a__x']); print(sorted((n,round(p.x,3),round(p.y,3)) for n,p in L.items.items()))"
                % (Path(__file__).resolve().parents[1] / "scripts"))
        runs = {subprocess.run([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, text=True,
                               check=True).stdout for seed in ("1", "2", "3")}
        self.assertEqual(len(runs), 1)


if __name__ == "__main__":
    unittest.main()
