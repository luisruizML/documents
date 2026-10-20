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
        text = page("An illustrative order placed in Samoa.\n\n| **sample_order_bk** | **total_amount** | **currency_code** |\n| --- | --- | --- |\n| ORD-0001 | 120.00 | WST |\n", "")
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
        ]
        for old, kind in cases:
            with self.subTest(kind=kind):
                new = old.replace("one row per", "one line per", 1)
                self.assertTrue(has(errors(old, new), "grain", vp.GRAIN_PREFIX[kind]))

    def test_type_not_on_list_is_rejected(self):
        errs = errors("| `currency_code` | | `string` |", "| `currency_code` | | `varchar(10)` |")
        self.assertTrue(has(errs, "type", "varchar(10)"))

    def test_decimal_needs_precision_and_scale(self):
        for bad in ("decimal", "decimal(18)"):
            with self.subTest(bad=bad):
                self.assertTrue(has(errors("`decimal(18,2)`", f"`{bad}`"), "type", bad))

    def test_amount_column_must_be_decimal(self):
        self.assertTrue(has(errors("`decimal(18,2)`", "`double`"), "type", "_amount"))

    def test_representation_terms_fix_types(self):
        cases = [
            ("| `status_code` | | `string` |", "| `status_code` | | `int` |", "_code"),
            ("| `status_name` | | `string` |", "| `status_name` | | `int` |", "_name"),
            ("| `event_dts` | | `timestamptz` |", "| `event_dts` | | `date` |", "_dts"),
        ]
        for old, new, term in cases:
            with self.subTest(term=term):
                self.assertTrue(has(errors(old, new), "type", term))

    def test_every_vault_object_has_a_fields_table_and_no_extra(self):
        self.assertTrue(has(errors("### sat_sample_order__pricing", "### sat_sample_order__other"), "fields", "sat_sample_order__pricing"))
        self.assertTrue(has(errors("### sat_sample_order__pricing", "### sat_sample_order__other"), "fields", "sat_sample_order__other"))

    def test_a_reference_table_is_not_a_vault_object_type(self):
        row = "| Reference table | `ref_order_status` | one row per code | — |"
        text = FIXTURE.read_text(encoding="utf-8").replace("| Non-historized Link |", row + chr(10) + "| Non-historized Link |", 1)
        self.assertTrue(has(vp.validate(text), "name", "Reference table"))

    def test_null_and_personal_data_are_yes_or_no(self):
        errs = errors("| `status_code` | | `string` | No | No | — |", "| `status_code` | | `string` | Maybe | No | — |")
        self.assertTrue(has(errs, "fields", "Maybe"))

    def test_hub_fields_include_hash_and_business_key(self):
        errs = errors("| `sample_order_bk` | ● | `string` | No | No | — | The order number |\n", "")
        self.assertTrue(has(errs, "fields", "sample_order_bk"))

    def test_satellite_fields_carry_parent_hash_key_and_no_business_key(self):
        errs = errors("| `currency_code` | | `string` | No | No | — | ISO 4217 code, e.g. `WST`, `PGK`, `NZD` |", "| `currency_code` | | `string` | No | No | — | ISO 4217 code, e.g. `WST`, `PGK`, `NZD` |\n| `sample_order_bk` | ● | `string` | No | No | — | wrong |")
        self.assertTrue(has(errs, "fields", "_bk"))


class RemainingSectionTests(unittest.TestCase):
    ENDPOINTS = (
        "| **Source** | **Endpoint** | **Bronze table** | **Provides** |\n| --- | --- | --- | --- |\n"
        "| registry | taxpayers | `bronze.registry__taxpayers` | Taxpayer records |"
    )

    def test_sources_is_declarative_or_empty_statement(self):
        self.assertEqual([e for e in errors("No endpoints declared yet", self.ENDPOINTS) if e.startswith("sources:")], [])
        self.assertTrue(has(errors("No endpoints declared yet", "We will probably call some API."), "sources", ""))

    def test_bronze_table_name_pattern(self):
        bad = self.ENDPOINTS.replace("bronze.registry__taxpayers", "Bronze.Registry_Taxpayers")
        self.assertTrue(has(errors("No endpoints declared yet", bad), "sources", "Bronze.Registry_Taxpayers"))

    def test_mapping_record_requires_declared_endpoints(self):
        mapping = "No endpoints declared yet\n\n| Bronze path | Decision | Vault object | Rule |\n| --- | --- | --- | --- |\n| `a.b` | Business key | `hub_sample_order` | 1 |"
        self.assertTrue(has(errors("No endpoints declared yet", mapping), "sources", "mapping"))

    def test_jurisdictions_table_columns(self):
        bad = errors("| **Edge case** | **Where it happens** |", "| **Edge** | **Where it happens** |")
        self.assertTrue(has(bad, "jurisdictions", "Edge case"))
        ok = errors(
            page().split("## Jurisdictions map")[1].split("## Examples")[0].strip(),
            "No jurisdiction differences known",
        )
        self.assertEqual([e for e in ok if e.startswith("jurisdictions:")], [])

    def test_diagram_needs_image_link(self):
        self.assertTrue(has(errors("![Sample Order cluster](Sample_Order.png)\n\n![Sample Order cluster, full](Sample_Order_Full.png)", "no picture"), "diagram", "image"))

    def test_diagram_needs_simple_and_full_versions(self):
        errs = errors("\n\n![Sample Order cluster, full](Sample_Order_Full.png)", "")
        self.assertTrue(has(errs, "diagram", "_Full.png"))

    def test_diagram_file_must_exist_when_base_dir_given(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(has(vp.validate(page(), base_dir=Path(d)), "diagram", "Sample_Order.png"))
            (Path(d) / "Sample_Order.png").write_bytes(b"x")
            (Path(d) / "Sample_Order_Full.png").write_bytes(b"x")
            self.assertEqual([e for e in vp.validate(page(), base_dir=Path(d)) if e.startswith("diagram:")], [])

    def test_decisions_table_columns(self):
        self.assertTrue(has(errors("| **Decision** | **Owner** |", "| **Question** | **Owner** |"), "decisions", "Decision"))
        table = "| **Decision** | **Owner** | **How it is decided** | **Decide by** |\n| --- | --- | --- | --- |\n| Whether a split shipment is one event or several | Data Architecture Engineer | Agreed with Finance | Before the first mapping that needs it |"
        self.assertEqual([e for e in errors(table, "None open") if e.startswith("decisions:")], [])

    def test_cli_exit_codes(self):
        import tempfile
        self.assertEqual(vp.main([str(FIXTURE)]), 0)
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.md"
            bad.write_text(page("| Status | Draft |", "| Status | Final |"), encoding="utf-8")
            self.assertEqual(vp.main([str(bad)]), 1)


class TableFormatTests(unittest.TestCase):
    def test_table_header_must_be_bold(self):
        errs = errors("| **Type** | **Name** |", "| Type | **Name** |")
        self.assertTrue(has(errs, "format", "Type"))

    def test_every_table_is_checked_for_bold_headers(self):
        errs = errors("| **Field** | **Value** |", "| Field | Value |")
        self.assertTrue(has(errs, "format", "Field"))

    def test_fields_table_needs_pii_and_default_columns(self):
        errs = errors("| **PII** |", "| **Personal data** |")
        self.assertTrue(has(errs, "fields", "PII"))
        errs = errors(" **Default** |", " **Other** |")
        self.assertTrue(has(errs, "fields", "Default"))

    def test_default_cell_must_not_be_empty(self):
        errs = errors("| `status_code` | | `string` | No | No | — |", "| `status_code` | | `string` | No | No | |")
        self.assertTrue(has(errs, "fields", "Default"))

    def test_base_columns_carry_their_indicator(self):
        cases = [
            ("| `sample_order_hk` | ◆ |", "| `sample_order_hk` | |", "sample_order_hk"),
            ("| `sample_order_bk` | ● |", "| `sample_order_bk` | ◆ |", "sample_order_bk"),
            ("| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |\n| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |\n\n### lnk_customer", "| `load_dts` | | `timestamptz` | No | No | — | When Nexus first loaded the row |\n| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |\n\n### lnk_customer", "load_dts"),
            ("| `hashdiff` | Δ |", "| `hashdiff` | ▪ |", "hashdiff"),
        ]
        for old, new, col in cases:
            with self.subTest(col=col):
                self.assertTrue(has(errors(old, new), "fields", col))

    def test_descriptive_column_has_no_indicator(self):
        errs = errors("| `currency_code` | | `string` |", "| `currency_code` | ● | `string` |")
        self.assertTrue(has(errs, "fields", "currency_code"))

    def test_own_hash_key_only_on_hub(self):
        errs = errors("| `customer_hk` | ◇ |", "| `customer_hk` | ◆ |")
        self.assertTrue(has(errs, "fields", "customer_hk"))


class DescriptionTests(unittest.TestCase):
    def test_code_column_needs_example_values(self):
        errs = errors("ISO 4217 code, e.g. `WST`, `PGK`, `NZD`", "ISO 4217 code")
        self.assertTrue(has(errs, "fields", "currency_code"))

    def test_examples_need_at_least_three_values(self):
        errs = errors("e.g. `WST`, `PGK`, `NZD`", "e.g. `WST`, `PGK`")
        self.assertTrue(has(errs, "fields", "three"))

    def test_closed_list_is_accepted_in_place_of_examples(self):
        errs = errors("One of `open`, `paid`, `cancelled`", "One of `open`, `paid`")
        self.assertEqual([e for e in errs if e.startswith("fields:")], [])

    def test_non_code_column_needs_no_examples(self):
        errs = errors("| Order total |", "| Order total |")
        self.assertEqual([e for e in errs if e.startswith("fields:")], [])


class TemplateTests(unittest.TestCase):
    def test_template_has_all_sections_and_headers(self):
        text = (HERE.parent / "assets" / "template.md").read_text(encoding="utf-8")
        parsed = vp.parse_page(text)
        self.assertEqual(parsed.order, vp.SECTIONS)
        self.assertEqual(list(parsed.tables("Vault objects")[0][0].keys()), ["Type", "Name", "Grain", "Business key"])
        self.assertEqual(list(parsed.tables("Jurisdictions map")[0][0].keys()), vp.JURISDICTION_COLUMNS)
        self.assertEqual(list(parsed.tables("Open decisions")[0][0].keys()), vp.DECISION_COLUMNS)
        fields = vp._fields_tables(parsed)
        self.assertEqual(list(next(iter(fields.values()))[0].keys()), ["Column", "Role", "Type", "Null", "PII", "Default", "Description"])
        self.assertEqual([r["Field"] for r in parsed.tables("Header")[0]], vp.HEADER_FIELDS)


if __name__ == "__main__":
    unittest.main()
