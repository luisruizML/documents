import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_diagram as bd  # noqa: E402
import build_erd as be  # noqa: E402

FIXTURE = HERE / "fixtures" / "valid_page.md"


class ErdTests(unittest.TestCase):
    def setUp(self):
        self.erd = be.build_erd([bd.load_model(FIXTURE.read_text(encoding="utf-8"))])
        self.entities = {e["name"]: e for e in self.erd["entities"]}

    def test_one_entity_per_vault_object_and_external_hub(self):
        for name in ("hub_sample_order", "sat_sample_order__pricing", "lnk_customer__sample_order", "hub_customer"):
            self.assertIn(name, self.entities)

    def test_columns_carry_type_nullability_and_keys(self):
        cols = {a["name"]: a for a in self.entities["hub_sample_order"]["attributes"]}
        self.assertEqual(cols["sample_order_hk"]["key"], "PK")
        self.assertEqual(cols["sample_order_bk"]["key"], "BK")
        self.assertEqual(cols["load_dts"]["type"], "timestamptz NOT NULL")

    def test_every_entity_has_a_column(self):
        for e in self.erd["entities"]:
            self.assertTrue(e["attributes"], e["name"])

    def test_child_points_to_parent_through_the_parent_hash_key(self):
        rel = next(r for r in self.erd["relationships"] if (r["from"], r["to"]) == ("sat_sample_order__pricing", "hub_sample_order"))
        self.assertEqual(rel["fromAttribute"], "sample_order_hk")
        self.assertEqual(rel["toCardinality"], "one")

    def test_pages_sharing_an_object_give_one_entity(self):
        model = bd.load_model(FIXTURE.read_text(encoding="utf-8"))
        erd = be.build_erd([model, model])
        self.assertEqual(len(erd["entities"]), len(self.erd["entities"]))


if __name__ == "__main__":
    unittest.main()
