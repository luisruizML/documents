---
name: brand-design-system
description: Use whenever creating or editing ANY diagram, chart, or image for the documents in this repo (Nexus, Rosetta, Arquitecture_summit) with drawio, Lucid, Mermaid, PlantUML or similar. Defines the mandatory brand typography, color palette, contrast rule, color scales, corner and connector rules.
---

# Brand Design System & Diagramming Instructions

## Overview

Mandatory visual identity for every diagram or chart that goes into a document. It governs the **look** (fonts, colors, shapes, connectors). Tool-specific skills (`drawio`, `lucid-diagram-conventions`) still govern **mechanics** (layout, file format, containment). If a topic-specific palette elsewhere conflicts with this skill, this skill wins unless the user says otherwise.

**Where the files go (Rosetta Business Objects):** `.drawio` sources in a `drawio/` subfolder and `.png` exports in an `images/` subfolder next to the page, named `Diagrams_<Object>_<Simplified|Full>`. The page links `images/<name>.png`. Other folders keep their current layout until they are migrated.

## When to Use

Any time a document needs a diagram, chart, or image: drawio (`.drawio`/`.png`), Lucid, Mermaid, PlantUML, or generated charts. Apply it before choosing a single color or font.

## 1. Typography (exactly three families)

| Use | Font |
|---|---|
| Titles & emphasized text (diagram titles, primary headers, milestones) | `Mulish`, sans-serif |
| Body & default text (node labels, descriptions, free-standing notes) | `Arial`, sans-serif |
| Code & technical data (file paths, variable names, SQL, raw code) and **connector labels** (the text on or above an arrow) | `Courier New`, monospace |

No other font families.

## 2. Color Palette & Roles

| Color | Hex | Role |
|---|---|---|
| Primary Indigo | `#3A0CA3` | Dominant structure, core process states, primary containers |
| Primary Teal | `#45E3CD` | Success states, highlighted nodes, secondary flows, positive accents |
| Primary Magenta | `#F72586` | Critical paths, alerts, starting triggers, key focal points |
| Neutral Gray | `#A6A8AB` | Borders, inactive components, secondary annotations, grid lines |
| Black | `#000000` | Text on light backgrounds |
| White | `#FFFFFF` | Canvas background, light end of gradients, text on dark nodes |

### Contrast rule (mandatory)
- Labels inside `#45E3CD` or light tints: text `#000000`.
- Labels inside `#3A0CA3` or `#F72586`: text `#FFFFFF`.

## 3. Dynamic Color Scales

Interpolate along the color wheel / saturation radius.

1. **Sequential (low to high / depth):** start from a primary (`#3A0CA3`, `#45E3CD`, or `#F72586`) and move inward toward `#FFFFFF`. Lightest = minimum intensity, solid brand hex = maximum.
2. **Diverging (comparative / bipolar):** interpolate along the arc:
   - `#3A0CA3` ↔ `#45E3CD`: **clockwise**
   - `#3A0CA3` ↔ `#F72586`: **counter-clockwise**
   - `#45E3CD` ↔ `#F72586`: **counter-clockwise**
   - Neutral midpoints move toward `#FFFFFF` or `#A6A8AB`.
3. **Qualitative (categorical):** step clockwise `#F72586` → `#3A0CA3` → `#45E3CD`; vary lightness between the pure color and `#FFFFFF` to get distinct, non-competing categories.

## 3b. Medallion Architecture Layers (mandatory exception)

Any chart that shows or refers to Medallion layers (Bronze, Silver, Gold, and elements assigned to them) uses these metallic colors for the layer elements, **instead of** indigo/teal/magenta. Everything else in the diagram (titles, connectors, non-layer nodes) still follows the core brand palette.

| Layer | Default fill | Variants | Default label text | Border / line |
|---|---|---|---|---|
| Bronze | `#B08D57` Metallic Bronze | `#8C6239` Antique Bronze, `#5C4033` Dark Bronze | `#000000` on `#B08D57`; `#FFFFFF` on `#8C6239` / `#5C4033` | `#8C6239` |
| Silver | `#D8D8D8` Light Silver | `#E5E4E2` Platinum / Cool Silver, `#A9A9A9` Sterling Silver | `#000000` | `#A9A9A9` |
| Gold | `#D4AF37` Metallic Gold | `#FFDF00` Bright Gold, `#CFB53B` Old Gold | `#000000` | `#CFB53B` |

Rules:
- Use the default fill for the layer container or main node; use variants for sub-elements, emphasis, or depth within that layer (lightest to darkest, same layer only).
- Never mix one layer's metallic colors into another layer's elements.
- Contrast rule still applies: black text on light/mid metallic fills, white text only on `#8C6239` and `#5C4033`.
- Medallion order is left to right or top to bottom: Bronze, Silver, Gold. Connectors between layers follow section 4.
- This replaces older per-topic Medallion colors (e.g. `#B0B7C6`, `#1F2A44`) in existing diagrams when they are next edited.

## 3c. Data Vault object colors (mandatory exception)

Diagrams of Data Vault objects color the object by type, **instead of** the Medallion Silver colors: Hub `#3A0CA3` (white text), Link `#45E3CD` (black text), Satellite `#F72586` (white text). A Satellite updated in place, which is the exception to the history default, uses a lighter tint of the Satellite color (65% toward white, black text) and a dashed border; the legend then adds "Satellite, in place (exception)". Lines and table grids inside an object are derived from its fill: lighter (55% toward white) on dark fills, darker (40% toward black) on light fills. The objects are collapsible containers (drawio `swimlane`): only the header bar and the border use the type color; the body is white with black text, so the picture is not overloaded. The grain is an italic note. `business-object-page/scripts/build_diagram.py` applies all of this.

## 4. Geometry & Connectors

- **Corners:** every box, container, card, and state block is rounded (`rounded=1` in drawio; `rx=5, ry=5` or rounded-corner syntax in Mermaid). No sharp 90° rectangles.
- **Routing:** orthogonal (elbow) or smooth curved connectors. Never diagonal point-to-point lines.
- **Crossings:** drawio uses line jumps (`jumpStyle=arc`); Lucid uses line hops (`lineJump=arc`). Mermaid: order nodes and use subgraphs to minimize crossings.
- **Line colors:** `#A6A8AB` regular flows, `#3A0CA3` major control paths, `#F72586` critical dependencies.
- **Connector labels (annotations on arrows):** always `Courier New`, size 11, text `#000000`, and an **explicit white label background** (`#FFFFFF`). Never rely on the tool's default background: draw.io takes it from the editor theme, so in dark mode the label shows black text on a black background even though the PNG export (always white) looks right.
- **Connector label position:** a label sits on the **first horizontal segment** of its connector, just after the object it leaves (10 pt of free line before it), and that segment is at least label width + 20 pt long, so the label ends before the first vertical. Never put a label on a vertical segment or on a bend: where connectors bundle toward a Hub, the other lines would cross it. When the gap between two objects is too small for the label, move the objects apart, not the label. The vertical bands start beyond the longest label of the gap and are nested (the connector farthest from the target outermost), so no line crosses a label. In drawio the label cell's `x` (relative, -1 to 1 along the path) is computed from the length of the first segment, not left at a fixed fraction. `business-object-page/scripts/build_diagram.py` does this and widens each gap to fit its labels; `scripts/postprocess_drawio.py` warns about any label that is not on the first horizontal segment.

## 5. Implementation Templates

### Mermaid: put at the top of every diagram

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Arial, sans-serif',
    'titleColor': '#3A0CA3',
    'primaryColor': '#3A0CA3',
    'primaryTextColor': '#FFFFFF',
    'primaryBorderColor': '#3A0CA3',
    'lineColor': '#A6A8AB',
    'secondaryColor': '#45E3CD',
    'tertiaryColor': '#FFFFFF',
    'edgeLabelBackground': '#FFFFFF'
  }
}}%%
```

### drawio style fragments

- Indigo node: `rounded=1;fillColor=#3A0CA3;strokeColor=#3A0CA3;fontColor=#FFFFFF;fontFamily=Arial;`
- Teal node: `rounded=1;fillColor=#45E3CD;strokeColor=#45E3CD;fontColor=#000000;fontFamily=Arial;`
- Magenta node: `rounded=1;fillColor=#F72586;strokeColor=#F72586;fontColor=#FFFFFF;fontFamily=Arial;`
- Title text: `fontFamily=Mulish;fontStyle=1;fontColor=#3A0CA3;`
- Code text: `fontFamily=Courier New;`
- Edge: `edgeStyle=orthogonalEdgeStyle;rounded=1;jumpStyle=arc;jumpSize=8;strokeColor=#A6A8AB;` (swap color per section 4). `jumpStyle` is the draw.io key; `lineJump` belongs to Lucid.
- Edge label (the separate `edgeLabel` cell): `edgeLabel;html=1;align=center;verticalAlign=middle;fontSize=11;labelBackgroundColor=#FFFFFF;fontColor=#000000;fontFamily=Courier New;`

**Mandatory post-processing step for the drawio skill's generator.** The generator writes `edgeLabel` cells without a background and in its theme font, and the rule above needs both. After generating each `.drawio` (and before exporting the PNG), rewrite every style that starts with `edgeLabel;` so it ends with `labelBackgroundColor=#FFFFFF;fontColor=#000000;fontFamily=Courier New;` and has no other `fontFamily`, `fontColor` or `labelBackgroundColor`. The script `scripts/postprocess_drawio.py <file.drawio>` does this, rounds every edge, and turns the marker `[[br]]` in a label into a line break (the generator collapses real line breaks). Export the PNG from that corrected `.drawio` with draw.io Desktop directly (`draw.io.exe -x -f png --scale 3 -b 10 -o out.png in.drawio`), not by importing the `.drawio` back through the generator, which re-guesses shapes from label words. Verify by opening the `.drawio` in dark mode: arrow labels must stay readable.

### Lucid

Set `fontFamily`, fill, and line colors per shape from the tables above; keep rounded shapes (`roundedRectangleContainer`, rounded rectangle) and smart lines.

**Exception for Data Vault object diagrams in Lucid:** lines are straight (the section 4 "never diagonal" rule is a drawio rule), and the object colors are the lighter Lucid set in `lucid-diagram-conventions` ("Data-model diagrams"): the same hues as section 3c, a lighter background and the drawio fill as border, with an even lighter fill for in-place Satellites.

## Common Mistakes

- Dark text on `#3A0CA3` / `#F72586`, or white text on `#45E3CD`.
- Using a font outside the three families.
- Straight diagonal connectors or sharp-cornered boxes.
- An arrow label on a vertical segment or a bend, or a gap between objects too narrow for the label on the first horizontal segment.
- Arrow labels in Arial or any theme font, or without an explicit white background (unreadable in the draw.io editor's dark mode).
- Inventing new hex values for categories instead of tinting the brand colors toward `#FFFFFF` (Medallion layers are the one exception, section 3b).
- Coloring Medallion layers with indigo/teal/magenta, or swapping the Bronze/Silver/Gold colors between layers.
- Using magenta decoratively; it is reserved for critical paths, alerts, triggers, and focal points.
