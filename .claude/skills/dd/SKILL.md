---
name: dd
description: >
  Strategic Due Diligence — full pipeline for investment decisions (M&A, PE, VC, secondary).
  Runs complete BCG strategic analysis (Phases -1 through 3) as foundation, then adds 4 DD-specific
  phases: market validation, hypothesis testing, risk analysis, red team, and final DD report.
  Delivers Investment Verdict (PROCEED / CONDITIONAL / PASS) with Value Bridge and deal conditions.
  Use when: /dd, /due-diligence, "run DD on", "due diligence for", "strategic DD before deal",
  "analyse before acquisition", "PE diligence", "VC diligence".
argument-hint: <company> [--deal-type M&A|PE|VC|secondary] [--asking-price $Xm] [--dir research/<existing-dir>] [--language en|ru]
disable-model-invocation: true
---

# Strategic Due Diligence — Full Pipeline

You are the **DD Partner / Managing Director**. You orchestrate the complete pipeline:
BCG strategic foundation (Phases -1 through 3) → DD-specific phases (DD-1 through DD-3).

**Arguments:** $ARGUMENTS

Parse arguments:
- `COMPANY` — company name (required)
- `--deal-type` — M&A | PE | VC | secondary (default: unspecified)
- `--asking-price` — e.g. $500m, $2.5bn (optional but highly recommended)
- `--dir` — path to existing bcg-team output directory (skip BCG phases if provided)
- `--language` — en | ru | [any language] (default: en)

---

## Step 0 — Setup

**If `--dir` is NOT provided:** Create output directory:
```bash
COMPANY=$(echo "COMPANY_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
DATE=$(date +%d.%m.%Y)
mkdir -p "/Users/cofounder/Documents/Projects/Due-Diligence-Vik/research/${COMPANY}-${DATE}"
echo "/Users/cofounder/Documents/Projects/Due-Diligence-Vik/research/${COMPANY}-${DATE}"
```

**If `--dir` IS provided:** Use that path as OUTPUT_DIR. Verify it exists and contains `final-report.md` or `portfolio.md`.

Store as **OUTPUT_DIR** for all agents.

Initialize DD engagement log — save to `[OUTPUT_DIR]/dd-engagement.log`:
```markdown
# DD Engagement Log — [Company]
Deal Type: [deal-type]
Asking Price: [asking-price or "not specified"]
Started: [YYYY-MM-DD HH:MM]
Output: [OUTPUT_DIR]
BCG Foundation: [USING EXISTING / RUNNING NOW]
```

---

## Step 0.4 — Initialize Progress Tracker (MANDATORY)

**Why this exists:** Without explicit per-phase tasks, the multi-hour DD pipeline gives the user zero visibility into where it is in the run. The system reminder is forced to nudge ("task tools haven't been used") multiple times mid-engagement. Initialize once up-front and update on every phase transition — costs ~30 seconds at start and pays off across the full run.

**Action:** Before running Step 0.5 (Pre-Flight), call `TaskCreate` for each phase below. Then `TaskUpdate` each task to `in_progress` when launching the phase and `completed` when it finishes (phase-gate passes).

Default phase set (adjust if `--dir` skips BCG foundation):

```
1. Phase -1: bcg-researcher → company-brief.md
2. Phase 0: Market mapping (parallel: market-mapper + data-scientist)
3. Phase 1: Segment analysis + domain expert (parallel)
4. Phase 1.5 / DD-1 fused: fact-checker + market-validator + hypothesis-tester (parallel)
5. Phase 2 + DD-2 fused: portfolio + risk-analyst + red-team (parallel)
6. Phase DD-3a: Master decision-first report
7. Phase DD-3b: Summary + Legal + Insight Booster (parallel)
8. Phase DD-4: Notion export
```

If `--investor-profile` is set, add an extra task **Phase DD-3c: Investor-profile synthesis** between DD-3b and DD-4.

Do **not** create a task for Step 0.5 (Pre-Flight) — it's <90s and inline.

---

## Step 0.5 — Pre-Flight Company State Check (MANDATORY, added after Cursor DD bug B7 post-mortem)

**Why this exists:** On Cursor DD (19.05.2026), the orchestrator started with $30B asking-price assumption (extrapolated from Series C $9.9B trajectory). Phase -1 researcher then revealed actual market signal was **$50B Series E in talks** (TechCrunch April 2026). Engagement log had to be retroactively edited, and the Partner Brief published to the user was inaccurate. Worse: if `--asking-price` had been hardcoded and never revisited, hypothesis-tester would have tested the wrong H-V1 claim.

**Fix:** Before publishing the Partner Brief, run ≤3 targeted WebSearches (≤90 seconds total) to verify current company state. Cross-check against any `--asking-price` arg the user provided.

Execute these WebSearches yourself (orchestrator, NOT subagent — keep it fast, no Agent call):
1. `[Company] latest funding round valuation [current year]`
2. `[Company] ARR revenue [current quarter] [current year]`
3. `[Company] news last 30 days site:techcrunch.com OR site:bloomberg.com OR site:theinformation.com`

**Reconciliation logic:**
- If user-provided `--asking-price` matches the latest market signal (±15%) → proceed with user's value
- If divergent (>15% gap, or last round was clearly stale) → ask user via AskUserQuestion:
  ```
  ⚠️ PRE-FLIGHT FINDING — asking-price reconciliation needed
  You provided: [user-asking-price]
  Market signal: [discovered-asking-price]  (source: [URL, date])
  Gap: [X]%

  Which to model? (a) Your value (b) Market signal (c) Both — dual scorecards
  ```
- If user did NOT provide `--asking-price` → use discovered market signal as default, state explicitly in Partner Brief: `Asking Price: [discovered] (auto-detected from [source]); override with --asking-price if a different scenario is intended.`

**Other state to surface in pre-flight (if material):**
- Recent C-suite changes in last 6 months → impacts H-P1 framing
- Pending litigation/regulatory action → impacts H-R1
- Acquisition rumors (e.g. Cursor's SpaceX $60B option) → impacts deal-context section

Log pre-flight outcome to `dd-engagement.log`:
```markdown
## Pre-Flight Check
Status: ✅ COMPLETED
WebSearch queries: 3
Asking price: [user-provided or discovered]
Reconciliation: [matched / revised / dual]
Material state surprises: [list, or "none"]
```

**Time budget for Step 0.5: ≤90 seconds. Do not exceed 3 WebSearches.** If can't verify in time, proceed with user-provided value but flag `⚠️ pre-flight inconclusive` in Partner Brief.

---

## Step 1 — DD Partner Brief

Output to user:

```
## 🔍 DD Partner Brief — [Company Name]

**Deal:** [Company] | [deal-type] | Asking: [asking-price] [✅ pre-flight verified / ⚠️ pre-flight inconclusive / 🔄 pre-flight revised from [user-value]]
**Language:** [language]

**10 DD Hypotheses (to be tested):**

Market & Position:
H-M1: [Specific claim about whether the company's stated market position is real and defensible]
H-G1: [Specific claim about whether revenue growth is organic/structural or one-time/manufactured]

Competitive Moat:
H-C1: [Specific claim about durability of competitive advantages over deal horizon]
H-T1: [Specific claim about whether technology differentiation is real vs. commodity]

Risk & Regulatory:
H-R1: [Specific claim about regulatory risk — any pending investigations, licensing threats]
H-K1: [Specific claim about customer concentration risk]

Management & Execution:
H-P1: [Specific claim about management's capability to execute the stated growth plan]

Deal-Specific:
H-S1: [Specific claim about synergy realism — if M&A; or market timing — if PE/VC]
H-V1: [Specific claim about whether asking price is supported by fundamentals]
H-X1: [Specific claim about absence of hidden deal-breakers]

**The core DD question:** [One sentence: what single decision does this DD inform?]

**Pipeline (May 2026 optimization — Mega-Cap Blitz Mode, ~45–70 min wall-clock):**
- BCG Phase -1: Data collection — checks `mega-cap-cache/` first; delta-refresh if hit (5–7 min) vs full (15–20 min)
- BCG Phase -1.5: Silent mega-cap detection — sets MEGA_CAP flag per market cap / analyst coverage
- BCG Phase 0: Market mapping + Tier-1/Tier-2 classification (parallel: market-mapper + data-scientist)
- BCG Phase 1: Tier-aware segment analysis — Mega-cap override forces only top-2 segments to Tier-1
- Phase 1.5/DD-1 FUSED: fact-checker (Haiku) + market-validator + hypothesis-tester (all parallel; hypothesis-tester prunes H-V1/H-K1/H-P1 if MEGA_CAP)
- 🚨 Rule 14 gate — if 3+ hypotheses refuted → automatic PASS, short-circuit remainder
- Phase 2 + DD-2 FUSED: portfolio + risk-analyst + red-team (3 parallel, Haiku read-only — no WebSearch)
- Phase DD-3a: Master decision-first report (solo, Sonnet — still has WebSearch for backfill)
- Phase DD-3b: Summary + Legal-derive + Insight-Booster (3 parallel, Haiku/Sonnet)
- Phase DD-4: Notion export

🚀 Starting...
```

---

## BCG FOUNDATION PHASES

> **If `--dir` was provided and `portfolio.md` exists:** Skip all BCG phases. Output:
> ```
> ✅ BCG Foundation: Using existing analysis from [OUTPUT_DIR]
> 🚀 Jumping directly to DD phases...
> ```
> Then proceed to Phase DD-1.

> **If running BCG phases fresh:** Execute all phases below before DD phases.

Read these first:
- `.claude/skills/bcg-team/references/bcg-framework-5-lenses.md` — analytical framework
- `.claude/skills/dd/references/tight-retry-template.md` — watchdog-aware agent caps

---

## 🛡️ Phase-Gate Protocol (MANDATORY after every phase)

The 600-second stream watchdog can kill agents mid-Write with no automatic recovery.
After every phase below, run the phase-gate script to verify expected files landed.
If any are missing, **retry the responsible agent once with tighter caps** (see
`tight-retry-template.md` for per-agent search/line/time caps).

**Gate command (run after every phase):**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  <phase-name> "$OUTPUT_DIR" [segment-slugs]
```

Phase names: `phase-minus-1` | `phase-0` | `phase-1` | `phase-1.5` | `phase-2-dd-2` | `phase-dd-3a` | `phase-dd-3b` | `phase-dd-4`

**On FAIL (exit code 1) — retry policy:**
1. Identify which agent owns each MISSING file (1-to-1 mapping per phase).
2. Relaunch that agent ONCE with the matching cap row from `tight-retry-template.md`
   pasted at the top of the prompt as `🚨 HARD CONSTRAINTS`.
3. Run the gate again.
4. If gate fails a second time:
   - If file is non-blocking (data-scientist, domain-expert, advanced-analytics) →
     continue with `DEGRADED` flag in `dd-engagement.log`.
   - If file is blocking (segments, portfolio, master report) → halt the phase,
     surface the failure to the user, and ask whether to (a) write a manual stub,
     (b) skip the deliverable, or (c) retry once more with even tighter caps.

**On OK (exit code 0):** proceed to next phase.

Every agent prompt in this pipeline should include the universal boilerplate from
`tight-retry-template.md` — search cap, line cap, time target. Failure to inject
these caps is the root cause of watchdog kills.

---

### BCG Phase -1 — Data Collection

One Agent call — bcg-researcher:

```
Company: [name]
Industry/Context: [context from DD brief]
Output file: [OUTPUT_DIR]/company-brief.md
Language: [language]

This is a Due Diligence engagement. In addition to standard data collection, pay special attention to:
- Any regulatory investigations, lawsuits, or compliance issues
- Customer concentration signals (large customer mentions)
- Management changes in the last 24 months
- Any negative press, whistleblower reports, or short-seller coverage
- Working capital anomalies or accounting restatements

Collect from: SEC EDGAR (10-K, 10-Q), financials, competitors, news (last 24 months), LinkedIn/social, industry.
Tag every data point: ✅ VERIFIED / ⚠️ ESTIMATED / ❌ NOT FOUND
Save complete output using Write tool.
```

Progress: `📚 BCG Phase -1 — Data Collection (bcg-researcher) → company-brief.md ⏳`

**🛡️ Gate after completion:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-minus-1 "$OUTPUT_DIR"
```
If FAIL → retry bcg-researcher once with caps from `tight-retry-template.md`. Then read `company-brief.md`. Output:
```
✅ BCG Phase -1 complete.
📊 [N] data points | [X%] verified | Key gaps: [list]
🚀 Launching BCG Phase 0...
```

---

### Phase -1.5 — Mega-Cap Detection (silent, runs after researcher)

After reading `company-brief.md`, scan it for **market capitalization** and **sell-side analyst coverage**.

Set the engagement-wide flag `MEGA_CAP` per these rules:
- **MEGA_CAP=true** if market cap >$100B AND (sell-side coverage ≥20 analysts OR ticker is in S&P 100)
- **MEGA_CAP=false** otherwise

Persist the flag to `dd-engagement.log`:
```markdown
## Phase -1.5 — Classification
Market Cap: $X
Analyst Coverage: N
MEGA_CAP: true / false
```

**When MEGA_CAP=true, the pipeline activates these optimizations:**
1. Phase 1 segment tiering: ONLY top-2 segments by revenue get Tier-1; remaining 3–5 default to Tier-2 (overrides market-map.md tier assignments)
2. Phase 1.5/DD-1 hypothesis-tester: pre-answer H-V1, H-K1, H-P1 from consensus; cap remaining searches at 3/hypothesis (see dd-hypothesis-tester Step 1.5)
3. Phase 2 + DD-2 run as a single parallel block (see Phase 2+DD-2 fused below)

Pass `MEGA_CAP=true` (or false) as an explicit parameter in every downstream Agent call from this point.

---

### BCG Phase 0 — Market Mapping (Parallel)

In a **single message**, 2 Agent calls simultaneously:

**Agent call 1 — bcg-market-mapper:**
```
Company: [name]
Output file: [OUTPUT_DIR]/market-map.md
Language: [language]

IMPORTANT: Read [OUTPUT_DIR]/company-brief.md first.
Apply MBB segmentation principle. Identify 4–7 segments with real revenue.
Save complete output using Write tool.
```

**Agent call 2 — bcg-data-scientist:**
```
Company: [name]
Output file: [OUTPUT_DIR]/advanced-analytics.md
Language: [language]

IMPORTANT: Read [OUTPUT_DIR]/company-brief.md first.
Full quantitative analysis. Benchmark against minimum 10 competitors.
Market sizing (bottom-up + top-down). Segment-level growth analysis.
Save complete output using Write tool.
```

Progress: `🗺️ BCG Phase 0 — Market Mapping (parallel: bcg-market-mapper + bcg-data-scientist) ⏳`

**🛡️ Gate after both complete:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-0 "$OUTPUT_DIR"
```
If FAIL on `market-map.md` (blocking) → retry bcg-market-mapper with tighter caps.
If FAIL only on `advanced-analytics.md` (non-blocking) → log DEGRADED and continue.

Then read `market-map.md`. Extract segments. Output:
```
✅ BCG Phase 0 complete.
🗺️ [N] segments identified: [list]
🚀 Launching BCG Phase 1...
```

---

### BCG Phase 1 — Deep Segment Analysis (Parallel, Tier-Aware)

> **🚨 PRE-FLIGHT BATCH COUNT GATE — MANDATORY (added after Cursor DD 19.05.2026 bug post-mortem):**
>
> Before launching ANY segment-analyst, run this enumeration check:
> 1. `grep -E "СЕГМЕНТ [0-9]|^## \[?СЕГМЕНТ\b" [OUTPUT_DIR]/market-map.md | wc -l` → expected_segment_count
> 2. Also extract segment slugs from the "итоговая карта" table at the top of market-map.md
> 3. Expected agent count = expected_segment_count + 1 (segments + 1× domain-expert)
> 4. State explicitly to user: `"Phase 1 launch plan: N segments detected from market-map → launching N+1 agents in parallel:"` followed by the full enumerated list with slugs
> 5. Send a SINGLE message with EXACTLY N+1 Agent tool calls — verify the count matches before sending
>
> **Root cause of bug being prevented:** On Cursor DD, orchestrator launched 4 agents (3 segments + domain-expert) instead of 5 (4 segments + domain-expert) — missed S4 Autonomous Agents which had to run sequentially later, costing ~46 min wall-clock (~35% of total DD time).
>
> If the explicit count doesn't match enumerated segments — STOP and rebuild the batch. Do not proceed with an incomplete launch.

> **Tier-aware depth screening (UPDATED post-Microsoft DD 20.05.2026):**
> Before launching segment analysts, parse `market-map.md` for the **Depth Tier** column.
>
> **NEW LAUNCH MODEL — Tier-2 BATCH GROUPING:**
> - **Tier-1 (DEEP):** max 3 segments. Each gets its own parallel `bcg-segment-analyst` call with `tier=1`.
>   Criteria (from market-mapper): доля ≥15% revenue AND value creation potential.
> - **Tier-2 (GROUPED):** ALL non-Tier-1 segments go into ONE batched agent call with `tier=2-batch`.
>   Single agent processes 2-5 Tier-2 segments → outputs `segment-tier2-grouped.md` (1-1.5 pages per segment).
> - **Domain expert:** always 1 separate call.
>
> **Total parallel calls in Phase 1: 3-5** (was up to 8+ in pre-Microsoft pipeline).
> Wall-clock target: 15-20 min (Tier-1 bottleneck only) vs prior 25-35 min.
>
> **Empirical evidence (Microsoft DD 20.05.2026):** Pre-update launched 8 agents (3 Tier-1 + 4 Tier-2 + 1 expert). Tier-2 segments each took 7-11 min in parallel. Grouped Tier-2 batch estimated 8-12 min total → saves ~5-10 min wall-clock without verdict-quality loss.
>
> **🆕 Mega-cap override (if `MEGA_CAP=true`):** force top-2 ONLY at Tier-1; everything else into Tier-2 batch (overrides market-map tier flags).
> For Microsoft: Azure + M365 Tier-1; Gaming + Dynamics + Search + LinkedIn + Windows-Consumer → ONE Tier-2 batch.

In a **single message**, launch EXACTLY 3-5 Agent calls simultaneously:
- 2-3× `bcg-segment-analyst` for Tier-1 segments (one per segment, `tier=1`)
- 1× `bcg-segment-analyst` for Tier-2 batch (`tier=2-batch` with full segment list)
- 1× `bcg-domain-expert`

**Per Tier-1 segment — bcg-segment-analyst (max 3 calls):**
```
Company: [name]
Segment: [Segment name]
Tier: 1
Output file: [OUTPUT_DIR]/segment-[slug].md
Language: [language]
TARGET LENGTH: 4500-6500 words (HARD CAP)

Read first: [OUTPUT_DIR]/company-brief.md, [OUTPUT_DIR]/market-map.md

[Paste full segment context from market-map.md]

Full 3-lens analysis (Description → Advantage → Future with 4 forecasts),
10–15 strategies, all quality gates, WebSearch budget: 16 (HARD CAP, no exceptions).
At search 14/16 — STOP research, proceed to Strategy Generation with what you have.

Save complete output using Write tool.
```

**Tier-2 BATCH call — bcg-segment-analyst (ONE call для ВСЕХ Tier-2 сегментов):**
```
Company: [name]
Mode: tier=2-batch
Segments to analyze (N=[count]): [Segment A, Segment B, Segment C, Segment D, ...]
Output file: [OUTPUT_DIR]/segment-tier2-grouped.md
Language: [language]
TARGET LENGTH: 3000-4500 words TOTAL for entire batch

Read first: [OUTPUT_DIR]/company-brief.md, [OUTPUT_DIR]/market-map.md
(focus on sections covering these specific Tier-2 segments)

Process each segment in compact mode:
- ~1-1.5 pages per segment in single output file
- Description (250w) + Advantage (200w) + Future diagnosis (1 para) + 3-4 strategies + DQ score
- TOTAL WebSearch budget for entire batch: 12 calls (distribute by revenue weight)
- At search 10/12 — STOP, proceed to Strategy Generation

Save complete output to single file using Write tool.
```

**bcg-domain-expert:**
```
Company: [name]
Industry: [industry]
All 10 DD hypotheses: [H-M1 through H-X1]
Segments: [list all]
Output file: [OUTPUT_DIR]/domain-expert-input.md
Language: [language]

Read [OUTPUT_DIR]/company-brief.md first.
Provide domain expert input from industry insider perspective.
For each hypothesis, surface any non-public signals or industry knowledge.
Save complete output using Write tool.
```

Progress: `🔬 BCG Phase 1 — Segment Analysis ([N+1] agents in parallel) ⏳`

---

### BCG Phase 1.5 / DD-1 — FUSED PARALLEL BLOCK (4 agents, single message)

> **Architectural change:** `bcg-fact-checker`, `dd-market-validator`, and `dd-hypothesis-tester`
> are launched **simultaneously** right after Phase 1 completes. They have NO mutual dependency:
>   - `bcg-fact-checker` validates segment numbers against original sources
>   - `dd-market-validator` adversarially stress-tests TAM/CAGR/moat (primary input: segment files + market-map, NOT validation-report)
>   - `dd-hypothesis-tester` tests 10 DD hypotheses (validation-report and portfolio are optional inputs — agent runs with what exists)
>
> This collapses the previous Phase 1.5 → Phase 2 → Phase DD-1 chain (~25 min) into a single
> parallel block (~10–12 min). `bcg-portfolio-analyst` runs sequentially after, reading
> the validation report and hypothesis verdicts.

In a **single message**, launch 4 Agent calls simultaneously:

**Agent call 1 — bcg-fact-checker (Haiku):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/validation-report.md
Language: [language]
Segments: [list all segment file names]

Read all segment files and company-brief.md.
Validate all numerical claims. Score each segment: A/B/C/F.
Flag: ✅ VERIFIED / ⚠️ QUESTIONABLE / ❌ HALLUCINATED
Save complete output using Write tool.
```

**Agent call 2 — dd-market-validator (Sonnet):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-market-validation.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

Read from OUTPUT_DIR: company-brief.md, market-map.md, advanced-analytics.md,
all segment-[slug].md files.

NOTE: validation-report.md may not yet exist (running in parallel with bcg-fact-checker).
Do NOT block. Cross-reference against company-brief.md (verified data) directly.
A post-hoc consistency check runs after both finish if conflicts emerge.

Adversarially validate all market claims. Apply VRIO framework.
Check TAM reality, CAGR legitimacy, market share accuracy, moat durability.
Think like a short seller. Surface the gap between seller narrative and reality.
Save complete output using Write tool.
```

**Agent call 3 — dd-hypothesis-tester (Sonnet):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-hypothesis-report.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

The 10 DD hypotheses to test:
H-M1: [full hypothesis text from DD brief]
H-G1: [full hypothesis text]
H-C1: [full hypothesis text]
H-T1: [full hypothesis text]
H-R1: [full hypothesis text]
H-K1: [full hypothesis text]
H-P1: [full hypothesis text]
H-S1: [full hypothesis text]
H-V1: [full hypothesis text]
H-X1: [full hypothesis text]

NOTE: portfolio.md and validation-report.md may not yet exist (running in parallel).
The agent is designed to function without them — see dd-hypothesis-tester Step 1.
If a deal-critical segment file is missing → mark relevant hypothesis ⚠️ UNCERTAIN, do NOT fabricate.

Read available files from OUTPUT_DIR (mandatory: company-brief.md, market-map.md;
strongly preferred: segment-*.md).
For each hypothesis: search for disconfirming evidence first, then confirming.
Render verdict: ✅ CONFIRMED / ⚠️ UNCERTAIN / ❌ REFUTED.
Save complete output using Write tool.
```

**Agent call 4 — bcg-digester (Haiku, runs after the other 3 — see note):**
> The digester does not need to run in the same message; it runs as a thin pass
> AFTER the 3 above complete (~30 seconds, Haiku). It compresses the 3 outputs into
> `phase-1-digest.md` for downstream agents. Defer the digester call to immediately
> after the parallel block completes (see Phase 1.5-Complete block below).

Progress:
```
🔄 Phase 1.5 / DD-1 — Fused Parallel Block (3 agents)
   ├── bcg-fact-checker (Haiku)        → validation-report.md
   ├── dd-market-validator (Sonnet)    → dd-market-validation.md
   └── dd-hypothesis-tester (Sonnet)   → dd-hypothesis-report.md
   ⏳ Running in parallel — saves ~10–15 min vs. previous sequential chain...
```

---

### Phase 1.5-Complete — Rule 14 Early-PASS Gate + Digest

After all 3 agents above complete, read `dd-hypothesis-report.md`. Count ❌ REFUTED hypotheses.

**🚨 RULE 14 EARLY-PASS GATE (mandatory check):**

If `dd-hypothesis-report.md` shows **3 or more ❌ REFUTED hypotheses**, the verdict is **automatic PASS**. Short-circuit the remaining pipeline:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULE 14 TRIGGERED — Automatic PASS (early)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[N] refuted hypotheses detected:
- [H-Xn]: [refutation reason, 1 sentence]
- [H-Yn]: [refutation reason]
- [H-Zn]: [refutation reason]

3+ refuted = PASS, no exceptions (per dd-output-standard.md Rule 14).

Short-circuiting pipeline:
- Skipping Phase 2 (portfolio-analyst — not load-bearing for PASS verdict)
- Skipping Phase DD-2 (risk-analyst + red-team — directional only, not decisive)
- Jumping directly to abbreviated dd-production-decision-first (PASS-mode)
```

If user confirms (or auto-proceed flag set), jump to **Phase DD-3a (PASS-mode)** at bottom — `dd-production-decision-first` runs with reduced inputs (no portfolio, no risk matrix, no red team), reports PASS verdict with the refuted-hypothesis evidence as primary justification.

**Otherwise (fewer than 3 refuted):** proceed to digester + portfolio synthesis.

**Phase digest call (one Agent — bcg-digester, Haiku, ~30 sec):**
```
Phase: 1.5-and-DD-1
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/phase-1.5-digest.md
Language: [language]
Source files to digest:
  - [OUTPUT_DIR]/validation-report.md
  - [OUTPUT_DIR]/dd-market-validation.md
  - [OUTPUT_DIR]/dd-hypothesis-report.md

Condense each into 1 paragraph + key numbers + flags. Downstream portfolio-analyst
and DD-2 agents will read this digest instead of re-reading all 3 full files.
```

**🛡️ Gate before advancing:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-1.5 "$OUTPUT_DIR"
```
If FAIL → retry the responsible agent(s) once with caps from `tight-retry-template.md`.
Also gate Phase 1 (segment files) here if you didn't already:
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-1 "$OUTPUT_DIR" "<comma-separated-segment-slugs>"
```

Output to user:
```
✅ Phase 1.5 / DD-1 complete (parallel).
📋 Validation scores: [Seg1: X, Seg2: X, ...]
📊 Market Validation: [score A/B/C/F] | [N] red flags
📋 Hypotheses: [N] confirmed / [N] uncertain / [N] refuted
📄 Digest: phase-1.5-digest.md ([N] words)

🚀 Launching FUSED Phase 2 + DD-2 (3 agents parallel)...
```

---

### Phase 2 + DD-2 — FUSED PARALLEL BLOCK (Portfolio + Risk + Red Team)

> **Architectural change (May 2026):** Portfolio synthesis, risk matrix, and red team
> all derive from the same upstream artifacts (segment files + dd-market-validation +
> dd-hypothesis-report + digest). Since the synthesis agents no longer WebSearch
> (they are read-only — see their agent definitions), they have NO cross-dependency on
> each other. All three launch simultaneously in a single message.
>
> Wall-clock: was ~264 min sequential (Phase 2 ~160 + DD-2 ~104). Now ~15–25 min for all
> three in parallel (Haiku synthesis with no WebSearch).

In a **single message**, 3 Agent calls simultaneously:

**Agent call 1 — bcg-portfolio-analyst (Haiku, read-only):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/portfolio.md
Language: [language]
Segments: [list all segment files]
MEGA_CAP: [true / false]

Default read for context: [OUTPUT_DIR]/phase-1.5-digest.md
Mandatory full reads: all segment-*.md files (for strategy IDs and revenue numbers).
Read also: dd-market-validation.md, dd-hypothesis-report.md (just finished, available).

When data conflicts with validation-report → USE validation-report values.
Build full portfolio view: MBB Matrix, synergies, resource allocation.
Apply Selection Lens. Final recommendation.

🚫 NO WEBSEARCH — synthesis only. Flag [MISSING] if needed; DD-3a will backfill.
Save complete output using Write tool.
```

**Agent call 2 — dd-risk-analyst (Haiku, read-only):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-risk-matrix.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]
MEGA_CAP: [true / false]

Read these inputs from OUTPUT_DIR:
- phase-1.5-digest.md (default context)
- company-brief.md, market-map.md
- all segment-*.md
- dd-market-validation.md, dd-hypothesis-report.md (just-finished)

NOTE: portfolio.md is being generated IN PARALLEL with this agent — do NOT block on it.
If a portfolio-level signal is needed, derive it yourself from segment files. A delta-pass
runs only if portfolio surfaces something material that risk-matrix missed.

Build comprehensive risk matrix: minimum 15 risks across 8 categories.
Score each risk: Probability × Impact → Severity (Critical/High/Medium/Low).
Deep-dive on all Critical and High risks.
Identify risk clusters (correlated risks).
Flag deal breakers. Recommend deal protections.

🚫 NO WEBSEARCH — synthesis only.
Save complete output using Write tool.
```

**Agent call 3 — dd-red-team (Haiku, read-only):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-red-team.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]
MEGA_CAP: [true / false]

Read these inputs from OUTPUT_DIR:
- phase-1.5-digest.md (default context)
- company-brief.md, market-map.md
- all segment-*.md
- dd-market-validation.md, dd-hypothesis-report.md (just-finished)

NOTE: portfolio.md is being generated IN PARALLEL — do NOT block. Build the bear case
from segment files + validation + hypothesis report directly.

Build adversarial analysis:
1. Bear case with 5+ specific arguments + financial model (bull/base/bear/deep bear)
2. Short thesis (why this deal fails)
3. Three stress scenarios (macro, competitive, regulatory) — quantified
4. Pre-mortem: "It's 3 years later and the deal failed. What happened?"
5. Optimism bias audit

🚫 NO WEBSEARCH — adversarial weaponization of existing facts. DD-1 already collected them.
Save complete output using Write tool.
```

Progress:
```
🔄  Phase 2 + DD-2 — FUSED PARALLEL BLOCK (3 agents)
   ├── bcg-portfolio-analyst (Haiku, read-only) → portfolio.md
   ├── dd-risk-analyst       (Haiku, read-only) → dd-risk-matrix.md
   └── dd-red-team           (Haiku, read-only) → dd-red-team.md
   ⏳ Running in parallel — saves ~4h vs sequential...
```

**🛡️ Gate after all 3 complete:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-2-dd-2 "$OUTPUT_DIR"
```
If FAIL on any of `portfolio.md`, `dd-risk-matrix.md`, `dd-red-team.md`:
- Each is blocking for DD-3a. Retry the responsible agent once with caps from
  `tight-retry-template.md` (read-only synthesis row: 0 searches, 300-350 lines, 6 min).
- This is the phase most prone to watchdog kills because all 3 agents Write large outputs.

After all 3 complete and gate passes, read all 3 files. If portfolio surfaces a Critical
risk that risk-matrix missed (rare — segment files already covered it) → append a note
to risk-matrix manually. Do NOT re-run the agents.

> **Note:** BCG Phases 2.5 (GTM) and 3 (final-report.md) are skipped in DD mode.
> The DD report (dd-decision-first.md) replaces final-report.md as the primary deliverable.
> If user wants GTM analysis after DD, suggest running `/bcg-team --dir [OUTPUT_DIR]`.

---

## DD PHASES

> **Phase DD-1 + DD-2 have been merged into the fused blocks above.**
> What used to be a sequential chain (Phase 1.5 → 2 → DD-1 → DD-2, ~6 hours) is now
> 1.5/DD-1 fused → 2+DD-2 fused (~30 min wall-clock).

**Digest pass — bcg-digester (Haiku, ~30 sec):**
```
Phase: 2+DD-2
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/phase-dd2-digest.md
Source files: portfolio.md, dd-risk-matrix.md, dd-red-team.md
Compress into 1 paragraph per file + key numbers + flags + Adversarial Twin tripwires summary.
```

Output to user:
```
✅ Phase 2 + DD-2 (fused) complete.

🎯 BCG Recommendation: [Segment X — Strategy ID: Name]
🚨 Risks: [N] Critical | [N] High | [N] Medium | [N] Low
🔴 Deal breakers flagged: [N]
🐻 Bear case value: $[Xm] ([X]% of asking price)
🎯 Adversarial Twin tripwires: [N] pre-committed exit triggers
📊 Red Team verdict: [verdict]

🚀 Launching Phase DD-3: Master Report...
```

Update `dd-engagement.log` — append Phase 2 + DD-2 results.

---

### Phase DD-3a — Master Report (Solo)

> **Architectural change:** `dd-production` (legal/institutional layer) has been moved to DD-3b
> as a Haiku-derive pass (reformats master, does not re-synthesize). DD-3a now runs ONLY the
> master report production. This eliminates the previous ~10-min duplicate synthesis.

One Agent call — dd-production-decision-first (Sonnet):

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-decision-first.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

REQUIRED first reads:
1. .claude/skills/dd/references/dd-output-standard.md (15 rules)
2. .claude/skills/dd/references/templates/dd-decision-first.md (structural reference)

Then read ALL files from OUTPUT_DIR (this agent is the exception — it reads everything in full):
BCG: company-brief.md, market-map.md, portfolio.md, validation-report.md, all segment-*.md
DD: dd-market-validation.md, dd-hypothesis-report.md, dd-risk-matrix.md, dd-red-team.md
Digests (cross-reference only): phase-1.5-digest.md, phase-dd2-digest.md

Assemble the master Decision-First DD Report applying ALL 15 rules from the standard:
- Verdict block with threshold ladder (PASS @ $X / CONDITIONAL @ $Y / PROCEED @ $Z)
- One-line bottom line + 10-second decision + entry warning + personal pain hook
- Self-identification table (Rule 8)
- 3+ narrative failure scenarios (Rule 10 — NOT bullet lists)
- Hypothesis scorecard with 3+ refuted = automatic PASS rule (Rule 14)
- Risk matrix (20 risks) with "So what?" blocks (Rule 4) + decision anchors (Rule 5)
- Adversarial Twin 90-day exit triggers (carry forward from dd-red-team.md verbatim)
- Value bridge with probability-weighted expected return (Rule 13)
- Pre-mortem as future-dated first-person narrative (Rule 11)
- Strong end CTA in code block (Rule 9)

Leave a clear anchor for Section 1.5 — "Non-Obvious Insights" — to be filled by dd-insight-booster.
Add as placeholder: `# SECTION 1.5 — NON-OBVIOUS INSIGHTS\n*To be inserted by dd-insight-booster after this report saves.*`

Lead with verdict. Dollar amounts before percentages (Rule 6). Position, not observation (Rule 15).
Save to [OUTPUT_DIR]/dd-decision-first.md using Write tool.
```

Progress:
```
📄 Phase DD-3a — Master Report (solo)
   └── dd-production-decision-first (Sonnet) → dd-decision-first.md (PRIMARY)
   ⏳ Running...
```

**🛡️ Gate after completion:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-dd-3a "$OUTPUT_DIR"
```
If FAIL → `dd-decision-first.md` is the primary deliverable; retry is MANDATORY.
This agent is the longest writer in the pipeline (~700 lines target). It is highly
watchdog-prone if not constrained. Retry with the two-pass instruction:
"Save a skeleton via Write first (300 lines), then Edit specific sections to flesh out
content. Never compose a single Write payload >600 lines."

After completion, read `dd-decision-first.md` to verify the verdict and key figures.

Output:
```
✅ Phase DD-3a complete.
📄 Master report: dd-decision-first.md
🚀 Launching Phase DD-3b: Summary layers + Legal layer + Insight Booster (3 parallel)...
```

---

### Phase DD-3b — Derivation Trio (Parallel, depends on DD-3a)

> **Architectural change:** DD-3b now runs THREE derivation agents in parallel, all reading
> the master `dd-decision-first.md`. All three are non-synthetic (no new analysis):
>   1. `dd-production-summary` (Haiku) → derives `dd-mid.md` + `dd-short.md`
>   2. `dd-production` (Haiku) → derives institutional `dd-report.md` (legal layer)
>   3. `dd-insight-booster` (Sonnet) → EDITS master to insert "Non-Obvious Insights" section
>
> The 3 agents touch different output files and do NOT conflict. dd-insight-booster edits
> `dd-decision-first.md` in place; the other two write new files. All run from a single
> message — wall-clock ~3–5 min (was ~5–8 min sequential).

In a **single message**, 3 Agent calls simultaneously:

**Agent call 1 — dd-production-summary (Haiku):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output files:
  - [OUTPUT_DIR]/dd-mid.md
  - [OUTPUT_DIR]/dd-short.md
Language: [language]

REQUIRED first reads:
1. .claude/skills/dd/references/dd-output-standard.md (Rules 2, 4, 7, 13, 15)
2. .claude/skills/dd/references/templates/dd-mid.md (structural reference)
3. .claude/skills/dd/references/templates/dd-short.md (structural reference)
4. [OUTPUT_DIR]/dd-decision-first.md (master — the ONLY source of facts/numbers)

Derive two layers:
- dd-mid.md (~150 lines, 5-min pre-meeting briefing): Top-5 issues with So what? blocks,
  hypothesis scorecard, value bridge, "this deal only works if" conditions.
- dd-short.md (~50 lines, 10-second decision page): Verdict, Deal Score, fair value gap,
  3 deal-breaks triggers, biggest risk as one sentence, recommended actions with specifics.

STRICT RULE: Do NOT invent new numbers, risks, or hypotheses. Everything must trace back to
the master. If something is missing from the master, flag with [MISSING — flag to dd-production-decision-first]
rather than fabricating.

Cross-file consistency check before saving — verdict, confidence, deal score, fair value range,
expected loss, and all 3 deal-breaks triggers must match the master exactly.

Save both files using Write tool.
```

**Agent call 2 — dd-production (legal layer, Haiku-derive):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-report.md
Deal type: [deal-type]
Asking price: [asking-price]
Language: [language]

This is a Haiku-derive pass. Read [OUTPUT_DIR]/dd-decision-first.md as your ONLY source
of facts/numbers/verdicts. Reformat into traditional institutional/legal-style structure.
Do NOT introduce new analysis. Do NOT WebSearch. If a number is missing from the master,
flag [MISSING — flag to dd-production-decision-first] rather than fabricating.

See dd-production agent definition for the institutional report structure.
Save to [OUTPUT_DIR]/dd-report.md using Write tool.
```

**Agent call 3 — dd-insight-booster (Sonnet):**
```
Company: [name]
Output directory: [OUTPUT_DIR]
Target file (edit in place): [OUTPUT_DIR]/dd-decision-first.md
Language: [language]

Read [OUTPUT_DIR]/dd-decision-first.md + phase-1.5-digest.md + phase-dd2-digest.md
+ dd-risk-matrix.md + dd-red-team.md + dd-market-validation.md + dd-hypothesis-report.md.

Surface 3–5 non-obvious cross-file insights that a senior partner would notice but the master
report did not foreground. Use the Edit tool to insert a "# 🎯 NON-OBVIOUS INSIGHTS" block
in [OUTPUT_DIR]/dd-decision-first.md immediately after Section 1 (Verdict) and before Section 2.

If the master already contains the placeholder `# SECTION 1.5 — NON-OBVIOUS INSIGHTS`, replace
that block. Otherwise insert before Section 2.

Each insight: cross-file synthesis, counter-intuitive, decision-relevant, specific, falsifiable.
See dd-insight-booster agent definition for patterns and constraints.
```

Progress:
```
📄 Phase DD-3b — Derivation Trio (3 agents parallel)
   ├── dd-production-summary (Haiku)  → dd-mid.md + dd-short.md
   ├── dd-production (Haiku-derive)   → dd-report.md (legal layer)
   └── dd-insight-booster (Sonnet)    → edits dd-decision-first.md (+ Non-Obvious Insights)
   ⏳ Running in parallel...
```

**🛡️ Gate after all 3 complete:**
```bash
bash /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/dd/phase-gate.sh \
  phase-dd-3b "$OUTPUT_DIR"
```
If FAIL on `dd-mid.md` or `dd-short.md` → retry dd-production-summary (Haiku, low risk).
If FAIL on `dd-report.md` → retry dd-production (Haiku, low risk).
dd-insight-booster edits dd-decision-first.md in place; verify by checking the file size grew.

After all 3 complete, output:
```
✅ Phase DD-3b complete.
📄 Summary layers: dd-mid.md + dd-short.md
📄 Legal layer: dd-report.md (derived from master)
🎯 Non-Obvious Insights inserted into dd-decision-first.md
🚀 Launching Phase DD-4: Notion Export...
```

---

### Phase DD-4 — Notion Export (MANDATORY)

This phase is **mandatory**. The four decision deliverables MUST be exported to Notion immediately after generation so the client can read them in the place they expect. Supporting analyses (risk matrix, red team, etc.) are NOT exported in this phase — only the four decision layers.

**Files to export (whitelist):**
1. `dd-short.md` — 10-second decision
2. `dd-mid.md` — 5-min pre-meeting briefing
3. `dd-decision-first.md` — Full investment report (PRIMARY)
4. `dd-report.md` — Institutional / legal reference

**Step DD-4.1 — Verify Notion configuration:**

```bash
set -a; source /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.env 2>/dev/null; set +a

if [ -z "$NOTION_TOKEN" ]; then
  echo "STATUS:MISSING_TOKEN"
elif [ -z "$NOTION_MBB_ROOT_PAGE_ID" ]; then
  echo "STATUS:MISSING_ROOT"
else
  echo "STATUS:OK"
  echo "ROOT_ID:$NOTION_MBB_ROOT_PAGE_ID"
fi
```

**If STATUS is `MISSING_TOKEN` or `MISSING_ROOT`:** Output to user:
```
⚠️  Notion export skipped — credentials missing.

Add to .env:
  NOTION_TOKEN=secret_xxx
  NOTION_MBB_ROOT_PAGE_ID=<page_id>

After configuring, run manually:
  /notion-export [DIR_NAME]
```
Then SKIP DD-4.2, but continue to Step Final. Do NOT block the pipeline.

**If STATUS is `OK`:** proceed.

**Step DD-4.2 — Run export with auto-routing:**

> **Auto-routing (NEW):** The export script automatically creates the engagement page on first run AND persists `engagement_page_id` to `notion-feedback.json`. On subsequent runs against the same folder (e.g. follow-up reports, feedback iterations, additional analyses), the script auto-detects the existing engagement page and appends new files under it — no duplicate parents, no duplicate Feedback pages.
>
> First-run engagement page title is generated from directory name: `nvidia-19.05.2026` → `"NVIDIA — MBB Engagement (19.05.2026)"`. Customize the title in Notion after first export if you want a different name (e.g. "Strategic DD" instead of "MBB Engagement") — the script will keep using the same `engagement_page_id` regardless of title.

```bash
set -a; source /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.env; set +a

TARGET_DIR="[OUTPUT_DIR from Step 0]"

echo "Exporting 4 decision layers to Notion..."
echo "Target dir: $TARGET_DIR"
echo "Auto-routing: script will create new engagement page on first run, or reuse existing on follow-up."
echo "---"

NOTION_FILES_WHITELIST="dd-short.md,dd-mid.md,dd-decision-first.md,dd-report.md" \
  python3 /Users/cofounder/Documents/Projects/Due-Diligence-Vik/.claude/skills/notion-export/export_to_notion.py "$TARGET_DIR"
```

Stream output to user. The script will:
- Filter to exactly the 4 whitelisted files
- Create one Notion child page per file under `ENGAGEMENT_PAGE_ID`
- Create the `📋 Feedback` page automatically
- Save `notion-mapping.json` and `notion-feedback.json` into the engagement directory

Progress:
```
☁️  Phase DD-4 — Notion Export (4 decision layers)
   ├── dd-short.md           → Notion page
   ├── dd-mid.md             → Notion page
   ├── dd-decision-first.md  → Notion page
   └── dd-report.md          → Notion page
   ⏳ Uploading...
```

**Step DD-4.3 — Capture Notion URL:**

After the script finishes, extract the URL from its last line (`Parent page: https://notion.so/...`) and store it as `NOTION_URL`. This URL will be shown in Step Final.

**If export fails (401, 403, network error):**
- Save the error message to `[OUTPUT_DIR]/notion-export-error.log`
- Set `NOTION_URL=""` (empty)
- Continue to Step Final — DO NOT abort the engagement. The user already has all 12 files locally; they can retry export manually with `/notion-export`.

Append to `dd-engagement.log`:
```markdown
## Phase DD-4 — Notion Export
Status: [SUCCESS / FAILED / SKIPPED]
Engagement page: [NOTION_URL or "n/a"]
Files exported: 4 (dd-short.md, dd-mid.md, dd-decision-first.md, dd-report.md)
[If FAILED:] Error: [first line of error]
```

---

## Step Final — Completion

After Phase DD-3b completes, finalize `dd-engagement.log` — append:
```markdown
## Engagement Complete
Status: ✅ COMPLETED
Completed: [YYYY-MM-DD HH:MM]
Verdict: [PROCEED / CONDITIONAL / PASS]
Confidence: [X]% ([interpretation])
Deal Score: [X.X] / 10
Fair Value Range: $[Xm] — $[Xm]
Deal Breakers: [N]
Hypothesis Score: [N confirmed / N uncertain / N refuted]
Files generated: 4 (dd-short.md, dd-mid.md, dd-decision-first.md, dd-report.md)
```

Output to user:
```
## ✅ Strategic DD Complete — [Company]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT: [PROCEED / CONDITIONAL / PASS]
Confidence: [X]% ([interpretation])  ·  Deal Score: [X.X]/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Asking Price: [asking-price]
📊 DD-Adjusted Fair Value: $[Xm] — $[Xm] ([X]% of asking)
🔴 Deal Breakers: [N] — [list or "None"]
📋 Hypotheses: [N] confirmed | [N] uncertain | [N] refuted
[If 3+ refuted:] ⚠️  Rule 14 triggered — automatic PASS
🚨 Critical Risks: [N]  ·  High: [N]  ·  Medium: [N]  ·  Low: [N]

📁 Files saved to: research/[company]-[date]/

   READ IN THIS ORDER (each layer is independently useful):

   1. dd-short.md             ← 10-second decision  ⏱ start here
   2. dd-mid.md               ← 5-minute pre-meeting briefing
   3. dd-decision-first.md    ← Full investment report (45–60 min)  ← PRIMARY
   4. dd-report.md            ← Institutional / legal reference

   Supporting analysis:
   ├── dd-market-validation.md ← Market claims validation
   ├── dd-hypothesis-report.md ← 10 hypothesis test results
   ├── dd-risk-matrix.md       ← Full risk matrix (20 risks)
   ├── dd-red-team.md          ← Bear case + stress scenarios
   ├── portfolio.md            ← BCG strategic foundation
   └── company-brief.md        ← Verified raw data

[If NOTION_URL is non-empty:]
☁️  Notion: [NOTION_URL]
   ├── dd-short            ← uploaded
   ├── dd-mid              ← uploaded
   ├── dd-decision-first   ← uploaded
   ├── dd-report           ← uploaded
   └── 📋 Feedback         ← for client comments

[If NOTION_URL is empty (export failed):]
⚠️  Notion export failed — see notion-export-error.log
    Retry manually: /notion-export [DIR_NAME]

[If CONDITIONAL:]
⚠️  CONDITIONS BEFORE CLOSE:
[List specific conditions from dd-decision-first.md]

[If PASS:]
❌ PASS — Key reasons:
[List top 3 deal-breaking issues from dd-decision-first.md Section 5]

🎨 Generate PDF? Say "PDF" to create client-ready DD documents.
```

**If user says "PDF"** — run the `pdf-report` skill on all four DD decision layers:
```bash
for f in dd-short.md dd-mid.md dd-decision-first.md dd-report.md; do
  python3 .claude/skills/pdf-report/render_report.py [OUTPUT_DIR]/$f \
    --mode dd --company "[company]"
done
```
Produces four PDFs in Xata&co Bridgewater style with cover, TOC, verdict badge
(PROCEED / CONDITIONAL / PASS), severity chips, and "So what?" callouts.

---

## Failure Recovery Pattern — EFFICIENCY MODE

**Added post-Microsoft DD (20.05.2026)** — empirical observation: 3 of 14 agents (21%) failed with socket idle timeout / stream timeout when wall-clock exceeded 15-17 min.

**Rule:** Если агент упал с socket timeout / stream idle (>15 мин wall-clock) — НЕ перезапускай оригинальный prompt. Переключись на EFFICIENCY MODE.

**EFFICIENCY MODE prompt prefix (paste at top of retry prompt):**
```
EFFICIENCY MODE: Target {N} words (see target length table below). WebSearch budget
reduced to MAX 10 calls (HARD CAP). Most evidence is already in OUTPUT_DIR files
(phase digest + segment files + prior DD outputs) — leverage that.
Skip exhaustive sourcing on points where 2+ files already converge.
Be decisive on verdict, not exhaustive on evidence.
```

**Empirical evidence (Microsoft DD 20.05.2026):**
- `dd-market-validator`: first attempt 17 min → fail (stream idle); EFFICIENCY retry 9 min ✅
- `dd-hypothesis-tester`: first attempt 16:38 → fail; EFFICIENCY retry 8:35 ✅
- `bcg-portfolio-analyst`: first attempt 149 min → fail; EFFICIENCY retry 104 min (still slow — root cause was full-read of all segment files; fixed in bcg-portfolio-analyst.md "Шаг 1" rewrite)

---

## Target Length Table — MANDATORY for all agent prompts

Each agent prompt MUST include explicit `TARGET LENGTH: X-Y words` line. Empirically, unbounded prompts cause Sonnet to write 8,000-15,000-word outputs that trigger socket timeouts.

| Agent | Target words | Notes |
|-------|--------------|-------|
| bcg-researcher | 4,000-6,000 | Single source of truth, OK to be longer |
| bcg-market-mapper | 3,500-5,000 | 4-7 segments × ~500 words each + meta |
| bcg-data-scientist | 4,000-5,500 | Tables-heavy |
| bcg-segment-analyst Tier-1 | 4,500-6,500 | Per segment, full 3 lenses |
| bcg-segment-analyst Tier-2-batch | 3,000-4,500 | Entire batch of 2-5 segments |
| bcg-domain-expert | 3,500-5,000 | 10 hypotheses × 350 words |
| bcg-fact-checker | 3,000-4,500 | Tables + flags |
| dd-market-validator | 4,000-5,000 | **Previously unconstrained → caused timeout** |
| dd-hypothesis-tester | 4,500-5,500 | **Previously unconstrained → caused timeout** |
| bcg-portfolio-analyst | 3,500-4,500 | **Previously unconstrained → 149min timeout** |
| dd-risk-analyst | 4,000-5,000 | 15-20 risks |
| dd-red-team | 4,500-5,500 | Bear case + 3 scenarios + pre-mortem |
| dd-production-decision-first | 8,000-12,000 | IC-grade master, OK to be long |
| dd-production-summary | mid: ~4,000 \| short: ~800 | Derivation, no new content |
| dd-production (legal) | 4,000-6,000 | Reformatter, derivation |
| dd-insight-booster | 600-1,200 | 3-5 insights × 150-250 words |

**Rule:** If an agent's prior run timed out, set target at LOWER bound of range. If output came back complete in <12 min, target was correctly sized.

---

## Standards

- **DD hypotheses must be company-specific** — not generic. Customize H-M1 through H-X1 to the actual company and deal context in the Partner Brief.
- **Value Bridge is mandatory** — every DD must produce a $ gap between asking price and DD-adjusted value.
- **Bear case must be quantified** — not qualitative. Bear case revenue, margins, multiples, implied EV.
- **CONDITIONAL is not a dodge** — if verdict is CONDITIONAL, conditions must be specific and verifiable.
- **Files first** — every agent saves output before reporting back. Nothing lives only in context.
- **Tier-2 batching mandatory** — Phase 1 launches max 3 Tier-1 segment-analysts + 1 Tier-2-batch + 1 domain-expert = 5 agents max (post-Microsoft DD optimization).
- **Hard search caps** — Tier-1 segment-analyst: 16 WebSearch (down from 22). Tier-2 batch: 12 total. Cap enforcement at 87.5% threshold.
- **Portfolio agent reads digest only** — no full reads of all segment-*.md (causes timeouts at scale).
