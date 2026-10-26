import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_lucid_global as g  # noqa: E402
import platform_usage as pu  # noqa: E402


class PlatformUsageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.edges = g.load_all()
        cls.listed = pu.listed_code_columns()
        cls.users = pu.code_list_users(cls.nodes)

    def test_the_code_list_page_names_the_list_columns_and_leaves_closed_lists_out(self):
        for key in ("hub_natural_person.jurisdiction_code", "sat_natural_person__demographics.gender_code",
                    "sat_geometry__shape.srs_code", "sat_natural_person__lifecycle.event_code",
                    "sat_location__natural_person__usage.role_code"):
            self.assertIn(key, self.listed)
        for closed in ("sat_rrr__status.status_code", "sat_code_list__access.access_code",
                       "sat_load_configuration__mechanism.mechanism_code", "sat_code_value__applicability.party_type_code"):
            self.assertNotIn(closed, self.listed)

    def test_a_repeated_column_name_is_told_apart_by_its_table(self):
        self.assertIn("sat_location__natural_person__usage.role_code", self.listed)
        self.assertIn("sat_legal_entity__natural_person__representation.role_code", self.listed)
        self.assertNotIn("sat_code_list__access.role_code", self.listed)

    def test_a_postal_code_is_not_a_list_column(self):
        self.assertNotIn("postal_code", self.users["sat_address__description"])

    def test_objects_of_the_code_list_page_are_not_users(self):
        self.assertFalse([n for n in self.users if n.startswith(("hub_code_", "sat_code_", "lnk_code_"))])

    def test_hubs_satellites_and_the_load_configuration_are_users(self):
        for name in ("hub_natural_person", "hub_address", "sat_natural_person__name", "sat_location__natural_person__usage",
                     "sat_load_configuration__mechanism"):
            self.assertIn(name, self.users)

    def test_every_user_column_exists_in_the_object(self):
        for name, columns in self.users.items():
            have = {r["Column"] for r in self.nodes[name].rows}
            self.assertTrue(set(columns) <= have, name)

    def test_load_configuration_users_are_the_twin_pairs(self):
        users = pu.load_configuration_users(self.nodes)
        self.assertEqual(len(users), 6)
        for name in users:
            self.assertTrue(name.startswith("sat_natural_person__"))
        self.assertIn("sat_natural_person__demographics", users)
        self.assertIn("sat_natural_person__demographics_history", users)

    def test_uses_lines_start_at_the_two_platform_hubs(self):
        lines = pu.uses_lines(self.nodes)
        self.assertEqual({a for a, _ in lines}, {"hub_code_list", "hub_load_configuration"})
        self.assertEqual(len(lines), len(self.users) + 6)
        self.assertEqual(len({b for _, b in lines if _ == "hub_code_list"}), len(self.users))


if __name__ == "__main__":
    unittest.main()
