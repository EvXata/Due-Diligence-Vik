#!/usr/bin/env python3
"""Build a conservative DD GTM discovery vector from research artifacts.

This script is intentionally light-touch: it detects product presence and
extracts obvious metadata from engagement logs / dd-short files. The curated
files in gtm-discovery remain the GTM source of truth until payment + CRM data
exist.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUT = ROOT / "gtm-discovery"


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return " ".join(match.group(1).strip().split())
    return ""


def has_any(folder: Path, names: list[str]) -> bool:
    return any((folder / name).exists() for name in names)


def ordered_products(folder: Path) -> list[str]:
    products: list[str] = []
    if has_any(folder, ["dd-red-team.md", "dd-breakup-short.md", "dd-breakup-bidding-war.md"]):
        products.append("bear_case")
    if has_any(folder, ["bull-case.md"]):
        products.append("bull_case")
    if has_any(folder, ["dd-decision-first.md"]):
        products.append("deep_audit")
    if has_any(folder, ["dd-short.md"]) and "deep_audit" not in products:
        products.append("fast_short")
    return products


def row_for(folder: Path) -> dict[str, object] | None:
    products = ordered_products(folder)
    if not products and not (folder / "dd-engagement.log").exists():
        return None

    log = read(folder / "dd-engagement.log") + "\n" + read(folder / "dd-short-engagement.log")
    short = read(folder / "dd-short.md")
    combined = log + "\n" + short

    verdict = first_match(combined, [r"^Verdict:\s+(.+)$", r"^Вердикт:\s+(.+)$"])
    confidence = first_match(combined, [r"^Confidence:\s+([0-9]+%?.*)$", r"^Уверенность:\s+([0-9]+%?.*)$"])
    deal_score = first_match(combined, [r"^Deal Score:\s+(.+)$", r"^Оценка сделки:\s+(.+)$"])
    deal_type = first_match(log, [r"^Deal Type:\s+(.+)$"])
    asking = first_match(log, [r"^Asking Price:\s+(.+)$", r"^Token Price:\s+(.+)$"])
    fair_value = first_match(log, [r"^Fair Value Range:\s+(.+)$"])
    hypothesis = first_match(log, [r"^Hypothesis Score:\s+(.+)$"])

    eligible = bool({"bear_case", "bull_case", "deep_audit", "fast_short"} & set(products))
    if not eligible:
        products = []

    return {
        "deal_id": folder.name,
        "source_dir": str(folder.relative_to(ROOT)),
        "ordered_products": products,
        "bear_case": "bear_case" in products,
        "bull_case": "bull_case" in products,
        "deep_audit": "deep_audit" in products,
        "fast_short": "fast_short" in products,
        "deal_type": deal_type,
        "asking_price": asking,
        "verdict": verdict or "PARTIAL_PIPELINE",
        "confidence": confidence,
        "deal_score": deal_score,
        "fair_value": fair_value,
        "hypothesis_score": hypothesis,
        "tournament_eligible": eligible,
    }


def main() -> None:
    rows = [row for folder in sorted(RESEARCH.iterdir()) if folder.is_dir() for row in [row_for(folder)] if row]
    OUT.mkdir(exist_ok=True)

    json_path = OUT / "dd-deal-vector.generated.json"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    csv_path = OUT / "dd-deal-vector.generated.csv"
    fieldnames = [
        "deal_id",
        "source_dir",
        "ordered_products",
        "bear_case",
        "bull_case",
        "deep_audit",
        "fast_short",
        "deal_type",
        "asking_price",
        "verdict",
        "confidence",
        "deal_score",
        "fair_value",
        "hypothesis_score",
        "tournament_eligible",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row = dict(row)
            row["ordered_products"] = "|".join(row["ordered_products"])
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {json_path.relative_to(ROOT)} and {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
