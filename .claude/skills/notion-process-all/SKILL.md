---
name: notion-process-all
description: >
  Scans ALL MBB research directories for pending Notion feedback and processes each one.
  Use when: /notion-process-all, "process all feedback", "проверь все фидбэки", "обработай все правки".
---

# Notion Process All — MBB Research Feedback

Scan every research directory for pending feedback and process each one.

---

## Step 1 — Find all research dirs with pending feedback

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

python3 - <<'EOF'
import json, subprocess, sys
from pathlib import Path

BASE = Path("/Users/maximpuda/Projects/bcg-team/research")
pending_dirs = []

for d in sorted(BASE.iterdir()):
    if not (d / "notion-feedback.json").exists():
        continue
    result = subprocess.run(
        ["python3", "/Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py",
         "read-feedback", str(d)],
        capture_output=True, text=True
    )
    items = json.loads(result.stdout or "[]")
    if items:
        pending_dirs.append({"dir": str(d), "name": d.name, "items": items})
        print(f"PENDING: {d.name} ({len(items)} items)", file=sys.stderr)
    else:
        print(f"CLEAN:   {d.name}", file=sys.stderr)

print(json.dumps(pending_dirs, ensure_ascii=False))
EOF
```

Parse stdout as JSON → `PENDING_DIRS` (array of `{dir, name, items}`).

**If `PENDING_DIRS` is empty:** Tell the user:
> "No pending feedback found across all research directories."
Stop.

**If items exist:** Show the user:
```
Found pending feedback in N engagements:
• <name>: X items
• <name>: Y items

Processing sequentially...
```

---

## Step 2 — Process each directory

For each entry in `PENDING_DIRS`, execute the full processing pipeline:

### 2a — Apply feedback to research files

Launch the `bcg-notion-processor` agent with:
```
research_dir: <entry.dir>
feedback_items: <entry.items as JSON>
```

Store the result as `PROCESSOR_OUTPUT`.

### 2b — Sync updated pages to Notion

For each file in `PROCESSOR_OUTPUT.changes`:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a
python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py \
  sync-page "<entry.dir>" "<stem>"
```

### 2c — Mark feedback items as done

For each item in `PROCESSOR_OUTPUT.item_responses`:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a
python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py \
  mark-done "<entry.dir>" "<block_id>" "<response>"
```

After finishing one directory, move to the next.

---

## Step 3 — Notify users in Notion

For each processed directory:

1. Load `notion-feedback.json` from `entry.dir` to get `feedback_page_id`
2. Collect unique `author_id` values from `entry.items` (each item has `author_id` — who wrote the feedback). Skip nulls.
3. Use the `notion-create-comment` MCP tool:
   - `page_id`: feedback_page_id
   - `rich_text`: a `mention` for each unique author_id, then the summary of changes for this engagement

Only the users who actually wrote the feedback get notified.

---

## Step 4 — Final report

```
✅ All feedback processed

Engagements updated: N
Total items completed: M
🔔 Notion notifications sent

• <name>: <N items> — <list of changed files>
• <name>: <N items> — <list of changed files>
```
