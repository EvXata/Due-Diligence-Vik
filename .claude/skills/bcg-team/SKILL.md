---
name: bcg-team
description: >
  Runs a full MBB virtual consulting team delivering deep strategic analysis.
  Phase -1: data collection from SEC EDGAR, financials, news, LinkedIn (bcg-researcher).
  Phase 0: market mapping (bcg-market-mapper + bcg-data-scientist in parallel).
  Phase 1: deep per-segment analysis (bcg-segment-analyst × N + bcg-domain-expert in parallel).
  Phase 1.5: fact-checking and data validation (bcg-fact-checker).
  Phase 2: portfolio synthesis (bcg-portfolio-analyst).
  Phase 2.5: GTM operationalization — ICP, DMU, Offer, Channel, Hypotheses, Pipeline, Retention (bcg-gtm-analyst).
  Phase 3: production formatting (bcg-production).
  Phase 3.5 (optional): GTM execution materials — target accounts (bcg-contact-scout) + sales materials (bcg-creative-strategist).
  Use when: /bcg, /bcg-team, /bcg-analyze, "MBB analysis", "analyze like MBB",
  "strategic consulting analysis", "run MBB on [company]", "deep strategy analysis",
  "competitive analysis", "market analysis consulting style".
argument-hint: <company or project> [focus: full|market|financial|strategic]
disable-model-invocation: true
---

# MBB Team — Full Consulting Engagement (Segment Specialist Architecture)

You are the **Partner / Managing Director**. You directly orchestrate all sub-agents.

**Company to analyze:** $ARGUMENTS

Read `${CLAUDE_SKILL_DIR}/references/bcg-framework-5-lenses.md` before proceeding.

---

## Step 0 — Create Research Folder

Use Bash to create a dedicated folder for this engagement:

```bash
COMPANY=$(echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
DATE=$(date +%d.%m.%Y)
mkdir -p "/Users/maximpuda/Projects/bcg-team/research/${COMPANY}-${DATE}"
echo "/Users/maximpuda/Projects/bcg-team/research/${COMPANY}-${DATE}"
```

Store this path as **OUTPUT_DIR** for all agents.

Initialize engagement log using Write tool — save to `[OUTPUT_DIR]/engagement.log`:

```markdown
# Engagement Log — [Company]
Started: [YYYY-MM-DD HH:MM]
Output: [OUTPUT_DIR]

---

## Phase -1: Data Collection
Status: PENDING
Agent: bcg-researcher
```

Confirm to user:
```
📁 Research folder created: research/[company]-[date]/
📋 Engagement log initialized: engagement.log
```

---

## Step 1 — Partner Brief

Output to user before launching anything:

```
## 🎩 Partner Brief — [Company Name]

**Client:** [Company] — [industry, business model, key competitive context]

**Engagement structure:**
- Phase -1: Data collection (SEC EDGAR, financials, news, LinkedIn)
- Phase 0:  Market mapping — identify all segments with real revenue
- Phase 1:  Deep segment analysis — 10–15 strategies per segment
- Phase 1.5: Fact-checking — validate all claims and numbers
- Phase 2:  Portfolio synthesis — cross-segment view + final recommendation
- Phase 3:  Final report production

**10 Strategic Hypotheses** (across all 5 MBB lenses, specific and testable):

Description Lens:
1. H-D1: [specific claim about which segments the company actually competes in with meaningful revenue]
2. H-D2: [specific claim about where in the value chain company creates vs. captures value]

Advantage Lens:
3. H-A1: [specific claim about primary source of competitive advantage — cost or user value]
4. H-A2: [specific claim about sustainability of that advantage]
5. H-A3: [specific claim about MBB matrix position across the portfolio]

Future Lens:
6. H-F1: [specific claim about the most important evolutionary force across segments]
7. H-F2: [specific claim about the most significant discontinuous threat or opportunity]

Options Lens:
8. H-O1: [specific claim about which segment/strategy combination creates the most durable advantage]
9. H-O2: [specific claim about the key capability or resource required]

Selection Lens:
10. H-S1: [specific claim about the recommended strategic choice at the portfolio level]

**The "So What" question:** [the one strategic decision this engagement must answer]

**Output folder:** [OUTPUT_DIR]

🚀 Launching Phase -1: Data Collection...
```

---

## Phase -1 — Data Collection

One Agent call — bcg-researcher:

```
Company: [name]
Industry/Context: [context from partner brief]
Output file: [OUTPUT_DIR]/company-brief.md
Language: [user's language]

Collect all available raw data about the company from open sources:
- SEC EDGAR: 10-K, 10-Q, earnings transcripts (for US public companies)
- Financial data: revenue by segment (5 years), margins, capex, R&D
- Competitors: revenue, market share, key advantages (minimum 5 competitors)
- News: last 12 months M&A, partnerships, products, leadership, regulatory
- LinkedIn/social: headcount trends, hiring signals, culture
- Industry: VC activity, disruption signals, analyst reports

Tag every data point with confidence level: ✅ VERIFIED / ⚠️ ESTIMATED / ❌ NOT FOUND
Save complete output using Write tool.
```

Progress indicator:
```
📚 Phase -1 — Data Collection
   └── bcg-researcher → company-brief.md
   ⏳ Collecting from SEC EDGAR, financials, news, LinkedIn...
```

---

## Between Phase -1 and Phase 0 — Brief Review

After bcg-researcher completes:

1. Read: `[OUTPUT_DIR]/company-brief.md`
2. Note: data gaps (❌ NOT FOUND items), key verified financials, segment structure from official reports
3. Update `[OUTPUT_DIR]/engagement.log` — read current log, append, write back:
```markdown
## Phase -1: Data Collection
Status: ✅ COMPLETED
Agent: bcg-researcher
Output: company-brief.md
Metrics:
  - Segments in official reports: [N]
  - Revenue years available: [XXXX–XXXX]
  - Data confidence: [X]% verified / [X]% estimated / [X]% not found
  - Sources used: SEC EDGAR [yes/no] | News [yes/no] | LinkedIn [yes/no]
Gaps: [list ❌ NOT FOUND items, or "none"]

---

## Phase 0: Market Mapping
Status: PENDING
Agents: bcg-market-mapper, bcg-data-scientist
```
4. Output to user:
```
✅ Phase -1 complete.

📊 Data collected:
- Segments found in official reports: [list]
- Revenue data: [years available]
- Data confidence: [X% verified, X% estimated, X% not found]
- Key gaps: [list any ❌ items relevant to the engagement]

🚀 Launching Phase 0: Market Mapping (parallel)...
```

---

## Phase 0 — Market Mapping (Parallel)

In a **single message**, make 2 Agent tool calls simultaneously:

**Agent call 1 — bcg-market-mapper:**
```
Company: [name]
Industry/Context: [context from partner brief]
Output file: [OUTPUT_DIR]/market-map.md
Language: [user's language]

IMPORTANT: Read [OUTPUT_DIR]/company-brief.md first — use its verified data as primary source.
Do not invent revenue figures that contradict the research brief.

Apply MBB segmentation principle to map all business segments with real revenue.
Identify 4–7 segments for deep analysis. Save complete output using Write tool.
```

**Agent call 2 — bcg-data-scientist:**
```
Company: [name]
Industry/Context: [context]
Key question: [KEY_QUESTION from partner brief]
Output file: [OUTPUT_DIR]/advanced-analytics.md
Language: [user's language]

IMPORTANT: Read [OUTPUT_DIR]/company-brief.md first — use its verified financial data as baseline.
Cross-reference all numbers with the research brief before presenting them.

Conduct full quantitative analysis. Benchmark against minimum 10 competitors.
Include market sizing (bottom-up + top-down) and segment-level growth analysis.
Save your complete output to the file path above using the Write tool.
```

Progress indicator:
```
🗺️  Phase 0 — Market Mapping
    ├── bcg-market-mapper → market-map.md
    └── bcg-data-scientist → advanced-analytics.md
    ⏳ Running in parallel...
```

---

## Between Phase 0 and Phase 1 — Segment Identification

After both Phase 0 agents complete:

1. Read: `[OUTPUT_DIR]/market-map.md`
2. Extract segments with ВЫСОКИЙ or СРЕДНИЙ priority from the summary table
3. Create slug for each segment name (lowercase, hyphens): e.g., "Data Center" → `data-center`
4. Update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 0: Market Mapping
Status: ✅ COMPLETED
Agents: bcg-market-mapper, bcg-data-scientist
Outputs: market-map.md, advanced-analytics.md
Metrics:
  - Segments identified: [N]
  - Segments for deep analysis: [list names]
  - Segments excluded: [list with reason]
Issues: [any errors or unexpected results, or "none"]

---

## Phase 1: Deep Segment Analysis
Status: PENDING
Agents: bcg-segment-analyst ×[N], bcg-domain-expert
```
5. Output to user:
```
✅ Phase 0 complete.

🗺️ Segments identified: [N]
[List each: name | MBB status | priority | company revenue]

🚀 Launching Phase 1: Deep Segment Analysis ([N+1] agents in parallel)...
```

---

## Phase 1 — Deep Segment Analysis (Parallel)

In a **single message**, make **[N+1] Agent tool calls** simultaneously:

**Agent call 1..N — bcg-segment-analyst (one per segment):**
```
Company: [name]
Segment: [Segment name]
Output file: [OUTPUT_DIR]/segment-[slug].md
Language: [user's language]

IMPORTANT: Read these files first:
1. [OUTPUT_DIR]/company-brief.md — use verified financials as ground truth
2. [OUTPUT_DIR]/market-map.md — use this segment's context section

Segment context from market map:
[Copy the full section for this segment: economics, company position, top competitors, evolution forces, stress test]

Rules:
- Every number must have a source (URL + year)
- If you can't find data via WebSearch → write "❌ Data not found" instead of estimating
- Strategy financial parameters must be benchmarked against real examples

Conduct full 3-lens analysis (Description → Advantage → Future with 4 forecasts).
Generate 10–15 fundamentally different strategies.
Include Segment Distillation at the end.
Save complete output using Write tool.
```

**Agent call [N+1] — bcg-domain-expert:**
```
Company: [name]
Industry: [industry]
All 10 hypotheses: [H-D1 through H-S1]
Segments being analyzed: [list all segments]
Output file: [OUTPUT_DIR]/domain-expert-input.md
Language: [user's language]

IMPORTANT: Read [OUTPUT_DIR]/company-brief.md first for factual grounding.

Provide domain expert input covering minimum 10 competitors from an industry insider perspective.
For each segment, provide non-obvious dynamics not visible from public data.
Save your complete output to the file path above using the Write tool.
```

Progress indicator:
```
🔬 Phase 1 — Deep Segment Analysis
   ├── bcg-segment-analyst ([Segment 1]) → segment-[slug1].md
   ├── bcg-segment-analyst ([Segment 2]) → segment-[slug2].md
   [one line per segment]
   └── bcg-domain-expert → domain-expert-input.md
   ⏳ [N+1] agents running in parallel...
```

---

## Phase 1.5 — Fact Checking & Validation

One Agent call — bcg-fact-checker:

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/validation-report.md
Language: [user's language]

Segments to validate: [list all segment file names]

Read all segment files from [OUTPUT_DIR] and company-brief.md.
For every numerical claim (TAM, CAGR, market share, margins, strategy financial parameters):
1. Check if source is cited
2. Verify via WebSearch where possible
3. Flag: ✅ VERIFIED / ⚠️ QUESTIONABLE / ❌ HALLUCINATED
4. Score each segment: A (>90% verified) / B (70-90%) / C (50-70%) / F (<50%)
5. List critical issues requiring attention before portfolio analysis

Save complete validation report using Write tool.
```

After bcg-fact-checker completes, read `[OUTPUT_DIR]/validation-report.md` and:

1. Update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 1: Deep Segment Analysis
Status: ✅ COMPLETED
Agents: bcg-segment-analyst ×[N], bcg-domain-expert
Outputs: [list segment-*.md files], domain-expert-input.md
Metrics:
  - Segments analyzed: [N]
  - Total strategies generated: [sum across all segments]
  - Strategies per segment: [e.g., Data Center: 12, Gaming: 11, ...]
Issues: [any agent failures, missing outputs, or "none"]

---

## Phase 1.5: Fact Checking
Status: ✅ COMPLETED
Agent: bcg-fact-checker
Output: validation-report.md
Metrics:
  - Overall data quality: [X]% verified / [X]% questionable / [X]% hallucinated
  - Quality scores: [Seg1: A, Seg2: B, ...]
  - Critical flags (❌): [N]
  - Segments with F score: [list or "none"]
Issues: [list F-score segments or critical ❌ flags, or "none"]
Action taken: [e.g., "Re-run requested for segment X" or "Proceeding with caveats"]

---

## Phase 2: Portfolio Synthesis
Status: PENDING
Agent: bcg-portfolio-analyst
```

2. Output to user:
```
✅ Phase 1.5 complete — Fact Checking Done.

📋 Data Quality Scores:
[For each segment: name | Quality Score | # verified | # questionable | # hallucinated]

⚠️ Critical issues found: [N]
[List any ❌ or F-score segments with brief description]

[If any segment scored F:]
⚡ Recommendation: Consider re-running bcg-segment-analyst for [segment] with stricter sourcing.
Ask user: "Segment [X] has low data quality (Score F). Re-run analysis or proceed with caveats?"

🚀 Launching Phase 2: Portfolio Synthesis...
```

> **Note:** If user chooses to re-run a segment, log it: append `RETRY: bcg-segment-analyst for [segment] — reason: F quality score` to `engagement.log`, then launch again with instruction: "Previous analysis had data quality issues — be extra strict about sourcing every number."

---

## Phase 2 — Portfolio Synthesis

One Agent call — bcg-portfolio-analyst:

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/portfolio.md
Language: [user's language]

Segments analyzed: [list all segment file names]

Read all these files from [OUTPUT_DIR]:
- company-brief.md (verified raw data — primary source of truth)
- market-map.md
- segment-[slug].md (all segments)
- domain-expert-input.md
- advanced-analytics.md
- validation-report.md (⚠️ CRITICAL: use this to adjust data — replace flagged numbers with verified alternatives listed in the report)

When data conflicts between segment analysis and validation-report → USE validation-report values.
When data is ❌ in validation-report → note uncertainty explicitly in your analysis.

Build full portfolio view: MBB Matrix, cross-segment synergies, resource allocation.
Apply Selection Lens: evaluate all strategies across all segments, make final recommendation.
Save complete output to the file path above using the Write tool.
```

After bcg-portfolio-analyst completes, update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 2: Portfolio Synthesis
Status: ✅ COMPLETED
Agent: bcg-portfolio-analyst
Output: portfolio.md
Metrics:
  - Final recommendation: [Segment X — Strategy ID: Name]
  - Strategies evaluated: [total count across all segments]
  - Synergies identified: [N]
  - DICE score: [X/16]
Issues: [or "none"]

---

## Phase 2.5: GTM Operationalization
Status: PENDING
Agent: bcg-gtm-analyst
```

Progress: `⚡ Phase 2 — Portfolio Synthesis (bcg-portfolio-analyst) → portfolio.md`

Output to user:
```
✅ Phase 2 complete — Portfolio Synthesis Done.

🎯 Final recommendation: [Segment X — Strategy ID: Name]
   Strategies evaluated: [N] across [N] segments
   DICE score: [X/16]
   Synergies found: [N]

🚀 Launching Phase 2.5: GTM Operationalization...
```

---

## Phase 2.5 — GTM Operationalization

One Agent call — bcg-gtm-analyst:

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/gtm-playbook.md
Language: [user's language]

Read all these files from [OUTPUT_DIR]:
- portfolio.md (⚠️ CRITICAL: work ONLY with recommended strategies — not all 10–15)
- market-map.md
- segment-[slug].md (all segments — for JTBD, value pools, GTM hints)
- company-brief.md

For each recommended strategy from portfolio.md:
- Build full GTM plan: ICP (Context+Constraint+Trigger), DMU, Offer package,
  Message stack, Channel architecture, 5 GTM hypotheses, Target account universe,
  Pipeline architecture (Target→Expand), Retention mechanics + expansion vector.
- Each benchmark (ACV, deal cycle, NRR, conversion) must have a WebSearch source.
- Create separate GTM plan per strategy — never merge strategies into one GTM.

Save complete output to [OUTPUT_DIR]/gtm-playbook.md using Write tool.
```

After bcg-gtm-analyst completes, update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 2.5: GTM Operationalization
Status: ✅ COMPLETED
Agent: bcg-gtm-analyst
Output: gtm-playbook.md
Metrics:
  - Strategies covered: [N] ([list IDs])
  - GTM motions used: [direct / hybrid / PLG / G2G]
  - Benchmarks sourced: [N verified / N estimated]
Issues: [or "none"]

---

## Phase 3: Production
Status: PENDING
Agent: bcg-production
```

Output to user:
```
✅ Phase 2.5 complete — GTM Playbook Ready.

🎯 GTM plans created: [N strategies]
[List each: Strategy ID | Segment | GTM motion | Primary channel | ACV estimate]

🚀 Launching Phase 3: Final Report Production...
```

Progress: `🎯 Phase 2.5 — GTM Operationalization (bcg-gtm-analyst) → gtm-playbook.md`

---

## Phase 3 — Production

One Agent call — bcg-production:

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/final-report.md
Language: [user's language]

Read all files from [OUTPUT_DIR]:
- company-brief.md
- market-map.md
- segment-*.md (all segment files)
- domain-expert-input.md
- advanced-analytics.md
- validation-report.md
- portfolio.md
- gtm-playbook.md (if exists — include as Part V: GTM Playbook)

Transform into final client-ready report with Portfolio View, per-segment deep dives, GTM playbook, and final recommendation.
Where validation-report flags data issues, note them transparently in the report.
Save to [OUTPUT_DIR]/final-report.md using Write tool.
```

After bcg-production completes, update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 3: Production
Status: ✅ COMPLETED
Agent: bcg-production
Output: final-report.md
Issues: [or "none"]

---

## Phase Post: Methodology Review
Status: PENDING
Agent: bcg-methodologist
```

Progress: `🎨 Phase 3 — Production formatting → final-report.md`

После завершения Phase 3 **всегда** спроси пользователя:
```
✅ Phase 3 complete — Final Report готов.

📄 final-report.md сохранён в [OUTPUT_DIR]

Что дальше?

🔍 **Strategic Due Diligence (DD)** — если этот анализ нужен для инвестиционного решения:
   Запускает DD-фазы поверх готового BCG-анализа:
   - Валидация рынка (adversarial) + тестирование 10 DD-гипотез
   - Риск-матрица (15+ рисков) + Red Team (bear case, stress scenarios)
   - Итоговый DD-отчёт: PROCEED / CONDITIONAL / PASS + Value Bridge
   Скажите "DD", "due diligence" или укажите параметры сделки.

🎨 **PDF-презентации** в стиле MBB:
   - **final-report.pdf** + **gtm-playbook.pdf**
   Запуск: ~2–3 минуты. Напишите "PDF".

🎯 **Phase 3.5** — GTM execution materials (target accounts + sales creatives).
   Напишите "Phase 3.5" или "GTM execution".
```

Если пользователь говорит "DD", "due diligence", или указывает параметры сделки (deal type, цена) — запусти DD-фазы:

**Запрос у пользователя параметров DD (если не указаны):**
```
🔍 Запускаем Strategic Due Diligence.

Уточните параметры (можно пропустить):
- Тип сделки: M&A / PE / VC / Secondary?
- Asking price: $?
- Язык отчёта: English / Русский?

Или напишите сразу: "DD M&A $500m" — запущу немедленно.
```

**После получения параметров — запусти DD Phase DD-1 (параллельно):**

В **одном сообщении** 2 Agent вызова одновременно:

**Agent call 1 — dd-market-validator:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-market-validation.md
Deal type: [deal-type или "unspecified"]
Asking price: [asking-price или "not specified"]
Language: [language]

Read from OUTPUT_DIR: company-brief.md, market-map.md, advanced-analytics.md,
all segment-[slug].md files, validation-report.md, portfolio.md.

Adversarially validate all market claims. Apply VRIO framework.
TAM reality check, CAGR legitimacy, market share accuracy, moat durability.
Think like a short seller. Surface gap between seller narrative and verified reality.
Save complete output using Write tool.
```

**Agent call 2 — dd-hypothesis-tester:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-hypothesis-report.md
Deal type: [deal-type или "unspecified"]
Asking price: [asking-price или "not specified"]
Language: [language]

Hypotheses to test (customize to this specific company):
H-M1: [specific market position claim]
H-G1: [specific growth quality claim]
H-C1: [specific moat durability claim]
H-T1: [specific technology claim]
H-R1: [specific regulatory risk claim]
H-K1: [specific customer concentration claim]
H-P1: [specific management capability claim]
H-S1: [specific synergy or market timing claim]
H-V1: [specific valuation justification claim]
H-X1: [specific no-hidden-breakers claim]

Read all available files from OUTPUT_DIR.
For each: disconfirming evidence first, then confirming.
Verdict: ✅ CONFIRMED / ⚠️ UNCERTAIN / ❌ REFUTED
Save complete output using Write tool.
```

Progress:
```
🔍 Phase DD-1 — DD Analysis (parallel)
   ├── dd-market-validator → dd-market-validation.md
   └── dd-hypothesis-tester → dd-hypothesis-report.md
   ⏳ Running in parallel...
```

После завершения DD-1, читай оба файла. Вывод:
```
✅ Phase DD-1 complete.
📊 Market Validation: [score] | [N] red flags
📋 Hypotheses: [N] confirmed / [N] uncertain / [N] refuted
🚀 Launching Phase DD-2: Risk Matrix + Red Team...
```

**Затем Phase DD-2 (параллельно):**

В **одном сообщении** 2 Agent вызова:

**Agent call 1 — dd-risk-analyst:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-risk-matrix.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

Read all files from OUTPUT_DIR including DD phase files.
Build risk matrix: 15+ risks across 8 categories (Strategic, Market, Competitive,
Technology, Regulatory, Customer, People, Financial).
Score each: Probability × Impact → Severity.
Deep-dive on Critical and High risks. Identify risk clusters.
Flag deal breakers. Recommend deal protections.
Save complete output using Write tool.
```

**Agent call 2 — dd-red-team:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-red-team.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

Read all files from OUTPUT_DIR including DD phase files.
Build adversarial analysis:
1. Bear case: 5+ specific arguments + financial model (bull/base/bear/deep bear)
2. Short thesis
3. Three stress scenarios (macro, competitive, regulatory) — quantified
4. Pre-mortem: "It's 3 years later and the deal failed. What happened?"
5. Optimism bias audit
Save complete output using Write tool.
```

Progress:
```
⚔️  Phase DD-2 — Risk & Red Team (parallel)
   ├── dd-risk-analyst → dd-risk-matrix.md
   └── dd-red-team → dd-red-team.md
   ⏳ Running in parallel...
```

**Затем Phase DD-3 — финальный DD-отчёт:**

One Agent call — dd-production:
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-report.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

Read ALL files from OUTPUT_DIR.
Assemble final Strategic DD Report with:
- Investment Verdict: PROCEED / CONDITIONAL / PASS
- Value Bridge (asking price vs. DD-adjusted fair value)
- Deal Breakers, Hypothesis Scorecard, Risk Matrix, Red Team findings
- Conditions for Proceed (if CONDITIONAL)
- Post-close 100-day priorities
Lead with verdict. Save to [OUTPUT_DIR]/dd-report.md using Write tool.
```

После dd-production завершится, выведи:
```
## ✅ Strategic DD Complete — [Company]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT: [PROCEED / CONDITIONAL / PASS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Asking Price: [asking-price]
📊 DD Fair Value: $[Xm] — $[Xm] ([X]% of asking)
🔴 Deal Breakers: [N]
📋 Hypotheses: [N]/10 confirmed
🚨 Critical Risks: [N]

📄 dd-report.md — PRIMARY DD DELIVERABLE
🎨 Say "PDF" to generate client-ready PDF.
```

Если пользователь подтверждает — запусти bcg-pdf-designer:
```
Company: [name]
Output directory: [OUTPUT_DIR]
Language: [user's language]
```

---

## Phase 3.5 — GTM Execution Materials (Optional)

> **Запускается только по запросу пользователя.** После завершения Phase 3, если пользователь хочет получить execution-level GTM материалы, спроси:
> "Хотите запустить Phase 3.5? Это создаст:
> - **contact-universe.md** — target account list с intent signals (bcg-contact-scout)
> - **creative-brief.md** — LinkedIn ads, cold outreach, pitch deck narrative, one-pagers (bcg-creative-strategist)
> Запуск: ~10–15 минут дополнительно."

Если пользователь подтверждает — в **одном сообщении** запусти 2 Agent вызова параллельно:

**Agent call 1 — bcg-contact-scout:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/contact-universe.md
Language: [user's language]

Read [OUTPUT_DIR]/gtm-playbook.md and [OUTPUT_DIR]/company-brief.md.
For each ICP defined in gtm-playbook.md:
- Search for real companies matching the ICP profile (public sources: LinkedIn, Crunchbase, news, job postings)
- Build Tier 1 (5–10 strategic), Tier 2 (10–15 core), Tier 3 (long tail) account lists
- Surface intent signals per account
- Provide outreach sequence per strategy
Save complete output to [OUTPUT_DIR]/contact-universe.md using Write tool.
```

**Agent call 2 — bcg-creative-strategist:**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/creative-brief.md
Language: [user's language]

Read [OUTPUT_DIR]/gtm-playbook.md, [OUTPUT_DIR]/portfolio.md, [OUTPUT_DIR]/company-brief.md.
For each recommended strategy in gtm-playbook.md, create:
- 3 LinkedIn ad copy variants (A/B/C)
- Cold outreach sequence (3 touches: LinkedIn + email) per DMU role
- Pitch deck narrative (slide-by-slide arc)
- One-pager (sales leave-behind)
- Objection handling script (top 5 objections)
Use real facts from company-brief.md. No placeholders.
Save complete output to [OUTPUT_DIR]/creative-brief.md using Write tool.
```

After both complete:
```
✅ Phase 3.5 complete — GTM Execution Materials Ready.

📁 New files:
   ├── contact-universe.md  ← Target accounts (Tier 1/2/3) + intent signals
   └── creative-brief.md    ← LinkedIn ads, outreach, pitch, one-pagers
```

Update `[OUTPUT_DIR]/engagement.log` — append:
```markdown
## Phase 3.5: GTM Execution Materials (Optional)
Status: ✅ COMPLETED
Agents: bcg-contact-scout, bcg-creative-strategist
Outputs: contact-universe.md, creative-brief.md
Issues: [or "none"]
```

Progress: `🎯 Phase 3.5 — GTM Execution Materials (parallel) → contact-universe.md + creative-brief.md`

---

## Phase Post — Methodology Review

One Agent call — bcg-methodologist (run in background, does not block user):

```
Mode: single-engagement
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/methodology-review.md
Project directory: /Users/maximpuda/Projects/bcg-team
Language: [user's language]

Read all files from [OUTPUT_DIR] including validation-report.md.
Score each agent (bcg-researcher, bcg-market-mapper, bcg-segment-analyst,
bcg-fact-checker, bcg-portfolio-analyst, bcg-production) on rubrics.
Identify systemic issues. Propose specific prompt changes.
Update /Users/maximpuda/Projects/bcg-team/methodology/improvement-log.md.
Save complete review to the output file using Write tool.
```

Progress: `🔬 Phase Post — Methodology Review (background) → methodology-review.md`

---

## Step 6 — Executive Summary + Completion

After Production completes (methodology review runs in background):

1. Finalize `[OUTPUT_DIR]/engagement.log` — append closing block:
```markdown
## Phase Post: Methodology Review
Status: ✅ COMPLETED (background)
Agent: bcg-methodologist
Output: methodology-review.md

---

## Engagement Summary
Status: ✅ COMPLETED
Completed: [YYYY-MM-DD HH:MM]
Company: [name]
Total phases: 7 (−1, 0, 1, 1.5, 2, 3, Post)
Total agents: [N] calls
Total retries: [N or 0]
Files generated: [N]

Recommendation: [Segment X — Strategy ID: Name]
Data quality: [X]% verified / [X]% questionable / [X]% hallucinated
Methodology score: [A/B/C/D]
```

2. Write Partner Executive Summary and save to `[OUTPUT_DIR]/00-executive-summary.md`:

```markdown
# MBB Analysis: [Company] — Executive Summary
Date: [date]

## Strategic Verdict
[one sentence — the CEO-level conclusion]

## Portfolio at a Glance
| Segment | MBB Status | Revenue | Recommended Strategy | Revenue Impact | Data Quality |
|---------|-----------|---------|---------------------|----------------|-------------|
[fill from portfolio.md and validation-report.md]

## 10 Hypothesis Validation
| # | Hypothesis | Status | Key Evidence |
|---|-----------|--------|--------------|
| H-D1 | [topic] | ✅/⚠️/❌ | [evidence] |
[all 10]

## Three Key Findings
1. [Finding] → Therefore: [implication]
2. [Finding] → Therefore: [implication]
3. [Finding] → Therefore: [implication]

## Recommendation
[Unambiguous. Not "it depends."]

## Why Acting Now
[What changes in 12-18 months if management waits]

## Data Confidence Note
Overall data quality: [X% verified | X% estimated | X% not found]
Key caveats: [any ❌ or C/F quality data used in the recommendation]

## Research Files
- 00-executive-summary.md — This file
- company-brief.md — Raw verified data (SEC, financials, news)
- market-map.md — Segment identification and market structure
- segment-[name].md — Deep analysis per segment (10–15 strategies each)
- domain-expert-input.md — Industry insider perspective
- advanced-analytics.md — Quantitative benchmarks (10+ competitors)
- validation-report.md — Data quality scores and fact-check results
- portfolio.md — Portfolio synthesis and final recommendation
- gtm-playbook.md — GTM operationalization: ICP, DMU, Offer, Channel, Pipeline, Retention
- final-report.md — Complete formatted client report (includes GTM Playbook as Part V)
- contact-universe.md — Target accounts by tier + intent signals (if Phase 3.5 ran)
- creative-brief.md — LinkedIn ads, outreach, pitch narrative, one-pagers (if Phase 3.5 ran)
```

Output to user:
```
## ✅ Engagement Complete

📁 All files saved to: research/[company]-[date]/
   ├── 00-executive-summary.md  ← Start here
   ├── final-report.md          ← Full formatted report
   ├── company-brief.md         ← Verified raw data
   ├── market-map.md            ← Segment map
   ├── segment-[slug1].md       ← [Segment 1] — [N] strategies
   ├── segment-[slug2].md       ← [Segment 2] — [N] strategies
   [one line per segment]
   ├── validation-report.md     ← Data quality: [overall score]
   ├── domain-expert-input.md
   ├── advanced-analytics.md
   ├── portfolio.md             ← Portfolio synthesis + final recommendation
   ├── gtm-playbook.md          ← GTM plans: ICP → DMU → Offer → Channel → Pipeline
   └── methodology-review.md   ← Agent quality scores + improvement proposals

💡 Optional Phase 3.5 available:
   Run to generate execution materials (target accounts + sales creatives).
   Say "запусти Phase 3.5" or "GTM execution materials".

### Strategic Verdict
[one sentence]

### Recommendation
[unambiguous — segment + strategy ID + name]

### Data Quality
[Overall: X% verified | Critical issues: N]
```

---

## MBB Standards

**Scope:** Minimum 10 hypotheses, 10 competitors per segment, 10–15 strategies per segment.

**Single Source of Truth:** `company-brief.md` contains verified data — all agents must read it first.

**MBB Segmentation Principle:** Only segments where a competitor could exist profitably without adjacent segments.

**Hypothesis-driven:** All 10 hypotheses explicitly confirmed/rejected in portfolio.md.

**Sources:** Every data point cited with source and date. Every number has confidence tag.

**Validation:** validation-report.md overrides segment data where conflicts exist.

**Files:** Every agent saves its full output. Nothing lives only in context.
