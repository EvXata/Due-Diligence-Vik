# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A multi-agent AI system that delivers two integrated products:

1. **MBB Strategic Analysis** — full BCG-style consulting engagement (business unit strategy, portfolio strategy, GTM)
2. **Strategic Due Diligence** — investment-grade DD report (PROCEED / CONDITIONAL / PASS) for PE/VC/M&A/secondary deals

The DD pipeline runs on top of the BCG strategic foundation, adding adversarial validation, hypothesis testing, risk matrix, red team analysis, and a Value Bridge. Pricing: $500 / 48 hours (vs. $250K from MBB firms).

All agents are defined in `.claude/agents/`, all skills in `.claude/skills/`.

## Commands

### Strategic Due Diligence (PRIMARY PRODUCT)

**Run full DD pipeline (BCG foundation + DD phases):**
```
/dd <company>
/dd <company> --deal-type M&A --asking-price $500m
/dd <company> --deal-type PE --asking-price $2bn --language ru
/dd <company> --dir research/<existing-bcg-dir>   # use existing BCG output
/dd <company> --investor-profile retail-token-buyer   # add DD-3c memos for $-amount-driven investor
```
Delivers: **three-layer decision output** (10-sec → 5-min → 45-min) + Value Bridge + Risk Matrix + institutional reference.

The optional `--investor-profile` flag (`vc` | `family-office` | `retail-token-buyer` | `acquirer`) triggers an extra **Phase DD-3c — Investor-Profile Synthesis** that produces three audience-tailored memos: `bull-case.md` (what has to be true to make money), `customer-discovery.md` (DMU + churn analysis), `ma-exit-scenarios.md` (strategic acquirers + liquidation waterfall). All three are derivative (no WebSearch), run in parallel, and are added to the Notion export whitelist. Added after the dYdX (19.05.2026) post-mortem: the four standard decision layers don't answer the typical retail-token / family-office investor question "what does my decision look like as a [profile]?"

**Fast-mode DD short (~15 min, dd-short.md only):**
```
/dd-short <company>
/dd-short <company> --asking-price $500m --deal-type PE
/dd-short --from research/<existing-dd-dir>   # derive from existing master (3 min)
/dd-short <company> --no-redteam              # skip red team (12 min, no Bear Case section)
```
Lightweight standalone path that produces ONLY `dd-short.md`. Intelligent router:
- If `--from` points to a directory with `dd-decision-first.md` → derives via `dd-production-summary` (~3 min, full quality)
- Otherwise → runs parallel `dd-short-fast` (3 killer hypotheses + base case) + `dd-red-team-fast` (bear thesis + stress scenario + pre-mortem), then `dd-short-synthesizer` merges with reconciliation rules (~15 min)

Output retains Bear Case quote section (citation-ready bear thesis + stress scenario + compressed pre-mortem) so the file remains forward-worthy for sharing. Always carries a fast-mode disclosure flag and CTA to commission a full Strategic DD report — never poses as IC-grade. No internal commands or pipeline mechanics leak into client-facing files.

**Batch fast-mode DD (multiple companies in parallel):**
```
/dd-short-batch Apple, Microsoft, NVIDIA, AMD
/dd-short-batch                                 # then paste a list, one company per line
/dd-short-batch research/companies.txt          # read from file
/dd-short-batch <list> --batch-size 5 --deal-type secondary --language ru
```
Runs the dd-short fast pipeline for each company in parallel waves (default 10 companies per wave). Accepts plain names or pipe-extended rows: `Apple | $3.5T | secondary`. Produces per-company `dd-short.md` plus a sortable `batch-summary.md` table with verdicts, confidence, fair value, and gap vs asking. Resilient — one company's failure does not block the batch. Output goes to `research/batch-<date>/<slug>/`.

**Run BCG analysis first, then add DD:**
```
/bcg-team <company>
# → after Phase 3 completes, type "DD" or "DD M&A $500m"
```

**DD pipeline phases:**
- Phase DD-1 (parallel): `dd-market-validator` + `dd-hypothesis-tester`
- Phase DD-2 (parallel): `dd-risk-analyst` + `dd-red-team`
- Phase DD-3a (parallel): `dd-production-decision-first` + `dd-production` (legal layer)
- Phase DD-3b: `dd-production-summary` → derives `dd-mid.md` + `dd-short.md` from master
- Phase DD-3c (OPTIONAL, parallel — triggered by `--investor-profile`): `dd-bull-case-writer` + `dd-customer-discovery-synthesizer` + `dd-ma-scenarios-analyst` → `bull-case.md` + `customer-discovery.md` + `ma-exit-scenarios.md`
- Phase DD-4 (MANDATORY): Notion export of the 4 decision layers (or 7 if DD-3c ran) via `export_to_notion.py` whitelist

**DD output files (three-layer architecture — `dd-output-standard.md` Rule 1):**
```
dd-short.md            ← 10-second decision page (binary signal, ~50 lines)
dd-mid.md              ← 5-minute pre-meeting briefing (Top-5 issues with So what?)
dd-decision-first.md   ← Full investment report (45-60 min, IC-grade)  ← PRIMARY
dd-report.md           ← Institutional / legal reference (legacy format)

Optional investor-profile memos (only when --investor-profile is set):
bull-case.md             ← What has to be true to make money (4 conditions, conviction-graded allocation)
customer-discovery.md    ← DMU + churn + win-back per customer segment
ma-exit-scenarios.md     ← Strategic acquirers, valuation per M&A path, liquidation waterfall

Supporting analysis:
dd-market-validation.md  ← TAM/CAGR/moat validation (adversarial)
dd-hypothesis-report.md  ← 10 hypothesis test results (✅/⚠️/❌)
dd-risk-matrix.md        ← Full risk matrix (15+ risks, P×I scoring)
dd-red-team.md           ← Bear case + stress scenarios + pre-mortem
```

The three decision layers (`dd-short`, `dd-mid`, `dd-decision-first`) follow the 15-rule
**Decision-First Output Standard** (`.claude/skills/dd/references/dd-output-standard.md`):
verdict-first, "So what?" on every risk, dollar amounts before percentages, narrative
failure scenarios (not bullets), narrative pre-mortem, decision anchors after every
Critical/High risk, automatic PASS if 3+ hypotheses refuted.

The master (`dd-decision-first.md`) is the single source of truth — `dd-mid.md` and
`dd-short.md` derive from it; no figures appear in summary layers that don't trace back
to the master.

---

### MBB Strategic Analysis (FOUNDATION)

**Run a full MBB engagement:**
```
/bcg-team <company>
/bcg-team apple focus: financial
```

**Review methodology across past engagements:**
```
/bcg-methodology-review
/bcg-methodology-review segment-analyst
```

**Pre-call intelligence (before a sales call):**
```
/call-prep <company>
/call-prep "Acme Corp" — AI GTM platform
```
Researches the prospect company, builds a Value Pyramid, identifies Key Players (DMU), and generates a Contact Brief with talk track and MEDDPICC discovery questions.

**Analyze a sales call transcript:**
```
/analyze-call <company>
/analyze-call "Acme Corp" transcript.txt
```
Extracts MEDDPICC/BANT/3 Whys signals with quotes, generates Opportunity Summary, and produces `crm-update.json` for CRM write-back.

**Outreach — generate and send personalized messages:**
```
/send-outreach <engagement_dir>
/send-outreach acme-corp --dry-run
/send-outreach acme-corp --channel email --tier 1
/send-outreach acme-corp --goal sell-report   # sell a MBB research report
```
Runs `bcg-message-writer` to generate personalized emails per Tier 1 contact, shows drafts for approval, then sends via Resend.

Two goals: `gtm-outreach` (default — outreach on behalf of the client) and `sell-report` (sell a MBB-team analytical report to investors/analysts/corporates).

**Send follow-up emails (after initial wave):**
```bash
# Follow-up #1 — day 3
python3 .claude/skills/send-outreach/send_outreach.py \
  --data research/<dir>/outreach-drafts.json --approve all --follow-up 1

# Follow-up #2 — day 7 (breakup email)
python3 .claude/skills/send-outreach/send_outreach.py \
  --data research/<dir>/outreach-drafts.json --approve all --follow-up 2
```
Each contact in `outreach-drafts.json` has three messages: `body` (initial), `follow_up_1` (day 3), `follow_up_2` (day 7). The script tracks sent status per wave and skips already-sent contacts.

**CRM sync (pull/push):**
```
/crm-sync <engagement> --direction pull
/crm-sync <engagement> --direction push
```
Pulls contacts/accounts/opportunities from any CRM via Merge.dev into `crm-data/`. Push writes MEDDPICC fields from `crm-update.json` back to CRM. Supports HubSpot, Salesforce, Pipedrive, and 50+ other CRMs via one unified API.

**Export research to Notion:**
```
/notion-export <research_dir_name>
# e.g.: /notion-export tsmc-30.03.2026
```

For `/dd` engagements this happens automatically as Phase DD-4 — `/notion-export`
is only needed for BCG-only runs, or to manually retry a failed DD export.

**Process client feedback from Notion:**
```
/notion-process <research_dir_name>
# e.g.: /notion-process tsmc-02.04.2026
```
Reads unchecked items from the "📋 Feedback" Notion page, applies changes to local research files, syncs back to Notion, and marks each item done with a response.

**Process all client feedback at once:**
```
/notion-process-all
```
Scans every research directory for pending feedback and processes them sequentially.

**Export script (direct):**
```bash
NOTION_TOKEN=<token> NOTION_PARENT_PAGE_ID=<page_id> \
  python3 .claude/skills/notion-export/export_to_notion.py research/<dir>

# Restrict export to a subset of files (used by /dd Phase DD-4):
NOTION_TOKEN=<token> NOTION_PARENT_PAGE_ID=<page_id> \
NOTION_FILES_WHITELIST="dd-short.md,dd-mid.md,dd-decision-first.md,dd-report.md" \
  python3 .claude/skills/notion-export/export_to_notion.py research/<dir>
```

**Generate PDFs** (triggered interactively after Phase 3, or manually via bcg-pdf-designer agent using Chrome headless).

## Architecture

### DD Pipeline (PRIMARY)

`/dd` runs BCG foundation first, then DD-specific phases. The BCG foundation is the **DD-blitz projection of Pipeline v9.1.0** (canonical spec: [methodology/pipeline91.json](methodology/pipeline91.json), sha256 `204dfd45…`; cumulative on v9.0 `pipeline9.json` sha256 `68569d44…`) — same 68-stage architecture, time-compressed to ~45–70 min wall-clock by collapsing modules into the parallel blocks below. v9.1 quality patches (P1-P6) are inherited by the blitz via the runtime agents (`bcg-segment-analyst`, `bcg-market-mapper`, `bcg-fact-checker`, `bcg-portfolio-analyst`, `bcg-production`). Output file names are v9 legacy mirrors so DD agents read them unchanged. For full-fidelity v9 (all 68 stages, all 13 gates, all per-strategy isolation, ~2.5h wall-clock) run `/bcg-team <company>` first, then `/dd <company> --dir <output>`.

```
BCG Foundation (DD-blitz projection of v9 Modules 0-7):
  Phase -1   bcg-researcher          → company-brief.md           (v9 Onboarding O0/O1/F2/BP1 + Enrichment 00/00c/01/01b)
  Phase 0    bcg-market-mapper        → market-map.md          }  (v9 Segmentation 1S0-1S4 + G_PUREPLAYER)
             bcg-data-scientist       → advanced-analytics.md  }  (v9 Delivery 6D financial exhibits)
  Phase 1    bcg-segment-analyst ×N   → segment-[slug].md      }  (v9 Context 1B/1C/1D/1Y/1_BU_PORTFOLIO_VIEW/1_DESC_LOCK
             bcg-domain-expert        → domain-expert-input.md }   + Advantage 2_routing/2A/2B/2C/2_ADV_LOCK
                                                                   + Future 3A/3B/3C/3_FUT_LOCK
                                                                   + Onboarding 0d, auto-invoke if B2B-vertical — v9 BUG #4)
  Phase 1.5  bcg-fact-checker         → validation-report.md       (v9 V1+V2+V3 rolled into 1V_validation_report)
  Phase 2    bcg-portfolio-analyst    → portfolio.md               (v9 Options 4_GENERATE — incl. ENTRY anti-pattern flag (BUG #3)
                                                                    + Selection 5A/5B/5C/Beliefs/Champion/5_SELECT_final + G6/G7)

DD Phases:
  Phase DD-1   dd-market-validator         → dd-market-validation.md  } parallel
               dd-hypothesis-tester        → dd-hypothesis-report.md  }
  Phase DD-2   dd-risk-analyst             → dd-risk-matrix.md        } parallel
               dd-red-team                 → dd-red-team.md           }
  Phase DD-3a  dd-production-decision-first → dd-decision-first.md    } parallel
               dd-production               → dd-report.md  (legal)    }
  Phase DD-3b  dd-production-summary       → dd-mid.md + dd-short.md
                                            (derived from dd-decision-first.md)
  Phase DD-3c  dd-bull-case-writer              → bull-case.md            } parallel,
  (optional)   dd-customer-discovery-synth.     → customer-discovery.md   } only if
               dd-ma-scenarios-analyst          → ma-exit-scenarios.md    } --investor-profile
                                                 (Sonnet, no WebSearch, 3-5 min)
  Phase DD-4   notion-export (whitelist)   → 4 Notion pages + 📋 Feedback page
                                            (or 7 pages if DD-3c ran; MANDATORY —
                                             exports only the decision layers, not
                                             supporting analyses)
```

**dd-decision-first.md is the PRIMARY OUTPUT** — IC-grade, 45-60 min read.
`dd-mid.md` (5-min briefing) and `dd-short.md` (10-sec decision) derive from it.

**Notion export is mandatory but non-blocking:** if `NOTION_TOKEN` /
`NOTION_MBB_ROOT_PAGE_ID` are missing in `.env`, Phase DD-4 is skipped with a
clear message; the engagement still completes with all 12 files saved locally.
The export script (`export_to_notion.py`) accepts a `NOTION_FILES_WHITELIST`
env var (CSV of filenames) — DD pipeline passes
`dd-short.md,dd-mid.md,dd-decision-first.md,dd-report.md` to limit export to
just the four decision layers.

**Shortcut:** If BCG analysis already exists, use `--dir` to skip BCG phases and jump directly to DD.

---

### DD Short Fast-Mode Pipeline (`/dd-short`)

Lightweight standalone path that produces ONLY `dd-short.md` in ~15 min. Router picks one of two paths:

**Path A — Derivation Mode (~3 min)** — used when `--from` points to an existing engagement with `dd-decision-first.md`:
```
Phase A-1   dd-production-summary    → dd-short.md + dd-mid.md
                                       (derived from existing master, no new analysis)
```

**Path B — Standalone Fast-Mode (~15 min)** — used when no full DD exists:
```
Phase F-1   dd-short-fast            → dd-short-base.md      } parallel    } intermediate
            dd-red-team-fast         → dd-red-team-fast.md   }              } drafts (auto-deleted)
Phase F-2   dd-short-synthesizer     → dd-short.md          (merges + reconciliation R1-R5)
Phase F-3   cleanup                  → removes intermediate drafts iff dd-short.md is non-empty
                                       (drafts preserved on synthesis failure for debugging)
```

User-visible output is a single file: `dd-short.md`. Intermediate drafts (`dd-short-base.md`, `dd-red-team-fast.md`) exist only during the run and are removed after successful synthesis — they survive only if the synthesizer failed (so the user can inspect or re-run).

**Reconciliation rules (R1-R5)** in `dd-short-synthesizer`:
- R1: 3+ refuted hypotheses → automatic PASS (Rule 14)
- R2: Red Team gap >40% below asking → downgrade verdict by one tier
- R3: Base case PROCEED + Red Team PASS → confidence -15pp + downgrade tier
- R4: No material adversarial findings → keep base case
- R5: Worst case = max(base worst case, red team scenario downside)

**Output disclosure:** `dd-short.md` in fast-mode carries a header flag (`⚡ Strategic snapshot`) and a closing CTA recommending the full Strategic DD report (commercial language only — no internal command leak). Bear Case section (≤3-sentence bear thesis + 1-2 scenario summary + compressed pre-mortem) is included unless `--no-redteam` is passed — this is what makes the output forward-worthy for sharing.

**Output directory:** `research/<company>-<date>-fast/` (the `-fast` suffix distinguishes fast-mode engagements from full DD).

---

### DD Short Batch Pipeline (`/dd-short-batch`)

Wraps `dd-short` fast-mode for multiple companies with bounded parallelism. Does NOT call `/dd-short` recursively (skill-from-skill is sequential — would lose parallelism). Instead, invokes the three fast-mode agents directly per company in wave structure:

```
Per wave (max BATCH_SIZE companies, default 10):
  Phase F-1   dd-short-fast × N      } parallel — 2N agents per wave (peak concurrency)
              dd-red-team-fast × N   }
  Phase F-2   dd-short-synthesizer × N (skipped for any company that failed F-1)
  Phase F-3   cleanup drafts iff dd-short.md is non-empty
  Phase F-4   capture verdict for batch summary

Waves run sequentially (wave W+1 waits for wave W cleanup).

After all waves:
  Step 5      compile batch-summary.md (sortable table, sorted by verdict severity)
  Step 6      optional Notion export (batch summary + per-company reports)
```

Output structure:
```
research/batch-<date-time>/
  ├── batch-summary.md          ← client-facing sortable verdict table
  ├── batch-engagement.log      ← internal log (per-wave timing, failures)
  ├── <slug-1>/dd-short.md      ← per-company final report
  ├── <slug-2>/dd-short.md
  └── ...
```

**Parallelism cap:** Default batch size = 10 companies/wave → 20 simultaneous agent calls in Phase F-1 peak. Override with `--batch-size 5` for stricter cap (= 10 simultaneous calls).

**Resilience:** Failed companies are flagged in batch-summary.md (`❌ FAILED` row) but never abort the batch. Failed companies keep their intermediate drafts on disk for manual debugging or re-run.

**Input formats:** Plain text (one company per line OR comma-separated), pipe-extended rows (`Apple | $3.5T | secondary`), or file path. Deduplication by slug. Validation of asking-price and deal-type with logged warnings.

**Client-safe output:** `batch-summary.md` follows the same disclosure rules as `dd-short.md` — no internal commands, no agent names, no pipeline mechanics leak.

---

### BCG-Only Engagement Pipeline (Pipeline v9.1.0)

**Canonical spec:** [methodology/pipeline91.json](methodology/pipeline91.json) (sha256 `204dfd45…`,
cumulative on v9.0 `pipeline9.json` sha256 `68569d44…`), PRDs at
[methodology/PRD-pipeline-v9_1.md](methodology/PRD-pipeline-v9_1.md) and
[methodology/PRD-pipeline-v9.md](methodology/PRD-pipeline-v9.md). Mirrored inside the skill at
[.claude/skills/bcg-team/references/pipeline91.json](.claude/skills/bcg-team/references/pipeline91.json)
for runtime reads. The `bcg-team` skill ([.claude/skills/bcg-team/SKILL.md](.claude/skills/bcg-team/SKILL.md))
orchestrates v9.1's **68 stages across 9 modules with 13 quality gates**; stage prompts are read
verbatim from `pipeline91.json` so V0–V5 validator audits remain meaningful.

**v9.1 quality patches over v9.0 (cumulative, additive — no structural changes):**
- **P1** Innovate Archetype Mandatory Gate per segment in `4_GENERATE` (≥1 I OR explicit `NOT_VIABLE`)
- **P2** Question Mark 8-strategy floor + structural template (2D/2S/1P/1F/1I/1exit) in `4_GENERATE`
- **P3** Self-derived TAM `⚠️ NO INDEPENDENT SOURCE` warning at TOP of TAM block (`1S0_segmenter`, `1B_industry_economics`, `6F_market_map_data`)
- **P4** TAM-ceiling resolution protocol BLOCKING in `4_STRATEGY_FINANCIAL` (resolve via (a) revise share, (b) expand TAM with named source, or (c) explicit `target_not_independently_constrained` label)
- **P5** Part-V GTM scope gate on `6E_implementation_roadmap` + V5 6E↔6B trigram-Jaccard overlap detector
- **P6** Validation-override propagation checklist (`1V_validation_report.corrections_required[]` → `5_SELECT_final.corrections_applied[]` → `6A_decision_memo.corrections_applied[]`, V5 BLOCKS at G7 on parity failure)

Each `/bcg-team` run creates `research/<company>-<date>/` and walks the v9 modules:

```
Module 0   Onboarding (12 stages)        — O0/W0/O3.5/W1/O4/intake_routing/O1/O2/O3/F2/BP1/0d
                                           Gates: G_LITE · G_OAUTH · G_BP_PROBE · G_COVERAGE · G1_burning_problem
                                           Outputs incl. f2-client-context-brief.md (mirror → company-brief.md)
                                           v9 BUG #4: 0d auto-invoke for B2B-vertical industries
Module 1   Enrichment (4 stages)         — 00 / 00c / 01 / 01b           Gates: G0 · G1 · G2
                                           v9 BUG #1: 00c emits legal_bu_count AND strategic_bu_count
Module 2   Segmentation (5 stages)       — 1S0 / 1S1 / 1S2 / 1S3 / 1S4   Gate: G_PUREPLAYER
                                           v9 BUG #2: 1S1 4th verdict VALID_AS_CROSS_SEGMENT_PLAY
                                           1S4 lock → market-map.md
Module 3   Context per-BU (8 stages)     — 1B / 1C / 1D / 1Y / 1_BU_PORTFOLIO_VIEW / 1_DESC_LOCK / V1 / 1V
                                           Parallel with Module 2 · Gates: G3 · G3x
                                           1_DESC_LOCK → segment-<slug>.md (per BU)
                                           1V_validation_report → validation-report.md
Module 4   Advantage (7 stages)          — 2_routing / 2A / 2B / 2C / 2_source_driver_matrix / 2_ADV_LOCK / V2
                                           Gate: G4
Module 5   Future (5 stages)             — 3A / 3B / 3C / 3_FUT_LOCK / V3   Gate: G5
Module 6   Options (6 stages)            — 4_GENERATE + per-strategy ISOLATED orchestrators
                                           (4_STRATEGY_FINANCIAL / VIABILITY / COMPETITOR / SANITY_SYNTHESIS) + V4
                                           Gate: G6 · v9 BUG #3: ENTRY-cell anti-pattern auto-flag blocks elaboration
Module 7   Selection (9 stages)          — 5A / 5B / 5B_real_options / 5C / 5C_game_theory / 5_BELIEFS_AUDIT
                                           / 5_champion_test / 5_SELECT_final / V5
                                           Gate: G7 · v9 BUG #5: V5 inline contradiction check on 6A + 6B
                                           5_SELECT_final → portfolio.md
Module 8   Delivery (12 stages, parallel post-G7)
                                           6A_decision_memo / 6B_strategy_narrative / 6C_slide_structure
                                           / 6D_financial_exhibits / 6E_implementation_roadmap / 6F_market_map_data
                                           / 6G_risk_exhibit / 6H_appendix / 6I_strategy_card / 6J_hoshin_xmatrix
                                           / 6K_okr_cascade / 6L_change_adkar_cadence
                                           6A+6B+6C merged → final-report.md · 6E → gtm-playbook.md
                                           6D → advanced-analytics.md
Phase Post  bcg-methodologist (background) → methodology-review.md
```

**Agent topology (L0–L4):**
- L0 `senior-partner` (Partner orchestration in SKILL.md): G0 · G6 · G7
- L1 `project-manager` (Partner orchestration in SKILL.md): G1–G5 · G3x
- L2 orchestrators map to existing agents: `enrichment-orchestrator → bcg-researcher` ·
  `segmentation-orchestrator → bcg-market-mapper` · `context/advantage/future/options-orchestrator → bcg-segment-analyst` ·
  `selection-orchestrator → bcg-portfolio-analyst` · `delivery-orchestrator → bcg-production (+ bcg-gtm-analyst, bcg-data-scientist)` ·
  `validator-lead → bcg-fact-checker` · `domain-expert → bcg-domain-expert`
- L4 strategy-orchestrators run ISOLATED in `engagement/<id>/orchestrators/strat_<id>/` with own state/memory/checkpoint/validator

**Model tiering (pipeline9.json):** Opus for strategy synthesis / advantage diagnosis / pattern routing / sequencing / final selection · Sonnet for research / parallel analyses / QA / future scenarios / validator audits · Haiku for brief parsing / BU detection / classification / slide structure / exhibit data.

**DD compatibility:** v9 writes both v9-native artifacts and legacy-named mirrors (`company-brief.md`, `market-map.md`, `segment-*.md`, `validation-report.md`, `portfolio.md`, `gtm-playbook.md`, `final-report.md`, `advanced-analytics.md`, `domain-expert-input.md`) so `/dd` consumes v9 output without modification. See the v9→DD mapping table in [.claude/skills/dd/SKILL.md](.claude/skills/dd/SKILL.md#bcg-foundation-phases).

`f2-client-context-brief.md` (mirrored as `company-brief.md`) is the single source of truth — all downstream stages must read it before quoting numbers.

**Phase 3.5 (optional, post-G7):** bcg-contact-scout (target accounts) · bcg-creative-strategist (LinkedIn ads, outreach, pitch, one-pagers) · bcg-audience-scout (sell-report mode). Runs in parallel after Module 8 — independent of the v9 spec.

**Reproducibility:** before any stage fires, SKILL.md verifies `methodology/pipeline91.json` SHA256 matches `methodology/pipeline91.json.sha256`. Mismatch aborts the engagement. The v9.1 build is itself zero-diff reproducible via `python3 scripts/build_pipeline_v9_1.py` (cumulative on `scripts/build_pipeline_v9.py` once that builder ships).

### Sales Intelligence Pipeline (standalone)

Independent of `/bcg-team`, runs on-demand for any prospect:

```
/call-prep <company>
  → bcg-account-intel         → account-brief.md
                                 (Value Pyramid + Contact Brief + Key Players + Talk Track)

/analyze-call <company> [transcript]
  → bcg-call-analyzer         → call-analysis.md + crm-update.json
                                 (MEDDPICC + BANT + 3 Whys + Opportunity Summary)

/send-outreach <engagement> [--goal gtm-outreach|sell-report]
  → bcg-message-writer        → outreach-drafts.md + outreach-drafts.json
  → send_outreach.py          → outreach-log.json
                                 (Personalized email per contact → Resend)
                                 (Each contact: initial + follow_up_1 + follow_up_2)
  → send_outreach.py --follow-up 1|2   → follow-up wave (day 3 / day 7)

/crm-sync <engagement>
  → fetch_crm.py / write_crm.py → crm-data/*.json / CRM update
                                 (HubSpot, Salesforce, Pipedrive, 50+ CRMs via Merge.dev)
```

**Sell-report outreach** (find buyers for a MBB-team report):
```
bcg-audience-scout  → contact-universe.md
                       (investors, analysts, corporates, consultants, press)
/send-outreach <engagement> --goal sell-report
  → bcg-message-writer (sell-report mode) → outreach-drafts.json
  → send_outreach.py                      → outreach-log.json
```

### Key Files

**DD Agents:**
- `.claude/agents/dd-market-validator.md` — adversarial market claims validation (TAM, CAGR, VRIO)
- `.claude/agents/dd-hypothesis-tester.md` — tests 10 DD hypotheses (✅/⚠️/❌)
- `.claude/agents/dd-risk-analyst.md` — risk matrix (15+ risks, P×I, deal breakers)
- `.claude/agents/dd-red-team.md` — bear case, short thesis, stress scenarios, pre-mortem
- `.claude/agents/dd-production-decision-first.md` — master decision-first report (applies all 15 rules) → `dd-decision-first.md`
- `.claude/agents/dd-production-summary.md` — derives `dd-mid.md` + `dd-short.md` from master, strict no-new-numbers rule
- `.claude/agents/dd-production.md` — institutional/legal layer (legacy format) → `dd-report.md`

**DD Investor-Profile Agents (`Phase DD-3c`, triggered by `--investor-profile`):**
- `.claude/agents/dd-bull-case-writer.md` — 4-condition bull thesis, conviction-graded allocation table, monitoring tripwires → `bull-case.md`
- `.claude/agents/dd-customer-discovery-synthesizer.md` — customer segmentation + DMU per segment + churn analysis + win-back opportunities → `customer-discovery.md`
- `.claude/agents/dd-ma-scenarios-analyst.md` — strategic acquirers + valuation per M&A path + liquidation waterfall + probability-weighted exit value → `ma-exit-scenarios.md`

**DD Fast-Mode Agents (`/dd-short` standalone path):**
- `.claude/agents/dd-short-fast.md` — light research + 3 killer hypotheses (concentration, unit economics, moat) → `dd-short-base.md`
- `.claude/agents/dd-red-team-fast.md` — bear thesis + 1-2 stress scenarios + pre-mortem, runs in parallel without anchoring on base case → `dd-red-team-fast.md`
- `.claude/agents/dd-short-synthesizer.md` — merges base + red team into final `dd-short.md`, applies verdict reconciliation rules R1-R5, strict no-new-numbers

**DD Skills:**
- `.claude/skills/dd/SKILL.md` — full DD pipeline orchestrator (BCG foundation + DD phases, 60-90 min)
- `.claude/skills/dd-short/SKILL.md` — fast-mode orchestrator (~15 min standalone OR ~3 min derivation from existing master)
- `.claude/skills/dd-short-batch/SKILL.md` — batch fast-mode orchestrator for multiple companies (parallel waves, default 10 companies/wave, resilient to per-company failures)
- `.claude/skills/dd/references/dd-output-standard.md` — 15-rule decision-first standard (MANDATORY read for all production agents AND fast-mode agents)
- `.claude/skills/dd/references/templates/` — structural reference templates for the three decision layers

**BCG Agents & Pipeline v9.1.0:**
- `methodology/pipeline91.json` — **canonical strategy spec v9.1** (68 stages, 9 modules, 13 gates; sha256 `204dfd45…`)
- `methodology/PRD-pipeline-v9_1.md` — v9.1 release PRD + 6 quality patches (P1-P6)
- `methodology/pipeline91.json.sha256` — integrity hash (verified before every `/bcg-team` run)
- `methodology/pipeline9.json` — v9.0 base spec (sha256 `68569d44…`; cumulative base)
- `methodology/PRD-pipeline-v9.md` — v9.0 release PRD + 5 bug fixes from the Microsoft synthetic case
- `methodology/pipeline-v9-proposed-updates.md` — post-integration audit (proposed v9.1/9.2/v10 patch tiers)
- `scripts/build_pipeline_v9_1.py` — reproducible v9.1 patcher (cumulative on v9.0); zero-diff verified
- `.claude/skills/bcg-team/references/pipeline91.json` + `PRD-pipeline-v9_1.md` — runtime mirrors
- `.claude/skills/bcg-team/references/pipeline9.json` + `PRD-pipeline-v9.md` — v9.0 mirrors (cumulative base)
- `.claude/agents/` — all sub-agent definitions (one `.md` per agent); each maps to an L2 orchestrator role in v9 (see Architecture → BCG-Only Engagement Pipeline)
- `.claude/skills/bcg-team/SKILL.md` — Senior-Partner orchestration of v9.1's 68 stages; verifies pipeline91.json checksum on launch; reads stage prompts verbatim from pipeline91.json
- `.claude/skills/bcg-methodology-review/SKILL.md` — cross-engagement quality improvement
- `.claude/skills/notion-export/` — Notion export (SKILL.md + export_to_notion.py)
- `.claude/skills/call-prep/SKILL.md` — pre-call intelligence skill
- `.claude/skills/analyze-call/SKILL.md` — call transcript analysis skill
- `.claude/skills/send-outreach/` — outreach generation + sending (SKILL.md + send_outreach.py)
- `.claude/skills/crm-sync/` — CRM pull/push (SKILL.md + fetch_crm.py + write_crm.py)
- `.claude/skills/bcg-team/references/bcg-framework-5-lenses.md` — MBB 5-lens framework reference (always read at engagement start)
- `methodology/improvement-log.md` — accumulates cross-engagement patterns and applied changes
- `methodology/agent-improvements/` — per-agent improvement proposals
- `research/<company>-<date>/` — all engagement output (gitignored)

### MBB Analytical Framework

**5 lenses (sequential):** Description → Advantage → Future → Options → Selection

**Segmentation principle:** A segment is valid only if a competitor could exist profitably in it without adjacent segments.

**Quality gates per engagement:**
- 10 testable hypotheses (H-D1..H-S1), all explicitly confirmed or rejected
- 10+ competitors per segment with financial data
- 10–15 strategies per segment across archetypes: Defend, Pivot, Scale, Focus, Innovate, Innovation
- Every number cited with source + year + confidence tag: ✅ VERIFIED / ⚠️ ESTIMATED / ❌ NOT FOUND
- Data quality scores: A (>90% verified) / B (70–90%) / C (50–70%) / F (<50%)
- `validation-report.md` overrides segment data on conflicts

**Pyramid Principle:** All outputs lead with the conclusion, then arguments, then data.

## Publishing & Export — Xataco-Output Toolkit

This project produces research (`research/<engagement>/`) but does **NOT** own publishing. All Notion / Vercel / PDF exports go through the standalone **Xataco-Output toolkit** at `/Users/cofounder/Documents/Projects/output/` — three tools, one canonical source of truth for brand + Notion token + Vercel project.

| Tool | Script | Purpose |
|---|---|---|
| **Vercel publish** | `output/publish_reports.py` | Static HTML hub at `xata-reports.vercel.app`; each engagement = `/<slug>/` with sidebar nav + `all.html` (agent-readable single-fetch). Pure stdlib, no pip deps. |
| **PDF** | `output/pdf-report/render_report.py` | Bridgewater-style A4 in Xata&co brand. Modes: `generic` / `dd` (verdict badge) / `bcg` (MBB matrix). |
| **Notion** | `output/notion-export/export_to_notion.py` | Parent page per engagement + child page per `.md`. `NOTION_FILES_WHITELIST` env to subset. |

**Standard invocations:**

```bash
# Vercel publish (whole engagement folder → hub)
python3 /Users/cofounder/Documents/Projects/output/publish_reports.py \
  research/<eng>/ --title "<Engagement title>"

# PDF (single file → next to source)
python3 /Users/cofounder/Documents/Projects/output/pdf-report/render_report.py \
  research/<eng>/dd-decision-first.md --mode dd --company "<Name>"

# Notion (whitelisted subset of folder)
set -a; source /Users/cofounder/Documents/Projects/output/.env; set +a
NOTION_FILES_WHITELIST="dd-short.md,dd-mid.md,dd-decision-first.md,dd-report.md" \
  python3 /Users/cofounder/Documents/Projects/output/notion-export/export_to_notion.py \
  research/<eng>/
```

**Do NOT use** the local copies under `.claude/skills/notion-export/` and `.claude/skills/pdf-report/` — those are stale forks. Phase DD-4 of the `/dd` skill still invokes the local Notion copy; this is a known wiring drift and will be retargeted to the Xataco-Output toolkit on the next /dd update.

**Why two locations:** The output/ toolkit has its own `.env` (with the working `NOTION_TOKEN` for the shared root page), its own Vercel project auth (`xata-reports`), and bundles Xata&co brand CSS. Centralizing exports there keeps DD MarketStrat focused on the research pipeline without coupling to deployment infrastructure.

## Environment Setup

Copy `.env.example` → `.env` and fill in:

```
# Notion
NOTION_TOKEN=<your Notion integration token>
NOTION_MBB_ROOT_PAGE_ID=<root page ID in Notion>

# CRM Integration (/crm-sync) — Merge.dev (HubSpot, Salesforce, Pipedrive, 50+ CRMs)
MERGE_API_KEY=

# Outreach (/send-outreach)
RESEND_API_KEY=             # resend.com, 3000 emails/month free
FROM_EMAIL=
FROM_NAME=
```

The `.env` file is gitignored. Skills read it via `source .env`.

## Methodology Improvement Loop

After each engagement, `bcg-methodologist` auto-updates `methodology/improvement-log.md`. Running `/bcg-methodology-review` triggers a cross-engagement analysis that:
- Auto-applies P1 fixes (issue in >60% of engagements, HIGH impact) directly to agent `.md` files
- Proposes P2 fixes (>40% of engagements) for manual review
- Never auto-applies changes to the core MBB framework (5 lenses, segmentation principle, Pyramid Principle)
