# Data Scalability Problems at Nexus

*Companion document to* `Golden_Triad_Data_Boundaries.md` *— a direct continuation, not a new topic. That document drew the boundary and gave a four-test decision framework for the grey areas. This document is what happens when the boundary is ignored: six concrete failure patterns, each traced back to which test got skipped, each ending exactly where* `Golden_Triad_Data_Boundaries.md` *already said the answer belonged. Also a companion to* `Data_Principles.md` *O1 (One authoritative place per fact) and P3 (Storage and compute scale independently), and* `Medallion_Architecture.md`*, whose Silver/Gold separation most of these stories exist to justify from the failure side rather than the principle side.*

**Part:** 2 — Principles and mechanisms · **Document:** 9 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

Almost none of the failures in this document are actually about data *volume*. They're about something that needed to evolve — a schema, a rule, a report, a join — getting built inside the one system this whole architecture deliberately keeps rigid. Backend/BackOffice is supposed to hold current, bounded, transactional state (the Golden Triad, Data Principles §2); every story below is what happens when it's asked to also hold flexibility, history, or cross-cutting variation instead — the exact things the four-test framework in `Golden_Triad_Data_Boundaries.md` already routes to Nexus. Six war stories, each with the same shape: **Symptom → which test got ignored → root cause → what Nexus was already built to do instead.**

## **The Core Failure Pattern**

Before the specifics, the pattern that repeats across all six: a real, reasonable requirement shows up — a new jurisdiction, a report someone needs today, a page that needs data from three Dominions — and under deadline pressure, the fastest available fix is applied inside Backend, because Backend is where the code already is. The fix works, once. It doesn't scale, because the requirement it's solving was never a Backend-shaped problem — it was flexibility, history, or cross-Dominion aggregation, all explicitly Nexus's job per `Golden_Triad_Data_Boundaries.md`'s clean split. Each story below ends with the same category of answer: not "add more infrastructure," but "move this to the layer that was already built to hold it."

## **War Story 1: The Wide Table / Nullable Column Sprawl**

**Symptom.** Civil Registry grows from 1 jurisdiction to 12. Each jurisdiction's application form needs 3–8 fields the others don't — a national ID format, a regional benefit code, a locally-mandated consent checkbox. Backend's `applications` table starts at 15 columns; by jurisdiction 12 it's 60+, with any given row populating maybe a third of them.

**Which test got ignored.** Test 3 (volume and schema stability) — this data's schema needs to flex per jurisdiction, which is exactly the signal that it doesn't belong in a small, structurally stable Backend table.

**Root cause.** Jurisdiction-specific validation was treated as a Backend schema problem instead of a governed, per-jurisdiction rule set. Every new jurisdiction means a migration and a Backend deploy — client onboarding speed now depends on Backend's release cycle, which is precisely the coupling `Golden_Triad_Data_Boundaries.md` Grey Area 4 exists to prevent.

**What Nexus was already built to do instead.** Regulatory/reference data (Grey Area 4): rules authored and certified in Nexus as a governed data product, Backend holding only a fast, read-only cache. Onboarding jurisdiction 13 becomes a certified rule-set update, not a code change.

## **War Story 2: The JSON Blob Escape Hatch**

**Symptom.** The team notices Story 1 is unsustainable and adds `extra_fields JSONB` to sidestep further migrations. Six months later, jurisdiction 7's `national_id` key is spelled `nationalId` in some rows and `national_id` in others — two different engineers, two different conventions, nothing caught it at write time. A downstream report silently undercounts because it only queries one spelling.

**Which test got ignored.** Test 3 again, just disguised. "Flexible" and "unvalidated" aren't the same thing, and a JSONB column buys the first by giving up the second.

**Root cause.** The actual problem — schema needs to flex per client — was never solved, just hidden. Backend's "simple and lightweight" store quietly became an unvalidated document store with no schema to enforce consistency, discovered only when a report is already wrong.

**What Nexus was already built to do instead.** The same Grey Area 4 answer as Story 1 — a governed, versioned rule/field set with an actual schema, owned and validated in Nexus, not a JSON column nobody's enforcing.

## **War Story 3: Reporting Queries Against Production**

**Symptom.** A BI analyst needs "citizens with overdue renewals, by region" for a leadership review due end of day. Fastest path: connect straight to Backend's operational Postgres primary and run the join live — millions of rows, no covering index for this ad-hoc shape. The query takes 40 seconds and holds locks; citizen-facing renewal submissions start timing out for the duration.

**Which test got ignored.** Test 2 (cross-Dominion/historical reconstruction) — "by region, this quarter" is an aggregation question, not a single-transaction question, and it was run against the system built exclusively for single-transaction questions.

**Root cause.** Nothing separates analytical load from transactional load, so the two compete for the same connection pool and I/O — and they compound at the worst possible time, because reporting demand and citizen-facing demand both peak during business hours.

**What Nexus was already built to do instead.** This is the whole reason Medallion's Silver/Gold split exists (`Medallion_Architecture.md`): independently-scaled compute for exactly this kind of query, on data that's already been through the pipeline, never competing with Backend's transactional path for the same resources.

## **War Story 4: The Synchronous Cross-Dominion Fan-Out**

**Symptom.** A citizen profile page needs Civil Registry, Tax, and Vehicle Registry data. It's built as Backend calling three internal services live, in the request path. Each has its own ~200ms p99; the page's p99 becomes 600ms+. Then Vehicle Registry ships a bad deploy and its error rate climbs to 5% — the page's overall failure rate becomes roughly 1 − (0.95 × 0.98 × 0.99) ≈ 8%, even for requests that never touched vehicle data.

**Which test got ignored.** Test 2 — joining across Dominions to answer one question is exactly the case that routes to Nexus, not to a live Backend-to-Backend fan-out.

**Root cause.** A "gating" pattern (synchronous, must-succeed-now) was used for what's actually an "informational" read (`Golden_Triad_Data_Boundaries.md` Grey Area 2) — and every additional Dominion Nexus successfully onboards makes this page *less* reliable, by construction, since p99 is bounded by the slowest of N calls and failure probability compounds with every service added.

**What Nexus was already built to do instead.** A pre-joined `Subject 360` Gold view (per `Foundations.md` Annex B.5), read once, cached with an explicit staleness label if needed — one read instead of N synchronous ones, and growing Nexus makes the page *more* capable, not more fragile.

## **War Story 5: Hardcoded Retention/Regulatory Branches**

**Symptom.** Backend's nightly cleanup job has `WHERE created_at < NOW() - INTERVAL '7 years'` hardcoded from the first client's retention rule. Client 4's jurisdiction requires 10-year retention on tax-adjacent records. The job runs silently, successfully, every night for three years — until an external auditor for client 4 requests a year-8 record and it's gone.

**Which test got ignored.** Test 4 (ownership of regulatory logic) — a rule that changes per client, silently, is the exact signature this test exists to catch.

**Root cause.** A regulatory threshold was written as a code constant instead of governed data. Nothing about the failure looks like a bug: no exception, no failed test, no alert — it's discovered by an external auditor, which is a categorically worse discovery path than a CI failure.

**What Nexus was already built to do instead.** Retention and erasure policy governed centrally (`Encryption_Key_Custody.md`, Annex A), versioned and auditable per Annex C.6 certification — the same "own vs. cache" principle as Stories 1 and 2, applied to a rule whose consequence is compliance, not just correctness.

## **War Story 6: Read-Replica Sprawl as a Reporting Band-Aid**

**Symptom.** After Story 3's outage, the fix that looks obvious is "give BI its own read replica." Then compliance wants one for audit queries. Then a data science team wants one for a model. Three replicas later, each lags the primary by a different, load-dependent amount — BI's dashboard and compliance's report show different citizen counts for the same moment, with no way to explain the discrepancy after the fact.

**Which test got ignored.** Test 2, still — this "fix" avoids the outage but never actually answers a cross-Dominion or historical question, because a replica only ever mirrors *current* state.

**Root cause.** The fix treated Story 3 as an availability problem (add more copies of the database) rather than a layering problem (this was never Backend's question to answer). None of the three replicas can say what things looked like last Tuesday, which was never going to be solved by adding more replicas of "now."

**What Nexus was already built to do instead.** Iceberg/Delta time-travel (`Lakehouse_Architecture.md`) — a Silver or Gold table can be queried *as of* any past snapshot, on independently-scaled compute, from one governed source instead of three quietly-diverging copies.

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| Every failure maps to a specific, nameable test | "We violated Test 3" is a diagnosis a team can act on; "our data model doesn't scale" is not |
| The fix is always a redirect, not new infrastructure | Every story's answer already exists elsewhere in this documentation set — Grey Area 4, Medallion's Silver/Gold split, Annex B.5, Annex A, Iceberg time-travel — nothing new had to be invented to resolve any of them |
| Makes the cost of the boundary concrete | `Golden_Triad_Data_Boundaries.md`'s framework is easy to nod along with in the abstract; these six stories are what happens when a team nods along and then ships the shortcut anyway |

## **Honest Trade-Offs**

| Trade-off | The real cost |
| --- | --- |
| The "fast path" genuinely is faster, once | Every story's shortcut works the first time — that's exactly what makes it tempting under deadline pressure, and why the framework has to be applied deliberately, not assumed to be obvious |
| Some of these failures are silent for a long time | Stories 2 and 5 in particular don't throw errors — they're discovered by a wrong report or an external auditor, long after the shortcut shipped, which is a harder failure mode to catch in review than a crash |
| Doing it right costs something upfront | A certified rule set (Stories 1, 2, 5) or a Gold `Subject 360` view (Story 4) takes real design work Nexus has to actually do — the fix isn't free, it's just paid once instead of paid again by every new client or every new Dominion |

## **Diagram**

![Data Scalability Problems: three escalation chains — schema/regulatory shortcuts (wide table to JSON blob to hardcoded regulatory branches), query-load shortcuts (reporting on production to read-replica sprawl), and coupling shortcuts (synchronous cross-Dominion fan-out) — each ending in a real-world failure, all converging on Nexus's Medallion/Data Vault/DLC/Encryption Key Custody mechanisms as the actual fix](Data_Scalability_Problems.png)

*Diagram: three independent escalation chains, three different failure modes, one convergent fix. (Editable source: `Data_Scalability_Problems.drawio`.)*

## **Verdict**

Six different failures, three different escalation chains, and the same root cause every time: a requirement that needed flexibility, history, or cross-Dominion reach got solved inside Backend because that's where the code already was, not because it was ever a Backend-shaped problem. None of the fixes in this document are novel — every one of them is a pointer back to a mechanism this documentation set had already built before these stories were written: `Golden_Triad_Data_Boundaries.md`'s grey-area resolutions, Medallion's Silver/Gold separation, Data Vault's Silver placement, `Subject 360`, Annex A's governed retention policy, Iceberg's time-travel. The four-test framework isn't a checklist to consult after something breaks — these six stories are what it looks like when nobody consulted it before something shipped.
