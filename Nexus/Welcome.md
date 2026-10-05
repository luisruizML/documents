# **Welcome to Nexus**

**Front page** · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-30

*How to read the Nexus documentation set: what it is, why it runs from the business to the technology, and why the suite has to be seen in two ways at once.*

## **What this is**

Nexus is the data layer of the Public Services Suite (PSS 3.0). These 22 documents explain what it is for, what it commits to, and how it is built — in three parts, plus a glossary. They are written for the whole Product Vision & Design (PVD) unit: product owners, business analysts, UX designers and architects, and for the engineers who build what the architects design.

Every document is a Draft at version 0.1. Version 1.0 is the one the Architecture Review Board approves.

## **Two ways to see the suite: the captain and the team member**

A ship is run by people who see it differently. The captain sees the whole ship — where it is heading, what is in the way, and what one change on deck does to everything else. A team member sees their own station — what they are responsible for, what they receive, and what they hand over. Both views are true. The ship only works when both are held at once.

**The captain's view** is the matrix: three types of system — Engagement, Record, Insight — across seven value streams, heading towards one destination: *any legislation, zero custom development*. The captain's questions are about the whole: which decisions must the suite serve? Which problems matter most, and how big are they? Where does authority for each kind of data lie?

**The team member's view** is the Golden Triad: in one domain, the work of every process is shared between the Front-end, the Backend and Nexus, and every step has exactly one responsible part. The team member's questions are about their station: what do I own? What do I receive, and from whom? What do I hand over, under which contract?

**Why both are needed.** A captain's view with no stations is a strategy nobody can build. Stations with no captain produce parts that each work well and never form one suite — which is exactly how "each portal has its own database" happened. The three parts below move from the first view to the second.

## **Why the set goes from the business to the technology**

The set is read in the same order the suite is designed in: first the decisions that must be served, then what must be recorded, then how it is collected. Applied to the documents themselves:

1. **Part 1 — Start here** answers *why*: what a data layer is, what it does for Insight, Record and Engagement, and which problems — our clients' and our own — it must solve. This is the captain's view.
2. **Part 2 — Principles and mechanisms** answers *what we commit to*: the Data Principles, the mechanisms that carry them out, and how responsibility is split in every domain. This is where the two views meet.
3. **Part 3 — How it is built** answers *how*: the architecture and the tools, one decision per document. This is the team member's view.

Read in that order, every technology choice in Part 3 traces back to a principle in Part 2, and every principle traces back to a problem in Part 1. Read in reverse, the same tools look like preferences — and a tool chosen as a preference is a tool that gets replaced by the next preference. Technology is last because it is the part that should change most easily.

## **How to read it**

| If you are… | Read | About |
| --- | --- | --- |
| **Product owner, business analyst or UX designer** | Part 1, then Data Principles; keep the Glossary open | an hour |
| **Architect** | Everything, in order | about a day |
| **Engineer** | Data Principles, Technical Foundations and Golden Triad, then the Part 3 documents for your station | half a day, then as needed |
| **Architecture Review Board** | Data Principles (including its open decisions), then Technical Foundations | two hours |

Every acronym is expanded the first time it is used in each Part 1 document, and every term is defined in `Glossary.md`.

## **Reading order**

| # | Part | Document | File |
| --- | --- | --- | --- |
| 1 | 1 — Start here | The Data Layer in Blyce 2030 | `Data_Layer_Overview.md` |
| 2 | | The Data Layer and Systems of Insight | `Data_Layer_for_Insight.md` |
| 3 | | The Data Layer and Systems of Record | `Data_Layer_for_Record.md` |
| 4 | | The Data Layer and Systems of Engagement | `Data_Layer_for_Engagement.md` |
| 5 | | The Problems the Data Layer Must Solve | `Data_Layer_Problems.md` |
| 6 | 2 — Principles and mechanisms | Data Principles | `Data_Principles.md` |
| 7 | | Technical Foundations | `Foundations.md` |
| 8 | | Golden Triad Data Boundaries | `Golden_Triad_Data_Boundaries.md` |
| 9 | | Data Scalability Problems | `Data_Scalability_Problems.md` |
| 10 | 3 — How it is built | Hexagonal Architecture | `Hexagonal_Architecture.md` |
| 11 | | Infrastructure as Code | `IaC_Terraform.md` |
| 12 | | Kubernetes | `Kubernetes.md` |
| 13 | | Medallion Architecture | `Medallion_Architecture.md` |
| 14 | | Data Vault 2.0 | `Data_Vault_2.0.md` |
| 15 | | Lakehouse Architecture | `Lakehouse_Architecture.md` |
| 16 | | Apache Iceberg | `Apache_Iceberg.md` |
| 17 | | Broker & Message Services | `Broker_Messages_Services.md` |
| 18 | | ETL & Transformation Tooling | `ELT-ETL_Orchestration_Tooling.md` |
| 19 | | Data-Level Controls | `Data_Level_Controls.md` |
| 20 | | Encryption Key Custody | `Encryption_Key_Custody.md` |
| 21 | | Data Catalog | `Data_Catalog.md` |
| 22 | Glossary | Glossary | `Glossary.md` |

## **Status and feedback**

* **Everything is a Draft.** Technical Foundations, Golden Triad Data Boundaries and Data Scalability Problems are still being rewritten for PSS 3.0.
* **Open decisions** — where authority lies for each kind of data, who owns each value stream's data, and the broader stack — go to the Architecture Retreat on 7–9 October. They are listed in `Data_Principles.md`.
* **Feedback:** comment on the page it concerns. The data architect maintains the set; the Architecture Review Board decides on changes to the principles.
