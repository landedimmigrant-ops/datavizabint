# AbInt Phase 2 Dashboard: Analysis, Interpretations & Recommendations

*Prepared for Prem, AbInt Knowledge Broker — March 2026*

---

## 1. What the Data Is Telling Us (Network-Level Read)

### The Portfolio Is Strong but Unevenly Reviewed

29 projects, 5 reviewers, 157 classified sentences. The mean alignment score of 7.38/10 suggests a portfolio that broadly holds together — but the review coverage is thin. **20 of 29 projects have only a single reviewer**, which means most alignment and risk scores reflect one person's read, not a consensus. Only 9 projects were seen by two reviewers. No project was reviewed by three or more.

This is the single most important structural limitation of the current dashboard. Every pattern we surface carries this caveat.

### Reviewer Bias Is Real and Measurable

The reviewer profile charts reveal distinct reviewing styles:

- **Jackson** (63 sentences, 8 projects): Observational and recommendation-heavy. Scores relatively generous (avg 7.6). Writes the longest, most detailed feedback. His reviews tend to map projects against network infrastructure and future phases.
- **Suzanne** (33 sentences, 10 projects): Most critical voice. Highest proportion of questions (6 of 13 total). Flags ethical grounding, governance gaps, and accountability. She is the network's conscience in this data.
- **Hemi** (29 sentences, 13 projects): Broadest coverage but shortest sentences. Balanced across types. Frequently surfaces capacity-building needs and mentorship gaps.
- **Sara** (17 sentences, 3 projects): Most recommendation-dense (11 of 17). Strong on strategic positioning and cross-project connections. Limited sample though.
- **Jason** (15 sentences, 4 projects): Highest conviction score (0.542) but also highest concern (0.215). Sees both potential and risk simultaneously.

**Interpretation**: When a project scores low and was only reviewed by Suzanne, that's a different signal than if it scores low across two reviewers. The dashboard currently treats all scores equally — a refinement opportunity.

### The Tension Quadrant Is the Most Interesting Zone

Five projects sit in the "High Alignment + High Risk" zone — meaning reviewers see genuine value *and* genuine concern simultaneously. These are not problem projects; they are the ones where the most interesting strategic questions live:

- **Keolu Fox** (align 10.0, risk 0.391): Highest tension in the entire portfolio. Suzanne sees extraordinary potential but flags scope ambiguity and unclear community consultation.
- **Antoine Bellemare-Pepin** (align 8.0, risk 0.305): Technically the most ambitious project (High AI depth, spans all 5 AI domains). Risk is about reproducibility and network integration.
- **Ashley Cordes** (align 9.0, risk 0.259): The most connected project per reviewers. Risk is about scope sprawl — the book, the curricula, the carbon flux work — needs focus.

These three projects should get disproportionate strategic attention in Phase 2 planning because the upside justifies investment in risk mitigation.

---

## 2. Emergent Voice: LLM Interpretation of Research Themes

This is where I can offer something the keyword extraction alone cannot — a reading of *what the reviewers are collectively pointing toward* across projects, even when they do not use the same words.

### Theme 1: The Sovereign Stack Is Forming

Across 11 projects, "data sovereignty" surfaces as the single most cross-project phrase. But the underlying conversation is bigger than data governance. What reviewers are describing — across Sara's comments on local processing, Jackson's notes on community-controlled data repositories, and Suzanne's flags about governance agreements — is the outline of a **sovereign technology stack**: community-controlled data, locally governed infrastructure, and culturally grounded interfaces. This is not a single project's goal. It is an emergent network-level architecture.

**Projects contributing to this theme**: Cordes, Diamond & Pechawis, Clark, Bellemare-Pepin, Muller, Fox, Lloyd Jones, Shedlock (DEEP KIN)

**What the dashboard currently shows**: "Data Sovereignty & Governance" as a seeded theme with 5 reviewers, 16 projects. But this undersells it — the theme is actually about infrastructure sovereignty, not just data governance.

**Recommendation**: Rename this theme to "Sovereign Infrastructure" or "Sovereign Stack" in the Emergent Voice view. Add a short interpretive label beneath each theme bubble explaining the network-level read, not just the keyword cluster.

### Theme 2: The Mentorship Gap Is a Network Bottleneck

"Capacity building" and "mentorship learning" are the phrases, but the actual pattern in the sentences is more specific. Hemi repeatedly flags that projects need a "technical mentor/advisor/developer" (used verbatim for Darby Herman three times, and implied for others). Jackson notes that student-led projects risk losing continuity. Sara points to the need for "AI researchers to prototype."

**The interpretation**: The network has a missing middle layer. There are visionary PIs and community partners at one end, and technical ambitions at the other, but the connective tissue — people who can translate between Indigenous knowledge holders and AI system builders — is thin. This is a capacity problem, not a funding problem.

**What the dashboard currently shows**: "Capacity & Mentorship" with 4 reviewers, 12 projects. Correct but flat.

**Recommendation**: Surface a sub-theme: "Technical Translation Capacity" — the specific gap between IK grounding and AI implementation. This is distinct from general mentorship and has different interventions.

### Theme 3: The Language Cluster Wants to Be a Consortium

Jason explicitly recommends: *"I think all the Hawaiian language projects could be brought together, and a consortium made with the other language projects (Maori, Niitsitapi, maybe Haudenosaunee)."* This is not a vague thematic connection — it is a reviewer directly articulating a network action.

Projects in this cluster: Rice, Clark, Matsumoto, Srikanth, Kuwada, Little Bear (Blackfoot Dictionary), Leatherby, Chacaby (Mythos)

**What the dashboard currently shows**: "Language & AI" with 3 reviewers, 8 projects. The keyword extraction captures the overlap but not the strategic potential.

**Recommendation**: Add a "Reviewer-Proposed Actions" section to the Emergent Voice view that surfaces direct recommendations for network-level moves (consortium formation, shared builds, cross-pod sessions). These are different from general recommendations — they are structural proposals.

### Theme 4: The Emerging "Indigenous-Led" Theme Is Actually About Accountability

The auto-detected "Emerging: Indigenous-Led" theme (5 reviewers, 16 projects) looks like a positive clustering — but reading the underlying sentences, the conversation is more nuanced. Suzanne's sentences flagged under this theme are often *critical*: questioning whether projects are genuinely Indigenous-led or merely adjacent. Sara asks whether Ubalijoro's project is "Indigenous-led" despite clearly articulated value. Jackson flags the need for clearer documentation of how Indigenous members shaped direction.

**The interpretation**: "Indigenous-led" is not a celebration in this data — it is an accountability standard that reviewers are applying unevenly and that some projects are not meeting. This is a tension worth naming directly in the dashboard.

**Recommendation**: Split this emerging theme into two: "Indigenous Leadership (Affirmed)" for projects where reviewers confirm genuine Indigenous leadership, and "Indigenous Leadership (Questioned)" where reviewers flag gaps. This would be a powerful strategic lens.

### Theme 5: "Relational Approaches" Is Everywhere but Empty

The "Relational Approaches" theme has 5 reviewers and 18 projects but **zero extracted phrases**. This means the keyword seeding matched on general relational language but nothing specific enough to form a bigram. In practice, "relational" is used so broadly in this network's vocabulary that it has become a filler word — everything is relational.

**Recommendation**: Either remove this theme from the Emergent Voice (since it carries no specific signal) or redefine it with tighter seeding: "relational accountability," "reciprocal governance," "place-based relationships" — the specific relational practices that reviewers are actually pointing to.

---

## 3. Dashboard View-by-View Refinements

### Polarity Landscape
- **Issue**: The "Colour by AI Domain" toggle is good, but 15 of 29 projects show as "Not Yet Specified" grey, which visually dominates. Consider a third toggle option: "Colour by IK Methods" (Core/Partial/None) — this is fully populated and would give a complementary strategic lens.
- **Issue**: Risk scores are compressed between 0.05 and 0.39 — most projects cluster at the low end. Consider a log or sqrt scale on the X axis to spread them out and make the scatter more readable.
- **Suggestion**: Add a "single-reviewer" indicator (e.g., dashed circle border) to flag projects where the position reflects only one person's read.

### Coverage Map
- **Issue**: The TS dimensions table at the bottom is useful but the keyword-hit scoring produces some misleading results. "Technical AI Transformation" scores highest (avg 0.694) because generic words like "system," "model," and "technical" trigger constantly. Consider requiring 2+ keyword matches per sentence rather than counting individual word hits.
- **Suggestion**: Add a small heatmap row showing "Review Depth" — how many sentences each project received — so the reader knows which columns represent rich data vs thin coverage.

### Emergent Voice
- **Issue**: Theme bubbles are good for overview but clicking into a theme shows phrases and sentences without interpretation. This is where the LLM layer would add the most value.
- **Suggestion**: Add a short (2-3 sentence) **interpretive summary** inside each theme bubble's detail panel. These would be generated by the pipeline and would say things like: *"Reviewers across 5 pods are independently identifying data sovereignty as a prerequisite for technical development. This theme is strongest in Language and Environmental Stewardship projects."*
- **Suggestion**: Add a **"Network Question"** to each theme — a synthesised question that the theme data raises for strategic planning. e.g., *"Should AbInt invest in shared data governance frameworks before deepening AI development?"*

### Signal Cards
- **Refinement**: Currently sorted by alignment score (descending). Consider adding a sort toggle: by alignment, by risk, by review depth. Sorting by risk puts the attention-needing projects first.

### Reviewer Intelligence
- **Issue**: The new reviewer profile chart and project grouping are strong. One gap: when grouped by project, the polarity sort (positive → concern) is useful, but the reader cannot see *which type of concern*. A question about clarity is different from a flag about ethics. Consider adding a small colour-coded type chip on each card (already implemented) AND a border tint on the card itself (left-border colour matching the type).
- **Suggestion**: Add a "Consensus View" that only shows projects reviewed by 2+ reviewers, with both reviewers' sentences side by side. This is where the most reliable reads live.

### AI Domain
- **Issue**: The "Not Yet Specified" zone has 15 projects — more than half the portfolio. This is a data completeness issue in the spreadsheet, not a viz issue. But it makes the view less useful until more AI Domain values are filled in.
- **Suggestion**: For unfilled projects, consider auto-inferring domain from the primary research area as a fallback (e.g., Language projects → likely NLP/Language Models).

---

## 4. Three Highest-Impact Next Steps

1. **Add interpretive summaries to Emergent Voice themes**: This is where the LLM lens adds the most unique value. Not just keywords — a short analytical read of what the theme means for the network. I can generate these from the sentence data and embed them directly in the dashboard.

2. **Flag single-reviewer projects visually**: A dashed circle or small icon on the Polarity Landscape and Signal Cards would immediately communicate data confidence. This is a 30-minute change that significantly improves how the dashboard is read in planning meetings.

3. **Build a "Network Actions" panel**: Extract the 10-15 sentences where reviewers propose specific structural moves (consortium formation, shared builds, workshops, exits). These are not recommendations about individual projects — they are recommendations about the network itself. Surfacing them as a distinct view or panel would give strategic planners exactly what they need.

---

*This analysis is based on 157 classified reviewer sentences across 29 projects, 5 reviewers, and 40 cross-project phrases. All interpretations reflect patterns in the data as of March 2026. Single-reviewer bias is noted throughout.*
