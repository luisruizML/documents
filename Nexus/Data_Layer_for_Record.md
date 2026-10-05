# The Data Layer and Systems of Record

*Third of five short documents on the data layer for the Public Services Suite (PSS 3.0) — read `Data_Layer_Overview.md` first. It answers one question: how does the data layer help build systems of Record? Second in the design sequence, after Insight has established which decisions we need to serve.*

**Part:** 1 — Start here · **Document:** 3 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **The core is an abstraction**

"The core" is not one system doing everything behind the counter. It is an abstraction: the place where a decision is **owned and recorded** — who owes what, who is eligible, what the ledger shows, when enforcement starts. How that decision is *reached* is a separate question, and much of the work behind it is data work.

**The data layer does not belong to Record alone.** It provides analytic services to Engagement, Record and Insight alike — this document covers what it does for Record. Record is made of the modules that own decisions: registers, rules engine, assessment, eligibility, ledger, enforcement. A module asks; the data layer does the heavy lifting and answers. *Is this applicant already registered under another number? Do they meet the prerequisites for this benefit? Is this filing consistent with everything else we know?* The module records the outcome and stays accountable for it — without having to hold every jurisdiction's variation, every historical obligation and every model inside itself. A core in which every module tries to hold all of that becomes the heavily customised, expensive-to-change system the suite exists to replace.

## **What the core is responsible for**

Across the seven value streams, Record covers: the rules engine, configuration and identity · the registers themselves · assessment and crediting · eligibility and disbursement · sub-ledger, ledger and reconciliation · enforcement and objections · validation and delivery for international exchange.

Read these as **responsibilities, not as the places where all the logic must live**. Responsibility for an eligibility decision sits with the eligibility module; the matching, scoring and checking that inform it are services the data layer provides, behind a clear contract.

## **What the data layer does for Record**

* **Duplicate resolution.** Duplicated taxpayer identification numbers (TINs) and mismatched birth, death and migration records are the normal condition, not an anomaly. Deciding whether two records are the same person takes a view across registers that no single register has.
* **Assessing prerequisites for go / no-go decisions.** Before a claim is approved, a refund released or a registration accepted, its prerequisites must be checked. Rules settle the clear-cut cases; advanced machine-learning (ML) models assess the rest — the likelihood of error, of fraud, of an incomplete file — and return an answer **with its reasons and its confidence**.
* **Consistency across value streams.** A filing checked against registry, customs and payment data, not only against itself.

One boundary does not move: for consequential decisions, **human accountability stays central**. A model can recommend go or no-go; low-confidence and high-impact cases go to a person, and the core records who decided and on what basis.

## **What the data layer holds for Record**

| What it holds | Why it lives in the data layer, not in each module |
| --- | --- |
| **History** — every prior value, and when it changed | A register answers *what is true now*. Keeping every previous version, with dates, is a different job — and it is what objections, audits and policy evaluation all depend on. |
| **Data quality, made visible** | "Registry data quality" sits in the Insight row — the data layer measuring the registers. No register credibly grades its own homework. |
| **The event record, and the contracts between modules** | See *Events, contracts, and the Modulith* below. |
| **Custody of personal data** | Spread across module databases wherever it was convenient to put it, personal data makes erasure and retention promises we cannot keep. Concentrated custody makes them mechanical. |

## **Data products it serves**

The same capabilities are offered as products, not one-off integrations:

* **APIs** (application programming interfaces) — defined, versioned ways for any module or portal to ask for data or for a decision input, instead of reaching into another system's tables.
* **ML models** — trained, versioned and monitored in one place, so the same eligibility or risk model serves every country through configuration rather than being rebuilt per client.
* **AI infrastructure** — the shared foundation for running models responsibly: hosting, the data they learn from, evaluation, and a record of what each model saw and recommended — so AI is used across the suite instead of bolted into individual screens.

## **Events, contracts, and the Modulith**

The core architecture is moving from monolith (1.0), through microservices (2.0), to a **Modulith** (3.0) — one deployable system divided internally into modules with clear, business-driven boundaries and explicit contracts between them.

Boundaries and contracts are data questions before they are code questions: a contract states what data one module gives another, in what shape, with what guarantees. **Domain events** — *an assessment was issued*, *a claim was approved* — let each module react to what happened elsewhere without being wired into it. The data layer carries and keeps those events, which keeps modules decoupled, feeds the Insight row, and gives the promise that a chain of events actually completed somewhere to be observed — a known gap today, since we have logs but not end-to-end tracing across systems.

## **The rule that prevents ambiguity**

The data layer's role varies with the kind of data, and exactly where the line falls is a decision for the Architecture Retreat. What holds regardless:

**For any given piece of data there is exactly one authoritative place, it is named explicitly, and it is never left ambiguous.**

For decisions this means two things are always recorded: the decision itself, in exactly one place, and **the inputs it was based on** — including any score the data layer computed and the version of the model that produced it. Two systems both believing they own the same fact is "each portal has its own database" reappearing one level down.

## **Zero custom development here**

This is where the constraint bites hardest. Rates, thresholds, exemptions, eligibility bands — and the models and checks that assess prerequisites — are **configured, not coded**. Each rule carries the dates it applies between, so it is never simply overwritten: the old version stays queryable. A budget-cycle rate change becomes a data change, with no release and no per-country branch in the codebase.

The stakes are documented. Administrations without configurable rules find legal updates slow and error-prone, and during COVID-19 emerging-economy tax systems needed *hundreds* of temporary measures within months. A suite that needs a deployment per measure cannot serve that.

## **Worked example: an objection to a two-year-old assessment**

A citizen disputes an assessment issued two years ago. To handle it fairly, the administration must answer four questions:

1. **What did we know then?** The register values as they stood on the assessment date — not today's.
2. **Which rule version applied?** The rates and thresholds in force that day.
3. **What informed the decision?** The inputs, the rule version, any model score and the model version that produced it — reproducible on demand.
4. **What has changed since, and why?** An address correction, a resolved duplicate, a re-graded register entry.

None of these are answerable from a system that stores only current state. All are routine if history, rule versions and decision inputs were kept from the start.

The payoff is that the administration can **show its working** — the direct answer to the fourth problem on our list: trust is fragile when citizens cannot see how their obligations were calculated or how their data was used. A decision that can be reconstructed line by line, including what a model contributed, is a different conversation from one that cannot.

## **Where to go next**

* `Data_Layer_for_Engagement.md` — how this data reaches people, and what comes back.
* `Data_Layer_Problems.md` — the full problem list, and the signals that show whether we are fixing them.
* `Data_Layer_for_Insight.md` — the decisions all of this exists to serve.
