# Strategic Due Diligence & MBB Consulting — AI System

A multi-agent AI system that delivers two integrated products:

1. **Strategic Due Diligence** — investment-grade DD report for PE/VC/M&A/secondary deals in 48 hours
2. **MBB Strategic Analysis** — full BCG-style consulting engagement (business unit strategy, portfolio, GTM)

The DD pipeline runs on top of the BCG strategic foundation — BCG phases provide the analytical base, DD phases adversarially challenge it and deliver an Investment Verdict through a **three-layer decision-first output**.

---

## Quick Start

```bash
# Full DD (BCG foundation + DD analysis) — minimum viable command
/dd Apple

# With deal context (recommended)
/dd Apple --deal-type PE --asking-price $3.5tn

# Run BCG first, then continue to DD interactively
/bcg-team Apple
# → after Phase 3 completes, type: "DD PE $3.5tn"

# DD on existing BCG output (saves time — skips BCG phases)
/dd Apple --dir research/apple-14.04.2026

# BCG only (no DD)
/bcg-team Apple
```

---

## Strategic Due Diligence

### GTM Discovery / Product Tournament Vector

Real DD engagements are converted into a tournament-ready product vector in
`gtm-discovery/`. The vector includes only deals where `bear_case`, `bull_case`,
`deep_audit`, or `fast_short` was ordered/produced, and maps each deal to a
buyer job, product SKU, GTM segment, and tournament score.

```bash
python3 scripts/build_dd_gtm_vector.py
```

Core files:
- `gtm-discovery/dd-deal-vector.csv` — curated source of truth for GTM tournament import
- `gtm-discovery/tournament-methodology.md` — scoring rubric and product taxonomy
- `gtm-discovery/gtm-discovery-playbook.md` — outbound hooks and product ladder

### What You Get — Three-Layer Decision Output

Every DD engagement produces **four deliverables**, ordered by reading time:

| File | Reading time | Purpose |
|------|-------------|---------|
| `dd-short.md` | **10 seconds** | Binary signal — first-screen verdict, fair-value gap, 3 deal-breakers |
| `dd-mid.md` | **5 minutes** | Pre-meeting briefing — Top-5 issues with "So what?" blocks, hypothesis scorecard, value bridge |
| `dd-decision-first.md` | **45–60 min** | Full IC-grade investment report — failure narratives, pre-mortem, self-identification table, exit triggers ← **PRIMARY** |
| `dd-report.md` | reference | Institutional / legal layer (legacy Pyramid Principle format) |

Plus four supporting analyses: `dd-market-validation.md`, `dd-hypothesis-report.md`, `dd-risk-matrix.md`, `dd-red-team.md`.

Each decision layer is **independently useful** — a reader who only sees `dd-short.md` has enough to act.

### The Decision-First Standard

The three decision layers follow a 15-rule standard (`.claude/skills/dd/references/dd-output-standard.md`):

- **Verdict-first.** Bottom line in the first 6 lines. Three-price threshold ladder (PASS @ $X / CONDITIONAL @ $Y / PROCEED @ $Z).
- **"So what?" on every risk.** Data → mechanism → quantified consequence → verdict anchor. No bare facts like "concentration is 61%".
- **Dollars before percentages.** `-$1.3T in base case (-31%)`, not `-31%`.
- **Narrative failure scenarios.** Three minimum, with timestamps, named actors, cascade steps, and warning signs the market is misframing today.
- **Narrative pre-mortem.** Future-dated first-person: "It is March 2028. The deal failed. Here is what happened."
- **Automatic PASS** if 3+ hypotheses refuted, no exceptions.
- **Decision anchors** (`→ This alone justifies a PASS`) after every Critical/High risk.

### What's in `dd-decision-first.md` (the master)

- **Section 1 — Verdict:** threshold ladder, confidence with interpretation, deal score, self-identification table, recommended actions per reader position
- **Section 2 — Three ways this fails:** ≥3 narrative failure scenarios with cascade and warning signs
- **Section 3 — The business (verified):** what the bull narrative gets wrong, with named figures
- **Section 4 — Hypothesis scorecard:** 10 hypotheses, critical refutations explained
- **Section 5 — Risk matrix:** 20 risks across 8 categories with risk-cluster summary
- **Section 6 — Value bridge:** named adjustments + bull/base/bear scenarios + probability-weighted expected return
- **Section 7 — Exit triggers & position rules:** pre-commitment table
- **Section 8 — Hedge structures** (public equity) **or Pre-close protections** (M&A/PE/VC)
- **Section 9 — Pre-mortem:** first-person narrative
- **Section 10 — What to watch:** leading indicators that fire before financials
- **Section 11 — Data quality appendix**

### Why It's Valuable for Funds

| What the report surfaces | Concrete value |
|--------------------------|---------------|
| Deal-breakers before capital is committed | Avoid a bad $50–500M deal |
| Growth story validation (often overstated) | Negotiation leverage: 5–20% price adjustment |
| Hidden risks (tech debt, customer concentration, regulatory) | Prevent value destruction post-close |
| Quantified bear case with stress scenarios | IC-ready stress test |
| 10-sec / 5-min / 45-min layered output | Each stakeholder reads at their level |

Price: **$500 / 48h** (vs. $250K from MBB firms)

### DD Pipeline

```
BCG Foundation:
  Phase -1   bcg-researcher          → company-brief.md
  Phase 0    bcg-market-mapper        → market-map.md          ⟳ parallel
             bcg-data-scientist       → advanced-analytics.md
  Phase 1    bcg-segment-analyst ×N   → segment-[slug].md      ⟳ parallel
             bcg-domain-expert        → domain-expert-input.md
  Phase 1.5  bcg-fact-checker         → validation-report.md
  Phase 2    bcg-portfolio-analyst    → portfolio.md

DD Phases:
  Phase DD-1   dd-market-validator         → dd-market-validation.md  ⟳ parallel
               dd-hypothesis-tester        → dd-hypothesis-report.md
  Phase DD-2   dd-risk-analyst             → dd-risk-matrix.md        ⟳ parallel
               dd-red-team                 → dd-red-team.md
  Phase DD-3a  dd-production-decision-first → dd-decision-first.md    ⟳ parallel
               dd-production               → dd-report.md (legal)
  Phase DD-3b  dd-production-summary       → dd-mid.md + dd-short.md
                                            (derived from dd-decision-first.md)
  Phase DD-4   notion-export (whitelist)   → 4 Notion pages + 📋 Feedback
                                            (MANDATORY, non-blocking)
```

**Phase DD-3a** runs the master report (decision-first) in parallel with the legal/institutional layer. **Phase DD-3b** derives the two short layers from the master — `dd-mid.md` and `dd-short.md` use only numbers that appear in `dd-decision-first.md`, ensuring cross-file consistency.

**Phase DD-4 (Notion export)** is mandatory and runs automatically. It exports **only the four decision deliverables** to Notion under a per-engagement page in "MBB Research Hub", and creates a `📋 Feedback` page for client comments. Supporting analyses stay local — Notion sees only what's needed for the decision.

If `NOTION_TOKEN` / `NOTION_MBB_ROOT_PAGE_ID` are missing in `.env`, Phase DD-4 is skipped with a clear retry instruction; the engagement still completes with all files saved locally.

### DD Output Files

```
research/apple-14.04.2026/
│
├── 📄 dd-short.md             ← 10-second decision  ⏱ start here
├── 📄 dd-mid.md               ← 5-min pre-meeting briefing
├── 📄 dd-decision-first.md    ← Full investment report  ← PRIMARY
├── 📄 dd-report.md            ← Institutional / legal reference
│
├── dd-market-validation.md    ← TAM/CAGR/moat adversarial validation
├── dd-hypothesis-report.md    ← 10 hypothesis test results (✅/⚠️/❌)
├── dd-risk-matrix.md          ← Full risk matrix (20 risks, P×I scoring)
├── dd-red-team.md             ← Bear case + stress scenarios + pre-mortem
│
├── company-brief.md           ← Verified raw data (single source of truth)
├── market-map.md              ← BCG segmentation
├── portfolio.md               ← BCG portfolio synthesis
├── validation-report.md       ← Fact-check report (A/B/C/F per segment)
├── advanced-analytics.md
├── segment-[slug].md          ← one per segment
│
├── notion-mapping.json        ← Notion page IDs (Phase DD-4)
├── notion-feedback.json       ← Feedback page ID
└── dd-engagement.log
```

### Command Options

```bash
/dd <company>                                     # minimal — all defaults
/dd <company> --deal-type M&A|PE|VC|secondary     # adapt analysis to deal type
/dd <company> --asking-price $500m                # enables Value Bridge with real price
/dd <company> --language ru                       # report in Russian (default: English)
/dd <company> --dir research/<existing-dir>       # skip BCG phases, use existing output
```

All flags are optional. `/dd Apple` works perfectly and runs the full pipeline.

---

## MBB Strategic Analysis

### MBB Consulting Pipeline

```
Phase -1  bcg-researcher          → company-brief.md
          SEC EDGAR, financials, news, LinkedIn, competitor data

Phase 0   bcg-market-mapper       → market-map.md          ⟳ parallel
          bcg-data-scientist      → advanced-analytics.md

Phase 1   bcg-segment-analyst ×N  → segment-[name].md      ⟳ parallel
          bcg-domain-expert       → domain-expert-input.md

Phase 1.5 bcg-fact-checker        → validation-report.md
          Verifies every number, flags hallucinations (✅/⚠️/❌)

Phase 2   bcg-portfolio-analyst   → portfolio.md
          MBB matrix, synergies, resource allocation, Selection Lens

Phase 2.5 bcg-gtm-analyst         → gtm-playbook.md
          ICP, DMU, Offer, Channel, Hypotheses, Pipeline, Retention

Phase 3   bcg-production          → final-report.md

Phase 3.5 bcg-contact-scout       → contact-universe.md    ⟳ parallel (optional)
          bcg-creative-strategist → creative-brief.md

Post      bcg-methodologist       → methodology-review.md
```

After Phase 3, you can continue to DD by typing "DD" (or "DD M&A $500m").

### Sales Intelligence Pipeline

```
/call-prep <company>
  bcg-account-intel  → account-brief.md
                        Value Pyramid + Contact Brief + Key Players + Talk Track

/analyze-call <company> [transcript]
  bcg-call-analyzer  → call-analysis.md + crm-update.json
                        MEDDPICC/BANT/3 Whys + Opportunity Summary

/send-outreach <engagement> [--goal gtm-outreach|sell-report]
  bcg-message-writer → outreach-drafts.md + outreach-drafts.json
  send_outreach.py   → outreach-log.json
                        Personalized email + 2 follow-ups per Tier 1 contact

/crm-sync <engagement> --direction pull|push
  fetch_crm.py / write_crm.py  →  HubSpot, Salesforce, Pipedrive, 50+ CRMs
```

---

## All Agents

### DD Agents

| Agent | Phase | Role |
|-------|-------|------|
| `dd-market-validator` | DD-1 | Adversarial TAM/CAGR/moat validation (VRIO) |
| `dd-hypothesis-tester` | DD-1 | Tests 10 deal hypotheses — disconfirming evidence first |
| `dd-risk-analyst` | DD-2 | Risk matrix: 15+ risks, P×I scoring, deal breakers, protections |
| `dd-red-team` | DD-2 | Bear case, short thesis, 3 stress scenarios, pre-mortem |
| `dd-production-decision-first` | DD-3a | Master IC-grade report (all 15 rules) → `dd-decision-first.md` |
| `dd-production` | DD-3a | Institutional / legal layer → `dd-report.md` (Pyramid Principle) |
| `dd-production-summary` | DD-3b | Derives `dd-mid.md` + `dd-short.md` from master, strict no-new-numbers contract |

### BCG Consulting Agents

| Agent | Phase | Role |
|-------|-------|------|
| `bcg-researcher` | -1 | SEC EDGAR + public data collection |
| `bcg-market-mapper` | 0 | MBB segmentation, revenue-bearing segments |
| `bcg-data-scientist` | 0 | Quantitative benchmarks, 10+ competitor analysis |
| `bcg-segment-analyst` | 1 | 5-lens analysis + 10–15 strategies per segment |
| `bcg-domain-expert` | 1 | Industry insider perspective, non-obvious dynamics |
| `bcg-fact-checker` | 1.5 | Validates all claims, data quality scoring A/B/C/F |
| `bcg-portfolio-analyst` | 2 | Portfolio view, Selection Lens, final recommendation |
| `bcg-gtm-analyst` | 2.5 | ICP, DMU, Offer, Channel, GTM hypotheses per strategy |
| `bcg-production` | 3 | Client-ready report, Pyramid Principle formatting |
| `bcg-contact-scout` | 3.5 | Target accounts + ICP scoring + email lookup |
| `bcg-audience-scout` | 3.5 | Find buyers for MBB reports (investors, analysts, press) |
| `bcg-creative-strategist` | 3.5 | LinkedIn ads, cold outreach sequences, pitch narratives |
| `bcg-methodologist` | post | Methodology evaluation + prompt improvement proposals |
| `bcg-pdf-designer` | on-demand | Chrome headless PDF generation |
| `bcg-notion-processor` | on-demand | Applies Notion feedback to research files |

### Sales Intelligence Agents

| Agent | Triggered by | Role |
|-------|-------------|------|
| `bcg-account-intel` | `/call-prep` | Pre-call: Value Pyramid, Contact Brief, Key Players, Talk Track |
| `bcg-call-analyzer` | `/analyze-call` | Transcript → MEDDPICC/BANT/3 Whys + crm-update.json |
| `bcg-message-writer` | `/send-outreach` | Personalized email per contact, 3-email sequence |

---

## All Skills

| Skill | Command | Description |
|-------|---------|-------------|
| `dd` | `/dd <company>` | **Full DD pipeline** (BCG + DD phases + auto Notion) → Investment Verdict |
| `bcg-team` | `/bcg-team <company>` | BCG consulting engagement (→ offers DD after Phase 3) |
| `bcg-methodology-review` | `/bcg-methodology-review` | Cross-engagement methodology improvement |
| `call-prep` | `/call-prep <company>` | Pre-call intelligence brief |
| `analyze-call` | `/analyze-call <company>` | Sales call transcript analysis |
| `send-outreach` | `/send-outreach <engagement>` | Generate + send personalized outreach |
| `crm-sync` | `/crm-sync <engagement>` | Pull/push CRM data via Merge.dev |
| `notion-export` | `/notion-export <dir>` | Manual export of a research folder (DD does this automatically) |
| `notion-process` | `/notion-process <dir>` | Apply pending Notion feedback |
| `notion-process-all` | `/notion-process-all` | Process feedback across all research directories |

---

## Typical Workflows

### Due Diligence before a PE deal

```bash
/dd "Figma" --deal-type PE --asking-price $20bn
# → 48h later: dd-short.md (10s) / dd-mid.md (5m) / dd-decision-first.md (45m) / dd-report.md
# → Notion export of the 4 decision layers happens automatically (Phase DD-4)
# → 📋 Feedback page created for the IC's comments

# Generate PDF for the IC deck
# → say "PDF" after DD completes
```

### Due Diligence on existing BCG analysis

```bash
# Already ran BCG last week:
/bcg-team Stripe

# Now running DD on the same output:
/dd Stripe --deal-type VC --asking-price $65bn --dir research/stripe-07.04.2026
# → same trio output + Notion export
```

### BCG strategic analysis → DD → outreach

```bash
# Step 1: Full BCG analysis
/bcg-team Figma

# Step 2: After Phase 3, type "DD M&A $20bn" → DD phases run on existing output
# → automatic Notion export of decision layers

# Step 3: Sell the DD report to interested funds
/send-outreach figma-14.04.2026 --goal sell-report
```

### Sales intelligence (standalone)

```bash
/call-prep "Acme Corp"
/analyze-call "Acme Corp" transcript.txt
/crm-sync acme-callprep-03.04.2026 --direction push
/send-outreach acme-callprep-03.04.2026
```

### Manual Notion retry (if Phase DD-4 failed)

```bash
# If the engagement completed but Notion was unreachable:
/notion-export figma-14.04.2026

# Or directly with the whitelist that DD uses:
NOTION_FILES_WHITELIST="dd-short.md,dd-mid.md,dd-decision-first.md,dd-report.md" \
  python3 .claude/skills/notion-export/export_to_notion.py research/figma-14.04.2026
```

### Follow-up email sequences

```bash
# Day 3: follow-up #1
python3 .claude/skills/send-outreach/send_outreach.py \
  --data research/<dir>/outreach-drafts.json --approve all --follow-up 1

# Day 7: follow-up #2 (breakup)
python3 .claude/skills/send-outreach/send_outreach.py \
  --data research/<dir>/outreach-drafts.json --approve all --follow-up 2
```

---

## Output Structure

### DD Engagement

```
research/apple-14.04.2026/
│
├── dd-short.md                ← 10-second decision  ⏱ start here
├── dd-mid.md                  ← 5-min pre-meeting briefing
├── dd-decision-first.md       ← Full investment report  ← PRIMARY
├── dd-report.md               ← Institutional / legal reference
│
├── dd-market-validation.md    ← supporting
├── dd-hypothesis-report.md    ← supporting
├── dd-risk-matrix.md          ← supporting
├── dd-red-team.md             ← supporting
│
├── company-brief.md
├── market-map.md
├── advanced-analytics.md
├── segment-[name].md          ← one per segment
├── domain-expert-input.md
├── validation-report.md
├── portfolio.md
│
├── notion-mapping.json        ← Notion page IDs (Phase DD-4)
├── notion-feedback.json
├── notion-export-error.log    ← only if Phase DD-4 failed
└── dd-engagement.log
```

### BCG-only Engagement (no DD)

Replace the `dd-*` files above with:

```
├── final-report.md
├── gtm-playbook.md            ← if /bcg-team requested GTM
├── contact-universe.md        ← if Phase 3.5 ran
├── creative-brief.md          ← if Phase 3.5 ran
└── methodology-review.md
```

### Sales Intelligence

```
research/acme-callprep-03.04.2026/
├── account-brief.md
├── outreach-drafts.md
├── outreach-drafts.json
├── outreach-log.json
├── call-analysis.md
├── crm-update.json
└── crm-data/
    ├── contacts.json
    ├── accounts.json
    └── opportunities.json
```

---

## MBB Framework

**5 lenses (sequential):** Description → Advantage → Future → Options → Selection

**Segmentation principle:** A segment exists only if a competitor can be profitable in it without adjacent segments.

**Hypothesis-driven:** Every engagement starts with 10 testable hypotheses, explicitly confirmed or rejected.

**Pyramid Principle:** All outputs lead with the conclusion, followed by arguments, then data.

**DD quality standards:**
- 10 DD hypotheses per engagement, all explicitly tested (✅/⚠️/❌)
- 3+ refuted hypotheses → automatic PASS, no exceptions (Rule 14)
- 15+ risks in risk matrix with P×I scoring; 20 risks minimum in the master report
- Bear case with quantified financial model (4 scenarios)
- Value Bridge: every DD must reconcile asking price with DD-adjusted value + probability-weighted expected return
- "So what?" block on every risk: data → mechanism → quantified consequence → verdict anchor

---

## Environment Setup

Copy `.env.example` → `.env`:

```bash
# Notion — required for automatic Phase DD-4 Notion export
NOTION_TOKEN=
NOTION_MBB_ROOT_PAGE_ID=

# CRM (/crm-sync) — Merge.dev (HubSpot, Salesforce, Pipedrive, 50+ CRMs)
MERGE_API_KEY=

# Outreach (/send-outreach)
RESEND_API_KEY=         # resend.com — 3000 emails/month free
FROM_EMAIL=
FROM_NAME=
```

If Notion credentials are missing, `/dd` still completes — Phase DD-4 logs a clear retry instruction and the four decision files remain available locally.

---

## References

- `.claude/skills/dd/references/dd-output-standard.md` — **15-rule Decision-First Output Standard** (mandatory read for DD production agents)
- `.claude/skills/dd/references/templates/` — structural reference templates (NVIDIA DD example)
- `.claude/skills/bcg-team/references/bcg-framework-5-lenses.md` — MBB 5-lens framework
- `methodology/dd-output-standard.md` — canonical copy of the DD standard
- `methodology/improvement-log.md` — cross-engagement methodology improvements
- `MBB Strategy Framework.pdf` — Source document (MBB, June 2001)
