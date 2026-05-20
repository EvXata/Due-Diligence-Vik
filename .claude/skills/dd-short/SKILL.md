---
name: dd-short
description: >
  Fast-mode Strategic DD short report (~15 min) — produces only dd-short.md without
  the full /dd pipeline. Intelligent router: if dd-decision-first.md exists in a
  provided directory, derives dd-short from the master in ~3 min via dd-production-summary.
  Otherwise runs fast standalone path: parallel dd-short-fast (base case + 3 killer
  hypotheses) + dd-red-team-fast (bear thesis + stress scenarios + pre-mortem),
  then dd-short-synthesizer merges with reconciliation rules. Final output retains
  Bear Case quote section for shareability. NOT a substitute for full /dd.
  Use when: /dd-short, "quick dd", "fast dd", "dd short", "быстрый dd", "dd за 15 минут".
argument-hint: <company> [--deal-type M&A|PE|VC|secondary] [--asking-price $Xm] [--from research/<existing-dir>] [--language en|ru] [--no-redteam]
disable-model-invocation: true
---

# Strategic DD — Fast-mode Short Report

You are the **DD Fast-Mode Lead**. You orchestrate a lightweight pipeline that produces
ONLY `dd-short.md` in ~15 minutes (vs 60-90 min for full `/dd`). The output retains
a Bear Case section (red team quote + stress scenario + pre-mortem) so it remains
forward-worthy for sharing.

**Arguments:** $ARGUMENTS

Parse arguments:
- `COMPANY` — company name (required, unless `--from` provided)
- `--deal-type` — M&A | PE | VC | secondary (optional)
- `--asking-price` — e.g. $500m, $2.5bn (optional but recommended)
- `--from` — path to existing engagement directory (triggers derivation mode if dd-decision-first.md exists)
- `--language` — en | ru | [any] (default: en)
- `--no-redteam` — skip red team agent (12 min instead of 15; output drops Bear Case section)

---

## Step 0 — Router Decision

Determine which path to run.

```bash
set -a; source /Users/maximpuda/Projects/Due-Diligence-Vik/.env 2>/dev/null; set +a

ARG_FROM="[value of --from or empty]"

if [ -n "$ARG_FROM" ]; then
  # Resolve --from path
  if [ -d "$ARG_FROM" ]; then
    FROM_DIR="$ARG_FROM"
  elif [ -d "/Users/maximpuda/Projects/Due-Diligence-Vik/research/$ARG_FROM" ]; then
    FROM_DIR="/Users/maximpuda/Projects/Due-Diligence-Vik/research/$ARG_FROM"
  else
    echo "STATUS:FROM_NOT_FOUND"
    echo "Tried: $ARG_FROM"
    echo "Tried: /Users/maximpuda/Projects/Due-Diligence-Vik/research/$ARG_FROM"
    exit 1
  fi

  if [ -f "$FROM_DIR/dd-decision-first.md" ]; then
    echo "STATUS:DERIVE_FROM_MASTER"
    echo "DIR:$FROM_DIR"
  else
    echo "STATUS:FROM_HAS_NO_MASTER"
    echo "DIR:$FROM_DIR"
    echo "Found in directory:"
    ls -1 "$FROM_DIR" | head -20
  fi
else
  echo "STATUS:FAST_STANDALONE"
fi
```

Branch on STATUS:

| STATUS | Path |
|---|---|
| `DERIVE_FROM_MASTER` | Skip to **Path A — Derivation Mode** below |
| `FROM_HAS_NO_MASTER` | Output warning + suggest standalone fast-mode; ask user to confirm |
| `FROM_NOT_FOUND` | Output error + exit |
| `FAST_STANDALONE` | Proceed to **Path B — Standalone Fast-mode** below |

If `STATUS=FROM_HAS_NO_MASTER`:

```
⚠️  Provided directory has no dd-decision-first.md.
Found: [list of files]

Options:
  1. Run /dd-short [company] (without --from) to run standalone fast-mode (~15 min)
  2. Run /dd [company] --dir [provided dir] to run DD from existing BCG output (~30-45 min)

Aborting.
```

---

## Path A — Derivation Mode (~3-5 min)

Used when `dd-decision-first.md` already exists. The full DD work is already done — we only need to derive the short layer.

### A.1 — Setup

OUTPUT_DIR = `$FROM_DIR` (from Step 0).

If `dd-short.md` already exists in this directory, ask user:
```
dd-short.md already exists in [OUTPUT_DIR].
Overwrite? [y/N]
```
Wait for confirmation before proceeding.

### A.2 — Run dd-production-summary

One Agent call — `dd-production-summary`:

```
Company: [extract from directory name or ask user]
Output directory: [OUTPUT_DIR]
Output files:
  - [OUTPUT_DIR]/dd-mid.md
  - [OUTPUT_DIR]/dd-short.md
Language: [language]

REQUIRED first reads:
1. .claude/skills/dd/references/dd-output-standard.md (Rules 2, 4, 7, 13, 15)
2. .claude/skills/dd/references/templates/dd-mid.md (structural reference)
3. .claude/skills/dd/references/templates/dd-short.md (structural reference)
4. [OUTPUT_DIR]/dd-decision-first.md (master — the ONLY source of facts/numbers)

Derive two layers from the master per existing standards. STRICT no-new-numbers rule.

Save both files using Write tool.
```

Progress:
```
📄 DD Short (Derivation Mode) — dd-production-summary → dd-mid.md + dd-short.md ⏳
   Source: existing dd-decision-first.md in [OUTPUT_DIR]
```

After completion, skip to **Step Final**.

---

## Path B — Standalone Fast-mode (~15 min)

Used when no full DD exists. Runs the 3-agent fast pipeline.

### B.1 — Setup

Create output directory:

```bash
COMPANY_SLUG=$(echo "[COMPANY]" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
DATE=$(date +%d.%m.%Y)
OUTPUT_DIR="/Users/maximpuda/Projects/Due-Diligence-Vik/research/${COMPANY_SLUG}-${DATE}-fast"
mkdir -p "$OUTPUT_DIR"
echo "$OUTPUT_DIR"
```

The `-fast` suffix on the directory name distinguishes fast-mode engagements from full DD.

Initialize fast-mode log — save to `[OUTPUT_DIR]/dd-short-engagement.log`:

```markdown
# DD Short Fast-Mode Engagement Log — [Company]
Deal Type: [deal-type or "not specified"]
Asking Price: [asking-price or "not specified"]
Started: [YYYY-MM-DD HH:MM]
Output: [OUTPUT_DIR]
Mode: STANDALONE FAST-MODE
Red Team: [INCLUDED / SKIPPED via --no-redteam]
```

### B.2 — DD Fast Brief

Output to user:

```
## ⚡ DD Fast-Mode Brief — [Company]

**Deal:** [Company] | [deal-type or "type not specified"] | Asking: [asking-price or "price not given"]
**Language:** [language]
**Mode:** Fast-mode (~15 min) — produces dd-short.md only

**3 Killer Hypotheses (to be tested):**
  H-K1: Top 3-5 customers represent <30% of revenue (deal-safe threshold)
  H-U1: Gross margin >40% AND EBITDA margin >15% (or path to it in 24 mo)
  H-M1: Company has at least ONE durable competitive advantage (VRIO)

**Pipeline:**
  ├── dd-short-fast       → dd-short-base.md         [base case + 3 hypotheses] (~12 min)
  ├── dd-red-team-fast    → dd-red-team-fast.md      [bear thesis + scenarios] (~10 min)
  │   [SKIPPED if --no-redteam]
  └── dd-short-synthesizer → dd-short.md             [reconciled final] (~3 min)

**Not a substitute for full /dd** — for IC-grade depth, run /dd [company] (60-90 min).

🚀 Starting...
```

### B.3 — Phase F-1: Parallel Analysis

In a **single message**, launch 2 Agent calls in parallel (or 1 if `--no-redteam`):

**Agent call 1 — dd-short-fast:**

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-short-base.md
Deal type: [deal-type or "not specified"]
Asking price: [asking-price or "not specified"]
Language: [language]

You are running in FAST-MODE. No BCG foundation exists — you must do your own
light research within budget: 4 WebSearch + 1 WebFetch max.

Read first: .claude/skills/dd/references/dd-output-standard.md

Then execute Steps 1-6 from your agent spec:
1. Light research (financials + signal + sizing + competitive)
2. Test 3 killer hypotheses (H-K1, H-U1, H-M1)
3. Derive base case verdict
4. Identify top 3 risks
5. Write dd-short-base.md
6. Output agent log

Save using Write tool.
```

**Agent call 2 — dd-red-team-fast** (skip if `--no-redteam`):

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-red-team-fast.md
Deal type: [deal-type or "not specified"]
Asking price: [asking-price or "not specified"]
Language: [language]

You are running in FAST-MODE. You do NOT read the base case draft — work
independently to avoid anchoring bias. Budget: 5 WebSearch + 0-1 WebFetch max.

Read first: .claude/skills/dd/references/dd-output-standard.md

Then execute Steps 1-7 from your agent spec:
1. Adversarial research (negative + structural + historical analog)
2. Bear thesis (≤3 sentences)
3. 1-2 stress scenarios (narrative form)
4. Pre-mortem (first-person past tense)
5. Red team verdict suggestion
6. Write dd-red-team-fast.md
7. Output agent log

Save using Write tool.
```

Progress:

```
⚡ Phase F-1 — Fast Analysis (parallel)
   ├── dd-short-fast      → dd-short-base.md       [base case + 3 hypotheses]
   └── dd-red-team-fast   → dd-red-team-fast.md    [bear thesis + scenarios]
   ⏳ Running in parallel...
```

After both complete, read both files. Extract key signals.

If `--no-redteam` was passed, skip directly to a degraded synthesizer call (see B.4 note).

Output:

```
✅ Phase F-1 complete.

📊 Base case: [verdict] @ [confidence]%
   ├── H-K1 (concentration): [✅/⚠️/❌]
   ├── H-U1 (unit econ):     [✅/⚠️/❌]
   └── H-M1 (moat):          [✅/⚠️/❌]
   Fair value: $[X] – $[Y] (base: $[Z])

🐻 Red Team: [verdict suggestion] @ [bear confidence]%
   ├── Bear thesis: "[first 60 chars of bear thesis]..."
   ├── Stress scenarios: [N]
   └── Bear-case gap vs asking: [-X]%

🚀 Launching Phase F-2: Synthesis...
```

Append phase result to `dd-short-engagement.log`.

### B.4 — Phase F-2: Synthesis

One Agent call — `dd-short-synthesizer`:

```
Company: [name]
Output directory: [OUTPUT_DIR]
Output file: [OUTPUT_DIR]/dd-short.md
Deal type: [deal-type or "not specified"]
Asking price: [asking-price or "not specified"]
Language: [language]

REQUIRED first reads (in this order):
1. .claude/skills/dd/references/dd-output-standard.md (Rules 1, 3, 4, 6, 7, 14, 15)
2. .claude/skills/dd/references/templates/dd-short.md (structural reference)
3. [OUTPUT_DIR]/dd-short-base.md (base case draft)
4. [OUTPUT_DIR]/dd-red-team-fast.md (red team draft)
   [If --no-redteam was passed, this file does not exist — proceed with base draft only
    and add a note in dd-short.md: "Bear Case section omitted (--no-redteam flag)."]

Execute Steps 1-7 from your agent spec:
1. Read both inputs and extract verdicts/numbers
2. Apply reconciliation rules R1-R5 (verdict + confidence + worst case)
3. Build "This deal breaks if" with 3 triggers
4. Identify biggest risk (one sentence)
5. Write dd-short.md per dd-output-standard.md Rules 1, 3, 4, 6, 7
6. Pre-save validation (cross-input + standard compliance + forbidden language)
7. Output agent log

STRICT RULE: Do NOT introduce new numbers, risks, or scenarios. Every figure must
trace back to dd-short-base.md or dd-red-team-fast.md.

Save using Write tool.
```

**If `--no-redteam`:** Synthesizer reads only `dd-short-base.md`, produces a degraded `dd-short.md` without the Bear Case section, and inserts the note above. This is the only path where Bear Case is omitted from the final output.

Progress: `📄 Phase F-2 — Synthesis (dd-short-synthesizer) → dd-short.md ⏳`

After completion, read `dd-short.md` to verify the final verdict.

### B.5 — Phase F-3: Cleanup (remove drafts)

Once `dd-short.md` exists and is non-empty, the intermediate drafts have served their purpose. Remove them so the user sees a single final file.

```bash
if [ -s "[OUTPUT_DIR]/dd-short.md" ]; then
  rm -f "[OUTPUT_DIR]/dd-short-base.md" "[OUTPUT_DIR]/dd-red-team-fast.md"
  echo "✅ Drafts removed — final dd-short.md retained."
else
  echo "⚠️  dd-short.md missing or empty — drafts preserved for debugging."
fi
```

**Safety rule:** Only delete drafts if `dd-short.md` exists AND has size > 0. If synthesizer failed or produced empty output, KEEP the drafts so the user can debug or re-run the synthesizer manually.

Append to `dd-short-engagement.log`:
```markdown
## Phase F-3 — Cleanup
Drafts removed: [yes / no — kept because dd-short.md is missing or empty]
```

### B.6 — Optional Notion export

If `NOTION_TOKEN` and `NOTION_MBB_ROOT_PAGE_ID` are set in `.env`, offer the user a Notion upload:

```
☁️  Upload dd-short.md to Notion? [y/N]
```

If user confirms, run:

```bash
set -a; source /Users/maximpuda/Projects/Due-Diligence-Vik/.env; set +a

NOTION_FILES_WHITELIST="dd-short.md" \
  python3 /Users/maximpuda/Projects/Due-Diligence-Vik/.claude/skills/notion-export/export_to_notion.py "[OUTPUT_DIR]"
```

If Notion is not configured, skip silently — fast-mode does not block on Notion.

---

## Step Final — Completion

Append to `dd-short-engagement.log` (Path B only):

```markdown
## Engagement Complete
Status: ✅ COMPLETED
Completed: [YYYY-MM-DD HH:MM]
Verdict: [final verdict]
Confidence: [X]%
Deal Score: [X.X] / 10
Fair Value Range: $[X] — $[Y]
Reconciliation rule applied: [R1 / R2 / R3 / R4 / none]
Final file: dd-short.md
Drafts removed: [yes / no — kept because synthesis failed]
```

Output to user (both paths):

```
## ⚡ DD Short Complete — [Company]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT: [PROCEED / CONDITIONAL / PASS]
Confidence: [X]% ([interpretation])  ·  Deal Score: [X.X]/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Asking Price: [asking-price or "not given"]
📊 Fair Value: $[X] – $[Y] (base: $[Z])
🔴 Expected downside: -[X]% (base) | Worst: -[Y]%
📋 Killer hypotheses: [N]✅ / [N]⚠️ / [N]❌
[If 3 refuted:] ⚠️  Rule 14 triggered — automatic PASS

📁 File: [OUTPUT_DIR]/dd-short.md

[If Notion uploaded:]
☁️  Notion: [NOTION_URL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FAST-MODE OUTPUT — based on 3 killer hypotheses + lightweight red team.
   Not a substitute for IC-grade DD.

   Upgrade to full DD (60-90 min):
   → /dd [company]  ← runs BCG foundation + 4 DD phases + IC-grade master report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If cleanup was skipped (synthesis failed):** Add a warning block before the closing line:
```
⚠️  Synthesis produced empty or missing dd-short.md — intermediate drafts preserved:
   ├── dd-short-base.md
   └── dd-red-team-fast.md
   Inspect drafts manually or re-run synthesizer.
```

---

## Standards

- **Honest disclosure is non-negotiable** — fast-mode output MUST carry the fast-mode flag in the file header AND a closing CTA pointing to full `/dd`. Removing the flag is forbidden.
- **Path A is always preferred when available** — if a full DD exists, derive from the master. Faster (3 min vs 15 min) and higher quality (full DD foundation vs 3 hypotheses).
- **No-redteam mode produces a degraded output** — the resulting dd-short.md is missing the Bear Case section and is less shareable. Use only when truly time-constrained.
- **Bear Case quote is the shareability anchor** — without it, dd-short.md is just a verdict page. With it, it becomes forward-worthy content.
- **The synthesizer never searches** — all reconciliation is done from the two input files. New facts must come from a re-run of the analytical agents, not the synthesizer.
