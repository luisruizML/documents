import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import validate_page as vp  # noqa: E402

PAGES = HERE.parents[3] / "Rosetta" / "Business_Objects"
SKIP = {"Index", "Vault_Objects_Inventory", "Platform"}


def pages():
    return [p for p in sorted(PAGES.glob("*.md")) if p.stem not in SKIP]


def fields_of(path):
    return vp._fields_tables(vp.parse_page(path.read_text(encoding="utf-8")))


class CodeListRowsOfTheRealPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = vp.code_list_table((PAGES / "Code_List.md").read_text(encoding="utf-8"))
        cls.columns = {}
        for path in pages():
            for table, rows in fields_of(path).items():
                for r in rows:
                    cls.columns[f"{table}.{vp._strip(r['Column'])}"] = r

    def test_every_page_agrees_with_the_code_list_table(self):
        for path in pages():
            text = path.read_text(encoding="utf-8")
            page = vp.parse_page(text)
            self.assertEqual(vp.check_code_list_rows(page, text, PAGES), [], path.stem)

    def test_every_row_names_a_column_that_exists(self):
        self.assertEqual([k for k in self.rows if k not in self.columns], [])

    def test_every_row_has_its_four_cells_filled(self):
        for key, cells in self.rows.items():
            self.assertEqual(len(cells), 4, key)
            self.assertTrue(all(c.strip() for c in cells), key)

    def test_a_row_is_flagged_list_or_closed_to_match(self):
        for key, cells in self.rows.items():
            flag = self.columns[key]["Code List"].strip()
            self.assertEqual(flag == "Closed", cells[1].startswith("Closed list"), key)

    def test_a_list_row_says_which_list_and_a_closed_row_gives_its_values(self):
        for key, cells in self.rows.items():
            if cells[1].startswith("Closed list"):
                self.assertGreaterEqual(cells[3].count("`"), 4, key)
            else:
                self.assertIn("`", cells[1], key)

    def test_rows_are_grouped_by_page_then_each_hub_with_its_satellites_then_each_link_with_its_satellites(self):
        pos = {key: i for i, key in enumerate(self.rows)}
        for path in pages():
            tabs = list(fields_of(path))
            parents = [t for t in tabs if t.startswith("hub_")] + [t for t in tabs if t.startswith("lnk_")]
            expected = []
            for parent in parents:
                name = parent.split("_", 1)[1]
                expected += [parent] + [t for t in tabs if t.startswith("sat_") and t[4:].rsplit("__", 1)[0] == name]
            expected += [t for t in tabs if t.startswith("sat_") and t not in expected]
            seen = []
            for key in sorted((k for k in pos if k.split(".")[0] in tabs), key=pos.get):
                t = key.split(".")[0]
                if not seen or seen[-1] != t:
                    seen.append(t)
            self.assertEqual(seen, [t for t in expected if t in seen], path.stem)

    def test_no_key_appears_twice(self):
        text = (PAGES / "Code_List.md").read_text(encoding="utf-8")
        keys = [l.split("|")[1].strip() for l in text.splitlines() if l.startswith("| `") and "." in l.split("|")[1] and "`" in l.split("|")[1]]
        dupes = [k for k in set(keys) if keys.count(k) > 1 and k in self.rows]
        self.assertEqual(dupes, [])


if __name__ == "__main__":
    unittest.main()
