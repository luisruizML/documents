# **Glossary**

**Part:** Glossary · **Document:** 22 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-30

*Every term used across the Nexus documentation set, in plain language. Terms are grouped by theme; each one points to the document where it is explained properly. New to the set? Start with* `Welcome.md`*.*

## **Suite and business**

| Term | Meaning | Explained in |
| --- | --- | --- |
| **AEOI (Automatic Exchange of Information)** | The international standard under which financial institutions report accounts held by foreign tax residents, for exchange between tax authorities. | `Data_Layer_Overview.md` |
| **Any legislation, zero custom development** | The suite's organising constraint: a new country, rate or rule is configuration, never a code change. | `Data_Layer_Overview.md` |
| **API (application programming interface)** | A defined way for one system to ask another for data or a service. | `Data_Layer_for_Engagement.md` |
| **Architecture Retreat** | The architecture meeting (7–9 October) where the open decisions in the Data Principles are settled. | `Data_Principles.md` |
| **Architecture Review Board** | The body that adopts and enforces the Data Principles. Its approval is what moves a document to version 1.0. | `Data_Principles.md` |
| **Baseline** | The measured value of a signal before a change, so the effect of the change can be shown. | `Data_Layer_Problems.md` |
| **Core** | An abstraction, not one system: the place where a decision is owned and recorded. | `Data_Layer_for_Record.md` |
| **Domain event** | A record that something happened — *an assessment was issued* — which other modules can react to. | `Data_Layer_for_Record.md` |
| **Engagement, Record, Insight** | The three types of system in PSS 3.0: what people touch, what decides and keeps, what we learn. | `Data_Layer_Overview.md` |
| **Golden Triad** | The three parts that share every process in a domain: Front-end, Backend and Nexus. Each process step has exactly one responsible part. | `Golden_Triad_Data_Boundaries.md` |
| **Modulith** | One deployable system divided internally into modules with clear boundaries and explicit contracts. | `Data_Layer_for_Record.md` |
| **Nexus** | The data layer of the suite: it provides analytic services to Engagement, Record and Insight alike, and is the bond between them. | `Data_Layer_Overview.md` |
| **PSS 3.0 (Public Services Suite)** | Blyce's product suite for public administrations, organised as three system types across seven value streams. | `Data_Layer_Overview.md` |
| **PVD (Product Vision & Design)** | The unit — product owners, business analysts, UX designers and architects — the Part 1 documents are written for. | `Welcome.md` |
| **Read model** | A view prepared in advance for one screen, so it can be shown instantly without the screen keeping its own copy. | `Data_Layer_for_Engagement.md` |
| **TIN (taxpayer identification number)** | The number that identifies a taxpayer; duplicated TINs are a common data-quality problem. | `Data_Layer_for_Record.md` |
| **Value stream** | One of the seven columns of the suite: Platform & Configuration, Registries, Taxation/Licenses/Contribution, Benefits, Finance, Compliance, AEOI. | `Data_Layer_Overview.md` |

## **Data modelling and organisation**

| Term | Meaning | Explained in |
| --- | --- | --- |
| **Bronze, Silver, Gold** | The three layers of the Medallion Architecture: raw data as it arrived; cleaned, typed and resolved data; data shaped for a specific use. | `Medallion_Architecture.md` |
| **CDC (change data capture)** | Capturing every committed change in a database as an event, without the application having to publish it. | `Golden_Triad_Data_Boundaries.md` |
| **Data Mesh** | An organisational model in which each domain owns its data as a product, on a shared platform. | `Lakehouse_Architecture.md` |
| **Data product** | A dataset with a named owner, a declared quality level and a service level, published for others to use. | `Foundations.md` |
| **Data Vault 2.0** | A modelling method built from Hubs, Links and Satellites; new requirements add to the model instead of changing it. | `Data_Vault_2.0.md` |
| **Dominion** | Nexus's unit of data ownership: a bounded domain mapped to one accountable team. | `Foundations.md` |
| **Identity resolution** | Deciding which records in different registers belong to the same person or business — without merging them. | `Foundations.md` |
| **Lakehouse** | Cheap object storage plus a table format that adds transactions, schemas and history. | `Lakehouse_Architecture.md` |
| **Objects, relationships, enrichment** | The things that exist, how they connect, and what we learn about them over time — Hubs, Links and Satellites in Data Vault terms. | `Data_Layer_Problems.md` |
| **Outbox pattern** | A backend writes the event it wants to publish into its own table in the same transaction as the change; a relay publishes it. | `Golden_Triad_Data_Boundaries.md` |
| **Subject 360** | The resolved, cross-register view of one person or business. | `Foundations.md` |
| **Survivorship** | The rules that decide which source is authoritative for each field when records are resolved together. | `Foundations.md` |

## **Trust, privacy and access**

| Term | Meaning | Explained in |
| --- | --- | --- |
| **Certification Gate** | A data product may be used outside its owning Dominion only after its owner certifies it. | `Foundations.md` |
| **Crypto-shredding** | Erasing personal data by destroying the key that encrypts it, so the data stays in place but can never be read again. | `Encryption_Key_Custody.md` |
| **DEK (data encryption key)** | A key that encrypts one subject's personal data; destroying it is how that data is erased. | `Encryption_Key_Custody.md` |
| **DLC (Data-Level Controls)** | Nexus's row-by-row access control, decided by following relationships in a graph. | `Data_Level_Controls.md` |
| **Legal Hold** | A legal obligation (tax, fraud, litigation) that blocks the erasure of a specific subject's data. | `Foundations.md` |
| **Lineage** | The traceable path from a figure back to the transformations and sources that produced it. | `Data_Catalog.md` |
| **Maker-checker** | Two different people are needed for a sensitive action: one requests, another approves. | `Foundations.md` |
| **PII (personally identifiable information)** | Personal data — anything that identifies a person. It is kept safely, not conveniently. | `Data_Principles.md` |
| **RBAC, ABAC, ReBAC** | Access control by role, by attribute, or by relationship. Nexus uses relationships (ReBAC). | `Data_Level_Controls.md` |
| **Tokenization** | Replacing a sensitive value with a meaningless token; the mapping back is held separately. | `Foundations.md` |

## **Reliability and operations**

| Term | Meaning | Explained in |
| --- | --- | --- |
| **ACID** | The four guarantees of a reliable write: all or nothing, always valid, isolated from other writes, and permanent once done. | `Lakehouse_Architecture.md` |
| **Annex** | A numbered section (A–H) of Technical Foundations describing one mechanism in detail. | `Foundations.md` |
| **Correlation ID** | An identifier carried through every step of a request, so it can be followed end to end. | `Foundations.md` |
| **RPO / RTO** | How much data may be lost (recovery point objective) and how long recovery may take (recovery time objective). | `Foundations.md` |
| **SLI / SLO** | A measured signal of service quality (indicator) and the target it must meet (objective). | `Foundations.md` |
| **Tier** | The service class of a data product — 1 real-time, 2 operational batch, 3 analytical — which sets its targets. | `Foundations.md` |
| **Time travel** | Querying a table as it was at a past moment, because every change is kept as a snapshot. | `Lakehouse_Architecture.md` |

## **Technology**

| Term | Meaning | Explained in |
| --- | --- | --- |
| **Airflow** | Schedules and monitors batch and event-driven work. | `ELT-ETL_Orchestration_Tooling.md` |
| **dbt** | Transformations written in SQL, with tests and lineage built in. | `ELT-ETL_Orchestration_Tooling.md` |
| **Debezium** | Reads a database's transaction log and publishes each change to Kafka (CDC). | `Golden_Triad_Data_Boundaries.md` |
| **Flink** | Processes continuous streams of events with low latency. | `ELT-ETL_Orchestration_Tooling.md` |
| **Hexagonal Architecture (ports and adapters)** | Business logic in a protected core; every technology plugs in through an adapter at the edge. | `Hexagonal_Architecture.md` |
| **Iceberg** | The open table format Nexus stores its Lakehouse tables in. | `Apache_Iceberg.md` |
| **IaC (Infrastructure as Code) / Terraform** | Environments defined in versioned files and built by running them — never by hand. Terraform is the tool. | `IaC_Terraform.md` |
| **Kafka** | The event backbone: a replayable log many consumers can read at their own pace. | `Broker_Messages_Services.md` |
| **Kubernetes** | Runs Nexus's workloads the same way on any cloud or on-premise. | `Kubernetes.md` |
| **ML (machine learning)** | Models that learn from data — for example, to assess prerequisites for a go / no-go decision. | `Data_Layer_for_Record.md` |
| **Neo4j** | The graph database behind identity resolution and Data-Level Controls. | `Data_Level_Controls.md` |
| **OpenBao** | The open-source key vault recommended for holding encryption keys. | `Encryption_Key_Custody.md` |
| **OpenMetadata** | The data catalog: what exists, who owns it, where it came from, and whether it is certified. | `Data_Catalog.md` |
