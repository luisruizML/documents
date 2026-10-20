---
name: business-object-page
description: Use when given a raw draft of a business object, or asked to write, update, add or check a Business Object page for Nexus Rosetta (Rosetta/Business_Objects/<Object>.md), including its diagrams and its row in the index.
---

# Business Object page

Turns a raw draft of one business object into a validated page in `Rosetta/Business_Objects/`, with two diagrams and a row in the index. The format, the validator and the diagram builder are in this skill; the rules behind them are in `Rosetta/Principles.md`.

Read `Rosetta/Business_Objects/Natural_Person.md` first. It is the worked example. `Code_List.md` shows a Platform object.

## Procedure

Do these in order.

1. **Classify** each thing in the draft into a Hub, a Link, a Non-historized Link or a Satellite. A draft that says "a Hub or a Link" is forced to one decision, and the decision is recorded.
2. **Name** every vault object by the convention (`hub_<object>`, `lnk_<a>__<b>` in alphabetical order, `sat_<parent>__<descriptor>`). Draft names such as `Hub_Tax_Account` become `hub_tax_account`. List each rename for the author.
3. **Type** every column from the allowed list, by representation term. Money is `decimal(P,S)`, identifiers are `string`, moments are `timestamptz`.
4. **State the grain** of every vault object, starting with the "one row per" of its type.
5. **Split** personal data into its own Satellite. Special-category data (race or ethnicity, tribe, religion, health) goes in its own Satellite too.
6. **Keep history by default.** An attribute group whose rows are not meant to be kept in place is delivered as a pair: the `_history` Satellite, which is the default, and an in-place Satellite with `row_version`, loaded only where a jurisdiction forbids keeping previous values. The current value is the view `cur_<parent>__<descriptor>`, never a stored copy. Do not choose in place for performance.
7. **Do not store what can be computed** (R13). Age, age group and "valid today" are Gold objects. Keep the date.
8. **Use the Code List object** for the values of a `_code` column that can change or differ by jurisdiction. A code on which logic depends is a closed list: `One of` in the Description. Never create a `ref_` table.
9. **Extract** edge cases from the draft into the Jurisdictions map, with the jurisdictions the draft names.
10. **Turn** the draft's examples into sample rows of the Hub and the Satellites.
11. **Collect** everything you could not decide into Open decisions, with owner, how it is decided and by when.
12. **Link across pages.** A Link may join a Hub defined on another page; the Hub is drawn as defined elsewhere and has no Fields table here. A Satellite on a Link is named `sat_<link name without lnk_>__<descriptor>`. A relationship you cannot name yet, such as a Link between two roles of the same object, is not invented: it goes in Open decisions.
13. **Write** the page from `assets/template.md`, then **validate**, then **draw**, then **update the index**.

## Fixed decisions

- One page per object, at the flat path `Rosetta/Business_Objects/<Object>.md`.
- Party is a thin Hub (`hub_party`). Natural Person and Legal Entity are separate Hubs, each with its own business key; each joins Party with a Link (`lnk_natural_person__party`, `lnk_legal_entity__party`).
- The business key of an object that several jurisdictions identify differently is `jurisdiction_code` + `key_type_code` + the normalized `<object>_bk`.
- Government Authority is not a Party. It is a Platform object.
- Payment objects belong to Finance.
- Platform objects (configuration, Code List, Government Authority) are listed in the Platform section of the index and on `Platform.md`.
- Source endpoints are declared by the author, never discovered. With none given, write `No endpoints declared yet`.
- Pages may name jurisdictions. They do not refer to internal meetings.

## Never invent

- Source endpoints, Bronze tables or source systems.
- The owner domain, when the draft does not say. Ask.
- Jurisdiction rules the draft does not state.
- Business keys the draft does not name.
- Abbreviations. Do not add one to the approved list without asking.

## Commands

Run from the repository root.

```
python .claude/skills/business-object-page/scripts/validate_page.py Rosetta/Business_Objects/<Object>.md
python .claude/skills/business-object-page/scripts/build_diagram.py Rosetta/Business_Objects/<Object>.md [--context lnk_a__b,lnk_c__d] [--no-export]
python -m unittest discover -s .claude/skills/business-object-page/tests
```

- `build_diagram.py` reads the page and writes `drawio/Diagrams_<Object>_Simplified.drawio` and `drawio/Diagrams_<Object>_Full.drawio` (the `.drawio` files go in the `drawio/` subfolder next to the page) and the two PNGs in `images/` (`images/Diagrams_<Object>_<Simplified|Full>.png`). The page links the PNGs as `images/...`. Each object is as wide as its content: Simplified from the name (250 minimum), Full from its Fields table. Connector labels sit on the first horizontal segment, and each gap between columns grows to fit its labels (`brand-design-system` section 4). `--context` names objects defined on other pages, which are drawn with a note and no table.
- Colors: Hub `#3A0CA3`, Link `#45E3CD`, Satellite `#F72586`. A Satellite updated in place is drawn lighter with a dashed border, so the history default stands out. The skill `brand-design-system` (section 3c) owns the rules.
- **Global Lucidchart diagram** of every Hub, Link and Satellite on the pages: `python .claude/skills/business-object-page/scripts/build_lucid_global.py out.json` reads the pages (so it cannot drift from them) and writes Lucid Standard Import JSON. Upload it with `lucid_create_diagram_from_specification` (`product: lucidchart`, `use_assisted_layout: false`), export a PNG and check it. The Lucid rules are in the skill `lucid-diagram-conventions` ("Data-model diagrams"). Regenerate and upload a new document whenever a page adds or changes a Vault object.
- Run the validator before reporting done. The validator checks form only. Whether the model is right is a human review.

## What to do with each validator error

| Tag | Fix |
| --- | --- |
| `section` | Add the missing section or put it in order. There are eleven. |
| `header` | Use a value from the list: owner and shared-with domains, scope, status. |
| `format` | Make every table header bold (`**Header**`). |
| `name` | Rename to the pattern; for a Link, put the parts in alphabetical order; for a Satellite, make sure its parent is on the page. A `ref_` name is not a type: use the Code List object. |
| `grain` | Start the grain with the "one row per" of its type. |
| `fields` | Give the table the seven columns; Null and PII are Yes or No; Default is never empty; Role matches the column; `_code` columns show three or more `e.g.` values or `One of`. |
| `type` | Use a type from the list; a `decimal` needs `(P,S)`; the representation term fixes the type. |
| `diagram` | Build both images with `build_diagram.py` and reference both. |

## Common mistakes

| Mistake | Instead |
| --- | --- |
| Legal Entity as a Satellite of `hub_party` | A Hub of its own, joined to Party by a Link |
| A Hub for a calendar or a list of values | Values of the Code List object |
| A Satellite that holds two grains | Two Satellites |
| Descriptive columns on `hub_party` | They live on the specific object |
| `Hub_Legal_Entity`, `LegalEntity` | `hub_legal_entity` |
| A stored age or "is active today" | A Gold object (R13) |
| One Satellite for in-place and history | A pair: `_history` is the default, the in-place one is the exception |
| Choosing in place because it is cheaper | History by default; partition and compact instead |
| Storing the current value in a second table | The `cur_` view over the history Satellite |
| A new table for each code list | New rows in the Code List object |

## When you finish

Report the page, the renames you made, the decisions you recorded as open, and anything you could not validate. Publishing to Confluence is a separate step the user asks for. Confluence images are attached by hand.
