import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_diagram as bd  # noqa: E402
import build_lucid as bl  # noqa: E402

FIXTURE = HERE / "fixtures" / "valid_page.md"


def shapes_of(doc):
    return [s for p in doc["pages"] for s in p["shapes"]]


class LucidTests(unittest.TestCase):
    def setUp(self):
        self.model = bd.load_model(FIXTURE.read_text(encoding="utf-8"))
        self.doc = bl.build_document([self.model])
        self.overview = self.doc["pages"][0]
        self.tables = [s for s in shapes_of(self.doc) if s["type"] == "table"]
        self.with_fields = [n for n in self.model.nodes if n.rows and not n.external]

    def test_document_is_valid_json_with_unique_page_ids(self):
        json.dumps(self.doc)
        ids = [p["id"] for p in self.doc["pages"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_one_overview_page_then_one_page_per_object_with_fields(self):
        self.assertEqual(len(self.doc["pages"]), 1 + len(self.with_fields))
        self.assertTrue(self.doc["pages"][0]["title"].endswith("(overview)"))
        self.assertEqual({p["title"] for p in self.doc["pages"][1:]}, {n.name for n in self.with_fields})

    def test_overview_has_no_tables(self):
        self.assertEqual([s for s in self.overview["shapes"] if s["type"] == "table"], [])

    def test_every_object_with_fields_has_tables_on_its_own_page(self):
        for page in self.doc["pages"][1:]:
            names = {s["id"].split("-c")[0][len("table_"):] for s in page["shapes"] if s["type"] == "table"}
            self.assertEqual(names, {page["title"]})

    def test_tables_hold_a_header_and_one_row_per_field(self):
        body_rows = sum(t["rowCount"] - 1 for t in self.tables)
        self.assertEqual(body_rows, sum(len(n.rows) for n in self.with_fields))
        for t in self.tables:
            self.assertEqual(t["colCount"], sum(bl.UNITS))

    def test_table_header_cells_are_the_page_columns(self):
        for t in self.tables:
            header = [c["text"] for c in t["cells"] if c["yPosition"] == 0]
            self.assertEqual(header, bd.FIELD_COLUMNS)

    def test_header_bar_uses_the_type_color(self):
        fills = {s["text"]: s["style"]["fill"]["color"] for s in shapes_of(self.doc) if s["id"].startswith("head_")}
        hub = next(v for k, v in fills.items() if "hub_sample_order" in k)
        sat = next(v for k, v in fills.items() if "sat_sample_order__pricing" in k)
        self.assertEqual(hub, "#3A0CA3")
        self.assertEqual(sat, "#F72586")

    def test_no_symbols_that_lucid_reads_as_emoji(self):
        text = json.dumps(self.doc, ensure_ascii=False)
        for symbol in "◆◇●▪Δ":
            self.assertNotIn(symbol, text)

    def test_table_stays_within_what_lucid_imports(self):
        for t in self.tables:
            self.assertLessEqual(len(t["cells"]), 49, t["id"])

    def test_every_cell_has_text(self):
        for t in self.tables:
            for c in t["cells"]:
                self.assertTrue(c.get("text"), c)

    def test_every_table_cell_of_the_grid_is_covered(self):
        for t in self.tables:
            covered = {(c["xPosition"] + dx, c["yPosition"]) for c in t["cells"] for dx in range(c.get("mergeCellsRight", 0) + 1)}
            self.assertEqual(len(covered), t["rowCount"] * t["colCount"])

    def test_ids_are_unique_across_the_whole_document(self):
        two = bl.build_document([self.model, self.model])
        ids = [s["id"] for p in two["pages"] for s in p["shapes"] + p["lines"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_one_pinned_line_per_edge_on_the_overview(self):
        lines = self.overview["lines"]
        self.assertEqual(len(lines), len(self.model.edges))
        for line in lines:
            self.assertIn("position", line["endpoint1"])
            self.assertIn("position", line["endpoint2"])
            self.assertEqual(line["endpoint2"]["style"], "arrow")

    def test_boxes_do_not_overlap_on_the_overview(self):
        boxes = [s["boundingBox"] for s in self.overview["shapes"] if s["id"].startswith("body_")]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                apart = (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"]
                         or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])
                self.assertTrue(apart)

    def test_tables_fit_inside_their_object_box(self):
        for page in self.doc["pages"][1:]:
            body = next(s["boundingBox"] for s in page["shapes"] if s["id"].startswith("body_"))
            for t in (s for s in page["shapes"] if s["type"] == "table"):
                b = t["boundingBox"]
                self.assertGreaterEqual(b["x"], body["x"])
                self.assertGreaterEqual(b["y"], body["y"])
                self.assertLessEqual(b["x"] + b["w"], body["x"] + body["w"])
                self.assertLessEqual(b["y"] + b["h"], body["y"] + body["h"])


if __name__ == "__main__":
    unittest.main()
