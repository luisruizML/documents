# Encryption Key Custody at Nexus

*Companion document to* `Foundations.md` *Annex A (GDPR Erasure Protocol) and Annex E (Disaster Recovery & Continuity) — Annex A and Annex E remain the single authoritative, detailed source of the adopted mechanism; nothing here amends them. This is the concentrated place for everything touching GDPR erasure, encryption-key custody, and key-vault security at Nexus — deliberately, because this subject matter is sensitive and easy to misread if its explanation is left thin and scattered across other companion documents. It has two distinct parts, kept strictly separate: a short, clearly-labeled summary of what Annex A and Annex E already commit Nexus to, each point citing back to the exact sub-annex rather than restating it in full, followed by an exploratory analysis of vault topology and alternatives that is clearly marked as not adopted. Annex A.1 commits Nexus to per-subject Data Encryption Keys (DEKs) held in "a dedicated key vault (KMS or equivalent)" without ever specifying a topology; Annex E.2 declares that same vault's loss "makes every subject's data permanently unrecoverable" and holds it to a stricter DR bar than anything else in the platform. The exploratory half of this document is the case for reconsidering that topology — it does* ***not*** *amend Annex A or Annex E, and any recommendation in it becomes Nexus's actual architecture only through the Annex H leadership amendment process.*

**Part:** 3 — How it is built · **Document:** 20 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

*Scope note: "The Adopted Mechanism — Summary" summarizes Annex A/E, which remain authoritative; everything after "Availability vs. Blast Radius" is exploratory, not adopted.*

## **Executive Summary**

Annex A.1 says every personal-data field is encrypted at Bronze ingestion with a per-subject DEK, and that DEKs "live in a dedicated key vault (KMS or equivalent), indexed by subject ID." Annex E.2 says that vault's loss is catastrophic and irreversible, and requires it to be replicated across independent failure domains with a cold, split-custody backup. Neither Annex says what kind of vault, what topology, or where it actually runs. That gap is this document's starting point.

The short version of what follows: **availability and blast radius are different problems**, and Annex E.2 only solves the first. Six ways to harden the vault itself are compared, landing on federating key material by Dominion or client combined with a real high-availability consensus cluster as the practical default. A separate, previously unstated finding — Annex A.1 as written puts the vault on Bronze's *write* path, in direct tension with Bronze's own design goal of absorbing bursty writes cheaply — points toward moving per-subject keying to the Silver-load boundary regardless of topology. And a deeper alternative is pressure-tested to its real conclusion: removing per-subject application-layer encryption from the pipeline entirely doesn't harden the vault, it deletes the question by deleting the component — at the cost of collapsing Nexus's security model from two independent control types (access control and cryptography) down to one, and at the cost of removing Annex A's GDPR erasure mechanism outright. That direction is where this analysis leans, but adopting it is a governance decision, not a documentation one — it belongs to Annex H, not to this file.

**A note on how to read this document.** GDPR erasure, encryption-key custody, and disaster recovery for the key vault are sensitive, easy-to-misread topics, and the substance of them used to be scattered thin across several companion documents. This document is written to be the one place that has to be right, without becoming a second copy of the source: the section immediately below summarizes the *adopted* mechanism, citing Annex A and Annex E point by point rather than restating them — for exact wording, go to the Annex itself. Everything after the "Availability vs. Blast Radius" heading is analysis and alternatives, clearly not adopted, clearly labeled as such throughout. If you read only one section, and you need to know what Nexus actually does today, read the one below and then go to Annex A/E for the full text.

## **The Adopted Mechanism — Summary**

This is a summary, not a second copy. `Foundations.md` Annex A and Annex E remain the single authoritative, detailed source of the adopted mechanism — for exact wording, thresholds, and procedure, go there. This list exists so the shape of what's adopted is visible without leaving this document, nothing more; nothing here is proposed, optional, or up for debate.

* **Erasure mechanism (Annex A.1).** A per-subject Data Encryption Key (DEK) encrypts personal-data fields at Bronze ingestion; destroying that DEK makes the field permanently unrecoverable ciphertext while the row itself stays in place. Join-key fields use tokenization instead, so erasure there means deleting a token mapping, not a key.
* **Approval (Annex A.2 — Maker-Checker).** Two distinct identities — a requester and a separate Data Protection approver — are required before an erasure executes.
* **Legal Hold (Annex A.3).** Every request is checked against a hold registry first; an active hold blocks or defers execution, logged either way.
* **Propagation (Annex A.4).** An event fans out to every downstream copy — Silver, Gold, feature stores, indexes, caches — each of which re-derives or purges; OpenMetadata lineage decides scope.
* **Audit (Annex A.5).** A metadata-only, append-only record, retained a minimum of 10 years, independent of the erased data's own retention.
* **Vault resilience (Annex E.1–E.2).** The DEK/token vault is exempt from the standard Tier RPO/RTO table — it needs near-synchronous replication across at least two independent failure domains, RTO ≤ 15 minutes, plus a cold, offline backup under split custody (Shamir's Secret Sharing).
* **Drills and ownership (Annex E.3, E.5).** The vault gets a mandatory quarterly restore drill and is owned directly by Nexus leadership, not any single Dominion.

Everything from here on is this document's own analysis and exploration, built on top of the mechanism above — not a restatement of it.

## **Availability vs. Blast Radius**

Annex E.2's requirements — near-synchronous replication across independent failure domains, RTO ≤ 15 minutes, a Shamir's-Secret-Sharing cold backup — are all about *uptime and durability*: can the vault survive a data center burning down. None of it addresses a different question: if the vault's access-control layer is breached — a leaked admin credential, a vault-software vulnerability, an over-broad policy — how much of Nexus's data does that expose? A replicated vault is still, logically, one trust domain; every copy answers to the same policy. Everything below is organized around closing that second gap, not the first one, which Annex E.2 already covers.

## **Hardening the Vault: Six Options**

| # | Approach | Fixes availability? | Fixes blast radius? | Ops cost for a lean team | Reuses an existing Nexus pattern? |
|---|---|---|---|---|---|
| 1 | **Status quo** — one flat vault, replicated, Shamir-backed cold backup | Partially | No — one compromise domain for everything | Lowest | — |
| 2 | **Federate by Dominion/client** — a separate namespace or CMK per Dominion (or per client, on top of Annex G.1's dedicated-deployment model) | No change | Yes — a breach caps at one Dominion or client, not the platform | Moderate (namespaces within one cluster) | **Yes** — mirrors Annex C.1 ("a Dominion is a bounded, domain-aligned unit of data ownership") and Annex G.1 exactly |
| 3 | **Live threshold / multi-party custody** — no single node or credential can unwrap a DEK alone, not just for cold backup | No change | Yes, strongest — defeats a single compromised credential or insider outright | High — most managed KMS products don't support this natively; real added latency at Bronze→Silver shredding volume | No — extends Annex E.2's Shamir idea from backup-only into live operations, which is new territory |
| 4 | **Real HA consensus cluster** (e.g. self-hosted Vault with Raft integrated storage, or a multi-region managed KMS) instead of primary/replica replication | Yes — near-zero RTO, automatic failover, mainstream and well-supported | No change | Modest (3–5 nodes instead of 2) | Upgrades what Annex E.2 already asks for |
| 5 | **Source-side / BYOK custody** — each Dominion or client holds the root key that wraps its own DEKs; Nexus's own infrastructure never holds a key spanning more than one Dominion | No change, and can make it worse (N external systems' uptime now on the critical path) | Yes, philosophically strongest | High — pushes real key-operations burden onto Dominions/clients who may not want it | **Yes** — extends Annex G.3's client-held cloud-backup key model from DR backups to the primary path |
| 6 | **HSM-backed root key** (a hardening layer, not a topology) | No change | Reduces exportable-key-material risk specifically | Low if built on a mainstream cloud KMS (most already do this by default) | Complements any of the above |

**Recommendation for the default:** federation (#2) on top of a real consensus cluster (#4) — mainstream, well-supported infrastructure, with blast radius capped at the bounded-context unit (Dominion or client) Nexus already treats as the natural boundary everywhere else. Live threshold custody (#3) is deliberately left out of the default: once #2 already contains blast radius, the added latency and bespoke-tooling cost buys comparatively little. It is better reserved as an opt-in for one especially sensitive tier or client than adopted platform-wide.

## **Open-Source Options for #4**

Approach #4 named "self-hosted Vault with Raft integrated storage" as its example — worth being precise about what that actually means today, since licensing across this whole space shifted materially in 2023 and "open source" no longer describes the incumbent the way it used to.

| Option | License | Genuinely open source? | Delivers #4's HA, free? | Best fit |
| --- | --- | --- | --- | --- |
| **OpenBao** — recommended default | MPL 2.0 (Linux Foundation) | Yes — OSI-approved | Yes — inherits Vault's exact Raft integrated-storage architecture | Neutral governance, forked from Vault's last MPL release (1.14.0), actively developed since (Namespaces, horizontal read scaling). Battle-tested by inheritance, not a rewrite. |
| **HashiCorp Vault (Community Edition)** | BSL 1.1 (since Aug 2023) | No — source-available, not OSI; converts to MPL 4 years after each release | Yes | Restriction is about *reselling* Vault as a competing hosted service, not Nexus's own internal use — but real tension with Data Principles L2 (Open formats; no vendor dependency). Largest ecosystem, docs, and hiring pool of anything here. |
| **Infisical** | MIT | Yes | Unproven at this scale — no established track record as an HA vault backing millions of per-subject DEKs | Fastest-growing independent challenger, gentler learning curve than Vault/OpenBao. Worth a bake-off as it matures, not a default pick today. |
| **CyberArk Conjur OSS** | LGPL v3.0 (server) + Apache 2.0 (clients) | Yes | No — HA/distributed architecture is a paid CyberArk Secrets Manager feature | Actively maintained (v1.24.0, Nov 2025), but the free edition is a single server against Postgres. Doesn't clear the bar for #4 without paying. |
| **OpenStack Barbican** | Apache 2.0 | Yes | Yes, via OpenStack's own HA patterns | Native PKCS#11 HSM plugin support ties directly into the on-premise HSM story below — but right only for a client already on OpenStack; Nexus's own on-premise mandate is Kubernetes (Annex D.4), not OpenStack. |

**Net:** default to OpenBao for the reasons above; Vault Community Edition remains a legitimate fallback where its ecosystem maturity outweighs the license concern; Infisical is worth a bake-off as it matures; Conjur OSS and Barbican are the right call only in their specific niches — an existing CyberArk relationship, or an existing OpenStack estate, respectively.

## **Under an On-Premise-Only Constraint**

The recommendation above leans on pieces that are cloud-native by default (managed multi-region KMS, HSM-as-a-service). Neither survives an on-premise-only requirement unchanged:

- **#4 substitutes to:** a self-hosted consensus cluster — OpenBao (or Vault Community Edition, per the license trade-off above) with Raft integrated storage, 3–5 nodes, run on the client's own Kubernetes deployment (Annex D.4).
- **#6 substitutes to:** a physical, PKCS#11-compatible HSM appliance, with the self-hosted cluster auto-unsealing against it — a real hardware line-item and vendor relationship the managed-cloud story got for free.
- **#2 is essentially unaffected** — namespacing is a policy concept, indifferent to cloud vs. on-prem.

The deciding factor is **whether the client has one site or two.** With a second site, the cluster stretches across both and delivers real protection against a whole-site loss — the same shape Annex G.4 already requires when cloud is prohibited: the client provisions a second on-premise site instead, at disclosed extra cost. With a single site, a Raft cluster still protects against node or rack failure — most of what actually goes wrong — but not against the building itself, and there is no cloud fallback to quietly cover that gap the way Annex G.3's hybrid default does elsewhere. Annex E.4 is already explicit that an unprovisioned backup destination means "no disaster recovery at all — this is a fact to be disclosed, not assumed away"; the same discipline applies here, to the live vault, not only the backup.

This is also precisely the case where option #3 (live threshold custody) stops being a marginal, opt-in extra: with no second site to spread trust across, multi-party custody is the only remaining lever against a compromised operator or credential at "the one site you've got" — worth the added cost narrowly, for single-site on-premise clients, not as a platform default.

## **Where the Vault Sits in the Pipeline**

A separate axis from topology: *when* in the pipeline the vault is actually load-bearing. Annex A.1, read literally, requires a DEK at Bronze **ingestion** — meaning every single Bronze write, today, already depends on the vault being available. That is in direct tension with `Medallion_Architecture.md`'s own design goal for Bronze: *"Bronze needs to absorb high-volume, bursty writes cheaply and reliably. It does not need query performance."* A vault dependency on every write is exactly the kind of coupling that goal argues against.

Deferring per-subject keying to the **Silver-load boundary** instead — the scheduled, batch "shredding" step that already exists, and that tolerates delay under Annex D's Freshness SLI — removes the vault from Bronze's write path entirely, regardless of which of the six options above is chosen. A vault outage would then degrade Silver's freshness, a recoverable, already-measured condition, rather than blocking ingestion outright. This is a real, orthogonal improvement worth adopting independent of the topology question.

## **The Deeper Alternative: Eliminating the Vault**

The furthest point this analysis was pushed to: what if Nexus does not apply per-subject application-layer encryption anywhere in the pipeline at all? Protection would rest entirely on two things that already exist regardless: generic infrastructure-level encryption at rest (disk/volume/object storage, provider- or OS-managed — defends against media leaving the trust boundary, essentially free to enable) and access control (storage IAM for Bronze, Data-Level Controls for Silver and Gold, per `Data_Level_Controls.md`).

This is not a variant of the six hardening options — it does not make the vault more resilient, it removes the question by removing the component. That has to be weighed honestly on both sides:

**What it buys:** every operational cost discussed above disappears — no topology decision, no per-Dominion namespacing, no HSM procurement, no live-threshold latency tax, nothing to hold to Annex E.2's stricter DR bar, no quarterly vault-specific restore drill (Annex E.3). For a lean team, this is a legitimate, not merely lazy, answer: fewer independently-operated systems is itself a security property, not only a cost saving.

**What it costs:** it converts Nexus's security posture from **defense-in-depth** — access control *and* an independent cryptographic layer, so one mistake in either doesn't expose data on its own — to a **single layer**, access control alone. Concretely: a leaked service credential, an over-broad IAM policy, a ReBAC traversal bug, or a misconfigured bucket each become the entire breach, immediately, with nothing else standing in the way. Misconfigured storage access is already the most common real-world cloud breach pattern industry-wide; this removes the one thing that would have contained exactly that failure mode. And it lands hardest specifically at Bronze — the layer `Medallion_Architecture.md`'s own access table already calls *"the highest-risk surface... the one layer where a raw, unredacted source payload can appear before any masking or cleaning runs"* — the layer today's design protects the most, this alternative protects the least.

**The unresolved conflict, stated once and left there:** with no per-subject key anywhere, Annex A.1's crypto-shredding mechanism has nothing left to destroy on an erasure request — there is no cryptographic path to make an immutable Bronze row unreadable. Annex A.4's downstream cascade (re-deriving or purging every copy in Silver, Gold, feature stores, search indexes, and caches) still functions unchanged, since it never depended on Bronze-level keys in the first place — so a **partial** erasure model survives even under this alternative: everywhere a citizen would actually encounter their data, gone; the immutable raw Bronze archive, not. That is the most likely resolution path if this direction is ever formally adopted, but it is a disclosed limitation, not full compliance, and reconciling it against Data Principles T1's guarantee that history is never overwritten is exactly the kind of core-principle change Annex H.1 classifies as **MAJOR** — leadership approval, not a documentation edit.

## **Strengths**

| Strength | Which direction it favors |
|---|---|
| Blast radius capped at a bounded context, not the platform | Harden-the-vault, via federation (#2) |
| Near-zero RTO on infrastructure failure, mainstream tooling | Harden-the-vault, via a consensus cluster (#4) |
| No vault write-path dependency on Bronze ingestion | Both directions equally, once keying is deferred to Silver-load |
| Fewest independently-operated systems for a lean team to run | Eliminate-the-vault |
| A single control layer that's fully understood and can actually be drilled, rather than six half-understood ones | Eliminate-the-vault |

## **Honest Trade-Offs**

| Trade-off | The real cost |
|---|---|
| Harden-the-vault still has an unstated topology today | Every option in the six-way table is a real build — none of them is "free," and Annex E.2 doesn't commit to any specific one, so this remains an open decision regardless of which option is favored |
| On-premise, single-site clients cannot get true site-level HA from a consensus cluster alone | No cloud fallback exists to quietly cover that gap; it must be disclosed at onboarding, per the same principle Annex E.4 already applies to backups |
| Eliminate-the-vault removes Annex A's GDPR erasure mechanism, not just weakens it | Only a partial-erasure model survives (downstream copies purge; Bronze's raw archive does not); adopting this requires reconciling Data Principles T1's guarantee that history is never overwritten with GDPR Article 17 from scratch, through Annex H, not this document |
| Eliminate-the-vault collapses defense-in-depth to a single control type | A misconfiguration that used to be contained by the vault becomes the entire breach; this is a categorical change in risk posture, not a quantitative one |

## **Verdict**

Annex A.1 and Annex E.2 specify a mechanism and a durability bar, but never a topology — that gap is real, and any of the six hardening options in this document closes it more honestly than the status quo's silence does. Federating key material by Dominion or client, on top of a real consensus cluster, is the practical default this analysis recommends if Nexus keeps a per-subject vault at all; on-premise-only, single-site clients are the one case where live threshold custody earns its cost rather than merely adding it. Moving per-subject keying to the Silver-load boundary is worth adopting regardless of topology, since it removes a dependency Bronze's own design goals never asked for.

The deeper alternative — eliminating per-subject encryption entirely — is where this analysis leans for practicality and long-term maintainability: it is the only option that doesn't just harden the single most catastrophic point of failure in Nexus, it removes it. But it does so by trading away defense-in-depth and by removing Annex A's GDPR erasure mechanism outright, and neither of those is this document's decision to make. Until Annex H's leadership amendment process says otherwise, Annex A.1 and Annex E.2 remain Nexus's authoritative, governing mechanism — this document is the case for reconsidering them, not a replacement for them.
