# Business Object Page and Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the standard Business Object page (template, validator, pilot pages for Natural Person and Party, diagram, index) and then the `business-object-page` skill that turns any raw object draft into that page.

**Architecture:** A markdown page with eleven fixed sections is the source of truth. A Python validator (standard library only) checks its form: sections, header values, vault-object names, types and grains. The skill is written after the pilot is reviewed, so it encodes the corrected format; it calls the validator before reporting done.

**Tech Stack:** Markdown, Python 3 standard library (`re`, `argparse`, `pathlib`, `unittest`), the `drawio` skill (draw.io Desktop export), the `brand-design-system` skill.

**Spec:** `docs/superpowers/specs/2026-10-19-business-object-page-design.md`. Naming, types and grain rules come from `Rosetta/Principles.md` (R6–R12).

## Global Constraints

- Pages live in `Rosetta/Business_Objects/<Object_Name>.md`, one flat folder, no domain in the path. Diagram beside it: `<Object_Name>.drawio` and `<Object_Name>.png`. Working files: `Rosetta/Business_Objects/.drawio-tmp/`.
- Eleven sections in this order, headings without numbers: `Header`, `Definition`, `Why it is its own object`, `Vault objects`, `Fields`, `Sources and mapping`, `Jurisdictions map`, `Examples`, `Modeling considerations`, `Diagram`, `Open decisions`. A section with nothing to say states so; it is never deleted or left blank.
- Owner domain and Shared with values: `Platform`, `Registries`, `Taxation Contributions and Licences`, `Finance`, `Compliance`, `Benefits`, `AEOI`. Scope: `Domain`, `Shared`, `Global`. Status: `Draft`, `Reviewed`, `Agreed`.
- Vault object types and name patterns: Hub `hub_<object>`; Link `lnk_<a>__<b>` (parts alphabetical); Non-historized Link `lnk_<a>__<b>`; Satellite `sat_<parent>__<descriptor>` (descriptor = after the last `__`); Reference table `ref_<name>`.
- Grain sentence must start with: Hub `one row per business key`; Link `one row per distinct combination of`; Non-historized Link `one row per occurrence of`; Satellite `one row per parent key`; Reference table `one row per code`.
- Allowed types: `boolean`, `int`, `long`, `double`, `float`, `decimal(P,S)`, `date`, `time`, `timestamptz`, `timestamp`, `timestamptz_ns`, `timestamp_ns`, `string`, `uuid`, `fixed(L)`, `binary`, `variant`, `geometry`, `geography`, `unknown`, `struct`, `list`, `map`.
- Endpoints are declared by the author and never discovered. With none declared the section says `No endpoints declared yet`.
- Pages may name specific jurisdictions. They never refer to internal meetings.
- Government Authority is a Platform object, never a Party. Natural Person and Legal Entity are separate Hubs. `hub_party` is thin: its only key is a Nexus-assigned party identifier.
- Payment objects belong to Finance, shared with Taxation Contributions and Licences.
- Commits add explicit paths only. The working tree holds unrelated changes.
- Test command: `python -m unittest discover -s .claude/skills/business-object-page/tests -v` (run from `C:\Development\documents`).

## Review Focus

1. A page saved with Windows line endings (`\r\n`), which is how this repo's files are written on this machine: the validator must treat it exactly as the same page with `\n`.
2. A Link that connects a Hub defined on another page (`lnk_natural_person__party` points to `hub_party`): the validator must accept it, and must still reject a Satellite whose parent is not on the page.
3. A draft-style name such as `Hub_Tax_Account` or `Sat_Entitlement_Status`: the error must say the lowercase form.
4. A `decimal` with no precision and scale, and an `amount` column typed `double`: both rejected.
5. A draft that says "Hub or Link" for one object: the skill must force one choice and record the alternative in Open decisions, not copy both.

## File Structure

| File | Responsibility |
| --- | --- |
| `.claude/skills/business-object-page/scripts/validate_page.py` | `validate()` and the CLI. One file: all rules are short and share the parsed page |
| `.claude/skills/business-object-page/tests/test_validate_page.py` | Unit tests for every rule |
| `.claude/skills/business-object-page/tests/fixtures/valid_page.md` | A complete valid page for a toy object, mutated by the tests |
| `.claude/skills/business-object-page/assets/template.md` | The empty page the skill fills in |
| `.claude/skills/business-object-page/SKILL.md` | The skill instructions |
| `Rosetta/Business_Objects/Natural_Person.md`, `Party.md`, `Index.md` | Pilot pages and the index |
| `Rosetta/Business_Objects/Natural_Person.drawio`, `.png` | Pilot diagram |

---

### Task 1: Validator core: sections, header, tables, line endings

**Files:**
- Create: `.claude/skills/business-object-page/scripts/validate_page.py`
- Create: `.claude/skills/business-object-page/tests/test_validate_page.py`
- Create: `.claude/skills/business-object-page/tests/fixtures/valid_page.md`

**Interfaces:**
- Produces: `validate(text: str, base_dir: Path | None = None, approved: frozenset[str] = frozenset()) -> list[str]`. Returns error strings, each starting with its rule tag: `section:`, `header:`, `name:`, `type:`, `grain:`, `fields:`, `sources:`, `jurisdictions:`, `diagram:`, `decisions:`. An empty list means valid.
- Produces: module constants `SECTIONS`, `DOMAINS`, `SCOPES`, `STATUSES`, `TYPES`, `GRAIN_PREFIX` holding the Global Constraints values.
- Produces: `parse_page(text: str) -> Page`, where `Page` is a dataclass with `title`, `sections: dict[str, list[str]]` (heading to body lines, in order) and `tables(section) -> list[list[dict[str, str]]]` (each markdown table in a section as a list of row dicts keyed by header).

- [ ] **Step 1: Write `valid_page.md`.** A complete page for the toy object `Sample Order`: header table (owner `Finance`, shared with `Taxation Contributions and Licences`, scope `Shared`, status `Draft`); vault objects `hub_sample_order`, `lnk_customer__sample_order` (customer Hub is on another page), `sat_sample_order__pricing`, `lnk_sample_order__shipment_event` (Non-historized Link), `ref_order_status`; one Fields table each, with `sat_sample_order__pricing` carrying `total_amount decimal(18,2)`; sources `No endpoints declared yet`; one Jurisdictions map row naming a country; one example; diagram line `![Sample Order cluster](Sample_Order.png)`; one Open decisions row.
- [ ] **Step 2: Write failing tests** in `test_validate_page.py`, with a helper `page(old=None, new=None)` that reads the fixture and replaces `old` once (asserting `old` is present):
  - `test_valid_fixture_has_no_errors`: `validate(page()) == []`
  - `test_crlf_line_endings_give_same_result`: `validate(page().replace("\n", "\r\n")) == []`
  - `test_missing_section_is_reported`: remove the `## Diagram` heading; assert an error starting `section:` contains `Diagram`
  - `test_sections_out_of_order_are_reported`: swap `Definition` and `Header`; assert `section:` error contains `order`
  - `test_blank_section_is_reported`: empty the Examples body; assert `section:` error contains `Examples`
  - `test_bad_owner_domain`: change `Finance` to `Treasury`; assert `header:` error contains `Treasury`
  - `test_bad_scope_and_status`: one assertion each for `Global-ish` and `Final`
  - `test_shared_with_accepts_several_domains`: `Registries, Finance` in Shared with gives no error
- [ ] **Step 3: Run the tests; expect FAIL** (`ModuleNotFoundError: validate_page`).
- [ ] **Step 4: Implement** `parse_page`, the constants, and the `section:` and `header:` rules in `validate_page.py`. Normalise `\r\n` to `\n` first. A heading is a line starting `## `. A table is a run of lines starting `|`; the second line is the separator.
- [ ] **Step 5: Run the tests; expect PASS.** Command: the test command above.
- [ ] **Step 6: Commit.**

```bash
git add .claude/skills/business-object-page/scripts/validate_page.py .claude/skills/business-object-page/tests
git commit -m "feat(business-object-page): validator core for page sections and header"
```

### Task 2: Validator vault-object rules

**Files:**
- Modify: `.claude/skills/business-object-page/scripts/validate_page.py`
- Modify: `.claude/skills/business-object-page/tests/test_validate_page.py`

**Interfaces:**
- Consumes: `parse_page`, `Page.tables`, the constants from Task 1.
- Produces: `check_vault_objects(page: Page, approved: frozenset[str]) -> list[str]`, called by `validate`. Reads the `Vault objects` table (columns `Type`, `Name`, `Grain`, `Business key`) and the `Fields` section (one `### <name>` heading with a table per vault object; columns `Column`, `Type`, `Null`, `Personal data`, `Description`).

- [ ] **Step 1: Write failing tests** (same helper):
  - `test_draft_style_name_is_rejected_with_lowercase_hint`: rename `hub_sample_order` to `Hub_Sample_Order` in the table; assert `name:` error contains `hub_sample_order`
  - `test_hub_with_double_underscore_is_rejected`: `hub_sample__order`
  - `test_link_parts_must_be_alphabetical`: rename to `lnk_sample_order__customer`; assert error contains `alphabetical`
  - `test_link_to_hub_on_another_page_is_accepted`: the fixture's `lnk_customer__sample_order` has no `hub_customer` row and gives no error
  - `test_satellite_parent_must_be_on_page`: rename to `sat_missing_thing__pricing`; assert error contains `parent`
  - `test_satellite_descriptor_is_after_last_double_underscore`: a Satellite on the Link, `sat_customer__sample_order__terms`, with parent `lnk_customer__sample_order` present, is accepted
  - `test_name_over_63_characters_is_rejected`
  - `test_short_unapproved_token_is_rejected`: `hub_tp_account` fails; `validate(..., approved=frozenset({"tp"}))` passes. Allowed short tokens without approval: `id`, `hk`, `bk`, `dts`, `of`, `to`, `by`, `in`, `on`, `no`, `is`
  - `test_grain_prefix_per_type`: for each of the five types, a wrong prefix gives a `grain:` error naming the expected prefix
  - `test_type_not_on_list_is_rejected`: `varchar(10)` gives `type:` error
  - `test_decimal_needs_precision_and_scale`: `decimal` and `decimal(18)` rejected, `decimal(18,2)` accepted
  - `test_amount_column_must_be_decimal`: `total_amount double` gives `type:` error mentioning `_amount`
  - `test_representation_terms_fix_types`: `_date` not `date`, `_dts` not `timestamptz`, `_flag` not `boolean`, `_code`, `_name`, `_id` not `string` or `uuid` each rejected
  - `test_every_vault_object_has_a_fields_table_and_no_extra`: delete one `###` block, and add one for an unlisted name; each gives a `fields:` error
  - `test_null_and_personal_data_are_yes_or_no`
  - `test_hub_fields_include_hash_and_business_key`: a Hub named `hub_sample_order` whose Fields table lacks `sample_order_hk` or `sample_order_bk` gives a `fields:` error naming the missing column
  - `test_satellite_fields_carry_parent_hash_key_and_no_business_key`: a Satellite whose Fields table contains a column ending `_bk` gives a `fields:` error (Satellites carry only the parent's hash key)
- [ ] **Step 2: Run; expect FAIL.**
- [ ] **Step 3: Implement** `check_vault_objects`. Name patterns are regexes per type; the Link check splits on `__` and compares to its sorted copy; the Satellite parent is the name without `sat_` and without everything from the last `__`, and must equal a Hub or Link name on the page minus its `hub_` or `lnk_` prefix. Representation-term map: `_id` to `string` or `uuid`; `_code`, `_name` to `string`; `_date` to `date`; `_dts` to `timestamptz`; `_amount` to `decimal(P,S)`; `_flag` to `boolean`; `_count` to `int` or `long`. Structural columns (`*_hk`, `*_bk`, `load_dts`, `record_source`, `hashdiff`) are exempt from the term map, and `*_hk`, `record_source`, `hashdiff` must be `string` or `fixed(L)`.
- [ ] **Step 4: Run; expect PASS.**
- [ ] **Step 5: Commit** (`feat(business-object-page): vault object naming, type and grain rules`).

### Task 3: Validator remaining sections and CLI

**Files:**
- Modify: `.claude/skills/business-object-page/scripts/validate_page.py`
- Modify: `.claude/skills/business-object-page/tests/test_validate_page.py`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: `check_sources`, `check_jurisdictions`, `check_diagram`, `check_decisions`, each `(page: Page, base_dir: Path | None) -> list[str]`; and `main(argv: list[str]) -> int` (exit 0 valid, 1 errors). CLI: `python validate_page.py <page.md> [--approved tin,...]`; prints `<file>: <error>` per line.

- [ ] **Step 1: Write failing tests:**
  - `test_sources_is_declarative_or_empty_statement`: a table with columns `Source`, `Endpoint`, `Bronze table`, `Provides` passes; free prose fails with `sources:`; the exact text `No endpoints declared yet` passes
  - `test_bronze_table_name_pattern`: `bronze.registry__taxpayers` passes; `Bronze.Registry_Taxpayers` fails
  - `test_mapping_record_requires_declared_endpoints`: a `Mapping` table beside `No endpoints declared yet` fails
  - `test_jurisdictions_table_columns`: columns must be `Edge case`, `Where it happens`, `Approach`, `Vault effect`; a section that says `No jurisdiction differences known` passes
  - `test_diagram_needs_image_link`: no `![...](x.png)` fails; with `base_dir` set, a missing file fails and an existing file passes (use `tempfile.TemporaryDirectory`)
  - `test_decisions_table_columns`: `Decision`, `Owner`, `How it is decided`, `Decide by`; `None open` passes
  - `test_cli_exit_codes`: `main([str(fixture)]) == 0`; a temp copy with a bad status gives `1`
- [ ] **Step 2: Run; expect FAIL.**
- [ ] **Step 3: Implement** the four checks and `main`; wire all checks into `validate`. The diagram check resolves the image path against `base_dir` (the page's folder in the CLI).
- [ ] **Step 4: Run; expect PASS.**
- [ ] **Step 5: Commit** (`feat(business-object-page): validator sources, jurisdictions, diagram, decisions and CLI`).

### Task 4: The page template

**Files:**
- Create: `.claude/skills/business-object-page/assets/template.md`
- Modify: `.claude/skills/business-object-page/tests/test_validate_page.py`

**Interfaces:**
- Consumes: `validate`, the constants.
- Produces: `template.md`, with every section in order, the exact table headers from the Global Constraints, and `<<placeholder>>` markers (double angle brackets) wherever the author must write.

- [ ] **Step 1: Write failing test** `test_template_has_all_sections_and_headers`: reads the template, runs `parse_page`, asserts the section list equals `SECTIONS`, and that each table header row equals the expected columns for `Vault objects`, `Fields` (inside the example `###` block), `Sources and mapping`, `Jurisdictions map`, `Open decisions`.
- [ ] **Step 2: Run; expect FAIL.**
- [ ] **Step 3: Write the template.** It carries, under each heading, a one-line italic instruction (what the section holds and which rule it follows, e.g. R7 under Jurisdictions map) and the empty table. The header table has rows `Object`, `Parent object`, `Owner domain`, `Shared with`, `Scope`, `Status`, `Version`, `Last updated`.
- [ ] **Step 4: Run; expect PASS.**
- [ ] **Step 5: Commit** (`feat(business-object-page): page template`).

### Task 5: Pilot pages: Natural Person and Party

**Files:**
- Create: `Rosetta/Business_Objects/Natural_Person.md`
- Create: `Rosetta/Business_Objects/Party.md`

**Interfaces:**
- Consumes: `template.md`, the validator CLI.
- Produces: two valid pages; the names `hub_natural_person`, `hub_party`, `lnk_natural_person__party` used by Tasks 6–7.

Content is taken only from the draft the user supplied. Anything the draft does not say is not added; it goes to Open decisions.

**Natural Person** (header: owner `Registries`; shared with `Taxation Contributions and Licences, Finance, Benefits, Compliance, AEOI`; scope `Global`; parent `Party`; status `Draft`). Definition and "Why it is its own object" from the draft (inclusive scope; identification differs from a Legal Entity; the only object tied to a biological lifecycle). Vault objects:

| Type | Name | Grain | Business key |
| --- | --- | --- | --- |
| Hub | `hub_natural_person` | one row per business key | `natural_person_bk`: the primary person identifier of the source of record, assigned once and never changed. It is not an identity document |
| Link | `lnk_natural_person__party` | one row per distinct combination of natural person and party | `hub_natural_person`, `hub_party` |
| Satellite | `sat_natural_person__name` | one row per parent key and name type, for each time its values change | — |
| Satellite | `sat_natural_person__identification` | one row per parent key and identification document (type and number), for each time its values change | — |
| Satellite | `sat_natural_person__registration` | one row per parent key and registration basis, for each time its values change | — |
| Satellite | `sat_natural_person__lifecycle` | one row per parent key, for each time its values change | — |

The hash key `natural_person_hk` is computed from `jurisdiction_code`, `key_type_code` and the normalized `natural_person_bk`, joined with a fixed separator. Normalization: trimmed, case-folded, Unicode-normalized. The hash algorithm is a platform decision and is not named on the page. Satellites carry only the parent's hash key.

Fields (structural columns first in each: `natural_person_hk`, `load_dts`, `record_source`; Satellites also `hashdiff`; Hub also `natural_person_bk`, `jurisdiction_code string`, `key_type_code string`; Link also `party_hk`):
- `sat_natural_person__name`: `name_type_code string` (legal name, alias, tribal title, community alias), `name_text string` (a mononym is valid), `script_code string` (writing system of the name). Personal data: yes for all.
- `sat_natural_person__identification`: `identification_type_code string` (passport, residence permit, national identity number, community card), `identification_id string` (never numeric), `issuing_jurisdiction_code string`, `expiry_date date` null. Personal data yes. A person with no document has no row. Whether a document is valid today is worked out when asked, never stored. A foreign passport exists only here; a residence permit or national ID is also a Credential in the Legal objects, which carries the right and the issuing Authority.
- `sat_natural_person__registration`: `registration_basis_code string` (document, biometric, testimony, census), `registration_date date`. Personal data no. A person can have several bases over time.
- `sat_natural_person__lifecycle`: `status_code string`, `origin_event_code string`, `origin_date date`, `termination_event_code string` null, `termination_date date` null. Personal data no. Citizenship and visa type are not here: they are Credentials or Entitlements attached to the person.

Modeling considerations must also state: a person known under two source keys stays two Hub rows, joined by a same-as relationship recorded when the source reports a merge. Keys are never rewritten and nothing is deleted. Open decisions add: the name of that same-as Link (the "link between two roles of the same object" case); and the configuration for a source whose primary key is a document number, where a key change is treated as a re-key event.

Jurisdictions map rows (from the draft): single names (mononyms) in tribal and island communities; no identity number for refugees, stateless persons and unregistered births; record created from a village chief's testimony; local character sets; temporary residents and cross-border workers. Each with approach (R7) and vault effect.

Example (illustrative, labelled as such): a person registered in Papua New Guinea from a village chief's testimony, with one mononym and no identification row. Show the `hub_natural_person` row and the rows of `sat_natural_person__name`, `sat_natural_person__registration` and `sat_natural_person__lifecycle`.

Sources and mapping: `No endpoints declared yet`. Open decisions: how biometric templates attach (through the Digital Artifact object, link defined on that page); whether a testimony's attesting authority is a link to Government Authority; the identifier choice per jurisdiction (platform configuration). Owners and "decide by" in the Principles format.

**Party** (owner `Registries`, scope `Global`, no parent): vault object `hub_party` only (`party_bk`, the Nexus-assigned party identifier; fields `party_hk`, `party_bk`, `load_dts`, `record_source`). Definition from the draft. "Why it is its own object": objects that point to "whoever owes or asks" need one Hub to point to, and identification stays in Natural Person and Legal Entity. States that Government Authority is not a Party.

- [ ] **Step 1:** Write both pages from the template.
- [ ] **Step 2: Validate.** Run: `python .claude/skills/business-object-page/scripts/validate_page.py Rosetta/Business_Objects/Natural_Person.md` and the same for `Party.md`. Expected for each: no output, exit code 0. The Diagram check will fail until Task 6 creates the PNG; run with the image link present and accept only that one error here.
- [ ] **Step 3: Commit** (`docs(rosetta): pilot business object pages Natural Person and Party`).

### Task 6: Pilot diagram

**Files:**
- Create: `Rosetta/Business_Objects/Natural_Person.drawio`, `Rosetta/Business_Objects/Natural_Person.png`
- Create: `Rosetta/Business_Objects/.drawio-tmp/natural_person/natural_person.spec.yaml`

**Interfaces:**
- Consumes: the vault object names from Task 5; skills `drawio` and `brand-design-system`.
- Produces: the diagram that Natural Person.md's Diagram section links.

- [ ] **Step 1:** Invoke the `drawio` and `brand-design-system` skills. Write the spec: `hub_party` (Hub, Silver palette per the Medallion rule, since these are Silver objects) on the right; `hub_natural_person` in the centre; `lnk_natural_person__party` between them; the four Satellites around `hub_natural_person`; grain sentence as a second line in each box; connector labels in Courier New on a white background.
- [ ] **Step 2:** Generate the `.drawio`, apply the brand skill's mandatory edge-label post-processing, export the PNG with draw.io Desktop (`draw.io.exe -x -f png --scale 3 -b 10 -o <png> <drawio>`).
- [ ] **Step 3: Verify.** Read the PNG: all six names visible, no overlapping lines or labels, black text on every light fill.
- [ ] **Step 4: Validate and commit.** Run the validator on `Natural_Person.md`; expected exit code 0. Commit the `.drawio`, `.png`, spec and page.

### Task 7: Index page

**Files:**
- Create: `Rosetta/Business_Objects/Index.md`

**Interfaces:**
- Consumes: the header values of the pilot pages.
- Produces: a table with columns `Object`, `Owner domain`, `Shared with`, `Scope`, `Status`, `Page`, one row per page in the folder; shared objects listed once, with every domain in `Shared with`.

- [ ] **Step 1:** Write the index with the two pilot rows and the sentence that each page follows the Business Object page format.
- [ ] **Step 2: Commit** (`docs(rosetta): business objects index`).

### Review gate: pilot

**Stop here.** The user reviews `Natural_Person.md`, `Party.md` and the diagram, and corrects the format. Task 8 starts only after the user approves the pilot. Corrections to the format are applied to the validator, the template and the pilot pages first (tests updated before code).

### Task 8: The skill

**Files:**
- Create: `.claude/skills/business-object-page/SKILL.md`

**Interfaces:**
- Consumes: `assets/template.md`, `scripts/validate_page.py`, the corrected pilot pages as the worked example, skills `drawio` and `brand-design-system`.
- Produces: a skill named `business-object-page` that triggers on a raw object draft or a request to write, update or add a Business Object page.

- [ ] **Step 1: Write the pressure scenario first.** In `.claude/skills/business-object-page/tests/scenarios.md`, record the scenario that Task 9 will run: the user's raw `Legal Entity` draft, expected results (valid page, `hub_legal_entity` separate from `hub_party`, `lnk_legal_entity__party`, no endpoints invented, Corporate and Collective/Informal both present as Jurisdictions map rows), and the failures to watch for (copying "Hub or Link" without a choice, inventing endpoints, putting Legal Entity in a Satellite of `hub_party`).
- [ ] **Step 2: Write `SKILL.md`.** Frontmatter `name: business-object-page` and a `description` that begins "Use when" and names the trigger (a raw draft of a business object, or adding, updating or checking a Business Object page for Rosetta). Body, in this order:
  1. The ten-step procedure from the spec section 4, each step one imperative line.
  2. The fixed decisions: Party/Natural Person/Legal Entity structure; Government Authority is Platform; payment objects are Finance; flat folder; jurisdictions may be named; endpoints declared only.
  3. The never-invent list.
  4. How to run the validator and what to do with each error tag.
  5. The common mistakes table (draft-style names; Legal Entity as a Satellite; a Hub for a calendar; a Satellite holding two grains).
  6. A pointer to the pilot pages as worked examples.
- [ ] **Step 3: Commit** (`feat(business-object-page): skill instructions and pressure scenario`).

### Task 9: Skill dry run

**Files:**
- Create: `Rosetta/Business_Objects/Legal_Entity.md`, `.drawio`, `.png`
- Modify: `.claude/skills/business-object-page/SKILL.md` (only to close gaps found)

**Interfaces:**
- Consumes: the skill, the scenario from Task 8.
- Produces: a validated Legal Entity page and an updated Index row.

- [ ] **Step 1:** Follow the skill on the user's Legal Entity draft (Corporate/Formal and Collective/Informal; lifecycle independence; hierarchies; flexible identification). Produce the page, diagram and validation.
- [ ] **Step 2: Verify against the scenario.** Validator exit code 0; the three watched failures absent; `grep -c "bronze\." Rosetta/Business_Objects/Legal_Entity.md` shows no invented Bronze table (the section says `No endpoints declared yet`).
- [ ] **Step 3:** Close any gap in `SKILL.md` that the run exposed, then re-run the validator.
- [ ] **Step 4: Commit** (`docs(rosetta): Legal Entity page; skill gaps closed`).

---

## Out of the plan

Confluence publication of the pages stays a separate, reviewed step after each batch. The remaining objects (Platform, Taxation, Finance and others) run through the skill after Task 9, by domain, each batch with its own review.
