#!/usr/bin/env python3
"""
Export research files to Notion. Idempotent: re-running updates existing pages
instead of creating duplicates. Skips files whose rendered content is unchanged.

Each file → one Notion child page under the engagement parent page.

Idempotency model:
  • On first run, creates a page per file and writes notion-mapping.json
    ({"filename_stem": {"page_id": "<id>", "sha256": "<hex>"}}) plus
    notion-feedback.json (engagement + feedback page IDs).
  • On subsequent runs, reads notion-mapping.json. For each file:
      - if its saved page is alive AND rendered-content sha256 matches the
        stored hash → SKIPS upload entirely (no API calls for that page).
      - if its saved page is alive but content has changed → WIPES blocks +
        re-uploads in place. Page ID preserved. Old Notion links keep working.
      - if the saved page is archived/missing → creates a new page.
      - if a file is new (not in mapping) → creates a new page.
  • Legacy mapping schema ({"stem": "<page_id>"}) is auto-upgraded on first
    run; legacy entries cannot skip (no prior hash) so always re-upload once,
    then store hash for future skip-eligibility.
  • The Feedback page ID and engagement page ID survive across runs too
    (saved in notion-feedback.json; only recreated if archived).

Usage:
    NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

    # Force fresh pages (ignore prior mapping — intentional rebuild):
    NOTION_FORCE_CREATE=1 NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

    # Force re-upload (keep page IDs, ignore content-hash skip):
    NOTION_FORCE_UPLOAD=1 NOTION_TOKEN=secret_xxx python3 export_to_notion.py <research_dir>

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
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Notion limits
MAX_BLOCKS_PER_REQUEST = 100
MAX_RICH_TEXT_LENGTH = 2000

# Engagement cover layout version. Bump when block schema (count or types) changes;
# bump triggers delete+recreate of the cover on next export (lands at end of page —
# one-time degradation). PATCH-in-place is used when version matches.
COVER_VERSION = "v1"


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


# URLs that Notion accepts in rich_text "link" objects must be absolute http(s).
# Relative paths (e.g. [file.md](file.md)) or mailto:/ftp:/ schemes cause
# 400 "Invalid URL for link" errors and silently drop the surrounding block.
NOTION_VALID_URL_RE = re.compile(r"^https?://[^\s<>]+$", re.IGNORECASE)


def is_valid_notion_url(url: str) -> bool:
    """Return True iff `url` is safe to pass as a Notion link target."""
    return bool(url) and bool(NOTION_VALID_URL_RE.match(url.strip()))


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
                if is_valid_notion_url(url):
                    for chunk in split_text(label):
                        result.append({"type": "text", "text": {"content": chunk, "link": {"url": url}}})
                else:
                    # Invalid URL (relative path, broken scheme, etc.) — render label as plain text.
                    # Notion rejects non-http(s) links with 400 errors that drop whole blocks.
                    for chunk in split_text(label):
                        result.append({"type": "text", "text": {"content": chunk}})

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


# Matches markdown links whose target is a local relative path to a .md / .log / .txt file
# (no scheme, no leading `/`, not a URL). Captures: (label, filename_stem, extension)
# Examples that match: [bull case](bull-case.md), [log](dd-engagement.log)
# Examples that DON'T match: [text](https://...), [text](./absolute/path)
RELATIVE_FILE_LINK_RE = re.compile(
    r"\[([^\]]+)\]\(([^):/\s]+)\.(md|log|txt)\)",
    re.IGNORECASE,
)


def rewrite_cross_links(content: str, link_map: Dict[str, str]) -> str:
    """Rewrite local `[label](file.md)` links to absolute Notion page URLs.

    `link_map` maps file stem (e.g. "bull-case") to a Notion page_id (with or
    without dashes). Unmatched stems are left untouched so the URL validator
    can later strip the broken link.
    """
    if not link_map:
        return content

    def _replace(m: re.Match) -> str:
        label, stem, ext = m.group(1), m.group(2), m.group(3)
        page_id = link_map.get(stem)
        if not page_id:
            return m.group(0)  # leave unchanged
        # Notion page URLs accept the id with or without dashes
        clean_id = page_id.replace("-", "")
        return f"[{label}](https://notion.so/{clean_id})"

    return RELATIVE_FILE_LINK_RE.sub(_replace, content)


def ensure_page_exists(headers: dict, parent_page_id: str, filepath: Path,
                      existing_page_id: Optional[str] = None) -> Tuple[str, bool]:
    """Allocate a Notion page for `filepath`. Returns (page_id, was_reused).

    `was_reused=True` means we successfully verified the existing_page_id is
    alive — the caller can SKIP a second page_is_alive() check before wipe.
    Reused pages also get their title refreshed to the current pretty-title
    map (best-effort), so renames flow through on re-export.
    `was_reused=False` means we created a fresh page (no wipe needed).

    Splitting allocation from content lets us build a full link_map before
    any content gets uploaded, so cross-file links can be rewritten.
    """
    title = pretty_title_for(filepath)
    if existing_page_id and page_is_alive(headers, existing_page_id):
        print(f"  Allocating: {filepath.name} — reusing existing page {existing_page_id} (title='{title}')")
        # Keep title in sync (cheap; tolerates older exports that used bare stems)
        _update_page_title(headers, existing_page_id, title)
        return existing_page_id, True
    if existing_page_id:
        print(f"  Allocating: {filepath.name} — saved page {existing_page_id} not alive; creating new")
    else:
        print(f"  Allocating: {filepath.name} — creating new page (title='{title}')")
    return create_page(headers, parent_page_id, title), False


def render_content(filepath: Path, link_map: Optional[Dict[str, str]] = None) -> Tuple[str, str]:
    """Read `filepath`, rewrite cross-file links if `link_map` provided,
    and return (rendered_content, sha256_hex).

    Hash is computed on POST-rewrite content so that link_map changes
    invalidate the cache correctly (a rewrite that changes target page_ids
    must trigger a re-upload, not a "skip — unchanged" decision)."""
    content = filepath.read_text(encoding="utf-8")
    if link_map:
        content = rewrite_cross_links(content, link_map)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return content, content_hash


def export_file_content(headers: dict, page_id: str, filepath: Path,
                        wipe_first: bool = False,
                        link_map: Optional[Dict[str, str]] = None,
                        rendered_content: Optional[str] = None) -> str:
    """Upload `filepath` content to `page_id`. Returns sha256 of rendered content.

    `wipe_first=True` triggers idempotent re-export (delete all existing blocks
    before append). Callers from main() already know this from ensure_page_exists()
    return value — no redundant page_is_alive() API call here.

    `rendered_content` allows caller to pre-compute the post-rewrite content
    (e.g. for hash comparison) and avoid double-reading + double-rewriting.
    """
    print(f"  Exporting content: {filepath.name} → {page_id}")
    if rendered_content is not None:
        content = rendered_content
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    else:
        content, content_hash = render_content(filepath, link_map)

    if wipe_first:
        print(f"    Wiping existing blocks (idempotent re-export)")
        delete_all_blocks(headers, page_id)

    blocks = markdown_to_blocks(content)
    print(f"    Blocks: {len(blocks)}, appending...")
    append_blocks(headers, page_id, blocks)
    print(f"    Done: {len(blocks)} blocks uploaded")
    return content_hash


def export_file(headers: dict, parent_page_id: str, filepath: Path,
                existing_page_id: Optional[str] = None,
                link_map: Optional[Dict[str, str]] = None) -> str:
    """Single-pass file export (back-compat wrapper). Returns page_id.

    Equivalent to ensure_page_exists() + export_file_content(). Use the
    two-step variants directly when you need to build a full link_map across
    multiple files before any content uploads, OR want content-hash skip.
    """
    page_id, was_reused = ensure_page_exists(headers, parent_page_id, filepath, existing_page_id)
    export_file_content(headers, page_id, filepath, wipe_first=was_reused,
                        link_map=link_map)
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


# ============================================================================
# Engagement cover page — MBB-style first-page index
# ============================================================================
#
# The engagement parent page in Notion gets an MBB-cover-deck-style index at
# the top: verdict callout, key numbers, reading guide with links to each
# decision layer, supporting analysis links, foundations links, methodology
# footer. The cover is built from data extracted from dd-short.md (or
# dd-decision-first.md as fallback) plus the link_map (file stem → page_id)
# built during Pass 1.
#
# Two-step placement for top-of-page positioning:
#   1. pre_create_cover_skeleton — runs BEFORE Pass 1 if no prior cover IDs
#      exist; appends placeholder skeleton to the (empty) engagement page so
#      it lands at the TOP. Subsequent child_page blocks from Pass 1 append
#      below the cover.
#   2. update_cover — runs AFTER Pass 2 + feedback page creation; PATCHes
#      each saved cover block in place with real content (positions preserved).
#      On version/count mismatch or dead blocks → delete + recreate (lands at
#      end of page on re-runs; one-time degradation, logged as warning).
#
# State persisted in notion-feedback.json:
#   cover_block_ids: [<id>, <id>, ...]  — in layout order
#   cover_version:   "v1"
# ============================================================================


def _page_url(page_id: str) -> str:
    """Convert page_id (with or without dashes) to absolute notion.so URL."""
    return f"https://notion.so/{page_id.replace('-', '')}"


def _text(content: str, **annot) -> dict:
    """Build a Notion rich_text 'text' element with optional annotations."""
    obj = {"type": "text", "text": {"content": content}}
    if annot:
        obj["annotations"] = annot
    return obj


def _link(label: str, url: str, **annot) -> dict:
    """Build a Notion rich_text 'text' element with a hyperlink."""
    obj = {"type": "text", "text": {"content": label, "link": {"url": url}}}
    if annot:
        obj["annotations"] = annot
    return obj


def _h1(title: str) -> dict:
    return {"object": "block", "type": "heading_1",
            "heading_1": {"rich_text": [_text(title)]}}


def _h2(title: str) -> dict:
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [_text(title)]}}


def _para(rich) -> dict:
    if isinstance(rich, str):
        rich = [_text(rich)]
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": rich}}


def _bullet(rich) -> dict:
    if isinstance(rich, str):
        rich = [_text(rich)]
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich}}


def _callout(rich, emoji: str, color: str) -> dict:
    if isinstance(rich, str):
        rich = [_text(rich)]
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": rich,
                        "icon": {"type": "emoji", "emoji": emoji},
                        "color": color}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


# Title-pattern → file stem reverse map for normalizing legacy "pretty title"
# mappings (e.g. from older exports where keys were "⚡ 5. Bull Case (...)").
# Order matters: most-specific (literal stems) FIRST, human-readable phrases
# AFTER. Each entry is (compiled_regex, stem). The first match wins.
_LEGACY_TITLE_PATTERNS = [
    # Literal stems — match these first to win over phrases below.
    (re.compile(r"\bdd-decision-first\b", re.IGNORECASE), "dd-decision-first"),
    (re.compile(r"\bdd-short\b", re.IGNORECASE),          "dd-short"),
    (re.compile(r"\bdd-mid\b", re.IGNORECASE),            "dd-mid"),
    (re.compile(r"\bdd-report\b", re.IGNORECASE),         "dd-report"),
    (re.compile(r"\bbull-case\b", re.IGNORECASE),         "bull-case"),
    (re.compile(r"\bcustomer-discovery\b", re.IGNORECASE), "customer-discovery"),
    (re.compile(r"\bma-exit-scenarios\b", re.IGNORECASE), "ma-exit-scenarios"),
    (re.compile(r"\bdd-red-team\b", re.IGNORECASE),       "dd-red-team"),
    (re.compile(r"\bdd-risk-matrix\b", re.IGNORECASE),    "dd-risk-matrix"),
    (re.compile(r"\bdd-hypothesis-report\b", re.IGNORECASE), "dd-hypothesis-report"),
    (re.compile(r"\bdd-market-validation\b", re.IGNORECASE), "dd-market-validation"),
    (re.compile(r"\bcompany-brief\b", re.IGNORECASE),     "company-brief"),
    (re.compile(r"\bmarket-map\b", re.IGNORECASE),        "market-map"),
    (re.compile(r"\bportfolio\b", re.IGNORECASE),         "portfolio"),
    (re.compile(r"\badvanced-analytics\b", re.IGNORECASE), "advanced-analytics"),
    (re.compile(r"\bdomain-expert-input\b", re.IGNORECASE), "domain-expert-input"),
    (re.compile(r"\bvalidation-report\b", re.IGNORECASE),  "validation-report"),
    (re.compile(r"\bfinal-report\b", re.IGNORECASE),       "final-report"),
    (re.compile(r"\bgtm-playbook\b", re.IGNORECASE),       "gtm-playbook"),
    (re.compile(r"\bcreative-brief\b", re.IGNORECASE),     "creative-brief"),
    (re.compile(r"\bcontact-universe\b", re.IGNORECASE),   "contact-universe"),
    # Human-readable phrases (used by older exports — case-insensitive).
    (re.compile(r"\bbull\s+case\b", re.IGNORECASE),                     "bull-case"),
    (re.compile(r"\bcustomer\s+discovery\b", re.IGNORECASE),            "customer-discovery"),
    (re.compile(r"\b(?:m&a|m\s*&\s*a|exit\s+scenarios?)\b", re.IGNORECASE), "ma-exit-scenarios"),
    (re.compile(r"\b(?:bear\s+case|red\s+team)\b", re.IGNORECASE),      "dd-red-team"),
    (re.compile(r"\brisk\s+matrix\b", re.IGNORECASE),                   "dd-risk-matrix"),
    (re.compile(r"\bhypothesis\b|\bscorecard\b", re.IGNORECASE),        "dd-hypothesis-report"),
    (re.compile(r"\b(?:moat\s*x.?ray|vrio|market\s+validation)\b", re.IGNORECASE), "dd-market-validation"),
    (re.compile(r"\bcompany\s+brief\b", re.IGNORECASE),                 "company-brief"),
    (re.compile(r"\bmarket\s+map(?:ping)?\b", re.IGNORECASE),           "market-map"),
    (re.compile(r"\badvanced\s+analytics\b", re.IGNORECASE),            "advanced-analytics"),
    (re.compile(r"\bdomain\s+expert\b", re.IGNORECASE),                 "domain-expert-input"),
    (re.compile(r"\b(?:validation\s+report|fact.?check\s+audit)\b", re.IGNORECASE), "validation-report"),
    (re.compile(r"\bportfolio\s+strategy\b", re.IGNORECASE),            "portfolio"),
    (re.compile(r"\bfinal\s+report\b", re.IGNORECASE),                  "final-report"),
    (re.compile(r"\bgtm\s+playbook\b", re.IGNORECASE),                  "gtm-playbook"),
    (re.compile(r"\bcreative\s+brief\b", re.IGNORECASE),                "creative-brief"),
    (re.compile(r"\bcontact\s+universe\b", re.IGNORECASE),              "contact-universe"),
    # Decision layers — human form
    (re.compile(r"\bdecision[- ]first\b", re.IGNORECASE),               "dd-decision-first"),
    (re.compile(r"\binstitutional[/ ]\s*legal\b", re.IGNORECASE),       "dd-report"),
    # Segments
    (re.compile(r"\bsegment[-_\s]+([a-z0-9-]+)\b", re.IGNORECASE),      "_segment_dynamic_"),
]


def _stem_from_legacy_title(title: str) -> Optional[str]:
    """Return the file stem implied by a legacy 'pretty title', or None."""
    for pat, stem in _LEGACY_TITLE_PATTERNS:
        m = pat.search(title)
        if not m:
            continue
        if stem == "_segment_dynamic_":
            return f"segment-{m.group(1).lower()}"
        return stem
    return None


def normalize_mapping(prior_mapping_raw: dict) -> dict:
    """Convert legacy 'pretty title' keyed entries to stem-keyed entries.

    Old exports (pre-v1 cover) used decorated keys like:
        "⚡ 1. dd-short (10-second decision)": "<page_id>"
        "🚀 5. Bull Case ($2M upside scenarios)":  "<page_id>"
    Current schema is:
        "dd-short": {"page_id": "<id>", "sha256": "<hex>"}

    Detects schema, upgrades legacy entries by reverse-mapping pretty titles
    back to stems (`_stem_from_legacy_title`). Already-normalized entries
    pass through unchanged. Unknown titles (e.g. INDEX) are skipped silently.
    """
    if not prior_mapping_raw:
        return {}

    # Heuristic: if every key looks like a file-stem token, mapping is current.
    stem_token = re.compile(r"^[a-z0-9][a-z0-9-]*$")
    if all(stem_token.match(k) for k in prior_mapping_raw):
        return prior_mapping_raw

    upgraded: Dict = {}
    skipped = []
    for k, v in prior_mapping_raw.items():
        if stem_token.match(k):
            upgraded[k] = v
            continue
        stem = _stem_from_legacy_title(k)
        if not stem:
            skipped.append(k)
            continue
        if stem in upgraded:
            continue  # first wins
        if isinstance(v, str):
            upgraded[stem] = {"page_id": v, "sha256": None}
        elif isinstance(v, dict):
            upgraded[stem] = v
    if upgraded:
        print(f"  Normalized legacy mapping: {len(prior_mapping_raw)} entries → "
              f"{len(upgraded)} stem-keyed" + (f" (skipped {len(skipped)})" if skipped else ""))
    return upgraded


def parse_engagement_metadata(research_dir: Path) -> dict:
    """Extract company name, date, fast-mode flag from research_dir name.

    Date-aware split — handles multi-hyphen company slugs (e.g. t-bank, t-mobile, jp-morgan).
    Date pattern at end of name (DD.MM.YYYY) is the canonical anchor; everything before is company.

    Examples:
        dydx-19.05.2026           → company="DYDX",      date="19.05.2026"
        microsoft-21.05.2026-fast → company="Microsoft", date="21.05.2026", is_fast=True
        tsmc-30.03.2026           → company="TSMC",      date="30.03.2026"
        t-bank-25.05.2026         → company="T-Bank",    date="25.05.2026"
        jp-morgan-15.06.2026      → company="JP-Morgan", date="15.06.2026"
    """
    import re
    name = research_dir.name
    is_fast = name.endswith("-fast")
    stripped = name[:-5] if is_fast else name

    # Date-aware split: find trailing DD.MM.YYYY (or D.M.YYYY) preceded by a dash
    m = re.search(r"-(\d{1,2}\.\d{1,2}\.\d{4})$", stripped)
    if m:
        company_raw = stripped[: m.start()]
        date_part = m.group(1)
    else:
        # Fallback to legacy first-hyphen split when no date pattern detected
        parts = stripped.split("-", 1)
        company_raw = parts[0]
        date_part = parts[1] if len(parts) > 1 else ""

    # Casing: tickers (≤4 chars, no internal hyphen) UPPERCASE; multi-word capitalize-each-word
    if "-" in company_raw:
        company = "-".join(w.capitalize() if len(w) > 2 else w.upper() for w in company_raw.split("-"))
    else:
        company = company_raw.upper() if len(company_raw) <= 4 else company_raw.capitalize()

    return {"company": company, "date": date_part, "is_fast": is_fast}


def detect_engagement_type(files: list) -> str:
    """Return engagement type based on which artefacts are present.

    Returns one of:
      'dd'       — Strategic Due Diligence (dd-decision-first / dd-short)
      'bcg'      — BCG/McKinsey-style strategic analysis (final-report / portfolio / gtm-playbook)
      'pmf'      — Product-Market Fit discovery (icp-* / fit-portfolio / traction-* / cohort-*)
      'strategy' — Generic strategy work (customer-discovery / market-mapping / moat-xray)
      'generic'  — Fallback (BCG layout, mostly empty slots)
    """
    names = {f.name for f in files}
    stems = {f.stem for f in files}

    if "dd-decision-first.md" in names or "dd-short.md" in names:
        return "dd"
    if any(n in names for n in ("final-report.md", "portfolio.md", "gtm-playbook.md")):
        return "bcg"
    # PMF detection: any pmf- agent output OR distinctive PMF artefacts
    if (any(s.startswith(("icp-", "pmf-", "cohort-", "traction-", "fit-")) for s in stems)
            or "fit-portfolio.md" in names
            or "pull-map.md" in names
            or "signal-audit.md" in names):
        return "pmf"
    # Strategy detection: distinctive strategy artefacts
    if any(s in stems for s in ("customer-discovery", "market-mapping", "moat-xray",
                                 "strategy-insights", "strategic-plan", "author-bet")):
        return "strategy"
    return "generic"


def extract_dd_verdict(research_dir: Path) -> dict:
    """Parse dd-short.md (or dd-decision-first.md as fallback) for headline data.

    Defensive — every field is optional. Caller renders '—' when missing.
    Supports both English and Russian dd-short variants.
    """
    out = {
        "verdict": None,            # PASS / PROCEED / CONDITIONAL PROCEED / CONDITIONAL PASS
        "headline": None,           # 1-2 sentence summary
        "fair_value": None,         # e.g. "$29M–$85M"
        "asking": None,             # e.g. "$120M"
        "gap": None,                # e.g. "-59%"
        "confidence": None,         # e.g. "82%"
        "hypothesis_breakdown": None,  # e.g. "1✅ / 5⚠️ / 4❌"
        "top_risks": [],            # list of short risk strings (max 3)
    }
    src = None
    for name in ("dd-short.md", "dd-decision-first.md"):
        p = research_dir / name
        if p.exists():
            src = p
            break
    if not src:
        return out
    body = src.read_text(encoding="utf-8")

    # Verdict — try multiple patterns (markdown table, bullet, plain label)
    for pat in [
        r"(?:Вердикт|Verdict|Recommendation|Decision)\s*[:|]\s*\**\s*(PASS|PROCEED|CONDITIONAL\s+PROCEED|CONDITIONAL\s+PASS)\b",
        r"\*\*(PASS|PROCEED|CONDITIONAL\s+PROCEED|CONDITIONAL\s+PASS)\*\*",
    ]:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            out["verdict"] = re.sub(r"\s+", " ", m.group(1).upper())
            break

    # Confidence
    m = re.search(r"(?:Confidence|Уверенность)\s*[:|]\s*\**\s*(\d+\s*%?)", body, re.IGNORECASE)
    if m:
        c = m.group(1).strip()
        if not c.endswith("%"):
            c += "%"
        out["confidence"] = c

    # Hypothesis breakdown — looks for "X✅ / Y⚠️ / Z❌" pattern
    m = re.search(r"(\d+)\s*[✅✓]\s*[/\\]\s*(\d+)\s*[⚠️🟡]\s*[/\\]\s*(\d+)\s*[❌✗]", body)
    if m:
        out["hypothesis_breakdown"] = f"{m.group(1)}✅ / {m.group(2)}⚠️ / {m.group(3)}❌"

    # Fair value
    for pat in [
        r"(?:Probability-weighted\s+fair\s+value|Fair\s+value|Справедливая\s+стоимость)\s*[:|]\s*\**\s*(\$[\d.,]+\s*[BMK]?\s*[–—\-]\s*\$[\d.,]+\s*[BMK]?)",
        r"(?:Fair\s+value|Справедливая\s+стоимость)\s*[:|]\s*\**\s*(\$[\d.,]+\s*[BMK]?)",
    ]:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            out["fair_value"] = m.group(1).strip()
            break

    # Asking
    for pat in [
        r"\$(\d[\d.,]*\s*[BMK]?)\s*MCap\s*(?:вход|asking)",
        r"(?:Asking|Asking\s+price)\s*[:|]\s*\**\s*(\$[\d.,]+\s*[BMK]?)",
        r"vs\s+(\$[\d.,]+\s*[BMK]?)\s*(?:asking|MCap\s*asking|запрашиваемой)",
    ]:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if not val.startswith("$"):
                val = f"${val}"
            out["asking"] = val
            break

    # Gap — explicit field, or % at end of fair value line
    for pat in [
        r"(?:Gap|Premium|Discount|Дисконт|Премия)\s*[:|]\s*\**\s*([-+]\d+\s*%)",
        r"Range[:|]\s*[-+]?\d+%[^()\n]*?\(([-+]?\d+%)\s*(?:база|base)?\)",
        r"Диапазон[^\n]*?:\s*([-+]\d+%)\s*\(база",
    ]:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            out["gap"] = m.group(1).replace(" ", "")
            break

    # Headline — first non-trivial paragraph after the verdict line
    if out["verdict"]:
        # Look for a bolded one-liner near the top
        head_m = re.search(r"\*\*Вы платите .+?\*\*\n+(.+?)(?=\n\n|\n---|$)", body, re.DOTALL)
        if not head_m:
            head_m = re.search(r"^(?:###?\s+(?:Headline|Bottom\s+line|Recommendation))[^\n]*\n+(.+?)(?=\n#{1,3}\s|\n---|\Z)",
                               body, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if head_m:
            txt = head_m.group(1).strip()
            txt = re.sub(r"\*\*?(.+?)\*\*?", r"\1", txt)
            txt = " ".join(txt.split())
            if len(txt) > 280:
                txt = txt[:280].rsplit(" ", 1)[0] + "…"
            if txt:
                out["headline"] = txt

    # Top risks — first 3 list items in a "Top Risks" / "Самый большой риск" / "Deal Breakers" section
    risk_section_m = re.search(
        r"(?:#{1,4}\s*)?(?:Top\s+\d*\s*Risks?|Самый\s+большой\s+риск|Key\s+Risks?|Critical\s+Risks?|Deal\s+Breakers|Эта\s+сделка\s+разрушится)[^\n]*\n+(.+?)(?=\n#{1,3}\s|\n---|\Z)",
        body, re.IGNORECASE | re.DOTALL)
    if risk_section_m:
        block = risk_section_m.group(1)
        # Match bullets / numbered items / arrow-prefixed lines
        items = re.findall(
            r"^(?:\s*[\-\*•→]|\s*\d+\.)\s+(.+?)(?=\n(?:\s*[\-\*•→]|\s*\d+\.|\n\n)|\Z)",
            block, re.MULTILINE | re.DOTALL)
        for item in items[:3]:
            cleaned = re.sub(r"\*\*?(.+?)\*\*?", r"\1", item)
            cleaned = " ".join(cleaned.split())
            if len(cleaned) > 240:
                cleaned = cleaned[:240].rsplit(" ", 1)[0] + "…"
            if cleaned:
                out["top_risks"].append(cleaned)

    return out


# Pretty title mapping for sub-pages. Restores the MBB-engagement convention
# used in earlier exports (e.g. dydx-19.05.2026): each child page in Notion
# gets an emoji-prefixed, human-readable title instead of the bare file stem.
_PRETTY_TITLES = {
    # Phase DD-3a/b — Decision layers
    "dd-short":          "⚡ dd-short — Decision (10 sec)",
    "dd-mid":            "📋 dd-mid — Briefing (5 min)",
    "dd-decision-first": "📕 dd-decision-first — PRIMARY (45-60 min)",
    "dd-report":         "📑 dd-report — Institutional reference",
    # Phase DD-3c — Investor profile
    "bull-case":         "🚀 Bull Case — Upside conditions",
    "customer-discovery": "👥 Customer Discovery — DMU + churn",
    "ma-exit-scenarios": "🤝 M&A / Exit Scenarios",
    # Phase DD-1 / DD-2 — Supporting analysis
    "dd-market-validation": "🏰 Market Validation / Moat X-Ray",
    "dd-hypothesis-report": "📁 Hypothesis Scorecard",
    "dd-risk-matrix":    "🚨 Risk Matrix",
    "dd-red-team":       "🐻 Red Team / Bear Case",
    # Foundations (BCG + DD shared)
    "company-brief":     "📁 Company Brief",
    "market-map":        "🗺️ Market Map",
    "portfolio":         "📊 Portfolio Strategy",
    "advanced-analytics": "📁 Advanced Analytics",
    "domain-expert-input": "📁 Domain Expert Input",
    "validation-report": "📁 Validation Report",
    # BCG-only
    "final-report":      "📕 Final Report",
    "gtm-playbook":      "🎯 GTM Playbook",
    "creative-brief":    "💡 Creative Brief",
    "contact-universe":  "👥 Contact Universe",
    # PMF Discovery
    "fit-portfolio":     "🎯 Fit Portfolio — ICP × Channel matrix",
    "pull-map":          "🧲 Pull Map — Demand signals",
    "signal-audit":      "🔍 Signal Audit — Validation evidence",
    "icp-analysis":      "👥 ICP Analysis",
    "icp-output":        "👥 ICP Output",
    "channel-pricing":   "💰 Channel & Pricing",
    "cohort-analysis":   "📈 Cohort Analysis",
    "traction-research": "📊 Traction Research",
    "references":        "🔗 References & Comparables",
    "moat-xray":         "🏰 Moat X-Ray",
    "pmf-report":        "📕 PMF Report — PRIMARY",
    "final-pmf-report":  "📕 Final PMF Report — PRIMARY",
    # Strategy (StrategyHero / personal-strategy / generic)
    "customer-discovery": "👥 Customer Discovery",
    "market-mapping":    "🗺️ Market Mapping",
    "strategy-insights": "💡 Strategy Insights",
    "strategic-plan":    "📕 Strategic Plan — PRIMARY",
    "author-bet":        "🎲 Author Bet",
}


def pretty_title_for(filepath: Path) -> str:
    """Return MBB-styled Notion page title for a file. Falls back to stem."""
    stem = filepath.stem
    if stem in _PRETTY_TITLES:
        return _PRETTY_TITLES[stem]
    if stem.startswith("segment-"):
        seg = stem.replace("segment-", "").replace("-", " ").title()
        return f"💼 Segment — {seg}"
    return stem


# Verdict → (emoji, callout background color) mapping
_VERDICT_STYLE = {
    "PASS":                ("❌", "red_background"),
    "PROCEED":             ("✅", "green_background"),
    "CONDITIONAL PROCEED": ("⚠️", "yellow_background"),
    "CONDITIONAL PASS":    ("⚠️", "orange_background"),
}


def build_dd_cover_blocks(meta: dict, verdict_data: dict, link_map: Dict[str, str],
                          feedback_page_id: Optional[str]) -> list:
    """Build the fixed 38-block DD cover (matches the approved demo layout).

    Block count is constant — missing data renders as placeholder text so PATCH
    in place works on re-runs without structural drift.
    """
    company = meta.get("company", "?")
    date_str = meta.get("date", "")
    is_fast = meta.get("is_fast", False)

    sub = {k: _page_url(v) for k, v in (link_map or {}).items()}
    fb_url = _page_url(feedback_page_id) if feedback_page_id else None

    verdict = verdict_data.get("verdict") or "VERDICT PENDING"
    icon, color = _VERDICT_STYLE.get(verdict, ("📋", "gray_background"))
    headline = verdict_data.get("headline") or "See dd-decision-first.md for the full investment thesis."

    blocks = []

    # 1. Title
    title = f"{company} — Strategic Due Diligence"
    if is_fast:
        title += "  ⚡"
    blocks.append(_h1(title))

    # 2. Metadata
    meta_parts = []
    if date_str:
        meta_parts.append(f"Дата: {date_str}")
    meta_parts.append("Подготовлено: Xata&Co Strategic DD Team")
    blocks.append(_para([_text("  ·  ".join(meta_parts), italic=True, color="gray")]))

    # 3. Verdict callout
    blocks.append(_callout(
        [_text(f"{verdict}\n", bold=True), _text(headline)],
        emoji=icon, color=color))

    # 4. Divider
    blocks.append(_divider())

    # 5. Reading Guide H2
    blocks.append(_h2("Reading Guide"))

    # 6. Intro paragraph
    blocks.append(_para([_text("Выберите слой по доступному времени.", italic=True, color="gray")]))

    # 7-10. Reading guide bullets (4 layers, fixed)
    layers = [
        ("dd-short",          "🕐 10 sec   →  ", "⚡ dd-short",          "  ·  бинарное решение, fair value gap"),
        ("dd-mid",            "🕔 5 min     →  ", "📋 dd-mid",           "  ·  pre-meeting briefing, top-5 issues"),
        ("dd-decision-first", "🕓 45 min   →  ", "📕 dd-decision-first", "  ·  PRIMARY — IC-grade master report"),
        ("dd-report",         "📑 Reference →  ", "dd-report",           "  ·  institutional / legal format"),
    ]
    for stem, prefix, label, suffix in layers:
        url = sub.get(stem)
        if url:
            rt = [_text(prefix, color="gray"), _link(label, url, bold=True),
                  _text(suffix, color="gray")]
        else:
            rt = [_text(prefix, color="gray"), _text(label, bold=True, color="gray"),
                  _text(f"{suffix}  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 11. Divider
    blocks.append(_divider())

    # 12. Key Numbers H2
    blocks.append(_h2("Key Numbers"))

    # 13. Key Numbers paragraph
    fv = verdict_data.get("fair_value") or "—"
    ask = verdict_data.get("asking") or "—"
    gap = verdict_data.get("gap") or "—"
    conf = verdict_data.get("confidence") or "—"
    hyp = verdict_data.get("hypothesis_breakdown") or "—"
    gap_color = "red" if gap.startswith("-") else ("green" if gap not in ("—", "0%") and gap.startswith("+") else "default")
    blocks.append(_para([
        _text("Fair value: ", color="gray"), _text(fv, bold=True),
        _text("  ·  Asking: ", color="gray"), _text(ask, bold=True),
        _text("  ·  Gap: ", color="gray"), _text(gap, bold=True, color=gap_color),
        _text("  ·  Confidence: ", color="gray"), _text(conf, bold=True),
        _text("  ·  Hypotheses: ", color="gray"), _text(hyp, bold=True),
    ]))

    # 14. Divider
    blocks.append(_divider())

    # 15. Top Risks H2
    blocks.append(_h2("Top Risks (Critical / High)"))

    # 16-18. 3 risk slots (fixed — fill with "—" when fewer)
    risks = verdict_data.get("top_risks", [])
    for i in range(3):
        if i < len(risks):
            rt = [_text("🔴  ", color="red"), _text(risks[i])]
        else:
            rt = [_text("—", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 19. Divider
    blocks.append(_divider())

    # 20. Supporting Analysis H2
    blocks.append(_h2("Supporting Analysis"))

    # 21-24. Supporting bullets (4 fixed)
    support = [
        ("dd-market-validation", "🏰  Market Validation / Moat X-Ray", "TAM stress-test, VRIO scorecard, competitive moat"),
        ("dd-hypothesis-report", "📁  Hypothesis Scorecard",            "10 deal-specific hypotheses tested ✅/⚠️/❌"),
        ("dd-risk-matrix",       "🚨  Risk Matrix",                     "P×I scoring, deal breakers, exit triggers"),
        ("dd-red-team",          "🐻  Red Team / Bear Case",            "bear thesis, stress scenarios, pre-mortem"),
    ]
    for stem, label, desc in support:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 25. Divider
    blocks.append(_divider())

    # 26. Investor-Profile Memos H2
    blocks.append(_h2("Investor-Profile Memos"))

    # 27-29. Investor profile bullets (3 fixed)
    profile = [
        ("bull-case",         "🚀  Bull Case",            "4 conditions for upside, conviction-graded allocation"),
        ("customer-discovery", "👥  Customer Discovery",  "DMU per segment + churn + win-back roadmap"),
        ("ma-exit-scenarios", "🤝  M&A / Exit Scenarios", "strategic acquirers, valuation per path, liquidation waterfall"),
    ]
    for stem, label, desc in profile:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated for this engagement)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 30. Divider
    blocks.append(_divider())

    # 31. Foundations H2
    blocks.append(_h2("Foundations"))

    # 32-35. Foundations bullets (4 fixed)
    foundations = [
        ("company-brief",      "📁  Company Brief",       "verified raw data — SEC, news, LinkedIn"),
        ("market-map",         "🗺️  Market Map",          "segment definitions, competitor universe"),
        ("portfolio",          "📊  Portfolio Strategy",  "MBB Growth-Share Matrix, Selection Lens"),
        ("advanced-analytics", "📁  Advanced Analytics",  "DCF, peer multiples, scenarios"),
    ]
    for stem, label, desc in foundations:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 36. Divider
    blocks.append(_divider())

    # 37. Methodology footer
    blocks.append(_callout([
        _text("Confidential — ", bold=True),
        _text("Methodology: BCG 5 Lenses (Description → Advantage → Future → Options → Selection)"
              "  ·  Decision-First Output Standard (15 rules)  ·  Pyramid Principle"),
    ], emoji="🔒", color="gray_background"))

    # 38. Feedback link paragraph
    fb_rt = [_text("Use the ", italic=True, color="gray")]
    if fb_url:
        fb_rt.append(_link("📋 Feedback page", fb_url, bold=True, italic=True, color="gray"))
    else:
        fb_rt.append(_text("📋 Feedback page", bold=True, italic=True, color="gray"))
    fb_rt.append(_text(" to send corrections — processed within 1 hour by the analytics team.",
                       italic=True, color="gray"))
    blocks.append(_para(fb_rt))

    return blocks


def build_bcg_cover_blocks(meta: dict, link_map: Dict[str, str],
                           feedback_page_id: Optional[str]) -> list:
    """Build the fixed BCG-mode cover (28 blocks). Used when no DD artefacts present."""
    company = meta.get("company", "?")
    date_str = meta.get("date", "")
    sub = {k: _page_url(v) for k, v in (link_map or {}).items()}
    fb_url = _page_url(feedback_page_id) if feedback_page_id else None

    blocks = []

    # 1. Title
    blocks.append(_h1(f"{company} — Strategic Analysis"))

    # 2. Metadata
    meta_parts = []
    if date_str:
        meta_parts.append(f"Дата: {date_str}")
    meta_parts.append("Подготовлено: Xata&Co Strategy Team")
    blocks.append(_para([_text("  ·  ".join(meta_parts), italic=True, color="gray")]))

    # 3. Mode callout
    blocks.append(_callout(
        [_text("MBB Strategic Engagement\n", bold=True),
         _text("Portfolio review · Segment-level strategy · GTM operationalization")],
        emoji="📊", color="blue_background"))

    # 4. Divider
    blocks.append(_divider())

    # 5. Primary Deliverables H2
    blocks.append(_h2("Primary Deliverables"))

    # 6-9. Primary bullets (4 fixed)
    primary = [
        ("final-report",  "📕  Final Report",       "Pyramid-principle synthesis — 45 min IC-grade read"),
        ("portfolio",     "📊  Portfolio Strategy", "MBB Growth-Share Matrix, Selection Lens"),
        ("gtm-playbook",  "🎯  GTM Playbook",       "ICP / DMU / Channels / Pipeline model"),
        ("market-map",    "🗺️  Market Map",         "Segment definitions, competitor universe"),
    ]
    for stem, label, desc in primary:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 10. Divider
    blocks.append(_divider())

    # 11. Foundations H2
    blocks.append(_h2("Foundations"))

    # 12-17. Foundations bullets (6 fixed)
    foundations = [
        ("company-brief",       "📁  Company Brief",       "Single source of truth — verified raw data"),
        ("advanced-analytics",  "📁  Advanced Analytics",  "Bottom-up sizing, growth forecasts, benchmarks"),
        ("domain-expert-input", "📁  Domain Expert Input", "Insider hypothesis validation"),
        ("validation-report",   "📁  Validation Report",   "Fact-check audit, source verification"),
        ("contact-universe",    "👥  Contact Universe",    "Decision-maker map"),
        ("creative-brief",      "💡  Creative Brief",      "Outreach & messaging strategy"),
    ]
    for stem, label, desc in foundations:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 18. Divider
    blocks.append(_divider())

    # 19. Methodology footer
    blocks.append(_callout([
        _text("Confidential — ", bold=True),
        _text("Methodology: BCG 5 Lenses (Description / Advantage / Future / Options / Selection)"
              "  ·  Pyramid Principle  ·  Segmentation by adjacent-segment independence"),
    ], emoji="🔒", color="gray_background"))

    # 20. Feedback link
    fb_rt = [_text("Use the ", italic=True, color="gray")]
    if fb_url:
        fb_rt.append(_link("📋 Feedback page", fb_url, bold=True, italic=True, color="gray"))
    else:
        fb_rt.append(_text("📋 Feedback page", bold=True, italic=True, color="gray"))
    fb_rt.append(_text(" to send corrections — processed within 1 hour.",
                       italic=True, color="gray"))
    blocks.append(_para(fb_rt))

    return blocks


def build_pmf_cover_blocks(meta: dict, link_map: Dict[str, str],
                            feedback_page_id: Optional[str]) -> list:
    """Build the fixed PMF Discovery cover (24 blocks).

    Tailored to pmf-discovery / pmf-navigator output: ICP analysis, fit portfolio,
    channel & pricing, cohort + traction research, pull/signal validation. No
    verdict callout — PMF is iterative discovery, not a binary decision.
    """
    company = meta.get("company", "?")
    date_str = meta.get("date", "")
    sub = {k: _page_url(v) for k, v in (link_map or {}).items()}
    fb_url = _page_url(feedback_page_id) if feedback_page_id else None

    blocks = []

    # 1. Title
    blocks.append(_h1(f"{company} — Product-Market Fit Discovery"))

    # 2. Metadata
    meta_parts = []
    if date_str:
        meta_parts.append(f"Дата: {date_str}")
    meta_parts.append("Подготовлено: Xata&Co PMF Team")
    blocks.append(_para([_text("  ·  ".join(meta_parts), italic=True, color="gray")]))

    # 3. Mode callout
    blocks.append(_callout(
        [_text("PMF Discovery Engagement\n", bold=True),
         _text("ICP refinement · Channel-pricing fit · Cohort + traction validation")],
        emoji="🎯", color="blue_background"))

    # 4. Divider
    blocks.append(_divider())

    # 5. Primary Deliverables H2
    blocks.append(_h2("Primary Deliverables"))

    # 6-9. Primary bullets (4 fixed)
    primary = [
        ("final-pmf-report", "📕  Final PMF Report",     "Synthesized findings + recommendations"),
        ("fit-portfolio",    "🎯  Fit Portfolio",         "ICP × Channel × Pricing matrix"),
        ("icp-analysis",     "👥  ICP Analysis",          "Segments, JTBD, decision-makers"),
        ("channel-pricing",  "💰  Channel & Pricing",     "GTM channels, pricing tiers"),
    ]
    for stem, label, desc in primary:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 10. Divider
    blocks.append(_divider())

    # 11. Validation Layer H2
    blocks.append(_h2("Validation Layer"))

    # 12-15. Validation bullets (4 fixed)
    validation = [
        ("cohort-analysis",   "📈  Cohort Analysis",      "Retention, expansion, churn drivers"),
        ("traction-research", "📊  Traction Research",    "Comparable case studies, benchmarks"),
        ("signal-audit",      "🔍  Signal Audit",         "Demand signals, market evidence"),
        ("pull-map",          "🧲  Pull Map",             "Who is actively reaching for the solution"),
    ]
    for stem, label, desc in validation:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 16. Divider
    blocks.append(_divider())

    # 17. Foundations H2
    blocks.append(_h2("Foundations"))

    # 18-21. Foundations bullets (4 fixed)
    foundations = [
        ("domain-expert-input", "📁  Domain Expert Input", "Insider perspective"),
        ("references",          "🔗  References",          "Comparables, prior art"),
        ("moat-xray",           "🏰  Moat X-Ray",          "Defensibility analysis"),
        ("company-brief",       "📁  Company Brief",       "Raw verified data"),
    ]
    for stem, label, desc in foundations:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 22. Divider
    blocks.append(_divider())

    # 23. Methodology footer
    blocks.append(_callout([
        _text("Confidential — ", bold=True),
        _text("Methodology: PMF Discovery (ICP × JTBD × Pull)  ·  "
              "Cohort science  ·  Channel-pricing fit  ·  Signal-driven iteration"),
    ], emoji="🔒", color="gray_background"))

    # 24. Feedback link
    fb_rt = [_text("Use the ", italic=True, color="gray")]
    if fb_url:
        fb_rt.append(_link("📋 Feedback page", fb_url, bold=True, italic=True, color="gray"))
    else:
        fb_rt.append(_text("📋 Feedback page", bold=True, italic=True, color="gray"))
    fb_rt.append(_text(" to send corrections — processed within 1 hour.",
                       italic=True, color="gray"))
    blocks.append(_para(fb_rt))

    return blocks


def build_strategy_cover_blocks(meta: dict, link_map: Dict[str, str],
                                feedback_page_id: Optional[str]) -> list:
    """Build the fixed strategy-engagement cover (22 blocks).

    Tailored to StrategyHero / personal-strategy-agent style output:
    customer discovery, market mapping, moat x-ray, strategy insights,
    strategic plan. No formal verdict — strategy is option-driven.
    """
    company = meta.get("company", "?")
    date_str = meta.get("date", "")
    sub = {k: _page_url(v) for k, v in (link_map or {}).items()}
    fb_url = _page_url(feedback_page_id) if feedback_page_id else None

    blocks = []

    # 1. Title
    blocks.append(_h1(f"{company} — Strategic Plan"))

    # 2. Metadata
    meta_parts = []
    if date_str:
        meta_parts.append(f"Дата: {date_str}")
    meta_parts.append("Подготовлено: Xata&Co Strategy Team")
    blocks.append(_para([_text("  ·  ".join(meta_parts), italic=True, color="gray")]))

    # 3. Mode callout
    blocks.append(_callout(
        [_text("Strategy Engagement\n", bold=True),
         _text("Customer discovery · Market mapping · Moat analysis · Options selection")],
        emoji="🎲", color="purple_background"))

    # 4. Divider
    blocks.append(_divider())

    # 5. Primary Deliverables H2
    blocks.append(_h2("Primary Deliverables"))

    # 6-8. Primary bullets (3 fixed)
    primary = [
        ("strategic-plan",     "📕  Strategic Plan",      "Chosen options, sequencing, bets"),
        ("strategy-insights",  "💡  Strategy Insights",   "Non-obvious findings"),
        ("market-mapping",     "🗺️  Market Mapping",      "Segments, competitors, white space"),
    ]
    for stem, label, desc in primary:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 9. Divider
    blocks.append(_divider())

    # 10. Discovery Layer H2
    blocks.append(_h2("Discovery Layer"))

    # 11-13. Discovery bullets (3 fixed)
    discovery = [
        ("customer-discovery", "👥  Customer Discovery",  "JTBD, DMU, pain points"),
        ("moat-xray",          "🏰  Moat X-Ray",          "VRIO, defensibility"),
        ("author-bet",         "🎲  Author Bet",          "Founder/author thesis"),
    ]
    for stem, label, desc in discovery:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 14. Divider
    blocks.append(_divider())

    # 15. Foundations H2
    blocks.append(_h2("Foundations"))

    # 16-19. Foundations bullets (4 fixed)
    foundations = [
        ("company-brief",       "📁  Company Brief",       "Verified raw data"),
        ("domain-expert-input", "📁  Domain Expert Input", "Insider perspective"),
        ("validation-report",   "📁  Validation Report",   "Fact-check audit"),
        ("contact-universe",    "👥  Contact Universe",    "Decision-maker map"),
    ]
    for stem, label, desc in foundations:
        url = sub.get(stem)
        if url:
            rt = [_link(label, url, bold=True), _text(f"  ·  {desc}", color="gray")]
        else:
            rt = [_text(label, bold=True, color="gray"),
                  _text("  ·  (not generated)", color="gray", italic=True)]
        blocks.append(_bullet(rt))

    # 20. Divider
    blocks.append(_divider())

    # 21. Methodology footer
    blocks.append(_callout([
        _text("Confidential — ", bold=True),
        _text("Methodology: BCG 5 Lenses (Description / Advantage / Future / Options / Selection)"
              "  ·  Pyramid Principle  ·  Option-driven strategy"),
    ], emoji="🔒", color="gray_background"))

    # 22. Feedback link
    fb_rt = [_text("Use the ", italic=True, color="gray")]
    if fb_url:
        fb_rt.append(_link("📋 Feedback page", fb_url, bold=True, italic=True, color="gray"))
    else:
        fb_rt.append(_text("📋 Feedback page", bold=True, italic=True, color="gray"))
    fb_rt.append(_text(" to send corrections — processed within 1 hour.",
                       italic=True, color="gray"))
    blocks.append(_para(fb_rt))

    return blocks


def build_cover_blocks_for(engagement_type: str, meta: dict, verdict_data: dict,
                            link_map: Dict[str, str], feedback_page_id: Optional[str]) -> list:
    """Dispatch to the right cover builder based on engagement type."""
    if engagement_type == "dd":
        return build_dd_cover_blocks(meta, verdict_data, link_map, feedback_page_id)
    if engagement_type == "bcg":
        return build_bcg_cover_blocks(meta, link_map, feedback_page_id)
    if engagement_type == "pmf":
        return build_pmf_cover_blocks(meta, link_map, feedback_page_id)
    if engagement_type == "strategy":
        return build_strategy_cover_blocks(meta, link_map, feedback_page_id)
    # Generic fallback — reuse BCG layout (minimal harm if some links are missing)
    return build_bcg_cover_blocks(meta, link_map, feedback_page_id)


def _cover_block_alive(headers: dict, block_id: str) -> bool:
    """Check whether a Notion block is still alive (not archived/deleted)."""
    try:
        resp = api_request("GET", f"{NOTION_API}/blocks/{block_id}", headers)
        return not resp.get("archived", False)
    except Exception:
        return False


def pre_create_cover_skeleton(headers: dict, engagement_page_id: str,
                              cover_blocks: list, prior_cover_state: Optional[dict]) -> dict:
    """If no prior cover IDs exist, append the cover at the TOP of the engagement page.

    Must be called BEFORE Pass 1 (subpage allocation) on first export so the cover
    blocks land before any child_page blocks. On subsequent runs this is a no-op —
    update_cover handles the PATCH path.

    Returns updated cover_state dict ({"cover_block_ids": [...], "cover_version": ...}).
    """
    if prior_cover_state and prior_cover_state.get("cover_block_ids"):
        # Re-run: leave existing blocks where they are; update_cover will PATCH later.
        return prior_cover_state

    # First-run path — append (engagement page is empty → blocks land at top).
    print(f"  Cover: pre-allocating {len(cover_blocks)} skeleton blocks at top of engagement page")
    new_ids = []
    for i in range(0, len(cover_blocks), MAX_BLOCKS_PER_REQUEST):
        batch = cover_blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        try:
            resp = api_request("PATCH", f"{NOTION_API}/blocks/{engagement_page_id}/children",
                               headers, {"children": batch})
            new_ids.extend(b["id"] for b in resp.get("results", []))
        except Exception as e:
            print(f"    Warning: cover skeleton batch failed: {e}")
        if i + MAX_BLOCKS_PER_REQUEST < len(cover_blocks):
            time.sleep(0.3)
    return {"cover_block_ids": new_ids, "cover_version": COVER_VERSION}


def update_cover(headers: dict, engagement_page_id: str, cover_blocks: list,
                 prior_cover_state: Optional[dict]) -> dict:
    """Update cover with finalized content (post-Pass-2, after link_map is complete).

    Behaviour:
      • If prior cover_version matches current AND block count matches AND a sample
        of saved block_ids is alive → PATCH each block in place (position preserved).
      • Otherwise → delete saved blocks (best-effort) and append fresh cover.
        On re-runs, the appended blocks land at the END of the engagement page
        (Notion API has no prepend-to-non-empty-parent). Logged as warning.

    Returns updated cover_state.
    """
    prior_ids = (prior_cover_state or {}).get("cover_block_ids") or []
    prior_version = (prior_cover_state or {}).get("cover_version")

    structure_match = (
        prior_version == COVER_VERSION
        and len(prior_ids) == len(cover_blocks)
        and bool(prior_ids)
    )

    if structure_match:
        # Sample-check first 3 saved blocks to avoid full O(N) verification.
        sample_alive = all(_cover_block_alive(headers, bid) for bid in prior_ids[:3])
        if sample_alive:
            print(f"  Cover: PATCHing {len(prior_ids)} blocks in place")
            success = 0
            for i, (block_id, new_block) in enumerate(zip(prior_ids, cover_blocks)):
                btype = new_block["type"]
                payload = {btype: new_block[btype]}
                try:
                    api_request("PATCH", f"{NOTION_API}/blocks/{block_id}", headers, payload)
                    success += 1
                except Exception as e:
                    print(f"    Block {i + 1}/{len(prior_ids)} ({btype}) PATCH failed: {str(e)[:100]}")
                if (i + 1) % 8 == 0:
                    time.sleep(0.15)
            print(f"    PATCHed {success}/{len(prior_ids)} blocks")
            return {"cover_block_ids": prior_ids, "cover_version": COVER_VERSION}
        print("  Cover: saved blocks dead — recreating (will land at end of page)")
    elif prior_ids:
        print(f"  Cover: version/count mismatch (prior={prior_version}/{len(prior_ids)}, "
              f"new={COVER_VERSION}/{len(cover_blocks)}) — recreating (will land at end)")

    # Recreate path: delete old (best-effort), append fresh
    if prior_ids:
        for bid in prior_ids:
            try:
                requests.delete(f"{NOTION_API}/blocks/{bid}", headers=headers)
                time.sleep(0.05)
            except Exception:
                pass

    new_ids = []
    for i in range(0, len(cover_blocks), MAX_BLOCKS_PER_REQUEST):
        batch = cover_blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        try:
            resp = api_request("PATCH", f"{NOTION_API}/blocks/{engagement_page_id}/children",
                               headers, {"children": batch})
            new_ids.extend(b["id"] for b in resp.get("results", []))
        except Exception as e:
            print(f"    Warning: cover batch failed: {e}")
        if i + MAX_BLOCKS_PER_REQUEST < len(cover_blocks):
            time.sleep(0.3)
    return {"cover_block_ids": new_ids, "cover_version": COVER_VERSION}


def _update_page_title(headers: dict, page_id: str, new_title: str) -> None:
    """PATCH a Notion page's title property. Best-effort — silent on failure."""
    try:
        api_request("PATCH", f"{NOTION_API}/pages/{page_id}", headers, {
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": new_title}}]}
            }
        })
    except Exception as e:
        print(f"    Warning: page title update failed for {page_id}: {str(e)[:100]}")


def save_notion_meta(research_dir: Path, mapping: dict, feedback_page_id: str,
                     engagement_page_id: str, cover_state: Optional[dict] = None) -> None:
    """Save page ID mapping and feedback page info to the research directory."""
    with open(research_dir / "notion-mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)
    feedback_payload = {
        "feedback_page_id": feedback_page_id,
        "engagement_page_id": engagement_page_id,
    }
    if cover_state:
        feedback_payload["cover_block_ids"] = cover_state.get("cover_block_ids", [])
        feedback_payload["cover_version"] = cover_state.get("cover_version", COVER_VERSION)
    with open(research_dir / "notion-feedback.json", "w") as f:
        json.dump(feedback_payload, f, indent=2)
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
    # Cover state — block IDs and version of the engagement cover, persisted across runs
    prior_cover_state: Optional[dict] = None
    if parent_page_id:
        print(f"Using existing parent page (env override): {parent_page_id}")
        # Even with env override, try to pick up cover state if it was previously saved
        # for the same research dir (lets the cover PATCH in place on re-runs).
        feedback_meta_path = research_dir / "notion-feedback.json"
        if feedback_meta_path.exists():
            try:
                with open(feedback_meta_path) as f:
                    saved = json.load(f)
                if saved.get("cover_block_ids"):
                    prior_cover_state = {
                        "cover_block_ids": saved.get("cover_block_ids", []),
                        "cover_version": saved.get("cover_version"),
                    }
            except Exception:
                pass
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
                            # Carry over cover state for in-place PATCH
                            if saved.get("cover_block_ids"):
                                prior_cover_state = {
                                    "cover_block_ids": saved.get("cover_block_ids", []),
                                    "cover_version": saved.get("cover_version"),
                                }
                    except Exception as e:
                        print(f"  Saved engagement page {saved_engagement} no longer valid ({e}); will create new")
            except Exception as e:
                print(f"  Could not read notion-feedback.json: {e}")

    if not parent_page_id:
        root_page_id = os.environ.get("NOTION_MBB_ROOT_PAGE_ID")
        if not root_page_id:
            print("Error: set either NOTION_PARENT_PAGE_ID or NOTION_MBB_ROOT_PAGE_ID in .env")
            sys.exit(1)
        # Build title via the same date-aware parser used by parse_engagement_metadata.
        # Handles multi-hyphen company slugs (t-bank, jp-morgan, etc.) correctly.
        meta = parse_engagement_metadata(research_dir)
        company = meta["company"] or research_dir.name
        date_part = meta["date"] or research_dir.name
        engagement_title = f"{company} — MBB Engagement ({date_part})"
        print(f"Creating engagement page: '{engagement_title}' under root {root_page_id}")
        parent_page_id = create_page(headers, root_page_id, engagement_title)
        print(f"Engagement page ID: {parent_page_id}")

    # Load prior mapping (if any) so we can re-use existing pages — idempotent uploads.
    # NOTION_FORCE_CREATE=1 bypasses reuse and creates fresh pages (intentional fresh export).
    # NOTION_FORCE_UPLOAD=1 keeps page reuse but ignores content-hash skip (force re-upload).
    force_create = os.environ.get("NOTION_FORCE_CREATE", "").strip() in ("1", "true", "yes")
    force_upload = os.environ.get("NOTION_FORCE_UPLOAD", "").strip() in ("1", "true", "yes")
    prior_mapping_raw: Dict = {}
    mapping_path = research_dir / "notion-mapping.json"
    if mapping_path.exists() and not force_create:
        try:
            with open(mapping_path) as f:
                prior_mapping_raw = json.load(f)
            # Normalize legacy "pretty title" keyed mappings to current stem-keyed schema.
            # Safe no-op if already current.
            prior_mapping_raw = normalize_mapping(prior_mapping_raw)
            if prior_mapping_raw:
                print(f"Loaded prior mapping: {len(prior_mapping_raw)} entries — will reuse alive pages")
        except Exception as e:
            print(f"  Could not read notion-mapping.json: {e}")
    if force_create:
        print("NOTION_FORCE_CREATE=1 — ignoring prior mapping, creating fresh pages")
        prior_cover_state = None  # also drop cover state — full rebuild
    if force_upload:
        print("NOTION_FORCE_UPLOAD=1 — skipping content-hash check, re-uploading everything")

    # ----- Engagement cover prep ---------------------------------------------
    # Detect engagement type (dd / bcg / generic), parse metadata, and extract
    # DD verdict data (if applicable) BEFORE Pass 1. On first run (no prior
    # cover_block_ids), we pre-allocate the cover skeleton so it lands at the
    # top of the engagement page; subsequent child_page blocks from Pass 1
    # append below. On re-runs we skip pre-allocation — the saved skeleton
    # already holds the top slot and update_cover() will PATCH it in place
    # after Pass 2.
    engagement_type = detect_engagement_type(files)
    engagement_meta = parse_engagement_metadata(research_dir)
    verdict_data = extract_dd_verdict(research_dir) if engagement_type == "dd" else {}
    print(f"Engagement: type={engagement_type}, company={engagement_meta['company']}, "
          f"date={engagement_meta['date']}")
    if engagement_type == "dd" and verdict_data.get("verdict"):
        print(f"  Verdict extracted: {verdict_data['verdict']}  "
              f"(fair_value={verdict_data.get('fair_value') or '—'}, "
              f"confidence={verdict_data.get('confidence') or '—'})")

    # Build skeleton cover (no link_map yet — bullets render as placeholders).
    # Block count is identical to final cover so PATCH in place stays structurally valid.
    skeleton_blocks = build_cover_blocks_for(engagement_type, engagement_meta,
                                              verdict_data, {}, None)
    # Pre-allocate at top of engagement page (no-op if cover already exists).
    cover_state = pre_create_cover_skeleton(headers, parent_page_id, skeleton_blocks,
                                             prior_cover_state)

    # Mapping schema accepts two shapes for back-compat:
    #   legacy:  {"stem": "<page_id>"}                                 (string)
    #   current: {"stem": {"page_id": "<id>", "sha256": "<hex>"}}     (dict)
    def parse_mapping_entry(entry):
        """Return (page_id, sha256_or_None) for either schema."""
        if isinstance(entry, str):
            return entry, None
        if isinstance(entry, dict):
            return entry.get("page_id"), entry.get("sha256")
        return None, None

    # Two-pass export so cross-file links can resolve to absolute Notion URLs:
    #   Pass 1 — allocate (or reuse) a page_id for every file. Builds `link_map`.
    #   Pass 2 — read content, rewrite [foo](bar.md) → [foo](https://notion.so/<id>),
    #            compute sha256, SKIP if (reused page AND hash matches prior),
    #            otherwise wipe-and-append blocks.
    # Preserve unrelated entries from prior mapping (e.g. Feedback page) so they survive.
    # Only file-derived stems will be overwritten by this export.
    mapping: Dict = {}
    file_stems = {f.stem for f in files}
    for k, v in prior_mapping_raw.items():
        if k not in file_stems:
            mapping[k] = v

    # Pass 1 — allocate pages and build link_map (stem → page_id).
    # Track was_reused so Pass 2 can skip the redundant page_is_alive() call.
    print("\nPass 1: allocating pages...")
    link_map: Dict[str, str] = {}
    pass2_state: Dict[str, Tuple[str, bool]] = {}  # stem → (page_id, was_reused)
    prior_hash_for: Dict[str, Optional[str]] = {}
    for filepath in files:
        prior_pid, prior_hash = parse_mapping_entry(prior_mapping_raw.get(filepath.stem))
        prior_hash_for[filepath.stem] = prior_hash
        try:
            page_id, was_reused = ensure_page_exists(headers, parent_page_id, filepath,
                                                      existing_page_id=prior_pid)
            link_map[filepath.stem] = page_id
            pass2_state[filepath.stem] = (page_id, was_reused)
        except Exception as e:
            print(f"  ERROR allocating page for {filepath.name}: {e}")
            if prior_pid:
                # Surface stale entry so retries can heal next run.
                mapping[filepath.stem] = {"page_id": prior_pid, "sha256": prior_hash}

    # Pass 2 — upload content with cross-link rewriting + content-hash skip-if-unchanged.
    print("\nPass 2: uploading content (with cross-link rewriting + hash skip)...")
    skipped = 0
    uploaded = 0
    for filepath in files:
        state = pass2_state.get(filepath.stem)
        if state is None:
            print(f"  SKIP {filepath.name} — no page_id from Pass 1")
            continue
        page_id, was_reused = state
        try:
            # Render once (file read + cross-link rewrite + sha256), then decide.
            content, content_hash = render_content(filepath, link_map=link_map)

            prior_hash = prior_hash_for.get(filepath.stem)
            unchanged = (was_reused
                         and prior_hash is not None
                         and prior_hash == content_hash
                         and not force_upload)
            if unchanged:
                print(f"  SKIP {filepath.name} — content unchanged (sha256 match)")
                skipped += 1
            else:
                export_file_content(headers, page_id, filepath, wipe_first=was_reused,
                                    rendered_content=content)
                uploaded += 1

            # Always update mapping with current page_id + hash (canonical state).
            mapping[filepath.stem] = {"page_id": page_id, "sha256": content_hash}
        except Exception as e:
            print(f"  ERROR uploading {filepath.name}: {e}")
            # Preserve last-known-good entry so a future retry can resume.
            if state:
                mapping[filepath.stem] = {"page_id": page_id, "sha256": prior_hash_for.get(filepath.stem)}

    print(f"\nPass 2 summary: {uploaded} uploaded, {skipped} skipped (unchanged)")

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

    # ----- Finalize engagement cover -----------------------------------------
    # Rebuild cover with real link_map + feedback_page_id, then PATCH each
    # skeleton block in place (preserves top-of-page position) OR recreate
    # if structure changed (lands at end of page on re-runs).
    print("\nFinalizing engagement cover...")
    final_cover_blocks = build_cover_blocks_for(engagement_type, engagement_meta,
                                                 verdict_data, link_map, feedback_page_id)
    cover_state = update_cover(headers, parent_page_id, final_cover_blocks, cover_state)

    # Save metadata (preserves engagement_page_id + cover_block_ids for future runs)
    save_notion_meta(research_dir, mapping, feedback_page_id, parent_page_id, cover_state)

    print(f"\nDone! Parent page: https://notion.so/{parent_page_id.replace('-', '')}")


if __name__ == "__main__":
    main()
