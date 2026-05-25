#!/usr/bin/env python3
"""
build_pipeline_v9_1.py — Pipeline v9.1.0 patcher.

Cumulative on v9.0.0: reads methodology/pipeline9.json, applies six P1–P6 quality patches
(stage-content additions + new required fields). Writes methodology/pipeline91.json and
.sha256. No structural changes; the 68-stage / 9-module shape is preserved.

P1  4_GENERATE       — Innovate Archetype Mandatory Gate (per-segment ≥1 I or NOT_VIABLE)
P2  4_GENERATE       — Question Mark 8-floor + structural template
P3  1S0/1B/6F        — Self-derived TAM ⚠️ NO INDEPENDENT SOURCE warning at top
P4  4_STRATEGY_FINANCIAL — TAM-ceiling resolution protocol (a/b/c), blocking
P5  6E + V5          — Part V GTM-narrative scope gate; V5 extended for 6E ↔ 6B overlap
P6  1V + 5_SELECT_final + 6A — Validation-override propagation checklist

Usage:
    python3 scripts/build_pipeline_v9_1.py
    python3 scripts/build_pipeline_v9_1.py --input methodology/pipeline9.json \\
            --output methodology/pipeline91.json
"""

from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path


# ─────────────────────────── patch payloads ───────────────────────────

P1_P2_GENERATE = """

=== v9.1 PATCH P1 — Innovate Archetype Mandatory Gate (per segment) ===
For every segment / BU, you MUST generate ≥1 Innovate (I) strategy OR emit an explicit
`I: NOT_VIABLE — <reason>` line. Omission is a V4 validator failure.

DEFINITION: an Innovate strategy describes a business model, product category, or revenue
stream that does NOT currently exist for THIS company in THIS segment, AND is not a direct
variant of an existing product/play. Pure pricing changes, feature improvements, and same-
category M&A do NOT qualify as Innovate.

VALID I patterns: new pricing model · new buyer class served for the first time · new
position in the value chain · new regulatory category · new go-to-market motion (PLG into
enterprise-historical, etc.).

OUTPUT SCHEMA ADDITION (required):
  "innovate_strategies_generated": [{"segment": str, "strategy_id": str, "valid_pattern": str}]
  "innovate_not_viable": [{"segment": str, "reason": str}]


=== v9.1 PATCH P2 — Question Mark Strategy 8-Floor + Structural Template ===
Strategy-count floors per BCG position (BLOCKING — stage cannot emit unless met):
  Star          ≥ 10
  Question Mark ≥  8   ← v9.1 NEW (was implicit-only previously)
  Cash Cow      ≥  8
  Dog           ≥  6

For Question Mark segments, default structural template is:
  2×D (defend / fortify) + 2×S (scale / grow segment) + 1×P (pivot) + 1×F (focus / differentiate)
  + 1×I (innovate) + 1×exit (IPO / JV / divestiture)

OUTPUT SCHEMA ADDITION (required):
  "strategy_count_by_bcg_position": {"Star": int, "Question Mark": int, "Cash Cow": int, "Dog": int}
  "qm_structural_template_applied": bool
"""

P4_STRATEGY_FINANCIAL = """

=== v9.1 PATCH P4 — TAM-Ceiling Resolution Protocol (BLOCKING) ===
After computing FY+5 base case revenue per strategy, compute `implied_share_of_tam_pct`.

RESOLUTION RULE (BLOCKING — stage cannot emit `4_STRATEGY_FINANCIAL` for this strategy
until resolved):
  - `implied_share > 50%` AND company is NOT the dominant participant in the segment
    OR
  - `implied_share > 80%` for ANY participant

→ Resolve via ONE of:
  (a) revise FY+5 target to a credible share (cite competitor share precedent)
  (b) expand TAM with a NAMED Tier-1 / Tier-2 source accommodating new revenue streams
      (e.g., adjacent sub-segment now included)
  (c) explicitly label `target_not_independently_constrained: true` AND state the assumption
      that would need to hold for the target to be reachable

DO NOT flag-and-pass; resolution must occur inside this stage.

OUTPUT SCHEMA ADDITION (required):
  "ceiling_check": {
    "implied_share_of_tam_pct": float,
    "dominant_participant_flag": bool,
    "resolution_status": "resolved_a" | "resolved_b" | "labeled_c" | "not_triggered",
    "resolution_note": str
  }
"""

P3_SEGMENTER = """

=== v9.1 PATCH P3 — Self-Derived TAM Provenance Warning ===
For every candidate segment, classify TAM provenance:
  - `tier1_sourced`  — published as a named line item by Goldman, Morgan Stanley, IDC,
                       Gartner, Canalys, SEMI, McKinsey, BCG, Bain, or government.
  - `tier2_sourced`  — Bloomberg, Reuters, FT, WSJ, Forrester, Counterpoint, Grand View,
                       Mordor Intelligence, trade press.
  - `self_derived`   — your own bottom-up or top-down construction (Tier-3 aggregator ×
                       estimated share ratio, multi-source triangulation, etc.).

When `tam_provenance == "self_derived"`, emit at the TOP of the segment's TAM block
(NOT in a footnote) a warning verbatim of this form:

  > ⚠️ TAM — NO INDEPENDENT SOURCE
  > This TAM is self-derived via <methodology>. All downstream revenue targets that
  > reference this number inherit the same uncertainty.

V1 validator REJECTS placements in footnote or appendix.

OUTPUT SCHEMA ADDITION (required, per segment):
  "tam_provenance": "tier1_sourced" | "tier2_sourced" | "self_derived"
  "tam_warning_at_top": bool   (must be true whenever tam_provenance == "self_derived")
"""

P3_INDUSTRY = """

=== v9.1 PATCH P3 — Self-Derived TAM warning (industry-economics surface) ===
Mirror `1S0_segmenter`'s `tam_provenance` and `tam_warning_at_top` fields. When the BU's
industry TAM is self-derived, the warning must appear at the top of section "Industry
size & growth" — not as a footnote. V1 validator audits both stages for consistency.
"""

P3_MARKET_MAP_DATA = """

=== v9.1 PATCH P3 — Self-Derived TAM warning (delivery-surface) ===
When rendering market-map data for the deck, preserve the `⚠️ TAM — NO INDEPENDENT SOURCE`
banner above any self-derived TAM. Do NOT relocate to a footnote or speaker-note. V5
validator rejects banner removal.
"""

P5_IMPLEMENTATION_ROADMAP = """

=== v9.1 PATCH P5 — GTM Narrative Scope Gate ===
6E (implementation roadmap, "Part V" in the deck) is restricted to operational content.

ALLOWED in 6E:
  - ICP one-sentence definition (per recommended strategy)
  - 5-step channel sequence with timeline
  - ACV / deal-cycle / NRR three-row table
  - First-90-days plan: each line has named action · counterparty · binary milestone

FORBIDDEN in 6E (all live in 6A decision memo / 6B strategy narrative / 6D financial exhibits):
  - Sentences explaining WHY the market is attractive
  - Sentences describing the company's competitive advantage
  - Sentences re-stating WHAT the strategy is or WHY it was selected
  - Trigger phrase ban: any paragraph starting "This strategy assumes…" / "The essence
    of this approach…" / "We are betting that…" must be deleted or moved to 6B.

V5 inline contradiction check now also flags 6E ↔ 6B overlap (any sentence in 6E that
could appear verbatim in 6B → REVISE).

OUTPUT SCHEMA ADDITION (required):
  "scope_gate_self_check_passed": bool
  "forbidden_sentence_count_removed": int
"""

P5_V5_EXTENSION = """

=== v9.1 PATCH P5 — V5 6E ↔ 6B overlap detector ===
Extend `inline_contradiction_check` (added in v9.0.0 BUG #5) with a second scan pass:

PASS 2 — 6E ↔ 6B narrative overlap:
  - For every sentence in 6E_implementation_roadmap, compute trigram Jaccard similarity
    against every sentence in 6B_strategy_narrative.
  - Flag any sentence with similarity ≥ 0.65 OR identical claim with paraphrase.
  - Verdict policy:
      ≥ 0.85 similarity → REVISE (delete from 6E)
      0.65–0.85         → flag for Partner at G7
"""

P6_VALIDATION_REPORT = """

=== v9.1 PATCH P6 — Validation-Override Propagation Checklist ===
1V_validation_report now emits a structured `corrections_required[]` block that downstream
stages must explicitly acknowledge.

Each entry has shape:
  {
    "claim_id": str,
    "stated_value": str,
    "verified_value": str,
    "source_for_correction": str,
    "propagation_targets": [stage_id, ...]   // typically ["5_SELECT_final", "6A_decision_memo"]
  }

Downstream stages listed in `propagation_targets` MUST include a "Corrections applied"
block at preamble naming every entry by `claim_id`. V5 validator BLOCKS at G7 if any
correction in `corrections_required[]` is missing from its declared target.
"""

P6_SELECT_FINAL = """

=== v9.1 PATCH P6 — Corrections Applied preamble (selection) ===
5_SELECT_final MUST begin with a "Corrections applied" block listing every entry from
1V_validation_report.corrections_required[] where `5_SELECT_final` is in propagation_targets.
Each entry naming the claim_id, the stated_value (rejected) and the verified_value (used).

OUTPUT SCHEMA ADDITION (required):
  "corrections_applied": [{"claim_id": str, "verified_value": str}]
"""

P6_DECISION_MEMO = """

=== v9.1 PATCH P6 — Corrections Applied preamble (decision memo) ===
6A_decision_memo MUST mirror the corrections-applied block from 5_SELECT_final at the top
of the memo. V5 enforces parity (every claim in 5_SELECT_final.corrections_applied must
appear in 6A_decision_memo.corrections_applied).

OUTPUT SCHEMA ADDITION (required):
  "corrections_applied": [{"claim_id": str, "verified_value": str}]
"""


# ─────────────────────────── builder ───────────────────────────

# Map: stage_id → list of (label, patch_text) appended to stage.content
STAGE_CONTENT_PATCHES: dict[str, list[tuple[str, str]]] = {
    "4_GENERATE": [("P1_P2", P1_P2_GENERATE)],
    "4_STRATEGY_FINANCIAL": [("P4", P4_STRATEGY_FINANCIAL)],
    "1S0_segmenter": [("P3", P3_SEGMENTER)],
    "1B_industry_economics": [("P3", P3_INDUSTRY)],
    "6F_market_map_data": [("P3", P3_MARKET_MAP_DATA)],
    "6E_implementation_roadmap": [("P5", P5_IMPLEMENTATION_ROADMAP)],
    "V5_validator_check": [("P5", P5_V5_EXTENSION)],
    "1V_validation_report": [("P6", P6_VALIDATION_REPORT)],
    "5_SELECT_final": [("P6", P6_SELECT_FINAL)],
    "6A_decision_memo": [("P6", P6_DECISION_MEMO)],
}

# Map: stage_id → list of new required output fields to add (dedup against existing)
NEW_REQUIRED_FIELDS: dict[str, list[str]] = {
    "4_GENERATE": [
        "innovate_strategies_generated",
        "innovate_not_viable",
        "strategy_count_by_bcg_position",
        "qm_structural_template_applied",
    ],
    "4_STRATEGY_FINANCIAL": ["ceiling_check"],
    "1S0_segmenter": ["tam_provenance", "tam_warning_at_top"],
    "1B_industry_economics": ["tam_provenance", "tam_warning_at_top"],
    "6E_implementation_roadmap": [
        "scope_gate_self_check_passed",
        "forbidden_sentence_count_removed",
    ],
    "1V_validation_report": ["corrections_required"],
    "5_SELECT_final": ["corrections_applied"],
    "6A_decision_memo": ["corrections_applied"],
}


def find_stage(pipeline: dict, stage_id: str) -> dict | None:
    for stages in pipeline["modules"].values():
        for s in stages:
            if s["stage_id"] == stage_id:
                return s
    return None


def apply_patches(pipeline: dict) -> tuple[dict, list[str]]:
    """Apply v9.1 patches in place; return (pipeline, log_lines)."""
    log: list[str] = []

    # Content patches
    for stage_id, patches in STAGE_CONTENT_PATCHES.items():
        stage = find_stage(pipeline, stage_id)
        if stage is None:
            raise RuntimeError(f"Stage not found: {stage_id}")
        for label, text in patches:
            if label in stage["content"]:
                log.append(f"  SKIP  {stage_id} (already patched: {label})")
                continue
            stage["content"] = stage["content"].rstrip() + "\n" + text
            log.append(f"  PATCH {stage_id} += {label}")

    # Required-fields additions
    rf_root = pipeline.setdefault("required_fields_per_stage", {})
    for stage_id, new_fields in NEW_REQUIRED_FIELDS.items():
        existing = rf_root.setdefault(stage_id, [])
        for field in new_fields:
            if field in existing:
                log.append(f"  SKIP  required_fields[{stage_id}].{field} (already present)")
            else:
                existing.append(field)
                log.append(f"  FIELD required_fields[{stage_id}] += {field}")

    # Metadata bump
    meta = pipeline["pipeline_metadata"]
    meta["version"] = "9.1.0"
    meta["updated"] = "2026-05-25"
    meta["description"] = (
        "BCG 5-Lens BU strategy pipeline v9.1 — additive quality patches on v9.0.0. "
        "P1 Innovate mandatory gate · P2 Question Mark 8-floor · P3 Self-derived TAM "
        "warning · P4 TAM-ceiling resolution protocol · P5 GTM Part-V scope gate + V5 "
        "6E↔6B overlap detector · P6 Validation-override propagation checklist. "
        "No structural changes — same 68 stages, 9 modules, 13 gates."
    )
    meta["changelog_v9_1_0"] = (
        "v9.1.0 — 6 quality patches (additive, no structural changes). P1 Innovate "
        "mandatory per-segment (4-engagement pattern: Apple/Samsung/Amkor/Alphabet). "
        "P2 Question Mark 8-strategy floor + structural template. P3 Self-derived TAM "
        "⚠️ NO INDEPENDENT SOURCE warning at top of TAM block. P4 TAM-ceiling resolution "
        "protocol with required field ceiling_check (3-engagement pattern: Micron/Amkor/GFS). "
        "P5 GTM Part-V scope gate on 6E + V5 6E↔6B overlap detector "
        "(5-engagement declining-residual pattern: Samsung→GFS). "
        "P6 Validation-override propagation checklist 1V → 5_SELECT_final → 6A "
        "(Micron/Amkor partial-propagation failures). Cumulative on v9.0.0."
    )
    log.append(f"  META  version → {meta['version']}")
    return pipeline, log


# ─────────────────────────── main ───────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="methodology/pipeline9.json",
                    help="Input pipeline JSON (default: methodology/pipeline9.json)")
    ap.add_argument("--output", default="methodology/pipeline91.json",
                    help="Output JSON path (default: methodology/pipeline91.json)")
    ap.add_argument("--sha256", default=None,
                    help="SHA256 path (default: <output>.sha256)")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    sha_path = Path(args.sha256) if args.sha256 else out_path.with_suffix(".json.sha256")

    if not in_path.exists():
        print(f"❌ input not found: {in_path}", file=sys.stderr)
        return 1

    pipeline = json.loads(in_path.read_text())
    patched, log = apply_patches(pipeline)

    # Write deterministic JSON (sort keys NOT used — preserve insertion order to keep diff small)
    body = json.dumps(patched, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(body)
    digest = hashlib.sha256(body.encode()).hexdigest()
    sha_path.write_text(f"{digest}  {out_path.name}\n")

    by_model = {"haiku": 0, "sonnet": 0, "opus": 0}
    for stages in patched["modules"].values():
        for s in stages:
            by_model[s.get("model", "?")] = by_model.get(s.get("model", "?"), 0) + 1

    print(f"Pipeline v9.1.0 assembled.")
    print(f"  Total stages: {sum(len(v) for v in patched['modules'].values())} (unchanged)")
    print(f"  By model: haiku {by_model['haiku']}, sonnet {by_model['sonnet']}, opus {by_model['opus']}")
    print(f"  v9.1 patches applied:")
    for line in log:
        print(f"    {line}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
