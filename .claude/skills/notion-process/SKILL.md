---
name: notion-process
description: >
  Processes pending feedback from the Notion "📋 Feedback" page of a MBB engagement.
  Reads unchecked items, applies them to local research files, syncs updated pages
  back to Notion, and marks each item as completed with a response.
  Use when: /notion-process, "process feedback", "обработай фидбэк", "применить правки notion".
argument-hint: <research_dir_name>  # e.g. tsmc-02.04.2026
---

# Notion Process — MBB Research Feedback

**Engagement:** $ARGUMENTS

---

## Step 1 — Resolve research directory

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

BASE="/Users/maximpuda/Projects/bcg-team/research"
ARG="$ARGUMENTS"

if [ -z "$ARG" ]; then
  echo "STATUS:NO_ARG"
  echo "Available:"
  ls "$BASE"
elif [ -d "$ARG" ]; then
  echo "STATUS:OK"
  echo "DIR:$ARG"
elif [ -d "$BASE/$ARG" ]; then
  echo "STATUS:OK"
  echo "DIR:$BASE/$ARG"
else
  echo "STATUS:NOT_FOUND"
  echo "Available:"
  ls "$BASE"
fi
```

**If STATUS is `NO_ARG` or `NOT_FOUND`:** Show available folders, ask which one. Stop.

**If STATUS is `OK`:** extract `DIR:...` as TARGET_DIR. Proceed.

---

## Step 2 — Read pending feedback from Notion

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py \
  read-feedback "<TARGET_DIR>"
```

This prints a JSON array like:
```json
[
  {"block_id": "abc-123", "text": "Intel is a customer, not a competitor — remove from competitive matrix"},
  {"block_id": "def-456", "text": "Add Taiwan annexation scenario to Risk section of Strategy 3"}
]
```

**If the array is empty `[]`:** Tell the user:
> "No pending feedback found in the Notion Feedback page. Add items as checkboxes (☐) and re-run."
Stop.

**If items exist:** Show the user:
```
Found N pending feedback items:
1. <text of item 1>
2. <text of item 2>
...

Processing with the analytics team...
```

Store the full JSON as PENDING_ITEMS. Proceed.

---

## Step 3 — Apply feedback to research files

Launch the `bcg-notion-processor` agent with:

```
research_dir: <TARGET_DIR>
feedback_items: <PENDING_ITEMS JSON>
```

The agent will read relevant research files, apply each feedback item, and return:
```json
{
  "changes": [
    {"stem": "segment-advanced-logic", "summary": "Removed Intel from competitor matrix, added to Key Customers section"},
    {"stem": "portfolio", "summary": "Updated Intel threat level from HIGH to N/A"}
  ],
  "item_responses": [
    {"block_id": "abc-123", "response": "Updated competitive matrix across 2 files. Intel reclassified as Key Customer."},
    {"block_id": "def-456", "response": "Taiwan annexation scenario added to Risk section in Strategy 3 (segment-advanced-logic.md, final-report.md)."}
  ]
}
```

Store this as PROCESSOR_OUTPUT. Proceed.

---

## Step 4 — Sync updated pages to Notion

For each entry in `PROCESSOR_OUTPUT.changes`, run:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py \
  sync-page "<TARGET_DIR>" "<stem>"
```

Run these sequentially. Show progress to user: `Syncing <stem>...`

---

## Step 5 — Mark feedback items as done in Notion

For each entry in `PROCESSOR_OUTPUT.item_responses`, run:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/notion_ops.py \
  mark-done "<TARGET_DIR>" "<block_id>" "<response>"
```

---

## Step 6 — Notify users in Notion

Load `notion-feedback.json` from TARGET_DIR to get `feedback_page_id`.

Collect the unique `author_id` values from all items in PENDING_ITEMS (each item has an `author_id` field — the Notion user ID of whoever wrote the feedback). Skip null values.

Build a summary, e.g.:
`"Your feedback has been processed. Updated: segment-advanced-logic, portfolio. Intel reclassified as Key Customer."`

Use the `notion-create-comment` MCP tool to post a comment on the Feedback page:
- `page_id`: feedback_page_id
- `rich_text`: a `mention` object for each unique author_id, then the summary text

This notifies exactly the users who wrote the feedback — no one else.

---

## Step 7 — Report to user

```
✅ Feedback processed

📋 Items completed: N
📄 Files updated: <list of stems>
🔔 Notion notification sent

Summary of changes:
• <stem>: <summary>
• <stem>: <summary>
```
