#!/usr/bin/env bash
# phase-gate.sh — verify that expected output files exist for a given DD phase.
# Returns 0 if all expected files are present and non-empty (>2KB);
# returns 1 with a MISSING:<file> list otherwise.
#
# Usage:
#   phase-gate.sh <phase-name> <output-dir> [segment-slugs...]
#
# Phase names: phase-minus-1 | phase-0 | phase-1 | phase-1.5 | phase-2-dd-2 | phase-dd-3a | phase-dd-3b | phase-dd-3c | phase-dd-4
# segment-slugs (optional, phase-1 only): comma-separated list of expected segment filenames
#
# Examples:
#   phase-gate.sh phase-minus-1 /path/to/research/nvidia-20.05.2026
#   phase-gate.sh phase-1 /path/to/research/nvidia-20.05.2026 data-center,gaming,pro-viz,automotive
#   phase-gate.sh phase-1.5 /path/to/research/nvidia-20.05.2026

set -u

PHASE="${1:-}"
OUTPUT_DIR="${2:-}"
SEGMENTS="${3:-}"
MIN_BYTES=2048

if [ -z "$PHASE" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: phase-gate.sh <phase-name> <output-dir> [segment-slugs]" >&2
  exit 2
fi

if [ ! -d "$OUTPUT_DIR" ]; then
  echo "MISSING: output directory $OUTPUT_DIR does not exist" >&2
  exit 1
fi

# Per-phase expected files
case "$PHASE" in
  phase-minus-1)
    EXPECTED="company-brief.md"
    ;;
  phase-0)
    EXPECTED="market-map.md advanced-analytics.md"
    OPTIONAL="advanced-analytics.md"
    ;;
  phase-1-launch)
    # PRE-flight check: validate orchestrator about to launch right N+1 agent batch.
    # Prevents bug B1 (Cursor DD 19.05.2026 missed S4 segment in batch — cost 46 min).
    # Usage: phase-gate.sh phase-1-launch <output-dir> <expected-N>
    if [ -z "${SEGMENTS:-}" ]; then
      echo "Usage: phase-gate.sh phase-1-launch <output-dir> <expected-N>" >&2
      exit 2
    fi
    EXPECTED_COUNT="$SEGMENTS"
    if [ ! -f "$OUTPUT_DIR/market-map.md" ]; then
      echo "FAIL: phase-1-launch — market-map.md missing, cannot validate" >&2
      exit 1
    fi
    # Extract UNIQUE segment IDs (S1, S2, etc) that are NOT marked Tier-2 EXCLUDED.
    # Matches rows starting with "| S<digit>:" and excludes EXCLUDED / shut-down segments.
    PARSED_COUNT=$(grep -oE "^\| S[0-9]+:" "$OUTPUT_DIR/market-map.md" 2>/dev/null | \
                    sort -u | wc -l | tr -d ' ')
    # Subtract excluded segments (rows containing EXCLUDED in priority column)
    EXCLUDED_COUNT=$(grep -cE "^\| S[0-9]+:.*EXCLUDED" "$OUTPUT_DIR/market-map.md" 2>/dev/null | head -1 || echo 0)
    # ID-based dedup: get distinct S<n>: prefixes that aren't excluded
    PARSED_COUNT=$(grep -oE "^\| S[0-9]+:" "$OUTPUT_DIR/market-map.md" 2>/dev/null | sort -u | wc -l | tr -d ' ')
    if [ "$EXCLUDED_COUNT" -gt 0 ]; then
      PARSED_COUNT=$((PARSED_COUNT - EXCLUDED_COUNT))
    fi
    # Fallback: heading-based count
    if [ "$PARSED_COUNT" -eq 0 ]; then
      PARSED_COUNT=$(grep -cE "^## \[?(СЕГМЕНТ|Segment|S[0-9])" "$OUTPUT_DIR/market-map.md" 2>/dev/null || echo 0)
    fi
    if [ "$PARSED_COUNT" -eq 0 ]; then
      echo "WARN: phase-1-launch — could not parse segment count from market-map.md; orchestrator should verify manually" >&2
      echo "OK (warning): phase-1-launch — count parsing inconclusive, proceed with care"
      exit 0
    fi
    if [ "$EXPECTED_COUNT" != "$PARSED_COUNT" ]; then
      echo "FAIL: phase-1-launch — segment count mismatch"
      echo "  Orchestrator plans to launch: $EXPECTED_COUNT segment agents (+ 1 domain-expert)"
      echo "  market-map.md contains: $PARSED_COUNT segments"
      echo "  Action: re-enumerate segments before launching Phase 1 batch."
      exit 1
    fi
    echo "OK: phase-1-launch — $PARSED_COUNT segments enumerated, batch of $(($EXPECTED_COUNT + 1)) agents authorized"
    exit 0
    ;;
  phase-1)
    if [ -z "$SEGMENTS" ]; then
      # Fallback: any segment-*.md file is OK
      count=$(ls "$OUTPUT_DIR"/segment-*.md 2>/dev/null | wc -l | tr -d ' ')
      if [ "$count" -eq 0 ]; then
        echo "MISSING: no segment-*.md files found in $OUTPUT_DIR"
        exit 1
      fi
      echo "OK: phase-1 ($count segment files found)"
      exit 0
    fi
    EXPECTED=""
    IFS=',' read -ra SLUGS <<< "$SEGMENTS"
    for slug in "${SLUGS[@]}"; do
      EXPECTED="$EXPECTED segment-${slug}.md"
    done
    EXPECTED="$EXPECTED domain-expert-input.md"
    OPTIONAL="domain-expert-input.md"
    ;;
  phase-1.5 | phase-dd-1)
    EXPECTED="validation-report.md dd-market-validation.md dd-hypothesis-report.md"
    ;;
  phase-2-dd-2 | phase-2)
    EXPECTED="portfolio.md dd-risk-matrix.md dd-red-team.md"
    ;;
  phase-dd-3a)
    # master-anchors.json is the canonical extract for Haiku derives in DD-3b.
    # If missing, dd-production-summary / dd-production silently degrade to
    # reconstruction from supporting files (bug B3 observed on Cursor DD).
    EXPECTED="dd-decision-first.md master-anchors.json"
    ;;
  phase-dd-3b)
    EXPECTED="dd-mid.md dd-short.md dd-report.md"
    ;;
  phase-dd-3c)
    # Investor-profile synthesis trio. All three are additive — degradation
    # is non-blocking (the standard 4 decision layers carry the verdict).
    EXPECTED="bull-case.md customer-discovery.md ma-exit-scenarios.md"
    OPTIONAL="bull-case.md customer-discovery.md ma-exit-scenarios.md"
    ;;
  phase-dd-4)
    EXPECTED="notion-mapping.json notion-feedback.json"
    OPTIONAL="notion-feedback.json"
    ;;
  *)
    echo "Unknown phase: $PHASE" >&2
    echo "Valid: phase-minus-1 phase-0 phase-1 phase-1.5 phase-2-dd-2 phase-dd-3a phase-dd-3b phase-dd-3c phase-dd-4" >&2
    exit 2
    ;;
esac

OPTIONAL="${OPTIONAL:-}"
MISSING=""
DEGRADED=""

for f in $EXPECTED; do
  path="$OUTPUT_DIR/$f"
  size=0
  if [ -f "$path" ]; then
    if stat -f%z "$path" >/dev/null 2>&1; then
      size=$(stat -f%z "$path")
    else
      size=$(stat -c%s "$path")
    fi
  fi

  if [ "$size" -lt "$MIN_BYTES" ]; then
    if echo " $OPTIONAL " | grep -q " $f "; then
      DEGRADED="$DEGRADED $f"
    else
      MISSING="$MISSING $f"
    fi
  fi
done

if [ -n "$MISSING" ]; then
  echo "FAIL: phase $PHASE has missing/empty blocking files:"
  for f in $MISSING; do
    path="$OUTPUT_DIR/$f"
    if [ -f "$path" ]; then
      echo "  MISSING: $f (file exists but <${MIN_BYTES} bytes — likely killed mid-Write)"
    else
      echo "  MISSING: $f (file not created — agent failed before Write)"
    fi
  done
  if [ -n "$DEGRADED" ]; then
    echo "DEGRADED (non-blocking):"
    for f in $DEGRADED; do
      echo "  DEGRADED: $f"
    done
  fi
  exit 1
fi

if [ -n "$DEGRADED" ]; then
  echo "OK (degraded): phase $PHASE — blocking files present; non-blocking files missing:"
  for f in $DEGRADED; do
    echo "  DEGRADED: $f"
  done
  exit 0
fi

echo "OK: phase $PHASE — all expected files present (>${MIN_BYTES} bytes)"
exit 0
