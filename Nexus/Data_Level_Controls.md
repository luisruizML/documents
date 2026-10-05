# Data-Level Controls at Nexus

*Companion document to* `Data_Principles.md` *T4 (Personal data is kept safely, not conveniently) and O1 (One authoritative place per fact), and to* `Medallion_Architecture.md`*, whose Silver layer is governed by Data-Level Controls (DLC), filtered by Dominion and Role. This document expands on what DLC actually is: not a role list, but a mechanism, and argues specifically why that mechanism has to be relationship-based, not attribute- or role-based, given what Nexus already commits to elsewhere in this documentation set.*

**Part:** 3 — How it is built · **Document:** 19 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

Silver-layer access control is usually stated in one clause: "governed by Data-Level Controls (DLC), filtered by Dominion and Role." `Medallion_Architecture.md` illustrates it with a worked example — a BI Engineer from one Dominion can read a Gold view; the same BI Engineer from a different Dominion may not, unless that data has been certified for cross-Dominion consumption. What that clause does not say is *how* "filtered by Dominion and Role" actually gets decided for one specific row, for one specific request, at one specific moment — and that mechanism is not obvious. Dominion and Role are not static labels stapled to a user; they are a legal state (is there an active Legal Hold on this exact subject, Annex A.3), a governance state (has this Dominion certified this product for outside consumption, Annex C.6), and a relationship that shifts as identity resolution runs (Annex B). None of that is expressible as a fixed lookup table.

The short version of the argument: Role-Based Access Control (RBAC) is the obvious first answer, and it is the wrong one for Nexus — it turns every Dominion × condition combination into a role someone has to hand-maintain, and it has no way to notice when the underlying relationship graph changes. Attribute-Based Access Control (ABAC) is a real improvement, but it still treats Dominion ownership as a static attribute on a resource rather than a resolved relationship. Relationship-Based Access Control (ReBAC) is the right shape of question — "can this user reach this data through an unbroken, ungated chain of relationships" — and Nexus can implement it without standing up new infrastructure: as graph traversal queries against the same Neo4j knowledge graph Nexus already uses for identity resolution (Annex B). DLC becomes a query pattern against a graph that already exists, answering a second question with the same relationships that answer the first.

## **Why RBAC Is Insufficient**

RBAC assigns permissions to static, coarse-grained buckets: a user has a role, a role has a set of permissions, and "can this user read Silver" is answered by checking bucket membership. This is the model most systems reach for first because it is simple to reason about and simple to implement — and it is precisely that simplicity that breaks under Nexus's actual access question.

The access question for any given Silver row is not one condition. It is several, evaluated together, for that row, at that moment:

* **Dominion match.** Does the requester's Dominion own this row, or has the requester's Dominion been granted certified cross-Dominion access to the owning Dominion's data product (Annex C.6)?
* **Legal Hold state.** Is there an active Legal Hold on this specific subject (Annex A.3) that should suppress visibility regardless of the requester's role — a state that can appear or disappear on a subject-by-subject basis, independent of anything about the requester?
* **Certification state.** If this is a cross-Dominion request, has the owning Dominion actually certified this data product for outside consumption yet, or is certification still pending?

RBAC has exactly one lever to pull against all three of these at once: define more roles. "BI Engineer, Civil Registry, no active hold, certified consumer" is a role. So is the same thing for the Tax Dominion. So is every other Dominion, crossed with every combination of hold state and certification state that might apply. This is combinatorial by construction — the number of roles needed grows with the product of Dominions and conditions, not the sum, and every one of those roles is a row a human has to create, name, and remember to retire.

That maintenance burden compounds with a second problem, specific to Nexus: RBAC is a static, human-curated list sitting next to a graph of relationships (Annex B) that changes continuously. A `SAME_AS` edge gets confirmed between two `LocalIdentity` nodes, and the subject those two records represent is now, correctly, one entity instead of two — but no RBAC role knows that happened. Roles don't subscribe to the identity graph. Someone has to notice the resolution occurred and go update the access rule by hand, or — far more likely in practice — nobody does, and the role list quietly drifts out of sync with what the graph actually says is true.

## **Evaluating ABAC**

Attribute-Based Access Control is a real step forward from RBAC, and it deserves credit as one: instead of a fixed role bucket, a policy engine evaluates a rule against attributes at query time — something like `user.dominion == resource.dominion AND user.role IN [...] AND NOT resource.legal_hold_active`. This collapses the combinatorial role explosion RBAC produces. One policy, evaluated per request, replaces a role for every Dominion × condition combination — Legal Hold and certification state become attributes checked in the same rule instead of separate roles to maintain.

The trade-off that shows up as the attribute and condition count grows is a familiar one: the policy set itself becomes sprawling and hard to audit. A rule engine with dozens of attributes and nested conditions is not meaningfully easier to reason about than the role list it replaced — it has just moved the complexity from "which role" to "which rule fired, and why."

But the trade-off that actually matters for Nexus specifically is more fundamental: ABAC still treats `resource.dominion` — "does this data belong to my Dominion" — as a static attribute lookup on the resource. That is exactly the assumption Annex B breaks. A citizen's data doesn't sit under one fixed Dominion label forever; which Dominion's record is authoritative for a given subject, and which other Dominions have a resolved relationship to that same subject, is something identity resolution decides and can revise as `SAME_AS` matches are confirmed, disputed, or reversed (Annex B.4). ABAC's attribute model has no natural place to put "this is true because of a relationship the graph resolved, and that resolution can change." It can only re-check a flag that something else has to remember to update — the same maintenance gap RBAC had, one level more sophisticated.

## **Evaluating ReBAC**

Relationship-Based Access Control decides access by traversing relationships between the requester and the resource, rather than by looking up a role or an attribute. The access question becomes: does a path exist connecting this user to this resource, through the specific relationship types that constitute permission, with no relationship on that path that constitutes a block?

This is conceptually the closest fit to Nexus, because Nexus's actual access questions are already relationship questions, not attribute lookups, once they're stated precisely:

* "Does this user's Dominion own this subject's data" is not an attribute check — it's asking whether an **IS-OWNER-OF** relationship exists between a Dominion node and a Subject node.
* "Has this Dominion been granted cross-Dominion access" is asking whether a **CERTIFIED-FOR** relationship exists between the requesting Dominion and the data product (Annex C.6).
* "Is there a reason to block this specific subject regardless of who's asking" is asking whether a **HAS-ACTIVE-HOLD** relationship exists on the Subject node (Annex A.3).

None of these are properties of the user or properties of the resource in isolation. They are edges in a graph — the same kind of edge Annex B already uses to answer "is this the same citizen."

## **The Graph-Inspired Model: ReBAC on the Identity Graph Nexus Already Has**

The decision Nexus makes is not "adopt ReBAC as an abstract pattern" — it's "implement ReBAC as graph traversal queries against the same Neo4j knowledge graph Nexus already uses for citizen-to-institution mapping." A permission check is a traversal query: does a path exist from this **User** node, through a **HAS-ROLE** edge, through a **BELONGS-TO** edge to a **Dominion** node, to an **IS-OWNER-OF** edge reaching this **Subject** node — with no **HAS-ACTIVE-HOLD** node breaking that path, and, if the requesting Dominion differs from the owning Dominion, a **CERTIFIED-FOR** edge (Annex C.6) satisfied along the way?

The argument this document is actually making is narrower, and stronger, than "graphs are good at relationships in general": this is not a new system bolted onto Nexus for the sole purpose of access control. Annex B already stands up a Neo4j graph of `LocalIdentity`, `Subject`, and `SAME_AS` nodes and edges to answer "is this the same citizen recorded by two different Dominions." DLC extends that same graph with a small number of additional node and edge types — User, Role, Dominion, Legal Hold, and the relationships between them — and answers a second question against it: "can this user see this citizen's data." Both questions are relationship-traversal questions over the same underlying entities, in the same store, maintained by the same operational discipline. When a `SAME_AS` edge is confirmed and a Subject's ownership resolves differently, the very next permission check against that Subject sees the new graph state automatically — there is no separate access-control record that has to be told the identity graph changed, because there was never a separate copy of the fact to begin with.

![Data-Level Controls: Graph Traversal Access Check — an allowed path (User A, green) traverses has-role, belongs-to, and owns edges to a Subject node, while a blocked path (User B, red dashed) is intercepted by a Legal Hold node before reaching the same Subject](Data_Level_Controls.png)

*Editable source: `Data_Level_Controls.drawio`.*

## **Worked Example: The BI Engineer, Extended**

`Medallion_Architecture.md` sets up the scenario at a high level: a BI Engineer from one Dominion queries a Gold view that includes data another Dominion contributed. This section is the mechanism underneath that one line.

**The request.** A BI Engineer in the Tax Dominion queries a `Subject 360` view (Annex B.5) that joins Tax filing data with Civil Registry address data for a given citizen — the same cross-Dominion join `Medallion_Architecture.md`'s Example 2 describes.

**The traversal that runs.** For the Civil Registry portion of that row, the graph is walked: User (this BI Engineer) → **HAS-ROLE** → Role (BI Engineer) → **BELONGS-TO** → Dominion (Tax) → does a **CERTIFIED-FOR** edge exist from Dominion (Tax) to the Civil Registry data product this query touches? → does a **HAS-ACTIVE-HOLD** node sit on this specific citizen's Subject node?

**What grants access.** The Civil Registry Dominion's owner (Annex C.2) has certified this specific data product for cross-Dominion consumption (Annex C.6), and no Legal Hold is active on this citizen. The traversal completes — every edge required for access exists, none of the blocking conditions do — and the row is returned.

**What denies access.** Either no `CERTIFIED-FOR` edge exists yet between the Tax Dominion and this Civil Registry product (certification hasn't happened, or was explicitly withheld), or a `HAS-ACTIVE-HOLD` node sits on this specific citizen's Subject — an active anti-fraud or litigation hold (Annex A.3) that should suppress visibility for this one citizen regardless of what the Tax Dominion is otherwise certified for. Either way, no complete path exists, and the row is withheld — not because the BI Engineer's role was wrong, but because the specific relationship the request depends on isn't there.

**What RBAC would have had to do instead.** One of two things, and both are the pattern this document opened with. Either a human maintains a dedicated role — "Tax BI Engineer, Civil-Registry-certified, hold-aware" — that has to be re-derived and re-assigned every time certification status or a citizen's hold status changes, which for a hold that can appear on any subject at any time is not a role change anyone can realistically track per-request. Or, far more likely under real deadline pressure, the fine-grained version gets judged impractical to hand-maintain and the team grants the Tax Dominion broad Silver-wide read access to Civil Registry data instead — which is exactly the failure mode Data Principles T4 and O1 exist to prevent, and exactly the outcome the Certification Gate (Annex C.6) was built to make impossible.

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| Reuses existing infrastructure | The Neo4j graph Annex B stands up for identity resolution is the same graph DLC queries — no new system to build, deploy, or operate |
| Access reflects the graph's current state automatically | A confirmed `SAME_AS` resolution, a newly certified data product, or a newly filed Legal Hold is visible to the very next permission check — no manual role update ever has to catch up to it |
| Composable with Legal Holds and the Certification Gate | Both are just additional node types and edge conditions on the same traversal — new access constraints extend the query, they don't require a new subsystem |
| One clear place for this kind of logic | Matches the Hexagonal Architecture principle already adopted at Nexus (`Hexagonal_Architecture.md`) of one obvious place for a given kind of rule — permission logic is graph traversal, in the graph, not scattered across role tables and application-layer `if` statements |

## **Honest Trade-Offs**

| Trade-off | The real cost |
| --- | --- |
| Traversal query latency at read time | A permission check is a live graph query, not a cached lookup. For Tier 1 data products (Annex D: p99 ≤ 300ms), that traversal has to fit inside the same latency budget as the rest of the request — this needs active query design and indexing, not an assumption that graph reads are free |
| Harder to answer "what can this user see" upfront | RBAC answers that question by reading a role's permission list — one query, one table. ReBAC answers it by enumerating every reachable path from that user through the graph, which is a materially heavier operation than reading a static list, and not something to run casually for every user on every page load |
| A bigger operational blast radius | Neo4j now sits behind two critical paths instead of one: identity resolution (Annex B) and every single permission check. A Neo4j outage doesn't just stall identity resolution — it blocks every DLC-governed read across Nexus, a larger failure surface than a simple RBAC lookup table would ever present |

## **Verdict**

"Governed by Data-Level Controls (DLC), filtered by Dominion and Role" states the goal, not the mechanism. RBAC is the mechanism most systems would reach for by default, and it is the wrong one here: Nexus's access question is multi-dimensional and continuously shifting in a way a static role list cannot track without becoming either unmaintainable or dangerously coarse. ABAC narrows the gap but still treats a resolved relationship as a static attribute. The right mechanism is DLC as graph traversal, on the same graph Annex B already builds for identity resolution. Not a second system Nexus now has to operate — the same relationships, answering a second question.

DLC's reach isn't Silver-only, and it isn't "every layer, uniformly," either — it tracks where resolved identity exists. Silver and Gold are both built on resolved `Subject` nodes, so the same traversal governs both: the Worked Example above is a Gold read (a `Subject 360` view, Annex B.5), and Gold's cross-Dominion case is that same traversal with one more required edge, `CERTIFIED-FOR` (Annex C.6). Bronze is a different case, not an exempt one — it still needs the correct permissions to access, it's just governed by a different, already-established mechanism: Bronze is raw and pre-resolution, so there is no `Subject` node yet for an `IS-OWNER-OF` or `HAS-ACTIVE-HOLD` edge to attach to, and a per-subject relationship traversal has nothing to traverse. DLC picks up exactly where resolved identity starts; what actually covers Bronze — encryption keyed per subject, plus a narrow role allowlist — is deliberately not re-explained here. It's sensitive enough to deserve one careful, complete explanation rather than a partial one repeated in every document that touches it — see `Encryption_Key_Custody.md`.
