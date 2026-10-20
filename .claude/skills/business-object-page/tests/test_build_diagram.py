import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_diagram as bd  # noqa: E402

FIXTURE = HERE / "fixtures" / "valid_page.md"


def cells(xml: str):
    return list(ET.fromstring(xml).iter("mxCell"))


def styled(xml: str, fragment: str):
    token = fragment.rstrip(";")
    return [c for c in cells(xml) if token in (c.get("style") or "").split(";")]


class ColorTests(unittest.TestCase):
    def test_vault_object_colors(self):
        self.assertEqual(bd.PALETTE["Hub"]["fill"], "#3A0CA3")
        self.assertEqual(bd.PALETTE["Link"]["fill"], "#45E3CD")
        self.assertEqual(bd.PALETTE["Satellite"]["fill"], "#F72586")

    def test_text_follows_the_brand_contrast_rule(self):
        self.assertEqual(bd.PALETTE["Hub"]["text"], "#FFFFFF")
        self.assertEqual(bd.PALETTE["Link"]["text"], "#000000")
        self.assertEqual(bd.PALETTE["Satellite"]["text"], "#FFFFFF")

    def test_line_is_lighter_on_dark_fills_and_darker_on_light_fills(self):
        def lum(h):
            return sum(int(h[i:i + 2], 16) for i in (1, 3, 5))
        self.assertGreater(lum(bd.derive_line("#3A0CA3")), lum("#3A0CA3"))
        self.assertLess(lum(bd.derive_line("#45E3CD")), lum("#45E3CD"))

    def test_non_historized_link_uses_link_colors(self):
        self.assertEqual(bd.palette_for("Non-historized Link"), bd.PALETTE["Link"])


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model = bd.load_model(FIXTURE.read_text(encoding="utf-8"))

    def test_page_objects_carry_their_fields_and_grain(self):
        hub = self.model.node("hub_sample_order")
        self.assertFalse(hub.external)
        self.assertEqual(hub.grain, "one row per business key")
        self.assertEqual(hub.rows[0]["Column"], "sample_order_hk")

    def test_hub_on_another_page_is_found_from_the_link_name(self):
        customer = self.model.node("hub_customer")
        self.assertTrue(customer.external)
        self.assertIsNone(customer.rows)

    def test_context_objects_are_added(self):
        model = bd.load_model(FIXTURE.read_text(encoding="utf-8"), context=["lnk_other__sample_order"])
        self.assertTrue(model.node("lnk_other__sample_order").external)
        self.assertTrue(model.node("hub_other").external)

    def test_edges_run_from_child_to_parent(self):
        pairs = {(e.child, e.parent) for e in self.model.edges}
        self.assertIn(("sat_sample_order__pricing", "hub_sample_order"), pairs)
        self.assertIn(("lnk_customer__sample_order", "hub_customer"), pairs)
        self.assertIn(("lnk_customer__sample_order", "hub_sample_order"), pairs)


class InPlaceSatelliteTests(unittest.TestCase):
    """A Satellite updated in place is the exception to the history default, so it is drawn lighter."""

    def setUp(self):
        text = FIXTURE.read_text(encoding="utf-8")
        grain = "one row per parent key, for each time its values change"
        self.assertIn(grain, text)
        self.model = bd.load_model(text)
        self.model.node("sat_sample_order__pricing").grain = "one row per parent key, replaced in place when its values change"
        self.simple = bd.to_drawio(self.model, full=False, title="t")
        self.full = bd.to_drawio(self.model, full=True, title="t")

    def test_in_place_palette_is_a_lighter_satellite_color(self):
        def lum(h):
            return sum(int(h[i:i + 2], 16) for i in (1, 3, 5))
        light = bd.palette_for("Satellite", in_place=True)
        self.assertGreater(lum(light["fill"]), lum(bd.PALETTE["Satellite"]["fill"]))
        self.assertEqual(light["text"], "#000000")

    def test_only_an_in_place_satellite_gets_the_lighter_color(self):
        self.assertTrue(self.model.node("sat_sample_order__pricing").in_place)
        self.assertFalse(self.model.node("hub_sample_order").in_place)
        light = bd.PALETTE["Satellite (in place)"]["fill"]
        self.assertIn(f"fillColor={light};", self.simple)
        self.assertNotIn("fillColor=#F72586;swimlaneFillColor", self.simple)

    def test_in_place_container_has_a_dashed_border(self):
        head = [c for c in cells(self.simple) if c.get("value") == "sat_sample_order__pricing"][0]
        self.assertIn("dashed=1", head.get("style"))

    def test_the_full_table_header_stays_light(self):
        light = bd.PALETTE["Satellite (in place)"]["fill"]
        self.assertIn(f"fillColor={light};", self.full)
        self.assertGreater(self.full.count(f"fillColor={light};"), 1)

    def test_legend_lists_the_exception_only_when_one_is_present(self):
        self.assertIn("Satellite, in place (exception)", self.simple)
        plain = bd.to_drawio(bd.load_model(FIXTURE.read_text(encoding="utf-8")), full=False, title="t")
        self.assertNotIn("in place", plain)
        self.assertNotIn(bd.PALETTE["Satellite (in place)"]["fill"], plain)


class ExportScaleTests(unittest.TestCase):
    def geometry(self, bottom):
        return f'<mxGeometry x="0" y="{bottom - 100}" width="10" height="100" as="geometry"/>'

    def test_a_short_picture_keeps_the_wanted_scale(self):
        self.assertEqual(bd.fit_scale(self.geometry(1000), 2), 2)

    def test_a_tall_picture_is_scaled_down_so_it_is_not_cut_off(self):
        scale = bd.fit_scale(self.geometry(3033), 2)
        self.assertLess(scale, 2)
        self.assertLessEqual(3033 * scale, bd.MAX_PNG_HEIGHT)


class DrawioTests(unittest.TestCase):
    def setUp(self):
        text = FIXTURE.read_text(encoding="utf-8")
        self.model = bd.load_model(text)
        self.simple = bd.to_drawio(self.model, full=False, title="Sample Order cluster")
        self.full = bd.to_drawio(self.model, full=True, title="Sample Order cluster")

    def test_simple_version_has_no_tables(self):
        self.assertEqual(styled(self.simple, "shape=table"), [])

    def test_full_version_has_one_table_per_page_object_with_fields(self):
        self.assertEqual(len(styled(self.full, "shape=table")), 4)

    def test_full_table_has_header_plus_one_row_per_field(self):
        expected = sum(len(n.rows) + 1 for n in self.model.nodes if n.rows)
        self.assertEqual(len(styled(self.full, "shape=tableRow")), expected)

    def test_table_headers_are_bold_and_match_the_page_columns(self):
        header_cells = [c for c in styled(self.full, "fontStyle=1") if c.get("value") in bd.FIELD_COLUMNS]
        self.assertEqual({c.get("value") for c in header_cells}, set(bd.FIELD_COLUMNS))

    def test_each_object_is_a_collapsible_container(self):
        containers = styled(self.simple, "swimlane")
        self.assertEqual(len(containers), len(self.model.nodes))
        for c in containers:
            self.assertNotIn("collapsible=0", c.get("style"))

    def test_notes_are_italic(self):
        notes = [c for c in styled(self.simple, "text;") if (c.get("value") or "").startswith("one row per")]
        self.assertTrue(notes)
        for c in notes:
            self.assertIn("fontStyle=2", c.get("style"))

    def test_containers_use_the_type_colors(self):
        fills = {c.get("value"): c.get("style") for c in styled(self.simple, "swimlane")}
        self.assertIn("fillColor=#3A0CA3", fills["hub_sample_order"])
        self.assertIn("fillColor=#45E3CD", fills["lnk_customer__sample_order"])
        self.assertIn("fillColor=#F72586", fills["sat_sample_order__pricing"])

    def test_edge_labels_use_the_brand_label_style(self):
        edges = [c for c in cells(self.simple) if c.get("edge") == "1" and c.get("value")]
        self.assertTrue(edges)
        for e in edges:
            for part in ("labelBackgroundColor=#FFFFFF", "fontFamily=Courier New", "fontColor=#000000", "jumpStyle=arc"):
                self.assertIn(part, e.get("style"))

    def test_boxes_do_not_overlap(self):
        for xml in (self.simple, self.full):
            boxes = []
            for c in styled(xml, "swimlane"):
                g = c.find("mxGeometry")
                boxes.append((float(g.get("x")), float(g.get("y")), float(g.get("width")), float(g.get("height"))))
            for i, a in enumerate(boxes):
                for b in boxes[i + 1:]:
                    apart = a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1]
                    self.assertTrue(apart, f"{a} overlaps {b}")


if __name__ == "__main__":
    unittest.main()
