# Sample Order

## Header

| **Field** | **Value** |
| --- | --- |
| Object | Sample Order |
| Parent object | — |
| Owner domain | Finance |
| Shared with | Taxation Contributions and Licences |
| Scope | Shared |
| Status | Draft |
| Version | 0.1 |
| Last updated | 2026-10-19 |

## Definition

A sample order is a request, made by a customer, to buy goods at an agreed price.

## Why it is its own object

An order is created and closed on its own schedule, is identified by its own number, and is owned by Finance, so it cannot be an attribute of the customer.

## Vault objects

| **Type** | **Name** | **Grain** | **Business key** |
| --- | --- | --- | --- |
| Hub | `hub_sample_order` | one row per business key | `sample_order_bk`: the order number assigned by the source |
| Link | `lnk_customer__sample_order` | one row per distinct combination of customer and sample order | `hub_customer`, `hub_sample_order` |
| Satellite | `sat_sample_order__pricing` | one row per parent key, for each time its values change | — |
| Non-historized Link | `lnk_sample_order__shipment_event` | one row per occurrence of a shipment event for a sample order | `hub_sample_order`, `hub_shipment_event` |

## Fields

### hub_sample_order

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `sample_order_hk` | ◆ | `string` | No | No | — | Hash key |
| `sample_order_bk` | ● | `string` | No | No | — | The order number |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### lnk_customer__sample_order

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `customer_hk` | ◇ | `string` | No | No | — | Hash key of the customer |
| `sample_order_hk` | ◇ | `string` | No | No | — | Hash key of the order |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

### sat_sample_order__pricing

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `sample_order_hk` | ◇ | `string` | No | No | — | Hash key of the parent |
| `total_amount` | | `decimal(18,2)` | No | No | — | Order total |
| `currency_code` | | `string` | No | No | — | ISO 4217 code, e.g. `WST`, `PGK`, `NZD` |
| `status_code` | | `string` | No | No | — | One of `open`, `paid`, `cancelled` |
| `status_name` | | `string` | No | No | — | The label of the status |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |
| `hashdiff` | Δ | `string` | No | No | — | Hash of the descriptive values |

### lnk_sample_order__shipment_event

| **Column** | **Role** | **Type** | **Null** | **PII** | **Default** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| `sample_order_hk` | ◇ | `string` | No | No | — | Hash key of the order |
| `shipment_event_hk` | ◇ | `string` | No | No | — | Hash key of the event |
| `event_dts` | | `timestamptz` | No | No | — | When the event happened |
| `load_dts` | ▪ | `timestamptz` | No | No | — | When Nexus first loaded the row |
| `record_source` | ▪ | `string` | No | No | — | Which system and endpoint the row came from |

## Sources and mapping

No endpoints declared yet

## Jurisdictions map

| **Edge case** | **Where it happens** | **Approach** | **Vault effect** |
| --- | --- | --- | --- |
| Orders priced in a second currency | Papua New Guinea | Recorded as a scenario of the same order (R7) | A second `currency_code` value in `sat_sample_order__pricing` |

## Examples

An illustrative order placed in Samoa.

| **sample_order_bk** | **total_amount** | **currency_code** |
| --- | --- | --- |
| ORD-0001 | 120.00 | WST |

## Modeling considerations

- An order is never deleted; a cancelled order gets a new Satellite row.

## Diagram

![Sample Order cluster](Diagrams_Sample_Order_Simplified.png)

![Sample Order cluster, full](Diagrams_Sample_Order_Full.png)

## Open decisions

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| Whether a split shipment is one event or several | Data Architecture Engineer | Agreed with Finance | Before the first mapping that needs it |
