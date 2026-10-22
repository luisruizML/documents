import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import graph_layout as gl  # noqa: E402

try:
    import networkx  # noqa: F401
except ImportError:  # pragma: no cover
    networkx = None


@unittest.skipIf(networkx is None, "networkx is not installed: pip install -r .claude/skills/business-object-page/requirements.txt")
class GraphLayoutTests(unittest.TestCase):
    KINDS = {"hub_a": "Hub", "hub_b": "Hub", "lnk_a__b": "Link", "sat_a__x": "Satellite", "sat_a__y": "Satellite",
             "sat_b__z": "Satellite", "hub_c": "Hub", "sat_c__w": "Satellite"}
    EDGES = [("lnk_a__b", "hub_a"), ("lnk_a__b", "hub_b"), ("sat_a__x", "hub_a"), ("sat_a__y", "hub_a"), ("sat_b__z", "hub_b"),
             ("sat_c__w", "hub_c")]

    def run_layout(self):
        sats = [n for n, k in self.KINDS.items() if k == "Satellite"]
        return gl.layout(self.KINDS, {"sat_a__y": True}, self.EDGES, sats)

    def test_every_object_is_placed_once_with_the_size_of_its_kind(self):
        L = self.run_layout()
        self.assertEqual(set(L.items), set(self.KINDS))
        for name, p in L.items.items():
            self.assertEqual((p.w, p.h), gl.SIZE[self.KINDS[name]])

    def test_nothing_overlaps_and_no_structural_lines_cross(self):
        L = self.run_layout()
        self.assertEqual((L.overlaps, L.crossings), (0, 0))
        items = list(L.items.values())
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                self.assertFalse(gl._overlap(a.rect, b.rect), f"{a.name} overlaps {b.name}")
                self.assertFalse(gl._overlap(a.label_rect, b.rect), f"label of {a.name} overlaps {b.name}")

    def test_the_layout_is_deterministic(self):
        a, b = self.run_layout(), self.run_layout()
        self.assertEqual({n: (p.x, p.y, p.lx, p.ly) for n, p in a.items.items()},
                         {n: (p.x, p.y, p.lx, p.ly) for n, p in b.items.items()})

    def test_disconnected_components_do_not_overlap_the_main_one(self):
        L = self.run_layout()
        main = [L.items[n] for n in ("hub_a", "hub_b", "lnk_a__b", "sat_a__x", "sat_a__y", "sat_b__z")]
        other = [L.items[n] for n in ("hub_c", "sat_c__w")]
        for m in main:
            for o in other:
                self.assertFalse(gl._overlap(m.rect, o.rect))
                self.assertFalse(gl._overlap(m.label_rect, o.label_rect))

    def test_a_label_is_clear_of_its_own_shape(self):
        for p in self.run_layout().items.values():
            self.assertFalse(gl._overlap(p.rect, p.label_rect))

    def test_geometry_helpers(self):
        self.assertTrue(gl._cross((0, 0), (2, 2), (0, 2), (2, 0)))
        self.assertFalse(gl._cross((0, 0), (1, 1), (2, 0), (3, 1)))
        self.assertTrue(gl._segment_hits((0, 0), (10, 10), (4, 4, 6, 6)))
        self.assertFalse(gl._segment_hits((0, 0), (10, 0), (4, 4, 6, 6)))


if __name__ == "__main__":
    unittest.main()
