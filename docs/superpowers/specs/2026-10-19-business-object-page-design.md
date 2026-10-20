# Business Object page and skill: design

**Date:** 2026-10-19 · **Status:** Draft, awaiting review · **Section:** Nexus Rosetta, Business Objects

## 1. Understanding

**Intent.** Rosetta needs a Business Objects section where every business object of the Public Services Suite (PSS 3.0) is defined once, in one standard page. Seven domains take part: Platform, Registries, Taxation, Contributions and Licences, Finance, Compliance, Benefits and AEOI. Some objects belong to one domain, some are shared, and some are global. The format must fit all of them, and a skill must turn a raw draft of any object into that format.

**Success looks like:**
- Any team can open one page and know what the object means, how it is stored in the vault, where its data comes from, and how it changes between jurisdictions.
- Two people writing two objects produce pages with the same structure, the same naming and the same types.
- The skill never invents what it cannot know (source endpoints, jurisdiction rules), and lists it as an open decision instead.

**Constraints inherited from the published Principles (R1–R12):** names follow the naming convention (R9), types come from the allowed list (R11), every table states its grain (R12), variation between jurisdictions is a scenario and not a new object (R7), every source element is mapped, parked or excluded with a reason (R8).

**Decisions already taken with the user:**
1. One page per **business object**, not per Hub, Link or Satellite. A business object is a cluster of vault objects.
2. The first object is **Natural Person**, with **Party** as its parent.
3. The format is built first, then the skill, then the rest of the objects in batches by domain.

## 2. The page

One markdown file per business object, with its diagram next to it. Eleven sections, always in this order. A section with nothing to say states that explicitly; it is never deleted.

| # | Section | Content |
| --- | --- | --- |
| 1 | **Header** | Object name, parent object (if any), owner domain, shared with, scope, status, version, last updated |
| 2 | **Definition** | The agreed meaning, in plain language |
| 3 | **Why it is its own object** | The "why separate it?" argument, with the lifecycle, key and owner that differ from its neighbours |
| 4 | **Vault objects** | One row per vault object: type, name, grain, business key |
| 5 | **Fields** | One table per vault object: column, type, nullable, personal data, description |
| 6 | **Sources and mapping** | The source API endpoints that relate to this object, declared as facts, and the mapping record from Bronze path to vault object |
| 7 | **Jurisdictions map** | Edge cases that need a different approach: edge case, where it happens, approach, effect on the vault |
| 8 | **Examples** | At least one realistic scenario, shown as sample rows of the Hub and its Satellites |
| 9 | **Modeling considerations** | Rules the model must respect, and what breaks if they are ignored |
| 10 | **Diagram** | The standard diagram of the cluster, in the brand style |
| 11 | **Open decisions** | Same table as Principles: decision, owner, how it is decided, decide by |

### Header values

| Field | Allowed values |
| --- | --- |
| Owner domain | Platform, Registries, Taxation Contributions and Licences, Finance, Compliance, Benefits, AEOI |
| Shared with | Zero or more of the same list |
| Scope | **Domain** (used only by its owner), **Shared** (used by named other domains), **Global** (used by all domains) |
| Status | **Draft** (written, not reviewed), **Reviewed** (Data Team has read it), **Agreed** (approved for use in Silver) |

### Vault object types

| Type | Name pattern | Grain sentence starts with |
| --- | --- | --- |
| Hub | `hub_<object>` | one row per business key |
| Link | `lnk_<object_a>__<object_b>` | one row per distinct combination of |
| Non-historized Link | `lnk_<object_a>__<object_b>`, flagged as non-historized | one row per occurrence of |
| Satellite | `sat_<parent>__<descriptor>` | one row per parent key, for each time its values change |
| Reference table | `ref_<name>` | one row per code |

A Non-historized Link is used for events and transactions, which happen once and never change: messages, audit entries, payments. A reference table is used for things that are not business events and are not created by the business: calendars, configuration, code lists.

### The Vault objects table

| Column | Meaning |
| --- | --- |
| Type | One of the five types above |
| Name | Follows the naming convention exactly |
| Grain | A sentence that starts with the right "one row per" |
| Business key | For a Hub, the key and how it is chosen; for a Link, the Hubs it connects; otherwise "—" |

### The Fields table (one per vault object)

| Column | Meaning |
| --- | --- |
| Column | Name, ending in a representation term; structural columns (`<object>_hk`, `load_dts`, `record_source`, `hashdiff`) are listed first |
| Type | From the allowed list. `decimal(P,S)` always has precision and scale |
| Null | Yes or no |
| Personal data | Yes or no. A yes forces the attribute into its own Satellite (T4) |
| Description | One line |

### The Jurisdictions map table

| Column | Meaning |
| --- | --- |
| Edge case | What differs, in one line |
| Where it happens | Countries or kinds of jurisdiction, as examples |
| Approach | How the model handles it, following R7 (a scenario, not a new object) |
| Vault effect | Which vault object carries the difference |

## 3. Where the pages live

| What | Where |
| --- | --- |
| Source of truth | `Rosetta/Business_Objects/<Object_Name>.md`, one flat folder with no domain in the path |
| Diagram | Next to the page: `<Object_Name>.drawio` and `<Object_Name>.png` |
| Working files | `Rosetta/Business_Objects/.drawio-tmp/` |
| Confluence | One child page per object under **Business Objects** in the NXR space |
| Index | The Business Objects page lists every object: owner domain, shared with, scope, status, link |

The domain is data in the page header, not a place on disk. An object shared by several domains is one file, and the index lists it under the owner and under every domain it is shared with.

## 4. The skill

**Name:** `business-object-page`, a project skill in `.claude/skills/business-object-page/`.

**Input:** a raw draft of one object (definition, modeling considerations, examples, in any order), plus optionally the owner domain and any source documentation.

**What it does, in order:**
1. **Classify** each thing in the draft into a vault object type. Anything described as "a Hub or a Link" is forced to a single decision and recorded.
2. **Name** every vault object by the naming convention. A draft name such as `Hub_Tax_Account` becomes `hub_tax_account`.
3. **Type** every column from the allowed list, by representation term. Money is `decimal(P,S)`, identifiers are `string`, moments are `timestamptz`.
4. **State the grain** of every vault object.
5. **Split** personal data into its own Satellite.
6. **Extract** edge cases from the draft into the Jurisdictions map.
7. **Turn** the draft's examples into sample rows of the Hub and Satellites.
8. **Draw** the cluster with the `drawio` skill, following `brand-design-system`.
9. **Collect** everything it could not decide into Open decisions.
10. **Validate** the page, then write the markdown and the diagram.

**Endpoints are declared, never discovered.** The author gives the endpoints that relate to the object, and the skill writes only those, as plain declarative lines: source, endpoint, Bronze table name, what it provides. It does not add endpoints that merely look related. When none have been given, the section says "No endpoints declared yet" and the page carries no mapping record.

**It never invents:** source API endpoints, the owner domain when the draft does not say (asks), jurisdiction rules the draft does not state, and business keys the draft does not name.

**Jurisdictions may be named.** Pages may name specific countries and territories, because they explain why a design choice was made (a flag registry in the Marshall Islands, customary land tenure in Papua New Guinea). The skill keeps them where the draft has them and never replaces them with generic wording. The pages do not refer to internal meetings.

**Validator** (`scripts/validate_page.py`, run by the skill before it reports done). It fails the page when:
- a section is missing or out of order;
- a name does not match its pattern, or contains an abbreviation not on the approved list;
- a type is not on the allowed list, or a `decimal` has no precision and scale;
- a vault object has no grain, or a grain that starts with the wrong "one row per";
- the header uses a value outside its list;
- a Satellite has a parent that is not in the Vault objects table;
- a Link connects Hubs that are not alphabetical.

The validator checks form. Whether the model is right stays a human review.

## 5. Pilot

The first page is **Natural Person**, written from the draft already supplied, with **Party** as its parent. It is the test of the format: it has a parent, strong jurisdiction edge cases (mononyms, tribal names, no identity number), several Satellite splits and a clear personal-data boundary.

### Party, Natural Person and Legal Entity

A Natural Person and a Legal Entity identify themselves to the State in different ways. A Natural Person may exist with no identity number at all, on a testimony or a biometric record. A Legal Entity is identified by a registration or tax number, or, if it is informal, by a registry code tied to a community. They also have different lifecycles: a biological one, and an administrative one. So they are **separate Hubs, each with its own business key and its own identification Satellites**. They are not subtypes held in Satellites of one Hub.

**Party** is the family, not a place to store attributes. Many objects must point to "whoever owes or asks" without caring which kind it is: a tax account, a payment, a benefit claim. **Decided:** a thin `hub_party`, whose only key is a Nexus-assigned party identifier, joined by `lnk_natural_person__party` and `lnk_legal_entity__party`. All identification stays in the two specific Hubs. Every object that points to "whoever owes or asks" points to `hub_party`. The rejected alternative was no `hub_party`, with every shared relationship duplicated once per kind.

### Government Authority is not a Party

A **Government Authority** is the body that operates the deployment: it issues credentials, grants entitlements and enforces restrictions. Nexus is deployed into its system. It is therefore a **Platform** object, with its own page, and not a kind of Party. The only parties are the citizens and the legal entities that use the system to pay taxes or ask for a benefit. The Authority object carries what is specific to the deployment: which Authority issues which credential, and which Authority applies which rule in which jurisdiction.

After the pilot is reviewed, the skill is written from the corrected page, and the other objects are run through it in domain order: Registries, Platform, then Taxation, Contributions and Licences.

**Ownership decided so far:** Payment Event and the other payment objects belong to **Finance**, even though the first draft placed them under Taxes. Taxation, Contributions and Licences share them.

## 6. Out of scope for this design

- The content of the other objects.
- Choosing the technology for lineage or the catalog (already covered in Nexus).
- Automatic publishing to Confluence. The skill produces the markdown and the diagram; the Confluence update stays a separate, reviewed step.

## 7. Risks

| Risk | What we do about it |
| --- | --- |
| The draft's examples use abbreviations or names that break the convention | The skill renames them and lists each rename in the page, so the author can see what changed |
| A draft treats an authority or an agency as a Party | It is recorded as the Government Authority object in Platform, and the draft's role-playing links are kept as links to that object |
| Two domains define the same object differently | Both appear in the Jurisdictions map or Open decisions; the page is not marked Agreed until one definition is chosen (R6) |
| The pages drift from Confluence | The markdown is the source; the Confluence page is updated from it and carries the same version number |
