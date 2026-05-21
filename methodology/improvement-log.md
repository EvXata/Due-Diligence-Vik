# MBB Team — Methodology Improvement Log
*История улучшений системы анализа по результатам engagement-ов*

---

## 2026-05-20 — Microsoft Strategic DD engagement

**Overall:** Pipeline completed successfully (CONDITIONAL LONG verdict, 4 decision layers + 8 supporting analyses), но wall-clock 3h 16m vs план 50-70min (4-5x overrun); 3 agent timeouts; Phase 2 portfolio bottleneck = 104 min single-agent wall-clock.

### Root causes identified
1. **Tier-2 sprawl** — 4 отдельных Tier-2 segment-analysts вместо группового pass (Microsoft: LinkedIn + Dynamics + Search + Windows/On-prem × 7-11 min each в parallel wave, фактически не давало speedup т.к. Tier-1 Azure был bottleneck)
2. **Portfolio agent context overload** — full reads 7 segment-*.md файлов (>500KB суммарно) → stream idle timeout (149 min first attempt, 104 min retry)
3. **Unbounded WebSearch** — Azure Tier-1 segment-analyst использовал 21 поиск (cap был 22), wall-clock 26:44 заблокировал всю Phase 1 wave
4. **No retry strategy** — failed агенты перезапускались с оригинальным prompt вместо EFFICIENCY MODE prefix
5. **No target word counts** — Sonnet писал 8-15K-word outputs, вызывая socket timeouts на агентах с большим контекстом

### Changes applied (P1 — auto-applied 2026-05-20)
1. **bcg-market-mapper.md** — Tier-1 hard cap 3 segments; новые критерии: revenue ≥15% AND value creation potential. Tier-2 grouping rule: ALL non-Tier-1 → ОДИН batched run.
2. **bcg-segment-analyst.md** — новый режим `tier=2-batch` (один agent обрабатывает 2-5 Tier-2 сегментов, output: ОДИН файл `segment-tier2-grouped.md`, WebSearch budget 12 на весь batch); Tier-1 WebSearch hard cap снижен с 22 → 16 с cap enforcement на 87.5%
3. **bcg-portfolio-analyst.md** — STRICT READING DISCIPLINE: PRIMARY (digest + segment-tier2-grouped), SECONDARY (только Grep по Tier-1 файлам), FORBIDDEN (full reads всех segment-*.md)
4. **dd/SKILL.md** — Phase 1 launch logic переписана: max 3 Tier-1 + 1 Tier-2 batch + 1 domain-expert = 3-5 agents (было до 8+); добавлен EFFICIENCY MODE recovery pattern; добавлена Target Length Table на все agent prompts

### Expected impact (target benchmarks для следующего mega-cap DD)
- Phase 1 wall-clock: 26:44 → 15-20 min (-25 to -45%)
- Phase 2 wall-clock: 104 min → 8-15 min (**-85%**)
- Phase 1.5/DD-1 wall-clock (с retry): ~26 min → ~12 min (-55%)
- **Total wall-clock на mega-cap DD: 3h 16m → ~1h 30m-2h (-40 to -55%)**
- Agent calls Phase 1: 8 → 5 (-37%)
- Failure rate: 21% (3/14) → target <5%

### Preserved (NOT changed)
- 5 lenses framework
- Segmentation principle (competitor existence test)
- 10 DD hypotheses standard
- 15 rules of dd-output-standard.md
- Tier-1 archetype completeness gates
- Rule 14 (3+ refuted → automatic PASS)
- Quality bar (verified data tags ✅/⚠️/❌)

### Methodology principle reinforced
**Приоритизация > параллелизм.** Запуск 8 агентов параллельно не быстрее запуска 5 правильно отобранных агентов, когда bottleneck — один Tier-1 сегмент. Группировка некритичных сегментов в один batch + снижение search caps на критичных = главный рычаг оптимизации.

---

## 2026-04-10 — GlobalFoundries (GFS) engagement

**Overall Quality:** A-
**Weakest agent:** bcg-segment-analyst (Home & Industrial IoT) — 4.2 / 5 — IoT-specific foundry TAM ($15–22B) is double-estimated (Tier 3 market report × estimated IoT share ratio); IFRS/Non-IFRS net income confusion ($965M presented without qualifier); D3 (MIPS RISC-V IP bundling) and I2 (AI-Native IoT Platform) are delivery-model variants of the same MIPS-for-edge-AI hypothesis; two consecutive years of strategy overlap with different IDs
**Second weakest agent:** bcg-data-scientist — 4.5 / 5 — Node-tier revenue splits (used to compute $53B SAM) are Tier 2/3 sourced; ±15% uncertainty on key node-tier assumption acknowledged but not propagated into forward revenue estimates ($7.2–7.8B FY2026 stated with more precision than inputs justify); downside scenario for SiPh failure absent from growth analysis section

**Top 3 issues:**
1. GTM Playbook narrative redundancy persists (fifth consecutive engagement) — Part V individual GTM play narratives re-describe competitive context and strategic rationale present in Part III; approximately 200–300 words per GTM play are redundant in this engagement (declining from 800/600/400 words in Samsung/Apple/Alphabet but not eliminated); severity declining confirms prior changes are partially effective; structural scope restriction needed to eliminate residual [bcg-production]
2. A&D FY2030 revenue target ($450–600M base case) mathematically approaches or exceeds estimated US Trusted Foundry TAM ($500–800M lower bound); fact-checker correctly identified the ceiling breach (75–120% share) and flagged it ⚠️; neither fact-checker nor portfolio analyst resolved it — the breach propagated to final report with only a footnote caveat; third confirmed occurrence of ceiling breach noted but unresolved before downstream passing [bcg-segment-analyst + bcg-fact-checker]
3. Self-derived TAM (RF SOI $6–8B; IoT $15–22B) labeled in footnotes rather than prominently at top of TAM section; strategy revenue targets stated against these TAMs pass ceiling checks only because targets are small relative to an uncertain denominator; downstream agents (fact-checker, portfolio analyst) inherit the circularity without adequate weight [bcg-market-mapper + bcg-segment-analyst]

**Additional issues noted:**
4. NVIDIA $2B investment in Lumentum/Coherent — marked ⚠️ QUESTIONABLE in validation report but no WebSearch replacement figure proposed; standard requires flagged claims to either be verified with a replacement or removed from downstream use; final-report.md CID/SiPh section cites the figure without ⚠️ qualifier [bcg-fact-checker]
5. Smart Mobile D1 (9SW qualification) / F3 (FR3 design win lock-in) are sequential phases of one 6G opportunity, not independent strategic bets; Smart Mobile D2 (managed harvest) / F1 (focus on sole-source only) both produce identical outcomes ($2.0–2.2B floor); effective distinct strategy count is ~55–57 of 61 stated (not a blocking issue — all segments still meet minimums — but dilutes strategic completeness) [bcg-segment-analyst (Smart Mobile)]

**Proposed prompt changes:** 3 changes (see /research/globalfoundries-10.04.2026/methodology-review.md)
- Change 1 (GTM Playbook Narrative Scope Gate): bcg-production — Part V content restricted to ICP one-sentence definition, 5-step channel sequence with timeline, ACV/deal-cycle/NRR three-row table, and first-90-days with one named action/counterparty/binary milestone; sentences describing why the market is attractive, what GFS's competitive advantage is, or what the strategy recommends must be deleted from Part V (all covered in Parts II–IV); any sentence that could appear in Part III must be removed from Part V — HIGH confidence
- Change 2 (Self-Derived TAM Prominence Protocol): bcg-market-mapper + bcg-segment-analyst — When no Tier 1 or Tier 2 source publishes the segment TAM as a named line item, place a ⚠️ TAM — NO INDEPENDENT SOURCE warning at the TOP of the TAM section (not in a footnote) before any numbers; warning must state the derivation methodology and explicitly note that all strategy revenue targets using this TAM carry the same uncertainty — HIGH confidence
- Change 3 (Niche Segment Revenue Ceiling Resolution Protocol — extension of Amkor Change 3): bcg-segment-analyst — After computing FY2030 base case revenue target, compute implied share of estimated TAM; if share exceeds 50% for a non-dominant participant or 80% for any participant, resolve within the segment by one of: (a) revise target to credible share; (b) provide expanded TAM with named source accommodating new revenue streams; (c) label target "not independently constrained"; do NOT flag and pass unresolved to downstream agents — HIGH confidence

**Applied immediately:** All 3 changes are HIGH confidence. Change 1 is highest priority (5-engagement confirmed pattern). Change 3 extends an existing rule from impossible market share to forward projection ceiling breaches — third confirmed occurrence requiring the extension.

**What worked well:**
- bcg-domain-expert (4.8 / 5) — highest-quality domain expert output in any semiconductor engagement in the corpus; TSMC COUPE window identified with April 2026 sources (real-time); ICFR-to-DFARS audit risk chain is the highest-value non-obvious insight in the engagement; LTSA downcycle analysis correctly distinguishes revenue-smoothing from revenue-guarantee; all 10 hypotheses validated with explicit insider logic and contradicting evidence; no over-confirmed verdicts
- Validation-report correction propagation clean — all three corrections (automotive +17%, IFRS $888M, Microchip $5.8B) acknowledged by name in portfolio.md preamble and propagated correctly to final-report.md prose; first clean propagation after addressing Micron/Amkor partial propagation failures
- bcg-fact-checker — 80 claims across 5 segments; TSMC COUPE confirmed with April 2026 sources on engagement date; ceiling test on A&D FY2030 target performed; all corrections structured with replacement language; automotive YoY growth error (+15.6% vs. +17%) caught; IFRS/Non-IFRS distinction resolved
- All 10 hypotheses explicitly resolved with intellectual honesty — H-D2 correctly weakened (IP accumulation narrative), H-F1 correctly reframed (GFS does not operate at sub-5nm), H-A2 correctly nuanced (DoD contract vs. policy cycle distinction); no force-confirmed verdicts

**Data quality metrics:**
- Average Data Quality Score across 5 segments: B (82% average: Smart Mobile 78%, Automotive 89%, IoT 71%, CID/SiPh 88%, A&D 86%) — MEDIUM-HIGH
- Best segment: Automotive (B — 89% verified) — Mordor Intelligence TAM/CAGR verified; GFS revenue confirmed; all partnership announcements sourced to GlobeNewswire press releases; one minor YoY growth rate error caught and corrected
- Worst segment: Home & Industrial IoT (B — 71% verified) — IoT foundry TAM is Tier 3 derived; $965M net income labeling error; silicon-specific IoT market research is the weakest sub-market coverage in any specialty semiconductor engagement
- Total claims checked: 80 | Total ✅ verified: 65 (81%) | Total ⚠️ questionable: 12 (15%) | Total ❌ hallucinated/inconsistent: 3 (4%) | Error rate: 4%
- Error rate of 4% matches Alphabet engagement as the corpus floor; 9th consecutive engagement at ≤7%; the 4% floor appears stable across semiconductor and technology companies with strong SEC disclosure

**Cross-engagement pattern summary (as of this engagement, 27 engagements total):**
- GTM/Part V narrative redundancy at declining severity: 5/5 most recent engagements (Samsung 800→Apple 600→Alphabet 400→GFS 200–300 words); prior changes reduce but do not eliminate; Change 1 addresses root cause (content scope restriction rather than word-count reduction)
- A&D / niche segment revenue ceiling breach passed unresolved: 3/3 confirmed occurrences (Micron AEBU, Amkor Automotive, GFS A&D); Amkor Change 3 covered impossible market share (>100%); this engagement extends the pattern to forward projections approaching TAM ceiling (>50%); Change 3 adds the extension
- Self-derived TAM (circular calculation) labeled in footnotes: FIRST EXPLICIT IDENTIFICATION in log; mechanism present in 2–3 prior specialty semiconductor engagements; Change 2 directly addresses with prominence requirement
- bcg-fact-checker consistently strongest agent: 27-engagement track record; 4% error rate matches corpus floor; semiconductor-specific investigative quality (process node distinctions, contract structures, subsidy program details) maintained
- bcg-domain-expert improving for semiconductor engagements: GFS at 4.8/5 is highest-quality semiconductor domain expert in corpus; Alphabet at 4.8/5 was highest consumer technology; the pattern of domain expert being the most analytically differentiated agent is now consistent across company types
- All-hypotheses-resolved standard maintained: 5 consecutive engagements with all 10 hypotheses explicitly closed; GFS is the strongest hypothesis architecture for any semiconductor company in the corpus
- Validation-report correction propagation protocol working: 2 consecutive clean engagements (Alphabet, GFS) after Micron/Amkor partial propagation failures; Amkor Change 4 (full propagation checklist) confirmed effective

**Priority action for next engagement lead:** Apply Change 1 (GTM Playbook Narrative Scope Gate) to bcg-production before the next engagement — 5-engagement confirmed pattern; the severity-declining trend confirms prior changes work but the scope restriction (not word-count reduction) is the structural fix needed to eliminate residual. Apply Change 3 (Niche Segment Revenue Ceiling Resolution Protocol extension) for any engagement with a non-disclosed segment or nascent platform revenue — third confirmed occurrence pattern is now above the CONFIRMED threshold.

---

## 2026-04-09 — Alphabet Inc. (GOOGL) engagement

**Overall Quality:** A-
**Weakest agent:** bcg-segment-analyst (Subscriptions/Platforms/Devices) — 3.7 / 5 — only 4 strategies vs. 8-minimum for a Question Mark; Innovate and Focus archetypes absent; smart home CAGR (27%) is the most aggressive unverified market claim in the engagement (Grand View Tier-2 only); App Store TAM figures all Tier-2; segment internal heterogeneity (Play + Pixel + Nest + Google One) makes the shared advantage argument diffuse
**Second weakest agent:** bcg-segment-analyst (Other Bets/Waymo) — 4.0 / 5 — only 2 strategies (D1, S1) vs. 8-minimum for a Question Mark; B2B fleet licensing, Toyota consumer vehicle software licensing, international expansion, and IPO preparation are all distinct strategic options that were not developed; Pivot, Focus, and Innovate archetypes absent

**Top 3 issues:**
1. Innovate archetype absent across all five segments — the Innovate (I) archetype produced zero strategies in this engagement despite Alphabet being one of the most AI-transformation-intensive companies in the corpus; the current archetype gate ensures I strategies are present when submitted but does not prevent the agent from simply generating thin or absent I coverage in the first place; concurrent with phase-conflation issue from Apple engagement, this confirms the archetype presence gate is insufficient — the quality of I strategies must also be enforced [bcg-segment-analyst — all five segments]
2. Question Mark strategy count floor not enforced — SPD (4 strategies) and Waymo (2 strategies) both fall below the 8-minimum for a Question Mark BCG position; the Samsung Change 2 (strategy count blocking gate) uses Star/Cash Cow/Dog minimums (10/8/6) but does not explicitly state a minimum for Question Mark; the agent defaults to low effort in segments perceived as strategically subordinate [bcg-segment-analyst — SPD and Waymo segments]
3. Data-scientist benchmark temporal mismatch — competitor benchmark table compares Alphabet's 2025 metrics against most peers' 2024 data (Microsoft FY2024, Meta Q4 2024, Apple FY2024) despite 2025 full-year data being available and used by the researcher in company-brief.md; same temporal scope mechanism as Apple engagement (quarterly vs. annual) applied to the cross-company benchmarking axis rather than within-company metrics; creates a systematic overstatement of Alphabet's relative performance improvement in ROIC and margin trend analysis [bcg-data-scientist]

**Additional issues noted:**
4. Part V strategy section partially re-summarizes Part III — approximately 400 words in Part V re-describe strategies already detailed in Part III; below the 600–800 word level seen in Samsung/Apple/Micron (indicating Samsung Change 3 has partially taken effect) but present; 5th consecutive engagement with this pattern at declining severity [bcg-production]
5. Waymo valuation error caught but highlight of correction propagation success — Waymo $100B (pre-close guidance) stated in segment files; fact-checker correctly identified the $126B post-close figure and flagged it; portfolio analyst applied correction by name at document preamble; final-report contains inline correction note; this is the correction propagation protocol working correctly — contrasting with Micron/Amkor where propagation was incomplete

**Proposed prompt changes:** 4 changes (see /research/alphabet-09.04.2026/methodology-review.md)
- Change 1 (Innovate Archetype Mandatory Generation): bcg-segment-analyst — An Innovate strategy must describe a business model, product category, or revenue stream that does not currently exist for this company in this segment; it cannot be a variant of an existing product; if no I strategy is technically viable, state "I: Not viable for this segment in this time horizon — [reason]" rather than omitting; valid I patterns: new pricing model, new customer segment served for the first time, new supply chain position, new regulatory category — HIGH confidence
- Change 2 (Question Mark / Dog Strategy Count Floor): bcg-segment-analyst — Add Question Mark explicitly to the minimum count requirements at 8 strategies; provide structural template for Question Mark segments: 2×D, 2×S, 1×P, 1×F, 1×I, 1×exit strategy (IPO/JV/divestiture); self-check: count before submission; template specifically designed for nascent segments where strategic option space is broader than mature segments — HIGH confidence
- Change 3 (Cross-Company Benchmark Temporal Parity Gate): bcg-data-scientist — All peer metrics must use the most recently completed fiscal year available as of engagement date; if target company has FY2025 data, all peers must use FY2025 if available; explicitly check whether company-brief.md or market-map.md contains more recent data for any peer than what the table uses; note fiscal year in table footnote; never compare target company's most recent year against competitors' prior year without explicit temporal mismatch labeling — HIGH confidence
- Change 4 (Part V Incremental Content Enforcement — Strengthened): bcg-production — Part V must NOT re-describe strategies already detailed in Part III; for any paragraph in Part V that describes what a strategy involves (rather than why it was selected, what the key assumption is, or what happens first in execution), delete or move to Part III; Part V contains exclusively: (a) selection logic with quantified trade-offs vs. alternatives; (b) single most critical assumption with failure signal; (c) portfolio-level risk correlation analysis; (d) 30/90/180-day implementation sequence with named owners and measurable KPIs — HIGH confidence

**Applied immediately:** All 4 changes are HIGH confidence — recommended for immediate manual application. Change 1 (Innovate mandatory generation) is highest priority — 4-engagement confirmed absence pattern across Apple, Samsung, Amkor, and Alphabet; addresses the most analytically significant quality gap in the current corpus.

**What worked well in this engagement:**
- bcg-fact-checker (4.7 / 5) — strongest conglomerate fact-checking in corpus; 116 claims across 5 structurally different markets; AWS annual/quarterly conflation catch required understanding Amazon's quarterly vs. annual reporting cadence; Netflix subscriber count required going to Netflix Q4 2025 earnings directly; Waymo pre-close vs. post-close valuation distinction ($100B vs. $126B) required knowing the February 2026 Series D close date; all investigative, not mechanical; tabular format with stated/verified/status/source is the reference standard
- bcg-domain-expert (4.8 / 5) — highest-quality competitive dynamics in any consumer technology engagement in the corpus; five dynamics all go beyond financial analysis: AI Overview citation bifurcation (cited brands earn 91% more paid clicks — winner-take-most dynamic invisible in aggregate CTR), Apple deal annual renegotiation as structural leverage degradation (not just a one-time risk), ad tech second case structural overhang on YouTube's programmatic plumbing (not just Google Network), Waymo unit economics vs. valuation disconnect ($150–200K Jaguar vs. $30K Baidu Gen-6), Wiz multi-cloud neutrality tension (deal-by-deal resolution); all five sourced with primary URLs
- bcg-portfolio-analyst (4.8 / 5) — VERDICT on line 8 with $85–110B incremental revenue and $280–340B NPV; synergies described at mechanism level ("Search intent → Performance Max → Gemini bid optimization" flywheel, not "advertising synergies exist"); DICE score 7/16 with weakest-link identification (Wiz startup culture vs. Google process); all 10 hypotheses closed with honest INSUFFICIENT DATA for H-P1, H-S1, H-Waymo1; all 4 validation-report corrections applied at document preamble by name
- bcg-researcher (4.8 / 5) — Q4 2025 and full-year 2025 Alphabet earnings sourced correctly (engagement date April 9, 2026; earnings released February 2026); $240B cloud backlog and 30.1% Q4 2025 cloud margin — both strategically pivotal — captured and propagated correctly; 2020–2025 segment revenue table with source-per-row; ESTIMATED tags include derivation methodology for all estimated sub-line items
- Validation-report correction propagation — all four confirmed errors (AWS $128.7B, Netflix 375M subscribers, Waymo $126B, Palo Alto $9.2B) explicitly acknowledged by name in portfolio.md preamble and carried through to final-report.md with inline correction notes; first engagement in recent corpus where Amkor-type partial propagation error did not occur; confirms that Change 4 from Amkor engagement (full propagation checklist) is taking effect

**Data quality metrics:**
- Average Data Quality Score across 5 segments: B (80% of 116 claims verified) — MEDIUM-HIGH
- Best segment: Other Bets/Waymo (B — 85% verified) — Waymo operational data (rides/week, ARR, fleet size, valuation) all primary-sourced; math verification on rides/vehicle/day and revenue/vehicle/year explicit
- Worst segment: Subscriptions/Platforms/Devices (B — 72% verified) — Smart Home CAGR (27%) is the most aggressive unverified market claim; App Store and global smartphone TAM figures all Tier-2
- Total claims checked: 116 | Total ✅ verified: 93 (80%) | Total ⚠️ questionable: 19 (16%) | Total ❌ hallucinated/inconsistent: 4 (4%) | Error rate: 4% — lowest error rate in the entire corpus to date; 8th consecutive engagement at ≤7%; 4% is the new floor
- Overall data quality: B (80% verified) — best consumer technology / conglomerate engagement in the log; SEC transparency of Alphabet (segment revenue, operating income, and margin all primary-sourced) enables higher verification rates than hardware companies

**Cross-engagement pattern summary (as of this engagement, 26 engagements total):**
- Innovate archetype absent or phase-conflated: 4/4 most recent engagements (Apple Mac/iPad I1-I2 phase-conflation, Samsung 4/6 segments missing I, Amkor FOPLP/I1 same thesis, Alphabet all five segments absent I) — CONFIRMED SYSTEMATIC PATTERN, highest-severity unresolved quality issue in the corpus; Change 1 directly addresses; the archetype presence gate is insufficient without a substance gate
- Question Mark strategy count below minimum: NEW CONFIRMATION in this engagement (SPD 4 strategies, Waymo 2 strategies); combined with Samsung (5/6 segments below minimum), the strategy count gate is confirmed to not apply to Question Mark and Dog segments; Change 2 extends the gate explicitly
- Part V / Part III redundancy at declining severity: 5/5 most recent engagements (800→600→400 word trend); Samsung Change 3 partially effective; Change 4 (strengthened version) needed to eliminate residual
- Cross-company benchmark temporal mismatch: FIRST OCCURRENCE as data-scientist issue specifically; related to the Apple temporal scope gate (Change 1, Apple engagement) which addressed within-company metrics; Change 3 extends to cross-company benchmarking axis
- Validation-report correction propagation working: FIRST CLEAN ENGAGEMENT after Micron/Amkor partial propagation failures; Amkor Change 4 (full propagation checklist) appears effective; monitor for one more engagement before confirming pattern resolved
- bcg-fact-checker consistently strongest agent: 26-engagement track record; Alphabet engagement error rate of 4% is the new corpus floor; investigative quality maintained across structurally different market segments
- bcg-portfolio-analyst stable at highest performance tier: 4.8/5 for third time in last 5 engagements; synergy mechanism specificity and DICE integrity score maintained; hypothesis closure intellectual honesty (INSUFFICIENT DATA used appropriately) is a rare quality maintained consistently

**Priority action for next engagement lead:** Apply Change 1 (Innovate archetype mandatory generation) before the next engagement — 4-engagement confirmed absence pattern is the most analytically significant quality gap in the current corpus. Change 2 (Question Mark strategy count floor with structural template) is second priority — the template specifically helps with nascent/small segments where the agent defaults to low-effort coverage. Both changes address patterns that reduce the strategic completeness of deliverables in ways that are visible to clients.

---

## 2026-04-09 — Amkor Technology, Inc. engagement

**Overall Quality:** A-
**Weakest agent:** bcg-segment-analyst (Consumer/IoT) — 4.1 / 5 — JCET mainstream revenue overstated 2x ($2–3B stated vs. $1.0–1.5B actual per JCET 2024 annual report ">72% advanced packaging"); D1/P3/F3 strategies are three IDs for the same geopolitical tariff hedge; FOPLP source attribution unverifiable; FOPLP/I1 strategy pair are the same thesis under different naming
**Second weakest agent:** bcg-segment-analyst (AI/HPC) — 4.2 / 5 — ASE gross margin comparison uses ATM-only 2025 segment margin (23.5%) against Amkor consolidated 2025 (14.0%); correct like-for-like is Amkor 14.0% vs. ASE 17.7% (2025 consolidated) — stated gap 2.6x actual gap

**Top 3 issues:**
1. Competitor margin comparison scope mismatch — AI/HPC segment compares ASE ATM-2025-segment margin (23.5%) against Amkor consolidated-2025 margin (14.0%); correct like-for-like shows 3.7pp gap, not 9.5pp; stated gap inflates competitive urgency by 2.6x; same mechanism as Apple engagement annual/quarterly conflation (different scope axis: segment vs. consolidated rather than quarter vs. annual); caught by fact-checker and corrected in portfolio.md tables but final-report.md prose retains original incorrect figure [bcg-segment-analyst (AI/HPC) + bcg-production]
2. Third-party estimate presented as primary source disclosure — Mobile SiP segment states "Amkor 2025 10-K confirms approximately $3,080 million in SiP-related advanced packaging"; the 10-K discloses only Advanced Products ($5,556M) and Mainstream Products ($1,152M); the $3,085M figure is from DCF Modeling (third-party analysis site), not a 10-K line item; third consecutive engagement with this pattern (Micron: CXMT share methodology; Apple: Samsung MX extraction) — CONFIRMED SYSTEMATIC PATTERN [bcg-segment-analyst]
3. Validation-report correction partial propagation — ASE margin correction applied in portfolio.md structured table but final-report.md Part III prose narrative retains "ASE's 23.5% ATM segment gross margin versus Amkor's 14.0% overall"; data tables corrected, surrounding prose not updated; first occurrence of this specific mechanism (tables vs. prose divergence) [bcg-production]

**Additional issues noted:**
4. Impossible market share self-acknowledged but not resolved — Automotive segment computes OSAT-addressable TAM from Tier-3 40% penetration rate, producing Amkor share of 61% (impossible); analyst correctly flags within segment file but does not provide an alternative denominator with primary source; portfolio analyst must independently construct alternative framing ($1.2B / $4.9B total = 25%); downstream agents should not need to resolve upstream denominator errors [bcg-segment-analyst (Automotive) + bcg-market-mapper]
5. Strategy ID overlap — Mobile SiP D3 (Vietnam SiP Margin Optimization) and S1 (Scale Vietnam to 3.6B items/yr) are the same Vietnam capacity ramp program at different naming angles; Consumer segment D1/P3/F3 are three variants of the same Section 301 tariff hedge thesis; reduces effective distinct strategy count by 3–4 across the engagement [bcg-segment-analyst]

**Proposed prompt changes:** 4 changes (see /research/amkor-technology-09.04.2026/methodology-review.md)
- Change 1 (Source Attribution Precision Gate): bcg-segment-analyst — A data point is VERIFIED only if the named source explicitly states that specific number as a named line item; figures derived via third-party calculation from a primary filing must be tagged ESTIMATED even if the underlying primary source is valid; apply specifically when sub-line figures are cited for companies that do not disclose them — HIGH confidence
- Change 2 (Competitor Margin Comparison Scope Gate): bcg-segment-analyst — When comparing any financial metric between target company and competitor, verify both figures represent the same fiscal year AND the same reporting scope (both consolidated or both same segment type); never compare one company's consolidated figure against another company's division-only figure without explicit labeling; present both consolidated and segment margin when they differ materially — HIGH confidence
- Change 3 (Impossible Share Self-Correction Rule): bcg-segment-analyst + bcg-market-mapper — If (company revenue) / (computed TAM or sub-TAM) produces a share >50% for a non-dominant participant or >100% for any participant, the denominator is wrong; do not report the impossible figure; propose an alternative denominator with a Tier-2 source or present share against the next-wider market definition; resolve within the segment, not downstream — HIGH confidence
- Change 4 (Validation-Report Correction Full Propagation): bcg-production — For each ❌ or flagged correction in validation-report.md: verify the correct figure appears in every data table AND verify surrounding prose does not contain the original incorrect figure in any descriptive passage; a number corrected in a table but retained in prose is an incomplete correction — HIGH confidence

**Applied immediately:** All 4 changes are HIGH confidence — recommended for immediate manual application. Change 2 (scope gate) is highest priority — extends Apple engagement "temporal scope gate" to the segment/consolidated axis; this is the same error mechanism applied to a different dimension.

**What worked well in this engagement:**
- bcg-domain-expert (4.8 / 5) — highest-quality competitor re-ranking in hardware corpus; PTI threat re-rated from consensus LOW to HIGH (PiFO at 30% below CoWoS-L cost, fully booked through 2027, $1.4B investment); Dynamic 3 (FOPLP commoditizing Amkor's SiP/Fan-Out margin exactly as Arizona ramps) is the most strategically consequential non-obvious insight in the engagement; five dynamics all sourced with primary URLs
- bcg-fact-checker (4.6 / 5) — JCET ">72% advanced packaging" disclosure catch required reading JCET's own 2024 annual report and translating the implication for segment mix; this is investigative, not mechanical; ASE gross margin scope error (ATM-2025-segment vs. consolidated-2024) required simultaneous understanding of year and reporting scope — technically demanding; all 5 critical errors surfaced with exact replacement language
- bcg-portfolio-analyst (4.7 / 5) — all 5 validation-report corrections acknowledged by name before BCG matrix; "dangerous cash concentration in one cow" portfolio diagnosis with Apple = 30.8% of revenue named explicitly; internal capital conflict (Automotive underfunded by AI capex surge) explicitly stated as portfolio conflict; DICE completed with phased authorization recommendation tied to HDFO HVM binary outcome
- bcg-researcher (4.7 / 5) — Q4 2025 and full-year 2025 data current to within 60 days (engagement date April 9, 2026); 2026 capex guidance ($2.5–$3.0B, most strategically important single data point) VERIFIED from Q4 2025 earnings call; revenue verified for 2019–2025; all ESTIMATED tags include derivation methodology
- Hypothesis architecture — all 10 hypotheses closed; H-S5 (EMIB exclusivity) correctly rated INSUFFICIENT DATA rather than force-confirmed based on announcement; intellectual honesty maintained

**Data quality metrics:**
- Average Data Quality Score across 4 segments: B (70–75% verified per segment) — MEDIUM
- Best segment: Automotive (B — 75% verified) — Grand View Research TAM, JCET 34.2% automotive growth, Amkor automotive quarterly data all primary-sourced
- Worst segment: Consumer/IoT (B — 72% verified, 6% hallucinated/inconsistent) — JCET mainstream revenue 2x overstated; FOPLP source attribution unverifiable
- Total claims checked: 84 | Total ✅ verified: 59 (70.2%) | Total ⚠️ questionable: 20 (23.8%) | Total ❌ hallucinated/inconsistent: 5 (6.0%) | Error rate: 6.0%
- 7th consecutive engagement at ≤7% error rate; verifiable/questionable split continuing to improve
- Overall data quality: B (70.2% verified) — slightly below Samsung (78.7%) and Micron (76%) but above ByteDance (72%); consistent with specialized hardware companies where Chinese competitor sub-segment data is structurally unverifiable

**Cross-engagement pattern summary (as of this engagement, 25 engagements total):**
- Source attribution precision (third-party estimate presented as primary disclosure): 3/3 most recent non-Chinese-company engagements (Micron CXMT share, Apple Samsung MX, Amkor Advanced SiP) — CONFIRMED SYSTEMATIC PATTERN; mechanism: analyst cites most authoritative available figure without distinguishing whether the named source is the origin vs. a calculator from the origin; Change 1 directly addresses
- Competitor margin comparison scope mismatch (segment vs. consolidated, or different years): NEW CONFIRMED PATTERN — appears in 2 of last 3 semiconductor engagements (Apple: quarterly vs. annual; Amkor: segment vs. consolidated); same root mechanism (analyst retrieves most impressive/available figure without scope verification); Change 2 extends existing temporal scope gate to the segment/consolidated dimension
- Impossible market share not resolved before passing downstream: 2/4 semiconductor engagements (Micron AEBU TAM arithmetic, Amkor Automotive OSAT penetration) — EMERGING PATTERN; analyst correctly identifies the problem but does not resolve it, creating noise for downstream agents; Change 3 directly addresses
- Partial correction propagation (tables corrected, prose retains original error): FIRST OCCURRENCE — monitor for recurrence before escalating to confirmed pattern; Change 4 proposes a structural checklist fix
- Part IV / Executive Summary redundancy: NOT PRESENT in this engagement — Samsung/Apple engagement Changes 3/4 appear to have taken effect; Amkor Part V (GTM Playbook) is distinct from Part I Executive Summary; first engagement in recent corpus where this pattern is absent; positive trend
- bcg-fact-checker consistently strongest agent: 25-engagement track record; JCET disclosure catch and ASE scope error catch are both technically demanding; high-quality handoff format maintained
- bcg-portfolio-analyst stable at high performance: 4.7/5; all corrections applied, DICE substantive, hypothesis closure complete; no regression in 12 consecutive engagements
- bcg-domain-expert improving: highest score in hardware corpus; PTI competitive re-rating and FOPLP commoditization timing are the most consequential non-obvious insights in any OSAT engagement

**Priority action for next engagement lead (especially semiconductor/hardware companies):** Apply Change 2 (Competitor Margin Comparison Scope Gate) immediately — extends the confirmed Apple "temporal scope gate" to the segment/consolidated axis; the mechanism is identical and the fix is the same (verify scope before using any competitor margin figure). Apply Change 1 (Source Attribution Precision Gate) before any engagement where the company does not disclose sub-segment financials (most hardware companies report 2–4 categories, analysts routinely cite third-party sub-segment estimates as if they were primary disclosures).

---

## 2026-04-08 — Samsung Electronics Co., Ltd. engagement

**Overall Quality:** B+
**Weakest agent:** bcg-segment-analyst (NAND Flash) — 3.1 / 4 — NAND CAGR stated as 10–15% vs. actual 5–6% (Mordor Intelligence 2026–2031); enterprise SSD sub-segment CAGR (15.5%) conflated with total market; only 5 strategies vs. 10 minimum; missing Scale and Innovate archetypes; YMTC revenue share outdated (5–7% stated vs. 11% actual); data quality score C (69% verified) — lowest in engagement
**Second weakest agent:** bcg-production — 3.4 / 4 — Part IV ("Portfolio Synthesis") reproduces Part I ("Three Findings") content near-verbatim for the third consecutive engagement (~600–700 words of structural redundancy); one Geopolitical section heading is informational rather than conclusion-format

**Top 3 issues:**
1. Sub-segment CAGR applied to total market — NAND segment cited enterprise SSD CAGR (15.5%) as the overall NAND market CAGR; actual full-market CAGR is 5.32–5.87% (Mordor Intelligence); data-scientist had both figures simultaneously and did not flag the conflict; changed BCG positioning from confirmed Cash Cow to borderline Star [bcg-segment-analyst + bcg-data-scientist gap]
2. Strategy count below minimum across all 6 segments — DRAM (8), HBM (6), NAND (5), Foundry (5), SDC (5), Galaxy MX (5) vs. required 10-minimum; archetype gate (added March 2026) ensures all 5 archetypes present but does not enforce minimum count; Scale and Focus archetypes absent or thin in 4+ segments [bcg-segment-analyst]
3. Part IV / Executive Summary redundancy, third consecutive engagement — "Three Cross-Segment Synergies" in Part IV replicates "Three Findings" from Part I; Change 4 proposed in Apple engagement not yet applied to production agent prompt; confirmed structural pattern [bcg-production]

**Additional issues noted:**
4. HBM Q3 2025 Samsung share understated (22% stated vs. 35% actual per Counterpoint Research) — data-staleness / source-selection error; understated Samsung's recovery pace by 59%; caught by fact-checker; same mechanism as ByteDance/Runway ML and Apple/Samsung MX revenue errors [bcg-segment-analyst]
5. Internal OLED share inconsistency (41% Counterpoint vs. 48% UBI Research) persisted from market-map.md into segment analysis; both valid sources but inconsistency uncorrected until fact-checker resolution [bcg-segment-analyst + bcg-market-mapper]

**Proposed prompt changes:** 3 changes (see /research/samsung-electronics-08.04.2026/methodology-review.md)
- Change 1: bcg-segment-analyst — Sub-segment CAGR disambiguation gate: for every CAGR cited, state explicitly whether it applies to (a) full segment or (b) sub-segment/geographic subset; BCG positioning must use full-segment CAGR; if full-segment CAGR not found, state "NOT FOUND" rather than using sub-segment figure; self-check: if CAGR ≥ 2x slowest sub-segment rate, search for more conservative authoritative estimate — HIGH confidence
- Change 2: bcg-segment-analyst — Strategy count blocking gate: required minimums by BCG position (Star: 10 strategies; Cash Cow: 8; Dog: 6) with specific per-archetype minimums; self-check before submission; most commonly missing archetypes are Scale and Focus — explicit instruction to generate these if absent — HIGH confidence
- Change 3: bcg-production — Part IV incremental content requirement: Part IV must NOT repeat Part I; required incremental content: (1) alternatives explicitly rejected with quantified trade-offs; (2) single most important assumption with failure signal; (3) three first-30-day actions with named owner/deliverable/KPI; (4) portfolio cyclical resilience comparison (% structural revenue 2028 vs. today); self-check: read Part I then Part IV — any sentence that could appear in both must be rewritten — HIGH confidence

**Applied immediately:** All 3 changes are HIGH confidence — recommended for immediate manual application before next engagement. Change 3 is the most overdue (same pattern in ByteDance, Micron, Apple, Samsung = 4 consecutive).

**What worked well in this engagement:**
- bcg-fact-checker (4.0 / 4) — highest fact-checker score in any conglomerate engagement in the corpus; 94 claims across 6 segments; 20 documented searches; HBM Q3 2025 share correction (22% → 35%) required finding a Counterpoint Research source that contradicted a widely-circulated figure — investigative, not mechanical; corrected data table with exact replacement language for all 5 errors is production-quality handoff format; all 10 hypotheses closed in validation-report with supporting and contradicting evidence
- bcg-domain-expert (3.9 / 4) — strongest in corpus for semiconductor engagement; Dynamic 3 (chaebol organizational structure as root cause of Samsung foundry yield gap) is the most sophisticated causal analysis in recent memory — correctly identifies incentive structure (rewarding technology announcements over yield), decision lag (Chairman-level approval), and DS culture (foundry as second-tier vs. memory) as organizational root causes; Dynamic 1 (MR-MUF vs. TC-NCF packaging process war) explains Samsung's 2024 HBM failure as an architectural decision made in 2019, not a 2024 execution failure
- bcg-portfolio-analyst (4.0 / 4) — third consecutive perfect score; all 5 validation-report corrections acknowledged by name before BCG matrix; DICE Effort=3 correctly identified as binding constraint (simultaneous HBM ramp + foundry yield + Galaxy AI monetization at extreme organizational load); "Why the Surgical Focus Alternative Was Rejected" with 5 explicit reasons is model Pyramid Principle execution
- Hypothesis architecture (10/10) — intellectually honest "weakens" verdicts for H-A3, H-F2, H-S1; none over-confirmed; H-S1 ("optimal strategy = concentrate on Foundry/HBM; retreat from CE") correctly rated as "analytically correct but operationally constrained by chaebol structure" — rare and valuable intellectual honesty
- Q1 2026 real-time data capture — Samsung's April 7, 2026 preliminary earnings guidance (KRW 57.2T OP, KRW 133T revenue) incorporated day-of; without this, the urgency of the "supercycle window closing" thesis would be understated by ~4x

**Data quality metrics:**
- Average Data Quality Score across 6 segments: B (79% verified) — MEDIUM-HIGH; consistent with recent semiconductor engagements
- Best segments: Advanced Logic Foundry (B — 87% verified), HBM (B — 82% verified)
- Worst segment: NAND Flash (C — 69% verified) — only C-grade in engagement; CAGR error and YMTC share staleness are primary causes
- Total claims checked: 94 | Total ✅ verified: 74 (78.7%) | Total ⚠️ questionable: 15 (16%) | Total ❌ hallucinated/wrong: 5 (5.3%) | Error rate: 5.3% — continues improvement trend (below 7% corpus average)
- 6th consecutive engagement at ≤6% error rate; trend confirmed improving

**Cross-engagement pattern summary (as of this engagement, 24 engagements total):**
- Sub-segment CAGR applied to total market: 3/6 recent non-pure-play engagements — CONFIRMED SYSTEMATIC PATTERN; mechanism identical each time; Change 1 directly addresses; escalated from EMERGING to CONFIRMED
- Strategy count below minimum (5–8 per segment vs. 10): 4/4 most recent multi-segment engagements — CONFIRMED SYSTEMATIC PATTERN; archetype gate improved archetype coverage but not count; Change 2 directly addresses
- Part IV / Executive Summary redundancy: 4/4 most recent engagements (ByteDance, Micron, Apple, Samsung) — CONFIRMED STRUCTURAL PATTERN; most persistent unresolved pattern in log; Change 3 directly addresses; earlier proposed Change 4 (Apple engagement) not applied — must apply now
- HBM Q3 share understatement (22% vs. 35%): same source-staleness mechanism as ByteDance/Runway ML, Apple/Samsung MX revenue; 3/4 recent engagements with a "fast-moving private company or volatile market share figure" — data freshness gate (Change 2, ByteDance engagement) should extend to market share figures in high-velocity categories
- bcg-fact-checker consistently strongest agent: 24-engagement track record; Samsung HBM Q3 share correction is most consequential competitive intelligence catch in a Korean conglomerate engagement
- bcg-portfolio-analyst stable at high performance: 4.0/4; correction acknowledgment protocol maintained perfectly for 3 consecutive engagements; no regression

**Priority action for next engagement lead (especially multi-segment industrial/hardware companies):** Apply Change 1 (sub-segment CAGR disambiguation gate) immediately — 3-engagement confirmed pattern that takes under 60 seconds to check per segment. Apply Change 3 (Part IV incremental content requirement) to bcg-production before the next engagement — this is now a 4-engagement confirmed pattern with the single highest impact on client-facing document quality.

---

## 2026-04-08 — Apple Inc. engagement

**Overall Quality:** B+
**Weakest agent:** bcg-segment-analyst (Mac segment) — 4.0 / 5 — Microsoft Surface revenue cited as $8.9B (hallucinated; actual ~$5B based on Microsoft FY2024 Devices segment $4.7B); Dell CSG overstated by $2.6B; HP Personal Systems understated by up to $3.5B; Mac-I1 and Mac-I2 strategies are sequential phases of one strategy rather than independent strategic choices
**Second weakest agent:** bcg-production — 4.5 / 5 — Executive Summary and Part IV "Why This Strategy Wins" are substantively identical (~600 words of near-verbatim repetition); Part header naming inconsistent (hybrid topic/conclusion format across 4 of 6 parts)

**Top 3 issues:**
1. Annual vs. quarterly metric conflation — Services gross margin cited as "73.9% FY2025" when 73.9% is the FY2024 annual figure; FY2025 full-year gross margin is ~75–76% based on quarterly progression (Q3 FY2025: 75.6%); iPad full-year unit share cited as 44.9% when this is a Q4 2025 peak, not the full-year average (~40–43%); both errors follow identical mechanism — analyst used most recent/impressive data point without verifying temporal scope (annual vs. quarterly); appears in 2/5 segments of this engagement and in 3 of the last 5 engagements across the corpus [bcg-segment-analyst]
2. Inherited verification — Samsung MX Division revenue $74.5B tagged "Tier 1 VERIFIED" in market-map.md when Samsung does not separately disclose smartphone revenue; the $74.5B is an analyst extraction from the combined MX+Networks segment (~$94B / KRW 128.4T); fact-checker correctly reclassified to ESTIMATED; market-map.md itself not updated; third occurrence of over-inherited verification in the log (Micron: CXMT share; ByteDance: Runway ML; Apple: Samsung MX) [bcg-market-mapper]
3. Innovate strategy phase-conflation — Mac-I1 (on-device AI inference infrastructure) and Mac-I2 (Mac-as-a-Service for enterprise AI outcomes) are Phase 1 and Phase 2 of one strategy, not independent strategic bets; executing I1 is a prerequisite for I2; revenue ranges overlap ($5–10B vs. $3–5B); same pattern in iPad-I1 and iPad-I2 (both target enterprise/clinical buyer, both $3–5B revenue impact); ByteDance engagement had same issue in Lark segment; pattern is systematic [bcg-segment-analyst]

**Additional issues noted:**
4. Part IV = Executive Summary redundancy — "Why This Strategy Wins — Three Reasons" in Part IV reproduces the Executive Summary's "Three Findings" with different wording but identical information content (~600 words); second consecutive engagement with this pattern (Micron: ~800 words); production agent re-derives the verdict from inputs rather than building incrementally on Parts II and III [bcg-production]
5. Mac competitor revenue errors not caught by arithmetic check — Microsoft Surface $8.9B is 78% above the verifiable ~$5B figure; segment flagged it as ESTIMATED but did not attempt WebSearch to verify; the arithmetic gate (revenue/share/TAM triangulation) does not catch competitor revenue errors that lie outside the segment-level math [bcg-segment-analyst + bcg-fact-checker gap]

**Proposed prompt changes:** 4 changes (see /research/apple-08.04.2026/methodology-review.md)
- Change 1: bcg-segment-analyst — Temporal scope gate: for every percentage figure (market share, gross margin, growth rate), verify and explicitly state the time period it represents; distinguish full-year annual average, single quarter, trailing twelve months; quarterly peak/trough is not a valid substitute for full-year annual metric without explicit labeling — HIGH confidence
- Change 2: bcg-market-mapper — Segment extraction verification rule: a competitor revenue figure is VERIFIED only if the named competitor's own filing explicitly states that specific sub-line; figures derived from parent entity disclosures (Samsung MX from combined MX+Networks; Lenovo PC from Intelligent Devices Group) must be tagged ESTIMATED with derivation methodology documented regardless of source quality — HIGH confidence
- Change 3: bcg-segment-analyst — Innovate differentiation gate: before finalizing a segment with two or more I strategies, verify each passes three tests: (1) both pursable simultaneously without one being a prerequisite; (2) different customer segments/channels/technology platforms; (3) non-overlapping revenue ranges; if two I strategies fail this test, consolidate and generate a genuinely distinct second Innovate strategy — HIGH confidence
- Change 4: bcg-production — Part IV differentiation rule: Part IV must add information not in the Executive Summary; required incremental content: alternatives explicitly rejected with quantified trade-offs; single most important assumption the strategy depends on; first 30-day action with named owner and measurable trigger; if content duplicates Executive Summary, replace it with alternatives analysis and key swing factor — HIGH confidence

**Applied immediately:** All 4 changes are HIGH confidence — recommended for immediate manual application before next engagement.

**What worked well in this engagement:**
- bcg-fact-checker (4.7 / 5) — highest fact-checker score in any consumer technology engagement in the corpus; 80 claims across 5 segments; 28 documented searches; Samsung MX extraction catch (KRW 128.4T vs. $74.5B smartphone-only) required understanding Samsung's segmentation reporting methodology — analytically sophisticated beyond mechanical claim verification; corrected data table at end of validation-report with exact replacement language for all 7 flagged items is the model handoff format; hypothesis validation table 10/10 with supporting and opposing evidence columns; all 10 hypotheses closed with CONFIRMED / PARTIALLY CONFIRMED / INSUFFICIENT DATA
- bcg-portfolio-analyst (4.8 / 5) — VERDICT on line 8 with quantified $68–92B incremental revenue, +$400–600B NPV, 35–45% IRR; all 7 validation-report corrections acknowledged by name and applied before BCG matrix; 10-row synergy map with dollar estimates per synergy pair; three-scenario NPV with probability weights; DICE completed with substantive commentary on all 4 dimensions; Effort=3 correctly identified as binding constraint (three distinct organizational stretches: enterprise sales culture, foldable supply chain, medical regulatory expertise); all 10 hypotheses explicitly closed with confidence levels
- WHA segment (4.7 / 5) — strongest segment in the engagement; identified three-lane competitive dynamic (Garmin/fitness, Huawei/volume, Oura/subscription) that Apple must address simultaneously; FDA clearance moat quantified (Apple: 4 clearances; Samsung: 2; Garmin: 0; replication timeline: 18–36 months each); Biolinq wrist CGM FDA clearance as external weak signal demonstrates genuine market monitoring; no hallucinated figures — only segment in engagement with zero factual errors
- bcg-researcher — FY2020–FY2025 segment table with source-per-row, confidence tags, and FY2024 10-K accession number citation is production reference standard; Google TAC binary risk flagged in company overview before any agent raised it
- Google TAC coherence — all 6 agents independently identified and quantified the $20B Google TAC as the single largest strategic risk; no agent required explicit instruction to focus on it; analytical framework coherence across the full pipeline on a non-obvious risk factor

**Data quality metrics:**
- Average Data Quality Score across 5 segments: B (73.4% verified) — MEDIUM-HIGH; consistent with recent consumer technology engagements
- Best segment: Wearables (B — 71% verified, 0% hallucinated) — Garmin data fully verified from FY2025 earnings; Oura company guidance verified; competitor shares verified from Counterpoint full-year 2025
- Worst segment: Mac (B — 69% verified, 6% hallucinated/wrong) — Microsoft Surface $8.9B is the only ❌ in the engagement; Dell CSG and HP Personal Systems both in the questionable range
- Total claims checked: 80 | Total verified: 59 (73.75%) | Total questionable: 17 (21.25%) | Total hallucinated/wrong: 4 (5%) | Error rate: 5% — matches Micron engagement; below corpus average of ~7%
- 5th consecutive engagement at ≤5% error rate; improving trend confirmed

**Cross-engagement pattern summary (as of this engagement, 23 engagements total):**
- Annual/quarterly metric conflation: 3/5 most recent engagements — CONFIRMED SYSTEMATIC PATTERN; mechanism identical each time (analyst retrieves most recent/impressive figure without verifying temporal scope); Change 1 directly addresses; escalated from EMERGING to CONFIRMED pattern
- Inherited verification (parent source tier applied to derived sub-segment figure): 3/3 most recent non-semiconductor engagements — CONFIRMED SYSTEMATIC PATTERN; Samsung MX (Apple), Runway ML (ByteDance), CXMT share methodology (Micron); Change 2 directly addresses
- Innovate strategy phase-conflation (I1 and I2 as phases of one strategy): 2/2 most recent engagements (Apple Mac + iPad, ByteDance Lark) — EMERGING PATTERN; I archetype coverage requirement met on paper but strategic differentiation insufficient; Change 3 directly addresses
- Part IV = Executive Summary redundancy: 2/2 consecutive engagements (Apple, Micron) — CONFIRMED PATTERN; production agent interprets conclusion section as verdict restatement; Change 4 directly addresses
- final-report.md absent: 8/23 engagements (35% historical rate) — STABLE; no production failure in 6 consecutive engagements
- bcg-fact-checker consistently strongest agent: 23-engagement track record; Apple engagement at 4.7/5 matches Micron as highest single-engagement score; corrected data table format at validation-report end is now a structural standard
- bcg-portfolio-analyst stable at high performance: 4.8/5; DICE, hypothesis closure, validation-report correction acknowledgment all maintained as structural standards across 11 consecutive engagements

**Priority action for next engagement lead:** Apply all 4 changes from this engagement before the next engagement begins — all are HIGH confidence and address patterns present in 2–3+ of the most recent 5 engagements. Change 1 (temporal scope gate) is the highest-priority single addition: it eliminates an error class that has appeared in 3/5 recent engagements and requires 10 seconds of verification per data point.

---

## 2026-04-07 — Micron Technology, Inc. engagement

**Overall Quality:** A-
**Weakest agent:** bcg-segment-analyst (AEBU — Automotive & Embedded) — 3.8 / 5 — combined TAM lower bound ($15B) is mathematically inconsistent with Micron's own revenue ($4.75B) and stated market share (15-20%); minimum implied TAM is $23.75B, making the $15B lower bound logically impossible; multiple strategy financial parameters rest on single-source automotive sub-segment data; caught by fact-checker and corrected in portfolio but should not have required remediation
**Second weakest agent:** bcg-production — 4.6 / 5 — final-report.md successfully produced (no production failure); minor: AEBU TAM range in Part III not updated to corrected $20-30B (persists as $15-25B despite validation-report correction); CXMT share in CDBU competitor table retains pre-correction "~4-5%" rather than corrected "~4%"; three-reasons structure in Part IV is near-verbatim repetition of Part I findings without incremental insight (~800 words of redundancy)

**Top 3 issues:**
1. TAM/revenue/market-share internal arithmetic inconsistency — AEBU segment states combined addressable market $15-25B while simultaneously stating Micron revenue $4.75B at 15-20% market share; $4.75B / 0.20 = $23.75B is the mathematical minimum TAM; the $15B lower bound contradicts the analyst's own data; this check takes 10 seconds of arithmetic and should be a self-check before submission; validation-report correctly caught and proposed corrected range $20-30B; error was propagated into market-map and segment but not fully corrected in final-report.md [bcg-segment-analyst + bcg-production]
2. Validation-report corrections not fully propagated to final-report.md — fact-checker identified 4 critical issues and proposed corrections; portfolio-analyst applied all 4 at document preamble level; but final-report.md's AEBU section retains pre-correction TAM ($15-25B) and CDBU competitor table retains pre-correction CXMT share (~4-5% vs. corrected ~4%); correction flow: validation-report → portfolio.md preamble works; portfolio.md preamble → final-report.md per-segment prose does not work; structural pipeline gap [bcg-production]
3. Researcher conservative ESTIMATED tag on officially announced corporate event — company-brief.md labels the Crucial consumer business exit as "ESTIMATED (market reports; not officially confirmed)"; official Micron IR press release dated December 3, 2025 exists and was found by the segment analyst (who correctly tagged it VERIFIED); researcher appears to have missed the IR press release or applied a conservative default tag; required fact-checker intervention to correct; this class of error — conservative tagging of announced corporate events — is distinct from financial estimation and should not require remediation [bcg-researcher]

**Additional issues noted:**
4. CDBU segmentation rationale conflates BCG test outcome with analytical decision — market-map states "BCG Test: PASSED — with nuance" for CDBU; Kioxia demonstrably exists as a pure-play enterprise SSD company, which technically means the BCG separability test yields two sub-segments; the mapper correctly chose to bundle for strategic analytical reasons (unified capacity allocation trade-off) but the label "PASSED" obscures the true test result; should state "BCG Test: AMBIGUOUS — bundled for analytical convenience" with explicit disclosure of the override [bcg-market-mapper]
5. Hypothesis ID scheme diverges between validation-report and portfolio — validation-report uses H-D1/H-D2/H-D3/H-D4/H-S1/H-S2/H-S3/H-P1/H-P2/H-P3 (10 items); portfolio.md generates its own H-D1/H-D2/H-A1/H-A2/H-F1/H-F2/H-O1/H-O2/H-S1 (9 items); all substantive hypothesis topics addressed, but cross-document referencing is confused; minor structural gap [bcg-portfolio-analyst]

**Proposed prompt changes:** 4 changes (see /research/micron-08.04.2026/methodology-review.md)
- Change 1: bcg-segment-analyst — Internal consistency arithmetic gate: after filling segment economics, perform three mandatory checks: (1) Micron revenue / share upper bound = minimum TAM → TAM lower bound must be ≥ this value; (2) Micron revenue / TAM upper bound = minimum share → share lower bound must be ≥ this value; (3) strategy revenue impact must be ≤ (TAM × realistic share gain); do not submit segment where these triangulations fail — HIGH confidence
- Change 2: bcg-production — Correction propagation protocol: read validation-report.md "Corrected Data for Portfolio Analysis" table before writing any section; for every corrected figure in that table, use only the corrected value in final-report.md; search draft for original (uncorrected) values and replace; append "(corrected per validation-report.md)" on first use — HIGH confidence
- Change 3: bcg-researcher — Corporate event verification gate: for any announced corporate action (product line exit, acquisition completed, CHIPS grant awarded, facility groundbreaking, executive appointment, customer design win publicly announced), always search "[company] [event] press release [year]" and site:investors.[company].com before applying ESTIMATED tag; officially announced events with IR press releases are VERIFIED by definition — HIGH confidence
- Change 4: bcg-market-mapper — BCG test override disclosure standard: when analytically choosing to bundle sub-segments despite pure-play competitors existing, label as "BCG Test: AMBIGUOUS — bundled for analytical convenience" rather than "PASSED — with nuance"; include explicit override statement naming the sub-segments that would separate under strict application and the strategic rationale for bundling — MEDIUM confidence

**Applied immediately:** Changes 1, 2, 3 recommended for immediate manual application (all HIGH confidence). Change 4 is MEDIUM confidence — analytical transparency improvement, not a factual error fix.

**What worked well in this engagement:**
- bcg-fact-checker (4.7 / 5) — strongest fact-checking output in any semiconductor engagement in the log; 76 claims across 4 segments; 22 documented searches; Samsung HBM4 NVIDIA supply negotiations resolved from "НЕ ВЕРИФИЦИРОВАНО" to VERIFIED via Digitimes; HBM share sum checks (Q2: 62+21+17=100%, Q3: 57+22+21=100%) confirm active internal consistency verification beyond claim-by-claim checking; all 4 critical issues identified with explicit replacement language; corrected data table at end of validation-report is the model handoff format; hypothesis validation table 10/10 with Supporting and Challenging Data columns
- bcg-portfolio-analyst (4.8 / 5) — VERDICT on line 8 with quantified NPV ($28-38B), IRR (35-45%), and central strategic question explicitly answered; "The central question answered" subsection immediately below VERDICT is excellent BCG practice; 7-row synergy map with dollar estimates per synergy; three-scenario NPV with probability weights; DICE completed with substantive commentary on all 4 dimensions; binding constraint correctly identified as engineering talent competition between CMBU and AEBU; all 4 validation-report corrections applied at document top before MBB matrix; all 10 hypotheses closed in structured table
- bcg-researcher — both old (CNBU/MBU/EBU/SBU FY2022-FY2024) and new (CMBU/CDBU/MCBU/AEBU FY2023-FY2025) segment structures documented side-by-side for historical continuity; HBM revenue trajectory table (quarterly milestones FY2024 through Q2 FY2026 with source per row) is production-ready competitive intelligence; design win table with customer/product/HBM SKU/source structure is strongest hardware competitive intelligence table in the corpus
- bcg-market-mapper — stress-tests are substantive; 3 specific Q1/Q2/Q3 questions per segment with analytical (not boilerplate) responses; CMBU stress-test on NVIDIA vertical integration answered with specificity; PIM threat answered with commercial timeline; TAM sanity check shown explicitly (top-3 supplier revenue sum vs. stated TAM confirms plausibility)
- No production failure — final-report.md produced in a 4-segment semiconductor engagement; six-part structure with strategic verdict block-quote on line 8; all segment headers are conclusion-format; "Therefore:" closings on every segment subsection; production stability maintained for the fifth consecutive engagement
- All 10 hypotheses explicitly closed — both validation-report and portfolio.md include hypothesis outcome tables; H-D4 (CXMT threat) and H-P3 (Crucial exit capacity redirect) both CONFIRMED with primary sources; honest PARTIALLY CONFIRMED verdicts for H-D1, H-D2, H-S1 (not over-confirmed)

**Data quality metrics:**
- Average Data Quality Score across 4 segments: B (76% verified) — MEDIUM-HIGH; above corpus average for semiconductor pure-play engagements
- Best segment: CMBU (B — 82% verified) — HBM share data, Micron revenue trajectory, power efficiency claim all primary-sourced; cleanest semiconductor segment in recent corpus
- Weakest segment: AEBU (B — 71% verified) — automotive NVMe SSD and BGA SSD sub-segments both single-source; TAM internal inconsistency is the only ❌ structural flag in the engagement; Renesas revenue conflates MCU + power + memory
- Total claims checked: 76 | Total ✅ verified: 58 (76%) | Total ⚠️ questionable: 14 (18%) | Total ❌ hallucinated/inconsistent: 4 (5%) | Error rate: 5% (below corpus average of ~7%)
- Overall error rate 5% continues the recent improvement trend from 10% early corpus to ~4-5% semiconductor engagements; 2nd consecutive semiconductor engagement at ≤5%

**Cross-engagement pattern summary (as of this engagement, 22 engagements total):**
- TAM/revenue/share internal arithmetic inconsistency: 2/4 recent semiconductor engagements (AEBU here, TSMC mature node in prior) — EMERGING SEMICONDUCTOR PATTERN; occurs when analyst sources TAM and market share independently without checking triangulation with known Micron/company revenue; Change 1 directly addresses
- Validation-report correction propagation gap (corrections reach portfolio preamble but not final-report per-segment prose): 2/3 recent engagements — EMERGING PATTERN; structural pipeline gap where production agent does not systematically override segment prose with fact-checker corrections; Change 2 directly addresses
- Researcher conservative ESTIMATED tag on announced corporate events: 3 identified occurrences in log (Crucial exit here, Apple QTL correction in Qualcomm, Runway ML valuation in ByteDance all required fact-checker remediation for events that had press releases) — EMERGING PATTERN across company types; Change 3 directly addresses
- BCG test override disclosure: 2/3 semiconductor engagements (CDBU here, Qualcomm QCT/QTL in prior) — segmentation judgment calls not explicitly disclosed as overrides; MEDIUM priority
- final-report.md absent: 8/22 engagements (36% historical rate) — STABLE; no production failure in 5 consecutive engagements; MVR protocol changes appear effective
