# Spec-Driven Development with GitHub Spec Kit — Presentation Structure

**Audience:** Architects retreat (technical depth + business considerations)
**Format:** 12 core slides + 8 appendix slides (20 total)
**Diagrams:** every visual below references a diagram ID (e.g. `D4`) defined as Mermaid code in `sdd-presentation-diagrams-core.md` (D1–D12) and `sdd-presentation-diagrams-appendix.md` (D13–D20).

---

## 0. Deck-wide design system

| Element | Rule |
|---|---|
| **Action titles** | Every slide title is a full-sentence claim. Reading only the titles should tell the whole story. |
| **Anchor diagram** | The cycle diagram (`D4`) reappears as a small "you are here" marker on slides 5–10, with the current stage highlighted. |
| **Color semantics** | One color for **human decisions** (review gates, arbitration, approvals), one for **AI generation**, one neutral for **artifacts**. Used identically on every diagram (the Mermaid files use `human`, `ai`, `artifact`, `optional` classes). |
| **Business marker** | A small icon (e.g. a briefcase) marks content aimed at the business audience. |
| **Illustrative data** | Any chart without real data is labeled *"Illustrative"* on the slide. Replace with your own project numbers where possible. |
| **Appendix band** | Appendix slides have a thin gray header band labeled "Appendix" and a "↩ back to slide X" link. |
| **Copyrighted material** | The "Sheldon Cooper" analogy is used in text/narration only — no images of the character. |

### Suggested timing (45-minute slot)

| Block | Slides | Time |
|---|---|---|
| Problem & context | 1–3 | ~8 min |
| The method | 4–8 | ~18 min |
| Toolchain | 9–10 | ~8 min |
| Business & adoption | 11–12 | ~8 min |
| Q&A (appendix on demand) | 13–20 | remaining |

---

# CORE DECK

## Slide 1 — Title

**Action title:** *Code serves the spec: Spec-Driven Development with GitHub Spec Kit*

**Content**
- Subtitle: "A method for making AI coding agents predictable, governable and auditable"
- Presenter name, role, date, retreat name
- One-line promise: what the audience takes away — a mental model, a governance approach, an adoption path

**Visual**
- `D1` — Minimal inversion graphic: `Spec → Code`, with the order visibly flipped. Nothing else on the slide.

**Transition:** "Let me start with a colleague we've all worked with…"

---

## Slide 2 — The problem

**Action title:** *We hired a brilliant, literal-minded engineer — and gave them no context*

**Content**
- **Analogy (narration + text):** an LLM without a method is like working with Sheldon Cooper with no context — brilliant, literal, and useless without clear instructions. GitHub frames coding agents the same way: literal-minded pair programmers, not search engines.
- **Left column — technical symptoms**
  - Code that looks right but doesn't quite work
  - Misses the actual intent
  - Picks a stack/architecture you wouldn't choose
  - The codebase silently becomes the de facto specification
- **Right column — business impact** 💼
  - Rework
  - Unpredictable delivery
  - Architecture drift
  - Decisions without an audit trail
- **Bottom banner — problem statement:** "The issue isn't the agent's ability to code. It's our lack of method."

**Visual**
- `D2` — "Widening gap" line chart: code volume rising steeply vs. verified intent staying flat; the gap = drift / rework / risk. *(Illustrative — replace with real data if available.)*

**Transition:** "GitHub saw exactly this problem and built something to address it."

---

## Slide 3 — Spec Kit: origin, credibility and the core idea

**Action title:** *Spec Kit reverses the relationship: specifications drive code, not the other way around*

**Content**
- **Top strip — origin:** built and open-sourced by GitHub · announced September 2, 2025 · MIT license · agent-agnostic (Copilot, Claude Code, Gemini CLI and more) · ~139k stars, ~12.5k forks · 1.0 milestone after one year *(verify exact version before the retreat)*
- **Middle — the power inversion:**
  - Before: code was the truth; PRDs, design docs and diagrams went stale
  - With SDD: the spec (plus the constitution) is the truth; code is its expression
- **Right box — why we can trust it**
  1. Vendor backing and longevity (GitHub / Microsoft ecosystem)
  2. Open and inspectable — templates and agent instructions are plain Markdown
  3. No lock-in — works with any major coding agent
  4. Active, large community
  5. **My own experience using it on real projects**
- **Footnote — balanced view:** critics (e.g. Gojko Adzic) warn SDD could reintroduce agile-era rigidity. Answer: lean, living specs + the convergence loop.

**Visuals**
- `D3a` — Before/after inversion diagram (code-as-truth vs. spec-as-truth).
- `D3b` — Timeline: launch → extensions/presets → convergence loop → 1.0.

**Transition:** "Here's how the method actually works, end to end."

---

## Slide 4 — The Spec Kit cycle (anchor slide)

**Action title:** *One constitution per project, one repeatable cycle per feature*

**Content**
- **Phase 0 (once per project):** context brief → constitution engineering → `/speckit-constitution`
- **Per feature:** `specify` → [`clarify`] → `plan` → [`checklist`] → `tasks` → [`analyze`] → `implement` ⇄ `converge`
- **Legend:** solid = core step · dashed = optional quality gate · person icon = human review gate
- **Key message:** "The spec changes first. Code changes are a consequence."
- **Feedback loop:** production learnings (incidents, metrics) flow back into the spec

**Visual**
- `D4` — The central cycle diagram with artifacts under each step, human gates between steps, the implement⇄converge loop, and the feedback arrow to `specify`. A reduced version is reused as the "you are here" marker on slides 5–10.

**Transition:** "Everything starts with the constitution, so let's look at it closely."

---

## Slide 5 — The constitution

**Action title:** *The constitution turns architecture principles into rules the agent must pass*

**Content**
- **What it is:** the project's "architectural DNA" — principles every plan is checked against, stored in `.specify/memory/constitution.md` and versioned with the code
- **The nine default articles, grouped**
  - *Structure:* I Library-first · II CLI interface
  - *Quality:* III Test-first (non-negotiable) · IX Integration-first testing
  - *Restraint:* VII Simplicity · VIII Anti-abstraction
  - *Project-defined:* IV–VI (e.g. security, observability, versioning)
- **Governance:** amendment process — documented rationale, maintainer approval, backward-compatibility assessment
- **Callout:** "The defaults are opinionated. Our job is to write *ours*."

**Visuals**
- `D5a` — "Constitution as a filter": plans pass through article gates; failures branch to *Complexity Tracking — justify or fix*.
- `D5b` — Article cards grouped by category (structure / quality / restraint / project-defined).

**Transition:** "Because the constitution governs everything downstream, I don't write it in one pass."

---

## Slide 6 — How I build the constitution

**Action title:** *I engineer the constitution through structured debate — two models, one architect, human escalation*

**Content**
- **Input — the context brief:** services, patterns, language/frameworks, company standards, limitations
- **Loop**
  1. LLM A (strongest model, high reasoning) drafts from the brief
  2. LLM B (different vendor, strongest model, high reasoning) challenges the draft using the *same* brief
  3. I argue, request alternative viewpoints, ask for pros and cons
  4. Repeat until satisfied
- **Escalation:** unresolved points go to an expert colleague — a human makes the final call
- **Output:** `/speckit-constitution` → versioned in the repo; contested decisions recorded (options · choice · why)
- **Lessons learned:** 2–3 from real projects *(your content)*
- **Optional refinements to mention:** ask the critic to *classify* findings (contradiction, untestable rule, missing concern, over-engineering, style); consider independent drafting to reduce anchoring
- **Business callout** 💼: "AI does the heavy lifting; senior judgment is spent only where it matters."

**Visuals**
- `D6a` — Debate flow: brief → Model A → draft → Model B → critique → architect decision → loop / escalate / publish.
- `D6b` — Escalation ladder: model vs. model → architect vs. model → architect vs. colleague (rising cost, falling frequency).

**Transition:** "With the constitution in place, each feature starts with a specification."

---

## Slide 7 — Specify and plan

**Action title:** *The spec defines what and why; the plan defines how — and that's where architecture lives*

**Content — two-column contrast**

| `spec.md` — what and why | `plan.md` + artifacts — how |
|---|---|
| User stories, acceptance criteria | Architecture and stack decisions |
| No tech stack, no APIs, no code structure | `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| `[NEEDS CLARIFICATION]` markers — the agent may not guess | "Phase -1" constitutional gates |
| Checklists act as unit tests for the spec | Complexity Tracking ≈ lightweight ADR log |

- **Callout for architects:** "The boundary between spec and plan is where architects add the most value."

**Visuals**
- `D7a` — Spec → plan split with gates between them.
- `D7b` — "Stable vs. volatile": spec content changes rarely, plan content changes more often. *(Illustrative.)*
- *Also recommended:* a real split-screen screenshot — a `spec.md` fragment with a clarification marker next to the matching `plan.md` gate checklist.

**Transition:** "Once the plan passes the gates, the agent starts building — and verifying."

---

## Slide 8 — Tasks → implement → converge

**Action title:** *Implementation is test-first and ends only when the code converges on the spec*

**Content**
- **Tasks:** derived from contracts, entities and scenarios; `[P]` marks tasks safe to run in parallel
- **Enforced order:** contracts → contract tests → integration → e2e → unit → source code
- **Analyze:** consistency check across spec, plan and tasks
- **Converge:** repeat implement ⇄ converge until the report says "Converged"
- **Key message:** "This is the answer to 'specs always drift.'"

**Visuals**
- `D8a` — Task dependency graph with parallel `[P]` lanes.
- `D8b` — Convergence chart: open spec–code gaps falling to zero across iterations. *(Illustrative — use real numbers from one feature if possible.)*
- `D8c` — Test-first order strip.

**Transition:** "All of this depends on the agent understanding your existing code — which is where Spec Kit needs help."

---

## Slide 9 — Context engineering: ASTs and Graphify

**Action title:** *Agents plan better when they query the code's structure instead of reading its text*

**Content**
- **What an AST is:** Abstract Syntax Tree — the structured representation of code (functions, calls, imports, inheritance) a parser builds; captures meaning and structure, not text
- **Three approaches compared**

| Approach | How the agent understands code | Weakness |
|---|---|---|
| grep / reading files | Text matching, file by file | Token-expensive, misses indirect relationships |
| Embeddings / vector RAG | Semantic similarity | Probabilistic — "similar" ≠ "calls" |
| **AST graph** | Real structural relationships | Deterministic, precise, cheap to query |

- **Graphify:** local deterministic tree-sitter parsing (no LLM, nothing leaves the machine for code) · every edge tagged `EXTRACTED` or `INFERRED` · not a vector store · ~40 languages · ADRs and `# WHY:` comments become nodes linked to code · git hooks keep the graph current at no API cost · MCP server available
- **Where it plugs into Spec Kit:** feeds `/speckit-plan` and `/speckit-analyze`; essential for brownfield
- **Automation setup:** Anthropic's `claude-code-setup` plugin (`claude-automation-recommender` skill) scans the repo and recommends the top 1–2 MCP servers, skills, hooks, subagents and slash commands — read-only, recommendations only. *(Claude Code-specific; present as "a step every agent setup needs" if the audience uses mixed agents.)*

**Visuals**
- `D9a` — AST mini-tree for `total = price * qty`.
- `D9b` — Three-lane comparison: grep vs. embeddings vs. AST graph.
- `D9c` — Pipeline: repo → tree-sitter → knowledge graph → queries → Spec Kit plan/analyze.
- *Also recommended:* a real screenshot of Graphify's `graph.html`.

**Transition:** "But every tool we add to the agent is also a way in. So how do we decide what to trust?"

---

## Slide 10 — Trust your toolchain

**Action title:** *Every skill, MCP server and plugin inherits your agent's power — vet it like production code*

**Content**
- **Threat facts (2026)**
  - ClawHavoc: 1,184+ malicious agent skills in one marketplace, deploying infostealers
  - A malicious skill inherits the agent's full permissions (files, credentials, network, memory)
  - MCP "rug pulls": trust is bound to the server name, not its content — a trusted server can ship a malicious update
  - Large-scale scans: roughly a quarter of skills have at least one vulnerability
- **Real examples from our own toolchain**
  - Graphify's official PyPI package is `graphifyy` (double y) — other `graphify*` packages are not affiliated (typosquatting risk)
  - Graphify's own security scans in CI are advisory, not blocking — even popular projects have gaps
- **Vetting checklist (summary):** provenance · read before install · pin versions · least privilege · data flow · re-review on update · organization catalog
- **Scope:** MCP servers, skills, plugins, hooks, and Spec Kit community extensions/presets
- **Business callout** 💼: "An approved catalog is the governance control — same as for open-source libraries."

**Visuals**
- `D10a` — Attack surface: agent permissions at the center, extension points around it, vetting checkpoints on each.
- `D10b` — Trust funnel: all tools → provenance → review → pinning → least privilege → approved catalog.
- `D10c` — *(Optional)* bar chart of cited 2026 incident figures, with sources on the slide.

**Transition:** "So what does the organization get in return for this discipline?"

---

## Slide 11 — The business case

**Action title:** *SDD moves effort to the start and cuts rework, risk and onboarding cost*

**Content**
- **Value levers** 💼: less rework · more predictable delivery · traceable decisions for audit/compliance · faster onboarding (specs as living documentation) · cheap "what-if" exploration (several implementations from one spec)
- **Costs, stated honestly:** upfront spec effort · tooling · skills shift · review time
- **Metrics**
  - Delivery: DORA (lead time, deployment frequency, change failure rate, time to restore)
  - SDD-specific: % of changes that start from a spec · iterations to "Converged" · defects traced to spec gaps · spec-to-merge time
- **Your own data** — even one project is more convincing than any vendor claim (avoid quoting the methodology document's "15 minutes vs. 12 hours" example as fact)

**Visuals**
- `D11a` — Cost-of-change curve with "SDD catches it here" vs. "vibe coding finds it here". *(Illustrative.)*
- `D11b` — Effort distribution: vibe coding vs. SDD (spec / implementation / review / rework). *(Illustrative.)*
- `D11c` — KPI dashboard mock-up (4 tiles).

**Transition:** "It's not free of risk — so let's be honest about that, and look at a path forward."

---

## Slide 12 — Risks, adoption roadmap and discussion

**Action title:** *Start small, write our constitution, then scale with shared presets*

**Content**
- **Risks → mitigations**

| Risk | Mitigation |
|---|---|
| Ceremony on small changes | Use the bug-fix flow; skip optional gates |
| Review fatigue | Short specs; focus review on spec + plan |
| Constitution nobody maintains | Named owner + amendment process |
| Tool changes fast | Pin versions; track releases |
| Toolchain supply chain | Approved catalog (slide 10) |
| "Two LLMs agreeing" false confidence | Human arbitration + expert escalation (slide 6) |

- **Roadmap (four steps):** Pilot on one bounded context → organization base constitution + templates → presets, extensions, CI checks → scale across teams
- **Discussion questions**
  - "What goes into articles IV–VI for us?"
  - "Who approves constitutional amendments?"
  - "Which system pilots first?"

**Visuals**
- `D12a` — Risk matrix (likelihood × impact).
- `D12b` — Roadmap staircase with exit criteria per step.
- Final screen: discussion questions only, large.

---

# APPENDIX

## Slide 13 — Repository anatomy and team workflow

**Action title:** *Specs live next to the code, get reviewed like code, and merge like code*

**Content**
- **Project level:** `.specify/memory/constitution.md` · templates and scripts under `.specify/` · agent integration files (skills/commands for your agent)
- **Feature level — `specs/NNN-feature-name/`:** `spec.md` · `plan.md` · `research.md` · `data-model.md` · `contracts/` · `quickstart.md` · `tasks.md`
- **Other processes:** `.specify/bugs/<slug>/` · `.specify/assessments/<slug>/`
- **Team workflow**
  1. `/speckit-specify` creates the feature number, branch and folder
  2. Spec and plan reviewed in a PR **before** implementation
  3. Implementation on the same branch
  4. Merge brings spec and code in together — one versioned unit
- **Review ownership:** business → `spec.md` · architect → `plan.md` + gates · developers → `tasks.md` + code
- **Key message:** "One branch holds intent and implementation — git history becomes decision history."

**Visuals**
- `D13a` — Annotated directory tree (color-coded by ownership).
- `D13b` — Branch flow (git graph) with review gate on spec/plan.
- `D13c` — Review ownership map.

**When to use:** "Where does this live?", "How do we review it?", "How does it fit our Git flow?"

---

## Slide 14 — Worked example / demo

**Action title:** *One real feature, from idea to converged code*

**Content**
- **The feature:** a real, anonymized feature — small but non-trivial (e.g. an API endpoint with a business rule and a persistence change)
- **Walkthrough table**

| Step | Input | Output | What I reviewed/changed | Time |
|---|---|---|---|---|
| `specify` | One-paragraph description | `spec.md` | Resolved N clarification markers | … |
| `plan` | Stack and constraints | `plan.md`, contracts | Gate failed → justified or simplified | … |
| `tasks` | — | `tasks.md` | Reordered tasks | … |
| `implement` / `converge` | — | Code + tests | N iterations to "Converged" | … |

- **2–3 value moments:** e.g. a clarification marker caught a wrong auth assumption; a gate blocked an unnecessary abstraction
- **Honest note:** where the agent still needed correction
- **Fallback:** a 2–4 minute pre-recorded version of the demo

**Visuals**
- `D14a` — Sequence of the feature walkthrough (architect ↔ agent ↔ repository).
- `D14b` — Time split pie (real numbers only).
- *Also recommended:* screenshot cards per step; a before/after "caught early" snippet.

**When to use:** "Show me it actually works" — or promote into the main flow for a longer slot.

---

## Slide 15 — Artifact map

**Action title:** *Every command produces a reviewable artifact, and every artifact has an owner*

**Content**

| Command | Artifact(s) | Purpose | Reviewed by | Gate type |
|---|---|---|---|---|
| `/speckit-constitution` | `constitution.md` | Project principles | Architect (+ expert) | Once per project; amendment process |
| `/speckit-specify` | `spec.md` | What and why | Product / business | Required |
| `/speckit-clarify` | updates `spec.md` | Resolve ambiguity | Product + architect | Optional |
| `/speckit-plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` | How | Architect | Required, with gates |
| `/speckit-checklist` | quality checklists | Spec quality | Architect / QA | Optional |
| `/speckit-tasks` | `tasks.md` | Executable breakdown | Tech lead / developers | Required |
| `/speckit-analyze` | consistency report | Cross-artifact check | Architect | Optional |
| `/speckit-implement` | code + tests | Build | Developers | Required |
| `/speckit-converge` | convergence report | Close spec–code gap | Developers + architect | Repeat until "Converged" |

- **Key message:** "Optional gates are where you tune rigor to the risk of the change."
- *Verify command names and outputs against the pinned version before the retreat.*

**Visuals**
- `D15a` — Swimlane-style sequence: Business / Architect / Developers / AI agent, each artifact landing with its reviewer.
- `D15b` — Rigor dial: low-risk change (core steps only) → critical system (all gates).

**When to use:** "Who's responsible for what?", "Isn't this too much process?", "Which steps can we skip?"

---

## Slide 16 — Context brief template

**Action title:** *The context brief is the true source of truth — the constitution is derived from it*

**Content — template sections**
1. System purpose
2. Service landscape
3. Architectural patterns (approved / to avoid)
4. Stack and versions
5. Integration constraints
6. Security and compliance
7. Operational standards
8. Company limitations (licensing, vendors, budget, skills)
9. Explicit out of scope
10. Open questions

- **Reuse:** the same brief feeds Phase 0 (constitution) and later `/speckit-plan`
- **Tip:** short and factual — long narrative briefs produce long, vague constitutions

**Visuals**
- `D16a` — Template sections as a mind map.
- `D16b` — "One input, two uses".
- `D16c` — Traceability: brief sections → constitution articles.

**When to use:** "What exactly do you give the models?"

---

## Slide 17 — Sample constitution

**Action title:** *A real constitution is short, testable and specific to its context*

**Content**
- 3–4 articles from one of your real constitutions (anonymized)
- Per article: **Source** (brief section) · **Enforcement** (plan gate / analyze / CI / review) · **Why** (one-line rationale)
- **Good vs. weak**
  - ❌ "Code should be secure and maintainable" — not checkable
  - ✅ "All external calls go through the approved API gateway; direct outbound HTTP from services is prohibited" — checkable
- **Amendment history:** 1–2 dated amendments
- **Prep:** remove client names, internal URLs and anything security-sensitive

**Visuals**
- `D17a` — Article annotation: article → source / enforcement / why.
- `D17b` — Testability scale: aspiration → enforceable rule.
- `D17c` — Amendment timeline.

**When to use:** "What does a good one look like?", "How specific should it be?"

---

## Slide 18 — ASTs and code graphs in depth

**Action title:** *From syntax tree to knowledge graph: how the agent gets a reliable map of the system*

**Content**
1. **Parsing:** tree-sitter builds an AST per file — deterministic, no LLM
2. **Extraction:** nodes (classes, functions, modules) and edges (`calls`, `imports`, `inherits`)
3. **Cross-file resolution:** each edge tagged `EXTRACTED` or `INFERRED`
4. **Clustering:** communities (subsystems) and "god nodes"
5. **Querying:** `query`, `path A B`, `explain X` — answered from the graph
- **Spec Kit benefits:** plan impact analysis · analyze against real structure · brownfield onboarding map
- **Limits:** structure, not runtime behavior (reflection, dynamic dispatch, config-driven wiring may be missed); must be rebuilt as code changes (hooks handle it)

**Visuals**
- `D18a` — Five-stage pipeline with EXTRACTED (solid) vs. INFERRED (dashed) edges.
- `D18b` — A `path` query hop by hop (impact analysis).
- `D18c` — Token comparison: file reading vs. graph query. *(Measure on a real repo — placeholder values.)*
- *Also recommended:* a real `graph.html` screenshot.

**When to use:** "What exactly is an AST?", "Why not RAG?", "How does this help with legacy?"

---

## Slide 19 — Full vetting checklist

**Action title:** *Nothing enters the agent's toolchain without passing the same checks as production dependencies*

**Content**

| # | Check | How to verify | Red flags |
|---|---|---|---|
| 1 | Provenance | Official publisher, verified repo, exact package name | Look-alike names, new accounts, no repo link |
| 2 | Read before install | Read SKILL.md, hooks, MCP config, install scripts | Hidden/encoded instructions, network calls in hooks |
| 3 | Version pinning | Lockfiles, exact versions, no unpinned `npx`/latest | Auto-updating installs |
| 4 | Least privilege | Scope file paths, network, credentials, tools | Broad filesystem or credential access |
| 5 | Data flow | What leaves the machine, to which provider/region | Unclear telemetry, unexpected endpoints |
| 6 | Security posture | Security policy, advisories, blocking CI scans | No SECURITY.md, ignored advisories |
| 7 | Maintenance | Commit activity, issue response, maintainer count | Single maintainer, abandoned |
| 8 | License | Compatible with company policy | Unclear or restrictive |
| 9 | Re-review on update | Diff review before upgrading | Large unexplained changes |
| 10 | Catalog registration | Approved list with an owner | Ad hoc installs on individual machines |

- **Scope:** MCP servers, skills, plugins, hooks, Spec Kit community extensions and presets
- **Process:** request → review → approve → catalog → monitor → re-review

**Visuals**
- `D19a` — Tool trust lifecycle (state diagram).
- `D19b` — Trust tiers pyramid.

**When to use:** "How do we govern this?", "Who approves tools?", security questions.

---

## Slide 20 — References

**Action title:** *Everything in this talk is open and verifiable*

**Content — grouped links**
- **Spec Kit:** repository · docs site · methodology (`spec-driven.md`) · releases · launch post (GitHub Blog, Sept 2025)
- **Methodology & critique:** Martin Fowler / Birgitta Böckeler on SDD tools · Microsoft developer blog · critical perspectives (DevOps.com)
- **Context engineering:** Graphify · tree-sitter · Anthropic `claude-code-setup` plugin
- **Security research:** agent-skill supply chain papers (arXiv) · MCP security analyses · OWASP agentic guidance
- **Internal:** constitution template, context brief template, pilot proposal

**Visuals**
- `D20` — Reference map (mind map), plus a **QR code** to one page with all links.

**When to use:** end of talk; leave on screen during Q&A.

---

## Appendix navigation (Q&A jump table)

| If asked about… | From slide | Jump to |
|---|---|---|
| Where it lives / how it's reviewed | 4 or 8 | 13 |
| Proof it works | 3 or 8 | 14 |
| Roles and ownership | 4 | 15 |
| What you give the models | 6 | 16 |
| What a good constitution looks like | 5 or 6 | 17 |
| ASTs, RAG, legacy | 9 | 18 |
| Tool governance and security | 10 | 19 |

**Preparation priority:** slides 14, 16 and 17 need material from your own projects — spend preparation time there.

---

## Sources

- GitHub Spec Kit repository — https://github.com/github/spec-kit
- Spec Kit methodology (`spec-driven.md`) — https://github.com/github/spec-kit/blob/main/spec-driven.md
- GitHub Blog launch post (Sept 2, 2025) — https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- Microsoft for Developers on Spec Kit — https://developer.microsoft.com/blog/spec-driven-development-spec-kit/
- Visual Studio Magazine coverage — https://visualstudiomagazine.com/articles/2025/09/03/github-open-sources-kit-for-spec-driven-ai-development.aspx
- DevOps.com (incl. critique) — https://devops.com/githubs-spec-kit-puts-the-spec-back-in-software-development/
- Martin Fowler / Birgitta Böckeler on SDD tools — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Graphify — https://github.com/Graphify-Labs/graphify
- Anthropic `claude-code-setup` plugin — https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup
- Towards Secure Agent Skills (arXiv) — https://arxiv.org/pdf/2604.02837
- Formal Analysis and Supply Chain Security for Agentic AI Skills (arXiv) — https://arxiv.org/pdf/2603.00195
- Malicious MCP servers and the supply chain problem — https://dev.to/roxdavirox/malicious-mcp-servers-and-the-unsolved-supply-chain-problem-for-ai-agents-k4h
