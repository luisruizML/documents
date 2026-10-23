import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import validate_page as vp  # noqa: E402

INDEX = HERE.parents[3] / "Rosetta" / "Business_Objects" / "Index.md"


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.text = INDEX.read_text(encoding="utf-8")

    def test_every_page_section_is_explained(self):
        for name in vp.SECTIONS:
            self.assertIn(f"| **{name}** |", self.text, name)

    def test_every_role_symbol_is_explained(self):
        for symbol in vp.ROLES:
            self.assertIn(symbol, self.text, symbol)

    def test_header_values_are_listed(self):
        for value in vp.SCOPES + vp.STATUSES:
            self.assertIn(value, self.text, value)

    def test_vault_object_types_and_grains_are_listed(self):
        for kind, grain in vp.GRAIN_PREFIX.items():
            self.assertIn(kind, self.text)
            self.assertIn(grain, self.text)

    def test_vault_object_colors_are_listed(self):
        for color in ("#3A0CA3", "#45E3CD", "#F72586"):
            self.assertIn(color, self.text)

    def test_both_diagrams_of_the_reference_page_are_shown(self):
        self.assertIn("(images/Diagrams_Natural_Person_Simplified.png)", self.text)
        self.assertIn("(images/Diagrams_Natural_Person_Full.png)", self.text)

    def test_index_shows_graph_simplified_version_and_full_version_in_that_order_each_under_a_title(self):
        order = [("### Graph", "images/Lucid_Simplified_Graph.png", "9219fb1c-3d87-4919-ac1b-2cc4f49a33c4"),
                 ("### Simplified version", "images/Lucid_Simplified_Version.png", "4ca7a389-f932-49ff-8d30-64ecf58eb555"),
                 ("### Full version", "images/Lucid_Full_Model.png", "75d0c576-8f34-4e96-81e8-5fc5c189996f")]
        at = [[self.text.index(part) for part in step] for step in order]
        for position in at:
            self.assertEqual(position, sorted(position))
        self.assertEqual(sorted(p[0] for p in at), [p[0] for p in at])

    def test_index_shows_the_global_lucid_model(self):
        self.assertIn("## The full picture", self.text)
        self.assertIn("lucid.app/lucidchart/75d0c576-8f34-4e96-81e8-5fc5c189996f", self.text)
        self.assertNotIn("Global_Model.png", self.text)

    def test_every_table_header_is_bold(self):
        self.assertEqual(vp.check_bold_headers(self.text), [])


if __name__ == "__main__":
    unittest.main()
