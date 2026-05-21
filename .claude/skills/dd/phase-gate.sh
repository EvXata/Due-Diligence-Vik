#!/usr/bin/env bash
# phase-gate.sh — verify that expected output files exist for a given DD phase.
# Returns 0 if all expected files are present and non-empty (>2KB);
# returns 1 with a MISSING:<file> list otherwise.
#
# Usage:
#   phase-gate.sh <phase-name> <output-dir> [segment-slugs...]
#
# Phase names: phase-minus-1 | phase-0 | phase-1 | phase-1.5 | phase-2-dd-2 | phase-dd-3a | phase-dd-3b | phase-dd-4
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
    EXPECTED="dd-decision-first.md"
    ;;
  phase-dd-3b)
    EXPECTED="dd-mid.md dd-short.md dd-report.md"
    ;;
  phase-dd-4)
    EXPECTED="notion-mapping.json notion-feedback.json"
    OPTIONAL="notion-feedback.json"
    ;;
  *)
    echo "Unknown phase: $PHASE" >&2
    echo "Valid: phase-minus-1 phase-0 phase-1 phase-1.5 phase-2-dd-2 phase-dd-3a phase-dd-3b phase-dd-4" >&2
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
