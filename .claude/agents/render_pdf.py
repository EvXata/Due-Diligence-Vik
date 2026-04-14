#!/usr/bin/env python3
"""MBB PDF Renderer — 16:9 presentation slides from markdown reports"""

import re, sys
from pathlib import Path

try:
    from markdown_it import MarkdownIt
    _md = MarkdownIt("commonmark", {"html": True}).enable("table")
    HAS_MDIT = True
except Exception:
    HAS_MDIT = False

OUTPUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
COMPANY    = sys.argv[2] if len(sys.argv) > 2 else "Company"


# ─────────────────────────────────────────────────────────────
# SEGMENT PARSER
# ─────────────────────────────────────────────────────────────

def parse_segments(text):
    segs = {"stars": [], "cows": [], "questions": [], "dogs": []}
    seen = set()  # deduplicate by name
    star_kw = ["звезда", "star", "⭐"]
    cow_kw  = ["дойная корова", "корова", "cash cow", "🐄"]
    q_kw    = ["трудный ребёнок", "вопрос", "question mark", "❓"]
    dog_kw  = ["собака", "пёс", "dog", "🐕"]

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        name    = re.sub(r"\*+", "", cols[0]).strip()
        status  = cols[1].lower()
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


# ─────────────────────────────────────────────────────────────
# MBB MATRIX SVG
# ─────────────────────────────────────────────────────────────

def _place(items, x0, y0, x1, y1):
    n = len(items)
    if not n: return []
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    return [
        (x0 + (x1-x0)*((i%cols)+1)/(cols+1),
         y0 + (y1-y0)*((i//cols)+1)/(rows+1), s)
        for i, s in enumerate(items)
    ]

def _bubbles(pos, fill, max_rev):
    out = []
    for cx, cy, s in pos:
        r = max(22, min(48, 16 + (s["revenue"]/max(max_rev,1))*32))
        words = s["name"].split()
        lines, ln = [], ""
        for w in words:
            if len(ln)+len(w)+1 <= 13: ln = (ln+" "+w).strip()
            else:
                if ln: lines.append(ln)
                ln = w
        if ln: lines.append(ln)
        lines = lines[:3]
        out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{fill}" fill-opacity="0.88" stroke="white" stroke-width="2"/>')
        dy = cy - (len(lines)-1)*6 + 3
        for j, l in enumerate(lines):
            out.append(f'<text x="{cx:.0f}" y="{dy+j*11:.0f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="9" font-weight="bold" fill="white">{l}</text>')
    return "\n".join(out)

def generate_bcg_matrix_svg(segs):
    all_s = segs["stars"]+segs["cows"]+segs["questions"]+segs["dogs"]
    if not all_s: return ""
    mx = max(s["revenue"] for s in all_s)
    W, H, MX, MY = 800, 500, 400, 250

    bg = (f'<rect x="20" y="20" width="{MX-20}" height="{MY-20}" rx="6" fill="#EBF7F0"/>'
          f'<rect x="{MX}" y="20" width="{W-MX-10}" height="{MY-20}" rx="6" fill="#FEF9EE"/>'
          f'<rect x="20" y="{MY}" width="{MX-20}" height="{H-MY-10}" rx="6" fill="#EBF2FA"/>'
          f'<rect x="{MX}" y="{MY}" width="{W-MX-10}" height="{H-MY-10}" rx="6" fill="#FDEAEA"/>')

    axes = (f'<line x1="{MX}" y1="12" x2="{MX}" y2="{H-8}" stroke="#C0CAD4" stroke-width="1.5" stroke-dasharray="5,3"/>'
            f'<line x1="12" y1="{MY}" x2="{W-8}" y2="{MY}" stroke="#C0CAD4" stroke-width="1.5" stroke-dasharray="5,3"/>')

    labels = (f'<text x="{W//2}" y="13" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="#888">← Высокая доля рынка · · · Низкая →</text>'
              f'<text x="11" y="{H//2}" text-anchor="middle" font-family="Arial,sans-serif" font-size="10" fill="#888" transform="rotate(-90,11,{H//2})">↑ Высокий рост</text>')

    titles = (f'<text x="{(20+MX)//2}" y="44" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="#1C6B3A">⭐ ЗВЁЗДЫ</text>'
              f'<text x="{(MX+W-10)//2}" y="44" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="#C05A00">❓ ТРУДНЫЕ ДЕТИ</text>'
              f'<text x="{(20+MX)//2}" y="{MY+20}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="#1355A0">🐄 ДОЙНЫЕ КОРОВЫ</text>'
              f'<text x="{(MX+W-10)//2}" y="{MY+20}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="bold" fill="#A01010">🐕 СОБАКИ</text>')

    bubbles = (
        _bubbles(_place(segs["stars"],     22,  48, MX-2, MY-2),  "#1C8A46", mx) +
        _bubbles(_place(segs["questions"], MX+2, 48, W-12, MY-2), "#E07B00", mx) +
        _bubbles(_place(segs["cows"],      22, MY+28, MX-2, H-12), "#2B6CB0", mx) +
        _bubbles(_place(segs["dogs"],      MX+2, MY+28, W-12, H-12), "#C53030", mx)
    )

    return (f'<div class="bcg-matrix-wrap"><p class="bcg-matrix-title">MBB Growth-Share Matrix</p>'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;display:block;margin:0 auto">'
            f'{bg}{axes}{labels}{titles}{bubbles}</svg></div>')


# ─────────────────────────────────────────────────────────────
# MARKDOWN → HTML
# ─────────────────────────────────────────────────────────────

def md_to_html(text):
    if HAS_MDIT:
        return _md.render(text)
    h = text
    for n in range(6, 0, -1):
        h = re.sub(r'^#{%d}\s+(.+)$'%n, r'<h%d>\1</h%d>'%(n,n), h, flags=re.M)
    h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
    h = re.sub(r'\*(.+?)\*', r'<em>\1</em>', h)
    h = re.sub(r'`(.+?)`', r'<code>\1</code>', h)
    h = re.sub(r'\n\n+', '</p><p>', h)
    return f'<p>{h}</p>'


# ─────────────────────────────────────────────────────────────
# POST-PROCESS
# ─────────────────────────────────────────────────────────────

def post_process(html, matrix_svg):
    # Tables
    html = html.replace("<table>",      '<table class="bcg-table">')
    html = html.replace("<thead>",      '<thead class="bcg-thead">')
    html = html.replace("<tbody>",      '<tbody class="bcg-tbody">')
    html = html.replace("<blockquote>", '<blockquote class="bcg-card">')
    html = html.replace("<hr>",         '<hr class="bcg-hr">')
    html = html.replace("<hr />",       '<hr class="bcg-hr">')

    # Status badges
    def badge(cls, icon, label):
        return f'<span class="badge badge-{cls}">{icon}&nbsp;{label}</span>'
    for pat, cls, icon, lbl in [
        (r"(?<!\w)Звезда(?!\w)",       "star", "⭐", "Звезда"),
        (r"(?<!\w)Star(?!\w)",          "star", "⭐", "Star"),
        (r"Дойная корова",              "cow",  "🐄", "Дойная корова"),
        (r"(?<!\w)Cash Cow(?!\w)",      "cow",  "🐄", "Cash Cow"),
        (r"Трудный ребёнок",            "q",    "❓", "Трудный ребёнок"),
        (r"(?<!\w)Question Mark(?!\w)", "q",    "❓", "Question Mark"),
        (r"(?<!\w)Собака(?!\w)",        "dog",  "🐕", "Собака"),
        (r"(?<!\w)Dog(?!\w)",           "dog",  "🐕", "Dog"),
    ]:
        html = re.sub(
            r'(<td[^>]*>)((?:(?!</td>).)*?)(' + pat + r')',
            lambda m, cls=cls, icon=icon, lbl=lbl: m.group(1)+m.group(2)+badge(cls,icon,lbl),
            html)

    # Replace ASCII MBB matrix
    if matrix_svg:
        def maybe_replace(m):
            c = m.group(0)
            if re.search(r'[Вв]ысок.*рост|ЗВЁЗДЫ|STARS?|High.*[Gg]rowth', c):
                return matrix_svg
            return c
        html = re.sub(r'<pre><code[^>]*>.*?</code></pre>', maybe_replace, html, flags=re.DOTALL)

    return html


# ─────────────────────────────────────────────────────────────
# SECTIONIZE: each H1/H2 → its own slide
# ─────────────────────────────────────────────────────────────

def sectionize(html):
    # Split on H1, H2, H3 — H3 creates sub-slides (segments, subsections)
    parts = re.split(r'(<h[123][^>]*>.*?</h[123]>)', html, flags=re.DOTALL)
    slides, buf_title, buf_level, buf_content = [], None, None, []

    def text_len(h):
        return len(re.sub(r'<[^>]+>|\s', '', h))

    def flush():
        if buf_title is None and not "".join(buf_content).strip():
            return
        content_html = "\n".join(buf_content).strip()
        title_text   = re.sub(r'<[^>]+>', '', buf_title or "").strip()
        lvl          = buf_level or 2

        # Skip near-empty slides: H1 metadata slide (just date + hr)
        content_text = re.sub(r'<[^>]+>', '', content_html).strip()
        if lvl == 1 and len(content_text) < 200:
            return
        # Skip H2/H3 parent slides with no meaningful body (all content is in child H3 slides)
        if lvl in (2, 3) and len(content_text) < 60:
            return

        # Pick heading tag: H1→h1, H2→h2, H3→h2 (visually same, just smaller)
        h_tag   = "h1" if lvl == 1 else "h2"
        css_sub = " slide-sub" if lvl == 3 else ""
        slides.append(
            f'<div class="slide{css_sub}">'
            f'<{h_tag} class="slide-title">{title_text}</{h_tag}>'
            f'<div class="slide-body">{content_html}</div>'
            f'</div>'
        )

    for part in parts:
        m = re.match(r'<(h[123])[^>]*>', part)
        if m:
            flush()
            buf_content = []
            buf_title   = part
            buf_level   = int(m.group(1)[1])
        else:
            if buf_title is None and part.strip():
                buf_title, buf_level = "", 2
            buf_content.append(part)

    flush()
    return "\n".join(slides)


# ─────────────────────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────────────────────

def cover_page(company, date, doc_type):
    sub = {
        "report": "Портфельный анализ и стратегические рекомендации",
        "gtm":    "GTM Playbook: от стратегии к выручке",
    }.get(doc_type, "Стратегический анализ")
    meta = f"Дата: <strong>{date}</strong> | Xata&co | Конфиденциально" if date else "Xata&co | Конфиденциально"
    return f"""<div class="slide cover-slide">
  <div class="cover-left">
    <div class="cover-label">MBB Стратегический Анализ:</div>
    <div class="cover-company">{company}</div>
    <div class="cover-sub">{sub}</div>
    <div class="cover-meta">{meta}</div>
  </div>
  <div class="cover-right">
    <div class="cover-pattern">
      <div class="cover-circle c1"></div>
      <div class="cover-circle c2"></div>
      <div class="cover-circle c3"></div>
      <div class="cover-bcg-mark">MBB</div>
    </div>
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────
# CSS — clean presentation style, 16:9
# ─────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

@page {
  size: 1280px 720px;
  margin: 0;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  font-size: 13px;
  line-height: 1.5;
  color: #1A1A1A;
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* ── SLIDE BASE ── */
.slide {
  width: 1280px;
  height: 720px;
  padding: 52px 72px 44px;
  background: #ffffff;
  break-before: page;
  page-break-before: always;
  position: relative;
  overflow: hidden;
}
.slide:first-of-type {
  break-before: auto;
  page-break-before: auto;
}
/* Fade-out gradient at bottom if content overflows */
.slide::after {
  content: '';
  position: absolute;
  bottom: 44px;
  left: 0;
  right: 0;
  height: 36px;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,1));
  pointer-events: none;
}

/* ── COVER ── */
.cover-slide {
  display: flex;
  flex-direction: row;
  padding: 0;
  gap: 0;
}
.cover-left {
  flex: 0 0 58%;
  padding: 72px 64px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;
}
.cover-label {
  font-size: 18px;
  font-weight: 600;
  color: #1C6B3A;
  margin-bottom: 12px;
  line-height: 1.3;
}
.cover-company {
  font-size: 42px;
  font-weight: 800;
  color: #1C6B3A;
  line-height: 1.15;
  margin-bottom: 16px;
}
.cover-sub {
  font-size: 22px;
  font-weight: 400;
  color: #E07B00;
  margin-bottom: 32px;
  line-height: 1.3;
}
.cover-meta {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}
.cover-right {
  flex: 0 0 42%;
  background: linear-gradient(135deg, #0A3D1F 0%, #1C6B3A 40%, #2E9B58 70%, #C8E6D0 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cover-pattern { position: relative; width: 100%; height: 100%; }
.cover-circle {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.15);
}
.c1 { width: 340px; height: 340px; top: -80px; right: -80px; }
.c2 { width: 240px; height: 240px; bottom: 40px; left: -40px; border-color: rgba(255,255,255,0.1); }
.c3 { width: 180px; height: 180px; top: 50%; left: 50%; transform: translate(-50%,-50%); background: rgba(255,255,255,0.06); border: none; }
.cover-bcg-mark {
  position: absolute;
  top: 50%; left: 50%; transform: translate(-50%,-50%);
  font-size: 80px;
  font-weight: 800;
  color: rgba(255,255,255,0.18);
  letter-spacing: -4px;
  font-family: 'Inter', sans-serif;
}

/* ── SLIDE TITLES ── */
.slide-title {
  margin-bottom: 6px;
  line-height: 1.2;
  font-weight: 700;
}
h1.slide-title {
  font-size: 28px;
  color: #1C6B3A;
  margin-bottom: 4px;
}
h2.slide-title {
  font-size: 24px;
  color: #1C6B3A;
  margin-bottom: 4px;
}
/* H3-level sub-slides (segment analyses) */
.slide-sub h2.slide-title {
  font-size: 20px;
}

/* ── SLIDE BODY ── */
.slide-body { margin-top: 6px; }

/* Sub-headings inside slides */
.slide-body h2 {
  font-size: 14px;
  font-weight: 700;
  color: #E07B00;
  margin: 18px 0 8px;
}
.slide-body h3 {
  font-size: 14px;
  font-weight: 600;
  color: #E07B00;
  margin: 14px 0 7px;
}
.slide-body h4 {
  font-size: 13px;
  font-weight: 600;
  color: #334;
  margin: 10px 0 5px;
}

.slide-body p { margin: 0 0 8px; line-height: 1.55; font-size: 13px; }
.slide-body ul, .slide-body ol { margin: 4px 0 8px 22px; }
.slide-body li { margin-bottom: 4px; font-size: 13px; line-height: 1.5; }
.slide-body strong { font-weight: 700; color: #1A1A1A; }
.slide-body em { color: #555; }

/* Cards (blockquote) — orange left border */
.bcg-card {
  border-left: 4px solid #E07B00;
  background: #FFF8F0;
  padding: 12px 18px;
  margin: 10px 0;
  border-radius: 0 6px 6px 0;
}
.bcg-card p { margin: 0 0 4px; font-size: 13px; }
.bcg-card p:last-child { margin: 0; }
.bcg-card strong { color: #C05A00; }

.bcg-hr { border: none; border-top: 1px solid #E8E8E8; margin: 14px 0; }

pre {
  background: #F6F8FA;
  border: 1px solid #E0E4EA;
  border-radius: 5px;
  padding: 10px 14px;
  font-size: 11px;
  font-family: 'SFMono-Regular', Consolas, monospace;
  margin: 8px 0;
  overflow: auto;
}
code {
  font-family: 'SFMono-Regular', Consolas, monospace;
  font-size: 11px;
  background: #F0F4F8;
  padding: 1px 4px;
  border-radius: 3px;
}
pre code { background: none; padding: 0; }

/* ── TABLES ── */
.bcg-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 14px;
  font-size: 12px;
  page-break-inside: avoid;
}
.bcg-thead th {
  background: #F0F0F0;
  color: #1A1A1A;
  font-weight: 600;
  font-size: 12px;
  padding: 9px 12px;
  text-align: left;
  border-bottom: 2px solid #D0D0D0;
}
.bcg-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #EBEBEB;
  vertical-align: top;
  line-height: 1.45;
  font-size: 12px;
}
.bcg-tbody tr:first-child td { border-top: none; }
.bcg-table td:first-child { font-weight: 600; }

/* ── BADGES ── */
.badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  border: 1.5px solid currentColor;
}
.badge-star { color: #1C6B3A; background: #EAF5EE; }
.badge-cow  { color: #1355A0; background: #E8EFF9; }
.badge-q    { color: #C05A00; background: #FEF3E7; }
.badge-dog  { color: #980000; background: #FDEAEA; }

/* ── MBB MATRIX ── */
.bcg-matrix-wrap { margin: 14px auto 16px; text-align: center; page-break-inside: avoid; }
.bcg-matrix-title { font-size: 14px; font-weight: 700; color: #1C6B3A; margin-bottom: 8px; }
"""


# ─────────────────────────────────────────────────────────────
# BUILD & WRITE
# ─────────────────────────────────────────────────────────────

def process_file(md_path, output_html, doc_type="report"):
    text = md_path.read_text(encoding="utf-8")

    name_m  = re.search(r"^#[^#].*?:\s*(.+?)$",      text, re.M)
    date_m  = re.search(r"\*([^\|*\n]+?)\s*\|\s*MBB", text)
    company = name_m.group(1).strip() if name_m else COMPANY
    date    = date_m.group(1).strip() if date_m else ""

    segs       = parse_segments(text)
    matrix_svg = generate_bcg_matrix_svg(segs)

    body = md_to_html(text)
    body = post_process(body, matrix_svg)
    body = sectionize(body)
    cover = cover_page(company, date, doc_type)

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>MBB — {company}</title>
<style>{CSS}</style>
</head>
<body>
{cover}
{body}
</body>
</html>"""

    Path(output_html).write_text(html, encoding="utf-8")
    print(f"✅ HTML: {output_html}")


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

report = OUTPUT_DIR / "final-report.md"
gtm    = OUTPUT_DIR / "gtm-playbook.md"

if report.exists():
    process_file(report, OUTPUT_DIR / "final-report.html", "report")
else:
    print(f"⚠️  Not found: {report}")

if gtm.exists():
    process_file(gtm, OUTPUT_DIR / "gtm-playbook.html", "gtm")
else:
    print("ℹ️  No gtm-playbook.md — skipping.")

print("Done.")
