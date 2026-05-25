# PRD — BCG Strategy Pipeline v9.1.0

**Status:** Final · 2026-05-25
**Supersedes:** PRD-pipeline-v9.md (still valid — v9.1 is cumulative)
**Type:** Quality release (additive only; no structural changes)
**Companion artefacts:**
- `methodology/pipeline91.json` — generated execution spec (sha256 `204dfd45…`)
- `methodology/pipeline91.json.sha256` — integrity hash
- `scripts/build_pipeline_v9_1.py` — reproducible builder (cumulative on v9)
- `methodology/pipeline-v9-proposed-updates.md` — post-integration audit that surfaced these 6 patches

---

## 1. Why v9.1 (TL;DR)

v9.1 brings the **spec into alignment with the runtime agents** + adds one genuinely new enforcement (P4 TAM-ceiling resolution). Six patches surface confirmed cross-engagement patterns (Apple/Samsung/Amkor/Alphabet — Innovate absence; Micron/Amkor/GFS — TAM-ceiling breach; Micron/Amkor — partial-correction propagation; Samsung→GFS — Part V GTM redundancy).

Pre-v9.1 state: the agent prompts in `.claude/agents/bcg-*.md` already enforced P1, P2, P3, P5 and most of P6 via earlier `applied-changes.md` patches; the v9 spec itself did not yet encode them, so V0–V5 validator audits had no spec hook to assert against. v9.1 closes that loop.

---

## 2. 6 patches applied

| # | Patch | Stage(s) patched | Type | Evidence (engagements) |
|---|---|---|---|---|
| P1 | Innovate Archetype Mandatory Gate (per segment ≥1 I OR explicit NOT_VIABLE) | `4_GENERATE` | content + 2 required fields | 4 — Apple/Samsung/Amkor/Alphabet |
| P2 | Question Mark 8-strategy floor + structural template (2D/2S/1P/1F/1I/1exit) | `4_GENERATE` | content + 2 required fields | 1 explicit (Alphabet) + 5 prior latent |
| P3 | Self-derived TAM `⚠️ NO INDEPENDENT SOURCE` warning at TOP of TAM block | `1S0_segmenter`, `1B_industry_economics`, `6F_market_map_data` | content + 2 required fields per stage | 1 explicit (GFS) + 2 prior latent in semiconductor |
| P4 | **NEW** — TAM-ceiling resolution protocol (a/b/c, BLOCKING) | `4_STRATEGY_FINANCIAL` | content + 1 required field | 3 — Micron/Amkor/GFS |
| P5 | Part V GTM-narrative scope gate + V5 6E↔6B trigram-Jaccard overlap detector | `6E_implementation_roadmap`, `V5_validator_check` | content + 2 required fields | 5 declining-residual — Samsung→GFS |
| P6 | Validation-override propagation checklist (1V emits `corrections_required[]`; 5_SELECT_final + 6A must echo `corrections_applied[]` at preamble) | `1V_validation_report`, `5_SELECT_final`, `6A_decision_memo` | content + 1 required field per stage | 2 — Micron/Amkor partial propagation |

---

## 3. Build output

```
Pipeline v9.1.0 assembled.
  Total stages: 68 (same as v9 — no structural changes)
  By model: haiku 12, sonnet 31, opus 25
  v9.1 patches applied: 6/6 (10 stage-content patches, 14 new required fields)
SHA256: 204dfd451041f3f7a02342cee537feb1b7e22c3b777ac7e083d5eb550459a75a
```

---

## 4. Required fields added

| Stage | New required fields |
|---|---|
| `4_GENERATE` | `innovate_strategies_generated`, `innovate_not_viable`, `strategy_count_by_bcg_position`, `qm_structural_template_applied` |
| `4_STRATEGY_FINANCIAL` | `ceiling_check` (= `{implied_share_of_tam_pct, dominant_participant_flag, resolution_status, resolution_note}`) |
| `1S0_segmenter` | `tam_provenance`, `tam_warning_at_top` |
| `1B_industry_economics` | `tam_provenance`, `tam_warning_at_top` |
| `6E_implementation_roadmap` | `scope_gate_self_check_passed`, `forbidden_sentence_count_removed` |
| `1V_validation_report` | `corrections_required` (array of `{claim_id, stated_value, verified_value, source_for_correction, propagation_targets[]}`) |
| `5_SELECT_final` | `corrections_applied` (array of `{claim_id, verified_value}`) |
| `6A_decision_memo` | `corrections_applied` (array of `{claim_id, verified_value}`) |

---

## 5. Runtime-agent alignment

The corresponding `.claude/agents/bcg-*.md` already enforce most of v9.1 from earlier `applied-changes.md` patches:

| Patch | Runtime agent | Already enforced? | New work in v9.1 release |
|---|---|---|---|
| P1 | bcg-segment-analyst | ✅ (2026-03-28 Innovate blocking gate + 2026-04-09 substance gate) | spec encoding only |
| P2 | bcg-segment-analyst | ✅ (2026-04-09 QM minimum + structural template) | spec encoding only |
| P3 | bcg-market-mapper | ✅ partial (2026-03-28 TAM Source Hierarchy) | bring agent in line with new `tam_provenance` field |
| P4 | bcg-segment-analyst | ⚠️ partial (Revenue Check at >30% implied share) | upgrade to BLOCKING a/b/c resolution rule |
| P5 | bcg-production | ✅ (2026-04-09 Part V Incremental Content Enforcement strengthened) | spec encoding + V5 overlap detector new |
| P6 | bcg-portfolio-analyst + bcg-fact-checker | ✅ (2026-05-22 T-Bank Changes 3+4) | spec encoding only |

**Only P4 requires a fresh runtime patch** — see `.claude/agents/bcg-segment-analyst.md` edit landing alongside this PRD.

---

## 6. Reproducible build chain

```bash
# Full chain (each cumulative on previous):
python3 scripts/build_pipeline_v9.py   --output methodology/pipeline9.json    # v9.0.0 base (sha256 68569d44…)
python3 scripts/build_pipeline_v9_1.py --output methodology/pipeline91.json   # v9.1.0 (sha256 204dfd45…)

# Verify reproducibility:
python3 scripts/build_pipeline_v9_1.py --output /tmp/check.json
diff methodology/pipeline91.json /tmp/check.json   # zero-diff expected
```

v9.1 confirmed reproducible (zero-diff against a fresh build).

---

## 7. Deployment

v9.1 ships as drop-in replacement for v9 — no agent prompts need re-writing (only P4 in bcg-segment-analyst), no orchestration changes. Same 4-level hierarchy, same 13 gates, same orchestrator topology.

| Stage | Window | Approach |
|---|---|---|
| 1. Shadow | First engagement (T-Bank acceptance test) | Verify all 6 patches activate; capture V5 overlap-detector behavior |
| 2. Cohort | Next 3 engagements | 100% on v9.1; monitor false-positive rate on overlap detector |
| 3. Deprecate v9 | After cohort stable | v9 archived |

### Rollback triggers
- V5 6E↔6B overlap detector false-positive rate > 5% (legitimate cross-references flagged)
- P4 ceiling resolution blocks > 20% of strategies (would imply revenue-target inflation systemic, not a model bug)
- `corrections_applied` parity check at 6A breaks deck rendering in any downstream PDF agent

---

## 8. Changelog

| Version | Date | Change |
|---|---|---|
| v9.1.0 | 2026-05-25 | **FINAL** — 6 quality patches (additive). P1 Innovate mandatory per segment. P2 Question Mark 8-floor + template. P3 Self-derived TAM warning at top. P4 (**new**) TAM-ceiling resolution a/b/c. P5 Part V scope gate + V5 6E↔6B overlap detector. P6 Validation-override propagation checklist. Cumulative on v9.0.0. No structural changes. |
| v9.0.0 | 2026-05-24 | 5 bug fixes from Microsoft synthetic case (see PRD-pipeline-v9.md). |

---

*END PRD v9.1.0 FINAL*
