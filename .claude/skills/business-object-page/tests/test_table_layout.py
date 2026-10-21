import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import md_to_storage as ms  # noqa: E402
import sync_confluence as sc  # noqa: E402
import table_layout as tl  # noqa: E402

PAGES = HERE.parents[3] / "Rosetta" / "Business_Objects"
PAGE_NAMES = ["Party", "Natural_Person", "Legal_Entity", "Code_List", "Load_Configuration"]


def page_text(name):
    return (PAGES / f"{name}.md").read_text(encoding="utf-8")


class VaultWidthTests(unittest.TestCase):
    def setUp(self):
        self.body = [["Hub", "`hub_a`", "The table that a.", "one row per business key", "`a_bk`"],
                     ["Satellite", "`sat_a__" + "very_long_" * 4 + "name`", "The table that b.", "one row per parent key", "—"]]
        self.w = tl.vault_widths(self.body)

    def test_the_widths_cover_the_page(self):
        self.assertEqual(sum(self.w), tl.PAGE_WIDTH)

    def test_business_key_is_half_of_definition(self):
        self.assertLessEqual(abs(self.w[4] - self.w[2] / 2), 1)

    def test_grain_is_the_wildcard(self):
        type_w, name_w, definition, grain, business = self.w
        self.assertLessEqual(abs(grain - (tl.PAGE_WIDTH - 1.5 * definition - type_w - name_w)), 2)

    def test_type_and_name_fit_their_texts(self):
        self.assertGreaterEqual(self.w[1], tl.text_width(self.body[1][1]))
        self.assertLess(self.w[0], 120)


class FieldsWidthTests(unittest.TestCase):
    def test_the_widths_cover_the_page_and_the_four_small_columns_are_equal(self):
        body = [["`a_hk`", "◇", "`string`", "No", "No", "—", "Hash key"],
                ["`some_long_column_name_code`", "", "`decimal(18,6)`", "Yes", "Yes", "`9999-12-31`", "x"]]
        w = tl.fields_widths([body])
        self.assertEqual(sum(w), tl.PAGE_WIDTH)
        self.assertEqual(len({w[1], w[3], w[4], w[5]}), 1)
        self.assertEqual(max(w), w[6])

    def test_every_fields_table_of_a_page_has_the_same_widths(self):
        xml = ms.convert(page_text("Natural_Person"))
        groups = {tuple(re.findall(r"width: ([0-9]+)px", m)) for m in re.findall(r"<colgroup>.*?</colgroup>", xml) if m.count("<col ") == 7}
        self.assertEqual(len(groups), 1)


class ParagraphTests(unittest.TestCase):
    def test_a_description_is_split_before_its_examples_and_at_sentences(self):
        self.assertEqual(tl.paragraphs("Kind of name: e.g. `a`, `b`; empty when unknown. Second sentence."),
                         ["Kind of name:", "e.g. `a`, `b`; empty when unknown.", "Second sentence."])

    def test_a_code_span_with_a_full_stop_is_not_split(self):
        self.assertEqual(tl.paragraphs("Pattern `^a. B$` is used."), ["Pattern `^a. B$` is used."])

    def test_the_text_is_not_changed_by_the_split(self):
        text = "One of `a`, `b`. Another sentence with e.g. `x`."
        self.assertEqual(" ".join(tl.paragraphs(text)), text)


class TableIntegrityTests(unittest.TestCase):
    def test_every_markdown_table_has_the_same_number_of_cells_in_every_row(self):
        for name in PAGE_NAMES + ["Index", "Platform", "Vault_Objects_Inventory"]:
            for head, body in tl.split_tables(page_text(name)):
                for row in body:
                    self.assertEqual(len(row), len(head), f"{name}: {head[0]} table, row {row[:2]}")

    def test_the_converted_tables_keep_every_row_and_cell(self):
        for name in PAGE_NAMES:
            text = page_text(name)
            tables = tl.split_tables(text)
            xml = ms.convert(text)
            stored = re.findall(r"<table.*?</table>", xml, flags=re.S)
            self.assertEqual(len(stored), len(tables), name)
            for (head, body), table in zip(tables, stored):
                rows = re.findall(r"<tr>(.*?)</tr>", table, flags=re.S)
                self.assertEqual(len(rows), len(body) + 1, f"{name}: {head[0]}")
                for row in rows:
                    self.assertEqual(len(re.findall(r"<t[hd][ >]", row)), len(head), f"{name}: {head[0]}")

    def test_the_text_of_a_cell_survives_the_split_into_paragraphs(self):
        for name in PAGE_NAMES:
            for head, body in tl.split_tables(page_text(name)):
                if tl.kind(head) not in ("vault", "fields"):
                    continue
                column = [tl.plain(h).strip() for h in head].index("Definition" if tl.kind(head) == "vault" else "Description")
                for row in body:
                    self.assertEqual(" ".join(tl.paragraphs(row[column])), row[column], f"{name}: {row[0]}")

    def test_the_vault_and_fields_tables_of_every_page_cover_the_page_width(self):
        for name in PAGE_NAMES:
            widths = tl.document_widths(page_text(name))
            self.assertEqual(sum(widths["vault"]), tl.PAGE_WIDTH, name)
            self.assertEqual(sum(widths["fields"]), tl.PAGE_WIDTH, name)
            self.assertGreater(widths["vault"][2], widths["vault"][0], name)
            self.assertGreater(widths["fields"][6], max(widths["fields"][:6]), name)


class AppearanceTests(unittest.TestCase):
    def test_only_the_properties_that_are_not_wide_are_changed(self):
        props = [{"key": "content-appearance-draft", "value": "full-width", "version": {"number": 3}},
                 {"key": "content-appearance-published", "value": "default", "version": {"number": 2}}]
        self.assertEqual(sc.appearance_changes(props), [("content-appearance-published", 2)])

    def test_a_missing_property_is_created(self):
        self.assertEqual(sc.appearance_changes([]), [("content-appearance-draft", None), ("content-appearance-published", None)])


if __name__ == "__main__":
    unittest.main()
