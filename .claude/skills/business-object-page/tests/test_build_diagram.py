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


class RoleLinkTests(unittest.TestCase):
    """A Link whose name carries a role suffix still joins the Hubs named in its Business key cell."""

    def model(self, name, business_key):
        text = FIXTURE.read_text(encoding="utf-8")
        text = text.replace("`lnk_customer__sample_order`", f"`{name}`").replace("`hub_customer`, `hub_sample_order` |", business_key + " |", 1)
        return bd.load_model(text)

    def test_hubs_come_from_the_business_key_not_from_the_name(self):
        model = self.model("lnk_customer__sample_order_owner", "`hub_customer`, `hub_sample_order`")
        pairs = {(e.child, e.parent) for e in model.edges}
        self.assertIn(("lnk_customer__sample_order_owner", "hub_sample_order"), pairs)
        self.assertFalse(model.has("hub_sample_order_owner"))

    def test_one_object_in_two_roles_gets_two_labelled_edges(self):
        model = self.model("lnk_customer__customer_relation", "`hub_customer` (subject), `hub_customer` (related)")
        edges = [(e.parent, e.label) for e in model.edges if e.child == "lnk_customer__customer_relation"]
        self.assertEqual(sorted(edges), [("hub_customer", "related"), ("hub_customer", "subject")])

    def test_diagram_builds_with_two_edges_to_one_hub(self):
        model = self.model("lnk_customer__customer_relation", "`hub_customer` (subject), `hub_customer` (related)")
        for full in (False, True):
            xml = bd.to_drawio(model, full=full, title="t")
            self.assertEqual(len([c for c in cells(xml) if c.get("edge") == "1"]), len(model.edges))


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
        notes = [c for c in styled(self.simple, "text;") if (c.get("value") or "").startswith("The table that")]
        self.assertTrue(notes)
        for c in notes:
            self.assertIn("fontStyle=2", c.get("style"))

    def test_simple_note_is_the_definition_and_full_note_is_definition_then_grain(self):
        simple = [c.get("value") for c in styled(self.simple, "text;")]
        full = [c.get("value") for c in styled(self.full, "text;")]
        node = self.model.node("hub_sample_order")
        self.assertIn(node.definition, simple)
        self.assertNotIn(node.grain, simple)
        self.assertIn(node.definition + "<br><br>" + node.grain, full)

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


def widths(xml):
    return {c.get("value"): float(c.find("mxGeometry").get("width")) for c in styled(xml, "swimlane")}


class WidthTests(unittest.TestCase):
    def setUp(self):
        self.model = bd.load_model(FIXTURE.read_text(encoding="utf-8"))
        self.simple = bd.to_drawio(self.model, full=False, title="t")
        self.full = bd.to_drawio(self.model, full=True, title="t")

    def test_simple_object_is_at_least_250_wide(self):
        self.assertTrue(all(w >= 250 for w in widths(self.simple).values()))
        self.assertEqual(widths(self.simple)["hub_sample_order"], 250)

    def test_simple_object_with_a_long_name_is_name_width_plus_10(self):
        node = bd.Node("sat_" + "very_long_name_" * 4 + "x", "Satellite", "one row per parent key")
        expected = bd.measure(node.name, "mono_bold", 12) + bd.HEAD_INSET + bd.NAME_PAD
        self.assertGreater(expected, 250)
        self.assertEqual(bd._simple_w(node), int(expected) + 1 if expected % 1 else int(expected))

    def test_notes_wrap_inside_the_object(self):
        w = bd._simple_w(self.model.node("hub_sample_order"))
        long = bd.Node("hub_x", "Hub", "one row per business key " * 6)
        self.assertGreater(len(bd.wrap(long.note, "sans_italic", 11, w - 16)), 1)

    def test_full_object_is_table_width_plus_margins(self):
        node = self.model.node("sat_sample_order__pricing")
        table = sum(bd.column_widths(node.rows))
        self.assertEqual(widths(self.full)[node.name], max(table + bd.FRAME_PAD, bd._simple_w(node)))

    def test_description_is_250_and_role_null_pii_share_one_width(self):
        cols = dict(zip(bd.FIELD_COLUMNS, bd.column_widths(self.model.node("hub_sample_order").rows)))
        self.assertEqual(cols["Description"], 250)
        self.assertEqual(len({cols["Role"], cols["Null"], cols["PII"]}), 1)

    def test_column_type_default_fit_their_longest_text(self):
        rows = [{"Column": "a", "Type": "string", "Default": "x"}, {"Column": "a_much_longer_column_name", "Type": "t", "Default": "y"}]
        cols = dict(zip(bd.FIELD_COLUMNS, bd.column_widths(rows)))
        self.assertGreater(cols["Column"], cols["Type"])
        self.assertEqual(cols["Column"], int(bd.measure("a_much_longer_column_name", "mono", 10) + 0.999) + bd.CELL_PAD)

    def test_objects_of_a_diagram_do_not_all_share_one_width(self):
        self.assertGreater(len(set(widths(self.full).values())), 1)

    def test_outputs_are_named_diagrams_object_simplified_or_full(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "Sample_Order.md"
            page.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(bd.main([str(page), "--no-export"]), 0)
            self.assertEqual(
                sorted(p.name for p in (Path(d) / "drawio").glob("*.drawio")),
                ["Diagrams_Sample_Order_Full.drawio", "Diagrams_Sample_Order_Simplified.drawio"],
            )


class LabelPlacementTests(unittest.TestCase):
    """A connector label sits on the first horizontal segment, with free line on both sides, before any vertical."""

    def setUp(self):
        text = (HERE.parents[3] / "Rosetta" / "Business_Objects" / "Natural_Person.md").read_text(encoding="utf-8")
        self.model = bd.load_model(text)
        self.xml = bd.to_drawio(self.model, full=False, title="t")
        root = ET.fromstring(self.xml)
        self.box = {}
        ids = {}
        for c in root.iter("mxCell"):
            g = c.find("mxGeometry")
            if "swimlane" in (c.get("style") or "").split(";"):
                self.box[c.get("value")] = (float(g.get("x")), float(g.get("y")), float(g.get("width")), float(g.get("height")))
                ids[c.get("id")] = c.get("value")
        self.edges = []
        for c in root.iter("mxCell"):
            if c.get("edge") == "1":
                g = c.find("mxGeometry")
                pts = [(float(p.get("x")), float(p.get("y"))) for p in g.iter("mxPoint")]
                self.edges.append((c, ids[c.get("source")], ids[c.get("target")], pts, float(g.get("x"))))

    def label_span(self, child, parent, pts, label_x, label):
        cx, _, cw, _ = self.box[child]
        px, _, pw, _ = self.box[parent]
        child_left = cx < px
        x_out = cx + cw if child_left else cx
        x_in = px if child_left else px + pw
        x_bend = pts[0][0] if pts else x_in
        half = bd.label_w(label) / 2
        centre = x_out + (1 if child_left else -1) * (label_x + 1) / 2 * (abs(x_bend - x_out) + (abs(pts[0][1] - pts[1][1]) + abs(x_in - x_bend) if pts else 0)) if pts else None
        return x_out, x_bend, half, centre, child_left

    def test_every_label_fits_on_the_first_horizontal_segment(self):
        checked = 0
        for cell, child, parent, pts, label_x in self.edges:
            label = cell.get("value")
            if not label or not pts:
                continue
            x_out, x_bend, half, centre, child_left = self.label_span(child, parent, pts, label_x, label)
            lo, hi = sorted((x_out, x_bend))
            self.assertGreaterEqual(centre - half, lo + bd.LABEL_PAD - 1, label)
            self.assertLessEqual(centre + half, hi - bd.LABEL_PAD + 1, label)
            checked += 1
        self.assertGreater(checked, 5)

    def test_no_vertical_band_crosses_a_label(self):
        spans = []
        for cell, child, parent, pts, label_x in self.edges:
            label = cell.get("value")
            if label and pts:
                _, _, half, centre, _ = self.label_span(child, parent, pts, label_x, label)
                spans.append((cell.get("value"), centre - half, centre + half, pts[0][1]))
        for other, _, _, pts, _ in self.edges:
            if not pts:
                continue
            x = pts[0][0]
            y0, y1 = sorted((pts[0][1], pts[1][1]))
            for name, a, b, y in spans:
                if y0 <= y <= y1:
                    self.assertFalse(a < x < b, f"a vertical at x={x} crosses the label {name}")

    def test_the_gap_between_columns_grows_with_the_longest_label(self):
        short = bd.gap_widths(self.model, bd._columns(self.model))
        for e in self.model.edges:
            if e.label:
                e.label = e.label + "_a_much_longer_descriptor_than_any_other"
        long = bd.gap_widths(self.model, bd._columns(self.model))
        self.assertGreater(max(long.values()), max(short.values()))


if __name__ == "__main__":
    unittest.main()
