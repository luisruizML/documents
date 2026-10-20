---
name: lucid-diagram-conventions
description: Use when creating or editing a Lucid diagram (via the lucid MCP) for the Nexus data-architecture documentation set, or when asked to keep a Lucid diagram visually consistent with its drawio counterpart, avoid overlapping lines, or lay out zones/containers/swimlanes cleanly.
---

# Lucid Diagram Conventions

## Overview

House-style judgment calls for Lucid diagrams in the Nexus project, layered **on top of** the Lucid MCP's own required reading — `lucid://skills/diagram-specification` governs format mechanics (assisted layout, containment rules, smart lines); this skill governs the choices that spec doesn't make for you: container vs. swimlane, which colors, what direction.

## When to Use

- Building a new Lucid diagram for a Nexus topic (architecture, data flow, layered/zoned model).
- Porting or extending an existing Nexus `drawio` diagram into Lucid.
- No fixed rule yet for choosing Lucid over `drawio` — decide case by case. `drawio` stays the default for diagrams that live in git as the `Topic.md` / `.drawio` / `.png` trio; reach for Lucid when you specifically need it (e.g. a shareable link).

**Always read `lucid://skills/diagram-specification` before calling `lucid_create_diagram_from_specification`** — it's a hard requirement of the tool itself, not optional here.

## No-Overlap Checklist

- Default `use_assisted_layout: true` (top-level) and `assistedLayout: true` on every container/swimLanes/bpmnPool, unless the diagram is genuinely spatial (map, floor plan, wireframe) or the container nests other containers.
- Use **smart lines**: leave relative `position` unset on both line endpoints so attachment points auto-adjust as shapes move. Only hardcode a position when the user asks for a specific attachment point (e.g. "connect to the top") — and if you set one endpoint's position, you must set both.
- Respect the containment rule: leave padding on all four sides between a shape and its parent container's edge. A bounding box that crosses the edge is NOT contained and assisted layout won't fix it.
- A prompt hint like "X at the center" does not require disabling assisted layout — AL honors it through initial placement.

## Container vs. Swimlane

| Content shape | Use |
|---|---|
| Grouping by domain/zone/boundary (Golden Triad's Raw/Conformed/Curated, Medallion's Bronze/Silver/Gold) | `rectangleContainer` / `roundedRectangleContainer` per zone, `assistedLayout: true` |
| Sequential flow across systems/teams/steps (ELT/ETL orchestration, broker message flow) | `swimLanes` or `bpmnPool`, one lane per system/team, `assistedLayout: true` on the container (not per-lane) |
| A zone containing sub-groups | Outer container `assistedLayout: false` (nested containers shouldn't be re-laid-out); inner containers `assistedLayout: true` |

## Direction Default

Top-to-bottom for layered/architectural diagrams (zones stacked by tier); left-to-right for sequential/pipeline diagrams (process step 1 → step N). Override per diagram when the source drawio version already establishes a different direction.

## Typography

- Default font: **Arial**.
- Code/inline code text (shape text, table cells, line labels showing code, config, or file paths): **Cousine**.
- The only approved alternative to Arial for regular (non-code) text: **Mulish**. Use it only when asked for or when Arial doesn't fit the diagram's intent — don't mix it in ad hoc alongside Arial in the same diagram.
- Set via each shape/line's `fontFamily` (or the `font-family` inline CSS span for mixed text, per the diagram-specification's TEXT FORMATTING section).

## Color: Match the Source Topic

**First apply the `brand-design-system` skill** (fonts, core palette, contrast, connectors). Where the table below conflicts with it, the brand skill wins; the table only records legacy per-topic colors from existing drawio diagrams. Each topic keeps the semantic colors its `drawio` version already established, for visual continuity between the two. Extend this table as topics get ported:

| Topic | Colors |
|---|---|
| Data Vault 2.0 (generic, Nexus) | Hub `#6A1B9A` (fill `#F3E5F5`) · Link `#00796B` (fill `#E0F2F1`) · Satellite `#EF6C00` (fill `#FFE0B2`) |
| Rosetta Business Objects | See "Data-model diagrams" below: Hub `#8F63F4`, Link `#A2F1E6`, Satellite `#FCB3D5`, in place `#FEDBEB` |
| Medallion Architecture | Superseded: use the Bronze/Silver/Gold metallic colors in `brand-design-system` section 3b (legacy: Bronze `#B0B7C6` · Silver `#45E3CD` · Gold `#D4AF37` · Platinum `#1F2A44`) |
| Golden Triad | `#F72586` · `#45E3CD` · `#3A0CA3` |

A brand-new topic with no `drawio` precedent: ask before inventing a palette, or borrow the nearest related topic's colors if the concepts overlap.

## Data-model diagrams (Hubs, Links, Satellites): proven recipe

Built by `business-object-page/scripts/build_lucid_global.py`; this is the house style for any Vault diagram in Lucid and it **overrides the assisted-layout checklist above**.

- **Straight lines only** (`lineType: "straight"`), unlike drawio, which routes elbows. Pin `position` on both endpoints and use `assisted layout: false`. With no elbows to hide a bad layout, arrange the boxes so no two lines cross and none passes through another box (the tests check this).
- **Colors**, same hues as drawio with a lighter background and the drawio fill as border: Hub fill `#8F63F4` / border `#3A0CA3`; Link `#A2F1E6` / `#45E3CD`; Satellite, history (default) `#FCB3D5` / `#F72586`; Satellite, in place (exception) `#FEDBEB` / `#FCB3D5`.
- **Box size = text + 10 pt on each side** (Lucid units are 160 per 72 pt). Compute the width from the longest line and the height from the line count, one font size for all objects (name bold 11 pt, grain italic 8 pt). Twin Satellites (`x` and `x_history`) share the wider width and sit together, default first, joined by a dashed line without arrowheads.
- **Grain inside each box**, as an italic second line (`<b>`, `<i>`, `<span style="font-size:8pt">`, `<br>` all work). Arrows run child to parent, with arrowheads.
- **Bands by owner domain** (`roundedRectangleContainer`, fill `#F6F4FC`), a four-entry legend, and a note.
- **Ids must be short** (`n1`, `e1`): ids of about 49 characters make the import fail with HTTP 400. Keep the real object name in `customData`.
- The API sometimes answers "Internal server error"; retry. Preflight "text-fit" and "shape-clearance" warnings are advisory when font sizes are explicit.
- Do not import large field tables; keep one shape per object. Always export a PNG and look at it before handing over, then create a view-only share link (`role: "view"`).
- Lucid documents cannot be deleted by the tools; create a new document per version and leave the old ones.

## Prefer Named Shapes for Tech/Cloud Components

Nexus diagrams reference Kubernetes, Iceberg, brokers, AWS/GCP/Azure services. Use `namedShape`/`namedContainer` from the relevant shape library (`lucid://shape-libraries/{aws-2024,gcp-2021,azure-2024}/...`) instead of recreating icons with basic shapes.

## Common Mistakes

- Setting relative `position` on only one line endpoint — import fails; set both or neither.
- Shape touching/crossing a container's edge — assisted layout won't pull it in; add padding.
- Inventing a new color per diagram instead of reusing the topic's established palette above.
- Long shape or line ids (import fails with HTTP 400), and boxes wider than their text (the text looks small).
- Disabling assisted layout just because the prompt implied a position — AL still honors it.

## Evolving This Skill

Living house-style guide, not a restatement of the Lucid spec. When a new Nexus topic gets a Lucid version, add its palette to the table above. New conventions (naming, export handling, additional shape-library defaults) get folded in here as they come up.
