# Legal: Country Research Notes

## Purpose and how to use it

This is a working document for research, not a page of the Business Objects set, and it is not published to Confluence. It collects, for 23 countries and territories of the Caribbean, Oceania, Africa and the wider Americas, what the three Legal objects must be able to hold: who holds land and by what right, how rights over land and vessels are registered, which activities need a licence, which cards prove a right, and what happens when a card is lost.

The model it tests is on the pages [Legal](../Business_Objects/Legal.md), [Entitlement](../Business_Objects/Entitlement.md), [Credential](../Business_Objects/Credential.md) and [RRR](../Business_Objects/RRR.md). It is meant to be filled in by a researcher and then reviewed with a local expert for each country. The findings feed the open decisions of those pages, in particular the treatment of customary and communal holders.

**Status:** skeleton. Every card below holds only starting hypotheses, each marked *General knowledge, verify*. Nothing in this file has been checked against a source yet.

## Rules for the researcher

1. **Tag every statement.** Use one of these tags at the end of the line:
   - **[Source]**: stated by a document you cite in the Sources field of the card (law, regulation, authority site, report), with the title, issuer, date and link.
   - **[Verify]**: general knowledge or a secondary source that has not been checked against the law or the authority. Say what would confirm it.
   - **[Open]**: not found. Write what you looked for.
2. **Never invent names.** If you cannot find the name of an authority, a register, a law or a form, write *Open*. Do not fill a gap with something plausible.
3. **Prefer primary sources.** The constitution, the land and planning acts, the fisheries and shipping acts, the register's own pages. Date every source and note when the law last changed.
4. **Keep the language neutral.** Describe what exists. Put what it means for the model only in the field *What this changes in the model*.
5. **Do not edit the Business Object pages.** Record proposed changes in the field *What this changes in the model* and in the section *Model impact summary*, and let the author decide.
6. **Mark personal and sensitive material.** Do not record named individuals. Describe the rule, not the case.
7. **A card is done when** every field has at least one tagged statement or an *Open* with what was searched, the sources are listed, and the three or four expert questions are written.

## How a card feeds the model

| **Field in the card** | **Where it lands** |
| --- | --- |
| Land tenure types, holders, registration | [RRR](../Business_Objects/RRR.md): `rrr_type_code`, `rrr_class_code`, the holder, `key_type_code`, `sat_rrr__registration` |
| Derived rights and restrictions | [RRR](../Business_Objects/RRR.md): `lnk_rrr__rrr_hierarchy`, restrictions, the open decision on a bond over part of a parcel |
| Change of use, vessel and activity licensing | [Entitlement](../Business_Objects/Entitlement.md): `entitlement_type_code`, `activity_code`, `sat_entitlement__quota`, the Links to the things |
| Credentials and identity | [Credential](../Business_Objects/Credential.md): `credential_type_code`, `form_code`, `sat_credential__status` |
| Customary groups as holders | The open decisions on [Legal](../Business_Objects/Legal.md) and on [RRR](../Business_Objects/RRR.md); the class `collective` of [Legal Entity](../Business_Objects/Legal_Entity.md) |

## Cross-country matrix

Fill this table last, from the cards, with a few words and the tag in each cell. *Open* means not yet researched.

| **Country or territory** | **Group** | **Customary or communal land** | **Leases from the State** | **Change-of-use permit** | **Vessel licensing** | **Credential for a right** | **Card status** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Antigua and Barbuda | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Anguilla | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Aruba | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Bonaire | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Curaçao | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Dominica | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Grenada | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Saba | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Sint Eustatius | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Sint Maarten | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| St Kitts and Nevis | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| St Vincent and the Grenadines | Caribbean | Open | Open | Open | Open | Open | Skeleton |
| Kiribati | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Marshall Islands | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Palau | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Papua New Guinea | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Samoa | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Vanuatu | Oceania | Open | Open | Open | Open | Open | Skeleton |
| Ghana | Africa | Open | Open | Open | Open | Open | Skeleton |
| Kenya | Africa | Open | Open | Open | Open | Open | Skeleton |
| Greenland | Wider Americas | Open | Open | Open | Open | Open | Skeleton |
| Peru | Wider Americas | Open | Open | Open | Open | Open | Skeleton |
| Suriname | Wider Americas | Open | Open | Open | Open | Open | Skeleton |

## Cases that stress the model

The same ten cases are asked of every country. Add the country to the case when it applies, and note the variant.

| **Case** | **How the Legal pages hold it today** | **What to find out** |
| --- | --- | --- |
| A customary group holds land and there is no title | RRR holder is a Legal Entity classified as collective; key `platform_assigned`; `customary_testimony` | Is a group a legal person by law? If not, how is it named in the register? Who signs for it? |
| State land lent to a community, or leased to a company, and a sublease | Two or three RRRs joined by `lnk_rrr__rrr_hierarchy` | Who can grant a lease over customary land? Does the register show the chain? |
| Family land that passes by inheritance with no new title | RRR with participations by share; evidence by declaration | How many heirs hold at once? How are their shares recorded, if at all? |
| A permit to change the use of a building | Entitlement `change_of_use_permit` for a structure; Gold check of declared use | Is a permit needed? Who grants it? Is the use recorded on the register? |
| A licence to fish or to carry tourists tied to a vessel | Entitlement for an asset; quota with a unit and a period | Is the licence for the vessel, the operator, or both? Is the quota in days, tonnes or fees? |
| A ship registered in an open registry by an owner who lives elsewhere | Asset flag; RRR with an owner of another jurisdiction | Who is the legal owner and how is it shown on the register? |
| A card or certificate is lost or destroyed in a disaster | Credential status; new Credential for the same Entitlement | How is a replacement issued and what proves the right in the meantime? |
| A right is suspended and the holder keeps the card | Entitlement `suspended`; Credential `active`; Gold discrepancy view | Does the authority collect the card? How long can the two disagree? |
| A bond over only part of a parcel (right of way, easement) | Open decision on the RRR page | How is the part described: by text, by sketch, by coordinates? |
| A foreign State or agency holds land | Legal Entity classified as public with its own jurisdiction | How is a foreign holding recorded and what privileges apply? |

## Country cards

Each card has the same fields. The first block is the starting hypothesis, taken from the design discussion and not from a source.

### Caribbean

#### Antigua and Barbuda

**Starting hypotheses**

- A hurricane can destroy physical credentials (the lost-card case in the Credential page). Check how the licensing authority replaces them. *General knowledge, verify.*
- Check whether Barbuda has communal land that is not held in individual title. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Anguilla

**Starting hypotheses**

- British Overseas Territory: check which law governs land registration and whether a separate planning permit is needed to change the use of a building. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Aruba

**Starting hypotheses**

- Constituent country of the Kingdom of the Netherlands: check long leases from the government (a lease of State land for a long term) and how the register records them. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Bonaire

**Starting hypotheses**

- Special municipality of the Netherlands: check which land register and which planning rules apply, and how they differ from Aruba and Curaçao. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Curaçao

**Starting hypotheses**

- Constituent country of the Kingdom of the Netherlands: check long leases from the government and the land register. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Dominica

**Starting hypotheses**

- Check the Carib Territory: land held in common by a community, and how the right of an individual inside it is recorded. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Grenada

**Starting hypotheses**

- Check family land that passes by inheritance without a registered title, and how the register treats it. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Saba

**Starting hypotheses**

- Special municipality of the Netherlands: check the land register and the permit to change the use of a building. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Sint Eustatius

**Starting hypotheses**

- Special municipality of the Netherlands: check the land register and the permit to change the use of a building. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Sint Maarten

**Starting hypotheses**

- Constituent country of the Kingdom of the Netherlands that shares an island with another jurisdiction: check which register and which law apply on each side. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### St Kitts and Nevis

**Starting hypotheses**

- Two islands in one federation: check whether land, planning and vessel registration are federal or island matters. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### St Vincent and the Grenadines

**Starting hypotheses**

- Many small islands: check how a right over land on an outer island is registered and by whom. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

### Oceania

#### Kiribati

**Starting hypotheses**

- Check how land is inherited and registered, and whether fishing access is granted in days or in tonnes, to vessels or to operators. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Marshall Islands

**Starting hypotheses**

- Check customary rights over land held by lineages and their leaders, and the vessel registry that registers ships of owners who live elsewhere (open registry). *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Palau

**Starting hypotheses**

- Check customary land held by clans and traditional leaders, and the way fishing access is granted (days or tonnes, to a vessel or to an operator). *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Papua New Guinea

**Starting hypotheses**

- Check customary land and the legal form that a customary group can take to hold or lease land (a group registered as a legal person), and State leases over customary land. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Samoa

**Starting hypotheses**

- Check customary land governed by titles of chiefs and families, and how a lease over it is recorded. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Vanuatu

**Starting hypotheses**

- Check the rule that land belongs to custom owners, how a lease is granted over it and registered, and the vessel registry that registers ships of owners who live elsewhere (open registry). *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

### Africa

#### Ghana

**Starting hypotheses**

- Check land held by stools, skins and families under customary rules, and how a right over it is registered with the land authority. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Kenya

**Starting hypotheses**

- Check the three kinds of land (public, private, community), how community land is registered, and leases of a fixed term. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

### Wider Americas

#### Greenland

**Starting hypotheses**

- Check whether land can be privately owned or only used by allocation, and who allocates a plot for a house or a business. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Peru

**Starting hypotheses**

- Check the legal status of peasant and native communities that hold land in common, and how the national property register records it. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

#### Suriname

**Starting hypotheses**

- Check the rule that land is State domain, how a right of use is granted, and how the claims of Indigenous and Maroon communities are recorded. *General knowledge, verify.*

| **Field** | **Findings** | **Tag** |
| --- | --- | --- |
| Legal tradition and who makes land and licensing law | *Open.* (Common law, civil law, customary law, or a mix; which body registers land, which body issues licences, which body grants permits.) | Open |
| Land tenure types | *Open.* (State, freehold, leasehold (term and who can grant it), customary, communal, family land. What share of land is each, if known.) | Open |
| Who holds and how a holder is identified | *Open.* (Is a clan, a lineage, a community, a family or a chief a holder by law? Is there a legal form for a customary group? How is the holder named in the register?) | Open |
| Registration and proof | *Open.* (What is registered, who registers it, and what counts as proof when nothing is registered (testimony, survey, declaration).) | Open |
| Derived rights and restrictions | *Open.* (Lease from State land or customary land, sublease, mortgage, easement, planning restriction, embargo over a vessel.) | Open |
| Change of use of a building or a parcel | *Open.* (Is a permit needed to change use (for example storage to housing)? Who grants it? Does it have a number, a term, a card or certificate?) | Open |
| Vessel and activity licensing | *Open.* (Fishing, tourism, passenger transport: is the licence tied to the vessel, to the operator or both? Is access a quota, days at sea or a fee? Is there a regional scheme?) | Open |
| Credentials and identity | *Open.* (Which cards and certificates prove a right. What happens when they are lost or destroyed. Residence status and what proves it.) | Open |
| What this changes in the model | *Open.* (A case the Legal pages cannot hold today, or a value the Code List must support. Name the object and the column.) | Open |
| Questions for a local expert | *Open.* (Three or four questions that only a person who works with the register or the authority can answer.) | Open |
| Sources | *Open.* (Law, regulation, authority website, report. Title, issuer, date, link.) | Open |

## Model impact summary

*Filled in by the researcher after the cards. One row for each change the cards suggest, with the countries that need it. The author decides what enters the model.*

| **Suggested change** | **Object and column** | **Countries** | **Evidence** | **Decision** |
| --- | --- | --- | --- | --- |
| Open | Open | Open | Open | Open |

## Question bank for local experts

Questions grouped by theme. Pick the ones that fit the country and add the country-specific questions to its card.

**Land and holders**

- Which kinds of land exist by law, and what share is each?
- Who may hold land: persons, companies, groups, the State, a chief on behalf of a group?
- Is there a register of customary land, and what does it contain?
- What happens to a right when the holder dies and nothing is registered?

**Rights over land**

- Who can grant a lease, and for how long? Can a lease be mortgaged or sublet?
- What are the common easements and rights of way, and how are they recorded?
- Which restrictions are placed by planning, environment or heritage law, and who records them?

**Activities and licences**

- Which activities need a licence: driving, fishing, tourism, building, trading?
- Is a licence tied to a person, a company, a vessel or a building?
- Which authority grants each, and how is a refusal, a suspension or a renewal recorded?

**Proof**

- What does the holder receive: a card, a certificate, a digital record?
- How is a lost, stolen or destroyed credential replaced?
- Can the right be shown without the credential?

**Data and access**

- Is the register digital, and who can read it?
- Which of this is personal data under local law, and who may see it?

## Open decisions this research feeds

| **Decision** | **Page** | **What the research should settle** |
| --- | --- | --- |
| How collective holders (a tribe, a clan, a family, a community) are classified when the law does not treat them as a legal person | [Legal](../Business_Objects/Legal.md), [RRR](../Business_Objects/RRR.md) | Whether the class `collective` of Legal Entity is enough, or a third kind of Party is needed |
| How a bond over only part of a parcel is joined to the place it covers | [RRR](../Business_Objects/RRR.md) | Which descriptions the registers use: text, sketch, coordinates |
| Which RRR types are ownership, and which are rights over another's property | [RRR](../Business_Objects/RRR.md), [Code List](../Business_Objects/Code_List.md) | The list of types by country |
| Whether a credential that proves who someone is, and not a right, is a Credential | [Credential](../Business_Objects/Credential.md) | How identity cards and residence permits are issued and what they prove |
| Where the amount of a quota used is calculated | [Entitlement](../Business_Objects/Entitlement.md) | Which authority counts catches or days, and when |
