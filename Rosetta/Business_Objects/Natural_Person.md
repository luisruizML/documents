# Natural Person

## Header

| **Field** | **Value** |
| --- | --- |
| Object | Natural Person |
| Parent object | Party |
| Owner domain | Registries |
| Shared with | Taxation Contributions and Licences, Finance, Benefits, Compliance, AEOI |
| Scope | Global |
| Status | Draft |
| Version | 0.1 |
| Last updated | 2026-10-19 |

## Definition

A Natural Person is an individual human being recognized by the State as a subject of rights, obligations and service provision, regardless of civic, legal or migratory status.

The scope is inclusive: full citizens, temporary residents, cross-border workers, long-term tourists, refugees and stateless persons. Citizenship and visa type do not define the person. They are Credentials or Entitlements attached to the person (see the Legal objects).

## Why it is its own object

- **It is identified differently from a Legal Entity.** A Natural Person can exist with no national identity number and no passport, created from biometrics, a testimony from a local authority such as a village chief, or a census record. A Legal Entity is identified by a registration or tax number, or, if it is informal, by a registry code tied to a community. One shared identification structure would force one of them into the shape of the other.
- **It is the only object tied to a biological lifecycle.** It becomes active with an origin event (birth or immigration) and is inactivated, never deleted, by a termination event (confirmed death). A Legal Entity is created and ended by administrative acts.
- **Its identifiers change; the person does not.** A foreign resident may be known first by a passport, then by a residence permit, then by a national identity number. The person is the same throughout.
- **Name structures differ.** The model cannot force First Name, Middle Name and Last Name: single names (mononyms), tribal titles, community aliases and local character sets are all valid.

If a Natural Person were merged into a single Party table, every registry would have to invent a document number for people who have none, and every change of identifier would look like a new person.

## Vault objects

| **Type** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- |
| Hub | `hub_natural_person` | one row per business key | `natural_person_bk`: the primary person identifier of the source of record, assigned once and never changed. It is not an identity document |
| Link | `lnk_natural_person__party` | one row per distinct combination of natural person and party | `hub_natural_person`, `hub_party` |
| Satellite | `sat_natural_person__name` | one row per parent key and name type, for each time its values change | — |
| Satellite | `sat_natural_person__identification` | one row per parent key and identification document (type and number), for each time its values change | — |
| Satellite | `sat_natural_person__registration` | one row per parent key and registration basis, for each time its values change | — |
| Satellite | `sat_natural_person__lifecycle` | one row per parent key, for each time its values change | — |
| Satellite | `sat_natural_person__demographics` | one row per parent key, replaced in place when its values change | — |
| Satellite | `sat_natural_person__demographics_history` | one row per parent key, for each time its values change | — |
| Satellite | `sat_natural_person__physical_traits` | one row per parent key, replaced in place when its values change | — |
| Satellite | `sat_natural_person__physical_traits_history` | one row per parent key, for each time its values change | — |

The hash key `natural_person_hk` is computed from `jurisdiction_code`, `key_type_code` and the normalized `natural_person_bk`, joined with a fixed separator. Normalization: trimmed, case-folded, Unicode-normalized. The hash algorithm is a platform decision and is not named here. Satellites carry only the parent's hash key.

## Fields

*Indicators in Role: ◆ own hash key · ◇ hash key of another object · ● business key · ▪ load metadata · Δ hashdiff. Default: — means no default, so the loader must supply the value; a literal is a default in the sense of Iceberg format version 3.*

### hub_natural_person

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◆ | `string` | No | No | — | Hash key, from jurisdiction, key type and business key |
| `natural_person_bk` | ● | `string` | No | No | — | Primary person identifier of the source of record |
| `jurisdiction_code` | | `string` | No | No | — | Jurisdiction that owns the key, ISO 3166-1 alpha-3: e.g. `PNG`, `WSM`, `NZL` |
| `key_type_code` | | `string` | No | No | — | Which kind of identifier the business key is: e.g. `registry_person_id`, `civil_registry_number`, `census_id` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### lnk_natural_person__party

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the natural person |
| `party_hk` | ◇ | `string` | No | No | — | Hash key of the party |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### sat_natural_person__name

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `name_type_code` | | `string` | No | Yes | — | Which kind of name this is: e.g. `legal_name`, `alias`, `tribal_title`, `community_alias` |
| `name_text` | | `string` | No | Yes | — | The name as written; a single name is valid: e.g. `Kila`, `Maria Tui`, `Aroha` |
| `script_code` | | `string` | No | Yes | — | Writing system of the name, ISO 15924: e.g. `Latn`, `Cyrl`, `Arab` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_natural_person__identification

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `identification_type_code` | | `string` | No | Yes | — | Kind of document: e.g. `passport`, `residence_permit`, `national_identity_number`, `community_card` |
| `identification_id` | | `string` | No | Yes | — | The identifier as issued, always text: e.g. `X1234567`, `RP-889`, `N-555` |
| `issuing_jurisdiction_code` | | `string` | No | Yes | — | Jurisdiction that issued the document, ISO 3166-1 alpha-3: e.g. `NZL`, `WSM`, `PNG` |
| `expiry_date` | | `date` | Yes | Yes | null | When the document stops being valid; empty if it does not expire |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_natural_person__registration

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `registration_basis_code` | | `string` | No | No | — | Why the person was registered: e.g. `document`, `biometric`, `testimony`, `census` |
| `registration_date` | | `date` | No | No | — | When the person was registered on this basis |
| `artifact_uri` | | `string` | Yes | Yes | null | Pointer to the evidence held in Digital Artifact, such as a biometric template or a signed testimony; only the pointer is stored: e.g. `artifact://biometric/9f3a`, `artifact://testimony/p7-2026`, `artifact://census/c-1204`; empty when the basis has no artifact |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_natural_person__lifecycle

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `status_code` | | `string` | No | No | — | One of `active`, `inactive` |
| `origin_event_code` | | `string` | No | No | — | One of `birth`, `immigration` |
| `origin_date` | | `date` | Yes | No | null | Date of the origin event; empty when unknown, as with an unregistered birth |
| `termination_event_code` | | `string` | Yes | No | null | Only `death` (confirmed); empty while the person is active |
| `termination_date` | | `date` | Yes | No | null | Date of the termination event |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_natural_person__demographics

Keeps no history: the row is updated in place (row versioning). `row_version` starts at 1 and goes up by one with each update; the previous values are not kept. It serves the same purpose as `sat_natural_person__demographics_history`; the Platform configuration says which one a jurisdiction loads.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `gender_code` | | `string` | No | Yes | — | Gender as the jurisdiction defines it; the allowed list is set per jurisdiction: e.g. `male`, `female`, `non_binary`, `unspecified` |
| `row_version` | | `int` | No | No | `1` | How many times the row has been written: e.g. `1`, `2`, `3` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus last wrote the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the last write came from |

### sat_natural_person__demographics_history

Keeps its history: every change adds a row (SCD Type 2). The allowed `gender_code` values depend on the jurisdiction and can change over time. It carries the same attributes as `sat_natural_person__demographics`.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `gender_code` | | `string` | No | Yes | — | Gender as the jurisdiction defines it; the allowed list is set per jurisdiction: e.g. `male`, `female`, `non_binary`, `unspecified` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_natural_person__physical_traits

Keeps no history: the row is updated in place (row versioning). `row_version` starts at 1 and goes up by one with each update; the previous values are not kept. It serves the same purpose as `sat_natural_person__physical_traits_history`; the Platform configuration says which one a jurisdiction loads.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `height_cm` | | `decimal(4,1)` | Yes | Yes | null | Body height in centimetres, one decimal: e.g. `172.5`, `160.0`, `188.0`; empty when not measured |
| `blood_type_code` | | `string` | Yes | Yes | null | ABO group and Rh factor; empty when unknown. One of `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-` |
| `row_version` | | `int` | No | No | `1` | How many times the row has been written: e.g. `1`, `2`, `3` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus last wrote the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the last write came from |

### sat_natural_person__physical_traits_history

Keeps its history: every change adds a row (SCD Type 2). It carries the same attributes as `sat_natural_person__physical_traits`.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `height_cm` | | `decimal(4,1)` | Yes | Yes | null | Body height in centimetres, one decimal: e.g. `172.5`, `160.0`, `188.0`; empty when not measured |
| `blood_type_code` | | `string` | Yes | Yes | null | ABO group and Rh factor; empty when unknown. One of `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

## Sources and mapping

No endpoints declared yet

## Jurisdictions map

| **Edge case** | **Where it happens** | **Approach** | **Vault effect** |
| --- | --- | --- | --- |
| Single names (mononyms) and tribal titles | Papua New Guinea and other island and customary-law communities | The name is stored as written in `name_text`; no first, middle or last name is required (R7: a scenario of the same object) | `sat_natural_person__name`, with the kind of name in `name_type_code` |
| No identity document: refugees, stateless persons, unregistered births | Refugee-hosting and emerging-economy jurisdictions | The person exists without an identification row; the key is assigned by the registry | No row in `sat_natural_person__identification`; basis recorded in `sat_natural_person__registration` |
| Record created from a local authority's testimony | Customary-law communities, for example a village chief in Papua New Guinea | Registration basis is testimony; the person is later linked to documents when they exist | A `testimony` row in `sat_natural_person__registration` |
| Local character sets | Any jurisdiction with a non-Latin script | The name keeps its original script; `script_code` says which | `sat_natural_person__name` |
| Temporary residents, cross-border workers, long-term tourists | Any jurisdiction with a migration route | They are the same kind of person; their status is a Credential or Entitlement | Nothing on this object; see the Legal objects |
| Gender recorded with two values, then three or more | A jurisdiction that widens its definition | The code list in force is set for the jurisdiction; each change in a person's value is a new row | New rows in `sat_natural_person__demographics_history`; earlier rows stay as history |
| Gender recorded with three or more values, then two | A jurisdiction that narrows its definition | Same as above; a value no longer in the list stays readable in the earlier rows | New rows in `sat_natural_person__demographics_history` |
| Gender recorded with two values only | A jurisdiction that never widens its definition | Either satellite, with a shorter list | `sat_natural_person__demographics` or `sat_natural_person__demographics_history`, as configured |
| Passport first, then residence permit, then national identity number | Any jurisdiction with a naturalization route | Each document is a new identification row; the person's key never changes | New rows in `sat_natural_person__identification` |

## Examples

Illustrative data. The first example is a person with no document; the second is a resident whose identifiers change over time.

**A village chief registered from a testimony (Papua New Guinea).**

`hub_natural_person`

| **natural_person_bk** | **jurisdiction_code** | **key_type_code** |
| --- | --- | --- |
| P-7 | PNG | registry_person_id |

`sat_natural_person__name`

| **name_type_code** | **name_text** | **script_code** |
| --- | --- | --- |
| tribal_title | Kila | Latn |

`sat_natural_person__registration`

| **registration_basis_code** | **registration_date** |
| --- | --- |
| testimony | 2026-03-12 |

`sat_natural_person__lifecycle`

| **status_code** | **origin_event_code** | **origin_date** |
| --- | --- | --- |
| active | birth | (empty) |

`sat_natural_person__identification` has no row for this person.

**A foreign resident whose identifiers change (Samoa).** The key `P-1` stays the same throughout.

`sat_natural_person__identification`

| **identification_type_code** | **identification_id** | **issuing_jurisdiction_code** | **expiry_date** | **Loaded** |
| --- | --- | --- | --- | --- |
| passport | X1234567 | NZL | 2027-05-01 | on arrival |
| passport | X7654321 | NZL | 2037-05-01 | on renewal; the first row stays as history |
| residence_permit | RP-889 | WSM | 2030-01-15 | when the permit was issued |
| national_identity_number | N-555 | WSM | (empty) | after naturalization |

**A person whose jurisdiction widens its gender list.** `sat_natural_person__demographics_history` keeps both rows.

| **gender_code** | **Loaded** |
| --- | --- |
| female | before the change of list |
| non_binary | after the change of list; the first row stays as history |

`sat_natural_person__physical_traits` holds one row for the same person, updated in place. If the jurisdiction asks for history, `sat_natural_person__physical_traits_history` holds a row for each change instead.

| **height_cm** | **blood_type_code** | **row_version** |
| --- | --- | --- |
| 172.5 | O+ | 2 |

## Modeling considerations

- **Identifiers are facts, not keys.** Passports, permits and national numbers live in `sat_natural_person__identification` and are used to find and match a person. The business key is the source's own person identifier, so adding or replacing a document never changes a key.
- **Validity is never stored.** Whether a document is valid today is worked out when asked, from `expiry_date`. A scheduled check may publish an event when a date passes.
- **A person known under two source keys stays two Hub rows.** They are joined by a same-as relationship recorded when the source reports a merge. Keys are never rewritten and nothing is deleted.
- **Citizenship and visa type are not attributes.** They are Credentials and Entitlements. A residence permit or national identity number is also a Credential in the Legal objects, which carries the right and the issuing Authority; here it is only an identifier.
- **Personal data is kept in its own Satellites.** Name and identification hold personal data. Lifecycle does not, so it can be read by roles that must not see identity. Demographics and physical traits hold sensitive personal data and are also kept apart. The registration Satellite holds only a pointer (`artifact_uri`) to evidence in Digital Artifact, which is personal data in itself, so it is marked PII.
- **History is chosen by how the attribute behaves.** An attribute whose value or allowed list can change over time, such as gender, goes in a Satellite that keeps history. An attribute that does not need history, such as blood type, goes in a Satellite that is updated in place with `row_version`. By default there is no history. Every such group is delivered as a pair that serves the same purpose with a different mechanism, one updated in place and one with history (`_history`), and the Platform configuration says which one a jurisdiction loads.
- **The allowed values of a code belong to a Code List, not to the column.** Codes such as `gender_code`, `jurisdiction_code` and `key_type_code` take their values from the Code List object, which holds them per jurisdiction with validity dates. The column stays a string, so a change of list never changes the table. Codes that the logic depends on (`status_code`, `origin_event_code`, `termination_event_code`) and `blood_type_code` are closed lists written in the Description.
- **Derived values are not stored (R13).** Age and age group are computed from the birth date in the Gold layer; this page keeps only the date (`origin_date`).
- **A person is never deleted.** A confirmed death inactivates the record through `sat_natural_person__lifecycle`.
- **Government Authority is not a Party.** Only citizens and legal entities that use the system are parties.

## Diagram

![Natural Person cluster](Natural_Person.png)

![Natural Person cluster, full](Natural_Person_Full.png)

## Open decisions

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| How biometric templates attach to a person | Data Architecture Engineer and Data Product Owner | Only a pointer is stored here (`artifact_uri` in `sat_natural_person__registration`); the Digital Artifact page defines the artifact and its link | Before the Digital Artifact page is reviewed |
| Whether the attesting authority of a testimony is a link to Government Authority | Data Architecture Engineer and Data Product Owner | Decided when the Government Authority page is written | Before the first mapping that needs it |
| The name of the same-as Link between two Natural Person records | Data Architecture Engineer and Data Product Owner | They decide the name, following the Link rules in the Principles | Before the first mapping that needs it |
| Configuration for a source whose primary key is a document number | Data Architecture Engineer | A key change is treated as a re-key event and recorded with a same-as link | When such a source is onboarded |
| Which Natural Person codes become Code List values | Data Architecture Engineer | The Code List object holds them; the rule for which codes qualify is decided with that page | Before the Code List page is reviewed |
| Which key type and jurisdiction each source uses | Platform configuration | Set in the Nexus configuration for each jurisdiction | When a jurisdiction is configured |
