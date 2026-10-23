"""A family page has no Hub of its own: its objects are defined on the pages of its parts."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import build_diagram as bd
import validate_page as vp

PAGES = HERE.parents[3] / "Rosetta" / "Business_Objects"


class FamilyPageTests(unittest.TestCase):
    def text(self, name="Immovable_Assets"):
        return (PAGES / f"{name}.md").read_text(encoding="utf-8")

    def test_the_real_family_page_validates(self):
        self.assertEqual(vp.validate(self.text(), base_dir=PAGES), [])

    def test_the_parts_are_the_pages_in_the_table_rows(self):
        members = vp.family_members(vp.parse_page(self.text()))
        self.assertEqual(sorted(set(members)), ["Base_Parcel", "Built_Structure"])

    def test_the_movable_family_validates_and_merges_its_three_parts(self):
        text = self.text("Movable_Assets")
        self.assertEqual(vp.validate(text, base_dir=PAGES), [])
        self.assertEqual(sorted(set(vp.family_members(vp.parse_page(text)))), ["Base_Asset", "Model_Catalog", "Swappable_Component"])
        merged = bd.load_model(bd.merge_family(text, PAGES), ["hub_location", "hub_party"])
        self.assertEqual(len([n for n in merged.nodes if not n.external]), 29)

    def test_an_ordinary_page_is_not_a_family(self):
        self.assertIsNone(vp.family_members(vp.parse_page(self.text("Party"))))

    def test_a_family_that_links_one_page_is_refused(self):
        text = "\n".join(l.replace("[Built Structure](Built_Structure.md)", "Built Structure") if l.startswith("| [Built Structure]") else l
                         for l in self.text().split("\n"))
        errors = vp.validate(text)
        self.assertTrue(any("family page" in e for e in errors), errors)

    def test_the_diagram_merges_the_parts_without_repeating_an_object(self):
        merged = bd.load_model(bd.merge_family(self.text(), PAGES), ["hub_location", "hub_party"])
        names = [n.name for n in merged.nodes]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len([n for n in merged.nodes if not n.external]), 25)

    def test_an_ordinary_page_is_merged_unchanged(self):
        text = self.text("Party")
        self.assertEqual(bd.merge_family(text, PAGES), text)


if __name__ == "__main__":
    unittest.main()
