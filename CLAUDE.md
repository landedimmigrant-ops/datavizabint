# AbInt Phase 2 — Research Intelligence Dashboard
## Project context file — read this first in any new session

---

## What this is

An interactive single-file HTML dashboard for the **Abundant Intelligences (AbInt)** research network Phase 2 strategic planning. Built by Prem (knowledge broker, university research environment) to support leadership conversations about project strength, coverage gaps, reviewer signals, and research trajectories.

**Not a web app. Not a multi-file project.** One Python generator → one self-contained HTML file (~420KB, all data embedded).

---

## People

- **Prem** — owner, knowledge broker. Third culture background, intuitive/creative thinker, works in Canadian university research context. Not a developer — prefers conversational iteration over technical specs.
- **AbInt** — the research network. ~36 projects across multiple pods (research groups). Phase 2 is strategic planning.

---

## File locations

```
mnt/Data viz for program report/
├── CLAUDE.md                          ← this file
├── AbInt_Phase2_Dashboard.html        ← the deliverable (also served as index.html)
├── index.html                         ← copy of Dashboard.html (git pages)
├── AbInt_Research_Area_Reach.pptx     ← slide generated from dashboard data
└── README.md                          ← outdated, needs updating

/sessions/gifted-exciting-ramanujan/   ← working directory (Cowork VM / local)
├── gen_polarity3.py                   ← THE GENERATOR — edit this, run it, done
├── process_polarity3.py               ← data pipeline (Excel → polarity_data3.json)
├── polarity_data3.json                ← embedded data blob (~400KB)
├── polarity_llm_scores.json           ← LLM polarity scores for 37 projects
└── gen_area_slide.js                  ← pptxgenjs script for PPTX slide
```

**Rebuild pipeline:**
```bash
# Edit gen_polarity3.py, then:
python3 gen_polarity3.py
cp "mnt/Data viz for program report/AbInt_Phase2_Dashboard.html" \
   "mnt/Data viz for program report/index.html"
cd "mnt/Data viz for program report" && git add -A && git commit -m "..."
```

---

## Dashboard architecture — 9 active tabs

| Tab | ID | What it shows |
|-----|----|---------------|
| Polarity Landscape | view-polarity | Alignment vs risk scatter, coloured by research area |
| Coverage Map | view-coverage | Research area coverage, pod presence, TS dimensions, infrastructure |
| Emergent Voice | view-emergent | TF-IDF phrase clusters from reviewer language |
| Signal Cards | view-signals | Per-project cards: alignment, risk, status, emergent phrases |
| Reviewer Intelligence | view-reviewer | Reviewer pattern analysis (includes Project Overview sub-tab) |
| AI Domain | view-ai | AI type/depth breakdown across projects |
| Project Overview | (inside Reviewer Intelligence) | Project-level TS scores and comparisons |
| Pod Intelligence | view-pod | Per-pod profiles: AI depth, domains, areas, TS dims, themes |
| Pod Relations | view-pod-relations | Two sub-views: Force Network + Parallel Flow |
| TS Network Rollup | view-transform | TS dimension analysis across all projects |

**Network Transformation tab is MUTED** — nav button hidden, div `display:none`.

---

## Scoring model

**Alignment score (1–10):** 70% LLM score + 30% keyword score. Same `DATA.ts_project_scores` used in both Coverage Map and Project Overview — no divergence.

**Polarity (risk_score, conviction):** 70% LLM (`polarity_llm_scores.json`) + 30% keyword hybrid. Computed in `process_polarity3.py`, matched via `norm_pol()` (lowercase, strip special chars).

**TS dimensions:** 7 dimensions scored per project. LLM + keyword blend.

---

## Data model key facts

- **36 projects**, multiple pods
- Projects average **4.5 themes each** → fractional weights (`w = 1/n_themes`) used in Parallel Flow so total weight stays at 36
- Research areas assigned as **primary (1°)** and **secondary (2°)** — Coverage Map shows both with badges
- Pod names can contain unicode — `podColor()` handles this

---

## Pod Relations tab — two views

Toggle between Force Network and Parallel Flow via buttons at top of the tab.

### Force Network (`buildForceView`)
- **Theme-centric layout**: themes pulled to centre via `forceRadial(0)`, pods orbit outer ring via `forceRadial(outerR)`
- **Pill labels**: each theme gets a floating rounded-rect pill above its circle (dark bg, coloured border, coloured text) connected by a hairline. Circle size = data (project count). Pill size = text.
- **Click interaction (Option C)**: glow ring + outward pulse on selected node. Connected nodes stay bright. Unconnected nodes at 45% opacity. Non-connected links at 10%. Background labels at 35–40%.
- **Zoom**: +/− /reset buttons top-right + scroll zoom
- **Tooltip**: hover any node for connection count + details

### Parallel Flow (`buildFlowView`)
- **Axes**: Pod → Research Area → AI Depth → Theme (default) OR Theme → Research Area → AI Depth → Pod (toggled)
- **Toggle**: "VIEW FROM ● Pod" / "VIEW FROM ◆ Theme" buttons rendered as HTML above SVG
- **Band data**: each band has `originSet` (Set of start-axis values flowing through it) and `projects` (array of project short names)
- **Click-to-trace**: click any block OR label → traces full path across all 4 axes. Highlighted bands recoloured to clicked node's own colour (not dominant pod). Non-highlighted bands drop to 4% opacity.
- **Project popup**: hover any band → tooltip shows project names in that segment
- **Label padding**: PAD_L=152, PAD_R=162, SVG `overflow:visible` — pod/theme labels never clip

---

## Key functions in gen_polarity3.py

| Function | ~Line | Purpose |
|----------|-------|---------|
| `podColor(pod)` | ~400 | Returns consistent colour for a pod name |
| `renderCoverage()` | ~800 | Coverage Map tab — area cards, sorted by project count |
| `renderPodProfile()` | ~2300 | Pod Intelligence tab |
| `renderPodRelations()` | ~2430 | Pod Relations tab shell + view toggle |
| `buildForceView(canvas)` | ~2476 | Force network D3 vis |
| `buildFlowView(canvas, mode)` | ~2828 | Parallel sets / Sankey vis |
| `renderTransform()` | ~3080 | TS Network Rollup tab |

---

## Design conventions

- **Colour palette**: dark navy background `#080e1a`, muted blues/purples for UI chrome
- **Pod colours**: assigned via `podColor()` — consistent across ALL views
- **Theme colours**: pulled from `DATA.research_themes[].color` — consistent across all views
- **Area colours**: `AREA_COLOR[AREA_NAME_TO_ID[name]]`
- **Depth colours**: `{High:'#f87171', Mid:'#fbbf24', Low:'#a3e635', None:'#475569'}`
- **Text**: avoid heavy formatting in conversation (Prem prefers prose). Use minimal bullet points.
- **Commit style**: descriptive multi-line messages with Co-Authored-By footer

---

## Git state (as of this session)

Latest commits on `main`:
- `e171e56` — Parallel Flow: colour-consistent path tracing + project popup on hover
- `2be7b7b` — Parallel Flow: click-to-trace full path + Pod/Theme perspective toggle
- `7e507c8` — Force network: floating pill labels, zoom controls, theme-coloured links
- `67fdc45` — Force network: theme nodes dark-fill badge
- `494c932` — Force network: 45% background opacity, spread themes
- `16c2a1c` — Force network: theme-centric layout + Option C highlight interaction
- `3c13712` — Fix Parallel Flow label clipping: dynamic padding + overflow:visible

---

## Things discussed but not yet built

- **Force network → Pod × Theme matrix**: Prem was open to replacing the force network entirely with a matrix heatmap (pods as rows, themes as columns, bubble = project count, colour = AI depth). Deferred — he wanted to focus on Parallel Flow first.
- **Project drilldown in Parallel Flow**: clicking a highlighted band shows project names in tooltip. A richer panel view (showing all projects across a full traced path in one panel) was discussed but not built.
- **README.md update**: the existing README is outdated (describes 4 views). Needs rewriting to match current 9-tab state.

---

## Session management note

This project has been built across multiple long Cowork sessions. Context gets compacted. When starting a new session:
1. Read this CLAUDE.md first
2. Run `git log --oneline -10` in the project folder to see current state
3. Check `gen_polarity3.py` line count (`wc -l gen_polarity3.py`) — currently ~3200 lines
4. Do NOT assume anything about current state — read the file, check git

---

*Last updated: March 2026 — end of session covering Parallel Flow interactive features*
