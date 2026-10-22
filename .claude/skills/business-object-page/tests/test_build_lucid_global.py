import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_lucid_global as g  # noqa: E402


def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def crosses(p1, p2, p3, p4):
    return ccw(p3, p4, p1) * ccw(p3, p4, p2) < 0 and ccw(p1, p2, p3) * ccw(p1, p2, p4) < 0


def hits_box(p1, p2, box):
    """True when the straight segment passes through the inside of the box."""
    x0, y0, x1, y1 = box.x + 1, box.y + 1, box.x + box.w - 1, box.y + box.h - 1
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        if crosses(p1, p2, a, b):
            return True
    inside = lambda p: x0 < p[0] < x1 and y0 < p[1] < y1  # noqa: E731
    return inside(p1) and inside(p2)


class GlobalDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.edges = g.load_all()
        cls.layout = g.build_layout(cls.nodes, cls.edges)
        cls.spec = g.to_spec(cls.layout)
        cls.page = cls.spec["pages"][0]
        everything = {c["value"]: s for s in cls.page["shapes"] for c in s.get("customData", []) if c["key"] == "name"}
        cls.ghosts = {n for n in everything if ":" in n}
        cls.by_name = {n: s for n, s in everything.items() if n not in cls.ghosts}
        cls.name_of = {s["id"]: n for n, s in cls.by_name.items()}

    def test_one_box_per_vault_object_of_the_five_pages(self):
        self.assertEqual(set(self.by_name), set(self.nodes))
        self.assertEqual(len(self.by_name), 51)
        self.assertEqual(self.ghosts, {"hub_party:location"})

    def test_ids_are_short_enough_for_lucid(self):
        for s in self.page["shapes"]:
            self.assertLessEqual(len(s["id"]), 20, s["id"])
        for ln in self.page["lines"]:
            self.assertLessEqual(len(ln["id"]), 20, ln["id"])

    def test_one_arrow_per_child_to_parent_edge(self):
        arrows = [ln for ln in self.page["lines"] if ln["endpoint2"]["style"] == "arrow"]
        self.assertEqual(len(arrows), len(self.edges))
        self.assertEqual(sum(1 for ln in self.layout.lines if ln["parent"] in self.ghosts), 1)
        for ln in arrows:
            self.assertEqual(ln["lineType"], "straight")
            self.assertIn("position", ln["endpoint1"])
            self.assertIn("position", ln["endpoint2"])

    def test_every_line_is_straight(self):
        self.assertTrue(all(ln["lineType"] == "straight" for ln in self.page["lines"]))

    def test_colors_by_kind_and_the_in_place_exception(self):
        by_id = self.by_name
        fill = lambda n: by_id[n]["style"]["fill"]["color"]  # noqa: E731
        line = lambda n: by_id[n]["style"]["stroke"]["color"]  # noqa: E731
        self.assertEqual((fill("hub_party"), line("hub_party")), ("#8F63F4", "#3A0CA3"))
        self.assertEqual((fill("lnk_natural_person__party"), line("lnk_natural_person__party")), ("#A2F1E6", "#45E3CD"))
        self.assertEqual((fill("sat_natural_person__name"), line("sat_natural_person__name")), ("#FCB3D5", "#F72586"))
        self.assertEqual(
            (fill("sat_natural_person__demographics"), line("sat_natural_person__demographics")), ("#FEDBEB", "#FCB3D5"))
        self.assertEqual(fill("sat_natural_person__demographics_history"), "#FCB3D5")

    def test_in_place_background_is_lighter_than_the_default(self):
        light = lambda h: sum(int(h[i:i + 2], 16) for i in (1, 3, 5))  # noqa: E731
        self.assertGreater(light(g.STYLE["Satellite (in place)"]["fill"]), light(g.STYLE["Satellite"]["fill"]))
        self.assertEqual(g.STYLE["Satellite (in place)"]["line"], g.STYLE["Satellite"]["fill"])

    def test_box_height_is_text_height_plus_the_padding(self):
        for name, box in self.layout.boxes.items():
            if box.kind == "Hub":
                self.assertGreaterEqual(box.h, box.text_h + g.PAD, name)
            else:
                self.assertAlmostEqual(box.h, box.text_h + g.PAD, places=6, msg=name)

    def test_box_width_is_text_width_plus_the_padding(self):
        twins = {a for pair in self.layout.twins for a in pair}
        for name, box in self.layout.boxes.items():
            if name in twins:
                self.assertGreaterEqual(box.w, box.text_w + g.PAD - 1e-6, name)
            else:
                self.assertAlmostEqual(box.w, box.text_w + g.PAD, places=6, msg=name)

    def test_the_two_satellites_of_a_twin_pair_share_the_wider_width(self):
        for hist, plain in self.layout.twins:
            a, b = self.layout.boxes[hist], self.layout.boxes[plain]
            self.assertEqual(a.w, b.w)
            self.assertAlmostEqual(a.w, max(a.text_w, b.text_w) + g.PAD, places=6)

    def test_boxes_do_not_overlap(self):
        boxes = list(self.layout.boxes.values())
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                apart = a.x + a.w <= b.x or b.x + b.w <= a.x or a.y + a.h <= b.y or b.y + b.h <= a.y
                self.assertTrue(apart, f"{a.name} overlaps {b.name}")

    def test_no_two_lines_cross(self):
        segs = g.segments(self.layout)
        for i, (l1, a1, b1) in enumerate(segs):
            for l2, a2, b2 in segs[i + 1:]:
                self.assertFalse(crosses(a1, b1, a2, b2), f"{l1['child']}>{l1['parent']} crosses {l2['child']}>{l2['parent']}")

    def test_no_line_passes_through_an_unrelated_box(self):
        for ln, p1, p2 in g.segments(self.layout):
            for name, box in self.layout.boxes.items():
                if name in (ln["child"], ln["parent"]):
                    continue
                self.assertFalse(hits_box(p1, p2, box), f"{ln['child']}>{ln['parent']} passes through {name}")

    def test_twin_pairs_sit_together_default_first(self):
        self.assertEqual(len(self.layout.twins), 3)
        for hist, plain in self.layout.twins:
            a, b = self.layout.boxes[hist], self.layout.boxes[plain]
            self.assertLess(a.y, b.y)
            self.assertEqual(a.x, b.x)
            self.assertTrue(b.in_place)
            self.assertFalse(a.in_place)

    def test_each_box_carries_its_definition_in_italic(self):
        by_id = self.by_name
        self.assertIn("<i>The table that", by_id["hub_party"]["text"])
        plain = by_id["sat_natural_person__demographics"]["text"].replace("<br>", " ")
        self.assertIn("replaced when it changes", plain)
        self.assertNotIn("one row per", plain)

    def test_the_name_of_every_object_is_one_line(self):
        for name, box in self.layout.boxes.items():
            real = name.split(":")[0]
            self.assertEqual(box.name_lines, [real])
            self.assertIn(f"<b>{real}</b>", g.box_html(box))

    def test_a_box_is_wide_enough_for_its_name(self):
        for name, box in self.layout.boxes.items():
            self.assertGreaterEqual(box.w, g._w(name.split(":")[0], g.NAME_PT, g.BOLD_EM) + g.PAD - 1)

    def test_spec_is_valid_json_and_has_the_four_legend_entries(self):
        json.dumps(self.spec)
        legend = [s for s in self.page["shapes"] if s["id"].startswith("legend_box")]
        self.assertEqual(len(legend), 4)

    def test_both_owner_domain_bands_are_drawn(self):
        titles = {s["containerTitle"]["text"] for s in self.page["shapes"] if s["type"] == "roundedRectangleContainer"}
        self.assertEqual(titles, {"Registries (owner domain)", "Registries (owner domain): Location", "Platform (owner domain)"})


if __name__ == "__main__":
    unittest.main()
