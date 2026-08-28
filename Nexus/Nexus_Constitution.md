# **Nexus: Central Data Architecture & Constitution**

**Version:** 0.3.0 · **Status:** Draft · **Owner:** Nexus Leadership (see nexus_foundations.md, Annex C.4) · **Last Updated:** 2026-08-26
**Amendment Process:** See **nexus_foundations.md, Annex H: Document Governance**
**Companion Document:** `nexus_foundations.md` — the full technical mechanism behind every Annex referenced below.

## **Table of Contents**

1. Why the name "Nexus"?
2. Background
3. Motivations
4. Foundations
5. Basic Design Principles
6. Technologies and Methodologies
7. Observability and Operational Standards
8. Known Risks & Constraints
9. Glossary of Key Concepts

*Full engineering mechanisms for every Annex referenced throughout this document live in the companion file, `nexus_foundations.md`.*

## **Executive Summary**

Nexus is Blyce's central data architecture — the layer that turns data fragmented across institutions into a single, governed, trustworthy asset in service of the Blyce 2030 vision. It sits at the center of a deliberate three-part split, the "Golden Triad": Frontend and Backend stay simple and fast, while Nexus absorbs the complexity of synchronization, compliance, quality, and AI-readiness on their behalf.

This document sets out why Nexus exists, the principles it must never violate, and the technology it is built on — written for any stakeholder, technical or not. Every major risk identified in this Constitution — GDPR erasure conflicting with an immutable audit trail, the same citizen recorded differently by different institutions, vague performance promises, disaster recovery, data quality at scale, and where client data is legally allowed to live — now has a named, engineered mitigation, detailed in the companion document, `nexus_foundations.md`.

**Status:** Draft v0.3.0. Owned and amendable by Nexus leadership.

## **1\. Why the name "Nexus"?**

The word *Nexus* signifies a central connection point—the core where multiple complex elements meet and integrate.

In the context of the **Blyce 2030** vision, we are solving critical challenges: citizens losing time they can't afford, institutional inefficiencies draining morale, and legacy constraints that turn data into a barrier rather than an asset.

To overcome these hurdles, Nexus acts as our central nervous system for data. We achieve this by strictly separating responsibilities into a **"Golden Triad"**:

* **Frontend:** Focused purely on delivering a frictionless, highly responsive, secure, and feedback-rich user experience.  
* **Backend:** Dedicated exclusively to secure, high-speed operational transactions, keeping its data model as simple and lightweight as possible.  
* **Nexus (The Data Products Ecosystem):** The secure, modular, and schema-flexible engine that handles all the data heavy lifting. Whether an external partner calls our API, a frontend fetches a complex user state, or BI runs a quarterly report, they connect to this single, unified source of truth.

### **The Synchronization Challenge & Asynchronous Standard**

Because the operational backend is deliberately kept lightweight, the primary architectural challenge is the data synchronization pipeline between the Backend and Nexus.

To prevent bottlenecks and maintain the strict separation of the Golden Triad, **most services must run asynchronously**. Nexus is built to be multi-modal, fully capable of handling:

* **Batch jobs** for historical processing and large-scale aggregations.  
* **Event-driven** architectures for reactive microservices.  
* **Real-time** streams for immediate data availability.

### **Agnostic Deployment & Resource Efficiency**

Currently, analytics is prohibitively costly—draining time, IT capacity, and budgets. Nexus is designed to optimize and democratize this process. To achieve this, the architecture must be environment-agnostic. It is built to seamlessly deploy across **On-Premise** architectures and modern **Cloud Services**, ensuring it can adapt to whatever infrastructure constraints and security boundaries the client currently has. How data residency and tenancy are decided per client — and the default hybrid topology this implies — is defined in **nexus_foundations.md, Annex G: Multi-Tenancy & Data Residency**.

### **Pillars of Trust, Governance, and Future-Readiness**

Because Nexus is the ultimate source of truth, it must be governed by strict international and technological standards:

* **GovStack Alignment:** Nexus acts as the interoperable "Information Mediator," ensuring data can be securely shared across institutional boundaries using standardized, reusable civic building blocks.  
* **Compliance & Security by Design:** Built to natively support **ISO 27001/27002** and **SOC 2** standards through immutable audit trails, strict access controls, and transparent processing. It enforces **GDPR** at the root level via automated data masking, anonymization, and privacy-preserving pipelines.  
* **Data Governance:** Nexus relies on strict data stewardship, clear lineage, and automated quality controls to ensure it remains a pristine source of truth rather than a data swamp. The concrete, pragmatic mechanism behind these controls is defined in **nexus_foundations.md, Annex F: Data Quality**.  
* **The AI & Agents Foundation:** Advanced AI and autonomous agents cannot function on fragmented data. Nexus serves as the structured, high-quality fuel engine required to power Blyce's future AI capabilities.

## **2\. Background**

**Honoring the Foundation**

What we have built so far is exactly what has allowed us to reach this point. Our current systems work, and they serve as a highly effective starting point. We are not replacing a failure; we are evolving a success to meet the expanding demands of the Blyce 2030 vision.

**The Evolution of Data at Blyce**

Historically, our core operations have not been strictly "data-driven"—and that is perfectly fine. However, to go one step further, we must shift our paradigm. Instead of forcing our teams, citizens, and processes to adapt to rigid data structures, the data must adapt to *our* way of doing things.

**The Balancing Act: UX vs. Governance**

As we handle civic and institutional information, we face a critical balancing act. We must deliver a seamless, frictionless User Experience (UX) for all stakeholders—citizens, government bodies, and third parties—while simultaneously enforcing rigorous governance and maintaining audit-proof environments. Ultimately, the way we deal with data is how we enable and scale **trust**. Nexus is the architectural evolution required to ensure that trust is never compromised.

**Breaking the Monolith**

To achieve this scale, we are transitioning from a full monolithic architecture into three distinct layers—the Golden Triad (Frontend, Backend, Nexus). This shift is about establishing clear, non-negotiable boundaries of responsibility, while ensuring these three components work together seamlessly as a highly cohesive ecosystem.

**Embracing Imperfect Data & Radical Traceability**

We must accept a fundamental reality: data is not perfect, and it never will be. Mistakes will happen, and that is allowed. What is *not* allowed is losing visibility. To manage this, data becomes our key player in accountability. We must empower every user and administrator with the ability to "go back in time." This requires radical traceability—tracking exactly who did what, when, and why—ensuring that every action within our solution is fully auditable, deeply transparent, and reversible.

**Flexibility as a Strategic Catalyst**

Our current clients present us with a vast array of possibilities and highly varied constraints. Instead of viewing this demand for extreme flexibility as a problem to solve, we are treating it as a strategic opportunity. It gives us the precise environment needed to design a deeply adaptable Data Product—one that ultimately shapes and strengthens our entire core offering.

## **3\. Motivations**

**Abstracting the Complexity**

Public systems are inherently complex, but that complexity should never be the user's burden. Our primary motivation is to absorb and manage architectural intricacies deep within Nexus. By taking on the data heavy-lifting centrally, we free our Frontend and Backend layers to do what they do best. Ultimately, our job is to handle the systemic chaos so that citizens and government officials experience only simplicity, clarity, and ease of operation.

**Creating Tangible Value: Efficiency in Time and Resources**

We are not building technology for technology's sake. The shift to Nexus is driven by a mandate to create immediate, measurable value. Currently, extracting insights and managing data at an institutional level is costly—draining IT budgets, computing resources, and human capital. Nexus is motivated by the need to drastically reduce this friction, delivering a solution that optimizes resource allocation and gives citizens and civil servants their time back.

**Turning Data into an Enabler, Not a Barrier**

Historically, rigid data models and siloed information have acted as bottlenecks, slowing down feature development and limiting our clients' agility. We are motivated to flip this paradigm. Nexus will transform data from a constraint into a proactive enabler, allowing our clients to adapt their operations swiftly without being held back by underlying database limitations.

**Cultivating a Product-Driven, Agile Culture**

Technology alone will not get us to Blyce 2030; we must evolve our team into a highly focused, product-driven organization. We are motivated by a true agile mindset—one that relentlessly focuses on what creates value. We recognize that a product without user feedback is a product the client doesn't use. Therefore, measuring engagement and iterating rapidly based on real-world usage is a core driver for this architectural shift.

## **4\. Foundations**

To achieve our motivations, Nexus is built upon strict foundational pillars that dictate not just *what* we build, but *how* we build and operate it.

**Evolutionary Design and Safe Destructibility**

A product that is safe to break is a product that can evolve. We must build with evolution in mind, ensuring clear governance over changes while maintaining the flexibility to improve, create, or even destroy components safely. We embrace the future and the technologies that make our system unique, but we must do so in a way that allows us to iterate on mistakes and build up institutional knowledge systematically.

**Documentation and Testing as First-Class Citizens**

In a distributed, asynchronous architecture handling vast amounts of sensitive institutional data, documentation and testing are no longer optional best practices—they are more critical than ever. Rigorous, automated testing ensures our evolution does not break the core, and comprehensive, living documentation ensures the system remains understandable, maintainable, and verifiable across teams and over time.

## **5\. Basic Design Principles**

To operationalize our foundations, all engineering and architectural decisions within Nexus must adhere to the following technical principles:

**1\. API-First & Contract-Driven Interactions**

All data exposure—whether to external third parties, internal backend systems, or frontend services—must be handled via strict, versioned API contracts. This decouples downstream consumers from internal storage engines.

**2\. Asynchronous by Default**

To maintain the lightning-fast performance of the operational Backend, data synchronization and heavy processing within Nexus must occur asynchronously, natively supporting event-driven workflows, real-time streams, and batch jobs.

**3\. Immutability & Radical Traceability**

Because we accept that "data is not perfect," our core storage must be append-only and immutable. Data is never truly deleted or overwritten in the raw layer, providing a flawless audit trail and "time travel" capabilities. This principle coexists with GDPR's right to erasure through cryptographic rather than physical deletion — see **nexus_foundations.md, Annex A: GDPR Erasure Protocol** for the full mechanism.

**4\. Decoupled Compute and Storage**

Nexus must be designed to adapt to any environment, from strict On-Premise setups to elastic Cloud Services. By strictly separating storage from compute power, we can scale ingestion, processing, and API serving independently.

**5\. Strict Boundary Enforcement (Hexagonal Architecture)**

The API and serving layers will strictly isolate business logic from infrastructure components. Database adapters and external integrations must remain at the edge of the architecture. The full rationale — including its strengths, honest trade-offs, and why it is specifically necessary for a data product deployed across on-premise, cloud, and hybrid environments — is expanded in **`Hexagonal_Architecture.md`**.

**6\. Infrastructure as Code (IaC) as Mandatory**

To support flexible deployment models (On-Premise vs. Cloud) and evolutionary design, manual infrastructure configuration is prohibited. Every component of Nexus must be provisioned and managed strictly through code, ensuring reproducibility and security.

**7\. Agent-Driven Design**

Nexus is designed not just for human consumption, but for autonomous operations. The system must natively support **Agent-to-Agent (A2A)** communication protocols, while seamlessly facilitating **Human-in-the-Loop** workflows for critical oversight and governance approvals.

**8\. Rational and Pragmatic AI Utilization**

We embrace AI, but we do not chase hype. We enforce a strict "right tool for the job" philosophy and do not use resource-heavy GenAI models for tasks that can be solved deterministically. Specifically:

* **Linear Regression & Statistics:** Handled by traditional machine learning algorithms and math libraries, not LLMs.  
* **Well-Formatted PDFs:** Processed using standard, deterministic parsing libraries rather than costly, token-heavy AI vision models.  
* **Language Constraints:** We avoid or heavily restrict LLM usage in languages where the model lacks robust training data to prevent hallucinations and maintain absolute system trust.

## **6\. Technologies and Methodologies**

To execute on these principles, Nexus leverages a powerful open-source technology stack.

**Core Languages:**

* **SQL:** Originating in the 1970s and standardized in 1986, SQL boasts over 40 years of unmatched maturity. It is the absolute de facto standard for querying, transforming, and analyzing data across the industry.  
* **Python:** Created in 1991, Python is an Object-Oriented Programming (OOP) language that saw a massive surge in data science adoption starting in the late 2000s. It is universally compatible with almost every modern data technology. Crucially, **all Python development within Nexus must strictly utilize Pydantic**, ensuring rigorous data validation, typing, and serialization.

### **Data Modeling & Structuring**

* **Schema-Less Ingestion:** Initial data ingestion is highly flexible, capturing raw payloads as they occur to avoid blocking the Backend.  
* **Data Mesh & Domain-Driven Design (Dominions):** Data is decentralized into business domains (Dominions), treating data as a product with clear ownership. The operating model behind this ownership — roles, lifecycle, and dispute resolution — is defined in **nexus_foundations.md, Annex C: Dominion Governance**.  
* **Medallion Architecture with Strict Security:**  
  * **Bronze Layer (Raw):** Append-only, schema-less. **Security:** Fully encrypted. Access strictly limited to technical profiles (Architects, Data Engineers, Data Scientists).  
  * **Silver Layer (Cleaned):** Filtered and normalized. **Security:** Governed by Data-Level Controls (DLC), filtered by Dominion and Role. Accessed by BI and ML Engineers.  
  * **Gold Layer (Curated):** Business-level aggregations. **Security:** Strict filtering by Dominion and Role. Used for consumption APIs and reporting.  
* **Data Vault 2.0:** Handles complex, rapidly changing enterprise data models for auditing and extreme agility.

### **The Open-Source Core Stack (Compute & Storage)**

* **Unified Storage (Lakehouse, Relational, Document & Graph):**  
  * **Apache Iceberg & Delta Lake:** Lakehouse architectures for ACID transactions and "time-travel" on massive analytical datasets.  
  * **PostgreSQL:** The core engine for relational data in the Gold layer. Its unmatched extensibility (e.g., pgvector, PostGIS) and advanced analytical capabilities natively handle diverse structures (JSONB, Arrays).  
  * **Document DBs (MongoDB):** For highly flexible, unstructured serving, nested states, and caching.  
  * **Knowledge Graph DBs (e.g., Neo4j):** Essential for AI context. Stores complex relationships (e.g., citizen-to-institution mapping, hierarchical permissions) that traditional relational models struggle to query efficiently. It also serves as the substrate for cross-Dominion identity resolution — see **nexus_foundations.md, Annex B: Identity Resolution** for the full mechanism.  
  * **Unstructured Object Storage (S3 API Compatible):** The foundational storage layer for raw files (PDFs, Images, Video, Audio). This unstructured data is mapped via metadata into the Bronze layer to be processed by AI agents for text/feature extraction.  
* **Streaming Technologies:**  
  * **Apache Kafka:** The central nervous system for high-throughput, low-latency event ingestion.  
  * **Apache Flink:** For real-time streaming analytics and stateful computations on Kafka streams.  
* **Container Orchestration:**  
  * **Kubernetes:** The mandatory abstraction layer for both Cloud and On-Premise deployments, decoupling Nexus's compute workloads from any single physical machine, per §5.4 (Decoupled Compute and Storage). This is what allows an on-premise client's SLA targets (see **nexus_foundations.md, Annex D: Service Level Objectives**) to be benchmarked and scaled per-cluster rather than assumed from a cloud baseline.  
* **Batch Technologies:**  
  * **Apache Airflow:** Orchestration engine for managing complex batch DAGs.  
  * **dbt (Data Build Tool):** The core engine for SQL-based transformations and testing in Silver/Gold layers. Data quality checks live here as dbt tests rather than in a separate system — see **nexus_foundations.md, Annex F: Data Quality**.  
* **API & Serving Frameworks:**  
  * **FastAPI:** The primary framework for building high-performance REST APIs.  
  * **GraphQL / gRPC:** Supported alongside REST for flexible queries and high-speed microservice communication.

### **AI & Agents Ecosystem**

* **Agentic Frameworks:** **LangGraph** and the **Google GenAI SDK** for multi-step autonomous workflows.  
* **LLM Gateway (LiteLLM):** Centralized routing allowing seamless switching between **Local / On-Premise models** (for high-privacy citizen data) and **External Cloud Services** (for generalized reasoning).  
* **AI Observability:** **Langfuse** for tracing agent decisions and LLM outputs, ensuring transparency for the Human-in-the-Loop.  
* **Data Vigilante (OpenMetadata):** Acts as the semantic and governance backbone. It ensures that every asset is continuously documented, labeled, and tagged, providing AI agents with the pristine context they need to operate safely and accurately across the ecosystem.

## **7\. Observability and Operational Standards**

Nexus is designed to be fully observable. We cannot manage what we cannot measure. All components must adhere to strict operational standards:

* **Centralized Logging & Log Levels:** All services must output structured JSON logs to allow for automated querying and alerting. Log levels are strictly enforced:  
  * **DEBUG:** For detailed development tracing (disabled in production).  
  * **INFO:** For significant, successful operational state changes (e.g., pipeline completed).  
  * **WARN:** For recoverable errors or anomalies that require eventual attention.  
  * **ERROR:** For failures affecting a specific transaction or data load (requires alerting).  
  * **FATAL:** For complete system outages (requires immediate on-call paging).  
* **Distributed Tracing:** Every request entering the Golden Triad must be assigned a unique Correlation ID, allowing us to trace a single user action from the Frontend, through the Backend, and into the asynchronous Nexus pipelines.  
* **Performance & SLAs:** Nexus services are bound by strict Service Level Agreements (SLAs). While batch processing optimizes for throughput, API serving layers must optimize for latency, ensuring the Frontend never stalls waiting for analytical data. Concrete targets, tiers, and how they are measured — including the on-premise per-client benchmarking approach — are defined in **nexus_foundations.md, Annex D: Service Level Objectives**.  
* **Storage Lifecycle & Archiving:** We maintain a tiered storage strategy. Hot data (frequently accessed Gold layer) resides on high-performance compute. Cold data (historical Bronze layer logs, old unstructured PDFs) is automatically transitioned to cheaper, long-term archiving solutions, balancing cost with our radical traceability mandate.

## **8\. Known Risks & Constraints**

A resilient architecture requires a brutally honest assessment of its limitations and friction points. As we build Nexus, we must actively mitigate the following risks:

* **Infrastructure Overhead on On-Premise:** Deploying modern, distributed data components (Kafka, Spark, Lakehouses) in On-Premise environments introduces massive infrastructural overhead. Unlike the cloud, we lack instant elasticity. Capacity planning must be hyper-accurate to prevent systemic bottlenecks.  
* **Hardware Intensity for AI and Analytics:** Data manipulation and AI workflows are inherently resource-hungry. Intensive batch jobs, stream processing, and local LLM execution require significant RAM and GPU provisioning. If client hardware is under-specced, Nexus will degrade in performance.  
* **Security Key Management and Data Lock-out:** Because the Bronze layer is fully encrypted by design, the secure handling of encryption keys is an existential risk. We must build robust, automated backup and secure handover mechanisms for the client. If encryption keys are lost, the immutable data is permanently unrecoverable. Recovery targets, vault backup requirements, and the client's backup-destination obligation are defined in **nexus_foundations.md, Annex E: Disaster Recovery & Continuity**.  
* **The Cognitive Shift (Relational to Schema-less):** Moving a team from decades of strict Relational Database (RDBMS) design to a schema-less, event-driven, and Lakehouse mindset is a massive cultural hurdle. Without strict discipline and training, flexible ingestion can rapidly degrade into an unusable "data swamp."  
* **File Storage Criticality:** As we pivot towards unstructured data (media, PDFs) and Lakehouse formats (which rely heavily on Parquet files), our underlying Object File Storage becomes the absolute bedrock of the system. It is more critical than a traditional database disk; any instability here compromises the entire Nexus pipeline.  
* **Governance by Design as an AI Prerequisite:** We must ensure that every single schema change, new resource, or data domain is rigorously documented, labeled, and tagged via OpenMetadata. If we fail to maintain pristine metadata today, future AI agents will lack the semantic context required to navigate the Data Mesh, severely crippling our 2030 AI vision.

## **Glossary of Key Concepts**

Plain-language definitions of the recurring terms and proper nouns used throughout this document, for any reader — technical or not. Where a term is backed by a full technical mechanism, the pointer goes to the relevant Annex in `nexus_foundations.md`. Grouped by theme, alphabetical within each group.

### **Architecture & Structure**

* **API-First / Contract-Driven:** The rule that all data exposure — internal or external — happens through a strict, versioned API contract, so consumers never depend directly on internal storage. See §5.1.
* **Golden Triad:** The three-part architectural split of Frontend, Backend, and Nexus, each with a strictly separated responsibility. See §1.
* **GovStack:** An international framework of reusable, standardized civic technology building blocks that Nexus aligns with for cross-institution interoperability. See §1.
* **Hexagonal Architecture:** An architectural pattern that isolates business logic from infrastructure, keeping database adapters and external integrations at the system's edge. See §5.5 and `Hexagonal_Architecture.md`.
* **IaC (Infrastructure as Code):** The mandate that all infrastructure is provisioned and managed through code, never manual configuration. See §5.6.
* **Lakehouse:** A storage architecture (e.g., Apache Iceberg, Delta Lake) combining the flexibility of a data lake with the transactional guarantees of a warehouse, including time-travel. See §6.

### **Data Organization & Ownership**

* **Bronze Layer:** The raw, append-only, fully encrypted, schema-less ingestion layer of the Medallion Architecture. See §6.
* **Certification Gate:** The requirement that a data product must carry a verified "certified" status before any team outside its owning Dominion may consume it. See nexus_foundations.md, Annex C.6.
* **Data-Level Controls (DLC):** Access controls on the Silver layer that filter what a user or service can see, based on Dominion and role. See §6.
* **Data Mesh:** The philosophy of decentralizing data ownership into independent, domain-aligned Dominions, each treating its data as a product. See §2, §6.
* **Data Vault 2.0:** A modeling methodology for complex, rapidly changing enterprise data models with strong auditability. See §6.
* **Dominion:** A bounded, domain-aligned unit of data ownership mapped to one accountable team. See §6, nexus_foundations.md Annex C.1.
* **Medallion Architecture:** The three-layer data organization pattern of Bronze (raw), Silver (cleaned), and Gold (curated), each with its own security posture. See §6.

### **Privacy, Identity & Compliance**

* **Crypto-Shredding:** Encrypting each data subject's personal data with its own key, so that "erasure" means destroying the key rather than physically deleting the data. See nexus_foundations.md, Annex A.
* **Data Encryption Key (DEK):** A unique encryption key generated per data subject at ingestion, the basis of crypto-shredding. See nexus_foundations.md, Annex A.
* **Legal Hold:** A registered exception that blocks or defers an erasure request when data is subject to an active legal, tax, or fraud-investigation obligation. See nexus_foundations.md, Annex A.3.
* **Maker-Checker:** An approval pattern requiring two distinct identities — a requester and a separate approver — before a privileged, irreversible action executes. See nexus_foundations.md, Annex A.2.
* **SAME_AS relationship:** A confidence-scored graph edge linking two observations that may represent the same real-world subject, used in identity resolution. See nexus_foundations.md, Annex B.1.
* **Subject 360:** The resolved, query-time view of a single real-world subject's data, assembled from multiple Dominions via identity resolution. See nexus_foundations.md, Annex B.
* **Survivorship Rules:** The per-field rules deciding which Dominion's data wins when the same subject has conflicting values across sources. See nexus_foundations.md, Annex B.3.
* **Tokenization:** Replacing a real value with a non-reversible token at ingestion, keeping the token-to-value mapping in a separate vault so erasure only requires deleting the mapping. See nexus_foundations.md, Annex A.1.

### **Reliability & Operations**

* **Correlation ID:** A unique identifier attached to every request entering the Golden Triad, used to trace a single user action across Frontend, Backend, and Nexus. See §7.
* **RPO (Recovery Point Objective):** The maximum tolerable amount of data loss, measured in time, following a disruptive incident. See nexus_foundations.md, Annex E.1.
* **RTO (Recovery Time Objective):** The maximum tolerable time to restore a service after a disruptive incident. See nexus_foundations.md, Annex E.1.
* **SLI (Service Level Indicator):** A measurable signal — Freshness, Latency, Availability, or Correctness — used to define and track a Service Level Objective. See nexus_foundations.md, Annex D.1.
* **SLO (Service Level Objective):** A committed target for an SLI, defined per Tier. See nexus_foundations.md, Annex D.
* **Tier:** One of three predefined service classes (1: real-time, 2: operational batch, 3: analytical/historical) that sets the SLO and DR targets a data product commits to. See nexus_foundations.md, Annex D.2.

### **AI & Automation**

* **A2A (Agent-to-Agent):** A communication protocol standard that lets autonomous AI agents interact directly with one another, rather than only through human-facing interfaces. See §5.7.
* **HITL (Human-in-the-Loop):** The principle that autonomous processes include defined points where a human reviews or approves an action — reserved for ambiguous or high-risk cases, not routine ones. See §5.7.
* **OpenMetadata ("Data Vigilante"):** The platform serving as Nexus's semantic and governance backbone, ensuring every data asset is documented, labeled, and tagged. See §6.
