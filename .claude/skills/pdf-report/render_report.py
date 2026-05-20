#!/usr/bin/env python3
"""
render_report.py — Xata&co PDF Report Renderer

Converts any markdown report into a Bridgewater-style PDF in Xata&co brand colors.

Usage:
    python render_report.py <input.md>
    python render_report.py <input.md> -o output.pdf
    python render_report.py <input.md> --mode dd       # DD-aware (verdict, risks, value bridge)
    python render_report.py <input.md> --mode bcg      # BCG-aware (MBB matrix)
    python render_report.py <input.md> --mode generic  # universal (default)
    python render_report.py <input.md> --title "..." --subtitle "..." --company "Nvidia"

Stack:
    markdown-it-py → HTML → Jinja2 → Chrome headless --print-to-pdf
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Optional

try:
    from markdown_it import MarkdownIt
except ImportError:
    sys.exit("[fatal] missing dependency: pip install markdown-it-py")

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    sys.exit("[fatal] missing dependency: pip install jinja2")


SKILL_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SKILL_DIR / "templates"
ASSETS_DIR = SKILL_DIR / "assets"
CSS_XATA = ASSETS_DIR / "css" / "xata.css"
CSS_PRINT = ASSETS_DIR / "css" / "print.css"


# ──────────────────────────────────────────────────────────────────────
# Markdown → HTML
# ──────────────────────────────────────────────────────────────────────

_MD = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True}).enable("table")

# Box-drawing / divider characters often used as decorative section breaks
_DECOR_CHARS = "━─═‒–—═▬▔▁▂▃▄▅▆▇█▌▐▝▘▗▖▙▚▛▜▟□■◼◻⬛⬜▰▱·•∙·* "

def _is_decorative_heading(title: str) -> bool:
    """A heading is decorative if every char is a divider/box-drawing/whitespace char."""
    s = title.strip()
    if len(s) < 3:
        return False
    return all(c in _DECOR_CHARS for c in s)

def strip_decorative_headings(text: str) -> str:
    """Replace `# ━━━` and similar lines with horizontal-rule markers."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m and _is_decorative_heading(m.group(2)):
            # Collapse two consecutive decorative headings into a single <hr>
            if out and out[-1].strip() in ("---", ""):
                continue
            out.append("---")
            continue
        out.append(line)
    return "\n".join(out)


def md_to_html(text: str) -> str:
    return _MD.render(text)


# ──────────────────────────────────────────────────────────────────────
# Verdict detection (PROCEED / CONDITIONAL / PASS)
# ──────────────────────────────────────────────────────────────────────

_VERDICT_PATTERNS = [
    (r"\bPROCEED\b",       "PROCEED",     "proceed"),
    (r"\bCONDITIONAL\b",   "CONDITIONAL", "conditional"),
    (r"\bPASS\b",          "PASS",        "pass"),
    (r"\bПРОДОЛЖИТЬ\b",    "PROCEED",     "proceed"),
    (r"\bУСЛОВНО\b",       "CONDITIONAL", "conditional"),
    (r"\bОТКАЗАТЬ?\b",     "PASS",        "pass"),
    (r"\bОТКАЗ\b",         "PASS",        "pass"),
]

def detect_verdict(text: str) -> Optional[dict]:
    """Find the first verdict mention in early sections (cover / TL;DR / Verdict)."""
    head = text[:6000]
    for pat, value, klass in _VERDICT_PATTERNS:
        if re.search(pat, head):
            return {"label": "Verdict", "value": value, "klass": klass}
    return None


# ──────────────────────────────────────────────────────────────────────
# Front-matter parser (optional YAML between --- markers)
# ──────────────────────────────────────────────────────────────────────

def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# ──────────────────────────────────────────────────────────────────────
# Title extraction
# ──────────────────────────────────────────────────────────────────────

def extract_h1(text: str) -> Optional[str]:
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else None


# ──────────────────────────────────────────────────────────────────────
# Section splitting — break body on H1, optionally H2 too
# ──────────────────────────────────────────────────────────────────────

def split_into_sections(html: str, columns: bool = False, top_tag: str = "h1") -> list[dict]:
    """Split into top-level sections. Each section gets a page break."""
    pattern = rf'(?=<{top_tag}[^>]*>)'
    parts = re.split(pattern, html)
    out = []
    for p in parts:
        if not p.strip():
            continue
        out.append({"html": p, "columns": columns})
    if not out:
        out = [{"html": html, "columns": columns}]
    return out


def pick_top_heading_level(text: str) -> int:
    """Return 1 if body has ≥2 H1s, else 2 (use H2 as section-break level)."""
    h1_count = len(re.findall(r"^#\s+\S", text, re.M))
    return 1 if h1_count >= 2 else 2


def promote_h2_to_h1_css(html: str) -> str:
    """When top-level is H2, give it H1-like styling (page break + 24pt) via a class."""
    return re.sub(r"<h2(\s[^>]*)?>", r'<h2 class="top-h2"\1>', html)


# ──────────────────────────────────────────────────────────────────────
# TOC generation
# ──────────────────────────────────────────────────────────────────────

def build_toc(text: str, top_level: int = 1) -> list[dict]:
    """Build a 2-level TOC. top_level is the heading level treated as top-level (1 or 2)."""
    toc = []
    num_top = 0
    num_sub = 0
    sub_level = top_level + 1
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not m:
            continue
        level = len(m.group(1))
        title = re.sub(r"[`*_]", "", m.group(2)).strip()
        if level == top_level:
            num_top += 1
            num_sub = 0
            toc.append({"level": 1, "num": f"{num_top:02d}", "title": title})
        elif level == sub_level and num_top > 0:
            num_sub += 1
            toc.append({"level": 2, "num": f"{num_top}.{num_sub}", "title": title})
    return toc


# ──────────────────────────────────────────────────────────────────────
# HTML post-processing — callouts, badges, figures
# ──────────────────────────────────────────────────────────────────────

# Common phrases that mark a "So what?" anchor
_SO_WHAT_RX = re.compile(
    r"<blockquote>\s*<p>\s*(?:<strong>)?\s*(?:so what\??|и что\??|so what:)\s*",
    re.I,
)

def post_process_html(html: str, mode: str) -> str:
    # Tag blockquotes that start with "Key Takeaways" / "Ключевые выводы" / "TL;DR"
    def _tag_callouts(h: str) -> str:
        # Key Takeaways
        h = re.sub(
            r"<blockquote>\s*<p>\s*<strong>\s*(Key Takeaways?|Ключевые выводы|TL;DR|Главное)\s*[:：]?\s*</strong>",
            r'<div class="callout key-takeaways"><span class="callout-label">\1</span><p>',
            h,
            flags=re.I,
        )
        # So what?
        h = re.sub(
            r"<blockquote>\s*<p>\s*<strong>\s*(So what\??|И что\??)\s*[:：]?\s*</strong>",
            r'<div class="callout so-what"><span class="callout-label">\1</span><p>',
            h,
            flags=re.I,
        )
        # Critical Risk
        h = re.sub(
            r"<blockquote>\s*<p>\s*<strong>\s*(Critical Risk|Критический риск)\s*[:：]?\s*</strong>",
            r'<div class="callout risk-critical"><span class="callout-label">\1</span><p>',
            h,
            flags=re.I,
        )
        # High Risk
        h = re.sub(
            r"<blockquote>\s*<p>\s*<strong>\s*(High Risk|Высокий риск)\s*[:：]?\s*</strong>",
            r'<div class="callout risk-high"><span class="callout-label">\1</span><p>',
            h,
            flags=re.I,
        )
        # Close any opened callout divs (replace the closing </blockquote> that follows)
        # We do this naively — for every <div class="callout"> we leave the next </blockquote>
        # to be replaced. Simpler: replace all remaining </blockquote> that follow our callout divs.
        # Safer: do a pass that replaces </blockquote> with </div> ONLY if the most recent
        # opening tag is our callout div.
        return _close_callouts(h)

    html = _tag_callouts(html)

    # Verdict badges in text
    badge_patterns = [
        (r"\bPROCEED\b",       '<span class="badge badge-proceed">PROCEED</span>'),
        (r"\bCONDITIONAL\b",   '<span class="badge badge-conditional">CONDITIONAL</span>'),
        (r"(?<![A-Z])PASS(?![A-Z])", '<span class="badge badge-pass">PASS</span>'),
    ]
    # Only apply badges inside table cells to avoid messing up running prose
    def _badge_in_tds(h: str) -> str:
        def repl(m):
            cell = m.group(0)
            for pat, badge in badge_patterns:
                cell = re.sub(pat, badge, cell)
            return cell
        return re.sub(r"<td[^>]*>.*?</td>", repl, h, flags=re.DOTALL)
    html = _badge_in_tds(html)

    # Severity chips in table cells: Critical / High / Medium / Low
    def _severity_in_tds(h: str) -> str:
        sev_map = [
            (r"\bCritical\b",     '<span class="badge badge-critical">Critical</span>'),
            (r"\bКритический\b",  '<span class="badge badge-critical">Критический</span>'),
            (r"\bHigh\b",         '<span class="badge badge-high">High</span>'),
            (r"\bВысокий\b",      '<span class="badge badge-high">Высокий</span>'),
            (r"\bMedium\b",       '<span class="badge badge-medium">Medium</span>'),
            (r"\bСредний\b",      '<span class="badge badge-medium">Средний</span>'),
            (r"\bLow\b",          '<span class="badge badge-low">Low</span>'),
            (r"\bНизкий\b",       '<span class="badge badge-low">Низкий</span>'),
        ]
        def repl(m):
            cell = m.group(0)
            # heuristic — only apply badges if cell looks like a severity column
            # (short text, no other punctuation-heavy content)
            inner = re.sub(r"<[^>]+>", "", cell)
            if len(inner.strip()) > 25:
                return cell
            for pat, badge in sev_map:
                cell = re.sub(pat, badge, cell)
            return cell
        return re.sub(r"<td[^>]*>.*?</td>", repl, h, flags=re.DOTALL)
    html = _severity_in_tds(html)

    # BCG status badges in table cells (only when --mode bcg or generic)
    if mode in ("bcg", "generic"):
        bcg_badges = [
            (r"⭐\s*Звезда|Звезда\s*⭐|\bStar\b",       '<span class="badge badge-star">⭐ Star</span>'),
            (r"🐄\s*Дойная корова|Cash Cow|Дойная",   '<span class="badge badge-cow">🐄 Cash Cow</span>'),
            (r"❓\s*Трудный ребёнок|Question Mark",   '<span class="badge badge-q">❓ Question</span>'),
            (r"🐕\s*Собака|\bDog\b|🐕",                 '<span class="badge badge-dog">🐕 Dog</span>'),
        ]
        def _bcg_repl(m):
            cell = m.group(0)
            inner = re.sub(r"<[^>]+>", "", cell)
            if len(inner.strip()) > 40:
                return cell
            for pat, badge in bcg_badges:
                cell = re.sub(pat, badge, cell)
            return cell
        html = re.sub(r"<td[^>]*>.*?</td>", _bcg_repl, html, flags=re.DOTALL)

    return html


def _close_callouts(html: str) -> str:
    """For every <div class='callout ...'> opened (which replaced <blockquote>),
    close the corresponding </blockquote> with </div></div>."""
    out = []
    open_callouts = 0
    i = 0
    while i < len(html):
        if html[i:i+25].startswith('<div class="callout'):
            open_callouts += 1
        if open_callouts > 0 and html[i:i+13] == "</blockquote>":
            out.append("</div>")  # close inner <p> implicit? we left a <p> open — handle below
            open_callouts -= 1
            i += 13
            continue
        out.append(html[i])
        i += 1
    return "".join(out)


# ──────────────────────────────────────────────────────────────────────
# MBB Growth-Share Matrix (ported from agents/render_pdf.py, restyled)
# ──────────────────────────────────────────────────────────────────────

def parse_segments(text: str) -> dict:
    segs = {"stars": [], "cows": [], "questions": [], "dogs": []}
    seen = set()
    star_kw = ["звезда", "star", "⭐"]
    cow_kw  = ["дойная корова", "cash cow", "🐄"]
    q_kw    = ["трудный ребёнок", "question mark", "❓"]
    dog_kw  = ["собака", "dog", "🐕"]
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        name = re.sub(r"\*+", "", cols[0]).strip()
        status = cols[1].lower()
        rev_raw = cols[2] if len(cols) > 2 else ""
        if not name or name.lower() in ("сегмент", "segment", "---", ""):
            continue
        key = name.lower()[:20]
        if key in seen:
            continue
        seen.add(key)
        m = re.search(r"~?\$?([\d,.]+)\s*(?:–[\d,.]+)?\s*(?:млрд|billion|b\b|трлн|trln)", rev_raw, re.I)
        rev = float(m.group(1).replace(",", "")) if m else 1.0
        seg = {"name": name[:32], "revenue": rev}
        if   any(k in status for k in star_kw): segs["stars"].append(seg)
        elif any(k in status for k in cow_kw):  segs["cows"].append(seg)
        elif any(k in status for k in q_kw):    segs["questions"].append(seg)
        elif any(k in status for k in dog_kw):  segs["dogs"].append(seg)
    return segs


def _place(items, x0, y0, x1, y1):
    n = len(items)
    if not n: return []
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    return [
        (x0 + (x1 - x0) * ((i % cols) + 1) / (cols + 1),
         y0 + (y1 - y0) * ((i // cols) + 1) / (rows + 1), s)
        for i, s in enumerate(items)
    ]


def _bubbles(pos, fill, max_rev):
    out = []
    for cx, cy, s in pos:
        r = max(20, min(44, 14 + (s["revenue"] / max(max_rev, 1)) * 30))
        words = s["name"].split()
        lines, ln = [], ""
        for w in words:
            if len(ln) + len(w) + 1 <= 13:
                ln = (ln + " " + w).strip()
            else:
                if ln: lines.append(ln)
                ln = w
        if ln: lines.append(ln)
        lines = lines[:3]
        out.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{fill}" '
            f'fill-opacity="0.92" stroke="white" stroke-width="2"/>'
        )
        dy = cy - (len(lines) - 1) * 6 + 3
        for j, l in enumerate(lines):
            out.append(
                f'<text x="{cx:.0f}" y="{dy + j*11:.0f}" text-anchor="middle" '
                f'font-family="Geist,sans-serif" font-size="9" font-weight="600" fill="white">{l}</text>'
            )
    return "\n".join(out)


def generate_mbb_matrix_svg(segs: dict) -> str:
    """MBB Growth-Share Matrix — Xata-restyled (green + neutral palette)."""
    all_s = segs["stars"] + segs["cows"] + segs["questions"] + segs["dogs"]
    if not all_s:
        return ""
    mx = max(s["revenue"] for s in all_s)
    W, H, MX, MY = 800, 500, 400, 250

    # Quadrant tints — restrained Xata palette
    bg = (
        f'<rect x="20" y="20" width="{MX-20}" height="{MY-20}" rx="6" fill="#EAF6F0"/>'
        f'<rect x="{MX}" y="20" width="{W-MX-10}" height="{MY-20}" rx="6" fill="#F6F6F4"/>'
        f'<rect x="20" y="{MY}" width="{MX-20}" height="{H-MY-10}" rx="6" fill="#F0F4F8"/>'
        f'<rect x="{MX}" y="{MY}" width="{W-MX-10}" height="{H-MY-10}" rx="6" fill="#F8EFEC"/>'
    )

    axes = (
        f'<line x1="{MX}" y1="12" x2="{MX}" y2="{H-8}" stroke="#0f0f0d" stroke-width="1" '
        f'stroke-opacity="0.3" stroke-dasharray="4,3"/>'
        f'<line x1="12" y1="{MY}" x2="{W-8}" y2="{MY}" stroke="#0f0f0d" stroke-width="1" '
        f'stroke-opacity="0.3" stroke-dasharray="4,3"/>'
    )

    labels = (
        f'<text x="{W//2}" y="13" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
        f'font-size="9" fill="#6b6b67" letter-spacing="1">← HIGH SHARE  ·  LOW SHARE →</text>'
        f'<text x="11" y="{H//2}" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
        f'font-size="9" fill="#6b6b67" letter-spacing="1" transform="rotate(-90,11,{H//2})">↑ HIGH GROWTH</text>'
    )

    titles = (
        f'<text x="{(20+MX)//2}" y="44" text-anchor="middle" font-family="Geist,sans-serif" '
        f'font-size="11" font-weight="700" fill="#16A06B">★ STARS</text>'
        f'<text x="{(MX+W-10)//2}" y="44" text-anchor="middle" font-family="Geist,sans-serif" '
        f'font-size="11" font-weight="700" fill="#C28A1E">? QUESTION MARKS</text>'
        f'<text x="{(20+MX)//2}" y="{MY+20}" text-anchor="middle" font-family="Geist,sans-serif" '
        f'font-size="11" font-weight="700" fill="#2F6FBF">$ CASH COWS</text>'
        f'<text x="{(MX+W-10)//2}" y="{MY+20}" text-anchor="middle" font-family="Geist,sans-serif" '
        f'font-size="11" font-weight="700" fill="#B5331A">× DOGS</text>'
    )

    bubbles = (
        _bubbles(_place(segs["stars"],     22,  48, MX-2, MY-2),     "#16A06B", mx) +
        _bubbles(_place(segs["questions"], MX+2, 48, W-12, MY-2),    "#C28A1E", mx) +
        _bubbles(_place(segs["cows"],      22, MY+28, MX-2, H-12),   "#2F6FBF", mx) +
        _bubbles(_place(segs["dogs"],      MX+2, MY+28, W-12, H-12), "#B5331A", mx)
    )

    return (
        f'<div class="figure">'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:100%;display:block;margin:0 auto">'
        f'{bg}{axes}{labels}{titles}{bubbles}'
        f'</svg>'
        f'<div class="figure-caption"><span class="label">Figure 1</span>'
        f'MBB Growth-Share Matrix · bubble size proportional to revenue</div>'
        f'</div>'
    )


def maybe_inject_matrix(html: str, raw_md: str, mode: str) -> str:
    """If mode permits, parse segments and replace any ASCII-art matrix block."""
    if mode not in ("bcg", "generic"):
        return html
    segs = parse_segments(raw_md)
    svg = generate_mbb_matrix_svg(segs)
    if not svg:
        return html
    def repl(m):
        content = m.group(0)
        if re.search(r"(?i)(STARS?|ЗВЁЗД|CASH\s*COW|ДОЙН|QUESTION|DOG|СОБАК)", content):
            return svg
        return content
    return re.sub(r"<pre><code[^>]*>.*?</code></pre>", repl, html, flags=re.DOTALL)


# ──────────────────────────────────────────────────────────────────────
# Chrome PDF rendering
# ──────────────────────────────────────────────────────────────────────

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    for cmd in ("google-chrome", "chromium", "chrome"):
        p = shutil.which(cmd)
        if p:
            return p
    sys.exit("[fatal] Chrome/Chromium not found")


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = find_chrome()
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        sys.exit("[fatal] Chrome timed out after 180s — likely a font CDN hang. "
                 "Re-run with --keep-html and inspect the HTML.")
    if result.returncode != 0 or not pdf_path.exists():
        sys.stderr.write(result.stderr or result.stdout or "")
        sys.exit(f"[fatal] Chrome failed to render PDF (exit {result.returncode})")


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def humanize_company(name: str) -> str:
    if not name:
        return ""
    parts = re.split(r"[-_]", name)
    return " ".join(p.capitalize() for p in parts if p)


def main():
    ap = argparse.ArgumentParser(description="Xata&co PDF Report Renderer")
    ap.add_argument("input", help="Path to source .md file")
    ap.add_argument("-o", "--output", help="Output PDF path (default: <input>.pdf)")
    ap.add_argument("--mode", choices=["dd", "bcg", "generic"], default="generic",
                    help="Report type — affects section detection and visuals")
    ap.add_argument("--company", default=None, help="Company name (cover)")
    ap.add_argument("--title", default=None, help="Override cover title")
    ap.add_argument("--subtitle", default=None, help="Cover subtitle / one-line summary")
    ap.add_argument("--eyebrow", default=None, help="Small label above title")
    ap.add_argument("--lang", default=None, help="Document language (auto-detected if omitted)")
    ap.add_argument("--no-toc", action="store_true", help="Skip table of contents")
    ap.add_argument("--keep-html", action="store_true", help="Keep intermediate .html next to PDF")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.exists():
        sys.exit(f"[fatal] file not found: {src}")
    out = Path(args.output).resolve() if args.output else src.with_suffix(".pdf")

    raw = src.read_text(encoding="utf-8")
    fm, body = split_front_matter(raw)
    body = strip_decorative_headings(body)

    # Auto-detect mode from filename if not explicitly set
    fname = src.name.lower()
    mode = args.mode
    if mode == "generic":
        if "dd-" in fname or fname.startswith("dd-"):
            mode = "dd"
        elif "final-report" in fname or "gtm-playbook" in fname or "portfolio" in fname:
            mode = "bcg"

    # Cover metadata
    company = args.company or fm.get("company") or humanize_company(src.parent.name.split("-")[0]) or "Company"
    h1 = extract_h1(body) or f"{company} — Strategic Report"
    title = args.title or fm.get("title") or h1
    cover_title = title

    subtitle_default = {
        "dd": "Strategic Due Diligence · Investment-grade analysis",
        "bcg": "MBB Strategic Analysis · Portfolio recommendations",
        "generic": "Research Report",
    }[mode]
    subtitle = args.subtitle or fm.get("subtitle") or subtitle_default

    eyebrow_default = {
        "dd": "STRATEGIC DUE DILIGENCE",
        "bcg": "MBB STRATEGIC ANALYSIS",
        "generic": "RESEARCH REPORT",
    }[mode]
    eyebrow = args.eyebrow or fm.get("eyebrow") or eyebrow_default

    # Verdict (DD-mode primarily)
    verdict = detect_verdict(body) if mode == "dd" else None

    # Cover bottom meta blocks
    today = fm.get("date") or date.today().isoformat()
    cover_meta = [
        {"label": "Date",       "value": today},
        {"label": "Document",   "value": src.name},
        {"label": "Prepared by", "value": "Xata&co"},
        {"label": "Status",     "value": "Confidential"},
    ]

    # Lang auto-detect (very rough)
    lang = args.lang or fm.get("lang")
    if not lang:
        cyr = sum(1 for c in body[:2000] if "Ѐ" <= c <= "ӿ")
        lat = sum(1 for c in body[:2000] if c.isalpha() and c.isascii())
        lang = "ru" if cyr > lat else "en"

    # Strip leading H1 so it doesn't duplicate the cover title
    body_no_h1 = re.sub(r"^#\s+.+?\n", "", body, count=1, flags=re.M)

    # Pick top-level heading: H1 if doc has multiple H1s, else H2
    top_level = pick_top_heading_level(body_no_h1)
    top_tag = f"h{top_level}"

    # TOC — skip for very short docs (≤2 entries) to avoid a near-empty TOC page
    toc = [] if args.no_toc else build_toc(body_no_h1, top_level=top_level)
    if len(toc) < 3:
        toc = []

    # Render HTML body
    html = md_to_html(body_no_h1)
    html = post_process_html(html, mode)
    html = maybe_inject_matrix(html, body_no_h1, mode)
    if top_level == 2:
        html = promote_h2_to_h1_css(html)

    sections = split_into_sections(html, columns=False, top_tag=top_tag)

    # Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template("base.html")

    # Running title for @top-right (truncated, CSS-string-safe)
    running_title = re.sub(r'["\\]', "", company or title or "")[:60]

    full_html = tpl.render(
        lang=lang,
        title=title,
        cover_title=cover_title,
        subtitle=subtitle,
        eyebrow=eyebrow,
        meta_tag={"dd": "Due Diligence", "bcg": "Strategic Analysis", "generic": "Research"}[mode],
        verdict=verdict,
        cover_meta=cover_meta,
        toc=toc,
        sections=sections,
        running_title=running_title,
        css_xata=CSS_XATA.as_uri(),
        css_print=CSS_PRINT.as_uri(),
    )

    # Write intermediate HTML
    html_path = out.with_suffix(".html") if args.keep_html else Path(tempfile.mkstemp(suffix=".html")[1])
    html_path.write_text(full_html, encoding="utf-8")

    # Render PDF
    print(f"[info] mode={mode} lang={lang} sections={len(sections)} toc={len(toc)}")
    print(f"[info] rendering PDF → {out}")
    html_to_pdf(html_path, out)

    if args.keep_html:
        print(f"[info] kept HTML → {html_path}")
    else:
        try:
            html_path.unlink()
        except OSError:
            pass

    print(f"[done] {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
