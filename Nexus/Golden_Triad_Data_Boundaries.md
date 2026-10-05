# Golden Triad Data Boundaries at Nexus

*Companion document to* `Data_Principles.md` *§2 (The frame — the Golden Triad) and O2 (One responsible part of the triad per process step). The Golden Triad states the boundary in one line: Backend/BackOffice is "dedicated exclusively to secure, high-speed operational transactions, keeping its data model as simple and lightweight as possible," while Nexus "handles all the data heavy lifting." This document expands on what concretely belongs in each — and, more importantly, how to resolve the cases that don't fall cleanly on either side.*

**Part:** 2 — Principles and mechanisms · **Document:** 8 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

The Golden Triad's one-line boundary is a clean division of labor at the level of a principle, but it doesn't say what data concretely lives in Backend's own databases versus what Nexus owns, and it says nothing about the recurring grey areas every engineer building against this boundary eventually hits — a CDC staging table, a UI badge that needs a live count, a file upload mid-transaction, a validation rule that changes per jurisdiction. This document draws the clean boundary, gives a four-test decision framework for the cases that don't sort cleanly, and works through five grey areas that come up in practice, each resolved with a concrete example.

## **The Clean Split**

| Lives in Backend/BackOffice | Lives in Nexus |
| --- | --- |
| Current transactional state needed to answer a user-facing request *right now* — the row a form reads and writes | Everything historical — every prior value a field has ever held, not only the current one |
| Data touched inside a single ACID transaction (e.g., "reject this transfer if the balance is insufficient") | Data that requires joining across Dominions to answer |
| Session state, auth tokens, feature flags, in-flight workflow status | Identity resolution, survivorship, anything needing a `Subject 360` view (`Foundations.md`, Annex B) |
| Small, bounded, schema-stable operational tables | Anything whose volume grows with history, or whose schema needs to flex per Dominion, client, or regulation |
| Data needing sub-100ms p99 synchronous reads | Batch, streaming, ML, compliance, and audit — the "heavy processing" the Golden Triad assigns to Nexus |

This split is clean precisely because it restates a boundary the rest of this documentation set already committed to — `Medallion_Architecture.md`, `Data_Vault_2.0.md`, and `Data_Level_Controls.md` all describe Nexus's side of it in detail. None of them say how to resolve the cases that don't sort cleanly into either column — that's the rest of this document.

## **The Decision Framework**

Four tests, applied in order, to anything that doesn't obviously belong to one side:

1. **Transactional consistency.** Does this need to be correct inside the *same* ACID transaction as a write Backend is already doing? If yes, it has to live where that transaction runs — Backend.
2. **Cross-Dominion or historical reconstruction.** Does answering the question require joining across Dominions, or reconstructing a point in time rather than "now"? If yes, it's Nexus's — no amount of caching moves that job to Backend.
3. **Volume and schema stability.** Does this stay small and structurally stable, or does it grow with total history, or need to flex per Dominion, client, or regulation? Bounded and stable leans Backend; growing or flexible leans Nexus.
4. **Ownership of derived or regulatory logic.** Does serving this fast require Backend to own logic that changes independently of Backend's own release cycle — a business rule, an aggregation, a regulatory threshold? If Backend would have to redeploy every time the *rule* changes rather than every time the *feature* changes, that logic belongs in Nexus, however fast Backend needs to read the result.

Every grey area below is one or more of these tests pulling in different directions at once — which is exactly what makes it a grey area rather than a clean call. Documents further down this series (starting with the scalability companion to this one) reuse this same framework rather than inventing a new one per topic.

## **Grey Area 1: CDC & the Outbox Pattern**

Backend commits a write. Nexus needs to know it happened, reliably, in order, without Backend ever blocking on Nexus being available. Test 1 says the *fact that something changed* has to be captured atomically with the write — but test 2 says the durable historical record of that change belongs to Nexus, not Backend. The resolution is a relay mechanism, not a shared table.

**Two real patterns, not one:**

* **Log-based CDC (Debezium, the default).** Debezium reads the database's own transaction log — the Postgres WAL, the MySQL binlog — directly, and turns every committed change into a Kafka event, in commit order. It runs as a Kafka Connect connector, which is infrastructure Nexus already commits to (`Broker_Messages_Services.md`). This costs zero application code: every write path Backend has, including ones nobody remembers to instrument, is captured automatically, because Debezium doesn't depend on the application remembering to do anything. It also captures changes from outside application code entirely — a DBA's manual fix, a migration script — and it can take an initial consistent snapshot of existing data and continue streaming from that exact point, one mechanism for backfill and ongoing capture.
* **Explicit outbox table.** Backend writes a row to an `outbox_events` table in the *same local transaction* as the business write; a relay process reads that table and publishes to Kafka. This is the right tool specifically when the meaningful business event is composite — "an application was submitted" might touch an `applications` row, a `documents` row, and a `payments` row in one transaction, and a single designed event describing that whole fact is more useful to Nexus than three raw row-diffs a downstream consumer has to stitch back together. It's also the only option where a client's database won't grant replication-log access, which is a genuinely privileged permission some managed databases or DBA teams refuse.

**Two anti-patterns worth naming, because they're what gets built before either pattern is understood:**

* **Dual-write** — the application writes to its own database and publishes to Kafka as two separate operations. Not atomic: one can succeed while the other fails, with no transaction spanning both, producing silent data loss or duplication under any partial failure.
* **Polling** — a periodic `WHERE updated_at > last_checkpoint` query. Misses deletes outright (unless soft-deleted), misses rapid successive updates to the same row between polls (only the final state survives, every intermediate value lost), and adds recurring query load to the operational database. This directly conflicts with Data Principles T1 (History is never overwritten) — a change that happened and was then overwritten before the next poll never existed as far as Nexus is concerned.

**Worked example.** A citizen updates their address through the Backend app. Under log-based CDC, the `UPDATE citizens SET address = ...` commit is picked up by Debezium directly from the WAL — no other code runs. Under the outbox pattern, the same transaction also inserts a row into `outbox_events` describing an `address_changed` business event with exactly the fields Nexus needs, and a relay tails that table into Kafka. Either way, the event lands in Bronze as an immutable, append-only record — never a shared table both sides read and write.

**Recommendation:** Debezium by default for routine table-level capture; an explicit outbox table specifically for composite business events or where log access isn't grantable. A mature Backend plausibly runs both, for different tables.

## **Grey Area 2: Read Caches & UI Aggregates**

A caseworker's dashboard needs "3 pending approvals" and "42 overdue renewals" to render fast. Computing either is exactly the kind of join/aggregation the Golden Triad wants kept *out* of Backend's "simple and lightweight" data model — but a page that's slow to render is a real UX cost. The fork isn't speed; it's what the number is *for*.

* **Gating aggregates — block or allow a write.** "You already have 3 active applications, you can't submit a 4th" has to be correct at the exact moment Backend decides whether to accept the new write. Test 1 wins: this must be computed transactionally, from Backend's own bounded operational data. If a gating check would need cross-Dominion data to evaluate, that's a signal the workflow itself is mis-scoped — Backend shouldn't be gating a decision on data it doesn't own and can't see consistently.
* **Informational aggregates — pure display.** "42 overdue renewals" doesn't gate anything; it informs. This is Nexus's Gold layer, either called live through an API (fine if the latency budget allows it — Annex D's Tier 2, p95 ≤ 2s, comfortably covers a dashboard) or cached with an explicit, visible staleness label ("as of 09:41") if the UI needs to feel snappier. What it must never become is a number Backend silently recomputes from its own copy of the data — that's the exact "second source of truth" failure mode this whole boundary exists to prevent.

**Worked example.** A search-by-name autocomplete needs sub-100ms responses across potentially millions of citizens — clearly informational, clearly Nexus-scale. Rather than Backend building and maintaining its own search index (a second, competing source of search relevance), Nexus maintains the index against Gold data and serves it through an API Backend calls; if that latency doesn't clear the bar for autocomplete specifically, the answer is a Nexus-pushed, explicitly time-stamped cache — not a Backend-owned index that can silently drift from what Nexus considers current.

## **Grey Area 3: File/Document Upload Landing**

A citizen uploads an ID document mid-application. Raw files are Nexus's domain by design: unstructured object storage is mapped via metadata into the Bronze layer, to be processed by AI agents. Keeping large binary blobs in Backend's own "simple and lightweight" store directly contradicts what Backend's data model is supposed to stay.

**Default:** the Frontend uploads directly to Nexus's object storage via a pre-signed URL, bypassing Backend's own storage and database entirely for the bytes themselves. Backend's role shrinks to authorizing the upload (issuing or relaying the pre-signed URL/token) and recording a lightweight pointer plus status — `document_ref: <id>, status: pending_processing` — transactionally, as part of the workflow state it already owns.

**The one genuine third layer:** some uploads need a synchronous check before the workflow can proceed — file type, size limit, a virus scan — and the user is waiting live, so it can't wait on Nexus's full async Bronze → Silver pipeline. That check belongs at a thin upload-broker/edge layer, not strictly inside Backend or Nexus: fast, stateless, disposable, and deliberately not where the durable landing or OCR/AI extraction happens.

**Worked example.** A citizen attaches a passport scan to a renewal application. The Frontend requests a pre-signed URL (via Backend, so authorization is enforced), uploads the file straight to Nexus's object storage, and the edge layer confirms it's actually an image under the size limit before the Frontend shows "uploaded." Backend records `document_ref` and `status: pending_processing` in the same transaction that advances the application's workflow state. Bronze picks up the file asynchronously; OCR/AI extraction and validation happen entirely inside Nexus, on Nexus's own schedule, never blocking the citizen's session.

## **Grey Area 4: Regulatory/Reference Data**

Validating a submitted form needs to be fast and synchronous — "is this tax ID format valid for this jurisdiction," "is this citizen old enough per this region's threshold" — which pulls toward Backend under test 1. But the rules themselves change per client and jurisdiction, need versioning and an audit trail of when a threshold changed, and are exactly the kind of governed, evolving content Annex C already has a mechanism for: a Dominion-owned, certified data product (Annex C.6).

This is the same "own versus cache" shape as Grey Area 2, worth stating as one general principle rather than two unrelated rules: **Nexus owns and governs; Backend may cache a read-only copy for speed, but never becomes a second source of truth for anything it caches.** The ruleset is authored and certified in Nexus like any other Gold product; Backend holds a read-only, periodically-refreshed local copy (or an embedded rules-evaluation library fed by a Nexus-published version) purely for fast synchronous evaluation.

**Worked example.** A jurisdiction raises its minimum age for a permit from 16 to 17. A "Regulatory Rules" Dominion owner updates and re-certifies the ruleset in Nexus. Backend's local cache picks up the new version on its next refresh — seconds via a push/webhook, or minutes via poll — with no Backend code deploy required, and the change is versioned and audited exactly like every other Gold product under Annex C.6, not a silent constant buried in Backend's codebase.

## **Grey Area 5: Workflow Status History**

Backend needs "what's true right now" — an application is in status X — to render the UI and gate the next action, which test 1 puts squarely in Backend. Reconstructing "how did this application's status evolve over the last six months, and did that correlate with anything else" is a Nexus/Silver/Gold analytical question under test 2. The two needs don't compete; status is expected to live twice, deliberately, and that's not a smell.

Backend's current-status column is the fast, transactional answer to "what should the UI show now." Every status *change* flows through the exact same mechanism as Grey Area 1 — Debezium or the outbox — into Bronze, and becomes a proper Data Vault Satellite in Silver: full point-in-time history, survivorship-safe, joinable across Dominions, per `Data_Vault_2.0.md`. This is what actually reconciles "Backend owns current state" with "Nexus owns history" — the same CDC mechanism that captures an address change captures a status change, with no second, independently-written record to keep in sync.

**Worked example.** An application moves from `submitted` to `under_review` to `approved`. Backend's `applications.status` column always reflects the current value, read transactionally by the UI. Each transition is captured by CDC the same way any other row change is, lands in Bronze, and becomes a new `Application Status Satellite` row in Silver with its own load date — so "how long did review actually take, across every application this quarter" is a query against Silver, not a request to reconstruct history from Backend's audit log, because Backend was never asked to keep one.

## **Diagram**

![Golden Triad Data Boundaries: Frontend, Backend/BackOffice, and Nexus columns showing the clean split, with the five grey areas — CDC/outbox, read caches, file upload landing, regulatory data, and workflow status history — resolved in a middle band with arrows showing the actual mechanism connecting Backend to Nexus](Golden_Triad_Data_Boundaries.png)

*Diagram: the clean split on either side, with the five grey areas resolved as mechanisms connecting Backend and Nexus rather than data duplicated between them. (Editable source: `Golden_Triad_Data_Boundaries.drawio`.)*

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| Backend stays genuinely simple | Every grey area resolves toward Backend keeping only current, bounded, transactional state — derived and historical logic never creeps back in through a "just this once" exception |
| One designed contract instead of ad-hoc integration | The outbox pattern and pre-signed-URL uploads both replace implicit, easy-to-drift integrations with an explicit, versioned contract between Backend and Nexus |
| A reusable framework, not a one-off list | The four-test framework answers the next grey area that comes up, not just the five worked here — and carries forward into the scalability companion to this document |
| No second source of truth, anywhere | Every resolution — caching, status history, regulatory rules — is explicit about which side owns the fact and which side, if any, merely reads a copy |

## **Honest Trade-Offs**

| Trade-off | The real cost |
| --- | --- |
| CDC is infrastructure to operate, not a free abstraction | Debezium and Kafka Connect are another system with their own failure modes, lag, and monitoring surface — "Backend doesn't need to know about Nexus" doesn't mean nobody needs to know about the pipe connecting them |
| Cache staleness has to be a UX decision, not an accident | An informational aggregate or cached ruleset that's silently stale is worse than one that's honestly labeled as of a timestamp — this requires deliberate design, not just "add a cache" |
| The pre-signed-URL upload path adds a coordination step | Backend authorizing an upload it never sees the bytes of means more moving parts than a naive single-service upload handler, in exchange for keeping Backend's storage footprint genuinely small |
| Discipline is required, not just architecture | Nothing stops an engineer under deadline pressure from adding "just one more" derived aggregate straight into Backend — the framework only works if it's actually applied at the point a new grey area shows up |

## **Verdict**

The Golden Triad's one-line boundary is correct as far as it goes, but "Backend is simple, Nexus does the heavy lifting" was never going to resolve a CDC staging table, a live UI counter, a mid-transaction file upload, or a validation rule that changes by jurisdiction — the cases that actually determine whether the boundary holds in practice. The clean split above restates what the rest of this documentation set already committed to; the four-test decision framework is the actual deliverable, because it's what resolves the next grey area this document didn't anticipate. The five worked through here — CDC and the outbox pattern, read caches and UI aggregates, file upload landing, regulatory data, and workflow status history — are applications of that framework, not an exhaustive list, and the pattern that recurs across all five is the same one: Nexus owns and governs, Backend may hold a fast, explicit, read-only copy of the result, and nothing is ever allowed to become a second, independently-written source of truth.
