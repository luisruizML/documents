# The Data Layer and Systems of Engagement

*Fourth of five short documents on the data layer for the Public Services Suite (PSS 3.0) — read `Data_Layer_Overview.md` first. It answers one question: how does the data layer help build systems of Engagement? Last in the design sequence: once we know which decisions we serve and what the core must record, Engagement is how that data is obtained — and how people see the results.*

**Part:** 1 — Start here · **Document:** 4 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **The problem it ends**

Today each portal has its own database. The consequences are familiar: the same citizen types the same details into portal after portal; two portals disagree about the same person; a correction made in one never reaches the others. There is no single source of truth because every portal quietly became one.

The vision's answer is direct: **a system of engagement uses configuration files, not a database.**

## **Who Engagement serves**

Not only citizens. On one shared portal shell and design system:

* **Citizens and businesses** — registration, filing and assessment, claims, payment and refund journeys.
* **Public servants** — the case handling screens where backlogs are worked.
* **Institutions** — the reporting entity portal, where banks and other financial institutions submit their AEOI (Automatic Exchange of Information) reports.

## **What makes "configuration, not database" possible**

A portal can only give up its own database if three things are true:

1. **Every journey is described in configuration** — its steps, fields, validations and wording per jurisdiction — rather than coded per country.
2. **Everything a screen shows comes from a service**, not from a local copy.
3. **Everything a screen collects goes to the one place that owns it** — the relevant Record module — never into the portal itself.

The data layer is what makes the second one true, and much of the first one workable.

## **What the data layer gives Engagement**

* **Nothing asked twice.** Forms arrive pre-filled from what the suite already knows across value streams. Firms in small economies spend 100–250 hours a year on tax compliance, against about 40 in advanced economies — much of it re-typing data that already exists somewhere. Every pre-filled field is time handed back.
* **Read models.** A read model is a view prepared in advance for one particular screen — *this taxpayer's open obligations*, *this officer's case queue* — so the screen shows it instantly, without querying the core live and without keeping a copy of its own.
* **Explanations.** How a figure was reached — the inputs and the rule version — shown to the citizen or the officer at the moment they see the figure. It is the same reconstruction described in `Data_Layer_for_Record.md`, delivered *before* anyone has to object.
* **APIs for the systems people already use.** An API (application programming interface) is a defined way for one system to talk to another — and it means engagement does not have to happen in our portals at all. A business's accounting software can file directly; a bank can deliver its AEOI report automatically. That is what the vision means by public services that "flow naturally through the systems people already use."

## **What Engagement gives back**

Every journey produces signals: where people abandon a form, which steps take longest, which pre-filled fields get corrected most often. A pre-filled field that people keep correcting is a data-quality problem in a register — spotted by the people who actually know the truth.

These signals flow to Insight, as platform telemetry and registry data quality. **Engagement is a sensor, not only a display.**

## **The boundary**

A portal may cache and display; it never owns. If a screen needs a fact, it asks for it. If it collects a fact, it hands it to the place that owns it. *One authoritative place per fact, named explicitly* applies to portals first, because portals are where that rule broke.

## **Zero custom development here**

A new country's journeys are configuration over the same shell, the same design system and the same read models. A jurisdiction-specific field is configuration; the pre-fill logic is shared. Onboarding a country is not building a portal.

## **Worked example: a benefit claim from someone already known**

A citizen registered as a taxpayer two years ago and files every year. Now they apply for a child benefit.

1. **Identity.** They sign in once. The data layer already knows their tax record and their civil registry record belong to the same person.
2. **Pre-fill.** Name, address, date of birth and household members come from the civil registry; declared income comes from their tax filings. They confirm rather than type.
3. **Only the unknown is asked** — for example, a child's school enrolment, if no register holds it.
4. **Decision.** The eligibility module asks the data layer to assess the prerequisites, and gets an answer with its reasons.
5. **Explanation.** The result is shown with *why*: the income threshold, the household size, the rule version that applied.
6. **What flows back.** They correct their address. The correction goes to the register that owns addresses — not into the benefits portal — so every other part of the suite sees it at once. And the correction itself is recorded as a quality signal about that register.

Before: they would have filled in everything again, the benefits portal would hold its own copy of their address, and the correction would stay trapped there.

## **Where to go next**

* `Data_Layer_Problems.md` — the full problem list, and the signals that show whether we are fixing them.
* `Data_Layer_for_Record.md` — the decisions and history behind every explanation shown here.
* `Data_Layer_for_Insight.md` — where the signals from Engagement end up.
