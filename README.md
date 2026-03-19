# AbInt Phase 2 — Research Intelligence Dashboard

Interactive HTML data visualisations for the **Abundant Intelligences (AbInt)** research network Phase 2 strategic planning.

Built to support leadership conversations around Phase 2 research strategy: what projects are strong, where there are gaps, what reviewers are excited about, and how projects could combine.

---

## Current version → `main`

**`AbInt_Phase2_Dashboard.html`** — 4-view dashboard built from merged data (evaluation form + research dashboard):

| View | What it answers |
|------|-----------------|
| Polarity Landscape | Alignment vs risk per project, coloured by research area |
| Coverage Map | Which Research Areas are covered, pod representation, infrastructure sharability, TS dimension coverage |
| Emergent Voice | What reviewers are actually saying — phrase clusters from reviewer language, no predefined themes |
| Signal Cards | Project-level cards with alignment, risk, status, emergent phrases |

### Source scripts (in `src/`)
- `process_polarity3.py` — merges evaluation form + research dashboard, computes scores, extracts emergent phrases via TF-IDF
- `gen_polarity3.py` — generates the HTML from `polarity_data3.json`

---

## Version history (branches)

| Branch | File | Description |
|--------|------|-------------|
| `main` | `AbInt_Phase2_Dashboard.html` | Current — 4-view dashboard with Coverage Map |
| `v3-polarity-landscape` | `AbInt_Polarity_Landscape.html` | Polarity Landscape + Signal Cards + Leadership Language |
| `v2-theme-landscape` | `AbInt_ThemeLandscape.html` | Theme-based bubble landscape |
| `v1-strategic-sensemaking` | `AbInt_Strategic_Sensemaking.html` | Early strategic sensemaking prototype |

---

## Data sources
- **Evaluation form responses** — reviewer feedback from Jackson and Jason across 10 projects
- **Research Dashboard** — full AbInt project registry (status, pod, research area, AI depth, infrastructure sharability)

*Built with D3.js v7 · Single-file self-contained HTML · No server required*
