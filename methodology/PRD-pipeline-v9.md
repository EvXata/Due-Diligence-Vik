# PRD — BCG Strategy Pipeline v9.0.0 (FINAL)

**Status:** Final · 2026-05-24
**Supersedes:** PRD-pipeline-v8.md
**Type:** Bug-fix release (cumulative on v8, no structural changes)
**Companion artefacts:**
- `methodology/pipeline9.json` — generated execution spec
- `methodology/pipeline9.json.sha256` — integrity hash `68569d44…`
- `scripts/build_pipeline_v9.py` — reproducible builder (cumulative on v8)
- `methodology/v8-microsoft-synthetic-case-and-diff.md` — case that surfaced the 5 bugs

---

## 1. Why v9 (TL;DR)

v9 is a **pure bug-fix release** on top of v8. No new stages, no architectural changes. 5 production-risk bugs surfaced by the Microsoft synthetic case (`v8-microsoft-synthetic-case-and-diff.md`) — all fixed via prompt-content patches.

---

## 2. 5 bug fixes applied

| # | Bug | Where | Fix | Severity |
|---|---|---|---|---|
| 1 | Single-corporate-entity vs strategic-BU distinction broken | `00c_bu_structure_detection` (legacy enrichment module) | Output both `legal_bu_count` AND `strategic_bu_count`. Phase 1 fan-out uses larger value. When they disagree, PM confirms with Sponsor (auto-proceed in 24h if no objection). | HIGH |
| 2 | Pure Player Test missing 4th verdict for cross-segment-only-viable segments | `1S1_pure_player_test` | Add `VALID_AS_CROSS_SEGMENT_PLAY` verdict. Triggers downstream pattern routing as adjacency (not standalone Star/Cash-Cow/Dog). | MEDIUM |
| 3 | Entry-cell anti-pattern flag not auto-firing | `4_GENERATE` | When ENTRY classified, auto-evaluate 4 anti-pattern indicators. If ≥2 fire → `anti_pattern_flag=true` → BLOCKS 4_STRATEGY_FINANCIAL elaboration until Sponsor accepts in writing. | MEDIUM |
| 4 | `0d_domain_expert_input` lacks auto-invocation rule | `0d_domain_expert_input` | Add `auto_invoke_when` field. Auto-invokes for industry ∈ {IND-B2B-SW, IND-B2B-HW, IND-B2B-SVC, IND-FIN, IND-HCP, IND-IND, IND-ENRG}; manual for consumer (IND-B2C-RTL, IND-B2C-DTC, IND-MARKET). | MEDIUM |
| 5 | Inline contradiction check missing | `V5_validator_check` | Scan `6A_decision_memo` + `6B_strategy_narrative` for repeated claims with conflicting framing (e.g., "80% adoption" + "mostly pilot-stage"). HIGH-confidence contradiction → REVISE; MEDIUM/LOW → flag for partner at G7. | MEDIUM |

---

## 3. Build output

```
Pipeline v9.0.0 assembled.
  Total stages: 68 (same as v8 — no structural changes)
  By model: haiku 12, sonnet 31, opus 25
  v9 bug fixes applied: 5/5
    - 00c_bu_structure_detection: #1 — strategic_bu_count distinction
    - 1S1_pure_player_test: #2 — VALID_AS_CROSS_SEGMENT_PLAY verdict
    - 4_GENERATE: #3 — auto anti-pattern flag for ENTRY-cell strategies
    - 0d_domain_expert_input: #4 — auto_invoke_when rule
    - V5_validator_check: #5 — inline_contradiction_check
SHA256: 68569d44da346fcfe5a75880debbcaff81a0726be04589d041bd38f5b246f0a5
```

---

## 4. Required fields added/updated

| Stage | New required fields |
|---|---|
| `00c_bu_structure_detection` | `legal_bu_count`, `strategic_bu_count`, `bu_count_divergence_flag` |
| `1S1_pure_player_test` | `segments_valid_as_cross_segment_play` |
| `4_GENERATE` | `anti_pattern_flagged_strategies`, `entry_cell_evaluated` |
| `0d_domain_expert_input` | `auto_invoke_when`, `auto_invoked_for_this_engagement` |
| `V5_validator_check` | `inline_contradiction_check` |

---

## 5. Reproducible build chain

```bash
# Full chain (each cumulative on previous):
python3 scripts/build_pipeline_v6.py --output methodology/pipeline6.json   # 55 stages, base
python3 scripts/build_pipeline_v7.py --output methodology/pipeline7.json   # 62 stages, +7 onboarding
python3 scripts/build_pipeline_v8.py --output methodology/pipeline8.json   # 68 stages, +6 wow funnel
python3 scripts/build_pipeline_v9.py --output methodology/pipeline9.json   # 68 stages, +5 bug fixes

# Verify reproducibility:
python3 scripts/build_pipeline_v9.py --output /tmp/check.json
diff methodology/pipeline9.json /tmp/check.json   # zero-diff expected
```

All SHAs pinned in `.sha256` files. v9 confirmed reproducible.

---

## 6. Deployment

v9 ships as drop-in replacement for v8 — no agent prompts need re-writing, no orchestration changes. Same 4-level hierarchy, same 13 gates, same orchestrator topology. Only difference: 5 stage prompts have additional content + 5 stages have additional required output fields.

| Stage | Window | Approach |
|---|---|---|
| 1. Shadow | 1 week | Run v9 on the next in-flight engagement; verify all 5 bug fixes activate correctly |
| 2. Cohort A | 2 weeks | 100% of new engagements on v9 (no random assignment needed — bug-fix-only release) |
| 3. Deprecate v8 | Cohort A stable | v8 archived |

### Rollback triggers
- Any of 5 fix logics produces false positives (e.g., Pure Player VALID_AS_CROSS_SEGMENT_PLAY misapplied; anti-pattern flag firing on valid strategies; inline contradiction false alarm)
- Cost regression vs v8 baseline
- Sponsor friction with anti-pattern acceptance workflow

---

## 7. Changelog

| Version | Date | Change |
|---|---|---|
| v9.0.0 | 2026-05-24 | **FINAL** — 5 bug fixes from Microsoft synthetic case applied: strategic_bu_count distinction; VALID_AS_CROSS_SEGMENT_PLAY Pure Player verdict; auto anti-pattern flag for ENTRY-cell strategies; Domain Expert auto-invocation rule for B2B-vertical industries; inline contradiction check in V5 validator. No structural changes. Cumulative on v8. |

---

*END PRD v9.0.0 FINAL*
