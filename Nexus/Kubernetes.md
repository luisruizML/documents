# Kubernetes at Nexus

*Companion document to* `Data_Principles.md` *P1 (Deploy anywhere) and P3 (Storage and compute scale independently), and to* `Foundations.md` *Annex D.4, which mandates "Kubernetes (or equivalent container orchestration)" for every On-Premise deployment without saying why, or what "equivalent" actually covers. Also connects directly to* `IaC_Terraform.md` *(which provisions the clusters this document runs workloads on),* `Broker_Messages_Services.md` *and* `ELT-ETL_Orchestration_Tooling.md` *(whose tools — Kafka, Flink, Airflow — this document argues all run on the same substrate), and Annex G.1 (whose dedicated-deployment-per-client model exists specifically because of one of this document's honest weaknesses).*

**Part:** 3 — How it is built · **Document:** 12 of 22 · **Version:** 0.1 · **Status:** Draft · **Last Updated:** 2026-09-22

## **Executive Summary**

Kubernetes has been the assumed deployment target everywhere it's named in this documentation set — Annex D.4, Annex E.4, Annex G.1, `IaC_Terraform.md` — never independently justified, the same gap Iceberg, Flink, and Kafka each had before their own documents. This document closes it: a comparison against Nomad, Docker Swarm, cloud-native container services, and Apache Mesos; an honest strengths/weaknesses accounting, including one weakness this doc set already built a whole architectural decision around (Annex G.1); and the specific monitoring Kubernetes needs to keep the promises Annex D.4 and Annex E.3 depend on.

## **Alternatives, Compared**

| | Kubernetes | Nomad | Docker Swarm | Cloud-native (ECS/Fargate, Cloud Run, Container Apps) | Apache Mesos |
| --- | --- | --- | --- | --- | --- |
| License | Apache 2.0 | Business Source License — source-available, not OSI-approved; HashiCorp's August 2023 relicensing covered Nomad the same as Vault and Terraform | Apache 2.0 | Proprietary | Apache 2.0, but effectively unmaintained at meaningful scale |
| Governance | CNCF (Linux Foundation) — vendor-neutral | Single-vendor (HashiCorp) | Docker Inc., low active investment | A single cloud provider | Largely inactive since roughly 2018 |
| Operational complexity | Genuinely high — the most common industry criticism of Kubernetes, and a fair one | Markedly simpler; also schedules VMs and raw binaries, not only containers | Simple, but the ecosystem moved on | None — fully managed | High, and no longer worth paying given how far adoption has fallen |
| Fit for Nexus | Environment-agnostic by design — matches Data Principles P1 (Deploy anywhere) exactly | Real technical merit, foreclosed by the same BSL pattern already ruled out for Vault (`Encryption_Key_Custody.md`) | Lost the adoption race — ecosystem, operators, and hiring pool all point to Kubernetes now | Locked to one cloud, disqualified before features even enter the comparison — the same exclusion applied to cloud-native orchestrators in `ELT-ETL_Orchestration_Tooling.md` and message brokers in `Broker_Messages_Services.md` | Superseded; not a live contender today |

**Worth being precise about what "equivalent" in Annex D.4 actually covers.** Annex D.4 says *"Kubernetes (or equivalent container orchestration)"* — not "Kubernetes, full stop." K3s, K0s, and OpenShift aren't alternatives being compared and rejected here; they're Kubernetes-family distributions, legitimate within the same choice, and exactly what "or equivalent" already anticipates for a smaller on-premise client that doesn't need full upstream Kubernetes. Nomad and Docker Swarm are the two that were genuinely different technologies, evaluated and passed over.

**Verdict:** Kubernetes, specifically because Nexus's own already-chosen stack needs one consistent operational model across every client, cloud or on-premise — not an abstract "industry standard" claim.

## **Strengths**

| Strength | What it actually buys Nexus |
| --- | --- |
| Environment-agnostic by design | Directly matches Data Principles P1 (Deploy anywhere) — the same workload definition runs on any cloud or on-premise, without a rewrite |
| It's what lets Nexus's own stack share one operational model | Kafka (via the Strimzi operator), Flink (via its Kubernetes Operator), and Airflow (via its Helm chart / `KubernetesExecutor`) all run under the same platform, across every client — not three separate deployment stories to maintain |
| CNCF governance | Same vendor-neutral pattern as Iceberg, Flink, and Kafka — no BSL-style restriction to navigate |
| Terraform's Kubernetes provider extends the same provisioning workflow | `IaC_Terraform.md`'s "one workflow, every vendor" argument carries straight through from infrastructure into workload deployment, with no second tool to learn |
| Self-healing and autoscaling | A crashed pod is rescheduled automatically; Horizontal Pod and Cluster Autoscaling are the direct mechanism behind Annex D.4's own "scale the cluster" remediation path for an On-Premise client falling short of a Tier target |

## **Honest Weaknesses**

| Weakness | The real cost |
| --- | --- |
| Genuine operational complexity | The most cited criticism of Kubernetes industry-wide, and a fair one — a second instance of the relational-thinking problem `Data_Layer_Problems.md` already names, stacked on top of it, not replacing it |
| Networking is a genuinely deep, easy-to-misconfigure subsystem | CNI plugins, ingress controllers, and service mesh decisions carry real, ongoing configuration risk, not a one-time setup cost |
| Stateful workloads are historically the harder case | Kafka itself is stateful — StatefulSets and persistent volumes work, but need real operational maturity (storage class configuration, volume provisioning, backup integration) that stateless services don't demand |
| Multi-tenant isolation within one shared cluster is genuinely hard to secure correctly | This is not a hypothetical cost — it's exactly why **Annex G.1 already chose dedicated-deployment-per-client instead of a shared multi-tenant cluster**: *"This avoids the harder problem of cross-tenant Data-Level Control enforcement in a shared cluster entirely, rather than attempting to solve it."* This document isn't introducing that argument, it's citing the decision this doc set already made because of it |
| On-premise Kubernetes carries more burden than a managed cloud offering | A cloud provider's managed Kubernetes handles control-plane operations; on-premise means Nexus or the client operates the control plane itself — directly the "Infrastructure Overhead on On-Premise" risk carried in the Technical Foundations risk register |

## **Mandatory Monitoring**

Same structure as `Broker_Messages_Services.md` — four categories, not a flat list, because Kubernetes's guarantees are exactly as real as what's actually watched.

### **Control Plane Health**

* **API server availability and latency** — if the control plane API degrades, nothing new can be scheduled and nothing can reconcile, even if every existing workload keeps running for a while on inertia.
* **etcd health specifically** — disk write latency, leader-election stability, and database size against its configured quota. etcd is Kubernetes's own backing store for all cluster state; its degradation is a silent-killer signal, the direct analog to Kafka's controller-stability concern in `Broker_Messages_Services.md` — not something that announces itself until it's already serious.
* **NotReady node count** — nodes silently dropping out of the cluster, reducing real capacity below what Annex D.4's benchmark assumed.

### **Workload Health**

* **Pod restart / crash-loop rate** — a pod repeatedly crash-looping is an application or resource problem that needs attention, not a transient blip to wait out.
* **Pending, unschedulable pods** — usually a resource-request or capacity misconfiguration, worth catching before it becomes "why didn't this job run today."
* **Requested vs. actual CPU/memory usage** — an overcommitted node degrades silently, the same failure shape as Kafka's reliance on OS page cache: nothing crashes, everything just gets slower.

### **Storage & Stateful Workloads**

* **PersistentVolume provisioning failures and capacity** — a stateful workload that can't get the storage it asked for fails in a way that's easy to miss if nobody's watching for it specifically.
* **StatefulSet health for anything stateful on this cluster** — including Kafka brokers themselves, if run via Strimzi. This is where `Broker_Messages_Services.md`'s broker-level monitoring and this document's pod/volume-level monitoring **compose** rather than duplicate each other — one watches the broker's own health signals, the other watches whether the pod carrying that broker actually has the resources and storage it needs.
* **Backup and snapshot verification** — tied directly to Annex E.3's mandatory quarterly restore drill; a snapshot that's never been restored is not a verified backup, on a persistent volume the same as anywhere else in this documentation set.

### **Capacity & Tenancy Boundaries**

* **Actual usage against the Annex D.4 benchmark** — has real usage drifted from the benchmarked baseline that justified a client's Tier commitment, in either direction?
* **Resource quota utilization per namespace** — a Dominion or workload approaching its quota before anyone's decided whether that's expected growth or a problem.
* **Network policy and pod security standard compliance, checked as drift, not assumed** — this is specifically verifying that the isolation boundary Annex G.1 chose by using dedicated deployments stays intact over time, rather than trusting it was configured once and never revisited.

**Breach handling reuses the same infrastructure as `Broker_Messages_Services.md`:** the Technical Foundations structured logging and Correlation ID, Annex D.3's SLO-breach escalation, and Annex E.3's restore-drill requirement for anything storage-related — no new alerting system invented for this document specifically.

## **Diagram**

![Kubernetes monitoring dimensions: Control Plane Health, Workload Health, Storage and Stateful Workloads, and Capacity and Tenancy Boundaries, each with its specific signals, feeding into the same existing observability and SLO escalation infrastructure as Broker_Messages_Services.md](Kubernetes.png)

*Diagram: the four monitoring categories and their specific signals — deliberately the same shape as* `Broker_Messages_Services.md`*'s diagram, since both feed the same escalation path. (Editable source: `Kubernetes.drawio`.)*

## **Verdict**

Kubernetes was never actually chosen in this documentation set either — like Kafka, it was assumed, cited across Annex D.4, Annex E.4, and Annex G.1 without ever being run against its own alternatives. Against Nomad, Docker Swarm, cloud-native container services, and Apache Mesos, it wins for the same shape of reason Iceberg, Flink, and Kafka did: not abstract industry-standard status, but the specific fact that it's what lets Nexus's own already-chosen tools — Kafka, Flink, Airflow — share one operational model across every client, cloud or on-premise. The weaknesses are real and this document doesn't soften them: the operational complexity is a second cognitive-shift cost stacked on the relational-thinking problem `Data_Layer_Problems.md` already names, and multi-tenant isolation is hard enough to get right that Annex G.1 built its entire tenancy model specifically to avoid needing to solve it. The monitoring section exists for the same reason it did in `Broker_Messages_Services.md` — none of Kubernetes's guarantees hold on their own, only as long as control-plane health, workload health, storage, and tenancy boundaries are actually watched, through infrastructure this documentation set already built rather than a new system invented for this one platform.
