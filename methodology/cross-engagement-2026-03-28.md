# Cross-Engagement Analysis — MBB Team
*2026-03-28 | 15 engagements analyzed | bcg-methodologist*

---

## Scope of Analysis

**Engagements reviewed (15 total):**

| # | Company | Date | Overall Score | Weakest Agent |
|---|---------|------|--------------|---------------|
| 1 | Unicorn Ecosystem / Oscar Hartmann | 2026-03-24 | B | bcg-production (2.8/5 — final-report not produced) |
| 2 | NVIDIA | 2026-03-24 | B+ | bcg-segment-analyst (3.67/5 avg) |
| 3 | Oscar Hartmann Business Model (Russia) | 2026-03-25 | B+ | bcg-segment-analyst (4.1/5 avg) |
| 4 | Oscar Hartmann Multi-Market Investment | 2026-03-25 | B+ | bcg-segment-analyst (4.3/5 avg) |
| 5 | OpenAI | 2026-03-26 | B+ | bcg-production (N/A — final-report not produced) |
| 6 | Google DeepMind | 2026-03-26 | A- | bcg-production (N/A — final-report not produced) |
| 7 | Anthropic | 2026-03-26 | B+ | bcg-segment-analyst (3.82/5 avg) |
| 8 | DeepSeek | 2026-03-26 | B+ | bcg-segment-analyst (4.1/5 avg) |
| 9 | Intel | 2026-03-27 | B+ | bcg-production (4.2/5) |
| 10 | AMD | 2026-03-27 | B+ | bcg-segment-analyst (4.2/5 avg) |
| 11 | Microsoft | 2026-03-27 | B+ | bcg-segment-analyst (3.6/5 avg) |
| 12 | Meta | 2026-03-27 | A- | bcg-segment-analyst (3.5/5 avg) |
| 13 | Baidu | 2026-03-27 | B | bcg-segment-analyst Apollo Go (3.1/5) + bcg-production (0/5) |
| 14 | Amazon | 2026-03-27 | B+ | bcg-segment-analyst (3.8/5 avg) |
| 15 | ASML | 2026-03-28 | A- | bcg-segment-analyst (4.0/5 avg) |

---

## Pattern Analysis by Agent

### Summary Table

| Agent | Corpus Average Score | Most Frequent Issue | Appears in X/15 |
|-------|---------------------|--------------------|--------------------|
| bcg-researcher | 4.4 / 5 | LinkedIn signals thin; Data Gaps inline not consolidated; stale competitor data for fast-moving companies | 6 / 15 |
| bcg-market-mapper | 4.4 / 5 | TAM upper-end selection bias; WAU/MAU conflation; unverified corporate events stated as fact | 10 / 15 |
| bcg-segment-analyst | 3.9 / 5 (avg) | Innovate archetype absent; strategy count below minimum (Cash Cow/Dog); revenue projections exceed TAM ceiling; competitor revenue stale or misread | 15 / 15 |
| bcg-fact-checker | 4.5 / 5 | Strongest and most consistent agent; partial correction only (nearby claims not checked); unresolved arithmetic ambiguity left as "questionable" | 15 / 15 |
| bcg-portfolio-analyst | 4.6 / 5 | DICE applied to whole portfolio not individual strategies; one residual propagation error after corrections | 15 / 15 |
| bcg-production | 4.1 / 5 | Section headers topic-style not conclusion-style; final-report.md not produced (5/15 engagements) | 15 / 15 |
| bcg-domain-expert | 4.5 / 5 | Analytically constructed figures not labeled as such; one per-engagement cascade from domain expert claim to portfolio | 7 / 15 |
| bcg-data-scientist | 4.4 / 5 | Cross-file TAM discrepancy not reconciled with own market-map working figure | 8 / 15 |

---

## Pattern Analysis by Issue Type

### P1 Issues (present >60% of engagements, HIGH impact)

#### P1-A: Innovate Archetype Absent or Near-Absent in Majority of Segments
**Frequency:** 15 / 15 engagements (100%)
**Impact:** HIGH — the most strategically distinctive output (category-creating options) is consistently missing; final portfolios contain only optimization of existing positions; board-level question "what new categories could this company create?" goes unanswered in every engagement
**Agent:** bcg-segment-analyst
**Pattern trajectory:** Not improving. The Baidu engagement (engagement 13) was the only full-engagement resolution (all 4 segments had genuine Innovate). ASML and Amazon (engagements 14-15) reverted to full absence across all segments.
**Root cause confirmed:** The current prompt lists Innovate as one of five archetypes with identical instruction weight. There is no enforcement mechanism, no definition precise enough to distinguish Innovate from Defend/Pivot, and no blocking self-check gate. The agent generates the strongest strategies first (Defend, Scale) and terminates without completing the Innovate set.

#### P1-B: Pyramid Principle Partial Failure in Section Headers
**Frequency:** 13 / 15 engagements (87%)
**Impact:** HIGH — a reader scanning only headers cannot reconstruct the recommendation; fails the most basic Pyramid Principle test; erodes the executive value of the final report
**Agent:** bcg-production
**Pattern trajectory:** Not improving. The same failure has been flagged in 13 of 15 engagements. The current prompt says "use conclusion-style headers" but provides no explicit test, no prohibited examples, and no blocking self-check. The agent demonstrably CAN write strong conclusion headers (AWS, Advertising in Amazon; "Kodak Trap" in Intel) but applies the standard selectively and inconsistently.
**Root cause confirmed:** The prompt states the principle but does not enforce it. Without explicit examples of prohibited topic-headers, a blocking self-check, and a test the agent can apply mechanically before saving the file, the instruction is ignored under length pressure.

#### P1-C: Strategy Count Below Minimum for Cash Cow and Dog Segments
**Frequency:** 9 / 15 engagements (60%)
**Impact:** HIGH — MBB Dog and Cash Cow positions have rich option spaces (harvest rate, timing, licensing, exit sequencing) that are never explored when segment analysts generate 2-4 strategies vs. the required 6-15; portfolio analyst has no strategic options to evaluate for these positions
**Agent:** bcg-segment-analyst
**Pattern trajectory:** Present in most engagements with multiple segments; worsens when segments are structurally mature (AMD Console SoC, ASML DUV Dry, ASML DUV Immersion, Intel Altera, Oscar Hartmann segments)
**Root cause confirmed:** The current prompt specifies "10-15 strategies" without differentiating by MBB position. The agent interprets a Dog/Cash Cow position as justification for abbreviated analysis rather than as a prompt to explore the full option space within a constrained position.

### P2 Issues (present >40% of engagements, MEDIUM-HIGH impact)

#### P2-A: TAM Upper-End Selection Bias / Unreconciled Cross-File TAM Discrepancy
**Frequency:** 11 / 15 engagements (73%)
**Impact:** MEDIUM-HIGH — inflates apparent market opportunity; makes company's position appear more conservative than it is; distorts share calculations and investment prioritization
**Agent:** bcg-market-mapper (selection bias) + bcg-data-scientist (no reconciliation)
**Specific pattern:** Market-mapper selects the highest available estimate when multiple credible sources disagree. Data-scientist independently derives a different figure. Neither agent reconciles the discrepancy. Portfolio analyst receives contradictory inputs and must choose without guidance.
**Worst case documented:** ASML IBM TAM $46.2B (all semiconductor services) vs. $15-26B (equipment-specific aftermarket) — reverses the strategic implication from "18% penetration with vast headroom" to "41% penetration requiring new categories for growth."

#### P2-B: Competitor Revenue Currency Error (Forward Estimate Used When Actual Results Available)
**Frequency:** 7 / 15 engagements (47%)
**Impact:** MEDIUM-HIGH — understating a major competitor's revenue by 20-27% (Google Cloud in Microsoft engagement) fundamentally misrepresents competitive threat
**Agent:** bcg-market-mapper
**Pattern:** Market-mapper uses analyst forward projections for major competitor revenue without checking whether quarterly actual results were published. Alphabet Q4 2025 results were available 6+ weeks before the Microsoft engagement; market-mapper used a forward estimate 22-27% below actual.

#### P2-C: final-report.md Not Produced
**Frequency:** 5 / 15 engagements (33%)
**Impact:** HIGH for those engagements — client-presentable deliverable absent; engagement terminates at portfolio.md
**Agent:** bcg-production
**Engagements affected:** Unicorn Ecosystem, OpenAI, Google DeepMind, NVIDIA (partial), Baidu
**Pattern:** Five consecutive successes (Intel through Meta/Amazon) confirm the agent can produce the report when context budget is available. The Baidu recurrence was preceded by a rate-limit on the Apollo Go first attempt, suggesting context exhaustion as a contributing factor. The Unicorn, OpenAI, and DeepMind failures were early-corpus and appear to have stabilized.

#### P2-D: WAU/MAU Metric Conflation
**Frequency:** 4 / 15 engagements (27%), specifically in AI-adjacent engagements
**Impact:** MEDIUM — 2-4x overstatement of user base for ChatGPT/consumer AI platforms; affects competitive positioning analysis for all AI segments
**Agent:** bcg-market-mapper
**Pattern:** Consistently affects engagements involving OpenAI competitors (Google DeepMind, OpenAI, Anthropic, DeepSeek). "2.8B MAU" for ChatGPT cited in 3 separate engagements despite being flagged each time. Root cause: no explicit metric-type labeling requirement in the mapper prompt.

#### P2-E: Competitor Revenue Misread / IPO Proceeds Conflated with Operating Revenue
**Frequency:** 5 / 15 engagements (33%)
**Impact:** HIGH for affected strategies — 18x overstatement of Pony.ai revenue (Baidu) directly misrepresented Apollo Go's competitive positioning
**Agent:** bcg-segment-analyst + bcg-market-mapper
**Pattern:** Two sub-classes: (1) IPO proceeds cited as revenue for recently-listed companies (Pony.ai, DeepSeek-adjacent), (2) parent segment revenue attributed to subsidiary (Altera Intel "All Other" $3.6B vs. standalone $1.54B; AMD Embedded pre-carveout)

#### P2-F: Analytically Constructed Figures Not Labeled as Such
**Frequency:** 4 / 15 engagements (27%)
**Impact:** MEDIUM — creates cascade corrections downstream; Meta $14B WhatsApp revenue was a legitimate analytical construct (Click-to-WA + API fees) but unlabeled presentation propagated through portfolio analysis
**Agent:** bcg-domain-expert + bcg-segment-analyst
**Pattern:** Figures that combine two separately-reported line items, apply a derived coefficient, or represent a modeling output are presented as reported figures without explicit labeling.

---

## Error Rate Trend Analysis

| Engagement | Hallucination Rate | Overall Score | Fact-Checker Score |
|------------|-------------------|--------------|-------------------|
| NVIDIA (1) | ~8% | B+ | 4.6 |
| Oscar Russia (3) | ~7% | B+ | 4.5 |
| Oscar Multi (4) | ~7% | B+ | 4.6 |
| OpenAI (5) | ~6% | B+ | 4.6 |
| Google DeepMind (6) | ~4% | A- | 4.8 |
| Anthropic (7) | ~4% | B+ | 4.4 |
| DeepSeek (8) | ~5% | B+ | 4.6 |
| Intel (9) | ~5.6% | B+ | 4.4 |
| AMD (10) | ~5% | B+ | 4.7 |
| Microsoft (11) | ~4.2% | B+ | 4.5 |
| Meta (12) | ~5.4% | A- | 4.0 |
| Baidu (13) | ~8% | B | 4.4 |
| Amazon (14) | ~5% | B+ | 4.5 |
| ASML (15) | ~2.2% | A- | 4.7 |

**Trend:** Hallucination rate improving. Started at ~8% (NVIDIA), trending toward ~3-5% in recent engagements. ASML at 2.2% is the corpus low. The bcg-fact-checker is the most consistent performer (average 4.5/5) and is the primary reason error rates have not worsened.

**Quality score trend:** Three A- engagements in the final seven (Google DeepMind, Meta, ASML) vs. zero in the first eight. Improvement is real but driven by individual agent performance, not by resolved systemic issues.

---

## Prioritized Change Matrix

| Rank | Issue | Agent | Impact | Frequency | Complexity | Priority | Proposed in N engagements |
|------|-------|-------|--------|-----------|-----------|----------|--------------------------|
| 1 | Innovate archetype absent | bcg-segment-analyst | HIGH | 15/15 | MEDIUM | P1 | 13 engagements — never applied |
| 2 | Topic-style section headers | bcg-production | HIGH | 13/15 | LOW | P1 | 10 engagements — never applied |
| 3 | Strategy count too low for Cash Cow/Dog | bcg-segment-analyst | HIGH | 9/15 | LOW | P1 | 7 engagements — never applied |
| 4 | TAM upper-end selection / cross-file discrepancy | bcg-market-mapper + bcg-data-scientist | MEDIUM-HIGH | 11/15 | MEDIUM | P1 | 8 engagements — never applied |
| 5 | WAU/MAU conflation | bcg-market-mapper | MEDIUM | 4/15 (AI engagements: 4/4) | LOW | P1 | 4 engagements — never applied |
| 6 | Competitor revenue currency (forward vs. actual) | bcg-market-mapper | MEDIUM-HIGH | 7/15 | LOW | P2 | 5 engagements — never applied |
| 7 | Competitor revenue misread / IPO conflation | bcg-segment-analyst | HIGH (when present) | 5/15 | MEDIUM | P2 | 3 engagements — never applied |
| 8 | Revenue projection exceeds sub-market TAM | bcg-segment-analyst | MEDIUM-HIGH | 5/15 | LOW | P2 | 4 engagements — never applied |
| 9 | Unverified corporate events stated as fact | bcg-market-mapper | MEDIUM | 3/15 | LOW | P2 | 3 engagements — never applied |
| 10 | Analytically constructed figures not labeled | bcg-domain-expert | MEDIUM | 4/15 | LOW | P2 | 2 engagements — never applied |

---

## P1 Changes Applied in This Review

### Applied Change A: bcg-segment-analyst.md — Mandatory Strategy Count + Archetype Completeness Gate

**What changed:** Added "ОБЯЗАТЕЛЬНЫЙ КОНТРОЛЬ КАЧЕСТВА СТРАТЕГИЙ" section with three blocking gates:
1. Archetype Completeness Gate — mandatory table listing strategy count by archetype; minimum counts by MBB position (Star/QM: 10-15 / Cash Cow: 8-12 / Dog: 6-10); explicit statement that Dog with 2 strategies is a summary not an analysis
2. Innovate Archetype Gate — precise definition of what qualifies as Innovate vs. does not; positive examples (ambient commerce, ARM-of-AI-silicon, process intelligence subscription); negative examples (geography expansion, AI feature additions, price cuts); mandatory INNOVATE GAP statement if 2 genuine Innovate strategies cannot be produced
3. Financial Parameters Validation Gate — source validation (quote what the source actually says), revenue impact ceiling check (implied share >30% requires rewriting), fleet/unit math check, unverifiable data gate

**Rationale:** 15/15 engagements had Innovate absent. 9/15 had strategy count below minimum. These are the two highest-frequency structural failures in the corpus. The prior prompt instruction ("Generate 10-15 strategies covering all five archetypes") was present but had no enforcement mechanism. Gates create blocking conditions that prevent file save without addressing the gaps.

**Expected improvement:** Innovate archetype present in at least 50% of segments (vs. ~5% currently); Cash Cow and Dog segments consistently reach minimum strategy counts; revenue projections consistently checked against TAM ceiling.

### Applied Change B: bcg-production.md — Pyramid Principle Header Standard with Blocking Self-Check

**What changed:** Replaced the existing single-line header instruction with an explicit "СТАНДАРТ ЗАГОЛОВКОВ РАЗДЕЛОВ — СТРОГО ОБЯЗАТЕЛЕН" section containing:
- Explicit test for every header ("Does this answer 'So what?' or only announce the topic?")
- Prohibited (topic-style) headers with exact examples from prior engagements
- Required (conclusion-style) headers with calibrated examples for segment deep dives
- Mandatory template for segment headers: "[Segment]: [single most important strategic implication]"
- Sub-header examples converting generic topics to specific conclusions
- Blocking self-check before file save: read only headers; if headers-only reading is uninformative, rewrite before saving

**Rationale:** 13/15 engagements with partial or full Pyramid Principle failure in section headers. The agent demonstrably can write strong conclusion headers (proved by AWS, Advertising, and Intel headers) but does not apply the standard uniformly. The issue is selective application under length pressure, not inability. A blocking self-check test forces uniform application.

**Expected improvement:** Headers-only reading of the final report conveys the full strategic argument; significant reduction in topic-style headers in Parts II-IV.

### Applied Change C: bcg-market-mapper.md — TAM Source Hierarchy + WAU/MAU Discipline + Corporate Event Protocol

**What changed:** Added three mandatory discipline sections to the market mapper:
1. TAM Source Tier Hierarchy (Tier 1: Goldman/IDC/Gartner/Canalys vs. Tier 3: MarkSpark/aggregators); Tier 3 estimates >3x Tier 1 must be labeled as "aggressive bull case"
2. TAM Scope Gate: TAM must match segment boundary; if TAM > 3x sum of top-5 players' disclosed revenues, the definition is likely too broad
3. Competitor metric discipline: WAU and MAU must be explicitly labeled as WAU or MAU with source and date; no conflation permitted
4. Corporate event protocol: M&A completions, partnerships, executive changes less than 6 months old require two primary sources or [UNVERIFIED] flagging

**Rationale:** TAM selection bias in 11/15 engagements; WAU/MAU conflation in 4/15 (100% of AI engagements where this applied); unverified corporate events (Groq acquisition in AMD) propagated uncorrected through full engagement. All three are preventable with explicit labeling requirements.

**Expected improvement:** TAM figures consistently anchored to Tier 1 sources; ChatGPT and similar consumer AI user metrics correctly labeled as WAU; M&A events flagged for fact-checker verification.

---

## What Worked Well Across the Corpus

**1. bcg-fact-checker is the strongest and most consistent agent.** Average score 4.5/5 across all 15 engagements. Score range: 4.0–4.8. The agent has proven the "Corrected Data Table for Portfolio Analysis" format, the structured claim-by-claim verification table, and the hypothesis validation map. These structural outputs have been adopted and maintained for 10+ consecutive engagements. The ASML engagement (2.2% hallucination rate, 16 searches, 93 claims) is the best single fact-check performance in the corpus.

**2. bcg-portfolio-analyst has improved consistently.** The "validation corrections applied at top of document with before/after language" practice has been maintained for 8 consecutive engagements. DICE Framework completion with named binding constraint is now standard. Three-scenario NPV with probability weights appears in 7 of the last 10 engagements. The Intel "Kodak Trap" portfolio imbalance diagnosis and AMD three-scenario NPV ($14-16B base / $22-28B optimistic / $4-8B pessimistic) are the strongest individual portfolio outputs in the corpus.

**3. bcg-domain-expert consistently delivers the most analytically distinctive content.** The Apple-Gemini distillation-as-platform insight (Google DeepMind), ASML "Process Intelligence Company" reframing with €10-30M/fab pricing model, Meta DMA interoperability back-door threat, DeepSeek distillation economy Trojan horse dynamics, and AMD CoWoS supply ceiling are all non-obvious and directly influenced portfolio recommendations. Domain expert is the highest-variance agent (floor 4.2, ceiling 4.7) but consistently the highest originality.

**4. Final-report.md production has stabilized.** 10 consecutive successes (Intel through ASML) after the 4-engagement failure streak. The production agent appears to require a stable context budget — when earlier steps consume excess context (rate limits, retries), production reliability drops.

**5. Hypothesis coverage has improved.** The improvement log shows 10/10 hypotheses covered in the last 5 engagements with verdicts, which was rare in early engagements. This is the single most visible quality improvement across the corpus.

---

## Recommendation for Next Engagement

**Priority 1 (apply before next segment analysis):** The three P1 agent changes have been applied to the agent files in this review. The Innovate archetype gate, strategy count floor, and financial validation gates in bcg-segment-analyst.md will have the largest measurable impact. Verify these gates are enforced in the agent log output.

**Priority 2 (apply at market mapping stage):** The TAM source hierarchy and WAU/MAU discipline changes in bcg-market-mapper.md will prevent the most common data quality errors at their origin point (market-map stage) rather than requiring fact-checker correction downstream.

**Priority 3 (apply at production stage):** The header self-check in bcg-production.md requires only 2 minutes of review before file save. It directly addresses the most visible client-facing quality gap in 13/15 engagements.

**Unresolved P2 items proposed for manual application by engagement lead:**
- bcg-data-scientist: cross-file TAM reconciliation protocol (proposed in AMD Change 2, Intel Change 2, Baidu Change 4 — never applied)
- bcg-segment-analyst: competitor revenue verification for recently-listed companies (Baidu Change 1)
- bcg-segment-analyst: revenue projection TAM ceiling check (Microsoft Change 4 — now incorporated into bcg-segment-analyst gate)
- bcg-domain-expert: analytically constructed figures labeling requirement (Meta engagement proposed change)
