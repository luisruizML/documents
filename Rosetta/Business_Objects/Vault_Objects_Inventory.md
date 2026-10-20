# Vault Objects Inventory

Every Hub, Link and Satellite of the [Business Objects](Index.md) pages, one table per object type, with the owner domain and the object added on the left. Generated from the pages by `build_inventory.py`; regenerate it whenever a page adds or changes a Vault object.

## Hubs

| **Owner domain** | **Object** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- | --- |
| Registries | Party | `hub_party` | one row per business key | `party_bk`: a party identifier assigned by Nexus when a Natural Person or Legal Entity first becomes a party |
| Registries | Natural Person | `hub_natural_person` | one row per business key | `natural_person_bk`: the primary person identifier of the source of record, assigned once and never changed. It is not an identity document |
| Registries | Legal Entity | `hub_legal_entity` | one row per business key | `legal_entity_bk`: the primary identifier of the entity in the source of record, assigned once and never changed. It is a registration or tax number for a formal entity and a registry code for an informal one |
| Platform | Code List | `hub_code_list` | one row per business key | `code_list_bk`: the name of the list, such as `gender`. It is assigned once and never changed |
| Platform | Code List | `hub_code_value` | one row per business key | `code_value_bk`: the list name and the code joined by a colon, such as `gender:female` |
| Platform | Load Configuration | `hub_load_configuration` | one row per business key | `load_configuration_bk`: the jurisdiction and the attribute group joined by a colon, such as `WSM:natural_person__demographics`. The jurisdiction is `any` for the default of every jurisdiction |

## Links

| **Owner domain** | **Object** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- | --- |
| Registries | Natural Person | `lnk_natural_person__party` | one row per distinct combination of natural person and party | `hub_natural_person`, `hub_party` |
| Registries | Legal Entity | `lnk_legal_entity__party` | one row per distinct combination of legal entity and party | `hub_legal_entity`, `hub_party` |
| Registries | Legal Entity | `lnk_legal_entity__natural_person` | one row per distinct combination of legal entity and natural person | `hub_legal_entity`, `hub_natural_person` |
| Platform | Code List | `lnk_code_list__code_value` | one row per distinct combination of code list and code value | `hub_code_list`, `hub_code_value` |

## Non-historized Links

None yet.

## Satellites

| **Owner domain** | **Object** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- | --- |
| Registries | Natural Person | `sat_natural_person__name` | one row per parent key and name type, for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__identification` | one row per parent key and identification document (type and number), for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__registration` | one row per parent key and registration basis, for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__lifecycle` | one row per parent key, for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__demographics_history` | one row per parent key, for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__physical_traits_history` | one row per parent key, for each time its values change | — |
| Registries | Natural Person | `sat_natural_person__community_affiliation_history` | one row per parent key, for each time its values change | — |
| Registries | Legal Entity | `sat_legal_entity__name` | one row per parent key and name type, for each time its values change | — |
| Registries | Legal Entity | `sat_legal_entity__identification` | one row per parent key and identification (type and number), for each time its values change | — |
| Registries | Legal Entity | `sat_legal_entity__classification` | one row per parent key, for each time its values change | — |
| Registries | Legal Entity | `sat_legal_entity__lifecycle` | one row per parent key, for each time its values change | — |
| Registries | Legal Entity | `sat_legal_entity__natural_person__representation` | one row per parent key and role, for each time its values change | — |
| Platform | Code List | `sat_code_value__label` | one row per parent key, for each time its values change | — |
| Platform | Code List | `sat_code_value__applicability` | one row per parent key and jurisdiction, for each time its values change | — |
| Platform | Code List | `sat_code_list__usage` | one row per parent key and column that uses the list, for each time its values change | — |
| Platform | Code List | `sat_code_list__access` | one row per parent key and role, for each time its values change | — |
| Platform | Load Configuration | `sat_load_configuration__mechanism` | one row per parent key, for each time its values change | — |

## Satellites with row versioning

| **Owner domain** | **Object** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- | --- |
| Registries | Natural Person | `sat_natural_person__demographics` | one row per parent key, replaced in place when its values change | — |
| Registries | Natural Person | `sat_natural_person__physical_traits` | one row per parent key, replaced in place when its values change | — |
| Registries | Natural Person | `sat_natural_person__community_affiliation` | one row per parent key, replaced in place when its values change | — |
