# ETL & Transformation Tooling at Nexus

*Companion document to* `Data_Principles.md` *D4 (The right tool for the right job) and O4 (Modules communicate through events). Nexus works in batch, event-driven and real-time modes; this document explains why each needs its own tool — Apache Airflow, dbt and Apache Flink. Also connects concretely to* `Golden_Triad_Data_Boundaries.md` *and* `Data_Scalability_Problems.md` *(the CDC/outbox mechanism these tools actually run), and* `Apache_Iceberg.md` *(the maintenance jobs and streaming writes these tools are responsible for executing). Where* `Foundations.md` *Annex F already establishes that data-quality checks live as dbt tests, that mechanism is cited here, not re-argued.*

**Part:** 3 — How it is built · **Document:** 18 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

Nexus processes data in three modes — batch, event-driven, and real-time — and one universal tool can't cover all three. This document makes that case, then argues each tool's specific selection: Airflow over Dagster, Prefect, and cloud-native orchestrators for batch and event-driven work; dbt paired with Airflow — not either alone — for SQL-first transformation with governance and lineage built in, not bolted on; and Flink over Kafka Streams, Spark Structured Streaming, and ksqlDB for the streaming case specifically. It closes with the division of labor these three tools actually form together, and a worked example tracing one citizen record through all of it.

## **Why Three Computational Models Need Three Different Tools**

Batch, event-driven, and streaming aren't three schedules of the same computation — they're three different computational models, and treating them as interchangeable is where the tooling mistakes start:

* **Batch** — bounded input, a known start and end, a DAG of discrete dependencies between jobs ("run Silver after Bronze finishes for the day"), optimized for throughput over latency.
* **Event-driven** — unbounded but discrete individual events, typically reactive rather than continuous: something happens, a workflow triggers. Annex A.4's cascading erasure propagation is exactly this shape.
* **Streaming** — unbounded and continuous, requiring stateful processing over time — windowed aggregations, joins across streams, watermarking for events that arrive out of order — with exactly-once or at-least-once guarantees and a genuinely low latency floor.

Forcing one tool to cover all three produces a predictable failure: a batch scheduler faking streaming via short-interval polling pays real latency and overhead cost for something that was never actually continuous processing, or a stream processor gets pressed into service as a general cross-system job orchestrator it was never built for. This is the same "wrong layer for the job" shape `Data_Scalability_Problems.md`'s war stories already documented, applied to tooling instead of storage.

## **Orchestrating Batch & Event-Driven Work: Airflow vs. Alternatives**

| | Airflow | Dagster | Prefect | Cloud-native (Step Functions, Composer, ADF) |
| --- | --- | --- | --- | --- |
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 (Core) | Proprietary |
| Governance | Apache Software Foundation | Single-vendor (Dagster Labs) | Single-vendor (Prefect) | Single cloud provider |
| Ecosystem / operators | Largest by far — thousands of pre-built integrations | Smaller, growing | Smaller | Deep within one cloud, none outside it |
| On-premise / cloud-agnostic fit | Runs anywhere | Runs anywhere | Runs anywhere | Locked to one cloud |
| Conceptual model | DAG of tasks — familiar, well-trodden | Asset-centric — stronger DX, a real relearn for DAG-trained teams | Dynamic, Pythonic flows | Provider-specific |

Cloud-native orchestrators are excluded before features even enter the comparison: Data Principles P1 (Deploy anywhere) commits Nexus to running on-premise as a first-class deployment target, and a cloud-only orchestrator is disqualified by that alone, the same way `Golden_Triad_Data_Boundaries.md` ruled out anything that couples Nexus to infrastructure a client might not have. Between Airflow, Dagster, and Prefect, license isn't the differentiator — all three are genuinely Apache 2.0. The real difference is ecosystem maturity and operational track record at real scale, where Airflow remains the clear incumbent: the largest operator library, the deepest bench of engineers who already know it, and the most-tested backfill, retry, and alerting semantics of any option here.

**Verdict:** Airflow, for batch and event-driven orchestration both.

## **dbt + Airflow: Governance, Lineage, and Why SQL-First**

dbt has no scheduler of its own. `dbt run` and `dbt test` don't know *when* to run, and dbt has no concept of "wait for Bronze ingestion to land before starting" — that's a cross-system dependency, and dbt's world is internal to the warehouse. Airflow owns the *when* and the cross-system dependency graph; dbt owns the *what* — the transformation logic itself, plus its own internal dependency graph between models. This is the same "one system, one job" separation this documentation set keeps returning to, applied to transformation instead of storage or access control.

**Why SQL-first, specifically:** SQL is the one language every analyst, analytics engineer, and BI engineer at Nexus already knows. Routing routine Silver/Gold transformations through SQL rather than requiring a Python or Scala job for every model lowers who can safely contribute a transformation, without lowering the bar on correctness — dbt models are still reviewed, tested, and version-controlled exactly like code, because they *are* code.

**Governance and lineage aren't bolted onto dbt for Nexus — they're already load-bearing elsewhere in this documentation set.** Annex F.1 already establishes that data-quality rules live as dbt tests attached directly to Silver/Gold models, traveling in the same pull request as the model change rather than living in a separate DQ platform that can drift out of sync. dbt's `ref()` and `source()` macros build dbt's own internal dependency graph as a side effect of writing normal transformation SQL — that graph is what feeds column-level lineage into OpenMetadata, not a separate lineage mechanism someone has to maintain by hand.

**Why dbt *and* Airflow, not dbt alone:** Astronomer Cosmos — a real, specific integration, not an abstract claim — turns a dbt project into individual Airflow tasks, one per model, instead of one opaque "run dbt" black box. That means per-model retries, per-model observability, and per-model lineage inside Airflow's own UI, not just dbt's — the orchestration layer and the transformation layer stay separate concerns, but neither loses visibility into the other.

## **Streaming Transformation: Flink vs. Alternatives**

| | Flink | Kafka Streams | Spark Structured Streaming | ksqlDB |
| --- | --- | --- | --- | --- |
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 | Confluent Community License — source-available, not OSI-approved, restricts competing SaaS use |
| Processing model | True stream-native, per-event | True stream-native, per-event | Micro-batch under the hood (a continuous mode exists, but is less mature and less widely used) | True stream-native, SQL-only |
| Scope | Full programmatic API *and* SQL, rich connector ecosystem including Iceberg | Kafka-to-Kafka only — an embedded library, no external connectors | Broad ecosystem via Spark, but a higher latency floor than true stream-native processing | Kafka-to-Kafka only, SQL-only, simpler processing model |
| Fit for Nexus | First-class Kafka *and* Iceberg connectors | Can't reach Iceberg at all | Legitimate and broadly adopted, but the wrong latency profile for real-time work | Confluent-centric, license friction, more limited processing sophistication |

Kafka Streams is disqualified quickly — it's a fine choice for a simple transform embedded in one microservice, but it cannot write to Iceberg or reach any system outside Kafka, which rules it out for anything touching Bronze directly. Spark Structured Streaming is a real, popular option, but it's architecturally micro-batch under the hood even where a "continuous" mode exists, and Nexus's real-time mode needs an actual latency floor, not a very short batch interval wearing a streaming label. ksqlDB's SQL-first approach is appealing — the same instinct that makes dbt the right call for batch — but the Confluent Community License is the same BSL-shaped restriction this documentation set already flagged for Vault, and its processing sophistication doesn't match Flink's for anything beyond simple stream-to-stream transforms.

**Flink wins for two concrete reasons, not an abstract "most powerful" claim:** first-class Kafka integration — Nexus's own committed message broker (`Broker_Messages_Services.md`) — and first-class Iceberg integration (`Apache_Iceberg.md`), meaning one engine owns the entire Kafka-to-Bronze/Silver streaming path with real exactly-once guarantees end to end, not two half-solutions stitched together.

## **The Division of Labor**

Three tools, three jobs, none of them standing in for the other:

* **Kafka → Flink → Bronze/Silver** — continuous, low-latency ingestion and light real-time enrichment, written directly into Iceberg tables with exactly-once semantics.
* **Bronze/Silver → dbt → Silver/Gold** — batch SQL transformation, tested and lineage-tracked as part of the same change, executed by whatever engine sits under the warehouse.
* **Airflow, underneath both** — scheduling and monitoring the Flink jobs, triggering dbt runs on the right cross-system cadence, running the CDC relay jobs from `Golden_Triad_Data_Boundaries.md` and `Data_Scalability_Problems.md`, and running the Iceberg maintenance procedures from `Apache_Iceberg.md`. One orchestrator, visible in one place, over everything else that has its own, narrower job.

## **Diagram**

![ETL and transformation tooling division of labor: Kafka feeding Flink for continuous streaming writes into Bronze/Silver Iceberg tables, dbt performing batch SQL transformation from Bronze/Silver into Silver/Gold with tests and lineage, and Airflow orchestrating both paths plus CDC relay and Iceberg maintenance jobs](ELT-ETL_Orchestration_Tooling.png)

*Diagram: three tools, three computational models, one orchestrator visible over all of it. (Editable source: `ELT-ETL_Orchestration_Tooling.drawio`.)*

## **Worked Example: One Citizen Record, Through the Whole Pipeline**

A citizen updates their address through the Backend app.

1. **CDC.** Debezium captures the committed row change from Backend's write-ahead log (`Golden_Triad_Data_Boundaries.md`, Grey Area 1) and publishes it to Kafka — no application code involved.
2. **Streaming write.** A Flink job, orchestrated and monitored by Airflow, consumes that Kafka topic continuously and writes the change into the Civil Registry Dominion's Bronze Iceberg table, exactly once, within seconds.
3. **Batch transformation.** On its scheduled cadence, Airflow triggers the dbt run (via Cosmos, as individual per-model tasks) that shreds Bronze into Silver's `Citizen Satellite` — partitioned and sorted exactly as `Apache_Iceberg.md`'s worked example specifies — running dbt's schema tests (Annex F.1) in the same run, and updating OpenMetadata's lineage graph as a side effect of the `ref()`/`source()` macros already in the model.
4. **Gold aggregation.** A second, dependent dbt run, also Airflow-triggered, folds the updated Satellite into the `Subject 360` Gold view other Dominions read.
5. **Maintenance, on its own schedule.** Independently, Airflow runs the Iceberg `rewrite_data_files` and `expire_snapshots` procedures against the Satellite table, keeping file sizes and snapshot retention within the bounds `Apache_Iceberg.md` already specifies for this table.

Five steps, three tools, each one doing only the job it's actually built for — and the same Airflow instance is the one place a person can see all five of them at once.

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| Each tool is used for exactly the computational model it was built for | No batch scheduler faking streaming, no stream processor pressed into cross-system orchestration |
| Governance and lineage are side effects, not separate systems | dbt tests and OpenMetadata lineage come from the same `ref()`/`source()`/test definitions already written for the transformation itself |
| One visible orchestration layer over three narrow tools | Airflow's UI is the one place to see CDC relay, streaming jobs, batch transforms, and Iceberg maintenance together, without any of those systems needing to know about the others |
| Every choice traces to a concrete Nexus fact, not an abstract feature comparison | Flink wins on Kafka and Iceberg integration specifically; Airflow wins on ecosystem depth and on-premise fit specifically — not generic "most powerful" claims |

## **Honest Trade-Offs**

| Trade-off | The real cost |
| --- | --- |
| Three tools is three operational surfaces, not one | Airflow, dbt, and Flink each have their own failure modes, their own upgrade cycles, and their own on-call burden — consolidation would be simpler to operate, if it were actually possible to do the job with one tool |
| Airflow's DAG-of-tasks model is a real conceptual cost for teams trained on asset-centric thinking | Dagster's model is arguably a better fit for teams starting fresh; choosing Airflow trades some developer experience for ecosystem maturity and hiring pool depth |
| dbt's SQL-first default doesn't cover everything | Some transformations are genuinely better expressed in Python (complex ML feature engineering, for instance) — SQL-first is the default, not an absolute rule, and dbt's Python model support exists specifically for the cases where it isn't |
| Flink's operational complexity is real | Checkpointing, state backends, and exactly-once semantics are powerful but non-trivial to run correctly — this isn't a drop-in replacement for a simpler consumer, it's a genuine distributed system with its own failure modes to operate |

## **Verdict**

The answer to "why these three tools" isn't "pick the most popular tool in each category." Airflow wins because Nexus's own environment-agnostic mandate rules out the cloud-native alternatives before features even enter the comparison, and because ecosystem depth matters more than a modern conceptual model at Nexus's actual operating scale. dbt paired with Airflow, not either alone, is what turns SQL-first transformation into something with governance and lineage as side effects of writing the transformation itself, not a second system to keep in sync. And Flink wins the streaming case for the same reason Iceberg won the storage case in the previous document: not abstract technical superiority, but first-class integration with the two systems — Kafka and Iceberg — Nexus already committed to independently of this choice. Three tools, three computational models, and the division of labor between them is the actual architecture — not a detail underneath it.
