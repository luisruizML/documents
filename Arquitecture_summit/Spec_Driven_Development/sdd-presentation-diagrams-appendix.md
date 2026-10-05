# Spec-Driven Development with GitHub Spec Kit — Diagram Source, Appendix (Mermaid)

Companion to `sdd-presentation-structure.md`. Each diagram ID (`D13a`, `D14b`, …) matches the "Visual" references in the structure document. This file holds slides 13–20 (D13–D20); slides 1–12 (D1–D12) are in `sdd-presentation-diagrams-core.md`. Conventions below are identical to the core file.

**Conventions**
- Color classes used consistently across flowcharts:
  - `human` — human decisions / review gates (warm orange)
  - `ai` — AI generation steps (blue)
  - `artifact` — files and outputs (neutral gray)
  - `optional` — optional quality gates (dashed border)
  - `risk` — threats / warnings (red)
- Charts marked `%% ILLUSTRATIVE` use placeholder values — replace with real project data or label the slide "Illustrative".
- `xychart-beta` does not render series legends; add the legend in the slide itself.
- Renders in GitHub, GitLab, VS Code (Markdown Preview Mermaid Support), mermaid.live, and draw.io (*Arrange → Insert → Advanced → Mermaid*).


---

# APPENDIX

## Slide 13 — Repository anatomy and team workflow

### D13a — Directory tree (color-coded by owner)

```mermaid
flowchart LR
    ROOT["repo/"] --> SPECIFY[".specify/"]
    SPECIFY --> MEM["memory/constitution.md"]
    SPECIFY --> TPL["templates/ + scripts/"]
    SPECIFY --> BUGS["bugs/slug/"]
    SPECIFY --> ASSESS["assessments/slug/"]
    ROOT --> AGENT["agent integration files<br/>skills / commands"]
    ROOT --> SPECS["specs/"]
    SPECS --> FEAT["003-chat-system/"]
    FEAT --> F1["spec.md"]
    FEAT --> F2["plan.md"]
    FEAT --> F3["research.md<br/>data-model.md<br/>quickstart.md"]
    FEAT --> F4["contracts/"]
    FEAT --> F5["tasks.md"]
    ROOT --> SRC["src/ + tests/"]

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef review fill:#FFE8CC,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class MEM human
    class F1,F2,F4 review
    class F3,F5 artifact
    class SRC ai
    class ROOT,SPECIFY,TPL,BUGS,ASSESS,AGENT,SPECS,FEAT artifact
```

### D13b — Branch flow

```mermaid
gitGraph
    commit id: "main"
    branch "003-chat-system"
    checkout "003-chat-system"
    commit id: "spec.md"
    commit id: "clarifications"
    commit id: "plan.md + contracts"
    commit id: "PR review: spec + plan" type: HIGHLIGHT
    commit id: "tasks.md"
    commit id: "tests - red"
    commit id: "implementation - green"
    commit id: "converge: Converged" type: HIGHLIGHT
    checkout main
    merge "003-chat-system" id: "spec + code merged together"
```

### D13c — Review ownership

```mermaid
flowchart LR
    BUS(["Business / Product"]) --> R1["spec.md<br/>what and why"]
    ARC(["Architect"]) --> R2["constitution.md"]
    ARC --> R3["plan.md + gates<br/>contracts/"]
    DEV(["Developers / Tech lead"]) --> R4["tasks.md"]
    DEV --> R5["code + tests"]

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class BUS,ARC,DEV human
    class R1,R2,R3,R4,R5 artifact
```

---

## Slide 14 — Worked example / demo

### D14a — Feature walkthrough

```mermaid
sequenceDiagram
    autonumber
    actor A as Architect
    participant G as Coding agent + Spec Kit
    participant R as Repository

    A->>G: /speckit-specify - feature description
    G->>R: branch 00N-feature + spec.md
    G-->>A: spec with NEEDS CLARIFICATION markers
    A->>G: /speckit-clarify - answers
    Note over A,G: Value moment - wrong assumption caught early
    A->>G: /speckit-plan - stack and constraints
    G->>R: plan.md, contracts/, data-model.md
    G-->>A: gate failed - Complexity Tracking entry
    A->>G: simplify or justify
    A->>G: /speckit-tasks
    G->>R: tasks.md with parallel markers
    loop until Converged
        A->>G: /speckit-implement
        G->>R: tests then code
        A->>G: /speckit-converge
        G-->>A: remaining gaps
    end
    A->>R: PR - spec and code merged together
```

### D14b — Time split (REAL DATA ONLY)

```mermaid
%% PLACEHOLDER - fill with measured time from your worked example
pie showData
    title Worked example - where the time went
    "Specify + clarify" : 1
    "Plan + review" : 1
    "Tasks" : 1
    "Implement + converge" : 1
```

---

## Slide 15 — Artifact map

### D15a — Swimlane view: who produces, who reviews

```mermaid
sequenceDiagram
    participant B as Business
    participant A as Architect
    participant D as Developers
    participant G as AI agent

    G->>A: constitution.md - once per project
    G->>B: spec.md - required review
    G-->>B: clarify - optional
    G->>A: plan.md, contracts/, data-model.md - required + gates
    G-->>A: checklist - optional
    G->>D: tasks.md - required
    G-->>A: analyze report - optional
    G->>D: code + tests - required
    G->>D: converge report - repeat until Converged
```

### D15b — Rigor dial

```mermaid
flowchart LR
    LOW["Low-risk change<br/>specify, plan, tasks,<br/>implement, converge"]
    MED["Standard feature<br/>+ clarify<br/>+ analyze"]
    HIGH["Critical system<br/>+ clarify + checklist<br/>+ analyze<br/>+ expert review"]
    LOW -->|"more risk"| MED -->|"more risk"| HIGH

    classDef low fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef med fill:#FFE8CC,stroke:#C1692A,color:#1b1b1b
    classDef high fill:#E76F51,stroke:#9C3D26,color:#ffffff
    class LOW low
    class MED med
    class HIGH high
```

---

## Slide 16 — Context brief template

### D16a — Template sections

```mermaid
mindmap
  root((Context brief))
    What
      1 System purpose
      9 Explicit out of scope
      10 Open questions
    Landscape
      2 Service landscape
      5 Integration constraints
    Technology
      3 Architectural patterns
      4 Stack and versions
    Non-functional
      6 Security and compliance
      7 Operational standards
    Business
      8 Company limitations
```

### D16b — One input, two uses

```mermaid
flowchart LR
    BRIEF["Context brief"] --> P0["Phase 0<br/>dual-LLM constitution engineering"]
    P0 --> CONST["constitution.md"]
    BRIEF --> PLAN["/speckit-plan<br/>stack and constraints"]
    CONST --> PLAN
    PLAN --> OUT["plan.md"]

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class BRIEF,P0 human
    class PLAN ai
    class CONST,OUT artifact
```

### D16c — Traceability: brief → constitution articles

```mermaid
%% Example mapping - replace with your real brief sections and articles
flowchart LR
    subgraph B["Context brief sections"]
        direction TB
        B3["3 Architectural patterns"]
        B4["4 Stack and versions"]
        B6["6 Security and compliance"]
        B7["7 Operational standards"]
    end
    subgraph C["Constitution articles"]
        direction TB
        C1["I Library-first"]
        C4["IV Security boundaries"]
        C5["V Observability"]
        C8["VIII Anti-abstraction"]
    end
    B3 --> C1
    B3 --> C8
    B4 --> C8
    B6 --> C4
    B7 --> C5

    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    class B3,B4,B6,B7 artifact
    class C1,C4,C5,C8 human
```

---

## Slide 17 — Sample constitution

### D17a — Annotated article

```mermaid
flowchart LR
    ART["Article IV - Security boundaries<br/>All external calls go through the<br/>approved API gateway"]
    ART --> SRC["Source<br/>brief section 6"]
    ART --> ENF["Enforcement<br/>plan gate + CI network test"]
    ART --> WHY["Why<br/>central auth, audit, rate limiting"]

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class ART human
    class SRC,ENF,WHY artifact
```

### D17b — Testability scale

```mermaid
flowchart LR
    W["Aspiration<br/>Code should be secure<br/>and maintainable"]
    M["Guideline<br/>Prefer the API gateway<br/>for external calls"]
    S["Enforceable rule<br/>All external calls go through the gateway;<br/>direct outbound HTTP is prohibited"]
    W -->|"make it specific"| M -->|"make it checkable"| S

    classDef weak fill:#E76F51,stroke:#9C3D26,color:#ffffff
    classDef mid fill:#FFE8CC,stroke:#C1692A,color:#1b1b1b
    classDef strong fill:#2A9D8F,stroke:#1E6F66,color:#ffffff
    class W weak
    class M mid
    class S strong
```

### D17c — Amendment history

```mermaid
%% Replace with your real amendment history
timeline
    title Constitution amendment history
    v1.0 : Initial ratification
         : Approved by architecture board
    v1.1 : Article V amended
         : Added tracing requirement after incident review
    v1.2 : Article VII amended
         : Raised project limit with documented justification
```

---

## Slide 18 — ASTs and code graphs in depth

### D18a — From syntax tree to knowledge graph

```mermaid
flowchart LR
    S1["1 - Source files"] --> S2["2 - AST per file<br/>tree-sitter, deterministic"]
    S2 --> S3["3 - Nodes + edges<br/>classes, functions, modules"]
    S3 --> S4["4 - Cross-file resolution"]
    S4 --> S5["5 - Communities + god nodes"]
    S5 --> S6["6 - Query / path / explain"]

    subgraph LEGEND["Edge provenance"]
        direction LR
        X1["OrderService"] -->|"EXTRACTED - explicit in source"| X2["PaymentGateway"]
        X3["OrderService"] -.->|"INFERRED - resolved by tool"| X4["RetryPolicy"]
    end
    S4 ~~~ LEGEND

    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    class S1,S2,S3,S4,S5 artifact
    class S6 ai
```

### D18b — Impact analysis with a `path` query

```mermaid
flowchart LR
    A["OrderController"] -->|"calls"| B["OrderService"]
    B -->|"calls"| C["PaymentGateway"]
    C -->|"imports"| D["BankApiClient"]
    D -.->|"inferred: uses"| E["ExternalBankAPI"]

    classDef start fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef hop fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef target fill:#E76F51,stroke:#9C3D26,color:#ffffff
    class A start
    class B,C,D hop
    class E target
```

### D18c — Token comparison (MEASURE ON A REAL REPO)

```mermaid
%% PLACEHOLDER values - measure on a real repository before using
xychart-beta
    title "Context tokens to answer one structural question"
    x-axis ["Reading files", "Graph query"]
    y-axis "Tokens - thousands" 0 --> 100
    bar [80, 5]
```

---

## Slide 19 — Full vetting checklist

### D19a — Tool trust lifecycle

```mermaid
stateDiagram-v2
    [*] --> Requested
    Requested --> UnderReview: owner assigned
    UnderReview --> Rejected: fails a check
    UnderReview --> Approved: passes checks 1-8
    Approved --> Cataloged: added with pinned version
    Cataloged --> Monitored
    Monitored --> UnderReview: update or advisory
    Monitored --> Retired: abandoned or replaced
    Rejected --> [*]
    Retired --> [*]
```

### D19b — Trust tiers

```mermaid
flowchart TB
    T3["Tier 3 - Community / unknown<br/>full review, sandbox first"]
    T2["Tier 2 - Established open source<br/>standard review + pinning"]
    T1["Tier 1 - Official / vendor-maintained<br/>e.g. GitHub Spec Kit core,<br/>Anthropic official plugins<br/>lightweight review + pinning"]
    T3 --- T2 --- T1

    classDef t3 fill:#E76F51,stroke:#9C3D26,color:#ffffff
    classDef t2 fill:#FFE8CC,stroke:#C1692A,color:#1b1b1b
    classDef t1 fill:#2A9D8F,stroke:#1E6F66,color:#ffffff
    class T3 t3
    class T2 t2
    class T1 t1
```

---

## Slide 20 — References

### D20 — Reference map

```mermaid
mindmap
  root((References))
    Spec Kit
      Repository
      Docs site
      spec-driven.md methodology
      Releases
      GitHub Blog launch post
    Methodology and critique
      Fowler and Boeckeler on SDD tools
      Microsoft developer blog
      DevOps.com critique
    Context engineering
      Graphify
      tree-sitter
      claude-code-setup plugin
    Security research
      Agent skill supply chain papers
      MCP security analyses
      OWASP agentic guidance
    Internal
      Constitution template
      Context brief template
      Pilot proposal
```
