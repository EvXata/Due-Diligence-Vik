# Strategic Due Diligence & MBB Consulting — AI System

A multi-agent AI system that delivers two integrated products:

1. **Strategic Due Diligence** — investment-grade DD report for PE/VC/M&A/secondary deals in 48 hours
2. **MBB Strategic Analysis** — full BCG-style consulting engagement (business unit strategy, portfolio, GTM)

The DD pipeline runs on top of the BCG strategic foundation — BCG phases provide the analytical base, DD phases adversarially challenge it and deliver an Investment Verdict.

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

### What You Get

A `dd-report.md` with:

- **Investment Verdict**: `PROCEED` / `CONDITIONAL` / `PASS`
- **Value Bridge**: asking price → DD-adjusted fair value ($ gap)
- **Deal Breakers**: specific issues that could kill the deal
- **Hypothesis Scorecard**: 10 deal hypotheses, each ✅ / ⚠️ / ❌
- **Risk Matrix**: 15+ risks with probability × impact scoring and deal protections
- **Bear Case**: financial model (bull/base/bear/deep bear) + 3 stress scenarios + pre-mortem

### Why It's Valuable for Funds

| What the report surfaces | Concrete value |
|--------------------------|---------------|
| Deal-breakers before capital is committed | Avoid a bad $50–500M deal |
| Growth story validation (often overstated) | Negotiation leverage: 5–20% price adjustment |
| Hidden risks (tech debt, customer concentration, regulatory) | Prevent value destruction post-close |
| Quantified bear case with stress scenarios | IC-ready stress test |

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
  Phase DD-1  dd-market-validator     → dd-market-validation.md  ⟳ parallel
              dd-hypothesis-tester    → dd-hypothesis-report.md
  Phase DD-2  dd-risk-analyst         → dd-risk-matrix.md        ⟳ parallel
              dd-red-team             → dd-red-team.md
  Phase DD-3  dd-production           → dd-report.md  ← PRIMARY OUTPUT
```

### DD Output Files

```
research/apple-14.04.2026/
├── dd-report.md              ← PRIMARY DELIVERABLE — start here
├── dd-market-validation.md   ← TAM/CAGR/moat adversarial validation
├── dd-hypothesis-report.md   ← 10 hypothesis test results (✅/⚠️/❌)
├── dd-risk-matrix.md         ← Full risk matrix (15+ risks, P×I scoring)
├── dd-red-team.md            ← Bear case + stress scenarios + pre-mortem
└── [BCG foundation files below]
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
| `dd-production` | DD-3 | Final DD report: Verdict + Value Bridge + conditions |

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
| `dd` | `/dd <company>` | **Full DD pipeline** (BCG + DD phases) → Investment Verdict |
| `bcg-team` | `/bcg-team <company>` | BCG consulting engagement (→ offers DD after Phase 3) |
| `bcg-methodology-review` | `/bcg-methodology-review` | Cross-engagement methodology improvement |
| `call-prep` | `/call-prep <company>` | Pre-call intelligence brief |
| `analyze-call` | `/analyze-call <company>` | Sales call transcript analysis |
| `send-outreach` | `/send-outreach <engagement>` | Generate + send personalized outreach |
| `crm-sync` | `/crm-sync <engagement>` | Pull/push CRM data via Merge.dev |
| `notion-export` | `/notion-export <dir>` | Export research folder to Notion |
| `notion-process` | `/notion-process <dir>` | Apply pending Notion feedback |
| `notion-process-all` | `/notion-process-all` | Process feedback across all research directories |

---

## Typical Workflows

### Due Diligence before a PE deal

```bash
/dd "Figma" --deal-type PE --asking-price $20bn
# → 48h later: dd-report.md with PROCEED/CONDITIONAL/PASS verdict

# Export to Notion for the IC
/notion-export figma-14.04.2026

# Generate PDF for the IC deck
# → say "PDF" after DD completes
```

### Due Diligence on existing BCG analysis

```bash
# Already ran BCG last week:
/bcg-team Stripe

# Now running DD on the same output:
/dd Stripe --deal-type VC --asking-price $65bn --dir research/stripe-07.04.2026
```

### BCG strategic analysis → DD → outreach

```bash
# Step 1: Full BCG analysis
/bcg-team Figma

# Step 2: After Phase 3, type "DD M&A $20bn" → DD phases run on existing output

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

### DD + BCG Engagement

```
research/apple-14.04.2026/
├── dd-report.md              ← PRIMARY DD DELIVERABLE
├── dd-market-validation.md
├── dd-hypothesis-report.md
├── dd-risk-matrix.md
├── dd-red-team.md
├── company-brief.md
├── market-map.md
├── advanced-analytics.md
├── segment-[name].md         ← one per segment
├── domain-expert-input.md
├── validation-report.md
├── portfolio.md
├── gtm-playbook.md           ← if requested
├── final-report.md           ← BCG final report (if BCG-only run)
├── contact-universe.md       ← if Phase 3.5 ran
├── creative-brief.md         ← if Phase 3.5 ran
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
- 15+ risks in risk matrix with P×I scoring
- Bear case with quantified financial model (4 scenarios)
- Value Bridge: every DD must reconcile asking price with DD-adjusted value

---

## Environment Setup

Copy `.env.example` → `.env`:

```bash
# Notion
NOTION_TOKEN=
NOTION_MBB_ROOT_PAGE_ID=

# CRM (/crm-sync) — Merge.dev (HubSpot, Salesforce, Pipedrive, 50+ CRMs)
MERGE_API_KEY=

# Outreach (/send-outreach)
RESEND_API_KEY=         # resend.com — 3000 emails/month free
FROM_EMAIL=
FROM_NAME=
```

---

## References

- `.claude/skills/bcg-team/references/bcg-framework-5-lenses.md` — MBB 5-lens framework
- `MBB Strategy Framework.pdf` — Source document (MBB, June 2001)
