import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import md_to_storage as ms  # noqa: E402
import sync_confluence as sc  # noqa: E402


class ConvertTests(unittest.TestCase):
    def test_headings_paragraphs_and_inline_marks(self):
        out = ms.convert("## Title" + chr(10) + chr(10) + "Some **bold**, *italic* and `code`.")
        self.assertEqual(out, "<h2>Title</h2><p>Some <strong>bold</strong>, <em>italic</em> and <code>code</code>.</p>")

    def test_code_is_not_formatted_further(self):
        self.assertEqual(ms.inline("`a*b*c`"), "<code>a*b*c</code>")

    def test_special_characters_are_escaped(self):
        self.assertEqual(ms.inline("a < b & c"), "a &lt; b &amp; c")

    def test_table_has_a_header_row_and_cells(self):
        md = chr(10).join(["| **A** | **B** |", "| --- | --- |", "| 1 | `x` |"])
        out = ms.convert(md)
        self.assertIn("<p><strong>A</strong></p></th>", out)
        self.assertIn("<p><code>x</code></p></td>", out)

    def test_an_empty_cell_stays_a_cell(self):
        out = ms.convert("| **A** | **B** | **C** |" + chr(10) + "| --- | --- | --- |" + chr(10) + "| x | | z |" + chr(10))
        self.assertIn("<p>x</p></td><td style=\"vertical-align: middle;\"><p></p></td><td style=\"vertical-align: middle;\"><p>z</p></td>", out)

    def test_the_header_table_gets_column_widths(self):
        nl = chr(10)
        out = ms.convert("| **Field** | **Value** |" + nl + "| --- | --- |" + nl + "| Owner domain | Registries |" + nl + "| Shared with | " + "a long value " * 20 + " |" + nl)
        widths = [int(w) for w in re.findall(r"width: (\d+)px", out)]
        self.assertEqual(len(widths), 2)
        self.assertEqual(sum(widths), ms.layout.HEADER_WIDTH)
        self.assertLess(widths[0], 160)
        self.assertGreater(widths[1], widths[0])

    def test_another_table_has_no_column_widths(self):
        nl = chr(10)
        self.assertNotIn("colgroup", ms.convert("| **A** | **B** |" + nl + "| --- | --- |" + nl + "| x | y |" + nl))

    def test_lists(self):
        self.assertEqual(ms.convert("- one" + chr(10) + "- two"), "<ul><li><p>one</p></li><li><p>two</p></li></ul>")

    def test_an_image_refers_to_the_attachment_by_file_name(self):
        out = ms.convert("![Alt text](images/Diagrams_X_Full.png)")
        self.assertIn('<ri:attachment ri:filename="Diagrams_X_Full.png"/>', out)
        self.assertIn('ac:alt="Alt text"', out)

    def test_a_link_to_another_page_is_a_page_link_by_title(self):
        self.assertIn('<ri:page ri:content-title="Natural Person"/>', ms.inline("[Natural Person](Natural_Person.md)"))

    def test_an_external_link_stays_a_link(self):
        self.assertIn('<a href="https://x.y/z">here</a>', ms.inline("[here](https://x.y/z)"))

    def test_header_colors_apply_to_the_table_under_the_heading(self):
        md = chr(10).join(["## Hubs", "", "| **A** |", "| --- |", "| 1 |"])
        out = ms.convert(md, {"Hubs": ("#3A0CA3", "#FFFFFF")})
        self.assertIn('data-highlight-colour="#3A0CA3"', out)
        self.assertIn("color: #FFFFFF", out)

    def test_every_real_page_converts(self):
        for stem in ("Party", "Natural_Person", "Legal_Entity", "Code_List", "Load_Configuration"):
            text = (HERE.parents[3] / "Rosetta" / "Business_Objects" / f"{stem}.md").read_text(encoding="utf-8")
            out = ms.convert(text)
            self.assertEqual(out.count("<ac:image"), 2, stem)
            self.assertNotIn("**", out, stem)


class SyncTests(unittest.TestCase):
    def test_a_page_already_published_is_skipped(self):
        message = sc.MESSAGE_PREFIX + sc.checksum("<p>x</p>")
        self.assertEqual(sc.page_action(message, "<p>x</p>"), "skip")
        self.assertEqual(sc.page_action(message, "<p>y</p>"), "update")

    def test_the_lucid_embed_is_repointed(self):
        params = {"macroParams": {"documentId": {"value": "old"}},
                  "macroMetadata": {"placeholder": [{"data": {"url": "https://l/ac?documentId=old&x=1"}}]}}
        adf = {"content": [{"type": "extension", "attrs": {"extensionKey": "lucidchart", "parameters": params}}]}
        self.assertEqual(sc.point_index_at_lucid(adf, "new"), 1)
        self.assertEqual(params["macroParams"]["documentId"]["value"], "new")
        self.assertIn("documentId=new", params["macroMetadata"]["placeholder"][0]["data"]["url"])
        self.assertEqual(sc.point_index_at_lucid(adf, "new"), 0)


    def test_the_snapshot_date_of_the_embed_is_moved(self):
        params = {"macroParams": {"documentId": {"value": "d"}, "lastSnapshotDate": {"value": "Tue, 20 Oct 2026 15:55:09 GMT"}},
                  "macroMetadata": {"placeholder": [{"data": {"url": "https://l/ac?lastSnapshotDate=Tue%2C+20+Oct+2026+15%3A55%3A09+GMT&documentId=d"}}]}}
        adf = {"content": [{"type": "extension", "attrs": {"extensionKey": "lucidchart", "parameters": params}}]}
        self.assertEqual(sc.point_index_at_lucid(adf, "d", "Wed, 21 Oct 2026 10:00:00 GMT"), 1)
        self.assertEqual(params["macroParams"]["lastSnapshotDate"]["value"], "Wed, 21 Oct 2026 10:00:00 GMT")
        self.assertIn("Wed%2C+21+Oct+2026+10%3A00%3A00+GMT", params["macroMetadata"]["placeholder"][0]["data"]["url"])

if __name__ == "__main__":
    unittest.main()
