# The Data Layer and Systems of Insight

*Second of five short documents on the data layer for the Public Services Suite (PSS 3.0) — read `Data_Layer_Overview.md` first. It answers one question: how does the data layer help build systems of Insight? It comes before the documents on Record and Engagement because that is the order we design in.*

**Part:** 1 — Start here · **Document:** 2 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Why this one comes first**

The design sequence starts here:

1. **Which data-driven decisions are to be made?**
2. What data must be recorded in the core?
3. Through what engagement will this data be obtained?

Insight is not the last thing we build. It is the first thing we decide, because it determines what the other two have to do. A system of insight nobody specified up front cannot be retrofitted — it can only be approximated from whatever the screens happened to collect.

## **What the Insight row actually contains**

Across the seven value streams:

* **platform telemetry** — is the suite itself healthy, and how is it actually being used
* **registry data quality** — can the registers be trusted
* **tax reporting and analytics**, **benefits reporting**, **revenue reporting**
* **risk rating and case selection** — who to look at, and why
* **AEOI analytics and reporting** — what we owe partner jurisdictions under the Automatic Exchange of Information standard (AEOI), and the proof it is right

These are product capabilities, not per-country reports. That distinction is the whole game.

## **The decisions being served**

Insight is only worth building if it changes a decision someone actually makes. The real ones:

* Which taxpayers should we audit this quarter — and why those?
* Which arrears are worth pursuing first?
* Can we trust this register enough to act on it?
* What did last year's rate change actually do?
* What must we report to partner jurisdictions, and can we prove it?

Every one is an **evidence** question. Today they are largely answered by judgement and habit, because the evidence is not assembled anywhere. That is problem 3 on our own list — *data is an untapped asset and a barrier instead of an enabler* — stated operationally: decisions stay reactive.

## **What the data layer supplies**

Five things, none of which exist inside any single system on its own:

| What it supplies | Why it matters |
| --- | --- |
| **One integrated view across value streams** | Audit selection that sees only tax data is selecting on a fraction of what is knowable. The signal usually lives in the combination — registry, customs, benefits, payments. |
| **History** | You cannot evaluate a policy change without a trustworthy before and after. |
| **Resolved identity** | A taxpayer, a benefits claimant and a property owner may be one person across three registers. Until that is resolved, every count is wrong. |
| **Definitions that hold** | One definition of "arrears", one of "active taxpayer". Two teams reporting different numbers for the same quarter is not a reporting problem — it is a definition problem. |
| **Provenance** | Every figure traceable back to where it came from. Without it, "data as a trusted asset" is a slogan. |

## **Why Insight cannot be bolted on later**

This is the most expensive lesson in the sequence, so it is worth being blunt:

**No report can recover data the core never wrote down.**

If assessment status is stored as a current value with no record of *when* each change happened, then *how long does an assessment actually take* is unanswerable — not difficult, unanswerable — and stays that way until the core is changed and another year of data accumulates. The same applies to why a case was selected, which rule version produced a figure, and what a register held before it was corrected.

Deciding the questions first is what prevents this. It costs a conversation up front, and it is unrecoverable if skipped.

## **Zero custom development here**

"Any legislation, zero custom development" applies to reporting as hard as to anything else.

A report built for one country's tax code is a custom development, and it will be rebuilt for the next country. A report defined as **configuration over a shared model** is a product capability: the model is the same everywhere, the configuration differs. Concretely, the difference between —

* *this country needs a new arrears report* → a build, a release, a test cycle; and
* *this country's arrears thresholds and bands differ* → configuration, live the same day.

It also means policy insight does not depend on a vendor. The definitions, the history and the data belong to us and the administration, in open formats, whoever builds the next reporting tool.

## **Worked example: who gets audited**

Today, in many administrations, **70–90% of audits are desk audits**, and they change long-term behaviour very little. Selection draws mostly on what the tax system already holds, so it finds only what tax data alone can reveal. Meanwhile poor register quality raises enforcement costs by **20–40%**, and a complete view of one taxpayer can require **15+ external sources**.

With the data layer in place, case selection changes shape:

1. **Identity is resolved first**, so one taxpayer is one taxpayer across registers, customs declarations and benefit claims.
2. **Selection runs on the integrated view**, not the tax record alone — mismatches between declared income and observable activity become visible.
3. **Every selection carries its reason** and the data that triggered it, so an officer can see why a case surfaced and a citizen can be told.
4. **Outcomes feed back** — which selections produced adjustments, which wasted effort — so next quarter's selection is measurably better than this quarter's.

Point 3 matters as much as point 1. A risk score nobody can explain fails the trust test, and fragile trust is one of the five problems the suite exists to solve — not a nice-to-have.

## **Where to go next**

* `Data_Layer_for_Record.md` — what the core must keep for any of this to be possible.
* `Data_Layer_for_Engagement.md` — how data reaches people, and how engagement feeds insight back.
* `Data_Layer_Problems.md` — the full problem list, and the signals that tell us whether we are fixing them.
