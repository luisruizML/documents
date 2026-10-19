# <<Object name>>

## Header

*Who owns the object and where it stands. Owner domain, Shared with and Scope use the fixed lists; Status is Draft, Reviewed or Agreed.*

| **Field** | **Value** |
| --- | --- |
| Object | <<Object name>> |
| Parent object | <<Parent object, or —>> |
| Owner domain | <<Platform, Registries, Taxation Contributions and Licences, Finance, Compliance, Benefits or AEOI>> |
| Shared with | <<Zero or more domains, comma separated, or —>> |
| Scope | <<Domain, Shared or Global>> |
| Status | Draft |
| Version | 0.1 |
| Last updated | <<YYYY-MM-DD>> |

## Definition

*The agreed meaning, in plain language.*

<<Definition>>

## Why it is its own object

*The argument for keeping it separate: the lifecycle, key and owner that differ from its neighbours. State what breaks if it is merged.*

<<Why separate>>

## Vault objects

*One row per vault object. Names follow the naming convention (R9); every grain starts with the "one row per" of its type (R12).*

| **Type** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- |
| Hub | `hub_<<object>>` | one row per business key | `<<object>>_bk`: <<how the key is chosen>> |
| Link | `lnk_<<a>>__<<b>>` | one row per distinct combination of <<a and b>> | `hub_<<a>>`, `hub_<<b>>` |
| Satellite | `sat_<<parent>>__<<descriptor>>` | one row per parent key, for each time its values change | — |

## Fields

*One table per vault object, in the order of the table above. Types come from the allowed list (R11). PII forces its own Satellite (T4). A `_code` column says what its values look like: e.g. three or more values, or One of the closed list.*

*Indicators in Role: ◆ own hash key · ◇ hash key of another object · ● business key · ▪ load metadata · Δ hashdiff. Default: — means no default, so the loader must supply the value; a literal is a default in the sense of Iceberg format version 3.*

### hub_<<object>>

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `<<object>>_hk` | ◆ | `string` | No | No | — | Hash key |
| `<<object>>_bk` | ● | `string` | No | No | — | <<The business key>> |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

## Sources and mapping

*Declare only the endpoints that relate to this object. If none are declared, write exactly: No endpoints declared yet*

No endpoints declared yet

## Jurisdictions map

*Edge cases that need a different approach. A difference is a scenario of the same object, never a new object (R7). Name the countries; they explain the design.*

| **Edge case** | **Where it happens** | **Approach** | **Vault effect** |
| --- | --- | --- | --- |
| <<What differs>> | <<Countries or kinds of jurisdiction>> | <<How the model handles it>> | <<Which vault object carries the difference>> |

## Examples

*At least one realistic scenario, shown as sample rows of the Hub and its Satellites. Mark invented data as illustrative.*

<<Scenario and sample rows>>

## Modeling considerations

*Rules the model must respect, and what breaks if they are ignored.*

- <<Consideration>>

## Diagram

*The cluster, in the brand style.*

*Two pictures, generated from this page with `scripts/build_diagram.py`: the simple one and the full one with the tables.*

![<<Object name>> cluster](<<Object_Name>>.png)

![<<Object name>> cluster, full](<<Object_Name>>_Full.png)

## Open decisions

*Same table as the Principles document. If there are none, write exactly: None open*

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| <<Decision>> | <<Role>> | <<How>> | <<When>> |
