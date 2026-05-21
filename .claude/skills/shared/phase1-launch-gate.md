# Phase 1 — Pre-Flight Batch Count Gate (MANDATORY)

> **Canonical reference for the Phase 1 enumeration-and-launch protocol.**
> Referenced from `bcg-team/SKILL.md` and `dd/SKILL.md`. Edit here; do not
> duplicate inline.

**Why this gate exists:** On the Cursor DD engagement (19.05.2026), the
orchestrator launched 4 agents (3 segments + 1 domain-expert) instead of 5
(4 segments + 1 domain-expert) — missed S4 Autonomous Agents in the batch.
Recovery required a sequential second run of the missing segment, costing
~46 min wall-clock (~35% of total DD time). This gate prevents that class
of bug by enforcing an explicit enumeration → launch-count match before
dispatch.

---

## The 5-step gate (run in order, before ANY `bcg-segment-analyst` call)

1. **Enumerate segments from market-map.md:**
   ```bash
   grep -E "СЕГМЕНТ [0-9]|^## \[?СЕГМЕНТ\b" [OUTPUT_DIR]/market-map.md | wc -l
   ```
   → `expected_segment_count`.

2. **Extract segment slugs** from the "итоговая карта" / "summary map" table
   at the top of `market-map.md`. Each Tier-1 segment becomes a `tier=1`
   dispatch; all Tier-2 segments collapse to a single `tier=2-batch` dispatch.

3. **Compute expected agent count:**
   - Pre-Microsoft pipeline: `N_segments + 1` (one analyst per segment + 1 domain-expert)
   - Post-Microsoft pipeline (current): `min(N_tier1, 3) + (1 if any tier2 else 0) + 1`
     = at most 3 Tier-1 analysts + 1 Tier-2 batch + 1 domain-expert = 5 calls max

4. **State the launch plan explicitly to the user**, e.g.:
   ```
   Phase 1 launch plan: N segments detected from market-map →
   launching K agents in parallel:
     - tier=1: [slug-1], [slug-2], [slug-3]
     - tier=2-batch: [slug-4, slug-5, slug-6]
     - bcg-domain-expert
   ```

5. **Dispatch in a SINGLE message with EXACTLY K Agent tool calls.**
   If launched count ≠ planned count → STOP. Do not proceed with an
   incomplete launch — recover would cost a full sequential re-run.

---

## Failure modes this prevents

| Failure mode | Cost if missed |
|---|---|
| Skipped segment in batch (Cursor DD pattern) | ~46 min wall-clock recovery |
| Tier-1 over-assignment beyond cap of 3 | +25-45% Phase 1 wall-clock |
| Domain-expert forgotten | Missing insider verification of all 10 hypotheses |
| Multi-message dispatch (loses parallelism) | N × ~10 min sequential vs 1 × ~12 min parallel |

---

## Notes for orchestrators

- If `MEGA_CAP=true` is set (mega-cap override per dd/SKILL.md), the Tier-1
  cap may be raised above 3 (see "Mega-cap override" section in dd/SKILL.md).
- Tier-2 batch can be split into 2 batches if `N_tier2 > 5` (see dd/SKILL.md
  Sprint 3 #8 / forthcoming optimization). Each split = 1 additional agent
  call — adjust K accordingly.
- The grep pattern handles both Russian (`СЕГМЕНТ`) and English (`## SEGMENT`)
  headings via the alternation. If `bcg-market-mapper` ever changes its output
  format, update the pattern HERE — both SKILLs will pick it up.
