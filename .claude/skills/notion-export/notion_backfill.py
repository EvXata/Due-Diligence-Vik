#!/usr/bin/env python3
"""
Backfill notion-mapping.json, notion-feedback.json, and Feedback pages
for research directories that were exported before these features existed.

For each research directory:
1. Finds the matching engagement page under NOTION_MBB_ROOT_PAGE_ID
2. Lists its children to build the file→page_id mapping
3. Creates a "📋 Feedback" child page (skips if already exists)
4. Saves notion-mapping.json and notion-feedback.json locally

Usage:
    python3 notion_backfill.py                          # all research dirs
    python3 notion_backfill.py tsmc-30.03.2026 nvidia-24.03.2026  # specific dirs
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
MAX_BLOCKS_PER_REQUEST = 100

SKILLS_DIR = Path(__file__).parent
RESEARCH_DIR = SKILLS_DIR.parent.parent.parent / "research"


def get_headers() -> dict:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN not set")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_get(url: str, headers: dict, params: dict = None) -> dict:
    for attempt in range(3):
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            time.sleep(int(resp.headers.get("Retry-After", 2)))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"GET failed: {url}")


def api_post(url: str, headers: dict, data: dict) -> dict:
    for attempt in range(3):
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 429:
            time.sleep(int(resp.headers.get("Retry-After", 2)))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"POST failed: {url}")


def api_patch(url: str, headers: dict, data: dict) -> dict:
    for attempt in range(3):
        resp = requests.patch(url, headers=headers, json=data)
        if resp.status_code == 429:
            time.sleep(int(resp.headers.get("Retry-After", 2)))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"PATCH failed: {url}")


def get_all_children(headers: dict, block_id: str) -> list:
    results = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = api_get(f"{NOTION_API}/blocks/{block_id}/children", headers, params)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return results


def dir_to_title(dir_name: str) -> str:
    """Reproduce the title formula from export_to_notion.py."""
    parts = dir_name.split("-", 1)
    company = parts[0].upper() if len(parts[0]) <= 4 else parts[0].capitalize()
    date_part = parts[1] if len(parts) > 1 else dir_name
    return f"{company} — MBB Engagement ({date_part})"


def find_engagement_page(headers: dict, root_id: str, dir_name: str) -> str | None:
    """Find the Notion page ID for a research dir by matching title."""
    expected_title = dir_to_title(dir_name)
    children = get_all_children(headers, root_id)
    for block in children:
        if block.get("type") == "child_page":
            title = block["child_page"]["title"]
            if title == expected_title:
                return block["id"]
    # Fallback: case-insensitive partial match on company name
    company = dir_name.split("-")[0].lower()
    for block in children:
        if block.get("type") == "child_page":
            title = block["child_page"]["title"].lower()
            if company in title and "bcg engagement" in title:
                print(f"  Fuzzy match: '{block['child_page']['title']}'")
                return block["id"]
    return None


def create_feedback_page(headers: dict, parent_page_id: str) -> str:
    """Create 📋 Feedback page under parent with template content."""
    data = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": "📋 Feedback"}}]}
        },
    }
    result = api_post(f"{NOTION_API}/pages", headers, data)
    page_id = result["id"]

    template_blocks = [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content":
                    "Use this page to send feedback and corrections to the Xata&Co analytics team. "
                    "Write in free form below — the team will process it within the next hour."}}],
                "icon": {"type": "emoji", "emoji": "📋"},
                "color": "blue_background",
            },
        },
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "⏳ Pending"}}]},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "Write your feedback here — corrections, new facts, context. One topic per paragraph works best."},
                               "annotations": {"color": "gray", "italic": True}}],
            },
        },
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ Completed"}}]},
        },
    ]

    for i in range(0, len(template_blocks), MAX_BLOCKS_PER_REQUEST):
        batch = template_blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        api_patch(f"{NOTION_API}/blocks/{page_id}/children", headers, {"children": batch})

    return page_id


def process_research_dir(headers: dict, root_id: str, research_dir: Path) -> bool:
    dir_name = research_dir.name
    print(f"\n{'─' * 50}")
    print(f"Processing: {dir_name}")

    # Skip if already done
    if (research_dir / "notion-mapping.json").exists() and \
       (research_dir / "notion-feedback.json").exists():
        print("  Already has mapping + feedback — skipping")
        return True

    # Find engagement page
    engagement_page_id = find_engagement_page(headers, root_id, dir_name)
    if not engagement_page_id:
        print(f"  ERROR: Could not find Notion page for '{dir_to_title(dir_name)}'")
        return False
    print(f"  Found engagement page: {engagement_page_id}")

    # Build mapping from existing child pages
    children = get_all_children(headers, engagement_page_id)
    mapping = {}
    feedback_page_id = None

    for block in children:
        if block.get("type") == "child_page":
            title = block["child_page"]["title"]
            if title == "📋 Feedback":
                feedback_page_id = block["id"]
                print(f"  Feedback page already exists: {feedback_page_id}")
            else:
                mapping[title] = block["id"]

    print(f"  Mapped {len(mapping)} research pages")

    # Create Feedback page if missing
    if not feedback_page_id:
        print("  Creating Feedback page...")
        feedback_page_id = create_feedback_page(headers, engagement_page_id)
        print(f"  Feedback page created: {feedback_page_id}")

    # Save JSON files
    with open(research_dir / "notion-mapping.json", "w") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    with open(research_dir / "notion-feedback.json", "w") as f:
        json.dump({
            "feedback_page_id": feedback_page_id,
            "engagement_page_id": engagement_page_id,
        }, f, indent=2)

    print(f"  Saved notion-mapping.json ({len(mapping)} entries) + notion-feedback.json")
    return True


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN not set")
        sys.exit(1)

    root_id = os.environ.get("NOTION_MBB_ROOT_PAGE_ID")
    if not root_id:
        print("Error: NOTION_MBB_ROOT_PAGE_ID not set")
        sys.exit(1)

    headers = get_headers()

    # Determine which dirs to process
    if len(sys.argv) > 1:
        dirs = []
        for arg in sys.argv[1:]:
            d = Path(arg) if Path(arg).is_dir() else RESEARCH_DIR / arg
            if d.is_dir():
                dirs.append(d)
            else:
                print(f"Warning: directory not found: {arg}")
    else:
        dirs = sorted(d for d in RESEARCH_DIR.iterdir() if d.is_dir())

    print(f"Processing {len(dirs)} research directories...")

    ok, failed = [], []
    for d in dirs:
        success = process_research_dir(headers, root_id, d)
        (ok if success else failed).append(d.name)
        time.sleep(0.5)  # be gentle with API

    print(f"\n{'═' * 50}")
    print(f"Done: {len(ok)} succeeded, {len(failed)} failed")
    if failed:
        print("Failed:")
        for name in failed:
            print(f"  • {name}")


if __name__ == "__main__":
    main()
