# Pressure scenarios for `business-object-page`

Run a scenario by giving the skill the raw input and checking the result against **Expected** and **Failures to watch for**. A scenario passes only when every expected result holds and no watched failure appears.

## Scenario 1: Legal Entity from a raw draft

**Input.** The user's raw draft of `Party -> Non-Natural Person / Legal Entity`:

- Definition: a non-human organization, association or collective recognized by the State that holds rights, assumes legal responsibilities, conducts economic activities or interacts with government services.
- Two variations: **Corporate (Formal)**, with charters, governance and a Tax Identification Number or Company Registration Number; and **Collective / Informal**, recognized by social, cultural or customary law (tribal authorities, indigenous councils, family farming collectives, informal market vendor associations), registered so the State can allocate resources or grant customary land rights.
- Modeling considerations: **Lifecycle Independence** (administrative creation, dissolution, bankruptcy or merger, no biological death); **Complex Hierarchies** (a Legal Entity can own other Legal Entities; it is linked to Natural Persons as representatives, directors or tribal chiefs); **Flexible Identification** (a Tax ID or a government registry code linked to a village or community leader are both valid business keys).
- No endpoints are given.

**Expected.**

1. `validate_page.py` exits 0.
2. `hub_legal_entity` is a Hub of its own, separate from `hub_party`. `lnk_legal_entity__party` joins them.
3. `hub_party` is only referenced; it is defined on the Party page.
4. Corporate and Collective / Informal each appear as a row of the Jurisdictions map.
5. Both kinds of business key are accepted by the one Hub (`jurisdiction_code`, `key_type_code`, normalized `legal_entity_bk`).
6. The Sources and mapping section says `No endpoints declared yet`.
7. Hierarchy and representation are recorded as Links, with names that follow the Link rules; any name that is not decided is in Open decisions.
8. Both diagram images exist, and the Index has a row for the page.
9. Every `_code` column shows three or more `e.g.` values or a closed `One of` list.

**Failures to watch for.**

- Copying "Hub or Link" from the draft without choosing one.
- Inventing endpoints, Bronze tables or source systems.
- Putting Legal Entity in a Satellite of `hub_party`, or giving `hub_party` descriptive columns.
- Storing a derived value such as "is active today" or "age of the entity" (R13).
- Creating a table per code list instead of using the Code List object.
- Naming an object after its draft form (`Hub_Legal_Entity`, `LegalEntity`).
- A Satellite that holds two grains.

## Scenario 2: A draft that names an abbreviation

**Input.** A draft with `Hub_Tax_Acct` and a column `reg_no`.

**Expected.** The page uses `hub_tax_account` and a column named from the allowed representation terms; each rename is listed for the author. The validator reports no abbreviation error.

**Failures to watch for.** Keeping the abbreviation; adding it to the approved list without asking.

## Scenario 3: A draft that treats an authority as a Party

**Input.** A draft that lists a ministry as a kind of Party.

**Expected.** The ministry is recorded as the Government Authority object in Platform. No link from it to `hub_party` is created. The draft's role links stay as links to the Authority object.

**Failures to watch for.** Creating `lnk_government_authority__party`.

## Scenario 4: An attribute that may or may not need history

**Input.** A draft with `blood type` and `gender`, and a note that some jurisdictions change the gender list over time.

**Expected.** Two Satellites per group, one updated in place with `row_version` and one with `_history`. `blood_type_code` is a closed list; `gender_code` takes its values from the Code List object.

**Failures to watch for.** One Satellite for both mechanisms; a `ref_` table; a stored age.
