# Legal Entity

## Header

| **Field** | **Value** |
| --- | --- |
| Object | Legal Entity |
| Parent object | Party |
| Owner domain | Registries |
| Shared with | Taxation Contributions and Licences, Finance, Benefits, Compliance, AEOI |
| Scope | Global |
| Status | Draft |
| Version | 0.1 |
| Last updated | 2026-10-20 |

## Definition

A Legal Entity is a non-human organization, association or collective recognized by the State that holds rights, assumes legal responsibilities, conducts economic activities or interacts with government services.

It supports two variations of the same object. A **corporate (formal)** entity is a legally incorporated body such as a limited liability company, a multinational corporation, a state-owned enterprise or a formally registered NGO, with an official charter, a governance structure and a Tax Identification Number or Company Registration Number. A **collective (informal)** entity is a group recognized by social, cultural or customary law rather than corporate law, such as a tribal authority, an indigenous council, a family farming collective or an informal market vendor association. The State registers it to allocate resources, such as agricultural subsidies, or to grant land rights, such as customary tenure, even when it has no formal corporate paperwork.

## Why it is its own object

- **It is identified differently from a Natural Person.** A formal entity has a tax or company registration number. An informal one may have only a government-issued registry code tied to a village or to a community leader. Both are valid business keys of the one Hub. A Natural Person can exist with no identifier at all, so the two cannot share an identification structure.
- **Its lifecycle is administrative.** A Legal Entity is created by an act (incorporation, formal recognition) and can exist indefinitely. It ends by legal dissolution, bankruptcy or merger, never by a biological event.
- **It nests without limit.** A Legal Entity can own other Legal Entities, and it is linked to the Natural Persons who act for it: representatives, directors or tribal chiefs.
- **Two variations are one object.** A tribal authority and a limited company both hold rights and responsibilities toward the State. The difference is a scenario of the same object (R7), not a second object.

If a Legal Entity were a Satellite of Party, every Satellite of Party would have to carry two identification structures, and the entity's own hierarchy would have nowhere to attach.

## Vault objects

| **Type** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- |
| Hub | `hub_legal_entity` | one row per business key | `legal_entity_bk`: the primary identifier of the entity in the source of record, assigned once and never changed. It is a registration or tax number for a formal entity and a registry code for an informal one |
| Link | `lnk_legal_entity__party` | one row per distinct combination of legal entity and party | `hub_legal_entity`, `hub_party` |
| Link | `lnk_legal_entity__natural_person` | one row per distinct combination of legal entity and natural person | `hub_legal_entity`, `hub_natural_person` |
| Link | `lnk_legal_entity__party_owner` | one row per distinct combination of legal entity and owner party | `hub_legal_entity`, `hub_party` (owner) |
| Satellite | `sat_legal_entity__name` | one row per parent key and name type, for each time its values change | — |
| Satellite | `sat_legal_entity__identification` | one row per parent key and identification (type and number), for each time its values change | — |
| Satellite | `sat_legal_entity__classification` | one row per parent key, for each time its values change | — |
| Satellite | `sat_legal_entity__lifecycle` | one row per parent key, for each time its values change | — |
| Satellite | `sat_legal_entity__natural_person__representation` | one row per parent key and role, for each time its values change | — |
| Satellite | `sat_legal_entity__party_owner__ownership` | one row per parent key and holding type, for each time its values change | — |

The hash key `legal_entity_hk` is computed from `jurisdiction_code`, `key_type_code` and the normalized `legal_entity_bk`, joined with a fixed separator. Normalization: trimmed, case-folded, Unicode-normalized. The hash algorithm is a platform decision and is not named here. Satellites carry only the parent's hash key.

`lnk_legal_entity__party` says that a Legal Entity **is** a Party: each Legal Entity has exactly one. `lnk_legal_entity__party_owner` says that a Party **owns** a Legal Entity: it is a different relationship, with its own rows, and one Legal Entity can have many owners. The owner is any Party, so it can be a Natural Person or another Legal Entity.

## Fields

*Indicators in Role: ◆ own hash key · ◇ hash key of another object · ● business key · ▪ load metadata · Δ hashdiff. Default: — means no default, so the loader must supply the value; a literal is a default in the sense of Iceberg format version 3.*

### hub_legal_entity

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◆ | `string` | No | No | — | Hash key, from jurisdiction, key type and business key |
| `legal_entity_bk` | ● | `string` | No | No | — | Primary identifier of the entity in the source of record |
| `jurisdiction_code` | | `string` | No | No | — | Jurisdiction that owns the key, ISO 3166-1 alpha-3: e.g. `WSM`, `PNG`, `NZL` |
| `key_type_code` | | `string` | No | No | — | Which kind of identifier the business key is: e.g. `tax_identification_number`, `company_registration_number`, `community_registry_code` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### lnk_legal_entity__party

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the legal entity |
| `party_hk` | ◇ | `string` | No | No | — | Hash key of the party |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### lnk_legal_entity__natural_person

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the legal entity |
| `natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the natural person who acts for the entity |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### sat_legal_entity__name

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `name_type_code` | | `string` | No | No | — | Which kind of name this is: e.g. `legal_name`, `trading_name`, `community_name`, `alias` |
| `name_text` | | `string` | No | No | — | The name as written: e.g. `Pacific Fisheries Limited`, `Council of Elders`, `Kunai Growers Collective` |
| `script_code` | | `string` | No | No | — | Writing system of the name, ISO 15924: e.g. `Latn`, `Cyrl`, `Arab` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_legal_entity__identification

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `identification_type_code` | | `string` | No | No | — | Kind of identifier: e.g. `tax_identification_number`, `company_registration_number`, `community_registry_code`, `customary_land_registry_code` |
| `identification_id` | | `string` | No | No | — | The identifier as issued, always text: e.g. `TIN-884210`, `C-2291`, `HLD-017` |
| `issuing_jurisdiction_code` | | `string` | No | No | — | Jurisdiction that issued the identifier, ISO 3166-1 alpha-3: e.g. `WSM`, `PNG`, `NZL` |
| `community_name` | | `string` | Yes | No | null | Village or community the identifier is tied to, for an informal entity; empty for a formal one |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_legal_entity__classification

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `formality_code` | | `string` | No | No | — | One of `corporate`, `collective` |
| `legal_form_code` | | `string` | No | No | — | The legal form in the jurisdiction: e.g. `limited_liability_company`, `state_owned_enterprise`, `registered_ngo`, `tribal_authority`, `indigenous_council`, `farming_collective` |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_legal_entity__lifecycle

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `status_code` | | `string` | No | No | — | One of `active`, `inactive` |
| `origin_event_code` | | `string` | No | No | — | One of `incorporation`, `formal_recognition` |
| `origin_date` | | `date` | Yes | No | null | Date of the origin event; empty when unknown, as with a customary body recognized long ago |
| `termination_event_code` | | `string` | Yes | No | null | One of `dissolution`, `bankruptcy`, `merger`; empty while the entity is active |
| `termination_date` | | `date` | Yes | No | null | Date of the termination event |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### sat_legal_entity__natural_person__representation

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `lnk_legal_entity__natural_person_hk` | ◇ | `string` | No | No | — | Hash key of the link |
| `role_code` | | `string` | No | No | — | How the person acts for the entity: e.g. `director`, `representative`, `tribal_chief`, `trustee` |
| `appointed_date` | | `date` | Yes | No | null | When the person took the role; empty when unknown |
| `end_date` | | `date` | Yes | No | null | When the person left the role; empty while the role continues |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### lnk_legal_entity__party_owner

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `legal_entity_hk` | ◇ | `string` | No | No | — | Hash key of the legal entity that is owned |
| `owner_party_hk` | ◇ | `string` | No | No | — | Hash key of the party that owns it, a Natural Person or a Legal Entity |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### sat_legal_entity__party_owner__ownership

One Satellite holds the three dimensions of an ownership, so a change in any of them is one new row. Each holding type is its own row: an owner can hold the bare ownership of one share and the usufruct of another over the same entity.

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `lnk_legal_entity__party_owner_hk` | ◇ | `string` | No | No | — | Hash key of the link |
| `holding_type_code` | | `string` | No | No | — | The legal nature of the title. One of `full_ownership` (complete title with all economic yields), `bare_ownership` (title to the capital without current yields), `usufruct` (right to the dividends without title to the capital), `beneficial_ownership` (economic entitlement held through an intermediary, nominee or trust), `legal_nominee` (registered titleholder acting for a third party, with no economic benefit), `synthetic_economic` (contractual rights indexed to the shares, such as phantom stock, without holding equity) |
| `ownership_share_percent` | | `decimal(7,4)` | No | Yes | — | The share of the entity this holding represents, from 0 to 100: e.g. `60.0000`, `33.3333`, `100.0000` |
| `liquidity_status_code` | | `string` | No | No | `unrestricted` | Restrictions on distributions and disposal. One of `unrestricted` (free disposal), `attached_sequestered` (judicial freeze, embargo or court deposit, so the funds are blocked), `pledged_retained` (pledged to a creditor, owner keeps the distributions), `pledged_cash_sweep` (pledged, and every distribution goes to the creditor), `escrow_locked` (held by a third party until a condition is met) |
| `vesting_status_code` | | `string` | No | No | `fully_vested` | How mature the award is. One of `fully_vested` (unconditional, cannot be forfeited), `unvested_subject_to_clawback` (contingent on time or performance, with a risk of forfeiture or repurchase) |
| `effective_date` | | `date` | No | No | — | First day this combination applies |
| `end_date` | | `date` | Yes | No | null | Last day this combination applies; empty while it still applies |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

## Sources and mapping

No endpoints declared yet

## Jurisdictions map

| **Edge case** | **Where it happens** | **Approach** | **Vault effect** |
| --- | --- | --- | --- |
| Formal company with a tax or company registration number | Any jurisdiction with company law | The number is the business key; the key type says which number it is | `hub_legal_entity` with `key_type_code` `tax_identification_number` or `company_registration_number`; `formality_code` is `corporate` |
| Tribal authority, indigenous council or family farming collective with no corporate paperwork | Papua New Guinea and other customary-law communities | The entity is registered under a government-issued registry code tied to a village or a leader (R7: a scenario of the same object) | `hub_legal_entity` with `key_type_code` `community_registry_code`; `formality_code` is `collective`; `community_name` in `sat_legal_entity__identification` |
| Informal market vendor association | Emerging-economy jurisdictions | Registered so the State can allocate resources such as subsidies | Same as a collective |
| Customary land tenure held by a community | Papua New Guinea | The holder is a Legal Entity; the land right itself is a Legal object | `hub_legal_entity`; nothing on this object for the right |
| Entity that owns other entities, or is owned by persons | Any jurisdiction with corporate groups | Each entity is its own Hub row; the owner is a Party, so a person and a company are handled the same way | `lnk_legal_entity__party_owner` and `sat_legal_entity__party_owner__ownership` |
| Title split between two holders (bare ownership and usufruct) | Any jurisdiction | Each title is its own holding, with its own share | Two rows in `sat_legal_entity__party_owner__ownership`, one for each holding type |
| Shares held through a nominee, a trust or an intermediary | Any jurisdiction with fiscal transparency rules | The registered holder and the beneficiary are two owners with different holding types | Rows with `legal_nominee` and `beneficial_ownership` |
| Shares pledged, frozen by a court or held in escrow | Any jurisdiction | The restriction is a status of the holding, not a second object; when it ends, a new row is added | `liquidity_status_code` in `sat_legal_entity__party_owner__ownership` |
| Award that is not yet vested | Any jurisdiction | The vesting stage is a status of the holding; consolidation is a new row | `vesting_status_code` in `sat_legal_entity__party_owner__ownership` |
| Tribal chief, director or representative of an entity | Any jurisdiction | A person acts for an entity in a role, for a period | `lnk_legal_entity__natural_person` and `sat_legal_entity__natural_person__representation` |
| Dissolution, bankruptcy or merger | Any jurisdiction | The entity is inactivated and never deleted; a merger is also recorded as a relationship between the two entities | `sat_legal_entity__lifecycle`; the merger relationship is a same-as Link not yet named |

## Examples

Illustrative data. The first example is a formal company; the second is an informal council identified only by a community registry code.

**A formal company (Samoa).**

`hub_legal_entity`

| **legal_entity_bk** | **jurisdiction_code** | **key_type_code** |
| --- | --- | --- |
| C-2291 | WSM | company_registration_number |

`sat_legal_entity__name`

| **name_type_code** | **name_text** | **script_code** |
| --- | --- | --- |
| legal_name | Pacific Fisheries Limited | Latn |

`sat_legal_entity__classification`

| **formality_code** | **legal_form_code** |
| --- | --- |
| corporate | limited_liability_company |

`sat_legal_entity__lifecycle`

| **status_code** | **origin_event_code** | **origin_date** |
| --- | --- | --- |
| active | incorporation | 2019-04-02 |

**An informal council (Papua New Guinea).** It has no tax number and is known only by a registry code tied to a village.

`hub_legal_entity`

| **legal_entity_bk** | **jurisdiction_code** | **key_type_code** |
| --- | --- | --- |
| HLD-017 | PNG | community_registry_code |

`sat_legal_entity__identification`

| **identification_type_code** | **identification_id** | **issuing_jurisdiction_code** | **community_name** |
| --- | --- | --- | --- |
| community_registry_code | HLD-017 | PNG | Tari village |

`sat_legal_entity__classification`

| **formality_code** | **legal_form_code** |
| --- | --- |
| collective | indigenous_council |

`sat_legal_entity__natural_person__representation` for the village chief, a Natural Person with key `P-7`

| **role_code** | **appointed_date** | **end_date** |
| --- | --- | --- |
| tribal_chief | (empty) | (empty) |

**Ownership of a company (Samoa).** Pacific Fisheries Limited (`C-2291`) is owned 60% by a person and 40% by another company. Both owners are Parties.

`sat_legal_entity__party_owner__ownership`

| **Owner** | **holding_type_code** | **ownership_share_percent** | **liquidity_status_code** | **vesting_status_code** | **effective_date** |
| --- | --- | --- | --- | --- | --- |
| Natural Person `P-1` | full_ownership | 60.0000 | unrestricted | fully_vested | 2019-04-02 |
| Legal Entity `C-3310` | full_ownership | 40.0000 | unrestricted | fully_vested | 2019-04-02 |

**A share that changes its state.** The person pledges the shares to a bank, and later the pledge turns into a cash sweep. `sat_legal_entity__party_owner__ownership` keeps each state as a row and does not overwrite the earlier one.

| **Owner** | **holding_type_code** | **ownership_share_percent** | **liquidity_status_code** | **effective_date** | **end_date** |
| --- | --- | --- | --- | --- | --- |
| Natural Person `P-1` | full_ownership | 60.0000 | unrestricted | 2019-04-02 | 2024-06-30 |
| Natural Person `P-1` | full_ownership | 60.0000 | pledged_retained | 2024-07-01 | 2025-02-28 |
| Natural Person `P-1` | full_ownership | 60.0000 | pledged_cash_sweep | 2025-03-01 | (empty) |

**A title split in two.** A parent holds the bare ownership of 30% and a child holds the usufruct of the same 30%; there is one row for each holding type.

| **Owner** | **holding_type_code** | **ownership_share_percent** |
| --- | --- | --- |
| Natural Person `P-1` | bare_ownership | 30.0000 |
| Natural Person `P-9` | usufruct | 30.0000 |

## Modeling considerations

- **One Hub, two kinds of key.** A tax or company number and a community registry code are both business keys of the same Hub. The key type is part of the hash, so two keys with the same text but different types never collide.
- **Identifiers are facts, not keys.** Additional identifiers, such as a tax number added after incorporation, live in `sat_legal_entity__identification`. The business key is the source's own identifier, so adding one never changes a key.
- **Hierarchy has no depth in the model.** Ownership is a Link between a Legal Entity and its owner Party, and a Legal Entity is a Party too, so nesting is unlimited. How deep an entity sits in a group, the total share of an owner through several levels and the ultimate owner are computed in the Gold layer, never stored (R13).
- **Ownership is a different relationship from identity.** `lnk_legal_entity__party` has one row for each Legal Entity; `lnk_legal_entity__party_owner` has one row for each owner of an entity. The owner can be a Natural Person or a Legal Entity because the Link points to the Party.
- **One Satellite, three dimensions.** `holding_type_code`, `liquidity_status_code` and `vesting_status_code` are states of the same holding, so they share a Satellite; any change of one is a new row. The holding type is part of the grain: an owner with several titles over one entity has several rows, each with its own share and status.
- **A new state is a new row.** A pledge, a judicial freeze, an escrow or a vesting date is added with its dates; the earlier row stays, so the position on any past day can be rebuilt (R1). This Satellite keeps its history by default and has no in-place twin, because no jurisdiction asks to forget previous values.
- **The checks are rules, not constraints.** That the shares of one holding type add up to 100, that an entity does not own itself, and the treatment of cross-holdings are quality rules on the data, run in the Silver or Gold layer.
- **Representation is a relationship with a period.** The person is a Natural Person with their own page. The role and the dates live on the Link's Satellite, so a person can hold several roles and a role can pass to someone else without changing either Hub.
- **A Legal Entity is never deleted.** Dissolution, bankruptcy or merger inactivates the record through `sat_legal_entity__lifecycle`. After a merger, both Hub rows stay and are joined by a same-as relationship.
- **Whether an entity is active today is not stored.** It is worked out from the lifecycle dates when asked (R13).
- **Codes take their values from the Code List.** `key_type_code`, `name_type_code`, `identification_type_code`, `legal_form_code`, `role_code` and the jurisdiction codes hold values that change without changing any logic. `formality_code`, `status_code`, `origin_event_code`, `termination_event_code`, `holding_type_code`, `liquidity_status_code` and `vesting_status_code` are closed lists, because logic depends on them.
- **Government Authority is not a Legal Entity here.** The body that operates the deployment is a Platform object, not a Party.

## Diagram

Two pictures of the same cluster. Read the simplified one first, then use the full one when you need the columns. Colors: Hub indigo, Link teal, Satellite magenta; a Satellite updated in place is lighter, with a dashed border. Arrows run from the child to its parent.

### Simplified version

The shape of the cluster: 1 Hub, 3 Links and 6 Satellites, each with its name and grain. Use it to see how the objects relate. It has no columns.

![Legal Entity cluster, simplified](images/Diagrams_Legal_Entity_Simplified.png)

### Full version

The same objects, each with its Fields table (column, role, type, null, PII, default, description). Use it to check exactly what is stored. It is wide: zoom in or open the image on its own.

![Legal Entity cluster, full](images/Diagrams_Legal_Entity_Full.png)

## Open decisions

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| Whether the shares of one holding type must add up to 100 for each entity, and where the check runs | Data Architecture Engineer and Data Product Owner | Decided with Taxation, Contributions and Licences | Before the first mapping that needs it |
| Whether the stake columns are personal data only when the owner is a Natural Person | Data Architecture Engineer and Platform | Decided with the access rules of the platform; today the share is marked PII | Before the first review of this page |
| Whether `effective_date` and `end_date` are the dates the ownership applies in law, or only `load_dts` records when Nexus learned of it | Data Product Owner | Decided with the source owners | Before the first mapping that needs it |
| The name of the same-as Link between two Legal Entity records, for a merger or a re-key | Data Architecture Engineer and Data Product Owner | They decide the name, following the Link rules in the Principles | Before the first mapping that needs it |
| Whether a legal form is a value of one Code List for all jurisdictions or one list for each jurisdiction | Data Architecture Engineer and Platform | Decided with the Code List object, from the applicability of each value | Before the Code List page is reviewed |
| Whether a family-owned collective that is also a taxpayer is one Legal Entity or two | Data Product Owner | Decided with Taxation, Contributions and Licences | Before the first mapping that needs it |
| Which key type and jurisdiction each source uses | Platform configuration | Set in the Nexus configuration for each jurisdiction | When a jurisdiction is configured |
