# Pipeline v9 — Proposed Updates (post-integration audit)

**Date:** 2026-05-25
**Audit basis:**
- `methodology/improvement-log.md` (8 engagements 2026-04-07 → 2026-05-22)
- `methodology/framework-vs-pipeline-analysis-2026-05-22.md`
- `methodology/applied-changes.md`
- `methodology/PRD-pipeline-v9.md` (v9 release notes — bug-fix only)
- This repo's `/dd` blitz projection of v9 (`.claude/skills/dd/SKILL.md`)

v9.0.0 is explicitly a bug-fix release on v8 (no structural changes). The audit below surfaces **10 gaps with confirmed cross-engagement signal** that bug-fix-only could not address. Each is mapped to the exact stage(s) it would patch, with severity, evidence count, and a concrete spec edit.

Bundled into three releases — pick whichever cadence matches your roadmap.

---

## v9.1 — Quality Patches (quick wins, no structural change, ~1 week)

Same shape as v9.0.0 (content patches + new required fields on existing stages). Drop-in replacement for v8/v9.

### P1. Innovate Archetype Mandatory Generation Gate
**Patch:** `4_GENERATE` (Module 6 / Options, opus)
**Evidence:** 4/4 most recent engagements (Apple, Samsung, Amkor, Alphabet) — Innovate archetype absent or thin in every segment. Confirmed cross-engagement pattern in `improvement-log.md` 2026-04-09.
**Edit:**
- Add required field `innovate_strategies_generated[]` (array of strategy IDs that are net-new business model / category / revenue stream — not variants of existing products).
- Add explicit guard: "If no I strategy is technically viable for a segment in this time horizon → emit `I: NOT_VIABLE — <reason>`. Omission is a validator failure."
- Add VRule to `V4_validator_check`: any segment without ≥1 Innovate (or explicit `NOT_VIABLE`) → REVISE.

### P2. Question Mark Strategy-Count Floor
**Patch:** `4_GENERATE`
**Evidence:** Alphabet 2026-04-09: SPD (4 strategies) and Waymo (2 strategies) both Question Mark, both below the 8-floor that exists implicitly for Star/Cash Cow/Dog.
**Edit:**
- In `required_fields_per_stage["4_GENERATE"]` add `strategy_count_by_bcg_position` (dict: Star/Cash Cow/Dog/Question Mark → int).
- Floor: Star=10, Cash Cow=8, Dog=6, **Question Mark=8** (new).
- Provide structural template for Question Mark in stage content: `2×D, 2×S, 1×P, 1×F, 1×I, 1×exit (IPO/JV/divestiture)`.

### P3. Self-Derived TAM Prominence Warning
**Patch:** `1S0_segmenter` + `1B_industry_economics` + `6F_market_map_data`
**Evidence:** GFS 2026-04-10: IoT $15–22B self-derived (Tier-3 × estimated share ratio) labeled in footnote; flow propagated through to strategy revenue targets. First explicit identification of a 2–3 engagement pattern in specialty semiconductor.
**Edit:**
- New required field `tam_provenance` per segment: `tier1_sourced | tier2_sourced | self_derived`.
- When `self_derived=true`: stage content must emit a `⚠️ TAM — NO INDEPENDENT SOURCE` warning at the TOP of the TAM block (NOT in a footnote), with derivation methodology and explicit propagation note: "all downstream revenue targets using this TAM carry the same uncertainty."
- V1 validator rejects placement-in-footnote variants.

### P4. TAM-Ceiling Resolution Protocol (extension of Amkor Change 3)
**Patch:** `4_STRATEGY_FINANCIAL` (already mentions ceiling test — strengthen it)
**Evidence:** 3/3 confirmed occurrences (Micron AEBU, Amkor Automotive, GFS A&D). v9 mentions ceiling once but does not require resolution before downstream pass.
**Edit:**
- After computing FY+5 base case revenue per strategy, compute `implied_share_of_tam_pct`.
- Resolution rule (BLOCKING — stage cannot emit until resolved):
  - `> 50%` for non-dominant participant OR `> 80%` for any participant → resolve via one of:
    - (a) revise target to credible share
    - (b) provide expanded TAM with named source accommodating new revenue
    - (c) explicit label `target_not_independently_constrained: true`
- Required new field: `ceiling_resolution_status: resolved_(a)|resolved_(b)|labeled_(c)|pending`.

### P5. Part V GTM-Narrative Scope Gate
**Patch:** `6E_implementation_roadmap` (Module 8 / Delivery) + `6B_strategy_narrative`
**Evidence:** 5/5 most recent engagements with declining-but-residual GTM narrative redundancy (Samsung 800 → Apple 600 → Alphabet 400 → GFS 200–300 words duplicate per play).
**Edit:**
- `6E_implementation_roadmap` content restricted to: ICP one-sentence definition · 5-step channel sequence with timeline · ACV / deal-cycle / NRR three-row table · first-90-days with named action, counterparty, binary milestone.
- Explicitly forbidden in 6E: sentences describing why the market is attractive · what the company's competitive advantage is · what the strategy recommends (all covered in 6A / 6B / 6D).
- V5 inline contradiction check extended (one-line addition): also flag any sentence in 6E that could appear verbatim in 6B → REVISE.

### P6. Validation-Override Propagation Checklist
**Patch:** `1V_validation_report` (output schema) + `5_SELECT_final` (required reads)
**Evidence:** Micron / Amkor — partial propagation failures (corrections cited in fact-checker, lost in portfolio prose). Pattern fixed by Amkor Change 4; v9 inherits the rule but does not enforce it in spec.
**Edit:**
- `1V_validation_report` emits `corrections_required[]` (list of {claim, stated_value, verified_value, propagation_targets: [stage_ids]}).
- `5_SELECT_final` and `6A_decision_memo` must include explicit "Corrections applied" block at preamble naming every entry from `corrections_required[]` — V5 rejects if any are missing.

---

## v9.2 — Performance Patches (Microsoft post-mortem, ~2 weeks)

Stage-content additions plus orchestration metadata. Targets the wall-clock + reliability regressions Microsoft surfaced.

### P7. Tier-2 Batch-Grouping Rule (segmentation → context fan-out)
**Patch:** `1S0_segmenter` (sets tier) + Module 3 Context fan-out config
**Evidence:** Microsoft DD 2026-05-20: 4 separate Tier-2 segment-analysts ran in parallel but Tier-1 Azure was the bottleneck → wasted parallelism + 21% failure rate. Fixed in `bcg-market-mapper.md` and `bcg-segment-analyst.md` (`tier=2-batch` mode); v9 spec does not yet require batching.
**Edit:**
- `1S0_segmenter` required field: `tier1_segments[]` (hard cap 3, by revenue ≥ 15% AND value-creation potential).
- Add `tier2_batch_segments[]` (single group of all non-Tier-1 segments).
- Module 3 Context fan-out: `1B/1C/1D` per Tier-1 BU + ONE Tier-2-batch run (output: `1_DESC_LOCK_tier2_batch.md`).
- Update `orchestration.fan_out_caps.per_bu_soft_cap` from 5 → 4 (3 Tier-1 + 1 Tier-2 batch).

### P8. WebSearch Hard Caps in Stage Content
**Patch:** every L2 stage that uses `webSearch: true`
**Evidence:** Microsoft Azure analyst used 21 of 22 searches; wall-clock 26:44 blocked the Phase 1 wave.
**Edit:**
- Add `search_budget` field to each stage's `content`: Tier-1 context (`1B/1C/1D`) = 16 / Tier-2 batch = 12 / O0 lite = 12 / O1 public = 22 / domain-expert 0d = 8 / others = stage-specific.
- Add `search_budget_enforcement: hard_cap_at_87.5%` (worker must stop at 14/16 etc., not 16/16).
- New required field per stage: `search_used_count`.

### P9. Target-Length Table
**Patch:** every L2 stage with Sonnet/Opus model
**Evidence:** Microsoft socket timeouts when Sonnet wrote 8–15K-word outputs. Fixed in agent prompts; v9 spec carries no length cap.
**Edit:**
- Add `target_length_words` to each stage: Decision Memo (6A) ≤ 1800 · Strategy Narrative (6B) ≤ 2500/strategy · Description Lock (1_DESC_LOCK) ≤ 1500/BU · Portfolio Selection (5_SELECT_final) ≤ 3500 · Validator audits (V1–V5) ≤ 800.
- Stage worker must `wc -w` its draft before emit; if over target → trim, don't ship.

### P10. Context-Discipline Rule for Selection Module
**Patch:** `5_SELECT_final` required reads
**Evidence:** Microsoft Phase 2 portfolio-analyst loaded 7 segment files (>500KB) → 149-min first attempt, 104-min retry. Fixed in `bcg-portfolio-analyst.md`; v9 spec does not constrain reads.
**Edit:**
- `5_SELECT_final.inputs_from` policy:
  - PRIMARY (always read in full): `1V_validation_report`, `2_ADV_LOCK`, `3_FUT_LOCK`, `phase-1-digest.md` (when present), `1Y_cross_segment_synergies`.
  - SECONDARY (Grep only, not full reads): `1_DESC_LOCK_*` per BU.
  - FORBIDDEN: full reads of all `1B/1C/1D` raw stage files.
- Add validator check at `V5_validator_check`: confirm `5_SELECT_final.worker_telemetry.reads` did not exceed primary list.

---

## v10 — Structural Module Adds (≥1 month, framework analysis catch-up)

True modular extensions that close DD-only and BCG-2001-canonical gaps. Each is a new stage (or small cluster) added without disturbing v9 dependencies.

### P11. New `DD-X` cluster — DD-only stages (Module 8 sibling, conditional)

Triggered when engagement type = `M&A | PE | secondary`. All four run in parallel with `6E_implementation_roadmap`:

| New stage | Model | Owner | Purpose |
|---|---|---|---|
| `8X1_legal_blocker_audit` | sonnet | new `dd-legal-blocker-auditor` agent | License/permit transferability · change-of-control clauses · regulatory approvals · pending litigation · IP encumbrances → `dd-legal-blockers.md` |
| `8X2_stakeholder_alignment` | sonnet | new `dd-stakeholder-alignment` agent | Map material stakeholders · position (support/neutral/oppose) · influence · leverage · hostage situations → `dd-stakeholder-alignment.md` |
| `8X3_exit_readiness_qoe` | opus | extends `bcg-portfolio-analyst` | QoE recasting · IPO-readiness checklist (auditor / governance / segment reporting maturity) · 12-mo exit window viability → `dd-exit-readiness.md` |
| `8X4_carve_out_playbook` | opus | new `dd-carve-out-architect` agent | TSA scoping · standalone-cost gap · stranded-cost analysis · day-1 separation checklist · revenue dis-synergy (only fires when `deal_type=PE` with carve-out scope) → `dd-carve-out.md` |

Closes 4 of 5 "DD-critical missing" rows from framework analysis Part 3.B.

### P12. New `8Y` cluster — Operating-model + corp-dev (post-G7, optional)

Adds the BCG activation modules the framework analysis flagged as structural gaps:

| New stage | Model | Purpose |
|---|---|---|
| `8Y1_operating_model_blueprint` | opus | Talent location · structure · span of control · governance · day-1 vs steady-state |
| `8Y2_corp_dev_plan` | sonnet | M&A target list with rationale per target · bolt-on roll-up thesis support |
| `8Y3_pricing_rgm_diagnostic` | sonnet | Pricing strategy · RGM levers · packaging economics · price-elasticity assumptions |
| `8Y4_capability_gap_assessment` | sonnet | Gap-to-strategy mapping · build-vs-buy verdict per gap · 100-day capability priorities |

Triggered manually via `--with-activation` flag. Not on critical path.

### P13. New `Phase Post-G7+` cluster — value tracking + refresh triggers

Bridges the post-delivery gap the framework analysis flagged (C20–C22 in master pipeline):

| New stage | Cadence | Purpose |
|---|---|---|
| `9_value_realization_tracker` | quarterly post-delivery | Tracks % realization of each `5_SELECT_final.kpi_targets[]` · flags drift > 20% |
| `9_refresh_trigger` | event-driven | Listens for `signals.json` events (competitor M&A · regulatory shift · key-customer churn) → triggers automatic re-run of impacted segments only |

### P14. Per-segment Hypothesis Log
**Patch:** `1_DESC_LOCK` + Module 4/5/6 hand-offs
**Evidence:** Framework analysis 3.B.8 — master pipeline has per-segment running hypothesis JSON, v9 has only the 10 global H-D1..H-S1.
**Edit:** Add `segment_hypothesis_log.json` per BU written by `1_DESC_LOCK`, updated by `2_ADV_LOCK`, `3_FUT_LOCK`, `4_GENERATE`. Required input for `V5_validator_check` (confirms all per-segment hypotheses are explicitly resolved before final selection).

---

## Summary table

| ID | Patch | Module / Stage | v9.x release | Confirmed-pattern engagements | Effort |
|---|---|---|---|---|---|
| P1 | Innovate mandatory gate | 4_GENERATE · V4 | v9.1 | 4 (Apple/Samsung/Amkor/Alphabet) | S |
| P2 | Question Mark 8-floor | 4_GENERATE | v9.1 | 1 (Alphabet — first explicit) | S |
| P3 | Self-derived TAM warning | 1S0 · 1B · 6F | v9.1 | 1+2 latent (GFS + ~2 prior) | S |
| P4 | TAM-ceiling resolution | 4_STRATEGY_FINANCIAL | v9.1 | 3 (Micron/Amkor/GFS) | S |
| P5 | Part V scope gate | 6E · V5 | v9.1 | 5 (Samsung→GFS) | S |
| P6 | Validation propagation checklist | 1V · 5_SELECT_final · 6A | v9.1 | 2 (Micron/Amkor) | S |
| P7 | Tier-2 batch grouping | 1S0 + Module 3 fan-out | v9.2 | 1 (Microsoft) | M |
| P8 | WebSearch hard caps | every webSearch stage | v9.2 | 1 (Microsoft) | M |
| P9 | Target-length table | every Sonnet/Opus stage | v9.2 | 1 (Microsoft) | M |
| P10 | Selection context discipline | 5_SELECT_final · V5 | v9.2 | 1 (Microsoft) | M |
| P11 | DD-X cluster (4 stages) | new Module 8 sibling | v10 | framework analysis | L |
| P12 | 8Y activation cluster (4 stages) | new Module 8 sibling | v10 | framework analysis | L |
| P13 | Value tracker + refresh trigger | new Phase Post-G7+ | v10 | framework analysis | L |
| P14 | Per-segment hypothesis log | 1_DESC_LOCK + handoffs | v10 (or v9.2) | framework analysis | M |

---

## What NOT to add

The framework analysis lists ~30 more master-pipeline stages we don't carry (Pricing/MMM audit · ESG · Tax · Trust&Safety · etc.). **Do not add these to v9.** Each one inflates engagement cost without confirmed cross-engagement demand signal. Triage when a specific engagement type requests them.

Also do **not** revisit the 5 fixes already in v9.0.0 — they remain correct as-is.

---

## Suggested release plan

| Release | Patches | Effort | Risk | Confirmed-pattern delta |
|---|---|---|---|---|
| **v9.1** (next 1 week) | P1–P6 | ~1 week | Low (additive only) | Closes 6 confirmed-pattern issues, 13 engagement-occurrences |
| **v9.2** (next 2 weeks) | P7–P10 + P14 | ~2 weeks | Low-Med (orchestration tweaks) | Closes Microsoft regression class, reduces failure rate 21% → <5% |
| **v10** (next ~1 month) | P11–P13 | ~1 month | Med (new agents required) | Closes DD-critical coverage gaps + post-delivery value tracking |

All three releases are cumulative — same `build_pipeline_v9.py` pattern as v9.0.0.

---

*END proposals v9-update-2026-05-25*
