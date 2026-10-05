# The Problems the Data Layer Must Solve — and How We Detect Them

*Fifth of five short documents on the data layer for the Public Services Suite (PSS 3.0) — read `Data_Layer_Overview.md` first. It answers two questions: what problems must the data layer solve, and how will we know whether it is solving them? Problems are seen from two sides — our clients' and our own — and always at the top level, never through a single domain.*

**Part:** 1 — Start here · **Document:** 5 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **How to read this document**

* **Two perspectives.** Our clients have problems the suite exists to solve. We have problems of our own that decide whether we can build it. Both are real, and they are kept apart so neither hides the other.
* **Top level only.** A problem stated in terms of one domain — tax, benefits, licences — is a symptom. The problems below hold in every domain; domain evidence only illustrates them.
* **Size and importance are measured, not assumed.** Not every problem is big, and not every problem is important. The last section explains how we decide.

## **Part 1 — Our clients' problems**

These come from the suite's own foundations. Each holds across every domain, and each has a data dimension and a signal that shows whether we are making it smaller.

| The problem | Where the data layer comes in | How we detect it |
| --- | --- | --- |
| **Citizens lose time they can't afford to lose** — repeated information requests, queues, fragmented services, complex forms. | Nothing asked twice: what one institution already knows, the next form already shows. | Fields asked per journey; share pre-filled; time to complete; how often the same fact is requested again. |
| **Institutions operate with inefficiencies that drain capacity and morale** — manual work, low visibility of workload, large backlogs. | Workload views ready for every officer; routine checks done as services, not by hand. | Backlog size and age; share of cases completed without manual handling; time per case. |
| **Data is an untapped asset and a barrier instead of an enabler** — siloed systems, inconsistent standards, data that cannot move. | One integrated view, shared definitions, and APIs (application programming interfaces) through which data moves securely. | External sources connected versus needed; time to connect a new one; duplicate-identity rate; records failing validation. |
| **Trust between citizens and institutions is fragile** — opaque processes, poor traceability of decisions. | Every consequential figure explained; every decision reconstructable, including what a model contributed. | Share of decisions that can be fully reconstructed; objection rate; share of objections upheld. |

**The causes behind them repeat in every domain.** Fragmented registers and duplicated identities. Poor data quality. Rules that cannot change as fast as the law does. Legacy systems with no APIs and no data standards. Many external institutions that must be connected before one complete view exists. Decisions made after the fact rather than ahead of it. For example, the tax domain documents these with hard evidence — 15+ external entities for one complete taxpayer view, poor registers raising enforcement costs by 20–40%, hundreds of temporary measures during COVID-19 — and the same patterns appear in benefits, licences and registries.

## **Part 2 — Our own problems**

The suite's foundations name one internal problem directly: *being historically project-oriented has led to architectural fragmentation, duplicated efforts, and teams aligned to clients rather than outcomes.* Underneath it sit six more specific ones.

1. **The tool that made us successful now limits us.** We build on a low-code platform. It brought us our success, but new features are increasingly hard — sometimes nearly impossible — to deliver with it.
2. **We want to be data-driven, but our skills are single-tool.** Teams know one way of working, and the current stack cannot host a modern data layer.
3. **We think in relational tables.** Every design question starts as *which table, which column*. That makes change expensive: a new country's requirement becomes a new column and a migration. We need to think instead in three things:
   * **Objects** — the things that exist: a citizen, a business, a vehicle *(Hubs)*.
   * **Relationships** between them — this citizen owns this vehicle *(Links)*.
   * **Enrichment** — what we learn about them over time: an address, an income, a status *(Satellites)*.

   The terms in brackets come from Data Vault 2.0, a modelling method that matches this way of thinking well. Its advantage is that a new requirement usually adds enrichment instead of changing what exists.
4. **Our stack is too narrow.** One tool cannot do every job. We need a broader stack — the right tool for the right job — and a shared, basic set of tools everyone knows.
5. **We lack a common language.** **English is the one language of the model**: the names of objects, relationships, fields and rules, the code and the documentation. Every language a client needs is a translation layer on top, handled as configuration.
6. **We do not yet measure our own problems.** Which is why the next section exists.

| Internal problem | How we detect it |
| --- | --- |
| The tool limits us | Features requested but not deliverable on the current platform; effort per feature over time. |
| Custom development per client | **Share of changes that required code rather than configuration** — the zero-custom-development metric. |
| Single-tool skills | Share of each team able to work on the broader stack. |
| Relational thinking | Share of new data models expressed as objects, relationships and enrichment. |
| No common language | Share of models, code and documentation in English; translations held as configuration. |

## **Part 3 — Register, measure, improve**

Not every problem is big. Not every problem is important. Treating all of them as urgent is how effort is wasted — so every problem goes through three steps:

1. **Register it.** Write it down: what happens, who is affected, and whether it is a client or an internal problem.
2. **Measure it** on two separate scales:
   * **Size** — how often, how many people, how much time or money.
   * **Importance** — what it costs in trust, in revenue, in legal exposure, in people's lives.
3. **Improve it — then measure again.** A fix that is not re-measured is an assumption.

Size and importance together set the priority:

| | **Important** | **Not important** |
| --- | --- | --- |
| **Big** | Act now. | Automate, or consciously accept. |
| **Small** | Fix deliberately — a small problem with legal or trust consequences still matters. | Register it and leave it. |

This is also where detection lives. Two cells of the Insight row — *platform telemetry* and *registry data quality* — exist to watch the suite itself. The data layer gives Blyce the same analytic services it gives our clients, and every client needs a baseline at onboarding: without one, we can show the suite was installed, never that it helped.

## **What we do not yet know**

* **Which signals can be measured today** in the current products. Probably few — which is itself a finding.
* **Baselines**, for our clients and for ourselves.
* **Owners and targets.** This document names signals, not targets; targets need owners, and owners are not yet assigned.

## **Where to go next**

* `Data_Layer_Overview.md` — what the data layer is, and the bond it forms between Engagement, Record and Insight.
* `Data_Layer_for_Insight.md`, `Data_Layer_for_Record.md`, `Data_Layer_for_Engagement.md` — what it does for each.
