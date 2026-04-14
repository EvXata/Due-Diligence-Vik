#!/usr/bin/env python3
"""
Notion operations for MBB research feedback loop.

Subcommands:
  read-feedback <research_dir>
      → prints JSON: [{"block_id": "...", "text": "..."}, ...]
        (all unchecked to_do blocks on the Feedback page)

  mark-done <research_dir> <block_id> <response_text>
      → checks the to_do block, appends a callout child with the response

  sync-page <research_dir> <stem>
      → deletes all blocks on the mapped Notion page and re-uploads
        the local <stem>.md file content
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
MAX_RICH_TEXT_LENGTH = 2000


# ── Shared utilities ──────────────────────────────────────────────────────────

def get_headers() -> dict:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_request(method: str, url: str, headers: dict, data: dict = None, params: dict = None, retries=3) -> dict:
    for attempt in range(retries):
        resp = requests.request(method, url, headers=headers, json=data, params=params)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2))
            time.sleep(wait)
            continue
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()
    raise RuntimeError(f"Failed after {retries} retries: {url}")


def get_all_children(headers: dict, block_id: str) -> list:
    """Paginated fetch of all direct children of a block/page."""
    results = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = api_request("GET", f"{NOTION_API}/blocks/{block_id}/children",
                           headers, params=params)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return results


def load_meta(research_dir: Path) -> tuple[dict, dict]:
    """Load notion-mapping.json and notion-feedback.json from research dir."""
    mapping_file = research_dir / "notion-mapping.json"
    feedback_file = research_dir / "notion-feedback.json"

    if not mapping_file.exists():
        print(f"Error: notion-mapping.json not found in {research_dir}", file=sys.stderr)
        print("Run /notion-export first to create the Notion pages.", file=sys.stderr)
        sys.exit(1)
    if not feedback_file.exists():
        print(f"Error: notion-feedback.json not found in {research_dir}", file=sys.stderr)
        sys.exit(1)

    with open(mapping_file) as f:
        mapping = json.load(f)
    with open(feedback_file) as f:
        feedback = json.load(f)
    return mapping, feedback


# ── Markdown → Notion blocks (minimal, shared with export script) ─────────────

import re

def split_text(text: str, max_len: int = MAX_RICH_TEXT_LENGTH) -> list[str]:
    return [text[i:i+max_len] for i in range(0, len(text), max_len)] if text else [""]


def parse_inline(text: str) -> list[dict]:
    if len(text) > MAX_RICH_TEXT_LENGTH * 3:
        return [{"type": "text", "text": {"content": c}} for c in split_text(text)]

    result = []
    combined = re.compile(r"(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`|\[[^\]]+\]\([^)]+\))")
    pos = 0
    for m in combined.finditer(text):
        if m.start() > pos:
            for chunk in split_text(text[pos:m.start()]):
                result.append({"type": "text", "text": {"content": chunk}})
        raw = m.group(0)
        if raw.startswith("***") and raw.endswith("***"):
            for chunk in split_text(raw[3:-3]):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"bold": True, "italic": True}})
        elif raw.startswith("**") and raw.endswith("**"):
            for chunk in split_text(raw[2:-2]):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"bold": True}})
        elif raw.startswith("*") and raw.endswith("*"):
            for chunk in split_text(raw[1:-1]):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"italic": True}})
        elif raw.startswith("`") and raw.endswith("`"):
            for chunk in split_text(raw[1:-1]):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"code": True}})
        elif raw.startswith("["):
            lm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", raw)
            if lm:
                for chunk in split_text(lm.group(1)):
                    result.append({"type": "text", "text": {"content": chunk,
                                   "link": {"url": lm.group(2)}}})
        pos = m.end()
    if pos < len(text):
        for chunk in split_text(text[pos:]):
            result.append({"type": "text", "text": {"content": chunk}})
    return result or [{"type": "text", "text": {"content": ""}}]


def markdown_to_blocks(md: str) -> list[dict]:
    blocks = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            for chunk in split_text("\n".join(code_lines)):
                blocks.append({"object": "block", "type": "code",
                                "code": {"rich_text": [{"type": "text", "text": {"content": chunk}}],
                                         "language": lang or "plain text"}})
            i += 1
            continue
        h = re.match(r"^(#{1,3})\s+(.*)", line)
        if h:
            level = min(len(h.group(1)), 3)
            h_type = f"heading_{level}"
            blocks.append({"object": "block", "type": h_type,
                            h_type: {"rich_text": parse_inline(h.group(2))}})
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", line.strip()):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue
        if re.match(r"^[-*+]\s+", line):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": parse_inline(re.sub(r"^[-*+]\s+", "", line))}})
            i += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            blocks.append({"object": "block", "type": "numbered_list_item",
                            "numbered_list_item": {"rich_text": parse_inline(re.sub(r"^\d+\.\s+", "", line))}})
            i += 1
            continue
        if line.startswith("> "):
            blocks.append({"object": "block", "type": "quote",
                            "quote": {"rich_text": parse_inline(line[2:])}})
            i += 1
            continue
        if "|" in line and line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [
                [c.strip() for c in tl.strip().strip("|").split("|")]
                for tl in table_lines
                if not re.match(r"^\|[\s\-:|]+\|", tl)
            ]
            if rows:
                col_count = max(len(r) for r in rows)
                rows = [r + [""] * (col_count - len(r)) for r in rows]
                blocks.append({"object": "block", "type": "table",
                                "table": {"table_width": col_count, "has_column_header": True,
                                          "has_row_header": False,
                                          "children": [{"object": "block", "type": "table_row",
                                                         "table_row": {"cells": [parse_inline(c) for c in row]}}
                                                        for row in rows]}})
            continue
        if line.strip() == "":
            i += 1
            continue
        blocks.append({"object": "block", "type": "paragraph",
                        "paragraph": {"rich_text": parse_inline(line)}})
        i += 1
    return blocks


def append_blocks(headers: dict, page_id: str, blocks: list) -> None:
    for i in range(0, len(blocks), MAX_BLOCKS_PER_REQUEST):
        batch = blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        try:
            api_request("PATCH", f"{NOTION_API}/blocks/{page_id}/children",
                        headers, {"children": batch})
        except Exception as e:
            print(f"  Warning: batch failed: {e}", file=sys.stderr)
            for j, block in enumerate(batch):
                try:
                    api_request("PATCH", f"{NOTION_API}/blocks/{page_id}/children",
                                headers, {"children": [block]})
                except Exception as e2:
                    print(f"  Skipped block {i+j}: {str(e2)[:80]}", file=sys.stderr)
        if i + MAX_BLOCKS_PER_REQUEST < len(blocks):
            time.sleep(0.3)


# ── Subcommands ───────────────────────────────────────────────────────────────

PLACEHOLDER_TEXT = "Write your feedback here — corrections, new facts, context. One topic per paragraph works best."


def cmd_read_feedback(research_dir: Path) -> None:
    """Print JSON list of paragraph blocks from the ⏳ Pending section of the Feedback page."""
    headers = get_headers()
    _, feedback = load_meta(research_dir)
    feedback_page_id = feedback["feedback_page_id"]

    blocks = get_all_children(headers, feedback_page_id)

    # Collect paragraphs between the "⏳ Pending" heading and the next divider/heading
    in_pending = False
    pending = []
    for block in blocks:
        btype = block.get("type")
        if btype == "heading_2":
            heading_text = "".join(
                rt.get("text", {}).get("content", "")
                for rt in block["heading_2"].get("rich_text", [])
            )
            in_pending = "Pending" in heading_text
            continue
        if in_pending and btype == "divider":
            break
        if in_pending and btype in ("heading_1", "heading_2", "heading_3"):
            break
        if in_pending and btype == "paragraph":
            text = "".join(
                rt.get("text", {}).get("content", "")
                for rt in block["paragraph"].get("rich_text", [])
            ).strip()
            if text and text != PLACEHOLDER_TEXT:
                author_id = block.get("created_by", {}).get("id")
                pending.append({
                    "block_id": block["id"],
                    "text": text,
                    "author_id": author_id,
                })

    print(json.dumps(pending, ensure_ascii=False, indent=2))


def cmd_mark_done(research_dir: Path, block_id: str, response_text: str) -> None:
    """Delete the paragraph from Pending and append a response callout to the Completed section."""
    headers = get_headers()
    _, feedback = load_meta(research_dir)
    feedback_page_id = feedback["feedback_page_id"]

    # Read original text before deleting
    block_data = api_request("GET", f"{NOTION_API}/blocks/{block_id}", headers)
    original_text = "".join(
        rt.get("text", {}).get("content", "")
        for rt in (block_data or {}).get("paragraph", {}).get("rich_text", [])
    ).strip()

    # Delete paragraph from Pending section
    api_request("DELETE", f"{NOTION_API}/blocks/{block_id}", headers)

    # Append callout to the feedback page (lands in Completed section at bottom)
    from datetime import date
    today = date.today().strftime("%d.%m.%Y")
    callout = {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": original_text + "\n\n"},
                 "annotations": {"italic": True, "color": "gray"}},
                {"type": "text", "text": {"content": f"✅ {today} — {response_text}"},
                 "annotations": {"bold": True}},
            ],
            "icon": {"type": "emoji", "emoji": "📋"},
            "color": "green_background",
        },
    }
    api_request("PATCH", f"{NOTION_API}/blocks/{feedback_page_id}/children", headers,
                {"children": [callout]})
    print(f"Marked done: {block_id}")


def cmd_sync_page(research_dir: Path, stem: str) -> None:
    """Delete all blocks on the Notion page and re-upload from local .md file."""
    headers = get_headers()
    mapping, _ = load_meta(research_dir)

    page_id = mapping.get(stem)
    if not page_id:
        print(f"Error: '{stem}' not found in notion-mapping.json", file=sys.stderr)
        print(f"Available: {list(mapping.keys())}", file=sys.stderr)
        sys.exit(1)

    # Find local file
    local_file = research_dir / f"{stem}.md"
    if not local_file.exists():
        # Try without extension
        candidates = list(research_dir.glob(f"{stem}*"))
        if not candidates:
            print(f"Error: no file matching '{stem}' in {research_dir}", file=sys.stderr)
            sys.exit(1)
        local_file = candidates[0]

    print(f"Syncing '{stem}' → Notion page {page_id}")

    # Delete existing blocks
    print("  Deleting existing blocks...")
    existing_ids = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = api_request("GET", f"{NOTION_API}/blocks/{page_id}/children",
                           headers, params=params)
        existing_ids.extend(b["id"] for b in data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]

    for bid in existing_ids:
        api_request("DELETE", f"{NOTION_API}/blocks/{bid}", headers)
        time.sleep(0.05)
    print(f"  Deleted {len(existing_ids)} blocks")

    # Re-upload
    content = local_file.read_text(encoding="utf-8")
    blocks = markdown_to_blocks(content)
    print(f"  Uploading {len(blocks)} blocks...")
    append_blocks(headers, page_id, blocks)
    print(f"  Done: https://notion.so/{page_id.replace('-', '')}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    subcmd = sys.argv[1]
    research_dir = Path(sys.argv[2])

    if not research_dir.is_dir():
        # Try prepending research/ base path
        base = Path(__file__).parent.parent.parent.parent / "research"
        alt = base / sys.argv[2]
        if alt.is_dir():
            research_dir = alt
        else:
            print(f"Error: {research_dir} is not a directory", file=sys.stderr)
            sys.exit(1)

    if subcmd == "read-feedback":
        cmd_read_feedback(research_dir)

    elif subcmd == "mark-done":
        if len(sys.argv) < 5:
            print("Usage: notion_ops.py mark-done <research_dir> <block_id> <response_text>")
            sys.exit(1)
        cmd_mark_done(research_dir, sys.argv[3], sys.argv[4])

    elif subcmd == "sync-page":
        if len(sys.argv) < 4:
            print("Usage: notion_ops.py sync-page <research_dir> <stem>")
            sys.exit(1)
        cmd_sync_page(research_dir, sys.argv[3])

    else:
        print(f"Unknown subcommand: {subcmd}")
        print("Available: read-feedback, mark-done, sync-page")
        sys.exit(1)


if __name__ == "__main__":
    main()
