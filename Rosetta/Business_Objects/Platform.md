# Platform

*The place in Business Objects for what the platform itself owns and every domain uses: configuration and other cross-domain objects. A Platform object is not a Party and does not belong to one domain's registry.*

**Section:** Business Objects · **Owner domain:** Platform · **Version:** 0.1 · **Status:** Draft

## What belongs here

An object belongs to Platform when it meets all three tests:

- **Every domain reads it.** It is not specific to taxation, benefits, finance or any other domain.
- **It changes how data is read or loaded, not what a business fact means.** For example, which values a column accepts, or which mechanism a jurisdiction uses to keep or not keep history.
- **Platform decides it.** A domain can ask for a change; Platform owns the answer.

Platform objects follow the same page format as every other business object (see the [Business Objects index](Index.md)).

## Platform objects

| **Object** | **What it holds** | **Status** | **Page** |
| --- | --- | --- | --- |
| Code List | The allowed values of a column, with labels, jurisdictions, validity periods, where each list is used and who may read it | Draft | [Code List](Code_List.md) |
| Load Configuration | For each jurisdiction and attribute group, which Satellite of a twin pair is loaded: the one with history (the default) or the one updated in place | Draft | [Load Configuration](Load_Configuration.md) |

## Planned

| **Object** | **What it will hold** | **Where it comes from** |
| --- | --- | --- |
| Government Authority | The public bodies that issue credentials and attest records. It is not a Party | Open decision on [Natural Person](Natural_Person.md) |

## Rules for Platform objects

- **One generic object beats one table per need.** A new need adds rows, not tables. [Code List](Code_List.md) is the model for this.
- **Reference to where it is used.** Every configuration records the exact object and column it applies to, so a search from either side finds the other.
- **Access is part of the object.** What each role may read is recorded on the object, and the platform's role-based access control applies it.
- **Nothing is deleted.** A value or a setting that no longer applies is retired, because records loaded earlier still depend on it (R1).

## Open decisions

| **Decision** | **Owner** | **How it is decided** | **Decide by** |
| --- | --- | --- | --- |
| Where the roles used for access come from | Platform | Decided with the role-based access control design of the platform | Before the first list with restricted values |
