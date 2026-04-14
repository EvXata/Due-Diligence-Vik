#!/usr/bin/env python3
"""
MBB CRM Fetch — pulls contacts, accounts, opportunities from any CRM via Merge.dev.
Works with HubSpot, Salesforce, Pipedrive, and 50+ other CRMs via one unified API.

Usage:
  python3 fetch_crm.py --dir /path/to/research/company-date --account-token at_xxx

Requires in .env:
  MERGE_API_KEY=your_merge_api_key
"""

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def ensure_package(package_name: str, import_name: str = None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name, "-q"],
            check=True
        )


def merge_get_all(api_key: str, account_token: str, endpoint: str) -> list:
    """Fetch all pages from a Merge CRM endpoint."""
    ensure_package("requests")
    import requests

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Account-Token": account_token,
    }
    url = f"https://api.merge.dev/api/crm/v1/{endpoint}"
    results = []
    params = {"page_size": 100}

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"  ⚠️ {endpoint}: {response.status_code} — {response.text[:200]}")
            break
        data = response.json()
        results.extend(data.get("results", []))
        cursor = data.get("next")
        if not cursor:
            break
        params = {"page_size": 100, "cursor": cursor}

    return results


def fetch_via_merge(api_key: str, account_token: str) -> dict:
    results = {}

    print("Fetching contacts...")
    results["contacts"] = merge_get_all(api_key, account_token, "contacts")
    print(f"  ✅ Contacts: {len(results['contacts'])}")

    print("Fetching accounts...")
    results["accounts"] = merge_get_all(api_key, account_token, "accounts")
    print(f"  ✅ Accounts: {len(results['accounts'])}")

    print("Fetching opportunities...")
    results["opportunities"] = merge_get_all(api_key, account_token, "opportunities")
    print(f"  ✅ Opportunities: {len(results['opportunities'])}")

    print("Fetching notes...")
    results["notes"] = merge_get_all(api_key, account_token, "notes")
    print(f"  ✅ Notes: {len(results['notes'])}")

    return results


def save_results(results: dict, output_dir: Path):
    crm_dir = output_dir / "crm-data"
    crm_dir.mkdir(exist_ok=True)

    for key, data in results.items():
        filepath = crm_dir / f"{key}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"  Saved: crm-data/{key}.json ({len(data)} records)")

    summary = {
        "fetched_at": datetime.now().isoformat(),
        "provider": "merge.dev",
        "records": {k: len(v) for k, v in results.items()},
    }
    with open(crm_dir / "fetch-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ CRM data saved to: {crm_dir}")


def main():
    parser = argparse.ArgumentParser(description="MBB CRM Fetch via Merge.dev")
    parser.add_argument("--dir", required=True, help="Engagement directory path")
    parser.add_argument("--account-token", required=True,
                        help="Merge.dev account token for this client")
    args = parser.parse_args()

    api_key = os.environ.get("MERGE_API_KEY")
    if not api_key:
        print("ERROR: MERGE_API_KEY not set in .env")
        sys.exit(1)

    output_dir = Path(args.dir)
    if not output_dir.exists():
        print(f"ERROR: Directory not found: {output_dir}")
        sys.exit(1)

    print(f"\n🔄 MBB CRM Fetch | Merge.dev | {output_dir}\n")

    results = fetch_via_merge(api_key, args.account_token)
    save_results(results, output_dir)


if __name__ == "__main__":
    main()
