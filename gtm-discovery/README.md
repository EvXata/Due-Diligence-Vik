# Vik DD GTM Discovery Vector

**Scope:** only Strategic Due Diligence deals where a buyer ordered, received, or partially received one of:
- `bear_case` / red-team layer (`dd-red-team.md`, bear section in `dd-short.md`, breakup files)
- `bull_case` (`bull-case.md` or explicit bull optionality memo)
- `deep_audit` (`dd-decision-first.md`, full IC-grade DD)

This excludes generic BCG strategy work and sales collateral. NVIDIA is tracked as `partial_pipeline` because DD started, but no bear/bull/deep decision layer exists in the folder.

---

## Why This Vector Exists

The PreCompany v13 tournament found that diligence products can be ranked by buyer fit, price, conversion, and NPS. Vik DD already has real artifacts across public equity, token secondary, M&A/acquirer, and growth/private rounds. This folder turns those artifacts into a deal-level tournament dataset:

```
Vik DD files
    -> ordered product flags
    -> deal + buyer vector
    -> tournament score
    -> GTM discovery recommendation
    -> next outreach / packaging decision
```

The unit is not a company. The unit is a **purchased decision job**:

> "For this buyer, at this price, did bear case / bull case / deep audit create the most sellable decision value?"

---

## Files

| File | Purpose |
|---|---|
| `dd-deal-vector.csv` | Flat deal vector for spreadsheet / tournament import |
| `dd-deal-vector.json` | Structured version with notes and source files |
| `tournament-methodology.md` | Scoring logic, product taxonomy, GTM use |
| `gtm-discovery-playbook.md` | Product packaging + discovery motions derived from the vector |

Regenerate / extend:

```bash
python3 scripts/build_dd_gtm_vector.py
```

The script is intentionally conservative. It scans artifact presence and extracts obvious log metadata, but the curated vector remains the source of truth for GTM interpretation until there is CRM/payment data.

---

## Current Readout

The strongest GTM wedge is **Bear Case / Deep Audit for overpriced strategic decisions**.

Top observed jobs:
- **Private growth round overpricing:** Cursor Series E at $50B, PASS with high conviction.
- **Token secondary downside / unlock risk:** dYdX, PASS with Rule 14.
- **Sanctioned / constrained acquirer DD:** T-Bank / Tinkoff, PASS or conditional only with protections.
- **Mega-cap public equity entry discipline:** Microsoft and Bitcoin, CONDITIONAL with explicit tripwires.

Bull case is useful, but mostly as an **objection handler** after the bear case. In the current corpus, bull memos rarely overturn the verdict; they clarify the exact conditions under which a buyer can still proceed.

