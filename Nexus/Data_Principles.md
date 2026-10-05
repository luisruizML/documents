# **Data Principles**

**Part:** 2 — Principles and mechanisms · **Document:** 6 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

*The data principles for the Public Services Suite (PSS 3.0) — the "data first approach and data principles" the Blyce 2030 plan asks the data architect to lead. Written for the whole Product Vision & Design unit and for the Architecture Review Board, which adopts and enforces it. How each principle is carried out and checked is set out in its companion, Technical Foundations (`Foundations.md`). New to the set? Start with* `Welcome.md`*; terms are defined in* `Glossary.md`*.*

## **1. Purpose**

These principles bind anyone who designs part of the suite — a journey, a register, a rule, a report, a model. They exist so that one configurable suite can serve any legislation without custom development, and so that the data it holds can be trusted by the people it is about.

A principle here is a commitment, not a preference. Where a design breaks one, the break is made explicitly and recorded — never by default.

## **2. The frame**

The suite is seen in two ways — as the captain sees the whole ship, and as a team member sees their own station. Both describe the same system; `Welcome.md` explains why both are needed.

**The captain's view — three types of system across seven value streams.** Engagement is what people touch, Record is what decides and keeps, Insight is what we learn. They are *technically independent but functionally belong together*.

![The PSS 3.0 matrix: Engagement, Record and Insight across the seven value streams, with the data layer beneath all three](Data_Layer_Matrix.png)

*Diagram: the three system types across the seven value streams, with Nexus beneath them. (Editable source: `Data_Layer_Matrix.drawio`.)*

**The team member's view — the Golden Triad.** In every domain, the work of a process is shared between three parts:

| Part | Corresponds to | Responsible for |
| --- | --- | --- |
| **Front-end** | Engagement | Collecting, displaying and explaining — never owning data |
| **Backend** | Record | Deciding and recording: rules, registers, assessments, ledgers, enforcement |
| **Nexus** | the data layer | History, the integrated view, resolved identity, custody of personal data, events — and analytic services to all three |

Not every process needs all three. Every step of every process has exactly one responsible part. `Golden_Triad_Data_Boundaries.md` shows how that is worked out domain by domain.

**Nexus is the name of the data layer.** It provides analytic services to Engagement, Record and Insight alike — APIs, machine-learning models, AI infrastructure — and is the bond between them.

## **3. The principles**

### **Design**

| # | Principle | Why |
| --- | --- | --- |
| D1 | **Design insight-first.** Decide which decisions must be served, then what the core must record, then how engagement collects it. | Data the core never recorded can never be reported later. |
| D2 | **Configuration over code.** Rules, rates, fields, journeys and reports are configuration. | Any legislation, zero custom development: a new country is an onboarding, not a project. |
| D3 | **Think in objects, relationships and enrichment** — Hubs, Links and Satellites, in Data Vault 2.0 terms. | A new requirement adds enrichment instead of changing what already exists. |
| D4 | **The right tool for the right job.** A shared basic stack everyone knows, broadened deliberately. | No single tool can do every job well. |

### **Ownership**

| # | Principle | Why |
| --- | --- | --- |
| O1 | **One authoritative place per fact, named explicitly.** | Two owners of one fact is "every portal has its own database" again. |
| O2 | **One responsible part of the triad per process step.** Others may take part; responsibility is never shared or implied. | Unclear responsibility is where data problems start. |
| O3 | **Every value stream's data has a named owner.** | Ownership that belongs to everyone belongs to no one. |
| O4 | **Modules have explicit contracts and communicate through events.** | Modules stay independent, and every chain of events can be followed end to end. |

### **Trust**

| # | Principle | Why |
| --- | --- | --- |
| T1 | **History is never overwritten.** | Objections, audits and policy evaluation all depend on what was true *then*. |
| T2 | **Every consequential figure can be explained.** Decision inputs are recorded with the decision, including any model score and model version. | Trust is fragile when people cannot see how their obligations were calculated. |
| T3 | **Humans stay accountable for consequential decisions.** Models recommend; low-confidence and high-impact cases go to a person. | Automation removes busy work; it does not remove accountability. |
| T4 | **Personal data is kept safely, not conveniently.** Its custody is concentrated. | Erasure and retention can only be enforced where custody is known. |
| T5 | **Identity is resolved, never forcibly merged.** | Registers keep their own records, and a wrong match can be undone. |

### **Quality and evidence**

| # | Principle | Why |
| --- | --- | --- |
| Q1 | **Nothing is asked twice.** What one institution knows, the next form shows. | Citizens lose time they cannot afford to lose. |
| Q2 | **Quality is a precondition, not a clean-up.** Data that fails its checks is not used beyond its owner. | Bad data spreads faster than it can be corrected. |
| Q3 | **Register, measure, improve.** Size and importance are measured separately; every fix is measured again. | Not every problem is big, and not every problem is important. |
| Q4 | **Baseline at onboarding.** | Without a starting point we can show the suite was installed, never that it helped. |

### **Language and openness**

| # | Principle | Why |
| --- | --- | --- |
| L1 | **English is the language of the model** — names, rules, code and documentation. Every other language is a translation layer, held as configuration. | One model, many countries, no translation built into the design. |
| L2 | **Open formats; no vendor dependency.** | The data, the definitions and the history belong to the administration, whoever builds the next tool. |

### **Platform**

| # | Principle | Why |
| --- | --- | --- |
| P1 | **Deploy anywhere.** The suite runs on-premise and in the cloud; nothing assumes one provider. | Clients choose where their data lives, within their own infrastructure and legal limits. |
| P2 | **Everything as code.** Infrastructure is provisioned and changed through code, never by hand. | Every deployment is reproducible, reviewed and repeatable for the next client. |
| P3 | **Storage and compute scale independently.** | Heavy analysis never slows down the services people are using. |
| P4 | **Business logic is isolated from technology.** Contracts in the core, adapters at the edge; everything is exposed through versioned APIs. | A database, a cloud or a tool can change without rewriting what the suite does. |
| P5 | **Safe to evolve, safe to remove.** Any component can be replaced without threatening the rest. | A product that is safe to change is a product that can keep improving. |
| P6 | **Ready for AI.** Data is documented, labelled and traceable, so models and agents can use it safely. | AI built on undocumented, fragmented data cannot be trusted. |

## **4. Open decisions**

These are deliberately not settled here. They go to the Architecture Retreat (7–9 October):

* **Where authority lies for each kind of data.** The data layer can be primary custodian (personal data), sole holder (history, the integrated view, resolved identity), or derived from a Record module. Which applies where depends on how simple the core can stay, where personal data physically lives, and whether the event record is itself authoritative.
* **Value-stream owners.** Who owns each value stream's data (O3), and how today's Dominions map onto the seven value streams.
* **The broader stack.** Which tools make up the shared basic stack (D4) — a recommendation for the Technology Advisory Board.

## **5. Governance**

* **Author and maintainer:** the data architect.
* **Adoption and enforcement:** the Architecture Review Board.
* **Amendments** may be proposed by anyone; the Board decides. Every change is versioned and recorded in the Technical Foundations changelog.
* **Versions:** this document and Technical Foundations are versioned together. Everything stays at 0.x while in draft; **1.0 is the version the Board approves.**
## **6. Where to go next**

* `Foundations.md` — how each principle is carried out and checked.
* `Golden_Triad_Data_Boundaries.md` — how responsibility is split, domain by domain.
* `Glossary.md` — every term used across the set.
