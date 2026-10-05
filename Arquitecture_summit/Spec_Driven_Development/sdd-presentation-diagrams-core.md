# Spec-Driven Development with GitHub Spec Kit — Diagram Source, Core Deck (Mermaid)

Companion to `sdd-presentation-structure.md`. Each diagram ID (`D1`, `D4`, …) matches the "Visual" references in the structure document. This file holds slides 1–12 (D1–D12); slides 13–20 (D13–D20) are in `sdd-presentation-diagrams-appendix.md`. The document is split in two because the editor preview times out on pages with more than ~33 Mermaid diagrams.

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

# CORE DECK

## Slide 1 — Title

### D1 — The inversion

```mermaid
flowchart LR
    subgraph BEFORE["Before"]
        direction LR
        C1["Code<br/>source of truth"] --> S1["Spec<br/>written, then forgotten"]
    end
    subgraph AFTER["With Spec-Driven Development"]
        direction LR
        S2["Spec<br/>source of truth"] --> C2["Code<br/>its expression"]
    end
    BEFORE ==>|"inverted"| AFTER

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class S2 human
    class C2 ai
    class C1,S1 artifact
```

---

## Slide 2 — The problem

### D2 — The widening gap (ILLUSTRATIVE)

```mermaid
%% ILLUSTRATIVE values — replace with real data or label the slide "Illustrative"
%% Series 1 (rising) = AI-generated code volume; Series 2 (flat) = verified intent
xychart-beta
    title "Code volume vs. verified intent without a method"
    x-axis ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
    y-axis "Relative volume" 0 --> 100
    line [10, 22, 38, 55, 75, 95]
    line [10, 14, 17, 19, 21, 22]
```

---

## Slide 3 — Spec Kit: origin, credibility and the core idea

### D3a — Before / after: who is the source of truth?

```mermaid
flowchart TB
    subgraph OLD["Before: code is king"]
        direction TB
        CODE["Code<br/>single source of truth"]
        PRD["PRD"] -.->|"guides, then goes stale"| CODE
        DES["Design docs"] -.->|"guides, then goes stale"| CODE
        DIA["Diagrams"] -.->|"guides, then goes stale"| CODE
    end
    subgraph NEW["SDD: code serves the spec"]
        direction TB
        CON["Constitution + Spec<br/>source of truth"] --> PLAN["Plan"] --> TASKS["Tasks"] --> IMPL["Code + Tests"]
        IMPL -.->|"production learnings"| CON
    end
    OLD ~~~ NEW

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef faded fill:#F8F9FA,stroke:#CED4DA,color:#8D99AE,stroke-dasharray: 4 3
    class CON human
    class PLAN,TASKS artifact
    class IMPL,CODE ai
    class PRD,DES,DIA faded
```

### D3b — Spec Kit timeline

```mermaid
%% Verify dates and version numbers against the releases page before the retreat
timeline
    title GitHub Spec Kit maturity
    Sep 2025 : Open-sourced by GitHub
             : MIT license
             : Copilot, Claude Code, Gemini CLI support
    Late 2025 - 2026 : Extensions, presets, workflows, bundles
                     : Bug-fix and idea-assessment processes
                     : Agent skills invocation
    2026 : Convergence loop - implement and converge
    Sep 2026 : One year - 1.0 milestone
```

---

## Slide 4 — The Spec Kit cycle (anchor)

### D4 — The full cycle

```mermaid
flowchart LR
    subgraph P0["Phase 0 - once per project"]
        direction TB
        BRIEF["Context brief"] --> ENG["Constitution engineering<br/>dual-LLM + architect"]
        ENG --> CONST["/speckit-constitution"]
    end

    subgraph FEAT["Per feature"]
        direction LR
        SPEC["/speckit-specify"] --> G1{{"Review"}} --> CLAR["/speckit-clarify"]
        CLAR --> PLAN["/speckit-plan"] --> G2{{"Review + gates"}} --> CHK["/speckit-checklist"]
        CHK --> TASK["/speckit-tasks"] --> ANA["/speckit-analyze"] --> G3{{"Review"}}
        G3 --> IMP["/speckit-implement"]
        IMP <-->|"until Converged"| CONV["/speckit-converge"]
    end

    CONST --> SPEC
    CONV -.->|"production learnings update the spec"| SPEC

    A1[/"constitution.md"/] -.- CONST
    A2[/"spec.md"/] -.- SPEC
    A3[/"plan.md, research.md<br/>data-model.md, contracts/"/] -.- PLAN
    A4[/"tasks.md"/] -.- TASK
    A5[/"code + tests"/] -.- IMP

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef optional fill:#DCE6F2,stroke:#3D5A80,color:#1b1b1b,stroke-dasharray: 5 4
    class BRIEF,ENG,G1,G2,G3 human
    class CONST,SPEC,PLAN,TASK,IMP,CONV ai
    class CLAR,CHK,ANA optional
    class A1,A2,A3,A4,A5 artifact
```

### D4-mini — "You are here" marker (reuse on slides 5–10)

```mermaid
%% Change the class "here" to the current stage on each slide
flowchart LR
    C["Constitution"] --> S["Specify"] --> P["Plan"] --> T["Tasks"] --> I["Implement"] --> V["Converge"]
    classDef base fill:#E9ECEF,stroke:#8D99AE,color:#6c757d
    classDef here fill:#F4A261,stroke:#C1692A,color:#1b1b1b,stroke-width:3px
    class C,S,P,T,I,V base
    class C here
```

---

## Slide 5 — The constitution

### D5a — The constitution as a filter

```mermaid
flowchart LR
    PLAN["Proposed plan<br/>from /speckit-plan"] --> GATE

    subgraph GATE["Phase -1 constitutional gates"]
        direction TB
        GS["Simplicity gate<br/>Art. VII"]
        GA["Anti-abstraction gate<br/>Art. VIII"]
        GI["Integration-first gate<br/>Art. IX"]
        GP["Project articles<br/>IV - VI"]
    end

    GATE -->|"all pass"| OK["Approved plan<br/>-> /speckit-tasks"]
    GATE -->|"a gate fails"| CT["Complexity Tracking<br/>justify or simplify"]
    CT -->|"justified"| OK
    CT -->|"simplified"| PLAN

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef risk fill:#E76F51,stroke:#9C3D26,color:#ffffff
    class PLAN ai
    class GS,GA,GI,GP human
    class OK artifact
    class CT risk
```

### D5b — The nine articles, grouped

```mermaid
mindmap
  root((Constitution))
    Structure
      I Library-first
      II CLI interface
    Quality
      III Test-first - non-negotiable
      IX Integration-first testing
    Restraint
      VII Simplicity
      VIII Anti-abstraction
    Project-defined
      IV e.g. Security
      V e.g. Observability
      VI e.g. Versioning
    Governance
      Documented rationale
      Maintainer approval
      Compatibility assessment
```

---

## Slide 6 — How I build the constitution

### D6a — Structured debate flow

```mermaid
flowchart TB
    BRIEF["Context brief<br/>services, patterns, stack,<br/>standards, limitations"]
    BRIEF --> MA["LLM A<br/>strongest model, high reasoning"]
    MA --> DRAFT["Draft vN"]
    DRAFT --> MB["LLM B - different vendor<br/>same brief, high reasoning"]
    BRIEF --> MB
    MB --> CRIT["Critique<br/>contradictions, untestable rules,<br/>gaps, over-engineering"]
    CRIT --> ARCH{"Architect:<br/>satisfied?"}
    ARCH -->|"no - argue,<br/>pros and cons"| MA
    ARCH -->|"still unresolved"| EXP["Expert colleague<br/>final call"]
    EXP --> ARCH
    ARCH -->|"yes"| PUB["/speckit-constitution"]
    PUB --> REPO[("Repo: constitution.md<br/>+ decision records")]

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class ARCH,EXP human
    class MA,MB,PUB ai
    class BRIEF,DRAFT,CRIT,REPO artifact
```

### D6b — Escalation ladder

```mermaid
flowchart BT
    L1["Level 1 - Model vs. model<br/>frequency: every round | cost: low"]
    L2["Level 2 - Architect vs. model<br/>frequency: contested points | cost: medium"]
    L3["Level 3 - Architect vs. expert colleague<br/>frequency: rare | cost: high"]
    L1 -->|"not resolved"| L2
    L2 -->|"not resolved"| L3

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    class L1 ai
    class L2,L3 human
```

---

## Slide 7 — Specify and plan

### D7a — What/why vs. how

```mermaid
flowchart LR
    subgraph SPEC["spec.md - WHAT and WHY"]
        direction TB
        US["User stories"]
        AC["Acceptance criteria"]
        NC["NEEDS CLARIFICATION markers"]
        CK["Spec checklists"]
    end
    subgraph PLAN["plan.md + artifacts - HOW"]
        direction TB
        AR["Architecture and stack"]
        RS["research.md"]
        DM["data-model.md"]
        CO["contracts/"]
        CT["Complexity Tracking<br/>lightweight ADR log"]
    end
    SPEC ==>|"stable business intent"| GATES{{"Constitutional gates"}}
    GATES ==>|"architect owns this boundary"| PLAN

    classDef human fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class GATES human
    class US,AC,NC,CK,AR,RS,DM,CO,CT artifact
```

### D7b — Stable vs. volatile (ILLUSTRATIVE)

```mermaid
%% ILLUSTRATIVE - relative change frequency, not measured data
xychart-beta
    title "How often each layer changes"
    x-axis ["Constitution", "Spec - what/why", "Plan - how", "Tasks", "Code"]
    y-axis "Relative change frequency" 0 --> 10
    bar [1, 3, 5, 8, 10]
```

---

## Slide 8 — Tasks → implement → converge

### D8a — Task dependency graph with parallel lanes

```mermaid
flowchart LR
    T1["T001 Contracts"] --> T2["T002 Contract tests"]
    T2 --> T3["T003 P - Entity A model"]
    T2 --> T4["T004 P - Entity B model"]
    T2 --> T5["T005 P - Integration test setup"]
    T3 --> T6["T006 Service logic"]
    T4 --> T6
    T5 --> T7["T007 Integration tests"]
    T6 --> T7
    T7 --> T8["T008 Endpoint + e2e"]

    classDef par fill:#DCE6F2,stroke:#3D5A80,color:#1b1b1b,stroke-width:2px
    classDef seq fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class T3,T4,T5 par
    class T1,T2,T6,T7,T8 seq
```

### D8b — Convergence (ILLUSTRATIVE)

```mermaid
%% ILLUSTRATIVE - replace with real iterations from one feature
xychart-beta
    title "Open spec-to-code gaps per converge iteration"
    x-axis ["Iteration 1", "Iteration 2", "Iteration 3", "Iteration 4"]
    y-axis "Open gaps" 0 --> 12
    bar [11, 5, 2, 0]
    line [11, 5, 2, 0]
```

### D8c — Enforced test-first order

```mermaid
flowchart LR
    A["1 - contracts/"] --> B["2 - Contract tests"] --> C["3 - Integration tests"] --> D["4 - E2E tests"] --> E["5 - Unit tests"] --> F["6 - Source code<br/>make tests pass"]
    classDef test fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef code fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class A artifact
    class B,C,D,E test
    class F code
```

---

## Slide 9 — Context engineering: ASTs and Graphify

### D9a — AST for `total = price * qty`

```mermaid
flowchart TB
    ROOT["Assignment"] --> TGT["target:<br/>Identifier - total"]
    ROOT --> VAL["value:<br/>BinaryOp - multiply"]
    VAL --> L["left:<br/>Identifier - price"]
    VAL --> R["right:<br/>Identifier - qty"]

    classDef node1 fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef leaf fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class ROOT,VAL node1
    class TGT,L,R leaf
```

### D9b — Three ways an agent understands code

```mermaid
flowchart TB
    Q["Question: what breaks if I change PaymentService?"]

    subgraph G["grep / read files"]
        direction TB
        G1["Scan text file by file"] --> G2["Many tokens<br/>misses indirect calls"]
    end
    subgraph E["Embeddings / vector RAG"]
        direction TB
        E1["Find similar chunks"] --> E2["Probabilistic<br/>similar is not calls"]
    end
    subgraph A["AST knowledge graph"]
        direction TB
        A1["Traverse calls / imports / inherits"] --> A2["Deterministic, precise<br/>few tokens"]
    end

    Q --> G
    Q --> E
    Q --> A

    classDef weak fill:#F8F9FA,stroke:#CED4DA,color:#6c757d
    classDef strong fill:#3D5A80,stroke:#26394F,color:#ffffff
    class G1,G2,E1,E2 weak
    class A1,A2 strong
```

### D9c — From repository to Spec Kit

```mermaid
flowchart LR
    REPO[("Repository<br/>code, docs, ADRs")] --> TS["tree-sitter<br/>local AST parsing<br/>no LLM for code"]
    TS --> KG["Knowledge graph<br/>graph.json<br/>EXTRACTED / INFERRED edges"]
    KG --> QRY["Queries<br/>query / path / explain<br/>or MCP server"]
    QRY --> SKP["/speckit-plan<br/>impact analysis"]
    QRY --> SKA["/speckit-analyze<br/>check against real structure"]
    HOOK["git hooks<br/>rebuild on commit"] -.-> KG

    classDef ai fill:#3D5A80,stroke:#26394F,color:#ffffff
    classDef artifact fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    class TS,QRY artifact
    class KG artifact
    class SKP,SKA ai
```

---

## Slide 10 — Trust your toolchain

### D10a — Attack surface around the agent

```mermaid
flowchart TB
    subgraph CORE["Coding agent - runs with YOUR permissions"]
        direction LR
        P1["Filesystem"]
        P2["Credentials<br/>API keys, SSH, cloud"]
        P3["Network"]
        P4["Session context<br/>and memory"]
    end

    SK["Skills<br/>SKILL.md"] -->|"checkpoint"| CORE
    MCP["MCP servers"] -->|"checkpoint"| CORE
    PL["Plugins"] -->|"checkpoint"| CORE
    HK["Hooks"] -->|"checkpoint"| CORE
    EXT["Spec Kit community<br/>extensions / presets"] -->|"checkpoint"| CORE

    T1["Hidden instructions"] -.-> SK
    T2["Rug-pull updates"] -.-> MCP
    T3["Typosquatted packages"] -.-> PL

    classDef risk fill:#E76F51,stroke:#9C3D26,color:#ffffff
    classDef ext fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef perm fill:#3D5A80,stroke:#26394F,color:#ffffff
    class T1,T2,T3 risk
    class SK,MCP,PL,HK,EXT ext
    class P1,P2,P3,P4 perm
```

### D10b — Trust funnel

```mermaid
flowchart TB
    ALL["All available tools<br/>marketplaces, registries, repos"]
    ALL --> F1["Provenance check<br/>official publisher, exact package name"]
    F1 --> F2["Read before install<br/>SKILL.md, hooks, MCP config"]
    F2 --> F3["Pin versions<br/>lockfiles, no unpinned latest"]
    F3 --> F4["Least privilege<br/>scoped files, network, credentials"]
    F4 --> CAT["Approved organization catalog<br/>owner + periodic re-review"]

    classDef wide fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef step fill:#F4A261,stroke:#C1692A,color:#1b1b1b
    classDef final fill:#2A9D8F,stroke:#1E6F66,color:#ffffff
    class ALL wide
    class F1,F2,F3,F4 step
    class CAT final
```

### D10c — (Optional) 2026 incident figures

```mermaid
%% Figures from cited 2026 research - keep the source on the slide
%% Left: malicious skills in the ClawHavoc campaign; Right: percent of 42,447 scanned skills with a vulnerability
xychart-beta
    title "Agent skill supply chain, 2026"
    x-axis ["ClawHavoc malicious skills", "Scanned skills with a vulnerability - percent x10"]
    y-axis "Count" 0 --> 1400
    bar [1184, 261]
```

---

## Slide 11 — The business case

### D11a — Cost of change (ILLUSTRATIVE)

```mermaid
%% ILLUSTRATIVE - classic cost-of-change curve. Annotate on the slide:
%% "SDD catches misunderstandings here" at Spec/Plan, "Vibe coding finds them here" at Test/Production
xychart-beta
    title "Relative cost to fix a misunderstanding"
    x-axis ["Spec", "Plan", "Code", "Test", "Production"]
    y-axis "Relative cost" 0 --> 100
    line [1, 3, 10, 30, 100]
```

### D11b — Effort distribution (ILLUSTRATIVE)

```mermaid
%% ILLUSTRATIVE - replace with your own project data
pie showData
    title Vibe coding - effort distribution
    "Spec and planning" : 5
    "Implementation" : 45
    "Review" : 15
    "Rework" : 35
```

```mermaid
%% ILLUSTRATIVE - replace with your own project data
pie showData
    title SDD - effort distribution
    "Spec and planning" : 25
    "Implementation" : 45
    "Review" : 20
    "Rework" : 10
```

### D11c — KPI dashboard mock-up

```mermaid
flowchart LR
    subgraph DORA["Delivery - DORA"]
        direction TB
        K1["Lead time for changes"]
        K2["Change failure rate"]
    end
    subgraph SDD["SDD-specific"]
        direction TB
        K3["% of changes starting from a spec"]
        K4["Iterations to Converged"]
        K5["Defects traced to spec gaps"]
        K6["Spec-to-merge time"]
    end
    DORA ~~~ SDD

    classDef kpi fill:#FFFFFF,stroke:#3D5A80,color:#1b1b1b,stroke-width:2px
    class K1,K2,K3,K4,K5,K6 kpi
```

---

## Slide 12 — Risks, adoption roadmap and discussion

### D12a — Risk matrix

```mermaid
%% Positions are a starting point for discussion - adjust to your context
quadrantChart
    title Risk matrix before mitigation
    x-axis Low likelihood --> High likelihood
    y-axis Low impact --> High impact
    quadrant-1 Mitigate first
    quadrant-2 Plan contingency
    quadrant-3 Accept
    quadrant-4 Reduce frequency
    Ceremony on small changes: [0.75, 0.35]
    Review fatigue: [0.65, 0.5]
    Unmaintained constitution: [0.45, 0.7]
    Fast-changing tool: [0.7, 0.45]
    Toolchain supply chain: [0.35, 0.9]
    False LLM consensus: [0.4, 0.65]
```

### D12b — Adoption staircase

```mermaid
flowchart LR
    S1["Step 1 - Pilot<br/>one bounded context<br/><br/>Exit: one feature Converged<br/>+ lessons learned"]
    S2["Step 2 - Organization base<br/>base constitution + templates<br/><br/>Exit: approved by architects"]
    S3["Step 3 - Industrialize<br/>presets, extensions, CI checks,<br/>approved tool catalog<br/><br/>Exit: used by 3+ teams"]
    S4["Step 4 - Scale<br/>all new features spec-first<br/><br/>Exit: SDD KPIs tracked"]
    S1 --> S2 --> S3 --> S4

    classDef s1 fill:#E9ECEF,stroke:#8D99AE,color:#1b1b1b
    classDef s2 fill:#DCE6F2,stroke:#3D5A80,color:#1b1b1b
    classDef s3 fill:#8FA9C8,stroke:#3D5A80,color:#1b1b1b
    classDef s4 fill:#3D5A80,stroke:#26394F,color:#ffffff
    class S1 s1
    class S2 s2
    class S3 s3
    class S4 s4
```
