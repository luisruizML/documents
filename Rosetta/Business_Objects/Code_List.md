# Code List

## Header

| **Field** | **Value** |
| --- | --- |
| Object | Code List |
| Parent object | — |
| Owner domain | Platform |
| Shared with | Registries, Taxation Contributions and Licences, Finance, Benefits, Compliance, AEOI |
| Scope | Global |
| Status | Draft |
| Version | 0.1 |
| Last updated | 2026-10-21 |

## Definition

A **Code List** is a **named set** of allowed values for a column, such as gender, jurisdiction or key type, together with the label of each value in each language, how the value is read and checked, the jurisdictions where it applies, the period in which it is valid, where the list is used and who may read it.

**One object** holds every list. A new list is a new row, **never a new table**, so the model does not grow with each new need.

## Why it is its own object

- **Allowed values change; tables should not.** A jurisdiction can widen or narrow its list of gender values over time. If the list were a column constraint or a table of its own, each change would change a table. Here it is new rows with validity dates.
- **The same list is used in many places.** `jurisdiction_code` appears in several objects. One list means one definition (R6), with the places that use it recorded next to it.
- **Lists differ by jurisdiction.** The values that are allowed, and the period in which they are allowed, depend on where a person or entity is registered (R7). The difference is a scenario of the one list.
- **Some lists are sensitive.** The values of a community-affiliation list, for example, must be seen only by some roles. Access is recorded on the list.
- **One table for each list does not scale.** Every new need would add a table, a page, a definition and a mapping.

## Vault objects

| **Type** | **Name** | **Definition** | **Grain** | **Business key** |
| --- | --- | --- | --- | --- |
| Hub | `hub_code_list` | The table that holds the **name of each list** of allowed values, such as gender, jurisdiction or key type. A new list is a new entry here, **never a new table**. | one row per business key | `code_list_bk`: the name of the list, such as `gender`. It is assigned once and never changed |
| Hub | `hub_code_value` | The table that holds **each value** that can appear in a list, identified by the list name and the code, such as gender:female. The same code in two lists is **two different values**. | one row per business key | `code_value_bk`: the list name and the code joined by a colon, such as `gender:female` |
| Link | `lnk_code_list__code_value` | The table that records **which values** belong to **which list**. | one row per distinct combination of code list and code value | `hub_code_list`, `hub_code_value` |
| Satellite | `sat_code_value__label` | The table that records the **name shown** to people for each value in **each language**, a short name for small screens, what it means when the name is not enough, the order in which it is listed and whether it is a draft, active or retired. | one row per parent key and language, for each time its values change | — |
| Satellite | `sat_code_value__validation` | The table that records how a value is to be read and checked: the **data type** of the value, the usual unit, the limit of levels of a hierarchy kind and, for each jurisdiction, the **pattern** its written form must follow, such as the format of a passport number. | one row per parent key and jurisdiction, for each time its values change | — |
| Satellite | `sat_code_value__applicability` | The table that records where, when and for which kind of party a value is allowed: the **jurisdiction** (a country or territory), whether it applies to natural persons, to legal entities or to both, and the **first and last day**, so the same list can differ by jurisdiction, by kind of party and **over time**. | one row per parent key, jurisdiction and party type, for each time its values change | — |
| Satellite | `sat_code_list__usage` | The table that records where a **list is used**: which object and **which column** take their values from it. | one row per parent key and column that uses the list, for each time its values change | — |
| Satellite | `sat_code_list__access` | The table that records **which roles** may see the values of a list, and **how much** each may see, for lists that only some roles may read. | one row per parent key and role, for each time its values change | — |

The hash keys `code_list_hk` and `code_value_hk` are computed from the normalized business key, as for every Hub. A value's code is part of its business key, so the same code in two lists is two values.

## Fields

*Indicators in Role: ◆ own hash key · ◇ hash key of another object · ● business key · ▪ load metadata · Δ hashdiff. Default: — means no default, so the loader must supply the value; a literal is a default in the sense of Iceberg format version 3. Code List: `List` — the values are a list of the Code List object and the column has a row in the table of the Code List page; `Closed` — a closed list, written in the Description as One of; `—` — the column is not a code.*

### hub_code_list

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_list_hk` | ◆ | `string` | No | No | — | — | Hash key, from the business key |
| `code_list_bk` | ● | `string` | No | No | — | — | Name of the list: e.g. `gender`, `jurisdiction`, `key_type` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |

### hub_code_value

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_value_hk` | ◆ | `string` | No | No | — | — | Hash key, from the business key |
| `code_value_bk` | ● | `string` | No | No | — | — | List name and code joined by a colon: e.g. `gender:female`, `jurisdiction:PNG`, `key_type:census_id` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |

### lnk_code_list__code_value

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_list_hk` | ◇ | `string` | No | No | — | — | Hash key of the code list |
| `code_value_hk` | ◇ | `string` | No | No | — | — | Hash key of the code value |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |

### sat_code_value__label

One row for each value and language. A jurisdiction with more than one official language has one row for each; a reader asks for a language and, when there is no row, falls back to the default language of the jurisdiction and then to `en`.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_value_hk` | ◇ | `string` | No | No | — | — | Hash key of the parent |
| `language_code` |  | `string` | No | No | — | List | Language of the label, BCP 47: e.g. `en`, `fr`, `sm` |
| `label_short_name` |  | `string` | Yes | No | null | — | Short name for small screens such as a phone: e.g. `F`, `PNG`, `Census id`; empty when `label_name` is short enough |
| `label_name` |  | `string` | No | No | — | — | Name shown to people on a tablet or a computer: e.g. `Female`, `Papua New Guinea`, `Census identifier` |
| `description_text` |  | `string` | Yes | No | null | — | What the value means, when the label is not enough |
| `sort_order` |  | `int` | No | No | `0` | — | Position when the list is shown in this language: e.g. `1`, `2`, `3` |
| `status_code` |  | `string` | No | No | — | Closed | One of `draft`, `active`, `retired` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | — | Hash of the descriptive values |

### sat_code_value__validation

The data type says which value column a consumer reads (R11): a trait such as `height` is a `decimal`, so its value is read from `value_number`, and a trait such as `blood_type` is a `string`, so it is read from `value_text`. Because the type is declared once here, the load casts each value once and parks a value that does not fit (R8). The pattern is a form check, not proof that the document exists.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_value_hk` | ◇ | `string` | No | No | — | — | Hash key of the parent |
| `jurisdiction_code` |  | `string` | No | No | — | List | Jurisdiction (country or territory) the pattern applies to, ISO 3166-1 alpha-3, or `any`: e.g. `COL`, `CUW`, `any` |
| `value_data_type_code` |  | `string` | No | No | — | Closed | Type of the values that use this code. One of `string`, `integer`, `decimal`, `date`, `boolean` |
| `measure_unit_code` |  | `string` | Yes | No | null | List | Usual unit of a numeric value, a value of the list `measure_unit`: e.g. `cm`, `kg`, `percent`; empty when the value has no unit |
| `max_depth_count` |  | `int` | Yes | No | null | — | Most levels a hierarchy of this kind may have, for a value that names a kind of hierarchy: e.g. `2`, `3`, `5`; empty for any other value |
| `validation_pattern_text` |  | `string` | Yes | No | null | — | Regular expression the written form must match: e.g. `^[A-Z]{2}[0-9]{6}$`, `^[0-9]{6,10}$`; empty when there is no rule |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | — | Hash of the descriptive values |

### sat_code_value__applicability

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_value_hk` | ◇ | `string` | No | No | — | — | Hash key of the parent |
| `jurisdiction_code` |  | `string` | No | No | — | List | Jurisdiction (country or territory) where the value is allowed, ISO 3166-1 alpha-3, or `any` for every jurisdiction: e.g. `PNG`, `WSM`, `any` |
| `party_type_code` |  | `string` | No | No | `any` | Closed | Kind of party the value is allowed for. One of `natural_person`, `legal_entity`, `any`; `any` when the value does not depend on the kind of party |
| `valid_from_date` |  | `date` | No | No | `1900-01-01` | — | First day the value is allowed there; `1900-01-01` when it has always been allowed |
| `valid_to_date` |  | `date` | No | No | `9999-12-31` | — | Last day the value is allowed there; `9999-12-31` while it is still allowed. When a newer row starts for the same value and jurisdiction, the loader sets this to the day before it starts |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | — | Hash of the descriptive values |

### sat_code_list__usage

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_list_hk` | ◇ | `string` | No | No | — | — | Hash key of the parent |
| `usage_object_name` |  | `string` | No | No | — | — | Vault object that uses the list: e.g. `hub_natural_person`, `sat_natural_person__demographics`, `sat_natural_person__identification` |
| `usage_column_name` |  | `string` | No | No | — | — | Column of that object that takes its values from the list: e.g. `jurisdiction_code`, `gender_code`, `issuing_jurisdiction_code` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | — | Hash of the descriptive values |

### sat_code_list__access

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Code List** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `code_list_hk` | ◇ | `string` | No | No | — | — | Hash key of the parent |
| `role_code` |  | `string` | No | No | — | — | Role the rule applies to: e.g. `registrar`, `auditor`, `analyst` |
| `access_code` |  | `string` | No | No | — | Closed | One of `read`, `read_masked`, `none` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | — | Hash of the descriptive values |

## Sources and mapping

No endpoints declared yet

## Jurisdictions map

| **Edge case** | **Where it happens** | **Approach** | **Vault effect** |
| --- | --- | --- | --- |
| A list with two values in one jurisdiction and more in another | Any jurisdiction that defines a list on its own | The values are the same rows; each jurisdiction has its own applicability rows (R7) | `sat_code_value__applicability`, one row for each jurisdiction |
| A value that only one kind of party may take, such as a place of birth for a person and a registered office for a legal entity | Any jurisdiction | The value stays one row; its applicability rows say for which kind of party it is allowed, with `any` when both may take it | `party_type_code` in `sat_code_value__applicability` |
| A jurisdiction widens its list, then narrows it | Any jurisdiction that changes a definition | The value gets an end date; a value that returns gets a new applicability row | New rows in `sat_code_value__applicability`; earlier rows stay as history |
| A value used in old records that is no longer allowed | Any jurisdiction | The value is retired, never deleted, so old rows stay readable | `status_code` changes to `retired` in `sat_code_value__label` |
| A jurisdiction with more than one official language | Any multilingual country or territory | One label row for each official language; the reader falls back to the default language of the jurisdiction, then to `en` | Rows by `language_code` in `sat_code_value__label` |
| The format of an identifier differs by country | Any jurisdiction that issues documents, for example a Colombian passport, a United States driver licence or a Curaçao national identity card | The pattern belongs to the value and the jurisdiction; a value that does not match is parked with the reason, not rejected | `validation_pattern_text` in `sat_code_value__validation` |
| A list whose values only some roles may see | Lists of sensitive attributes | The roles and what each may see are recorded on the list | Rows in `sat_code_list__access` |

## Examples

Illustrative data. The list `gender` is allowed with different values in two jurisdictions.

`hub_code_value` and `sat_code_value__label`

| **code_value_bk** | **language_code** | **label_short_name** | **label_name** | **status_code** |
| --- | --- | --- | --- | --- |
| gender:male | en | M | Male | active |
| gender:female | en | F | Female | active |
| gender:female | fr | F | Féminin | active |
| gender:non_binary | en | NB | Non-binary | active |

`sat_code_value__applicability`

| **code_value_bk** | **jurisdiction_code** | **party_type_code** | **valid_from_date** | **valid_to_date** |
| --- | --- | --- | --- | --- |
| gender:male | any | any | 1900-01-01 | 9999-12-31 |
| gender:female | any | any | 1900-01-01 | 9999-12-31 |
| gender:non_binary | WSM | any | 2024-01-01 | 9999-12-31 |
| location_role:place_of_birth | any | natural_person | 1900-01-01 | 9999-12-31 |
| location_role:registered_office | any | legal_entity | 1900-01-01 | 9999-12-31 |
| location_role:mailing_address | any | any | 1900-01-01 | 9999-12-31 |

Here a person in `PNG` can be recorded only as male or female, and a person in `WSM` as male, female or non-binary from 2024. A place of birth can be given to a natural person only, a registered office to a legal entity only, and a mailing address to either.

`sat_code_value__validation` for a passport number, a height and a kind of hierarchy

| **code_value_bk** | **jurisdiction_code** | **value_data_type_code** | **max_depth_count** | **validation_pattern_text** |
| --- | --- | --- | --- | --- |
| identification_type:passport | any | string | (empty) | (empty) |
| identification_type:passport | COL | string | (empty) | ^[A-Z]{2}[0-9]{6}$ |
| physical_trait:height | any | decimal | (empty) | (empty) |
| legal_entity_hierarchy_type:holding_group | any | string | 2 | (empty) |

A value that is later given a new rule gets a new row, and the loader closes the previous one the day before. A height is a `decimal`, so the traits Satellite reads it from `value_number`.

`sat_code_list__usage` for the list `gender`

| **usage_object_name** | **usage_column_name** |
| --- | --- |
| sat_natural_person__demographics | gender_code |
| sat_natural_person__demographics_history | gender_code |

## Modeling considerations

- **A code is a Code List value when its values can change without changing any logic.** Examples: `gender_code`, `jurisdiction_code`, `key_type_code`, `name_type_code`, `identification_type_code`, `registration_basis_code`, `script_code`. A code on which logic depends is a closed list written in the column's Description with `One of`. Examples: `status_code`, `event_status_code`, `access_code`, `value_data_type_code`.
- **A column that uses a list says so in two places.** The Description of the column points to the list, and `sat_code_list__usage` records the exact object and column. A search of either finds the other.
- **A Code List is never deleted from.** A value that is no longer allowed is retired, because records loaded earlier still carry it (R1).
- **Applicability is a scenario, not a copy.** The same value is one row; where and when it is allowed is in `sat_code_value__applicability`.
- **A value can be limited to a kind of party.** `party_type_code` in `sat_code_value__applicability` says whether a value is for natural persons, legal entities or both. The load checks the value of a column against the kind of owner of the row: the table itself says it where each kind has its own Satellite or Link, as for the places of persons and entities, so no lookup is needed. A row that does not fit is parked with the reason, not rejected. The table itself accepts any combination.
- **Access is enforced by Platform.** `sat_code_list__access` records the rule; the role-based access control of the platform applies it.
- **Which code columns are values of a Code List.** A code is a list value when it can gain, lose or change a value without any rule changing. It is a closed list, written in the Description with `One of`, when a rule branches on its values. Every such column has one row below, named `<vault table>.<column>` so that a repeated name such as `role_code` is never ambiguous, and is flagged `List` or `Closed` in the Code List column of its Fields table. The validator checks that the flag and the row agree in both directions, and the gray dashed lines of the diagrams are read from these rows. The rows follow the order of the Index, one page after the other; inside a page each Hub comes with its Satellites, then each Link with its Satellites. The examples are the values the page of the column already gives:

| **Column** | **Where its values live** | **Why** | **Examples** |
| --- | --- | --- | --- |
| `sat_party__sensitivity.sensitivity_level_code` | List `sensitivity_level` | The levels are decided by Platform; the column becomes a closed list if the access rules branch on it (open decision on the Party page) | `standard`, `restricted`, `high` |
| `sat_party__sensitivity.reason_code` | List `sensitivity_reason` | The reasons are decided by Platform, and a new one is a value | `high_income`, `public_office`, `security_risk` |
| `hub_natural_person.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `PNG` (Papua New Guinea), `WSM` (Samoa), `NZL` (New Zealand) |
| `hub_natural_person.key_type_code` | List `key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `registry_person_id`, `civil_registry_number`, `census_id` |
| `sat_natural_person__name.name_type_code` | List `name_type` | Each jurisdiction has its own kinds of name | `legal_name`, `alias`, `tribal_title`, `community_alias` |
| `sat_natural_person__name.script_code` | List `script` (ISO 15924) | An external standard (ISO 15924), loaded as a list so every column reads the same way | `Latn` (Latin), `Cyrl` (Cyrillic), `Arab` (Arabic) |
| `sat_natural_person__identification.identification_type_code` | List `identification_type` | Each jurisdiction has its own kinds of document and number | `passport`, `residence_permit`, `national_identity_number`, `community_card` |
| `sat_natural_person__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `NZL` (New Zealand), `WSM` (Samoa), `PNG` (Papua New Guinea) |
| `sat_natural_person__identification.issued_by_code` | List `issuer` | Each jurisdiction has its own authorities; the list `issuer` is kept by the platform configuration | `civil_registry`, `immigration_office`, `road_transport_authority` |
| `sat_natural_person__registration.registration_basis_code` | List `registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `document`, `biometric`, `testimony`, `census` |
| `sat_natural_person__lifecycle.event_code` | List `person_event` | A new kind of event changes no table | `birth`, `immigration`, `emigration`, `declared_missing`, `found`, `death`, `repatriation`, `burial` |
| `sat_natural_person__lifecycle.event_place_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `PNG` (Papua New Guinea), `CUW` (Curaçao), `NZL` (New Zealand) |
| `sat_natural_person__lifecycle.event_status_code` | Closed list, written in the Description | A rule branches on each value | `recorded`, `voided` |
| `sat_natural_person__demographics.gender_code` | List `gender` | Set by each jurisdiction and restricted by role | `male`, `female`, `non_binary`, `unspecified` |
| `sat_natural_person__demographics_history.gender_code` | List `gender` | Set by each jurisdiction and restricted by role | `male`, `female`, `non_binary`, `unspecified` |
| `sat_natural_person__physical_traits.trait_code` | List `physical_trait` | A new trait is a new value, not a new column | `height`, `weight`, `blood_type` |
| `sat_natural_person__physical_traits.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `cm`, `kg`, `lb` |
| `sat_natural_person__physical_traits_history.trait_code` | List `physical_trait` | A new trait is a new value, not a new column | `height`, `weight`, `blood_type` |
| `sat_natural_person__physical_traits_history.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `cm`, `kg`, `lb` |
| `sat_natural_person__community_affiliation.affiliation_type_code` | List `affiliation_type` | Set by each jurisdiction and restricted by role | `ethnicity`, `tribe`, `religion` |
| `sat_natural_person__community_affiliation.affiliation_value_code` | One list for each affiliation type (`ethnicity`, `tribe`, `religion`), named by the type | Set by each jurisdiction and restricted by role | `melanesian`, `huli`, `christian` |
| `sat_natural_person__community_affiliation_history.affiliation_type_code` | List `affiliation_type` | Set by each jurisdiction and restricted by role | `ethnicity`, `tribe`, `religion` |
| `sat_natural_person__community_affiliation_history.affiliation_value_code` | One list for each affiliation type (`ethnicity`, `tribe`, `religion`), named by the type | Set by each jurisdiction and restricted by role | `melanesian`, `huli`, `christian` |
| `sat_natural_person__natural_person_relation__relationship.relationship_type_code` | List `relationship_type` | The values differ by jurisdiction | `spouse`, `parent`, `legal_guardian` |
| `sat_natural_person__natural_person_relation__relationship.relationship_status_code` | Closed list, written in the Description | A rule branches on each value | `active`, `ended` |
| `sat_natural_person__natural_person_relation__relationship.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `divorce`, `majority`, `death` |
| `sat_natural_person__natural_person_relation__relationship.responsibility_basis_code` | List `responsibility_basis` | The values differ by jurisdiction | `minority`, `disability`, `court_appointment` |
| `hub_legal_entity.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_legal_entity.key_type_code` | List `key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `tax_identification_number`, `company_registration_number`, `community_registry_code`, `holding_registry_code` |
| `sat_legal_entity__name.name_type_code` | List `name_type` | Each jurisdiction has its own kinds of name | `legal_name`, `trading_name`, `community_name`, `alias` |
| `sat_legal_entity__name.script_code` | List `script` (ISO 15924) | An external standard (ISO 15924), loaded as a list so every column reads the same way | `Latn` (Latin), `Cyrl` (Cyrillic), `Arab` (Arabic) |
| `sat_legal_entity__identification.identification_type_code` | List `identification_type` | Each jurisdiction has its own kinds of document and number | `tax_identification_number`, `company_registration_number`, `community_registry_code`, `customary_land_registry_code` |
| `sat_legal_entity__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `sat_legal_entity__identification.community_code` | List `community` | A community is set by each jurisdiction, and a new one is a value | `tari`, `kunai`, `mendi` |
| `sat_legal_entity__registration.registration_basis_code` | List `legal_entity_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `certificate_of_incorporation`, `tax_registration`, `community_recognition` |
| `sat_legal_entity__registration.identification_type_code` | List `identification_type` | Each jurisdiction has its own kinds of document and number | `tax_identification_number`, `company_registration_number`, `community_registry_code` |
| `sat_legal_entity__classification.criterion_code` | List `classification_criterion` | A new way to classify an entity is a value | `formality`, `legal_form`, `sector`, `economic_activity` |
| `sat_legal_entity__classification.classification_code` | One list for each criterion, named by the criterion (for example `legal_form`, `sector`) | Each criterion has its own classes, and a new class is a value | `corporate`, `public`, `limited_liability_company`, `holding` |
| `sat_legal_entity__lifecycle.event_code` | List `legal_entity_event` | A new kind of event changes no table | `incorporation`, `formal_recognition`, `dissolution`, `bankruptcy`, `merger`, `restoration` |
| `sat_legal_entity__lifecycle.event_place_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `sat_legal_entity__lifecycle.event_status_code` | Closed list, written in the Description | A rule branches on each value | `recorded`, `voided` |
| `sat_legal_entity__natural_person__representation.role_code` | List `representation_role` | A new way for a person to act for an entity is a value | `director`, `representative`, `tribal_chief`, `trustee` |
| `sat_legal_entity__party_owner__ownership.holding_type_code` | Closed list, written in the Description | A rule branches on each value | `full_ownership`, `bare_ownership`, `usufruct`, `beneficial_ownership`, `legal_nominee`, `synthetic_economic` |
| `sat_legal_entity__party_owner__ownership.liquidity_status_code` | Closed list, written in the Description | A rule branches on each value | `unrestricted`, `attached_sequestered`, `pledged_retained`, `pledged_cash_sweep`, `escrow_locked` |
| `sat_legal_entity__party_owner__ownership.vesting_status_code` | Closed list, written in the Description | A rule branches on each value | `fully_vested`, `unvested_subject_to_clawback` |
| `sat_legal_entity__legal_entity_hierarchy__membership.hierarchy_type_code` | List `legal_entity_hierarchy_type` | Each kind of grouping between legal entities is a value, with its own depth limit | `holding_group`, `branch`, `division`, `government_department` |
| `sat_legal_entity__legal_entity_hierarchy__membership.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `left_group`, `dissolved`, `merged` |
| `hub_administrative_zone.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_administrative_zone.zone_scheme_code` | List `zone_scheme` | Each jurisdiction follows its own standards for zones, and a new one is a value | `iso_3166_2`, `national_census`, `electoral` |
| `sat_administrative_zone__description.zone_level_code` | List `zone_level` | Each jurisdiction divides its territory into its own levels, and a new level is a value | `province`, `district`, `ward` |
| `hub_address.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_address.key_type_code` | List `address_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `registry_address_id`, `postal_address_id`, `platform_assigned` |
| `sat_address__description.script_code` | List `script` (ISO 15924) | An external standard (ISO 15924), loaded as a list so every column reads the same way | `Latn` (Latin), `Cyrl` (Cyrillic), `Arab` (Arabic) |
| `sat_geometry__shape.geometry_type_code` | List `geometry_type` | A new kind of shape is a value | `point`, `line`, `polygon` |
| `sat_geometry__shape.srs_code` | List `spatial_reference_system` | A new reference system is a value | `EPSG:4326` (WGS 84), `EPSG:3832` (PDC Mercator), `EPSG:2193` (New Zealand Transverse Mercator 2000) |
| `sat_geometry__shape.accuracy_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `metre`, `kilometre`, `foot` |
| `sat_administrative_zone__administrative_zone_hierarchy__period.hierarchy_type_code` | List `zone_hierarchy_type` | Each kind of division of the territory is a value, with its own depth limit | `administrative`, `electoral`, `census` |
| `sat_administrative_zone__administrative_zone_hierarchy__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `border_redrawn`, `merged`, `abolished` |
| `sat_legal_entity__location__usage.role_code` | List `location_role` | A new way to use a place is a value; `party_type_code` in the Code List limits a value to natural persons or legal entities | `registered_office`, `branch_office`, `mailing_address` |
| `sat_location__natural_person__usage.role_code` | List `location_role` | A new way to use a place is a value; `party_type_code` in the Code List limits a value to natural persons or legal entities | `residence`, `mailing_address`, `place_of_birth` |
| `hub_base_parcel.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_base_parcel.key_type_code` | List `base_parcel_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `registry_parcel_id`, `customary_tenure_id`, `platform_assigned` |
| `sat_base_parcel__description.parcel_kind_code` | List `parcel_kind` | Each jurisdiction has its own land classification, and a new kind is a value | `land`, `water`, `airspace`, `subsurface` |
| `sat_base_parcel__description.land_use_code` | List `land_use` | Each jurisdiction has its own land classification, and a new use is a value | `residential`, `agricultural`, `forest`, `commercial` |
| `sat_base_parcel__description.tenure_type_code` | List `tenure_type` | Each jurisdiction has its own forms of tenure, and a new one is a value | `freehold`, `leasehold`, `customary`, `state_land` |
| `sat_base_parcel__description.area_basis_code` | List `area_basis` | Each jurisdiction records an area in its own ways, and a new way is a value | `measured_from_coordinates`, `written_in_title`, `declared_by_holder`, `estimated` |
| `sat_base_parcel__description.area_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `square_metre`, `hectare`, `acre` |
| `sat_base_parcel__boundary.boundary_type_code` | List `boundary_type` | Each jurisdiction knows its boundaries in its own ways, and a new way is a value | `surveyed`, `textual`, `natural_feature`, `customary` |
| `sat_base_parcel__characteristic.trait_code` | List `parcel_characteristic` | A new trait is a new value, not a new column | `soil_type`, `access_road`, `slope_percent`, `flood_zone` |
| `sat_base_parcel__characteristic.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `metre`, `square_metre`, `percent` |
| `sat_base_parcel__valuation.valuation_method_code` | List `valuation_method` | Each jurisdiction has its own valuation methods, and each method needs its own data | `market_comparison`, `cost_approach`, `income_approach`, `mass_appraisal` |
| `sat_base_parcel__valuation.currency_code` | List `currency` (ISO 4217) | An external standard (ISO 4217), loaded as a list | `WST` (Samoan tala), `PGK` (Papua New Guinean kina), `NZD` (New Zealand dollar) |
| `sat_base_parcel__valuation.valuation_status_code` | Closed list, written in the Description | A rule branches on each value | `draft`, `submitted`, `accepted`, `rejected`, `withdrawn` |
| `sat_base_parcel__identification.identification_type_code` | List `base_parcel_identification_type` | Each jurisdiction has its own kinds of document and number | `cadastral_number`, `title_deed_number`, `survey_plan_number`, `customary_land_register_number` |
| `sat_base_parcel__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `sat_base_parcel__identification.issued_by_code` | List `issuer` | Each jurisdiction has its own authorities; the list `issuer` is kept by the platform configuration | `land_registry`, `survey_office`, `building_authority` |
| `sat_base_parcel__registration.registration_basis_code` | List `parcel_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `survey`, `title_deed`, `customary_testimony`, `court_order` |
| `sat_base_parcel__registration.identification_type_code` | List `base_parcel_identification_type` | Each jurisdiction has its own kinds of document and number | `cadastral_number`, `title_deed_number`, `building_permit_number` |
| `sat_base_parcel__location__usage.role_code` | List `immovable_asset_location_role` | A new way to place an asset is a value | `boundary`, `footprint`, `entrance`, `address` |
| `hub_built_structure.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_built_structure.key_type_code` | List `built_structure_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `registry_structure_id`, `permit_structure_id`, `platform_assigned` |
| `sat_built_structure__description.structure_type_code` | List `structure_type` | Each jurisdiction has its own kinds of structure, and a new one is a value | `house`, `hotel`, `apartment_unit`, `pier`, `wind_turbine` |
| `sat_built_structure__characteristic.trait_code` | List `structure_characteristic` | A new trait is a new value, not a new column | `toilet_count`, `room_count`, `wall_material`, `floor_count`, `roof_material` |
| `sat_built_structure__characteristic.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `square_metre`, `metre`, `count` |
| `sat_built_structure__valuation.valuation_method_code` | List `valuation_method` | Each jurisdiction has its own valuation methods, and each method needs its own data | `market_comparison`, `cost_approach`, `income_approach`, `mass_appraisal` |
| `sat_built_structure__valuation.currency_code` | List `currency` (ISO 4217) | An external standard (ISO 4217), loaded as a list | `WST` (Samoan tala), `PGK` (Papua New Guinean kina), `NZD` (New Zealand dollar) |
| `sat_built_structure__valuation.valuation_status_code` | Closed list, written in the Description | A rule branches on each value | `draft`, `submitted`, `accepted`, `rejected`, `withdrawn` |
| `sat_built_structure__identification.identification_type_code` | List `built_structure_identification_type` | Each jurisdiction has its own kinds of document and number | `building_permit_number`, `unit_number`, `occupancy_certificate_number`, `street_number` |
| `sat_built_structure__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `sat_built_structure__identification.issued_by_code` | List `issuer` | Each jurisdiction has its own authorities; the list `issuer` is kept by the platform configuration | `land_registry`, `survey_office`, `building_authority` |
| `sat_built_structure__registration.registration_basis_code` | List `structure_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `building_permit`, `completion_certificate`, `inspection`, `owner_declaration` |
| `sat_built_structure__registration.identification_type_code` | List `built_structure_identification_type` | Each jurisdiction has its own kinds of document and number | `cadastral_number`, `title_deed_number`, `building_permit_number` |
| `sat_base_parcel__built_structure__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `demolished`, `moved`, `parcel_merged` |
| `sat_built_structure__built_structure_hierarchy__membership.hierarchy_type_code` | List `structure_hierarchy_type` | Each kind of containment of a structure is a value, with its own depth limit | `strata_unit`, `wing`, `annex`, `floor` |
| `sat_built_structure__built_structure_hierarchy__membership.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `demolished`, `merged`, `reorganized` |
| `sat_built_structure__location__usage.role_code` | List `immovable_asset_location_role` | A new way to place an asset is a value | `boundary`, `footprint`, `entrance`, `address` |
| `hub_base_asset.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_base_asset.key_type_code` | List `base_asset_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `imo_number`, `vehicle_identification_number`, `tail_number`, `platform_assigned` |
| `sat_base_asset__description.asset_kind_code` | List `asset_kind` | Each jurisdiction has its own kinds of assets, and a new one is a value | `vessel`, `aircraft`, `special_vehicle`, `canoe` |
| `sat_base_asset__description.asset_class_code` | List `asset_class` | Each jurisdiction has its own classes of assets, and a new one is a value | `fishing_vessel`, `helicopter`, `crane_truck` |
| `sat_base_asset__characteristic.trait_code` | List `asset_characteristic` | A new trait is a new value, not a new column | `length_overall`, `gross_tonnage`, `seat_count`, `engine_count`, `hull_material` |
| `sat_base_asset__characteristic.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `metre`, `tonne`, `count` |
| `sat_base_asset__valuation.valuation_method_code` | List `valuation_method` | Each jurisdiction has its own valuation methods, and each method needs its own data | `market_comparison`, `cost_approach`, `income_approach`, `mass_appraisal` |
| `sat_base_asset__valuation.currency_code` | List `currency` (ISO 4217) | An external standard (ISO 4217), loaded as a list | `WST` (Samoan tala), `PGK` (Papua New Guinean kina), `NZD` (New Zealand dollar) |
| `sat_base_asset__valuation.valuation_status_code` | Closed list, written in the Description | A rule branches on each value | `draft`, `submitted`, `accepted`, `rejected`, `withdrawn` |
| `sat_base_asset__identification.identification_type_code` | List `base_asset_identification_type` | Each jurisdiction has its own kinds of document and number | `hull_number`, `call_sign`, `maritime_mobile_service_identity`, `local_registration_number` |
| `sat_base_asset__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `VUT` (Vanuatu), `MHL` (Marshall Islands) |
| `sat_base_asset__identification.issued_by_code` | List `issuer` | Each jurisdiction has its own authorities; the list `issuer` is kept by the platform configuration | `maritime_authority`, `civil_aviation_authority`, `transport_registry` |
| `sat_base_asset__registration.registration_basis_code` | List `asset_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `builder_certificate`, `bill_of_sale`, `inspection`, `owner_declaration` |
| `sat_base_asset__registration.identification_type_code` | List `base_asset_identification_type` | Each jurisdiction has its own kinds of document and number | `hull_number`, `engine_serial_number`, `call_sign` |
| `sat_base_asset__flag.flag_state_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | A flag is a country, so it reads the same list as every column that names one | `MHL` (Marshall Islands), `VUT` (Vanuatu), `WSM` (Samoa) |
| `sat_base_asset__flag.registry_type_code` | List `flag_registry_type` | Each jurisdiction has its own registries, and a new one is a value | `national_registry`, `open_registry`, `bareboat_charter_registry` |
| `sat_base_asset__location__usage.role_code` | List `movable_asset_location_role` | A new way to place an asset is a value | `port_of_registry`, `home_port`, `base_location` |
| `hub_swappable_component.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_swappable_component.key_type_code` | List `swappable_component_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `engine_serial_number`, `manufacturer_part_number`, `platform_assigned` |
| `sat_swappable_component__description.component_kind_code` | List `component_kind` | A new kind of part is a value | `engine`, `propeller`, `gearbox`, `rotor` |
| `sat_swappable_component__characteristic.trait_code` | List `component_characteristic` | A new trait is a new value, not a new column | `rated_power`, `fuel_type`, `operating_hours`, `cylinder_count` |
| `sat_swappable_component__characteristic.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `metre`, `tonne`, `count` |
| `sat_swappable_component__valuation.valuation_method_code` | List `valuation_method` | Each jurisdiction has its own valuation methods, and each method needs its own data | `market_comparison`, `cost_approach`, `income_approach`, `mass_appraisal` |
| `sat_swappable_component__valuation.currency_code` | List `currency` (ISO 4217) | An external standard (ISO 4217), loaded as a list | `WST` (Samoan tala), `PGK` (Papua New Guinean kina), `NZD` (New Zealand dollar) |
| `sat_swappable_component__valuation.valuation_status_code` | Closed list, written in the Description | A rule branches on each value | `draft`, `submitted`, `accepted`, `rejected`, `withdrawn` |
| `sat_swappable_component__identification.identification_type_code` | List `swappable_component_identification_type` | Each jurisdiction has its own kinds of document and number | `serial_number`, `type_certificate_number`, `local_part_number` |
| `sat_swappable_component__identification.issuing_jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `VUT` (Vanuatu), `MHL` (Marshall Islands) |
| `sat_swappable_component__identification.issued_by_code` | List `issuer` | Each jurisdiction has its own authorities; the list `issuer` is kept by the platform configuration | `maritime_authority`, `civil_aviation_authority`, `transport_registry` |
| `sat_swappable_component__registration.registration_basis_code` | List `component_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `maker_certificate`, `bill_of_sale`, `inspection`, `owner_declaration` |
| `sat_swappable_component__registration.identification_type_code` | List `swappable_component_identification_type` | Each jurisdiction has its own kinds of document and number | `hull_number`, `engine_serial_number`, `call_sign` |
| `sat_base_asset__swappable_component__period.position_code` | List `component_position` | A new position on an asset is a value | `port_engine`, `starboard_engine`, `main_rotor` |
| `sat_base_asset__swappable_component__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `removed`, `replaced`, `scrapped` |
| `sat_swappable_component__swappable_component_hierarchy__period.hierarchy_type_code` | List `component_hierarchy_type` | Each kind of containment of a part is a value, with its own depth limit | `sub_assembly`, `accessory`, `module`, `attachment` |
| `sat_swappable_component__swappable_component_hierarchy__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `removed`, `replaced`, `scrapped` |
| `hub_model_catalog.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_model_catalog.key_type_code` | List `model_catalog_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `icao_type_designator`, `maker_model_code`, `platform_assigned` |
| `sat_model_catalog__description.model_kind_code` | List `model_kind` | A new kind of model is a value | `vessel_hull`, `aircraft_airframe`, `engine`, `vehicle_chassis` |
| `sat_model_catalog__characteristic.trait_code` | List `model_characteristic` | A new trait is a new value, not a new column | `seat_count`, `maximum_takeoff_weight`, `rated_power`, `fuel_type` |
| `sat_model_catalog__characteristic.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `metre`, `tonne`, `count` |
| `hub_entitlement.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_entitlement.key_type_code` | List `entitlement_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `licence_number`, `permit_reference`, `quota_certificate_number`, `platform_assigned` |
| `sat_entitlement__description.entitlement_type_code` | List `entitlement_type` | Each jurisdiction has its own rights and licences, and a new one is a value | `driving_privilege`, `fishing_quota`, `change_of_use_permit`, `tourism_operation`, `residence_right`, `tax_holiday` |
| `sat_entitlement__description.activity_code` | List `entitlement_activity` | A new activity is a value | `heavy_goods_driving`, `commercial_fishing`, `passenger_transport`, `residential_use` |
| `sat_entitlement__description.issuing_authority_code` | List `issuer` | The authority that issues is a value of the platform configuration, not a Party | `transport_authority`, `fisheries_authority`, `planning_authority` |
| `sat_entitlement__quota.quota_type_code` | List `quota_type` | A new thing to limit is a value | `catch_weight`, `fishing_days`, `passenger_count`, `vehicle_weight` |
| `sat_entitlement__quota.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `tonne`, `day`, `person` |
| `sat_entitlement__quota.period_code` | List `quota_period` | A new period is a value | `per_year`, `per_voyage`, `per_season` |
| `sat_entitlement__status.status_code` | Closed list, written in the Description | A rule branches on each value | `active`, `suspended`, `revoked`, `surrendered` |
| `sat_entitlement__status.reason_code` | List `entitlement_status_reason` | Each jurisdiction has its own reasons for a change of status | `court_order`, `unpaid_fee`, `holder_request`, `safety_breach` |
| `sat_entitlement__party_holder__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `transferred`, `expired`, `deceased`, `surrendered` |
| `sat_base_asset__entitlement__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `replaced`, `sold`, `expired` |
| `sat_base_parcel__entitlement__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `replaced`, `sold`, `expired` |
| `sat_built_structure__entitlement__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `replaced`, `sold`, `expired` |
| `hub_credential.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_credential.key_type_code` | List `credential_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `card_number`, `certificate_serial`, `document_number`, `platform_assigned` |
| `sat_credential__description.credential_type_code` | List `credential_type` | Each jurisdiction has its own credentials, and a new one is a value | `licence_card`, `certificate`, `smart_card`, `visa_label`, `permit_letter` |
| `sat_credential__description.form_code` | Closed list, written in the Description | A rule branches on each value | `physical`, `digital` |
| `sat_credential__description.issuing_authority_code` | List `issuer` | The authority that issues is a value of the platform configuration, not a Party | `transport_authority`, `fisheries_authority`, `immigration_authority` |
| `sat_credential__status.status_code` | Closed list, written in the Description | A rule branches on each value | `active`, `lost`, `destroyed`, `stolen`, `surrendered`, `replaced`, `withheld`, `revoked` |
| `sat_credential__status.reason_code` | List `credential_status_reason` | Each jurisdiction has its own reasons for a change of status | `hurricane`, `theft`, `renewal`, `damaged` |
| `sat_credential__entitlement__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `replaced`, `expired`, `surrendered` |
| `hub_rrr.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3) | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `NZL` (New Zealand) |
| `hub_rrr.key_type_code` | List `rrr_key_type` | Each jurisdiction has its own kinds of identifier, and a new kind is a value | `registry_entry_id`, `deed_reference`, `decision_reference`, `platform_assigned` |
| `sat_rrr__description.rrr_class_code` | Closed list, written in the Description | A rule branches on each value | `right`, `restriction`, `responsibility` |
| `sat_rrr__description.rrr_type_code` | List `rrr_type` | Each jurisdiction has its own kinds of bond, and a new one is a value; the list says which class each belongs to and which are ownership | `freehold`, `leasehold`, `customary_title`, `state_title`, `mortgage`, `access_easement`, `embargo`, `river_cleanup` |
| `sat_rrr__description.imposed_by_code` | List `issuer` | The authority that imposes is a value of the platform configuration, not a Party | `land_registry`, `maritime_authority`, `court` |
| `sat_rrr__status.status_code` | Closed list, written in the Description | A rule branches on each value | `proposed`, `registered`, `disputed`, `discharged`, `cancelled` |
| `sat_rrr__registration.registration_basis_code` | List `rrr_registration_basis` | Each jurisdiction accepts its own kinds of evidence for a registration | `title_deed`, `lease_agreement`, `court_order`, `customary_testimony` |
| `sat_rrr__registration.identification_type_code` | List `rrr_identification_type` | Each jurisdiction has its own kinds of document and number | `deed_number`, `lease_number`, `case_number` |
| `sat_party__rrr__participation.participation_role_code` | Closed list, written in the Description | A rule branches on each value | `holder`, `counterparty`, `authority` |
| `sat_base_asset__rrr__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `discharged`, `sold`, `released` |
| `sat_base_parcel__rrr__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `discharged`, `sold`, `released` |
| `sat_built_structure__rrr__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `discharged`, `sold`, `released` |
| `sat_rrr__swappable_component__period.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `discharged`, `sold`, `released` |
| `sat_rrr__rrr_hierarchy__derivation.derivation_type_code` | List `rrr_derivation_type` | A new kind of derivation is a value | `lease`, `sublease`, `easement_grant`, `customary_allocation` |
| `sat_rrr__rrr_hierarchy__derivation.end_reason_code` | List `end_reason` | The values differ by jurisdiction | `expired`, `surrendered`, `merged` |
| `sat_code_list__access.access_code` | Closed list, written in the Description | A rule branches on each value | `read`, `read_masked`, `none` |
| `sat_code_value__label.language_code` | List `language` (BCP 47) | An external standard (BCP 47), loaded as a list so every column reads the same way | `en` (English), `fr` (French), `sm` (Samoan) |
| `sat_code_value__label.status_code` | Closed list, written in the Description | A rule branches on each value | `draft`, `active`, `retired` |
| `sat_code_value__validation.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3), or `any` for every jurisdiction | One list for every column that names a country or territory | `COL` (Colombia), `CUW` (Curaçao), `any` |
| `sat_code_value__validation.value_data_type_code` | Closed list, written in the Description | A rule branches on each value | `string`, `integer`, `decimal`, `date`, `boolean` |
| `sat_code_value__validation.measure_unit_code` | List `measure_unit` | A new unit is a new value, not a new column | `cm`, `kg`, `percent` |
| `sat_code_value__applicability.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3), or `any` for every jurisdiction | One list for every column that names a country or territory | `PNG` (Papua New Guinea), `WSM` (Samoa), `any` |
| `sat_code_value__applicability.party_type_code` | Closed list, written in the Description | A rule branches on each value | `natural_person`, `legal_entity`, `any`, `any` |
| `sat_load_configuration__mechanism.jurisdiction_code` | List `jurisdiction` (ISO 3166-1 alpha-3), or `any` for every jurisdiction | One list for every column that names a country or territory | `WSM` (Samoa), `PNG` (Papua New Guinea), `any` |
| `sat_load_configuration__mechanism.mechanism_code` | Closed list, written in the Description | A rule branches on each value | `row_versioning`, `history` |

- **A date range closes the one before it.** In `sat_code_value__applicability` and `sat_code_value__validation` a new row for the same value, jurisdiction and party type closes the open one: its end becomes the day before the new start (Principles, "Validity ranges").
- **A hierarchy kind has a depth.** `max_depth_count` in `sat_code_value__validation` says how many levels a kind of hierarchy may have. It is a setting of the value, so a deeper hierarchy changes a number and no table.
- **A value has a type.** `value_data_type_code` in `sat_code_value__validation` says whether the values of a code are strings, whole numbers, decimals, dates or booleans, so the load casts once and the Gold layer does not guess (R11).
- **External standards are still lists.** ISO 3166-1 for jurisdictions and ISO 15924 for scripts are loaded as lists, so every column reads the same way.

## Diagram

Two pictures of the same cluster. Read the simplified one first, then use the full one when you need the columns. Colors: Hub indigo, Link teal, Satellite magenta; a Satellite updated in place is lighter, with a dashed border. Arrows run from the child to its parent.

### Simplified version

The shape of the cluster: 2 Hubs, 1 Link and 5 Satellites, each with its name and grain. Use it to see how the objects relate. It has no columns.

![Code List cluster, simplified](images/Diagrams_Code_List_Simplified.png)

### Full version

The same objects, each with its Fields table (column, role, type, null, PII, default, description). Use it to check exactly what is stored. It is wide: zoom in or open the image on its own.

![Code List cluster, full](images/Diagrams_Code_List_Full.png)

## Open decisions

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| Where the roles of `sat_code_list__access` come from | Platform | Decided with the role-based access control design of the platform | Before the first list with restricted values |
| Whether the rule for which codes become Code List values is added to the Principles | Data Architecture Engineer | Decided in the Principles, from the examples in this page | Before the first review of this page |
| Whether `usage_object_name` and `usage_column_name` are filled by hand or read from the catalog | Data Architecture Engineer and Platform | Decided when the catalog (R5) is set up | Before the first list is loaded |
| Whether the validation pattern of a value is a regular expression only, or can name a check rule such as a check digit | Data Architecture Engineer | Decided with the first source that has a check digit | Before the first identification type is loaded |
| Whether a mapping from an old list to its replacement, such as an old gender list to a new one, is kept as data here | Data Architecture Engineer and Data Product Owner | Decided when the first jurisdiction changes a list that is used in reports | When such a change is announced |
| Whether a list can have a parent list, such as a region inside a jurisdiction | Data Architecture Engineer | Decided when the first hierarchical list is needed | When such a list is requested |
