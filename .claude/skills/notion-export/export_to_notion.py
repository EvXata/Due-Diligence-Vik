#!/usr/bin/env python3
"""
Export research files to Notion. Idempotent: re-running updates existing pages
instead of creating duplicates.

Each file → one Notion child page under the engagement parent page.

Idempotency model:
  • On first run, creates a page per file and writes notion-mapping.json
    ({"filename_stem": "<page_id>"}) plus notion-feedback.json (engagement +
    feedback page IDs).
  • On subsequent runs, reads notion-mapping.json. For each file:
      - if its saved page is alive (not archived) → WIPES blocks + re-uploads
        content in place. Page ID is preserved. Old Notion links keep working.
      - if the saved page is archived/missing → creates a new page.
      - if a file is new (not in mapping) → creates a new page.
  • The Feedback page ID and engagement page ID survive across runs too
    (saved in notion-feedback.json; only recreated if archived).

Usage:
    NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

    # Force fresh pages (ignore prior mapping — intentional rebuild):
    NOTION_FORCE_CREATE=1 NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

    # Explicit parent page override (rarely needed — auto-detected from saved state):
    NOTION_PARENT_PAGE_ID=<page_id> NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

    # Subset upload via whitelist:
    NOTION_FILES_WHITELIST=dd-short.md,dd-mid.md python3 export_to_notion.py <research_dir>
"""

import os
import sys
import re
import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Notion limits
MAX_BLOCKS_PER_REQUEST = 100
MAX_RICH_TEXT_LENGTH = 2000


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_request(method: str, url: str, headers: dict, data: dict = None, retries=3) -> dict:
    for attempt in range(retries):
        resp = requests.request(method, url, headers=headers, json=data)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2))
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code not in (200, 201):
            print(f"  API error {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Failed after {retries} retries")


def split_text(text: str, max_len: int = MAX_RICH_TEXT_LENGTH) -> list[str]:
    """Split text into chunks of max_len characters."""
    return [text[i:i+max_len] for i in range(0, len(text), max_len)] if text else [""]


def text_to_rich_text(text: str) -> list[dict]:
    """Convert a text string to Notion rich_text array (chunked)."""
    return [{"type": "text", "text": {"content": chunk}} for chunk in split_text(text)]


def parse_inline(text: str) -> list[dict]:
    """Parse inline markdown (bold, italic, code, links) into rich_text."""
    # Simple approach: detect **bold**, *italic*, `code`, [text](url)
    # For very long strings, fall back to plain chunking
    if len(text) > MAX_RICH_TEXT_LENGTH * 3:
        return text_to_rich_text(text)

    result = []
    patterns = [
        ("bold_italic", r"\*\*\*(.*?)\*\*\*"),
        ("bold",        r"\*\*(.*?)\*\*"),
        ("italic",      r"\*(.*?)\*"),
        ("code",        r"`(.*?)`"),
        ("link",        r"\[([^\]]+)\]\(([^)]+)\)"),
    ]

    pos = 0
    combined = re.compile(
        r"(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`|\[[^\]]+\]\([^)]+\))"
    )

    for m in combined.finditer(text):
        # Plain text before match
        if m.start() > pos:
            for chunk in split_text(text[pos:m.start()]):
                result.append({"type": "text", "text": {"content": chunk}})

        raw = m.group(0)
        if raw.startswith("***") and raw.endswith("***"):
            inner = raw[3:-3]
            for chunk in split_text(inner):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"bold": True, "italic": True}})
        elif raw.startswith("**") and raw.endswith("**"):
            inner = raw[2:-2]
            for chunk in split_text(inner):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"bold": True}})
        elif raw.startswith("*") and raw.endswith("*"):
            inner = raw[1:-1]
            for chunk in split_text(inner):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"italic": True}})
        elif raw.startswith("`") and raw.endswith("`"):
            inner = raw[1:-1]
            for chunk in split_text(inner):
                result.append({"type": "text", "text": {"content": chunk},
                                "annotations": {"code": True}})
        elif raw.startswith("["):
            link_m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", raw)
            if link_m:
                label, url = link_m.group(1), link_m.group(2)
                for chunk in split_text(label):
                    result.append({"type": "text", "text": {"content": chunk, "link": {"url": url}}})

        pos = m.end()

    if pos < len(text):
        for chunk in split_text(text[pos:]):
            result.append({"type": "text", "text": {"content": chunk}})

    return result if result else [{"type": "text", "text": {"content": ""}}]


def markdown_to_blocks(md: str) -> list[dict]:
    """Convert markdown text to Notion block objects."""
    blocks = []
    lines = md.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            # Notion code blocks max 2000 chars — split into multiple if needed
            for chunk in split_text(code_text, MAX_RICH_TEXT_LENGTH):
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                        "language": lang if lang else "plain text",
                    }
                })
            i += 1
            continue

        # Headings
        h_match = re.match(r"^(#{1,3})\s+(.*)", line)
        if h_match:
            level = len(h_match.group(1))
            text = h_match.group(2)
            h_type = {1: "heading_1", 2: "heading_2", 3: "heading_3"}[min(level, 3)]
            blocks.append({
                "object": "block",
                "type": h_type,
                h_type: {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", line.strip()):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Bulleted list
        if re.match(r"^[-*+]\s+", line):
            text = re.sub(r"^[-*+]\s+", "", line)
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s+", line):
            text = re.sub(r"^\d+\.\s+", "", line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            text = line[2:]
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Table — collect all table rows
        if "|" in line and line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1

            # Parse table: skip separator row (---|---|...)
            rows = []
            for tl in table_lines:
                if re.match(r"^\|[\s\-:|]+\|", tl):
                    continue
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)

            if rows:
                col_count = max(len(r) for r in rows)
                # Normalize
                rows = [r + [""] * (col_count - len(r)) for r in rows]

                blocks.append({
                    "object": "block",
                    "type": "table",
                    "table": {
                        "table_width": col_count,
                        "has_column_header": True,
                        "has_row_header": False,
                        "children": [
                            {
                                "object": "block",
                                "type": "table_row",
                                "table_row": {
                                    "cells": [parse_inline(cell) for cell in row]
                                }
                            }
                            for row in rows
                        ]
                    }
                })
            continue

        # Empty line → empty paragraph (skip multiple blank lines)
        if line.strip() == "":
            # Don't add multiple blank paragraphs
            if blocks and blocks[-1].get("type") != "paragraph" or \
               (blocks and blocks[-1].get("type") == "paragraph" and
                blocks[-1].get("paragraph", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "x") != ""):
                pass  # skip blank lines silently
            i += 1
            continue

        # Plain paragraph
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": parse_inline(line)}
        })
        i += 1

    return blocks


def create_page(headers: dict, parent_id: str, title: str) -> str:
    """Create a Notion page under parent_id and return its ID."""
    parent = {"type": "page_id", "page_id": parent_id}

    data = {
        "parent": parent,
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
    }

    result = api_request("POST", f"{NOTION_API}/pages", headers, data)
    return result["id"]


def append_blocks(headers: dict, page_id: str, blocks: list[dict]) -> None:
    """Append blocks to a page in batches of MAX_BLOCKS_PER_REQUEST."""
    # Flatten table children — tables need special handling
    # Tables with children must be created with children in the initial block
    # We send them as-is since they're nested

    for i in range(0, len(blocks), MAX_BLOCKS_PER_REQUEST):
        batch = blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        data = {"children": batch}
        try:
            api_request("PATCH", f"{NOTION_API}/blocks/{page_id}/children", headers, data)
        except Exception as e:
            print(f"    Warning: batch {i//MAX_BLOCKS_PER_REQUEST + 1} failed: {e}")
            # Try sending blocks one-by-one to isolate the problematic block
            for j, block in enumerate(batch):
                try:
                    api_request("PATCH", f"{NOTION_API}/blocks/{page_id}/children",
                                headers, {"children": [block]})
                except Exception as e2:
                    print(f"    Skipped block {i+j}: {str(e2)[:100]}")

        if i + MAX_BLOCKS_PER_REQUEST < len(blocks):
            time.sleep(0.3)  # Be gentle with rate limits


def page_is_alive(headers: dict, page_id: str) -> bool:
    """Return True if page exists and is not archived. False on any error or archived."""
    try:
        page = api_request("GET", f"{NOTION_API}/pages/{page_id}", headers)
        return not page.get("archived", False)
    except Exception:
        return False


def export_file(headers: dict, parent_page_id: str, filepath: Path,
                existing_page_id: Optional[str] = None) -> str:
    """Read a file and upload to Notion. Returns the page_id.

    If existing_page_id is provided and the page is alive, UPDATES in place
    (wipes existing blocks, re-appends) — idempotent. Otherwise creates new.
    """
    print(f"  Exporting: {filepath.name}")

    content = filepath.read_text(encoding="utf-8")
    title = filepath.stem  # filename without extension

    page_id = None
    if existing_page_id and page_is_alive(headers, existing_page_id):
        page_id = existing_page_id
        print(f"    Reusing existing page: {title} ({page_id}) — wiping blocks")
        delete_all_blocks(headers, page_id)
    else:
        if existing_page_id:
            print(f"    Saved page {existing_page_id} not alive; creating new")
        page_id = create_page(headers, parent_page_id, title)
        print(f"    Created page: {title} ({page_id})")

    # Convert to blocks
    blocks = markdown_to_blocks(content)
    print(f"    Blocks: {len(blocks)}, appending...")

    # Append all blocks
    append_blocks(headers, page_id, blocks)
    print(f"    Done: {len(blocks)} blocks uploaded")

    return page_id


def get_all_block_ids(headers: dict, block_id: str) -> list[str]:
    """Get all direct children block IDs of a page/block (paginated)."""
    ids = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = requests.get(
            f"{NOTION_API}/blocks/{block_id}/children",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()
        ids.extend(b["id"] for b in data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return ids


def delete_all_blocks(headers: dict, page_id: str) -> None:
    """Delete all blocks on a page."""
    ids = get_all_block_ids(headers, page_id)
    for block_id in ids:
        try:
            requests.delete(f"{NOTION_API}/blocks/{block_id}", headers=headers)
            time.sleep(0.05)
        except Exception as e:
            print(f"    Warning: could not delete block {block_id}: {e}")


def create_feedback_page(headers: dict, parent_page_id: str) -> str:
    """Create the 📋 Feedback page with instructions template."""
    page_id = create_page(headers, parent_page_id, "📋 Feedback")

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
    append_blocks(headers, page_id, template_blocks)
    return page_id


def save_notion_meta(research_dir: Path, mapping: dict, feedback_page_id: str, engagement_page_id: str) -> None:
    """Save page ID mapping and feedback page info to the research directory."""
    with open(research_dir / "notion-mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)
    with open(research_dir / "notion-feedback.json", "w") as f:
        json.dump({
            "feedback_page_id": feedback_page_id,
            "engagement_page_id": engagement_page_id,
        }, f, indent=2)
    print(f"Saved notion-mapping.json and notion-feedback.json")


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: set NOTION_TOKEN environment variable")
        print("  Get it at: https://www.notion.so/my-integrations")
        sys.exit(1)

    if len(sys.argv) < 2:
        print(f"Usage: NOTION_TOKEN=secret_xxx python3 {sys.argv[0]} <research_dir>")
        sys.exit(1)

    research_dir = Path(sys.argv[1])
    if not research_dir.is_dir():
        print(f"Error: {research_dir} is not a directory")
        sys.exit(1)

    headers = get_headers(token)

    # Find all files (md + log), sorted
    files = sorted(research_dir.glob("*"))
    files = [f for f in files if f.is_file() and f.suffix in (".md", ".log", ".txt")]
    print(f"Found {len(files)} files in {research_dir}")

    # Optional whitelist (env NOTION_FILES_WHITELIST="dd-short.md,dd-mid.md,...")
    whitelist_raw = os.environ.get("NOTION_FILES_WHITELIST", "").strip()
    if whitelist_raw:
        allowed = {name.strip() for name in whitelist_raw.split(",") if name.strip()}
        missing = allowed - {f.name for f in files}
        files = [f for f in files if f.name in allowed]
        if missing:
            print(f"Warning: whitelist entries not found in directory: {sorted(missing)}")
        print(f"Whitelist applied: {len(files)} files match ({sorted(f.name for f in files)})")
        if not files:
            print("Error: whitelist matched zero files — nothing to export")
            sys.exit(2)

    # Determine parent page for file pages.
    # Priority order:
    #   1. NOTION_PARENT_PAGE_ID env var (explicit override — always wins)
    #   2. engagement_page_id saved in notion-feedback.json from a previous run (auto-reuse)
    #   3. Create a new engagement page under NOTION_MBB_ROOT_PAGE_ID (first run)
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    if parent_page_id:
        print(f"Using existing parent page (env override): {parent_page_id}")
    else:
        # Try to auto-detect from previous run
        feedback_meta_path = research_dir / "notion-feedback.json"
        if feedback_meta_path.exists():
            try:
                with open(feedback_meta_path) as f:
                    saved = json.load(f)
                saved_engagement = saved.get("engagement_page_id")
                if saved_engagement:
                    # Verify the page still exists and is not archived
                    try:
                        verify = api_request("GET", f"{NOTION_API}/pages/{saved_engagement}", get_headers(token))
                        if not verify.get("archived", False):
                            parent_page_id = saved_engagement
                            print(f"Auto-detected engagement page from notion-feedback.json: {parent_page_id}")
                    except Exception as e:
                        print(f"  Saved engagement page {saved_engagement} no longer valid ({e}); will create new")
            except Exception as e:
                print(f"  Could not read notion-feedback.json: {e}")

    if not parent_page_id:
        root_page_id = os.environ.get("NOTION_MBB_ROOT_PAGE_ID")
        if not root_page_id:
            print("Error: set either NOTION_PARENT_PAGE_ID or NOTION_MBB_ROOT_PAGE_ID in .env")
            sys.exit(1)
        dir_name = research_dir.name  # e.g. tsmc-30.03.2026
        # Build title: "Tsmc — MBB Engagement (30.03.2026)"
        parts = dir_name.split("-", 1)
        company = parts[0].upper() if len(parts[0]) <= 4 else parts[0].capitalize()
        date_part = parts[1] if len(parts) > 1 else dir_name
        engagement_title = f"{company} — MBB Engagement ({date_part})"
        print(f"Creating engagement page: '{engagement_title}' under root {root_page_id}")
        parent_page_id = create_page(headers, root_page_id, engagement_title)
        print(f"Engagement page ID: {parent_page_id}")

    # Load prior mapping (if any) so we can re-use existing pages — idempotent uploads.
    # NOTION_FORCE_CREATE=1 bypasses reuse and creates fresh pages (intentional fresh export).
    force_create = os.environ.get("NOTION_FORCE_CREATE", "").strip() in ("1", "true", "yes")
    prior_mapping: Dict[str, str] = {}
    mapping_path = research_dir / "notion-mapping.json"
    if mapping_path.exists() and not force_create:
        try:
            with open(mapping_path) as f:
                prior_mapping = json.load(f)
            if prior_mapping:
                print(f"Loaded prior mapping: {len(prior_mapping)} entries — will reuse alive pages")
        except Exception as e:
            print(f"  Could not read notion-mapping.json: {e}")
    if force_create:
        print("NOTION_FORCE_CREATE=1 — ignoring prior mapping, creating fresh pages")

    # Export each file, capturing returned page IDs directly (no second-pass enumeration).
    mapping: Dict[str, str] = {}
    # Preserve unrelated entries from prior mapping (e.g. Feedback page) so they survive.
    # Only file-derived stems will be overwritten by this export.
    file_stems = {f.stem for f in files}
    for k, v in prior_mapping.items():
        if k not in file_stems:
            mapping[k] = v

    for filepath in files:
        existing_id = prior_mapping.get(filepath.stem)
        try:
            page_id = export_file(headers, parent_page_id, filepath,
                                  existing_page_id=existing_id)
            mapping[filepath.stem] = page_id
        except Exception as e:
            print(f"  ERROR exporting {filepath.name}: {e}")
            # If we had a prior page, keep it in mapping so a later run can retry update.
            if existing_id:
                mapping[filepath.stem] = existing_id

    # Feedback page: reuse existing if previously created (avoid duplicates on re-uploads).
    feedback_page_id = None
    feedback_meta_path = research_dir / "notion-feedback.json"
    if feedback_meta_path.exists():
        try:
            with open(feedback_meta_path) as f:
                saved_fb = json.load(f)
            saved_fb_id = saved_fb.get("feedback_page_id")
            if saved_fb_id:
                try:
                    verify_fb = api_request("GET", f"{NOTION_API}/pages/{saved_fb_id}", get_headers(token))
                    if not verify_fb.get("archived", False):
                        feedback_page_id = saved_fb_id
                        print(f"Reusing existing Feedback page: {feedback_page_id}")
                except Exception as e:
                    print(f"  Saved Feedback page {saved_fb_id} no longer valid ({e}); will create new")
        except Exception:
            pass

    if not feedback_page_id:
        print("Creating Feedback page...")
        feedback_page_id = create_feedback_page(headers, parent_page_id)
        print(f"Feedback page ID: {feedback_page_id}")

    # Save metadata (preserves engagement_page_id for future runs to auto-detect)
    save_notion_meta(research_dir, mapping, feedback_page_id, parent_page_id)

    print(f"\nDone! Parent page: https://notion.so/{parent_page_id.replace('-', '')}")


if __name__ == "__main__":
    main()
