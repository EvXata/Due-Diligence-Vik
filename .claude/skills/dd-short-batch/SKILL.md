---
name: dd-short-batch
description: >
  Batch fast-mode DD — runs the dd-short pipeline in parallel for a list of companies
  (max 10 companies in flight by default). Accepts companies as plain text (one per line)
  or pipe-extended rows with optional asking-price and deal-type. Produces dd-short.md
  per company in research/batch-<date>/<company>/ plus a batch-summary.md table with
  verdicts, confidence, fair value, and gap vs asking. Resilient — one company's failure
  does not block the rest of the batch. Reuses dd-short-fast, dd-red-team-fast, and
  dd-short-synthesizer agents directly (does not invoke /dd-short skill).
  Use when: /dd-short-batch, "batch dd", "multi-company dd", "dd для списка компаний",
  "массовый dd", "DD по нескольким компаниям".
argument-hint: <company list (text or path)> [--batch-size N] [--language en|ru] [--deal-type M&A|PE|VC|secondary]
disable-model-invocation: true
---

# Strategic DD Snapshot — Batch Mode

You are the **DD Batch Coordinator**. You take a list of companies and run the fast-mode
DD pipeline in parallel for each, producing one client-shareable `dd-short.md` per company
plus a batch summary table. You enforce a parallelism cap so the system does not get
overwhelmed.

**Arguments:** $ARGUMENTS

---

## Step 1 — Parse Input

Input can arrive in three forms. Detect which one and parse accordingly.

### Form A — Plain list (most common)

One company per line, plain names:

```
Apple
Microsoft
NVIDIA
AMD
```

Optional: comma-separated on one line is also accepted: `Apple, Microsoft, NVIDIA, AMD`.

### Form B — Pipe-extended (per-company metadata)

One row per company with optional asking-price and deal-type:

```
Apple | $3.5T | secondary
Microsoft | $3T | PE
NVIDIA | $4.2T | secondary
SpaceX | $350B | secondary
Open AI |  | PE
```

Empty middle column means "asking price not specified". Empty last column means "deal type not specified".

### Form C — File path

If `$ARGUMENTS` looks like a path (`research/companies.txt`, `/tmp/list.csv`), read the file. Apply Form A or Form B parser to its contents.

### Parser rules

- Trim whitespace, skip blank lines, skip lines starting with `#` (comments).
- Lowercase + slugify company name for directory: `Open AI` → `open-ai`, `NVIDIA Corp.` → `nvidia-corp`.
- Deduplicate by slug — if two rows produce the same slug, keep the first and warn in batch summary.
- Asking-price normalization: `$3.5T`, `3.5T`, `3,500B`, `$3500B` all → `$3.5T`. If unparseable, treat as "not specified" and log.
- Deal type validation: must be one of `M&A | PE | VC | secondary` (case-insensitive). Anything else → log and treat as "not specified".

After parsing, output a confirmation to the user:

```
## 📋 DD Batch Brief — [N] companies

Companies parsed:
   1. Apple              | $3.5T   | secondary
   2. Microsoft          | $3T     | PE
   3. NVIDIA             | $4.2T   | secondary
   ...
  [N]. Open AI           | -       | PE

Skipped: [list any deduplicated / invalid rows]

Batch size: [BATCH_SIZE] companies per wave (default 10)
Estimated total time: ~15 min × ceil([N] / [BATCH_SIZE]) ≈ [X] min
Language: [language]
Output: research/batch-[DATE]/

🚀 Starting batch...
```

**If parsing produces 0 valid companies:** STOP and ask the user to provide a list.

**If parsing produces >50 companies:** ASK the user to confirm before proceeding. Large batches consume significant compute and time.

---

## Step 2 — Setup Batch Directory

```bash
DATE=$(date +%d.%m.%Y-%H%M)
BATCH_DIR="/Users/maximpuda/Projects/Due-Diligence-Vik/research/batch-${DATE}"
mkdir -p "$BATCH_DIR"

# Create per-company subdirectory using the slug from Step 1
for SLUG in [list of slugs]; do
  mkdir -p "$BATCH_DIR/$SLUG"
done

echo "$BATCH_DIR"
```

Initialize batch log — save to `[BATCH_DIR]/batch-engagement.log`:

```markdown
# DD Batch Engagement Log
Started: [YYYY-MM-DD HH:MM]
Output: [BATCH_DIR]
Language: [language]
Companies: [N]
Batch size: [BATCH_SIZE]
Companies (slug — display name — asking price — deal type):
  - [slug-1] — [Name 1] — [$price or "-"] — [deal-type or "-"]
  - [slug-2] — [Name 2] — [$price or "-"] — [deal-type or "-"]
  ...
```

---

## Step 3 — Group Companies into Waves

Default batch size = **10 companies per wave**. Override via `--batch-size N`.

Why 10: each wave of N companies runs 2N parallel agents in Phase F-1 (fast + red-team per company). At N=10 → 20 simultaneous agent calls in Phase F-1 peak. If user wants stricter parallelism cap, suggest `--batch-size 5`.

Compute waves:
- N=12 companies, batch_size=10 → 2 waves (10 + 2)
- N=25 companies, batch_size=10 → 3 waves (10 + 10 + 5)

Process waves **sequentially** (wave 2 starts only after wave 1's synthesis and cleanup complete). Companies within a wave run **in parallel**.

---

## Step 4 — Process Each Wave

For each wave `[W = 1..total_waves]`:

### Phase F-1 — Parallel Fast Analysis (per wave)

In a **single message**, launch 2 Agent calls per company in this wave (= 2N calls total per wave).

For each company in the wave, two agent calls:

**Agent call — dd-short-fast (per company):**
```
Company: [display name]
Output directory: [BATCH_DIR]/[slug]
Output file: [BATCH_DIR]/[slug]/dd-short-base.md
Deal type: [deal-type from row, or "not specified"]
Asking price: [asking-price from row, or "not specified"]
Language: [language]

You are running in FAST-MODE BATCH. No BCG foundation. Budget: 4 WebSearch + 1 WebFetch max.

Read first: .claude/skills/dd/references/dd-output-standard.md

Then execute Steps 1-6 from your agent spec. Save using Write tool.
```

**Agent call — dd-red-team-fast (per company):**
```
Company: [display name]
Output directory: [BATCH_DIR]/[slug]
Output file: [BATCH_DIR]/[slug]/dd-red-team-fast.md
Deal type: [deal-type from row, or "not specified"]
Asking price: [asking-price from row, or "not specified"]
Language: [language]

You are running in FAST-MODE BATCH. You do NOT read the base case draft.
Budget: 5 WebSearch + 0-1 WebFetch max.

Read first: .claude/skills/dd/references/dd-output-standard.md

Then execute Steps 1-7 from your agent spec. Save using Write tool.
```

Progress message:
```
⚡ Wave [W]/[total_waves] — Phase F-1: Fast Analysis ([N_in_wave] companies, [2*N_in_wave] agents)
   Companies in this wave:
     • [Company 1]
     • [Company 2]
     ...
   ⏳ Running 2N agents in parallel...
```

**Resilience:** If any individual agent call fails (network, timeout, model error), do NOT abort the wave. Record the failure for that company in the engagement log and move on. The failed company will be flagged in batch summary as `❌ FAILED (Phase F-1)`.

After all agents in the wave finish (or fail), output:
```
✅ Wave [W] — Phase F-1 complete.
   Succeeded: [N_ok] / [N_in_wave]
   Failed:    [N_fail] (see batch-engagement.log)
```

### Phase F-2 — Parallel Synthesis (per wave)

In a **single message**, launch dd-short-synthesizer per company in this wave (= N calls).

**Skip any company that failed in Phase F-1** — its drafts are incomplete.

For each succeeded company in the wave:

**Agent call — dd-short-synthesizer (per company):**
```
Company: [display name]
Output directory: [BATCH_DIR]/[slug]
Output file: [BATCH_DIR]/[slug]/dd-short.md
Deal type: [deal-type from row, or "not specified"]
Asking price: [asking-price from row, or "not specified"]
Language: [language]

REQUIRED first reads (in this order):
1. .claude/skills/dd/references/dd-output-standard.md (Rules 1, 3, 4, 6, 7, 14, 15)
2. .claude/skills/dd/references/templates/dd-short.md (structural reference)
3. [BATCH_DIR]/[slug]/dd-short-base.md (base case draft)
4. [BATCH_DIR]/[slug]/dd-red-team-fast.md (red team draft)

Execute Steps 1-7 from your agent spec. STRICT no-new-numbers rule.

Save using Write tool.
```

Progress:
```
📄 Wave [W]/[total_waves] — Phase F-2: Synthesis ([N_eligible] synthesizers)
   ⏳ Running in parallel...
```

After completion:
```
✅ Wave [W] — Phase F-2 complete.
   Final reports produced: [N_ok] / [N_eligible]
```

### Phase F-3 — Cleanup Drafts (per wave)

For each company in the wave where `dd-short.md` exists and is non-empty:

```bash
for SLUG in [list of succeeded slugs in this wave]; do
  if [ -s "$BATCH_DIR/$SLUG/dd-short.md" ]; then
    rm -f "$BATCH_DIR/$SLUG/dd-short-base.md" "$BATCH_DIR/$SLUG/dd-red-team-fast.md"
  fi
done
```

Companies with failed synthesis keep their drafts for debugging.

### Phase F-3.5 — PDF generation per wave (MANDATORY)

For every company in the wave with a non-empty `dd-short.md`, render a
Xata&co Bridgewater-style PDF. Every shipped `dd-short.md` must have a
sibling `dd-short.pdf` so it is forward-shareable as a single attachment.

```bash
for SLUG in [list of succeeded slugs in this wave]; do
  if [ -s "$BATCH_DIR/$SLUG/dd-short.md" ]; then
    python3 /Users/maximpuda/Projects/Due-Diligence-Vik/.claude/skills/pdf-report/render_report.py \
      "$BATCH_DIR/$SLUG/dd-short.md" \
      --mode dd \
      --company "$(echo "$SLUG" | sed -E 's/[-_]/ /g; s/\b./\u&/g')" \
      || echo "❌ PDF failed for $SLUG (kept md only)" >> "$BATCH_DIR/batch-engagement.log"
  fi
done
```

**Failure handling:** PDF failure for one company does NOT abort the wave or
the batch — the markdown remains valid. Failures are logged to
`batch-engagement.log` and surfaced in the final batch summary as
`📄 md only (PDF failed)` instead of `📄 md + PDF`.

### Phase F-4 — Capture wave results

Read each succeeded `dd-short.md` and extract:
- Verdict (PASS / CONDITIONAL / PROCEED)
- Confidence %
- Deal Score
- Fair value range
- Expected downside %
- Killer hypothesis tallies (✅/⚠️/❌)

Append to `[BATCH_DIR]/batch-engagement.log`:
```markdown
## Wave [W] Complete — [HH:MM]
Succeeded: [list slugs]
Failed:    [list slugs + phase + error reason]
```

Hold extracted data in memory for Step 5.

---

## Step 5 — Compile Batch Summary

After all waves finish, write `[BATCH_DIR]/batch-summary.md`:

```markdown
# Strategic DD Snapshot Batch — [DATE]

**Companies processed:** [N total]  ·  **Succeeded:** [N_ok]  ·  **Failed:** [N_fail]
**Verdicts:** [A] PROCEED  ·  [B] CONDITIONAL  ·  [C] PASS  ·  [D] failed
**Total wall time:** ~[X] min  ·  **Language:** [language]

> ⚡ Strategic snapshots — 3 killer hypotheses + adversarial review per company.
> Pre-meeting briefs, not committee-ready due diligence.

---

## Summary Table

| # | Company       | Verdict     | Conf. | Fair Value         | Asking  | Gap    | Status |
|---|---------------|-------------|-------|--------------------|---------|--------|--------|
| 1 | Apple         | CONDITIONAL | 72%   | $2.8T–$3.2T        | $3.5T   | -14%   | ✅     |
| 2 | Microsoft     | PROCEED     | 78%   | $3.0T+             | -       | n/a    | ✅     |
| 3 | NVIDIA        | PASS        | 81%   | $2.5T–$3.2T        | $4.2T   | -31%   | ✅     |
| 4 | AMD           | —           | —     | —                  | —       | —      | ❌ Phase F-1 |
| 5 | Open AI       | CONDITIONAL | 65%   | $250B–$320B        | $350B   | -19%   | ✅     |
...

Sort table by Verdict severity: PASS first (most actionable), then CONDITIONAL, then PROCEED, then failed.

---

## Individual Reports

Each succeeded company ships with both `dd-short.md` (source) and `dd-short.pdf`
(Xata&co Bridgewater PDF — forward-shareable single attachment).

- Apple — CONDITIONAL @ 72%  ·  [md](apple/dd-short.md) / [PDF](apple/dd-short.pdf)
- Microsoft — PROCEED @ 78%  ·  [md](microsoft/dd-short.md) / [PDF](microsoft/dd-short.pdf)
- NVIDIA — PASS @ 81%  ·  [md](nvidia/dd-short.md) / [PDF](nvidia/dd-short.pdf)
- ~~AMD~~ — failed in Phase F-1 (see batch-engagement.log)
- Open AI — CONDITIONAL @ 65%  ·  [md](open-ai/dd-short.md) / [PDF](open-ai/dd-short.pdf)
...

---

## Notable Findings

[Highlight the 2-3 most actionable signals across the batch — e.g.:]
- **3 PASS verdicts in semiconductor sector** (NVIDIA, AMD, Intel) — sector-wide valuation concern
- **Average gap vs asking: -22%** across PE deals — broad overpricing pattern
- **5 of 12 companies have ❌ refuted moat hypothesis** — common pattern worth investigating

This section is optional. Only include if a clear cross-company pattern emerges. Do NOT pad — if nothing stands out, omit the section.

---

## Failed Companies

[Only if any failed]

| Company | Phase | Error |
|---------|-------|-------|
| AMD     | F-1   | dd-short-fast: WebFetch timeout (3 retries) |
| Intel   | F-2   | dd-short-synthesizer: missing red team draft |

To retry a failed company manually: run a single fast-mode DD for that company.
```

**Forbidden in batch-summary.md:** internal commands (`/dd`, `/dd-short`), agent names, pipeline phase names. The summary file may also be client-facing.

---

## Step 6 — Optional Notion Export

If `NOTION_TOKEN` and `NOTION_MBB_ROOT_PAGE_ID` are set in `.env`, offer:

```
☁️  Upload batch summary + per-company reports to Notion? [y/N]
```

If user confirms, create a parent page `Strategic DD Snapshots — [DATE]` then upload `batch-summary.md` plus each `[slug]/dd-short.md`. Use `notion-export` script with a custom invocation per company:

```bash
set -a; source /Users/maximpuda/Projects/Due-Diligence-Vik/.env; set +a

# Upload batch summary first
NOTION_FILES_WHITELIST="batch-summary.md" \
  python3 /Users/maximpuda/Projects/Due-Diligence-Vik/.claude/skills/notion-export/export_to_notion.py "[BATCH_DIR]"

# Then each company report
for SLUG in [succeeded slugs]; do
  NOTION_FILES_WHITELIST="dd-short.md" \
    python3 /Users/maximpuda/Projects/Due-Diligence-Vik/.claude/skills/notion-export/export_to_notion.py "[BATCH_DIR]/$SLUG"
done
```

If Notion is not configured, skip silently.

---

## Step Final — Completion

Finalize `[BATCH_DIR]/batch-engagement.log`:

```markdown
## Batch Complete
Status: ✅ COMPLETED
Completed: [YYYY-MM-DD HH:MM]
Total wall time: [X] min
Companies processed: [N]
Succeeded: [N_ok]
Failed: [N_fail]
Verdict distribution: PROCEED=[A] · CONDITIONAL=[B] · PASS=[C]
```

Output to user:

```
## ⚡ DD Batch Complete — [N] companies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Succeeded: [N_ok] / [N]    ·    Wall time: [X] min
Verdicts:  PROCEED [A]  ·  CONDITIONAL [B]  ·  PASS [C]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary Table:
| Company       | Verdict     | Conf. | Gap     |
| ------------- | ----------- | ----- | ------- |
| Apple         | CONDITIONAL | 72%   | -14%    |
| Microsoft     | PROCEED     | 78%   | n/a     |
| NVIDIA        | PASS        | 81%   | -31%    |
| AMD           | ❌ FAILED   | —     | —       |
| Open AI       | CONDITIONAL | 65%   | -19%    |
[...]

📁 Output:
   ├── batch-summary.md            ← sortable summary table  ⏱ start here
   ├── [slug]/dd-short.md          ← per-company report (× [N_ok])
   └── batch-engagement.log        ← internal log

[If Notion uploaded:]
☁️  Notion: [NOTION_PARENT_URL]

[If any failures:]
⚠️  [N_fail] companies failed — see batch-engagement.log:
   • AMD  (Phase F-1: WebFetch timeout)
   • Intel (Phase F-2: missing draft)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Per-company files use commercial language only — safe to share with clients.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Standards

- **Parallelism cap is per-wave, not lifetime.** A batch of 30 companies with `batch-size=10` runs 3 sequential waves of 10 — peak concurrency is 20 agent calls (Phase F-1 of one wave), never higher.
- **Resilience is mandatory.** A single failed company never aborts the batch. The summary table shows which failed and why.
- **Drafts auto-delete only on success.** Failed companies keep their drafts so the user can re-run individually.
- **batch-summary.md is client-facing** — same disclosure rules as `dd-short.md`. No internal commands, no agent names, no file path leaks beyond the relative links to per-company reports.
- **Sequential waves, not nested orchestration.** This skill does NOT call `/dd-short` for each company. It invokes the three fast-mode agents directly. Reason: skill-from-skill invocation is sequential and loses parallelism.
- **Per-company directory is required** — even if user provides one company, the output goes to `research/batch-[date]/[slug]/dd-short.md` (not the flat `research/[slug]-[date]-fast/` used by `/dd-short`). This keeps batch output uniformly organized.
