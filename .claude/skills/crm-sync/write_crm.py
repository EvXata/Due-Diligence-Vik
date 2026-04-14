#!/usr/bin/env python3
"""
MBB CRM Write — writes MEDDPICC/Next Actions from crm-update.json to any CRM via Merge.dev.
Works with HubSpot, Salesforce, Pipedrive, and 50+ other CRMs via one unified API.

Usage:
  python3 write_crm.py --data /path/to/crm-update.json --account-token at_xxx

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


def load_update(data_path: str) -> dict:
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_request(method: str, api_key: str, account_token: str,
                  endpoint: str, payload: dict = None):
    ensure_package("requests")
    import requests

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Account-Token": account_token,
        "Content-Type": "application/json",
    }
    url = f"https://api.merge.dev/api/crm/v1/{endpoint}"
    return requests.request(method, url, headers=headers, json=payload)


def write_via_merge(api_key: str, account_token: str, update: dict):
    opp = update.get("opportunity", {})
    meddpicc = update.get("meddpicc", {})
    opp_id = opp.get("opportunity_id") or opp.get("deal_id")

    if not opp_id:
        print("  ⚠️ No opportunity_id in crm-update.json")
        print("     Run /crm-sync --direction pull first to get IDs from CRM")
        return

    # Build opportunity update payload
    model = {}
    if opp.get("stage"):
        model["stage"] = opp["stage"]
    if opp.get("close_date"):
        model["close_date"] = opp["close_date"]
    if opp.get("next_step"):
        model["description"] = opp["next_step"]

    # MEDDPICC fields passed through to native CRM custom fields
    if meddpicc:
        model["integration_params"] = {k: v for k, v in {
            "meddpicc_metrics": meddpicc.get("metrics"),
            "meddpicc_economic_buyer": meddpicc.get("economic_buyer"),
            "meddpicc_decision_criteria": meddpicc.get("decision_criteria"),
            "meddpicc_decision_process": meddpicc.get("decision_process"),
            "meddpicc_paper_process": meddpicc.get("paper_process"),
            "meddpicc_identify_pain": meddpicc.get("identify_pain"),
            "meddpicc_champion": meddpicc.get("champion"),
            "meddpicc_competition": meddpicc.get("competition"),
        }.items() if v}

    if model:
        resp = merge_request(
            "PATCH", api_key, account_token,
            f"opportunities/{opp_id}", {"model": model}
        )
        if resp.status_code in (200, 201):
            print(f"  ✅ Opportunity updated: {opp_id}")
        else:
            print(f"  ⚠️ Update failed: {resp.status_code} — {resp.text[:200]}")

    # Add call summary as a note
    call_summary = update.get("call_summary")
    if call_summary:
        note_model = {
            "content": f"Call Analysis — {datetime.now().strftime('%Y-%m-%d')}\n\n{call_summary}",
            "opportunity": opp_id,
        }
        resp = merge_request("POST", api_key, account_token, "notes", {"model": note_model})
        if resp.status_code in (200, 201):
            print("  ✅ Call note added")
        else:
            print(f"  ⚠️ Note failed: {resp.status_code} — {resp.text[:200]}")

    print("\n✅ Merge.dev write complete")


def main():
    parser = argparse.ArgumentParser(description="MBB CRM Write via Merge.dev")
    parser.add_argument("--data", required=True, help="Path to crm-update.json")
    parser.add_argument("--account-token", required=True,
                        help="Merge.dev account token for this client")
    args = parser.parse_args()

    api_key = os.environ.get("MERGE_API_KEY")
    if not api_key:
        print("ERROR: MERGE_API_KEY not set in .env")
        sys.exit(1)

    if not Path(args.data).exists():
        print(f"ERROR: File not found: {args.data}")
        sys.exit(1)

    print(f"\n📤 MBB CRM Write | Merge.dev | {args.data}\n")
    update = load_update(args.data)
    write_via_merge(api_key, args.account_token, update)


if __name__ == "__main__":
    main()
