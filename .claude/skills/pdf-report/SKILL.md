---
name: pdf-report
description: Convert any markdown report into a beautiful Bridgewater-style PDF in Xata&co brand colors. Use when user asks "make a PDF", "render PDF", "красивый PDF", "/pdf <file.md>", or after /dd / /bcg-team completes. Universal markdown support + auto-detects DD reports (Verdict badge, Risk Matrix, Value Bridge) and BCG reports (MBB Growth-Share Matrix SVG, segment status chips).
---

# PDF Report Skill — Xata&co

Converts any markdown report into a beautifully typeset PDF in the style of
**Bridgewater Research** (institutional research format) using the **Xata&co**
brand palette: green `#16A06B` accent on white/cream background, Geist sans
+ IBM Plex Mono.

## When to use this skill

| Trigger | What to do |
|---|---|
| User types `/pdf <file.md>` | Run the script on the file |
| User says "make a PDF" / "красивый PDF" / "render PDF" of an MD report | Identify the source MD, run the script |
| Just finished `/dd` engagement | Run on `dd-decision-first.md`, `dd-mid.md`, `dd-short.md`, and `dd-report.md` |
| Just finished `/bcg-team` engagement | Run on `final-report.md` (and `gtm-playbook.md` if present) |

## Usage

```bash
# Basic (auto-detects mode from filename)
python3 .claude/skills/pdf-report/render_report.py <input.md>

# Explicit mode and metadata
python3 .claude/skills/pdf-report/render_report.py <input.md> \
  --mode dd \
  --company "NVIDIA" \
  --subtitle "Strategic Due Diligence · 24 March 2026"

# All flags
python3 .claude/skills/pdf-report/render_report.py <input.md> \
  -o <output.pdf>           # output path (default: <input>.pdf)
  --mode dd|bcg|generic     # report type (auto-detected if omitted)
  --company "NVIDIA"        # company name for cover
  --title "..."             # override cover title
  --subtitle "..."          # cover one-liner
  --eyebrow "..."           # small label above title
  --lang en|ru              # document language (auto-detected if omitted)
  --no-toc                  # skip table of contents
  --keep-html               # keep intermediate .html next to PDF (for debugging)
```

## Mode auto-detection

The script picks `--mode` from the source filename if not given:

- `dd-*.md` → `--mode dd` (renders Verdict badge, severity chips, "So what?" callouts)
- `final-report.md`, `gtm-playbook.md`, `portfolio.md` → `--mode bcg` (renders MBB Growth-Share Matrix from segment tables, status chips)
- anything else → `--mode generic` (universal markdown rendering)

## What the renderer does

1. **Parse front-matter** (YAML between `---` markers, optional)
2. **Strip decorative headings** like `# ━━━` (visual separators) → `<hr>`
3. **Detect verdict** (PROCEED / CONDITIONAL / PASS / ПРОДОЛЖИТЬ / УСЛОВНО / ОТКАЗ) in DD mode → cover badge
4. **Extract H1** for cover title
5. **Build TOC** from H1/H2
6. **markdown-it-py** → HTML (CommonMark + tables + typographer)
7. **Post-process**: callouts (Key Takeaways, So what?, Critical/High Risk), severity chips in tables, BCG status badges, MBB matrix SVG injection
8. **Jinja2 template** → full HTML doc with cover + TOC + sections
9. **Chrome headless** → PDF via `--print-to-pdf`

## Visual identity

- **Cover**: huge `52pt` Geist title, eyebrow tag with thin accent line, vertical accent bar on left edge, 4-column meta footer
- **Body**: A4 portrait, single column by default, justified text with hyphenation
- **H1**: page break + 24pt with full-width underline
- **H2**: green accent color `#16A06B`
- **Tables**: monospace UPPERCASE headers with top+bottom border (Bloomberg-terminal style)
- **Callouts**: `> Key Takeaways:` → green-bordered left-accent box; `> So what?:` → arrow callout
- **Footer**: `page X / Y · Xata&co · Confidential`

## Generic markdown features supported

All standard markdown: H1–H6, paragraphs, bold/italic, inline code, fenced code
blocks, tables, blockquotes, ordered/unordered lists, horizontal rules, links.

## Output

PDF is written next to the source MD by default (e.g. `dd-decision-first.md` → `dd-decision-first.pdf`).
Use `-o` to override. With `--keep-html`, a sibling `.html` file is also saved for debugging.

## Dependencies

- Python: `markdown-it-py`, `jinja2` (both standard in this repo)
- System: Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (or `chromium` in PATH)
- No network required at render time (fonts use system fallbacks)

## Files

```
.claude/skills/pdf-report/
  SKILL.md                  ← this file
  render_report.py          ← main script
  templates/
    base.html               ← Jinja2 cover + TOC + body skeleton
  assets/css/
    xata.css                ← Xata&co brand palette + base typography
    print.css               ← @page rules, page breaks, Bridgewater layout
```

## Integration points

- **/dd pipeline**: invoke after Phase DD-3b on all four decision layers
- **/bcg-team pipeline**: invoke after Phase 3 on `final-report.md` (replaces legacy `bcg-pdf-designer`)
- **Standalone**: type `/pdf <path>` or run the script directly
