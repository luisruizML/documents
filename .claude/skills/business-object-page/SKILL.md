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
4. **Define and state the grain** of every vault object. The Definition says in business words what the table is for (rules below); the grain starts with the "one row per" of its type.
5. **Split** personal data into its own Satellite. Special-category data (race or ethnicity, tribe, religion, health) goes in its own Satellite too.
6. **Keep history by default.** An attribute group whose rows are not meant to be kept in place is delivered as a pair: the `_history` Satellite, which is the default, and an in-place Satellite with `row_version`, loaded only where a jurisdiction forbids keeping previous values. The current value is the view `cur_<parent>__<descriptor>`, never a stored copy. Do not choose in place for performance.
7. **Do not store what can be computed** (R13). Age, age group and "valid today" are Gold objects. Keep the date.
8. **Use the Code List object** for the values of a `_code` column that can change or differ by jurisdiction. A code on which logic depends is a closed list: `One of` in the Description. Never create a `ref_` table.
9. **Extract** edge cases from the draft into the Jurisdictions map, with the jurisdictions the draft names.
10. **Turn** the draft's examples into sample rows of the Hub and the Satellites.
11. **Collect** everything you could not decide into Open decisions, with owner, how it is decided and by when.
12. **Link across pages.** A Link may join a Hub defined on another page; the Hub is drawn as defined elsewhere and has no Fields table here. A Satellite on a Link is named `sat_<link name without lnk_>__<descriptor>`. A relationship you cannot name yet, such as a Link between two roles of the same object, is not invented: it goes in Open decisions.
13. **Write** the page from `assets/template.md`, then **validate**, then **draw**, then **update the index**.

## Bold words

Bold marks the concept, not emphasis: a reader who skims only the bold words can rebuild what the object is for. `scripts/keywords.py` holds the rules and `scripts/bold_terms.py` the phrases of each Vault object; the validator checks the form (`bold` errors), a human reviews the choice.

1. **Count.** 2 to 4 bold phrases in each Definition of the Vault objects table; 3 to 6 in the page's Definition section. Each phrase is 1 to 4 words.
2. **What to bold, in this order.** The subject the table is about (**names**, **documents and numbers**, **events in the life**, **gender**), then a behaviour (**earlier values stay**, **replaced when it changes**, **carries no description**, **not stored**, **only the current**), then a qualifier that tells two tables apart (**over time**, **the default**, **the exception**, **not the identity table**). In the page Definition section: the object's name on first use, what it identifies, its identity rule.
3. **Never bold** the opening "The table that", a name in backticks, an example after "such as", a link, or a word that appears on every page, such as jurisdiction (except where it is the subject).
4. **A new Vault object** gets its row in `bold_terms.py` (phrases written word for word as they appear in the Definition); `keywords.propose` raises when a phrase is not in the text. The page text is the source: write the Definition with the markers (`**x**`). Diagrams (drawio, Lucid) receive the Definition without the markers; the Confluence page and the interactive graph show them bold.

## Writing a Definition

Every row of the Vault objects table has a Definition. The validator (`definition` errors) checks the form; the meaning is a human review.

1. One or two sentences, starting with "The table that", in business words, at most 400 characters.
2. It says what the table records and why a reader cares. It does not say how it is stored: no hash, no Hub, Link or Satellite jargon.
3. A Hub says which identifier it holds and that it carries no description of the object. A Link says which two things it joins and what the join means, and names its Satellite for the details. A Satellite says what it records; if it is one of a pair it says whether it is the default (keeps history) or the exception (updated in place, loaded only where a jurisdiction forbids keeping previous values), and names its twin.
4. When two tables could be confused, the Definition says which is which: the identity table `lnk_legal_entity__party` and the ownership table `lnk_legal_entity__party_owner`.
5. It states only what the page states elsewhere; it never adds a rule.

## Fixed decisions

- One page per object, at the flat path `Rosetta/Business_Objects/<Object>.md`.
- Party is a thin Hub (`hub_party`). Natural Person and Legal Entity are separate Hubs, each with its own business key; each joins Party with a Link (`lnk_natural_person__party`, `lnk_legal_entity__party`).
- The business key of an object that several jurisdictions identify differently is `jurisdiction_code` + `key_type_code` + the normalized `<object>_bk`.
- Government Authority is not a Party. It is platform configuration: the public bodies that act on the platform (issue, approve, restrict, see). A public body as a holder or a taxpayer, domestic or foreign, is a Legal Entity with the class `public` in the criterion `sector` of `sat_legal_entity__classification`; the same body can be both, as a person is a Natural Person and a user of the platform. No Link to a Government Authority Hub: a holder goes through the Party Link.
- A Link with a role (a person related to a person, or a Party that owns a Legal Entity) names the role as a suffix of the part that plays it: `lnk_legal_entity__party_owner`. The Business key cell lists the Hubs it joins, in order, and names the role in brackets when the same Hub is joined twice. A Satellite whose rows are keyed by a type (holding type, relationship type) states it in the grain: "one row per parent key and holding type". Ownership of a Legal Entity is `lnk_legal_entity__party_owner`, not `lnk_legal_entity__party`, which says that a Legal Entity is a Party.
- A validity range carries sentinels: `end_date` and `valid_to_date` are Null No with the default `9999-12-31`, `valid_from_date` has the default `1900-01-01`, and the loader closes the open row the day before a new one starts (Principles, "Validity ranges"). A column ending in `_number` is `decimal(P,S)`.
- Facts that happen on a date are rows of events (`event_code`, `event_date`), and measurements or classifications that can grow are rows of traits (`trait_code`, `value_text`, `value_number`), not one column each (Principles, "Patterns that repeat across objects"). Evidence is an `artifact_uri` that points to one stored object.
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
- **Gray dashed "uses" lines.** The global diagram and the graph both draw a light gray dashed line from `hub_code_list` to every object that has a column whose values come from a Code List, and from `hub_load_configuration` to the Satellites of a twin pair. The list is read from the pages by `scripts/platform_usage.py` (the columns the Code List page names in "Which code columns are values of a Code List"), never typed. A new column gets a flag in its Fields table and a row (`<vault table>.<column>`) in that table. The dashed lines are not structural: they are exempt from the no-crossing tests.
- **Simplified graph** (complements the global diagram, same pages): `python .claude/skills/business-object-page/scripts/build_lucid_graph.py out.json [--preview out.png]`. Hubs are circles, Links hexagons, Satellites small squares, each with its name beside it, like the hand-drawn `PSS Data Objects - Graph`. Placement is `scripts/graph_layout.py`: a force-directed skeleton of Hubs and Links (networkx `spring_layout`), Satellites fanned in the free angles, names in the free spots, the best of 120 fixed seeds, spread out until nothing overlaps. It needs `pip install -r .claude/skills/business-object-page/requirements.txt`. Same upload and N-1/N-2 housekeeping as the global diagram, title `PSS Data Objects - Graph (CURRENT, N objects)`.
- **Interactive graph (repository only, not in Confluence).** `python .claude/skills/business-object-page/scripts/build_html_graph.py [out.html]` writes `Rosetta/Business_Objects/html/Vault_Graph.html`: one self-contained file (inline SVG and JavaScript from `assets/graph_template.html`, no server, no external file, about 300 KB) with the layout of the simplified graph. The right panel lists Hubs, Links, Satellites with a filter; clicking an object (in the list or in the picture) fades everything but the objects directly related to it (for a Hub: its Links and Satellites, and the Satellites of those Links; the line set is computed in Python, `focus_of`, and tested) and opens the Vault Info panel on the left: Definition, Grain, Business key, Fields (with the Code List flag) and the related objects as links. `#<object name>` in the address opens it with an object selected. Pan by dragging, zoom with the wheel, Esc clears. A checkbox shows the Code List and Load Configuration lines for the whole graph; whatever is selected always shows its own dashed lines, darker, and keeps the platform object at the other end visible (the Vault Info lists them under "Dashed lines" with a button that zooms to include them). For an object with fields linked to the Code List, the bottom of the Vault Info lists "Code List examples": for each such field, where its values live, why, and the examples, as written in the Code List table (`code_list_examples` in `build_html_graph.py`). A click in the picture is read with `elementFromPoint`, because the svg captures the pointer; names are clickable like shapes. Selecting a Hub also keeps the Hubs across its Links, with the Link's line to them; "Directly related" shows the count of each type and colours each name like its shape; the groups of the list on the right start collapsed, open on a click, open for a filter and open for the group of the selected object. Light areas sit behind the picture (Assets around Immovable Assets and Movable Assets, Parties, Legal, Contact Point; `AREAS` in `build_html_graph.py`, a blob of circles and thick lines around the objects of the pages of each area, with a checkbox to hide them). The Code List / Confluence scripts never read this file; regenerate it whenever a page changes. Embedding it in Confluence needs a Marketplace HTML macro and is not done.
- **Finishing pass (both generated documents, graph and global model):** after the import, run `scripts/lucid_finish.js` on the new document with `lucid_run_script` (`source` = the file). The import JSON cannot set either of its two jobs: it sends every line behind every shape (lines cannot be re-ordered, so every block is brought to the front) and turns line jumps on, so crossing lines hop over each other. It reports lines whose end is not glued to a shape. Every line is drawn to the centre of its two shapes (`CENTRE` in `build_lucid_graph.py`), so each one visibly enters the shape it joins whatever that shape's outline is. The layout is the same on every run (the skeleton is built in sorted order; a test runs it under three hash seeds).
- The Diagram section has two subsections, `### Simplified version` and `### Full version`, each with a sentence on what it shows and when to use it, then its image. The validator checks the headings and their order.
- Run the validator before reporting done. The validator checks form only. Whether the model is right is a human review.

## What to do with each validator error

| Tag | Fix |
| --- | --- |
| `section` | Add the missing section or put it in order. There are eleven. |
| `header` | Use a value from the list: owner and shared-with domains, scope, status. |
| `format` | Make every table header bold (`**Header**`). |
| `name` | Rename to the pattern; for a Link, put the parts in alphabetical order; for a Satellite, make sure its parent is on the page. A `ref_` name is not a type: use the Code List object. |
| `grain` | Start the grain with the "one row per" of its type. |
| `bold` | Give each Vault Definition 2 to 4 bold phrases and the Definition section 3 to 6, each of 1 to 4 words, none in backticks, none the opening "The table that"; see "Bold words". |
| `definition` | Add the Definition column and give every row a sentence that starts with "The table that", ends with a full stop, has at most 400 characters and uses no technical word. |
| `fields` | Give the table the eight columns; an `end_date` or `valid_to_date` is Null No with Default `9999-12-31` and a `valid_from_date` has Default `1900-01-01`; Null and PII are Yes or No; Default is never empty; Role matches the column; `_code` columns show three or more `e.g.` values or `One of`. |
| `codelist` | Set the Code List column of the row: `List` for a `_code` column with `e.g.` values, `Closed` when the Description says `One of`, `—` for any other column. Then give the column a row in the table of the Code List page (`<vault table>.<column>`, where its values live, why, examples) or take it out: the flags of a page and the rows of that table must agree in both directions. |
| `type` | Use a type from the list; a `decimal` needs `(P,S)`; the representation term fixes the type. |
| `diagram` | Build both images with `build_diagram.py` and reference both. |

## The Code List column

Every Fields table has the column **Code List** between Default and Description. It is `List` for a `_code` column whose values come from a list of the Code List object, `Closed` for a closed list (the Description says `One of`) and `—` for everything else. The rows of the table "Which code columns are values of a Code List" on `Code_List.md` are the other half: one row for each flagged column, keyed `<vault table>.<column>` (the vault table, so that a repeated name such as `role_code` is never ambiguous), with where its values live, why, and examples taken from the page of the column. Rows are ordered like the Index, and inside a page each Hub is followed by its Satellites, then each Link by its Satellites; the first column is laid out on one line (`code_list_widths` in `table_layout.py`). `validate_page.py` checks both halves against each other, and `platform_usage.py` reads the same rows for the gray dashed lines of the diagrams. A `_code` column that is not a list (a postal code, the platform roles of the access rule) is named in `NOT_A_LIST` in `validate_page.py`. When a page adds a code column: write the flag, add the row to the Code List table, run the validator.

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

Report the page, the renames you made, the decisions you recorded as open, and anything you could not validate. Publishing to Confluence is a separate step the user asks for: `python .claude/skills/business-object-page/scripts/sync_confluence.py` publishes the five pages and the inventory and uploads the PNG files as new versions of their attachments, skipping whatever has not changed (`--dry-run` first; `--page <Object>` for one page; `--lucid <document id>` points the index embed at a Lucid document). It needs `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN` in the environment or in the `.env` of the repository root, which git ignores. The index page is not rewritten by the script, because it holds the Lucidchart embed.
- **The Index shows the two Lucid pictures as images, not as Lucidchart macros.** The macro is found by an `embedId` that only Lucid's own editor creates (a made-up one gives "macro link is no longer valid", and a copied one keeps showing the first document), and a smart link shows the Lucid interface. After a new Lucid document and its `lucid_finish.js` pass, export it with `lucid_export_document_as_PNG`, copy the PNG to `Rosetta/Business_Objects/images/Lucid_Simplified_Graph.png`, `Lucid_Simplified_Version.png` or `Lucid_Full_Model.png`, upload it as an attachment of the Index page and point its `mediaSingle` at the new file id; the link under it opens the interactive diagram. `--lucid` and `--lucid-graph` only work while the page still holds a macro.
- **Three Lucid pictures:** the graph (`build_lucid_graph.py`), the simplified version (`build_lucid_global.py out.json --simplified`: the same layout with the grain in each box) and the full version (`build_lucid_global.py out.json`: the definition in each box). Regenerate all three when a page changes, run `lucid_finish.js` on each and refresh the three PNGs on the Index.
- **Base Parcel and Built Structure.** Two pages, one Hub each, no umbrella Hub (the first draft was one page, Immovable Asset). Parcel and structure are two Hubs with no umbrella; each has its own Link to Location, and its holders and restrictions are RRRs and its permits Entitlements (Legal family). Characteristics are rows (Principles, "Traits as rows"); a valuation is a Satellite row with a closed status list, and the definitive value is a Gold view. In the global Lucid model the cluster sits below the Registries content: its Hubs are as tall as the rows they serve so the lines to them run level, and its long lines to hub_location cross short lines, which is allowed (jumps are on).

**Confluence tree.** Business Objects > Registries (Party > Natural Person, Legal Entity; Location; Contact Point (new, no page id yet: the first sync creates it under the Registries group page and `assets/confluence_pages.json` takes its id); Assets > Immovable Assets (a family page) > Base Parcel, Built Structure; Legal (a family page) > Entitlement, Credential, RRR; Movable Assets), Platform (Code List, Load Configuration), Vault Objects Inventory last. Registries and Assets are grouping pages with no Markdown source; their ids are in `assets/confluence_pages.json` under `group_pages`. A new page is created under its group.

**Family pages.** A page with no Hub of its own, such as Immovable Assets, says `No Vault objects of its own` in the first line of its Vault objects section and links its parts in the rows of the table that follows (the validator and `build_diagram.py` read the parts from those rows; the diagram merges them). It holds what the parts share: rules, shared decisions, the family picture. The parts carry only what is their own and point to the family page. Pages that group without content, such as Registries and Assets, stay as bare Confluence pages.

- **Legal (family page), Entitlement, Credential, RRR.** Three Hubs, no umbrella. An Entitlement is the right to an activity, a Credential is the proof of it, and an RRR (Right, Restriction, Responsibility) is the bond between a Party and a thing. `rrr` is an approved abbreviation (`APPROVED_ABBREVIATIONS` in `validate_page.py`). **Ownership is an RRR**: an owner is a Party in the role `holder` of an RRR of the class right, through `lnk_party__rrr` and `sat_party__rrr__participation` (roles `holder`, `counterparty`, `authority`, with the share). The asset pages have no ownership Links and no restriction Satellite. The Links to the things are one for each kind of asset (`lnk_base_parcel__rrr`, `lnk_built_structure__rrr`, `lnk_base_asset__rrr`, `lnk_rrr__swappable_component`, and `lnk_<kind>__entitlement` for entitlements), defined on the Legal pages, drawn on the asset pages. Deeds, leases, mortgages and court orders are `artifact_uri` pointers, never an object. Gold views: `entitlement__credential_discrepancy`, `rrr__ownership_share_check`, `asset__use_without_entitlement`. In the global Lucid model the Legal cluster stands east of the Location cluster (`_immovable_block`): the Links to each Hub on its right (RRR column, then entitlement column, right-aligned), `hub_rrr` as tall as the rows it serves, `hub_entitlement` and `hub_credential` at the top; the Links to Party sit at the top of the first column and go up the corridor east of the chain.

**Cross-page Links.** Every object is its own universe. A Link is defined once, in the Vault objects table of one page, but both pages draw it (`--context` names the Link, its Satellite and the Hub on the other side) and each page has a "Related pages" list under its Vault objects table with a page link to every object defined elsewhere, so a reader can go to the other side. `lnk_base_parcel__built_structure` is defined on Built Structure and drawn on Base Parcel. Pages written before this rule (Party, Natural Person, Legal Entity, Location) still need the list.

- **Nested parcels.** `lnk_base_parcel__base_parcel_hierarchy` and `sat_base_parcel__base_parcel_hierarchy__membership` mirror the structure ones (containment, not division; no fixed depth, `max_depth_count` in the Code List; one open parent for each kind; no loop). In the global Lucid model they are placed in the west column under the parcel Satellites, as the structure ones are.
- **Contact Point** (page `Contact_Point.md`, after Location). A way to reach a Party that is not a place: a phone number, an email or a messaging account; a mailing address stays in Location. One Hub `hub_contact_point` with a platform-assigned key (no personal data in the Hub), one Link to Party (`lnk_contact_point__party`, which serves natural persons and legal entities), the value in `sat_contact_point__description` (the only PII), the channels that reach it as rows of `sat_contact_point__channel` (voice, sms, whatsapp, imessage, telegram, email: the address is the identity, the channel is a fact about it, and a handle carries its `service_code`), and the use, the consent and the verification as Satellites of the Link (verification is a fact about a party and a channel, so a line shared by a company and an employee can be confirmed by one and not by the other). A number is kept in the international form with `jurisdiction_code` (numbering plan) and `extension_text` (a switchboard and each extension are separate contact points, same `value_text`); a mobile number and a fixed line are two values of `contact_kind`; the role of a switchboard is `main_line`. `consent_status_code` is a closed list. The consent rules of each jurisdiction are open decisions, not invented. In the global Lucid model the Link's line up to `hub_party` crosses the short lines of the ownership group, which is allowed (jump); the cluster sits west of the long lines to `hub_location`.
- **Movable Assets (family page), Base Asset, Swappable Component, Model Catalog.** Three Hubs, no umbrella; each Link is defined on the page of the side that depends on the other (the fitting of a part and the Link to its model are on the part and on the asset). Parts nest (hierarchy Link from the first version) and one Model Catalog Hub serves assets and parts through `model_kind_code`. The flag of an asset is a Satellite; its holders, restrictions, mortgages and liens are RRRs (Legal family), joined by `lnk_base_asset__rrr` and `lnk_rrr__swappable_component`. A Satellite name stays within 63 characters, so the hierarchy Satellite of parts is `__period`. The global Lucid model draws them below the Immovable cluster (`_immovable_block` places both): the Links of the Legal cluster to the asset and the part run east to the RRR column, and the Link that fits a part to an asset stands beside the model.
