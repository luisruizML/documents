# Natural Person

## Header

| Field | Value |
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

| Type | Name | Grain | Business key |
| --- | --- | --- | --- |
| Hub | `hub_natural_person` | one row per business key | `natural_person_bk`: the primary person identifier of the source of record, assigned once and never changed. It is not an identity document |
| Link | `lnk_natural_person__party` | one row per distinct combination of natural person and party | `hub_natural_person`, `hub_party` |
| Satellite | `sat_natural_person__name` | one row per parent key and name type, for each time its values change | — |
| Satellite | `sat_natural_person__identification` | one row per parent key and identification document (type and number), for each time its values change | — |
| Satellite | `sat_natural_person__registration` | one row per parent key and registration basis, for each time its values change | — |
| Satellite | `sat_natural_person__lifecycle` | one row per parent key, for each time its values change | — |

The hash key `natural_person_hk` is computed from `jurisdiction_code`, `key_type_code` and the normalized `natural_person_bk`, joined with a fixed separator. Normalization: trimmed, case-folded, Unicode-normalized. The hash algorithm is a platform decision and is not named here. Satellites carry only the parent's hash key.

## Fields

### hub_natural_person

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key, from jurisdiction, key type and business key |
| `natural_person_bk` | `string` | No | No | Primary person identifier of the source of record |
| `jurisdiction_code` | `string` | No | No | Jurisdiction that owns the key (ISO 3166-1) |
| `key_type_code` | `string` | No | No | Which kind of identifier the business key is |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |

### lnk_natural_person__party

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key of the natural person |
| `party_hk` | `string` | No | No | Hash key of the party |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |

### sat_natural_person__name

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key of the parent |
| `name_type_code` | `string` | No | Yes | Legal name, alias, tribal title or community alias |
| `name_text` | `string` | No | Yes | The name as written; a single name is valid |
| `script_code` | `string` | No | Yes | Writing system of the name (ISO 15924) |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |
| `hashdiff` | `string` | No | No | Hash of the descriptive values |

### sat_natural_person__identification

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key of the parent |
| `identification_type_code` | `string` | No | Yes | Passport, residence permit, national identity number or community card |
| `identification_id` | `string` | No | Yes | The identifier as issued; never numeric |
| `issuing_jurisdiction_code` | `string` | No | Yes | Jurisdiction that issued the document (ISO 3166-1) |
| `expiry_date` | `date` | Yes | Yes | When the document stops being valid; empty if it does not expire |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |
| `hashdiff` | `string` | No | No | Hash of the descriptive values |

### sat_natural_person__registration

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key of the parent |
| `registration_basis_code` | `string` | No | No | Document, biometric, testimony or census |
| `registration_date` | `date` | No | No | When the person was registered on this basis |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |
| `hashdiff` | `string` | No | No | Hash of the descriptive values |

### sat_natural_person__lifecycle

| Column | Type | Null | Personal data | Description |
| --- | --- | --- | --- | --- |
| `natural_person_hk` | `string` | No | No | Hash key of the parent |
| `status_code` | `string` | No | No | Active or inactive |
| `origin_event_code` | `string` | No | No | Birth or immigration |
| `origin_date` | `date` | Yes | No | Date of the origin event; empty when unknown, as with an unregistered birth |
| `termination_event_code` | `string` | Yes | No | Confirmed death; empty while the person is active |
| `termination_date` | `date` | Yes | No | Date of the termination event |
| `load_dts` | `timestamptz` | No | No | When Nexus first loaded the row |
| `record_source` | `string` | No | No | Which system and endpoint the row came from |
| `hashdiff` | `string` | No | No | Hash of the descriptive values |

## Sources and mapping

No endpoints declared yet

## Jurisdictions map

| Edge case | Where it happens | Approach | Vault effect |
| --- | --- | --- | --- |
| Single names (mononyms) and tribal titles | Papua New Guinea and other island and customary-law communities | The name is stored as written in `name_text`; no first, middle or last name is required (R7: a scenario of the same object) | `sat_natural_person__name`, with the kind of name in `name_type_code` |
| No identity document: refugees, stateless persons, unregistered births | Refugee-hosting and emerging-economy jurisdictions | The person exists without an identification row; the key is assigned by the registry | No row in `sat_natural_person__identification`; basis recorded in `sat_natural_person__registration` |
| Record created from a local authority's testimony | Customary-law communities, for example a village chief in Papua New Guinea | Registration basis is testimony; the person is later linked to documents when they exist | A `testimony` row in `sat_natural_person__registration` |
| Local character sets | Any jurisdiction with a non-Latin script | The name keeps its original script; `script_code` says which | `sat_natural_person__name` |
| Temporary residents, cross-border workers, long-term tourists | Any jurisdiction with a migration route | They are the same kind of person; their status is a Credential or Entitlement | Nothing on this object; see the Legal objects |
| Passport first, then residence permit, then national identity number | Any jurisdiction with a naturalization route | Each document is a new identification row; the person's key never changes | New rows in `sat_natural_person__identification` |

## Examples

Illustrative data. The first example is a person with no document; the second is a resident whose identifiers change over time.

**A village chief registered from a testimony (Papua New Guinea).**

`hub_natural_person`

| natural_person_bk | jurisdiction_code | key_type_code |
| --- | --- | --- |
| P-7 | PNG | registry_person_id |

`sat_natural_person__name`

| name_type_code | name_text | script_code |
| --- | --- | --- |
| tribal_title | Kila | Latn |

`sat_natural_person__registration`

| registration_basis_code | registration_date |
| --- | --- |
| testimony | 2026-03-12 |

`sat_natural_person__lifecycle`

| status_code | origin_event_code | origin_date |
| --- | --- | --- |
| active | birth | (empty) |

`sat_natural_person__identification` has no row for this person.

**A foreign resident whose identifiers change (Samoa).** The key `P-1` stays the same throughout.

`sat_natural_person__identification`

| identification_type_code | identification_id | issuing_jurisdiction_code | expiry_date | Loaded |
| --- | --- | --- | --- | --- |
| passport | X1234567 | NZL | 2027-05-01 | on arrival |
| passport | X7654321 | NZL | 2037-05-01 | on renewal; the first row stays as history |
| residence_permit | RP-889 | WSM | 2030-01-15 | when the permit was issued |
| national_identity_number | N-555 | WSM | (empty) | after naturalization |

## Modeling considerations

- **Identifiers are facts, not keys.** Passports, permits and national numbers live in `sat_natural_person__identification` and are used to find and match a person. The business key is the source's own person identifier, so adding or replacing a document never changes a key.
- **Validity is never stored.** Whether a document is valid today is worked out when asked, from `expiry_date`. A scheduled check may publish an event when a date passes.
- **A person known under two source keys stays two Hub rows.** They are joined by a same-as relationship recorded when the source reports a merge. Keys are never rewritten and nothing is deleted.
- **Citizenship and visa type are not attributes.** They are Credentials and Entitlements. A residence permit or national identity number is also a Credential in the Legal objects, which carries the right and the issuing Authority; here it is only an identifier.
- **Personal data is kept in its own Satellites.** Name and identification hold personal data. Registration and lifecycle do not, so they can be read by roles that must not see identity.
- **A person is never deleted.** A confirmed death inactivates the record through `sat_natural_person__lifecycle`.
- **Government Authority is not a Party.** Only citizens and legal entities that use the system are parties.

## Diagram

![Natural Person cluster](Natural_Person.png)

## Open decisions

| Decision | Owner | How it is decided | Decide by |
| --- | --- | --- | --- |
| How biometric templates attach to a person | Data Architecture Engineer and Data Product Owner | Through the Digital Artifact object; the link is defined on that page | Before the Digital Artifact page is reviewed |
| Whether the attesting authority of a testimony is a link to Government Authority | Data Architecture Engineer and Data Product Owner | Decided when the Government Authority page is written | Before the first mapping that needs it |
| The name of the same-as Link between two Natural Person records | Data Architecture Engineer and Data Product Owner | They decide the name, following the Link rules in the Principles | Before the first mapping that needs it |
| Configuration for a source whose primary key is a document number | Data Architecture Engineer | A key change is treated as a re-key event and recorded with a same-as link | When such a source is onboarded |
| Which key type and jurisdiction each source uses | Platform configuration | Set in the Nexus configuration for each jurisdiction | When a jurisdiction is configured |
