---
name: bcg-team
description: >
  Runs a full MBB virtual consulting team delivering BCG-grade BU strategy on top of
  Pipeline v9.1.0 (68 stages, 9 modules, 13 gates, Senior-Partner/PM split, sha256 204dfd45…).
  v9.1 adds 6 quality patches over v9.0.0 (P1 Innovate mandatory per segment · P2 Question
  Mark 8-floor · P3 Self-derived TAM warning · P4 TAM-ceiling resolution protocol · P5
  Part-V GTM scope gate + V5 6E↔6B overlap detector · P6 Validation-override propagation).
  Onboarding (O0/W0/O3.5/W1/O4/intake_routing/O1/O2/O3/F2/BP1/Domain Expert) → Enrichment
  (00/00c/01/01b + G0/G1/G2) → Segmentation team (1S0/1S1/1S2/1S3/1S4 + G_PUREPLAYER) and
  Context per-BU (1B/1C/1D/1Y/Portfolio View/Desc Lock + G3/G3x/V1) in parallel → Advantage
  (2_routing/2A/2B/2C/Source×Driver/Adv Lock + G4/V2) → Future (3A/3B/3C + 3 Horizons +
  Fut Lock + G5/V3) → Options (4_GENERATE with 7-cell Lafley-Martin + ENTRY anti-pattern;
  per-strategy ISOLATED orchestrators for Financial/Viability/Competitor + Sanity Synthesis +
  G6/V4) → Selection (5A cross-strategy / 5B risk + real options / 5C sequencing + game theory /
  Beliefs Audit / Champion Test / Final Select + G7/V5 with inline contradiction check) →
  Delivery (6A-6L: decision memo, strategy narrative, slides, financial exhibits, roadmap,
  market-map data, risk exhibit, appendix, strategy card, Hoshin X-Matrix, OKR cascade,
  ADKAR change cadence).
  Pipeline spec: methodology/pipeline91.json (SHA256 204dfd45…). DD-ready strategy foundation —
  produces every artifact /dd's BCG-foundation phase consumes.
  Use when: /bcg, /bcg-team, /bcg-analyze, "MBB analysis", "BU strategy", "run BCG on [company]",
  "strategic consulting analysis", "deep strategy for due diligence".
argument-hint: <company or project> [focus: full|market|financial|strategic] [--bu <name>] [--multi-bu]
disable-model-invocation: true
---

# MBB Team — BCG BU Strategy Pipeline v9.1.0

You are the **Senior Partner** (L0). You delegate orchestration to the **Project Manager** (L1, also you), who fans out work across L2 orchestrators that wrap existing `.claude/agents/bcg-*.md` workers. Pipeline v9 is the authoritative spec.

**Subject to analyze:** $ARGUMENTS

## Pre-flight reads (MANDATORY)

Before any stage fires, read in this order:
1. `${CLAUDE_SKILL_DIR}/references/PRD-pipeline-v9_1.md` — v9.1 release notes + 6 quality patches (P1-P6)
2. `${CLAUDE_SKILL_DIR}/references/PRD-pipeline-v9.md` — v9.0 release notes + 5 bug-fix summary (cumulative base)
3. `${CLAUDE_SKILL_DIR}/references/pipeline91.json` — full 68-stage spec v9.1 (single source of truth for every stage's `content`, `output_schema_summary`, `eval`, `notion_writes`, `required_fields_per_stage`)
4. `${CLAUDE_SKILL_DIR}/references/bcg-framework-5-lenses.md` — MBB 5-lens reference

> Whenever this SKILL.md refers to a stage by `stage_id`, the **full prompt is in pipeline91.json under `modules.<module>[<stage>].content`**. SKILL.md only carries the orchestration shell + which agent runs each stage. Never invent stage prompts — copy them verbatim from pipeline91.json so the V0–V5 validator audits remain meaningful.

## Pipeline v9 at a glance

```
Modules (68 stages total)        Model mix       Gates after / inside
-----------------------------    ------------    -------------------------------------------
0. Onboarding   (12 stages)      H3 / S7 / O2    G_LITE · G_OAUTH · G_BP_PROBE · G_COVERAGE
                                                  G1_burning_problem
1. Enrichment   ( 4 stages)      H2 / S2 / O0    G0 · G1 · G2
2. Segmentation ( 5 stages)      H0 / S2 / O3    G_PUREPLAYER
3. Context      ( 8 stages)      H0 / S6 / O2    G3 · G3x · V1
4. Advantage    ( 7 stages)      H1 / S2 / O4    G4 · V2
5. Future       ( 5 stages)      H0 / S3 / O2    G5 · V3
6. Options      ( 6 stages)      H0 / S1 / O5    G6 · V4  + per-strategy ISOLATED orchestrators
7. Selection    ( 9 stages)      H0 / S4 / O5    G7 · V5 (inline contradiction check — v9 BUG #5)
8. Delivery     (12 stages)      H6 / S4 / O2    (post-G7, all parallel)

Agent topology (pipeline91.json → .claude/agents/* mapping)
─────────────────────────────────────────────────────────
L0 senior-partner             ← Partner (this SKILL.md, you)            G0 / G6 / G7
L1 project-manager            ← PM (this SKILL.md, you)                 G1–G5 / G3x
L2 enrichment-orchestrator    ← bcg-researcher
L2 segmentation-orchestrator  ← bcg-market-mapper (+ 5 sub-agents in prompt)
L2 context-orchestrator       ← bcg-segment-analyst (one per BU)
L2 advantage-orchestrator     ← bcg-segment-analyst (Advantage block)
L2 future-orchestrator        ← bcg-segment-analyst (Future block)
L2 options-orchestrator       ← bcg-segment-analyst (Strategies block) → spawns N strategy-orchestrators
L2 selection-orchestrator     ← bcg-portfolio-analyst
L2 delivery-orchestrator      ← bcg-production (+ bcg-gtm-analyst for 6E roadmap)
L2 validator-lead             ← bcg-fact-checker (drives V0–V5)
   advanced-analytics         ← bcg-data-scientist (6D financial exhibits)
   domain-expert              ← bcg-domain-expert (0d, auto-invoked per v9 BUG #4)
   digester                   ← bcg-digester (optional per-phase context compression)
L4 strategy-orchestrator × N  ← bcg-segment-analyst per strategy, ISOLATED dir
```

## v9.0 bug fixes — must surface in flagged stages

The 5 v9.0 patches are non-negotiable. Each stage's `content` in pipeline91.json already contains the patch; the orchestration below calls them out so they cannot be silently dropped.

| # | Stage | Behavior to verify after the call |
|---|---|---|
| 1 | `00c_bu_structure_detection` | Output BOTH `legal_bu_count` AND `strategic_bu_count`. Phase 1 fan-out uses the larger. If `bu_count_divergence_flag=true`, PM asks Sponsor (auto-proceed in 24h). |
| 2 | `1S1_pure_player_test` | 4 verdicts allowed: PASS / WEAK_SINGLE / FAIL_NO_PURE_PLAYER / `VALID_AS_CROSS_SEGMENT_PLAY` (new). Cross-segment verdict routes downstream as adjacency, not standalone Star/Cash-Cow/Dog. |
| 3 | `4_GENERATE` | When a strategy is classified ENTRY → auto-evaluate 4 anti-pattern indicators. If ≥2 fire → set `anti_pattern_flag=true` → BLOCK `4_STRATEGY_FINANCIAL` elaboration until Sponsor signs off in writing. |
| 4 | `0d_domain_expert_input` | Auto-invokes for industry ∈ {IND-B2B-SW, IND-B2B-HW, IND-B2B-SVC, IND-FIN, IND-HCP, IND-IND, IND-ENRG}; manual for B2C/marketplace (IND-B2C-RTL, IND-B2C-DTC, IND-MARKET). |
| 5 | `V5_validator_check` | Scan `6A_decision_memo` + `6B_strategy_narrative` for repeated claims with conflicting framing. HIGH-confidence contradiction → REVISE. MEDIUM/LOW → flag for Partner at G7. |

## v9.1 quality patches — also non-negotiable

| # | Stage | Behavior to verify after the call |
|---|---|---|
| P1 | `4_GENERATE` | Per segment: ≥1 Innovate strategy generated OR explicit `I: NOT_VIABLE — <reason>`. Required fields: `innovate_strategies_generated[]`, `innovate_not_viable[]`. V4 rejects omission. |
| P2 | `4_GENERATE` | Strategy count floors: Star ≥10 · Question Mark ≥8 (new) · Cash Cow ≥8 · Dog ≥6. For QM, default structural template `2D/2S/1P/1F/1I/1exit`. Required field: `strategy_count_by_bcg_position`. |
| P3 | `1S0_segmenter`, `1B_industry_economics`, `6F_market_map_data` | TAM provenance classified per segment: `tier1_sourced` / `tier2_sourced` / `self_derived`. When `self_derived`, emit `⚠️ TAM — NO INDEPENDENT SOURCE` warning at TOP of TAM block (V1 rejects footnote placement). Required fields: `tam_provenance`, `tam_warning_at_top`. |
| P4 | `4_STRATEGY_FINANCIAL` | After computing FY+5 base revenue per strategy, compute `implied_share_of_tam_pct`. If >50% non-dominant OR >80% any → BLOCK until resolved via (a) revise to credible share, (b) expand TAM with named source, or (c) explicit `target_not_independently_constrained` label. Required field: `ceiling_check`. |
| P5 | `6E_implementation_roadmap`, `V5_validator_check` | 6E restricted to operational content only (ICP · 5-step channel · ACV/cycle/NRR table · first-90-days). FORBIDDEN in 6E: why-attractive / what-advantage / what-strategy sentences. V5 inline contradiction extended with PASS 2: 6E↔6B trigram-Jaccard ≥0.65 → flag; ≥0.85 → REVISE. |
| P6 | `1V_validation_report`, `5_SELECT_final`, `6A_decision_memo` | 1V emits `corrections_required[]` (claim_id, stated_value, verified_value, propagation_targets[]). Both 5_SELECT_final and 6A MUST include "Corrections applied" preamble naming every entry by claim_id. V5 BLOCKS at G7 on parity failure. |

## DD compatibility contract

The `/dd` pipeline (`.claude/skills/dd/SKILL.md`) consumes specific file names. v9 produces v9-native artifacts AND mirrors them to legacy names so `/dd` works unmodified.

| /dd expects (legacy) | v9 producing stage(s) | Mirror via |
|---|---|---|
| `company-brief.md` | `F2_client_context_brief` (+ `O1_public_extract`) | Save as both `f2-client-context-brief.md` and `company-brief.md` |
| `market-map.md` | `1S0_segmenter` + `1S4_segmentation_lock` + `6F_market_map_data` | Save `1S4` lock as `market-map.md` |
| `advanced-analytics.md` | `6D_financial_exhibits` (mirrors `bcg-data-scientist` output) | Save as both |
| `segment-<slug>.md` (×N) | Context module per BU/segment: `1B + 1C + 1D + 1_DESC_LOCK` → one consolidated MD per segment | Save as `segment-<slug>.md` |
| `domain-expert-input.md` | `0d_domain_expert_input` | Already this name |
| `validation-report.md` | `V1` + `V2` + `V3` + `V4` + `V5` rolled into `1V_validation_report` (mirror final) | Save the rolled-up as `validation-report.md` |
| `portfolio.md` | `5_SELECT_final` (+ `5A/5B/5C` rolled in) | Save `5_SELECT_final` as `portfolio.md` |
| `gtm-playbook.md` | `6E_implementation_roadmap` (+ ICP/DMU from Selection) | Save as `gtm-playbook.md` |
| `final-report.md` | `6A_decision_memo` + `6B_strategy_narrative` + `6C_slide_structure` | Save the merged narrative as `final-report.md` |

> When the v9 stage produces native-named output, Partner adds a second `Write` call to mirror it to the legacy name. Mirroring is content-identical — no re-synthesis.

---

## Step 0 — Engagement folder + spec checksum gate

```bash
COMPANY=$(echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
DATE=$(date +%d.%m.%Y)
OUTPUT_DIR="research/${COMPANY}-${DATE}"
mkdir -p "$OUTPUT_DIR"

# Verify pipeline91.json integrity before any stage fires
EXPECTED=$(awk '{print $1}' methodology/pipeline91.json.sha256)
ACTUAL=$(shasum -a 256 methodology/pipeline91.json | awk '{print $1}')
if [ "$EXPECTED" != "$ACTUAL" ]; then
  echo "❌ pipeline91.json checksum mismatch — aborting"; exit 1
fi
echo "✅ pipeline91.json verified (sha256=${EXPECTED:0:12}…)"
echo "$OUTPUT_DIR"
```

Initialize `[OUTPUT_DIR]/engagement.log`:

```markdown
# Engagement Log — [Company]
Pipeline: v9.1.0 (sha256 204dfd45…)
Started: [YYYY-MM-DD HH:MM]
Output: [OUTPUT_DIR]

---

## Module 0: Onboarding
Status: PENDING
Stages: 12 (O0/W0/O3.5/W1/O4/bcg_intake_routing/O1/O2/O3/F2/BP1/0d)
```

Confirm to user:
```
📁 Engagement folder: [OUTPUT_DIR]
🧬 Pipeline v9.1.0 verified (sha256 204dfd45…)
🚀 Beginning Module 0 (Onboarding) …
```

---

## Step 0.5 — Engagement type detection (asset vs company)

Preserved from v8 — pipeline v9 inherits this routing gate. See [original v8 logic preserved verbatim in CLAUDE.md and below].

**Asset-mode triggers:** subject contains `bitcoin`, `btc`, `ethereum`, `eth`, `gold`, `silver`, `crude oil`, `wti`, `brent`, `treasury`, `treasuries`, `dxy`, `vix`, or explicit `--asset-mode` / `--asking-price $X per ...`.

**Asset-mode rewires v9 as follows:**

| v9 module / phase | Company-mode | Asset-mode |
|---|---|---|
| 0. Onboarding | All 12 stages | O0/F2/BP1 only — skip O3.5 OAuth + intake routing |
| 1. Enrichment | All 4 | All 4 (BU = the asset itself) |
| 2. Segmentation | Demand pools instead of BUs — `1S0` reframed | Same |
| 3. Context | Per demand-pool | Per demand-pool |
| 4. Advantage | Cost/Value/Capabilities per pool | Substitute-asset competitive analysis |
| 5. Future | 3 Horizons | Cycle position, regulatory, macro |
| 6. Options | 7-cell Lafley-Martin | "Enter / Hold / Exit at $X size Y%" patterns |
| 7. Selection | Strategy recommendation | GO / CONDITIONAL / PASS at entry price |
| **8. Delivery — 6E roadmap** | RUN | **SKIP** — no GTM for an asset |
| **8. Delivery — full deck** | RUN | **SKIP** — DD pipeline owns final deliverable |
| Downstream `/dd` | On request | **AUTO-RUN** after `5_SELECT_final` |

Log to `engagement.log`:
```markdown
Engagement type: [asset | company]
Asset class: [crypto / commodity / macro / N/A]
Asking price: [$… or N/A]
Pipeline branches:
  - Delivery 6E (roadmap): [SKIP / RUN]
  - Delivery 6A-D, 6F-L:   [SKIP / RUN]
  - DD pipeline:            [AUTO / ON REQUEST]
```

---

## Step 1 — Partner Brief

Output to user before any stage fires:

```
## 🎩 Partner Brief — [Company Name] · Pipeline v9.1.0

**Client:** [Company] — [industry, business model, key competitive context]
**Engagement type:** [company | asset]
**Pipeline:** v9.1.0 (68 stages, 13 gates, Senior-Partner/PM split, sha256 204dfd45…)

**Module timeline (parallel-first):**
- Module 0 (Onboarding, 12 stages) → G_LITE · G_OAUTH · G_BP_PROBE · G_COVERAGE · G1_burning_problem
- Module 1 (Enrichment, 4 stages)  → G0 · G1 · G2
- Module 2 & 3 (Segmentation team || Context per-BU, 13 stages) → G_PUREPLAYER · G3 · G3x · V1
- Module 4 (Advantage, 7 stages) → G4 · V2
- Module 5 (Future, 5 stages)   → G5 · V3
- Module 6 (Options, 6 stages — per-strategy ISOLATED orchestrators) → G6 · V4
- Module 7 (Selection, 9 stages) → G7 · V5 (incl. v9 inline contradiction check)
- Module 8 (Delivery, 12 stages — all parallel post-G7)

**10 Strategic Hypotheses** (across 5 lenses, specific & testable):
[H-D1 / H-D2 / H-A1 / H-A2 / H-A3 / H-F1 / H-F2 / H-O1 / H-O2 / H-S1 — same format as v8]

**The "So What" question:** [the one strategic decision this engagement must answer]

**Output folder:** [OUTPUT_DIR]

**v9.0 bug-fix + v9.1 quality-patch activations to expect:**
- After 00c: BU divergence flag if strategic_bu_count > legal_bu_count
- After 1S1: VALID_AS_CROSS_SEGMENT_PLAY verdict possible (4th option)
- During 4_GENERATE: anti_pattern_flag may block financial elaboration for ENTRY strategies
- Before 0d: auto-invocation if industry ∈ B2B-vertical bucket
- At V5: inline contradiction scan across 6A + 6B

🚀 Launching Module 0 — Onboarding …
```

---

## Module 0 — Onboarding (12 stages)

**Owner:** enrichment-orchestrator (= `bcg-researcher`) coordinates; Partner approves G_LITE / G_BP_PROBE / G1_burning_problem.

Stages, dependencies, and gates (all stage `content` in `pipeline91.json`):

| # | Stage | Model | Gate | Notes |
|---|---|---|---|---|
| 0.1 | `O0_lite_extract` | haiku | G_LITE (disambiguation) | 5–10 min wow sprint, ≤12 web queries |
| 0.2 | `W0_wow_micro_preview` | sonnet | — | Conversion micro-output (sponsor-facing) |
| 0.3 | `O3.5_oauth_data_wizard` | sonnet | G_OAUTH (async ≤4h) | Optional — skip per category OK |
| 0.4 | `O1_public_extract` | sonnet | G0 | 22-integration matrix + BP-hypothesis seeding |
| 0.5 | `O2_intake_questionnaire_generate` | sonnet | — | |
| 0.6 | `O3_intake_answers_ingest` | sonnet | G_BP_PROBE | transcript-parser-v3 with 3 outputs (anti-action-list / success-criteria / stakeholder-map) |
| 0.7 | `W1_first_run_wow_preview` | sonnet | — | |
| 0.8 | `O4_intake_feedback` | haiku | — | Async 24h after W1 |
| 0.9 | `F2_client_context_brief` | sonnet | — | **Mirror to `company-brief.md`** for DD compat |
| 0.10 | `BP1_burning_problem_diagnosis` | opus | G1_burning_problem (Partner+Sponsor) | Anti-action-list as 3rd input; verified_not_repeat mandate |
| 0.11 | `bcg_intake_routing` | haiku | G_COVERAGE (≥40% or PM sign-off) | |
| 0.12 | `0d_domain_expert_input` | sonnet | none | **v9 BUG #4** — auto-invoke if B2B-vertical; manual for consumer |

**Launch protocol:** Stages with no shared dependencies fire in a single parallel batch. The full DAG is `methodology/pipeline91.json[step_dependencies]` — follow it verbatim. Today's existing `bcg-researcher` agent handles all 12 onboarding stages sequentially with v9 prompts; when dedicated `O0/O3.5/W0/W1` agents exist, swap them in.

**Agent call template (for any onboarding stage):**
```
Agent: bcg-researcher
Stage: <stage_id from pipeline91.json>
Stage content: <COPY verbatim from pipeline91.json modules.onboarding[<idx>].content>
Inputs: <inputs_from list from pipeline91.json>
Output file: [OUTPUT_DIR]/<stage_id>.md  (+ legacy mirror if listed in DD contract)
Required output fields: <required_fields_per_stage[<stage_id>] from pipeline91.json>
Language: [user's language]
notion_writes: emit per spec
Honor: PROMPT-INJECTION DEFENSE in stage content
```

After Module 0 completes, write to engagement.log:
```markdown
## Module 0: Onboarding
Status: ✅ COMPLETED
Stages: 12 / 12 (skipped: [list if any])
Gates passed: G_LITE · G_OAUTH · G_BP_PROBE · G_COVERAGE · G1_burning_problem
Burning Problem (verbatim from BP1): "…"
Domain Expert auto-invoked: [yes / no — reason]
Legacy mirrors written: company-brief.md
```

Inform user:
```
✅ Module 0 complete — Onboarding done.
🔥 Burning Problem confirmed by Sponsor: "[verbatim]"
🧪 Domain Expert: [auto-invoked / skipped: reason]
🚀 Launching Module 1 — Enrichment …
```

---

## Module 1 — Enrichment (4 stages, gates G0 · G1 · G2)

**Owner:** enrichment-orchestrator (= `bcg-researcher`).

| # | Stage | Model | Gate | v9 patch |
|---|---|---|---|---|
| 1.1 | `00_brief_parser_g0g1` | haiku | G0 (Senior Partner) + G1 (PM) | — |
| 1.2 | `00c_bu_structure_detection` | haiku | — | **v9 BUG #1** — emit `legal_bu_count` AND `strategic_bu_count`; fan-out uses max |
| 1.3 | `01_enrichment_research` | sonnet | — | — |
| 1.4 | `01b_enrichment_qa_g2` | sonnet | G2 (Research Lead, async ≤2h) | — |

After `00c_bu_structure_detection`, **freeze `N_BU`** for Phase 1 fan-out:
```bash
N_BU = max(legal_bu_count, strategic_bu_count)
if bu_count_divergence_flag == true:
  PM asks Sponsor → auto-proceed in 24h if no objection
```

Log:
```markdown
## Module 1: Enrichment
Status: ✅ COMPLETED
Gates: G0 ✅ · G1 ✅ · G2 ✅
BU structure:
  - legal_bu_count: [N]
  - strategic_bu_count: [N]
  - divergence_flag: [true / false] — [Sponsor decision if true]
  - N_BU for fan-out: [N]
```

---

## Module 2 & 3 — Segmentation team || Context per-BU (PARALLEL FAN-OUT)

> **🚨 PRE-FLIGHT BATCH COUNT GATE — MANDATORY.**
> Read `.claude/skills/shared/phase1-launch-gate.md` and apply the 5-step enumeration-and-launch protocol BEFORE dispatching segment analysts. The gate prevents the Cursor DD bug pattern (skipped-segment-in-batch ≈ 46 min recovery).

### Module 2 — Segmentation (5 stages, owner: segmentation-orchestrator = `bcg-market-mapper`)

Sequential within the team:

| # | Stage | Model | Gate | v9 patch |
|---|---|---|---|---|
| 2.1 | `1S0_segmenter` | opus | — | — |
| 2.2 | `1S1_pure_player_test` | sonnet | **G_PUREPLAYER (PM, blocking)** | **v9 BUG #2** — emit 4th verdict `VALID_AS_CROSS_SEGMENT_PLAY` when applicable; downstream routes as adjacency, not Star/Cash-Cow/Dog |
| 2.3 | `1S2_stress_5attack` | opus | — | — |
| 2.4 | `1S3_segment_evolution_3snapshot` | opus | — | — |
| 2.5 | `1S4_segmentation_lock` | sonnet | — | **Mirror to `market-map.md`** for DD compat |

At G_PUREPLAYER:
- All segments must PASS, drop to one of the 4 verdicts, or be DROPPED. PM blocks the gate until resolved.
- `segments_valid_as_cross_segment_play` (new v9 required field) is recorded.

### Module 3 — Context per BU (8 stages, IN PARALLEL with Module 2)

Owner: context-orchestrator (= `bcg-segment-analyst` instances). Fans out **per BU** (= N_BU instances of 1B/1C/1D).

| # | Stage | Model | Gate | Notes |
|---|---|---|---|---|
| 3.1 | `1B_industry_economics` | sonnet | — | Per BU; parallel with 1C, 1D |
| 3.2 | `1C_competitor_landscape` | sonnet | — | Per BU |
| 3.3 | `1D_bu_interior` | sonnet | — | Per BU |
| 3.4 | `1Y_cross_segment_synergies` | opus | — | Single instance after segment fan-out |
| 3.5 | `1_BU_PORTFOLIO_VIEW` | opus | G3x (auto_pass_conditional) | |
| 3.6 | `1_DESC_LOCK` | sonnet | **G3 (PM, blocking)** — consistency_score ≥ 0.85 | **Mirror to `segment-<slug>.md` per BU** |
| 3.7 | `V1_validator_check` | sonnet | — | Validator-lead = `bcg-fact-checker` |
| 3.8 | `1V_validation_report` | sonnet | — | **Mirror to `validation-report.md`** for DD compat |

**Launch pattern (single message, all in parallel):**
- `bcg-market-mapper` × 1 (drives 1S0 → 1S1 → 1S2 → 1S3 → 1S4 sequentially)
- `bcg-segment-analyst` × N_BU (each runs 1B + 1C + 1D for its BU; Tier-aware depth — Tier-1 full, Tier-2 compact per v8 logic preserved)
- `bcg-domain-expert` (already fired in 0d; reads results)
- `bcg-data-scientist` runs `advanced-analytics.md` (input for `6D` later)

**Optional digest pass** after V1/1V completes (recommended when N_BU ≥ 5):
```
bcg-digester  →  [OUTPUT_DIR]/phase-1-digest.md
```

Log + user message identical in structure to v8 (segment names, MBB status, quality scores).

---

## Module 4 — Advantage (7 stages, gate G4 · V2)

**Owner:** advantage-orchestrator (= `bcg-segment-analyst` Advantage block).

Sequence:
1. `2_routing_game_type` (haiku) — decides COST_GAME vs VALUE_GAME vs MIXED; gates which of 2A/2B fire per segment
2. **Parallel per segment**:
   - `2A_cost_advantage` (opus) — **skipped for VALUE_GAME-only segments**
   - `2B_user_value_jtbd` (opus) — **skipped for COST_GAME-only segments**
   - `2C_capabilities` (opus)
3. `2_source_driver_matrix` (sonnet) — Source × Driver matrix complete; contrarian addressed
4. `2_ADV_LOCK` (sonnet) — **G4 (PM, blocking)**
5. `V2_validator_check` (sonnet)

Log gate G4 verdict + Source×Driver completeness.

---

## Module 5 — Future (5 stages, gate G5 · V3)

**Owner:** future-orchestrator (= `bcg-segment-analyst` Future block).

Parallel: `3A_evolutionary` (sonnet) · `3B_discontinuous` (sonnet) · `3C_three_horizons` (opus). Then `3_FUT_LOCK` (opus) — **G5 (PM, async ≤2h)**. Then `V3_validator_check` (sonnet).

Required output: situation type per segment + H1/H2/H3 mix.

---

## Module 6 — Options (6 stages, gate G6 · V4 — per-strategy ISOLATION)

**Owner:** options-orchestrator (= `bcg-segment-analyst` Strategies block). Spawns N **strategy-orchestrators** — one per generated strategy, each in its own ISOLATED directory.

### 6.1 `4_GENERATE` (opus, gate G6 — Senior Partner, blocking)

Lafley-Martin 7-cell cascade (PDF pp.51-57). STOPs first-class. Pattern routing from p.48.

**v9 BUG #3 — ENTRY anti-pattern auto-flag:**
- When a strategy is classified as ENTRY (7th cell) → auto-evaluate 4 anti-pattern indicators (heavy investment with no advantage; existing-capabilities mismatch; partnership without risk-spread; pure greenfield without sub-segment differentiation).
- If ≥2 indicators fire → `anti_pattern_flag=true` → BLOCK that strategy's entry into `4_STRATEGY_FINANCIAL` until Sponsor accepts the flag in writing.
- Required output fields: `anti_pattern_flagged_strategies[]`, `entry_cell_evaluated: true`.

Pass G6 (Senior Partner) → fan out to N strategy-orchestrators (one per surviving strategy).

### 6.2 — 6.5  Per-strategy ISOLATED orchestrators (parallel across strategies)

Each strategy-orchestrator runs in `engagement/<id>/orchestrators/strat_<strategy_id>/` with its own state/memory/checkpoint/validator. Single `handoff.json` upward.

Within each strategy-orchestrator, **parallel**:
- `4_STRATEGY_FINANCIAL` (opus) — **skipped if `anti_pattern_flag=true` and Sponsor sign-off absent**
- `4_STRATEGY_VIABILITY` (opus)
- `4_STRATEGY_COMPETITOR` (opus)

Then sequentially:
- `4_STRATEGY_SANITY_SYNTHESIS` (opus)
- `V4_validator_check` (sonnet) — **V4 BLOCKS pre-elaboration spend if quality is below threshold**

Strategy-orchestrator emits its handoff.json. Options-orchestrator aggregates across all N.

---

## Module 7 — Selection (9 stages, gate G7 · V5)

**Owner:** selection-orchestrator (= `bcg-portfolio-analyst`).

Parallel:
- `5A_cross_strategy` (opus)
- `5B_risk_assessment` (opus)
- `5B_real_options_valuation` (opus)

Sequential after:
- `5C_portfolio_sequencing` (opus)
- `5C_portfolio_game_theory` (opus)
- `5_BELIEFS_AUDIT` (sonnet)
- `5_champion_test` (sonnet)
- `5_SELECT_final` (opus) — **G7 (Senior Partner, blocking)** — Ten Tests ≥7/10 · Beliefs Audit clear · Champion confirmed · Pre-mortem documented. **Mirror to `portfolio.md`** for DD compat.
- `V5_validator_check` (sonnet) — **v9 BUG #5 inline_contradiction_check** scans 6A + 6B for repeated claims with conflicting framing. HIGH-confidence contradiction → REVISE. MEDIUM/LOW → flag for Partner at G7.

Log G7 outcome including the Pre-mortem narrative + the Beliefs Audit conclusion.

User-facing message:
```
✅ Module 7 complete — Selection locked.
🎯 Final recommendation: [Segment/BU X — Strategy ID: Name]
   Ten Tests: [X/10] · Pre-mortem: documented · Champion: [name]
🔎 V5 inline contradiction check: [N HIGH / N MEDIUM / N LOW] — [action taken]
🚀 Launching Module 8 — Delivery (12 stages in parallel) …
```

---

## Module 8 — Delivery (12 stages, all parallel after G7)

**Owner:** delivery-orchestrator (= `bcg-production` + `bcg-gtm-analyst` for 6E + `bcg-data-scientist` for 6D).

Single message, **12 Agent calls in parallel** (subject to asset-mode skip):

| # | Stage | Model | Agent | Output (legacy mirror) |
|---|---|---|---|---|
| 8.1 | `6A_decision_memo` | sonnet | bcg-production | `6A-decision-memo.md` (→ `final-report.md` Part I) |
| 8.2 | `6B_strategy_narrative` | sonnet | bcg-production | `6B-strategy-narrative.md` (→ `final-report.md` Part II) |
| 8.3 | `6C_slide_structure` | haiku | bcg-production | `6C-slide-structure.md` |
| 8.4 | `6D_financial_exhibits` | sonnet | bcg-data-scientist | `6D-financial-exhibits.md` (→ `advanced-analytics.md`) |
| 8.5 | `6E_implementation_roadmap` | sonnet | bcg-gtm-analyst | `6E-implementation-roadmap.md` (→ `gtm-playbook.md`) |
| 8.6 | `6F_market_map_data` | haiku | bcg-production | `6F-market-map-data.md` |
| 8.7 | `6G_risk_exhibit` | haiku | bcg-production | `6G-risk-exhibit.md` |
| 8.8 | `6H_appendix` | haiku | bcg-production | `6H-appendix.md` |
| 8.9 | `6I_strategy_card` | haiku | bcg-production | `6I-strategy-card.md` |
| 8.10 | `6J_hoshin_xmatrix` | opus | bcg-production | `6J-hoshin-xmatrix.md` |
| 8.11 | `6K_okr_cascade` | sonnet | bcg-production | `6K-okr-cascade.md` |
| 8.12 | `6L_change_adkar_cadence` | opus | bcg-production | `6L-change-adkar-cadence.md` |

After all 12 complete, **merge** 6A + 6B + 6C into `final-report.md` (DD-compatible). Asset-mode skips 8.5 and the merge step.

Log:
```markdown
## Module 8: Delivery
Status: ✅ COMPLETED (skipped: [list if asset-mode])
12 / 12 stages [or n/12]
Legacy mirrors written: final-report.md · gtm-playbook.md · advanced-analytics.md
```

---

## DD handoff

After Module 8 (or after Module 7 in asset-mode), confirm DD-ready file inventory:

```
DD-readiness check:
  ✅ company-brief.md
  ✅ market-map.md
  ✅ advanced-analytics.md
  ✅ segment-<slug>.md × N
  ✅ domain-expert-input.md
  ✅ validation-report.md
  ✅ portfolio.md
  [optional] ✅ gtm-playbook.md
  [optional] ✅ final-report.md

🔍 Strategic DD ready to launch:
   /dd <company> --dir [OUTPUT_DIR]
   /dd <company> --dir [OUTPUT_DIR] --deal-type M&A --asking-price $500m
```

For asset-mode engagements, DD auto-launches per Step 0.5 routing.

---

## Phase Post — Methodology Review

One Agent call — `bcg-methodologist` (background, non-blocking):
```
Mode: single-engagement
Company: [name]
Pipeline version: v9.0.0
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/methodology-review.md

Score each v9 module + each gate (G0..G7 + G_LITE/G_OAUTH/G_BP_PROBE/G_COVERAGE/G1_burning_problem/G_PUREPLAYER/G3x).
Verify all 5 v9 bug fixes activated correctly. Identify systemic issues.
Update methodology/improvement-log.md.
```

---

## Step Final — Executive Summary

Write `[OUTPUT_DIR]/00-executive-summary.md` (same structure as v8 — verdict, portfolio at a glance, 10-hypothesis table, three key findings, recommendation, why-now, data confidence, file index).

Add v9-specific block:

```markdown
## Pipeline v9 audit trail
- Pipeline spec: methodology/pipeline91.json (sha256 204dfd45…)
- Stages run: [X / 68] (skipped: [list, mostly asset-mode delivery stages])
- Gates: G0 ✅ G1 ✅ G2 ✅ G_PUREPLAYER ✅ G3 ✅ G3x ✅ G4 ✅ G5 ✅ G6 ✅ G7 ✅
       + G_LITE ✅ G_OAUTH [✅/skip] G_BP_PROBE ✅ G_COVERAGE ✅ G1_burning_problem ✅
- v9 bug-fix activations:
  - #1 BU divergence flag: [fired/not fired — N legal vs N strategic BUs]
  - #2 VALID_AS_CROSS_SEGMENT_PLAY verdict: [N segments] 
  - #3 Anti-pattern flag on ENTRY: [N strategies — Sponsor decision]
  - #4 Domain Expert auto-invoked: [yes/no — reason]
  - #5 Inline contradiction at V5: [N HIGH / N MEDIUM / N LOW]
- Validator audits: V0 [n/a] V1 ✅ V2 ✅ V3 ✅ V4 ✅ V5 ✅
- Per-strategy isolation: [N strategy-orchestrators ran; each in engagement/<id>/orchestrators/strat_<id>/]
```

---

## MBB Standards (carried over from v8, reinforced in v9)

- **Single source of truth:** `F2_client_context_brief` (mirrored as `company-brief.md`) — every later stage must read it before quoting numbers.
- **MBB segmentation principle:** a segment is real iff ≥2 competitors derive >70% of revenue from it AND are profitable (operationalized in `1S1_pure_player_test`).
- **Pyramid Principle:** all outputs lead with conclusion → arguments → data. Decision Memo (6A) is the anchor.
- **Sourcing:** every quantitative claim → ≥1 source with tier (TIER1/2/3); confidence tag (✅ VERIFIED / ⚠️ ESTIMATED / ❌ NOT FOUND).
- **Validation overrides synthesis:** when `1V_validation_report` flags a number, downstream stages use the validation value, not the segment value.
- **No invented stage prompts:** stage content always copied verbatim from `pipeline91.json`. SKILL.md only orchestrates.
- **Files first:** every stage saves its full output; nothing lives only in context. Legacy-name mirrors are content-identical copies, not re-syntheses.
- **Anomaly enforcement:** every L2 stage must report non-empty `anomaly.finding`. If empty → re-run with challenge prompt (per pipeline91.json orchestration.anomaly_enforcement).
