"""The Contact Point page and the nesting of Base Parcels."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_page as vp  # noqa: E402

PAGES = Path(__file__).resolve().parents[4] / "Rosetta" / "Business_Objects"


def read(stem):
    return (PAGES / f"{stem}.md").read_text(encoding="utf-8")


class ContactPointTests(unittest.TestCase):
    def test_the_page_validates(self):
        self.assertEqual(vp.validate(read("Contact_Point"), base_dir=PAGES), [])

    def test_the_six_objects_and_the_one_link_to_party(self):
        rows = vp.parse_page(read("Contact_Point")).tables("Vault objects")[0]
        names = [r["Name"].strip("`") for r in rows]
        self.assertEqual(names, ["hub_contact_point", "lnk_contact_point__party", "sat_contact_point__description", "sat_contact_point__channel",
                                 "sat_contact_point__party__usage", "sat_contact_point__party__consent"])
        link = next(r for r in rows if r["Name"].strip("`") == "lnk_contact_point__party")
        self.assertIn("`hub_party`", link["Business key"])

    def test_the_value_is_personal_data_and_only_in_one_satellite(self):
        page = vp.parse_page(read("Contact_Point"))
        fields = vp._fields_tables(page)
        pii = [(t, r["Column"]) for t, rows in fields.items() for r in rows if r["PII"] == "Yes"]
        self.assertEqual(pii, [("sat_contact_point__description", "`value_text`")])

    def test_consent_status_is_a_closed_list_and_the_others_are_lists(self):
        fields = vp._fields_tables(vp.parse_page(read("Contact_Point")))
        flags = {r["Column"].strip("`"): r["Code List"] for r in fields["sat_contact_point__party__consent"]}
        self.assertEqual(flags["consent_status_code"], "Closed")
        self.assertEqual(flags["channel_code"], "List")
        self.assertEqual(flags["purpose_code"], "List")

    def test_every_code_column_of_the_page_has_a_row_on_the_code_list_page(self):
        rows = vp.code_list_table(read("Code_List"))
        fields = vp._fields_tables(vp.parse_page(read("Contact_Point")))
        for table, table_rows in fields.items():
            for r in table_rows:
                if r["Code List"] in ("List", "Closed"):
                    self.assertIn(f"{table}.{r['Column'].strip('`')}", rows)


class ParcelNestingTests(unittest.TestCase):
    def test_the_page_validates_and_has_the_hierarchy_pair(self):
        text = read("Base_Parcel")
        self.assertEqual(vp.validate(text, base_dir=PAGES), [])
        names = [r["Name"].strip("`") for r in vp.parse_page(text).tables("Vault objects")[0]]
        self.assertIn("lnk_base_parcel__base_parcel_hierarchy", names)
        self.assertIn("sat_base_parcel__base_parcel_hierarchy__membership", names)

    def test_the_hierarchy_has_the_same_columns_as_the_structure_one(self):
        def columns(stem, table):
            return [r["Column"].strip("`").replace("built_structure", "X").replace("base_parcel", "X")
                    for r in vp._fields_tables(vp.parse_page(read(stem)))[table]]
        self.assertEqual(columns("Base_Parcel", "lnk_base_parcel__base_parcel_hierarchy"),
                         columns("Built_Structure", "lnk_built_structure__built_structure_hierarchy"))
        self.assertEqual(columns("Base_Parcel", "sat_base_parcel__base_parcel_hierarchy__membership"),
                         columns("Built_Structure", "sat_built_structure__built_structure_hierarchy__membership"))

    def test_a_member_is_joined_to_its_parent_with_both_roles(self):
        link = [r for r in vp._fields_tables(vp.parse_page(read("Base_Parcel")))["lnk_base_parcel__base_parcel_hierarchy"]]
        self.assertEqual([r["Column"].strip("`") for r in link[:2]], ["parent_base_parcel_hk", "member_base_parcel_hk"])


if __name__ == "__main__":
    unittest.main()
