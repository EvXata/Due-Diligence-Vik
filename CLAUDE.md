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
```
Delivers: **three-layer decision output** (10-sec → 5-min → 45-min) + Value Bridge + Risk Matrix + institutional reference.

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
- Phase DD-4 (MANDATORY): Notion export of the 4 decision layers via `export_to_notion.py` whitelist

**DD output files (three-layer architecture — `dd-output-standard.md` Rule 1):**
```
dd-short.md            ← 10-second decision page (binary signal, ~50 lines)
dd-mid.md              ← 5-minute pre-meeting briefing (Top-5 issues with So what?)
dd-decision-first.md   ← Full investment report (45-60 min, IC-grade)  ← PRIMARY
dd-report.md           ← Institutional / legal reference (legacy format)

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
```

**Generate PDFs** (triggered interactively after Phase 3, or manually via bcg-pdf-designer agent using Chrome headless).

## Architecture

### DD Pipeline (PRIMARY)

`/dd` runs BCG foundation first, then DD-specific phases:

```
BCG Foundation (Phases -1 → 3):
  Phase -1   bcg-researcher          → company-brief.md
  Phase 0    bcg-market-mapper        → market-map.md          } parallel
             bcg-data-scientist       → advanced-analytics.md  }
  Phase 1    bcg-segment-analyst ×N   → segment-[slug].md      } parallel
             bcg-domain-expert        → domain-expert-input.md }
  Phase 1.5  bcg-fact-checker         → validation-report.md
  Phase 2    bcg-portfolio-analyst    → portfolio.md

DD Phases:
  Phase DD-1   dd-market-validator         → dd-market-validation.md  } parallel
               dd-hypothesis-tester        → dd-hypothesis-report.md  }
  Phase DD-2   dd-risk-analyst             → dd-risk-matrix.md        } parallel
               dd-red-team                 → dd-red-team.md           }
  Phase DD-3a  dd-production-decision-first → dd-decision-first.md    } parallel
               dd-production               → dd-report.md  (legal)    }
  Phase DD-3b  dd-production-summary       → dd-mid.md + dd-short.md
                                            (derived from dd-decision-first.md)
  Phase DD-4   notion-export (whitelist)   → 4 Notion pages + 📋 Feedback page
                                            (MANDATORY — exports only the 4 decision layers,
                                             not supporting analyses)
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

### BCG-Only Engagement Pipeline

Each `/bcg-team` run creates `research/<company>-<date>/` and executes agents sequentially, with parallelism inside phases:

```
Phase -1   bcg-researcher          → company-brief.md
Phase 0    bcg-market-mapper        → market-map.md          } parallel
           bcg-data-scientist       → advanced-analytics.md  }
Phase 1    bcg-segment-analyst ×N   → segment-[slug].md      } parallel
           bcg-domain-expert        → domain-expert-input.md }
Phase 1.5  bcg-fact-checker         → validation-report.md
Phase 2    bcg-portfolio-analyst    → portfolio.md
Phase 2.5  bcg-gtm-analyst          → gtm-playbook.md
Phase 3    bcg-production           → final-report.md
Phase 3.5  bcg-contact-scout        → contact-universe.md    } optional, parallel
           bcg-creative-strategist  → creative-brief.md      }
           bcg-audience-scout       → contact-universe.md    } optional (sell-report mode only)
Phase Post bcg-methodologist        → methodology-review.md  (background)
```

`company-brief.md` is the single source of truth — all agents must read it first before using any numbers.

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
- `.claude/skills/dd/SKILL.md` — DD orchestrator (full pipeline)
- `.claude/skills/dd/references/dd-output-standard.md` — 15-rule decision-first standard (MANDATORY read for production agents)
- `.claude/skills/dd/references/templates/` — structural reference templates for the three decision layers

**BCG Agents:**
- `.claude/agents/` — all sub-agent definitions (one `.md` per agent)
- `.claude/skills/bcg-team/SKILL.md` — BCG Partner orchestration (also triggers DD after Phase 3)
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
