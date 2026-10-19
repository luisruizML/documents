import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import validate_page as vp  # noqa: E402

FIXTURE = HERE / "fixtures" / "valid_page.md"


def page(old=None, new=None):
    text = FIXTURE.read_text(encoding="utf-8")
    if old is not None:
        assert old in text, f"fixture does not contain {old!r}"
        text = text.replace(old, new, 1)
    return text


def errors(old=None, new=None, **kw):
    return vp.validate(page(old, new), **kw)


def has(errs, tag, fragment):
    return any(e.startswith(tag + ":") and fragment in e for e in errs)


class CoreTests(unittest.TestCase):
    def test_valid_fixture_has_no_errors(self):
        self.assertEqual(vp.validate(page()), [])

    def test_crlf_line_endings_give_same_result(self):
        self.assertEqual(vp.validate(page().replace("\n", "\r\n")), [])

    def test_missing_section_is_reported(self):
        self.assertTrue(has(errors("## Diagram", "## Pictures"), "section", "Diagram"))

    def test_sections_out_of_order_are_reported(self):
        text = page().replace("## Definition", "## TMP").replace("## Header", "## Definition").replace("## TMP", "## Header")
        self.assertTrue(has(vp.validate(text), "section", "order"))

    def test_blank_section_is_reported(self):
        text = page("An illustrative order placed in Samoa.\n\n| sample_order_bk | total_amount | currency_code |\n| --- | --- | --- |\n| ORD-0001 | 120.00 | WST |\n", "")
        self.assertTrue(has(vp.validate(text), "section", "Examples"))

    def test_bad_owner_domain(self):
        self.assertTrue(has(errors("| Owner domain | Finance |", "| Owner domain | Treasury |"), "header", "Treasury"))

    def test_bad_scope_and_status(self):
        self.assertTrue(has(errors("| Scope | Shared |", "| Scope | Global-ish |"), "header", "Global-ish"))
        self.assertTrue(has(errors("| Status | Draft |", "| Status | Final |"), "header", "Final"))

    def test_shared_with_accepts_several_domains(self):
        errs = errors("| Shared with | Taxation Contributions and Licences |", "| Shared with | Registries, Finance |")
        self.assertEqual([e for e in errs if e.startswith("header:")], [])


if __name__ == "__main__":
    unittest.main()
