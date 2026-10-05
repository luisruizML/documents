# Broker & Message Services at Nexus

*Companion document to* `Data_Principles.md` *O4 (Modules have explicit contracts and communicate through events) — Apache Kafka is the central nervous system for that event traffic — and to* `ELT-ETL_Orchestration_Tooling.md`*, which already argues why Flink over its streaming alternatives, in part because of Flink's first-class Kafka integration. This document evaluates Nexus's message-broker and event-streaming layer as a category, landing on Kafka specifically — the same treatment* `Apache_Iceberg.md` *gave storage and* `ELT-ETL_Orchestration_Tooling.md` *gave orchestration and transformation. It does what neither did: justify Kafka itself against its own alternatives, state its strengths and weaknesses honestly, and specify what has to be monitored for it to stay healthy.*

**Part:** 3 — How it is built · **Document:** 17 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

Nexus's message-broker and event-streaming layer has been assumed as Kafka everywhere it's mentioned in this documentation set — never independently justified, the same gap Iceberg and Flink had before their own documents. This document closes it: a comparison against Pulsar, Redpanda, RabbitMQ, and NATS JetStream on the axis that actually matters for Nexus — its replayable-log model, which is what makes the CDC pattern from `Golden_Triad_Data_Boundaries.md`, `Data_Scalability_Problems.md`, and `ELT-ETL_Orchestration_Tooling.md` work at all — followed by an honest strengths/weaknesses accounting and the specific monitoring Kafka needs to keep that promise.

## **Alternatives, Compared**

| | Kafka | Pulsar | Redpanda | RabbitMQ | NATS JetStream |
| --- | --- | --- | --- | --- | --- |
| License | Apache 2.0 | Apache 2.0 | Business Source License — source-available, not OSI-approved, converts to Apache 2.0 four years after each release | MPL 2.0 | Apache 2.0, CNCF-hosted |
| Core model | Distributed commit log, replayable | Log plus native queue semantics; compute (brokers) and storage (BookKeeper) run as two separate systems | Kafka-API-compatible, single binary, no JVM | Traditional AMQP queue — a message is gone once acknowledged, by default | Lightweight pub/sub with a persistence layer added on top |
| Multi-tenancy | Bolt-on via ACLs and quotas | Native — tenants and namespaces are first-class | Bolt-on, Kafka-compatible | Bolt-on (vhosts) | Bolt-on |
| Ecosystem | Largest by far — Kafka Connect, Debezium, a client library in every language | Smaller; Flink's Pulsar connector is real but nowhere near as mature as its Kafka connector | Kafka-API-compatible, inherits some of Kafka's own tooling | Mature, but built around queue-paradigm tooling, not log-paradigm | Small, growing |
| Fit for Nexus | Matches the CDC/event-sourcing replay pattern exactly | Two systems to run and reason about instead of one, on top of undercutting `ELT-ETL_Orchestration_Tooling.md`'s Flink decision, which leaned specifically on Flink's Kafka integration | License friction; the JVM-free operations story is real, but Kafka 4.0 fully removing ZooKeeper (KRaft-only now) narrows that gap | RabbitMQ Streams (a plugin since ~2021) does add log-like replay — this isn't an absolute paradigm gap — but it's a retrofit onto a fundamentally queue-first broker, less battle-tested for this exact pattern than Kafka's native model | Not proven at Kafka's scale for a platform-wide backbone role |

**Pulsar is the genuinely interesting alternative here, not a strawman.** Its native multi-tenancy actually resonates with Nexus's own Dominion model more directly than Kafka's bolted-on ACLs do. It loses on two independent grounds, not one circular one: running BookKeeper and Pulsar brokers as separate systems is a real operational cost regardless of any other decision, and choosing it would separately undercut the Flink integration `ELT-ETL_Orchestration_Tooling.md` already committed to.

**Verdict:** Kafka, specifically for the replayable-log model — multiple independent consumers (Flink for Bronze landing, a future audit consumer, a future ML feature pipeline) reading the same history at their own pace, never depleting it for each other, which is exactly what Documents 1, 2, and 4's CDC pattern depends on.

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| The replayable log is the mechanism, not a feature | It's what makes "multiple consumers, one history" work at all — the literal foundation the CDC pattern in `Golden_Triad_Data_Boundaries.md` is built on |
| Kafka Connect and Debezium | The exact mechanism `Golden_Triad_Data_Boundaries.md` Grey Area 1 recommends by default — not a separate integration to build |
| Proven at extreme scale, industry-wide | One of the most battle-tested distributed systems that exists — this isn't a claim unique to Nexus, it's inherited from a decade of production use elsewhere |
| Apache Software Foundation, clean Apache 2.0 | Same vendor-neutral governance story as Iceberg and Flink — no BSL-style restriction to navigate |
| KRaft removed the ZooKeeper dependency | A real operational simplification that happened independently of any choice Nexus made — one fewer distributed system to run per Kafka cluster |

## **Honest Weaknesses**

| Weakness | The real cost |
| --- | --- |
| Partition count is a largely one-way decision | Increasing partitions later is possible; decreasing isn't, and partition count affects both ordering guarantees and consumer parallelism — this needs real capacity planning up front, not a reactive fix |
| JVM operational overhead | Garbage collection tuning and heap sizing are real, ongoing tuning work, not a one-time setup step |
| Leans on OS page cache for performance | Underprovisioned memory degrades performance silently rather than failing loudly — a harder failure mode to catch than an outright crash |
| Multi-tenancy is bolted on, not native | Nexus's own Dominion isolation (Annex C) has to be layered on top deliberately via ACLs, quotas, and topic-naming discipline — Kafka doesn't deliver it as a first-class primitive the way Pulsar's namespace model does |
| Cross-cluster replication (MirrorMaker 2) is a bolt-on | Less elegant than Pulsar's native geo-replication — though for Nexus's per-client-dedicated-deployment model (Annex G.1), each client's Kafka cluster is already isolated by construction, which narrows how much this actually matters in practice |

## **Mandatory Monitoring**

Kafka's durability and freshness guarantees are only as real as what's actually watched. Four categories, not a flat list — matching how every other operational section in this documentation set is structured:

### **Durability & Replication**

* **Under-replicated partitions** — the single most important Kafka health signal. `UnderReplicatedPartitions > 0` means a partition's redundancy is currently degraded, and it's the first alert that should fire, before anything else.
* **ISR (In-Sync Replica) shrink rate** — a replica set shrinking below `min.insync.replicas` is a leading indicator that writes under `acks=all` could soon start failing, not yet an active failure.
* **Replication-factor configuration drift** — a preventive check, not a runtime metric: has a topic been created with replication factor 1, silently violating Nexus's own durability expectations? This needs a configuration-compliance check, not just a health dashboard.

### **Consumer Health & Freshness**

* **Consumer lag, converted to time, not message count** — Annex D's Freshness SLI is measured in seconds (Tier 1: ≤60s), and a raw "messages behind" number doesn't tell you whether that SLO is being met until it's translated into elapsed time against the producer's timestamps.
* **Producer-side error and retry rates** — a rise here can surface a networking or authorization problem between Nexus's ingestion adapters (Debezium, Flink) and the cluster before it's visible as broker-side degradation at all.

### **Capacity & Configuration**

* **Broker disk headroom against the configured retention window** — Kafka's durability model depends on holding data for its retention period; disk pressure either forces retention to truncate early (breaking the replay guarantee CDC and audit consumers depend on) or risks the broker refusing writes outright. This needs a headroom alert well before capacity is actually hit.
* **Partition count growth versus planned broker capacity, as a trend** — since partition count is a largely one-way decision, this needs to be watched as a trajectory, not just a point-in-time number, to catch a capacity-planning problem before it's a same-day emergency.
* **Schema registry health and compatibility-check failures** — CDC events need a stable, evolvable schema (Debezium typically emits through a schema registry). This is the same governed-schema-evolution theme `Data_Vault_2.0.md` and `Apache_Iceberg.md` already established, applied to the message layer instead of the storage layer.

### **Cluster Stability**

* **Active controller count** — exactly one, cluster-wide, at all times, true under KRaft's quorum controller the same way it was true under ZooKeeper's elected one. Zero or unstable controller election is a serious cluster-health signal, not a transient blip to ignore.
* **Leader distribution and unplanned leader-election rate** — uneven leader distribution means uneven broker load; frequent unplanned elections indicate broker instability worth investigating before it becomes an outage.

**Breach handling reuses what already exists, rather than inventing a parallel system:** these signals feed the same structured logging and Correlation ID infrastructure Technical Foundations mandates, and an SLO breach here follows Annex D.3's existing escalation path — three breaches in a rolling 30-day window escalating to Nexus leadership — the same mechanism every other Tiered data product's SLO breach already uses.

## **Diagram**

![Kafka monitoring dimensions: Durability and Replication, Consumer Health and Freshness, Capacity and Configuration, and Cluster Stability, each with its specific signals, feeding into the Technical Foundations observability and Annex D.3's SLO breach escalation](Broker_Messages_Services.png)

*Diagram: the four monitoring categories and their specific signals, feeding into infrastructure this documentation set already committed to — not a new alerting system. (Editable source: `Broker_Messages_Services.drawio`.)*

## **Verdict**

Kafka was never actually chosen in this documentation set — it was assumed, the same way Iceberg and Flink were before their own documents forced the comparison. Run against Pulsar, Redpanda, RabbitMQ, and NATS JetStream on the axis that matters — a replayable log multiple independent consumers can read at their own pace — Kafka wins on the same grounds Iceberg and Flink did: not abstract superiority, but the specific fit with a pattern Nexus already committed to independently (CDC, per `Golden_Triad_Data_Boundaries.md`). The weaknesses are real and worth stating plainly — partition planning, JVM overhead, bolted-on multi-tenancy — and the monitoring section exists precisely because none of Kafka's guarantees hold on their own; they hold only as long as under-replication, consumer lag, disk headroom, and controller stability are actually watched, through the same observability and escalation infrastructure this documentation set already built for everything else.
