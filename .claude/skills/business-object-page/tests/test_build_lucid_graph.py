import json
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
        self.assertEqual(fill("lnk_location__party"), "#A2F1E6")
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

    def test_gray_dashed_lines_reach_every_code_list_and_load_configuration_user(self):
        dashed = [ln for ln in self.page["lines"] if ln["id"].startswith("u")]
        self.assertEqual(len(dashed), len(self.uses))
        self.assertGreaterEqual(len(dashed), 33)
        for ln in dashed:
            self.assertEqual(ln["stroke"], {"color": g.USES_COLOR, "width": 1, "style": "dashed"})

    def test_no_structural_crossings_and_no_overlaps(self):
        self.assertEqual(self.layout.crossings, 0)
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


if __name__ == "__main__":
    unittest.main()
