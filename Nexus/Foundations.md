# **Technical Foundations**

*Companion document to* **`Data_Principles.md`**. *This file contains the full engineering mechanism behind every Annex referenced in the Data Principles — audience: architects, engineers, and anyone implementing against these principles. For the principles themselves, see* `Data_Principles.md`*; for the terms, see* `Glossary.md`*.*

**Part:** 2 — Principles and mechanisms · **Document:** 7 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Contents**

* Annex A: GDPR Erasure Protocol
* Annex B: Identity Resolution
* Annex C: Dominion Governance
* Annex D: Service Level Objectives
* Annex E: Disaster Recovery & Continuity
* Annex F: Data Quality
* Annex G: Multi-Tenancy & Data Residency
* Annex H: Document Governance

## **Risk-to-Mitigation Summary**

Each risk below resolves to a concrete mechanism defined in one of the Annexes below.

| Risk | Mitigation | Annex |
|---|---|---|
| GDPR's right to erasure conflicts with an immutable, append-only audit trail | Crypto-shredding and tokenization: erasure destroys a key, not a record; approved by two distinct roles; checked against active legal holds | A |
| The same citizen or institution is recorded independently, and inconsistently, across Dominions | Graph-based identity resolution with confidence-scored, reversible matching — no physical merging of source data | B |
| "Data as a product" has no real ownership, decision rights, or dispute process | An accountable owner per Dominion, a defined lifecycle, a cross-Dominion escalation path, and a certification gate | C |
| Performance and uptime promises are asserted, never quantified | A tiered Service Level Objective framework, measured per request, with per-client benchmarking for On-Premise deployments | D |
| No stated recovery target if a data center — or the encryption key vault — is lost | RPO/RTO targets by tier, split-custody key backup, mandatory drills, and a shared client/Nexus backup responsibility | E |
| "Automated quality controls" is a slogan with no concrete mechanism | Quality checks live in dbt itself; AI proposes tests and triages failures; a human is needed only for the hardest cases | F |
| No stated rule for where a client's data may legally reside, or how tenants are isolated | Dedicated deployment per client; residency is the client's own declared, contractual decision; a hybrid on-premise + client-key-encrypted cloud backup by default | G |
| Principles with no version, owner, or amendment process | Formal semantic versioning, clear ownership, and a defined amendment process | H |

## **Annex A: GDPR Erasure Protocol**

This annex resolves the apparent tension between Data Principles T1 (History is never overwritten) and GDPR's right to erasure (Article 17). The resolution is cryptographic, not physical: Bronze remains genuinely append-only and nothing is ever rewritten or vacuumed on demand; what is destroyed on erasure is the ability to read the data, not the data itself.

*For a narrative walkthrough of this mechanism, and an open analysis of the key vault's own topology (federation, HA, and alternatives — none of it adopted), see* `Encryption_Key_Custody.md`*. This Annex remains the single authoritative source; that document is a readable map to it, not a second copy.*

**A.1 — Mechanism: Crypto-Shredding & Tokenization**

* At Bronze ingestion, every field containing personal data is encrypted with a **per-subject Data Encryption Key (DEK)**, not a shared table- or partition-level key. DEKs live in a dedicated key vault (KMS or equivalent), indexed by subject ID — never inside the data tables themselves.
* Erasure of a subject's data is executed by **destroying that subject's DEK**. The Bronze row physically persists — append-only and time-travel guarantees are untouched — but its personal-data fields become permanently unrecoverable ciphertext.
* For fields that must remain queryable as join keys (e.g., a citizen identifier used across Dominions), use **tokenization** instead: the real value is replaced with a token at ingestion, and the token-to-value mapping lives in a separate vault table. Erasure deletes the mapping row; the token persists harmlessly in Bronze.
* Iceberg/Delta snapshot expiration and vacuum remain a periodic storage-hygiene job, not the compliance mechanism — erasure must not depend on the timing of the next vacuum run.

**A.2 — Approval Workflow (Maker-Checker)**

* Erasure is a privileged, irreversible action and requires two distinct identities: a **requester** (any authorized role) and a separate **approver** (a designated Data Protection role), consistent with Data Principles T3 (Humans stay accountable for consequential decisions).
* The action does not execute until both identities are recorded. No single credential can unilaterally erase a subject's data.

**A.3 — Legal Hold Exception**

* Before execution, every erasure request is checked against a `legal_hold_registry` (subject reference, reason, expiry, authorizing party).
* A matching active hold blocks or defers execution — e.g., for tax, anti-fraud, or active-litigation obligations — and the block itself is logged with its reason, never silently ignored.

**A.4 — Cascading Propagation**

* Erasure must not stop at Bronze. On approval, an event (`subject.erasure_requested`) is published to the streaming backbone; every downstream Dominion or service holding a derived copy of that subject's data (Silver, Gold, ML feature stores, search/vector indexes, caches) subscribes and either re-derives from the now-shredded Bronze source or explicitly purges its own copy.
* OpenMetadata's lineage graph is the source of truth for *which* downstream assets must respond to a given erasure request.
* An orchestrated workflow owns the end-to-end request: fan out, collect completion acknowledgments from every affected Dominion, and only then close the request. This also yields a natural SLA metric — time from approval to full-cascade completion.

**A.5 — Audit Trail**

* Every erasure event is logged in a structured, append-only record that captures **only metadata — never the erased personal data itself**:
  * a pseudonymous subject reference (e.g., a hashed ID, never raw PII)
  * requester and approver identities
  * legal basis for the request
  * scope (which Dominions/layers were targeted)
  * mechanism used (key destroyed / token revoked)
  * timestamp
  * whether a legal hold was checked and its result
* This record is retained for a minimum of **10 years** — deliberately exceeding the typical 3–6 year GDPR accountability baseline — under a retention clock that is independent of, and outlives, the retention period that applied to the original (now-erased) data.

## **Annex B: Identity Resolution**

This annex resolves the gap between the goal of one authoritative place per fact (Data Principles O1) and the reality that the same citizen or institution is observed independently by multiple Dominions, each with its own local record. Nexus does not force these Dominions to physically merge or overwrite their data; instead, it resolves identity at query time using a dedicated graph layer, keeping Dominion ownership and Bronze immutability fully intact.

**B.1 — Data Model**

* **`LocalIdentity` node** — one per Dominion's observation of a subject. Properties: `dominion_id`, `local_id`, `source_record_ref`, `ingested_at`. This is a pointer back to that Dominion's own record, never a copy of its attributes.
* **`Subject` node** — the resolved golden identity. Deliberately thin, holding only an identifier and creation metadata — never the actual attributes — so it can never drift out of sync with the Dominions it represents.
* **`SAME_AS` relationship** — links two `LocalIdentity` nodes (or a `LocalIdentity` to a `Subject`), carrying `confidence_score`, `match_method` (`deterministic` | `probabilistic`), `evidence`, `decided_by`, `decided_at`, and `status` (`candidate` | `confirmed` | `rejected`).

**B.2 — Matching Pipeline**

* **Deterministic pass:** an exact match on a strong key (e.g., national ID, tax ID) produces an auto-confirmed `SAME_AS` edge with no human involved.
* **Probabilistic pass:** fuzzy matching on attributes such as name, date of birth, and address handles everything the deterministic pass leaves unresolved. Matches above a defined high-confidence threshold are auto-confirmed; matches below it are created as `candidate` edges and routed to a human steward for review, per Data Principles T3 (Humans stay accountable for consequential decisions).

**B.3 — Survivorship**

* Per-field source authority is resolved at query time when a `Subject 360` view is requested or materialized into Gold — for example, the civil registry Dominion is authoritative for legal name and date of birth, while the postal/address Dominion is authoritative for current address. Dominions' own records are never overwritten to produce this view.

**B.4 — Reversibility**

* A `confirmed` `SAME_AS` edge can be disputed by a steward and flipped to `rejected`, splitting a wrongly merged identity back into separate Subjects. This satisfies Data Principles T5 (Identity is resolved, never forcibly merged) and P5 (Safe to evolve, safe to remove) — identity-resolution mistakes are recoverable, not permanent.

**B.5 — Architectural Placement**

* The resolution graph reads from cleaned Dominion data in Silver. Gold exposes the resolved `Subject 360` view via API. Bronze remains untouched and per-Dominion, preserving the raw, immutable record required by Annex A.

**B.6 — Provenance**

* Every field returned in a `Subject 360` view carries a pointer back to the Dominion, record, and timestamp it was sourced from, making Data Principles O1 (One authoritative place per fact) auditable rather than asserted.

## **Annex C: Dominion Governance**

This annex turns the Data Mesh language — "Dominions," "data as a product," "clear ownership" — and Data Principles O3 (Every value stream's data has a named owner) into an actual operating model. At this stage, the goal is the minimum structure needed for real accountability, without prematurely formalizing named roles or a standing body the organization isn't ready to commit to yet. Naming a specific role (e.g., a Data Product Owner title) or standing up a formal governance body is deliberately left open for a later version of this document.

**C.1 — What a Dominion Is**

* A Dominion is a bounded, domain-aligned unit of data ownership, mapped 1:1 to one accountable team — never a whole department, and never an ownership vacuum where "whoever touches the table" is implicitly responsible.
* A Dominion owns one or more data products end-to-end: schema, quality, SLAs, and documentation, within its bounded context.

**C.2 — Dominion Ownership**

* Every Dominion has an accountable owner — a person or small group within the team responsible for it. The individual holding this responsibility may rotate; the responsibility itself is never vacant.
* This owner's decision rights are concrete, not advisory:
  * Approve or reject schema changes to the Dominion's own data products.
  * Approve or reject consumer access requests from other Dominions.
  * Sign off on Annex A erasure requests and Annex B survivorship rules that touch the Dominion.
  * Certify a data product as production-ready in OpenMetadata before any team outside the Dominion may consume it.

**C.3 — Dominion Lifecycle**

* **Creation** requires, before any publication to Silver or Gold is permitted: an accountable owner, a declared bounded context, and minimum OpenMetadata registration (schema, owner, SLA). This gate is what prevents the "data swamp" risk — data that exists but cannot be found, trusted, or attributed to an owner.
* **Retirement or merge** requires a consumer migration plan and a defined deprecation window before the prior data product is decommissioned.

**C.4 — Cross-Dominion Escalation**

* Decisions no single Dominion can make alone — Annex B survivorship conflicts, shared Bronze/Silver conventions, and erasure exceptions spanning multiple Dominions — are escalated to Nexus leadership.
* A standing, cross-Dominion governance body may be formalized in a later version of this document; until then, leadership serves this function directly.

**C.5 — Escalation Path**

* Disputes between Dominions follow a fixed three-step path:
  1. The two Dominions' owners attempt direct resolution.
  2. If unresolved after 5 business days, the dispute escalates to Nexus leadership.
  3. Leadership's ruling is binding and recorded in a standing decision log, so the same dispute is never re-litigated from scratch — and institutional knowledge builds up systematically instead of being lost.

**C.6 — Certification Gate**

* A data product must carry a "certified" OpenMetadata status — verified by an automated policy check or a designated reviewer — before any Dominion other than its owner may consume it. This is the enforcement mechanism behind "data as a product," which otherwise has no teeth beyond the label.

## **Annex D: Service Level Objectives**

This annex turns "strict SLAs" from an assertion into measurable targets. Because Nexus spans real-time and batch workloads, and both Cloud and On-Premise deployments with very different elasticity, a single blanket number is inappropriate — SLOs are defined as a tiered framework with an explicit, measured exception process for On-Premise.

**D.1 — Four Measurable SLI Categories**

* **Freshness** — time from source event to data availability in a given layer.
* **Latency** — Gold-layer API response time.
* **Availability** — uptime of serving APIs.
* **Correctness** — proportion of records passing data quality checks (the underlying DQ mechanism is defined in Annex F).

**D.2 — Tier System (Cloud Defaults)**

| Tier | Description | Freshness | API Latency | Availability |
|---|---|---|---|---|
| 1 | Real-time / citizen-facing | ≤ 60s | p99 ≤ 300ms | 99.9% |
| 2 | Operational batch | ≤ 4h | p95 ≤ 2s | 99.5% |
| 3 | Analytical / historical | ≤ 24h | best-effort | 99% |

A Dominion's accountable owner (Annex C.2) may commit a data product to a stricter target than its tier's floor, never a looser one.

**D.3 — Breach Handling**

* An SLO breach emits a `WARN` or `ERROR` entry per the standard log-level scheme (`DEBUG`, `INFO`, `WARN`, `ERROR`) used across Nexus.
* Three breaches within a rolling 30-day window automatically escalate to Nexus leadership (Annex C.4) as a remediation review.

**D.4 — On-Premise: Kubernetes and Per-Client Measurement**

* Every On-Premise deployment runs on Kubernetes (or equivalent container orchestration) over virtualized infrastructure — never bare metal — decoupling Nexus's compute workloads from any single physical machine, consistent with Data Principles P3 (Storage and compute scale independently) and P2 (Everything as code).
* The Tier table in D.2 is a **Cloud default only**. It is never assumed to hold On-Premise.
* Each On-Premise client's deployment is assigned its own measured capacity baseline: a benchmark/load-test run against that client's actual provisioned Kubernetes cluster, producing client-specific numbers before any Tier is committed to.
* This benchmark is what "capacity-planning sign-off" concretely means — a Dominion cannot commit a given On-Premise client to Tier 1 until the benchmark against that client's real cluster demonstrates it can be met.
* Because the deployment target is Kubernetes rather than fixed hardware, a client whose measured numbers fall short of a needed tier has a direct remediation path — scale the cluster — rather than a hardware replacement project.

**D.5 — Measurement**

* The Correlation ID carried by every request is the mechanism for computing real freshness and latency per request, per Dominion.
* The Dominion's owner publishes measured historical SLO compliance in OpenMetadata, alongside the committed target, so consumers see actual performance rather than only the promise.

**D.6 — Certification Dependency**

* A data product cannot pass the Annex C.6 certification gate without declaring the Tier it commits to (and, for On-Premise clients, the client-specific benchmarked numbers from D.4).

## **Annex E: Disaster Recovery & Continuity**

This annex sets recovery targets and backup-testing requirements — including for encryption-key loss, an existential risk for Nexus. Recovery objectives reuse the Tier system already established in Annex D rather than introducing a second, parallel classification.

*E.2 specifically — the key vault's own, stricter DR class — is explored further in* `Encryption_Key_Custody.md`*, including whether its current unstated topology is the right one. That analysis does not amend this Annex.*

**E.1 — RPO/RTO by Tier**

| Tier | RPO | RTO |
|---|---|---|
| 1 | ≤ 5 min | ≤ 1h |
| 2 | ≤ 4h | ≤ 8h |
| 3 | ≤ 24h | ≤ 24h |

**E.2 — The Key Vault Is a Distinct, Stricter DR Class**

* The DEK/token vault underpinning Annex A is not subject to the Tier table above — its loss makes every subject's data permanently unrecoverable, not merely delayed or degraded.
* It requires near-synchronous replication across at least two independent failure domains, with RTO ≤ 15 minutes.
* In addition, a cold, offline backup is maintained using split custody (e.g., Shamir's Secret Sharing across named individuals), so that no single infrastructure failure — and no single compromised person — can cause irreversible, total data loss.

**E.3 — Backup Drills Are Mandatory, Not Assumed**

* Every Tier 1 data product, and the key vault without exception, undergoes a quarterly restore drill.
* Drill results are recorded in the standing decision log established in Annex C.5. A backup that has never been restored is not a verified backup.

**E.4 — On-Premise: Shared Responsibility for the Backup Destination**

* Nexus is responsible for building and automating the backup and replication tooling on the Kubernetes-based on-premise deployment (Annex D.4).
* The client is contractually responsible for providing a physically or logically separate destination to receive that backup — a secondary site, a cloud storage bucket, or a third-party facility — sized to hold, at minimum, the full Bronze layer plus the key vault. Where the client's declared data residency permits a cloud destination, that backup must be encrypted with keys held exclusively by the client, per **Annex G: Multi-Tenancy & Data Residency**.
* This is the recovery floor, independent of the steady-state RTO/RPO in E.1: because Silver and Gold are derived and recomputable by replaying pipelines against Bronze, a complete Bronze-plus-vault backup is sufficient to reconstruct the entire on-premise deployment from nothing after total loss of the primary site, with no data loss beyond what was in flight since the last backup cycle.
* This obligation is stated explicitly during client deployment onboarding. A client that never provisions this destination has, by default, no disaster recovery at all — this is a fact to be disclosed, not assumed away.

**E.5 — Ownership**

* Each Dominion's accountable owner (Annex C.2) owns their own data product's DR plan and drill results.
* The key vault's DR plan is owned by Nexus leadership (Annex C.4), since its loss is a cross-cutting, existential risk rather than any single Dominion's concern.

## **Annex F: Data Quality**

This annex turns Data Principles Q2 (Quality is a precondition, not a clean-up) into a concrete mechanism. The design goal is pragmatism: quality checks must live inside the tools teams already use, AI does the labor of proposing tests and triaging failures, and a human is involved only for the genuinely hard cases — not as a bottleneck on every run.

**F.1 — Checks Live Inside dbt, Not a Separate System**

* Data quality rules are expressed as dbt tests attached directly to Silver/Gold models. A model change and its quality checks travel together in the same pull request — there is no separate DQ platform to keep in sync.

**F.2 — A Baseline Test Set Is a Certification Requirement**

* Every model requires, at minimum: not-null and uniqueness tests on primary/foreign keys, referential integrity on any join, and a freshness test matching the model's Annex D tier.
* A data product without this baseline cannot pass the Annex C.6 certification gate. This is the enforcement mechanism — quality is a precondition for certification, not a best practice teams may skip.

**F.3 — AI Proposes Tests; a Human Approves Once**

* An agent, built on Nexus's agentic stack (LangGraph / Google GenAI SDK), profiles a new or changed model and proposes additional tests — value ranges, categorical whitelists, expected row-count deltas — derived from the actual data rather than hand-written from scratch.
* The Dominion's accountable owner reviews and approves proposed tests at model-change time. This is a one-time human touch, not an ongoing review burden.

**F.4 — Automatic Triage on Failure**

* When a dbt test fails during an Airflow-orchestrated run, a triage agent classifies the failure:
  * **Known pattern within historical variance** (e.g., a null-rate blip inside normal range): the offending records are automatically quarantined to a dead-letter table, a `WARN` is emitted, and the pipeline continues on the clean subset. No human is involved.
  * **Novel or high-severity pattern** — a threshold breached by a wide margin, a Tier 1 dataset affected, or a field feeding Annex A or Annex B: the failure is escalated to a human steward. This is the sole point at which a person is required, matching the principle that AI handles the routine case and humans handle the genuinely difficult one.

**F.5 — A Live Correctness Score**

* Each data product publishes a rolling "percentage of records passing tests" figure in OpenMetadata, reported alongside its Freshness, Latency, and Availability figures from Annex D.5 — quality becomes visible before it causes a downstream incident, not after.

**F.6 — Escalation Reuses Annex C.5**

* A data quality issue a Dominion's owner cannot resolve alone follows the same three-step escalation path already defined in Annex C.5. No separate governance body is created for data quality.

## **Annex G: Multi-Tenancy & Data Residency**

This annex sets out, under Data Principles P1 (Deploy anywhere), how tenants are isolated and where a given client's data is legally permitted to reside. Both are decided per client, not assumed by the platform.

**G.1 — Tenancy Model: Dedicated Deployment per Client**

* The default tenancy model is one dedicated deployment per client, running on that client's own benchmarked Kubernetes cluster (Annex D.4) — not a shared multi-tenant database with row-level tenant filters.
* This avoids the harder problem of cross-tenant Data-Level Control enforcement in a shared cluster entirely, rather than attempting to solve it, and is appropriate given the sensitivity of civic and institutional data Nexus handles.

**G.2 — Residency Is a Client-Declared, Contractual Parameter**

* At onboarding, the client — through their own legal and compliance function — declares which jurisdiction(s) their data-at-rest must remain in.
* This declaration, not a Nexus default or assumption, determines which deployment topology is legally available to that client. Nexus does not choose residency on the client's behalf.

**G.3 — Default Topology: Hybrid, On-Premise Primary with Client-Key-Encrypted Cloud Backup**

* The primary deployment remains on-premise, in the client's own jurisdiction, satisfying the strictest residency requirement by construction.
* The disaster recovery backup already required by Annex E.4 is shipped to cloud storage, encrypted with keys held exclusively by the client — never by Nexus, and never by the cloud provider. The cloud provider's infrastructure holds only unreadable ciphertext at rest.

**G.4 — Cost vs. Restriction: an Explicit, Disclosed Decision**

* Cloud backup storage is materially cheaper and more elastic than a client provisioning a genuine second physical on-premise site, which matters for resource efficiency.
* However, some jurisdictions or data classifications legally prohibit ciphertext from leaving national borders regardless of encryption. The client's declared residency requirement (G.2) determines which path applies:
  * **Permitted:** the cheaper hybrid default (G.3) applies.
  * **Prohibited:** the client must provision a second on-premise site instead, at a correspondingly higher cost that is disclosed during onboarding — never discovered after an incident.

**G.5 — The Decision Is Recorded, Not Verbal**

* The client's residency declaration, chosen topology, and resulting cost implication are signed off jointly by the client and Nexus leadership (Annex C.4) during onboarding, and stored as part of that client's deployment record in OpenMetadata — auditable in the same way as every other decision in this documentation set.

## **Annex H: Document Governance**

A set of principles with no version, owner, or amendment process cannot be trusted to govern anything else. This governance applies jointly to `Data_Principles.md` and this companion document, `Foundations.md` — the two are versioned and amended together, never independently.

**H.1 — Versioning Scheme**

* Both documents follow a shared, semantic-style `MAJOR.MINOR.PATCH` scheme:
  * **MAJOR** — a change that alters a principle in `Data_Principles.md`, e.g. redefining the Golden Triad boundary or an immutability guarantee.
  * **MINOR** — addition of a new Annex, a new principle, or a materially expanded mechanism or presentation.
  * **PATCH** — clarifications, typo fixes, or cross-reference updates that do not change meaning.
* Both documents are version-controlled the same way code is, consistent with Data Principles P2 (Everything as code) — changes are reviewed, not silently edited in place.

**H.2 — Ownership and Amendment Process**

* Nexus leadership owns both documents.
* Any Dominion owner or member of Nexus leadership may propose an amendment. Leadership must approve a proposal before any version bump is published — no individual may unilaterally amend either document.
* Formalizing this into a named role or a standing governance body (see Annex C.2 and C.4) is left for a later version, once the organization is ready to commit to that structure.

**H.3 — Changelog**

| Version | Date | Summary | Approved By |
|---|---|---|---|
| 0.1 | 2026-09-22 | First draft for PSS 3.0, companion to the Data Principles. Annexes A–H. | Pending Architecture Review Board |
