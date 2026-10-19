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


class VaultObjectTests(unittest.TestCase):
    def test_draft_style_name_is_rejected_with_lowercase_hint(self):
        errs = errors("| Hub | `hub_sample_order` |", "| Hub | `Hub_Sample_Order` |")
        self.assertTrue(has(errs, "name", "hub_sample_order"))

    def test_hub_with_double_underscore_is_rejected(self):
        errs = errors("| Hub | `hub_sample_order` |", "| Hub | `hub_sample__order` |")
        self.assertTrue(has(errs, "name", "hub_sample__order"))

    def test_link_parts_must_be_alphabetical(self):
        errs = errors("`lnk_customer__sample_order` | one", "`lnk_sample_order__customer` | one")
        self.assertTrue(has(errs, "name", "alphabetical"))

    def test_link_to_hub_on_another_page_is_accepted(self):
        self.assertEqual([e for e in errors() if e.startswith("name:")], [])

    def test_satellite_parent_must_be_on_page(self):
        errs = errors("`sat_sample_order__pricing` |", "`sat_missing_thing__pricing` |")
        self.assertTrue(has(errs, "name", "parent"))

    def test_satellite_descriptor_is_after_last_double_underscore(self):
        text = page("`sat_sample_order__pricing` |", "`sat_customer__sample_order__pricing` |")
        errs = vp.validate(text)
        self.assertFalse(has(errs, "name", "parent"))

    def test_name_over_63_characters_is_rejected(self):
        long = "hub_" + "a" * 60
        self.assertTrue(has(errors("`hub_sample_order` |", f"`{long}` |"), "name", "63"))

    def test_short_unapproved_token_is_rejected(self):
        text = page("`hub_sample_order` |", "`hub_tp_account` |")
        self.assertTrue(has(vp.validate(text), "name", "tp"))
        self.assertFalse(has(vp.validate(text, approved=frozenset({"tp"})), "name", "tp"))

    def test_grain_prefix_per_type(self):
        cases = [
            ("one row per business key |", "Hub"),
            ("one row per distinct combination of customer", "Link"),
            ("one row per parent key, for each", "Satellite"),
            ("one row per occurrence of a shipment", "Non-historized Link"),
            ("one row per code |", "Reference table"),
        ]
        for old, kind in cases:
            with self.subTest(kind=kind):
                new = old.replace("one row per", "one line per", 1)
                self.assertTrue(has(errors(old, new), "grain", vp.GRAIN_PREFIX[kind]))

    def test_type_not_on_list_is_rejected(self):
        errs = errors("| `currency_code` | `string` |", "| `currency_code` | `varchar(10)` |")
        self.assertTrue(has(errs, "type", "varchar(10)"))

    def test_decimal_needs_precision_and_scale(self):
        for bad in ("decimal", "decimal(18)"):
            with self.subTest(bad=bad):
                self.assertTrue(has(errors("`decimal(18,2)`", f"`{bad}`"), "type", bad))

    def test_amount_column_must_be_decimal(self):
        self.assertTrue(has(errors("`decimal(18,2)`", "`double`"), "type", "_amount"))

    def test_representation_terms_fix_types(self):
        cases = [
            ("| `status_code` | `string` |", "| `status_code` | `int` |", "_code"),
            ("| `status_name` | `string` |", "| `status_name` | `int` |", "_name"),
            ("| `event_dts` | `timestamptz` |", "| `event_dts` | `date` |", "_dts"),
        ]
        for old, new, term in cases:
            with self.subTest(term=term):
                self.assertTrue(has(errors(old, new), "type", term))

    def test_every_vault_object_has_a_fields_table_and_no_extra(self):
        self.assertTrue(has(errors("### ref_order_status", "### ref_other_status"), "fields", "ref_order_status"))
        self.assertTrue(has(errors("### ref_order_status", "### ref_other_status"), "fields", "ref_other_status"))

    def test_null_and_personal_data_are_yes_or_no(self):
        errs = errors("| `status_code` | `string` | No | No |", "| `status_code` | `string` | Maybe | No |")
        self.assertTrue(has(errs, "fields", "Maybe"))

    def test_hub_fields_include_hash_and_business_key(self):
        errs = errors("| `sample_order_bk` | `string` | No | No | The order number |\n", "")
        self.assertTrue(has(errs, "fields", "sample_order_bk"))

    def test_satellite_fields_carry_parent_hash_key_and_no_business_key(self):
        errs = errors("| `currency_code` | `string` | No | No | ISO 4217 code |", "| `currency_code` | `string` | No | No | ISO 4217 code |\n| `sample_order_bk` | `string` | No | No | wrong |")
        self.assertTrue(has(errs, "fields", "_bk"))


if __name__ == "__main__":
    unittest.main()
