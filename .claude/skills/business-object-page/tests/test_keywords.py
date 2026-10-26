"""The keyword strategy: which words of a Definition are bold."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bold_terms  # noqa: E402
import build_lucid_global as g  # noqa: E402
import keywords  # noqa: E402
import validate_page as vp  # noqa: E402

PAGES = Path(__file__).resolve().parents[4] / "Rosetta" / "Business_Objects"
HISTORY = ("The table that records every gender recorded for a person over time, so earlier values stay. "
           "It is the default; `sat_x__y` is the exception.")


class ProposeTests(unittest.TestCase):
    def test_behaviours_and_qualifiers_come_with_the_subject(self):
        out = keywords.propose(HISTORY, ["gender"])
        self.assertEqual(keywords.bold_phrases(out), ["gender", "over time", "earlier values stay", "the default"])

    def test_the_opening_and_the_names_in_backticks_stay_plain(self):
        out = keywords.propose("The table that holds the identifier of `hub_x`. It carries no description of it.", ["identifier"])
        self.assertTrue(out.startswith("The table that holds"))
        self.assertIn("`hub_x`", out)
        self.assertEqual(keywords.bold_phrases(out), ["identifier", "carries no description"])

    def test_at_most_four_phrases(self):
        text = ("The table that holds only the current value, replaced when it changes, over time, so earlier values stay. "
                "It is the exception.")
        self.assertLessEqual(len(keywords.bold_phrases(keywords.propose(text, ["value"]))), 4)

    def test_a_phrase_that_is_not_in_the_text_is_an_error(self):
        with self.assertRaises(ValueError):
            keywords.propose("The table that holds a thing.", ["nothing"])

    def test_it_is_idempotent(self):
        once = keywords.propose(HISTORY, ["gender"])
        self.assertEqual(keywords.propose(once, ["gender"]), once)


class CheckTests(unittest.TestCase):
    def test_a_good_definition_passes(self):
        self.assertEqual(keywords.check_bold("x", "The table that holds the **identifier** and **a thing**.", 2, 4), [])

    def test_too_few_too_many_long_and_unclosed(self):
        self.assertTrue(keywords.check_bold("x", "The table that holds **one**.", 2, 4))
        self.assertTrue(keywords.check_bold("x", "**a** **b** **c** **d** **e**", 2, 4))
        self.assertTrue(keywords.check_bold("x", "**one two three four five** and **b**", 2, 4))
        self.assertTrue(keywords.check_bold("x", "an **unclosed marker and **b", 2, 4)
                        or keywords.check_bold("x", "**a** and **b", 2, 4))

    def test_a_name_in_backticks_and_the_opening_cannot_be_bold(self):
        self.assertTrue(keywords.check_bold("x", "The table that **`hub_x`** and **b**", 2, 4))
        self.assertTrue(keywords.check_bold("x", "**The table that** holds **b**", 2, 4))


class RealPagesTests(unittest.TestCase):
    def test_every_vault_object_has_its_phrases_and_they_are_in_its_definition(self):
        seen = set()
        for stem in g.PAGES:
            page = vp.parse_page((PAGES / f"{stem}.md").read_text(encoding="utf-8"))
            tables = page.tables("Vault objects")
            for row in tables[0] if tables else []:
                name = row["Name"].strip("`")
                seen.add(name)
                self.assertIn(name, bold_terms.SUBJECTS, name)
                self.assertEqual(keywords.propose(row["Definition"], bold_terms.SUBJECTS[name]), row["Definition"], name)
        self.assertEqual(seen, set(bold_terms.SUBJECTS))

    def test_diagrams_receive_the_definition_without_markers(self):
        import build_diagram as bd
        page = (PAGES / "Natural_Person.md").read_text(encoding="utf-8")
        model = bd.load_model(page)
        self.assertTrue(model.nodes)
        for node in model.nodes:
            self.assertNotIn("**", node.definition)


if __name__ == "__main__":
    unittest.main()
