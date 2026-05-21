---
name: notion-export
description: >
  Exports a MBB research folder to Notion. Each file becomes a separate child page
  under one engagement parent page inside "MBB Research Hub". Reads NOTION_TOKEN from .env
  automatically. **Auto-routing (NEW):** on second and subsequent invocations, the script
  reads `notion-feedback.json` from the engagement folder to find the existing engagement page
  and appends new files there — no duplicate engagement pages, no duplicate Feedback pages.
  Use when: /notion-export, "export to notion", "upload to notion", "send to notion",
  "экспорт в notion", "загрузить в notion", "перенести в notion".
argument-hint: <research_dir_name or path>  # e.g. tsmc-30.03.2026
disable-model-invocation: true
---

# Notion Export — MBB Research

## How Auto-Routing Works (Persistent Engagement Linkage)

After the FIRST export of an engagement folder, the script saves `notion-feedback.json` containing:
```json
{
  "feedback_page_id": "...",
  "engagement_page_id": "..."
}
```

On every SUBSEQUENT export of the same folder (even with a different file via `NOTION_FILES_WHITELIST`), the script:

1. Reads `notion-feedback.json` from the target directory
2. Verifies the engagement page is still active (not archived) via Notion API
3. **Auto-routes new files under the SAME engagement page** — no new parent created
4. **Reuses the existing Feedback page** instead of creating duplicates

This means: once an engagement is established in Notion, **every** subsequent file added locally and re-exported lands under the same parent automatically. No env var management needed.

**Precedence order for parent page selection:**
1. `NOTION_PARENT_PAGE_ID` env var (explicit override — always wins)
2. `engagement_page_id` from `notion-feedback.json` (auto-detect from previous run)
3. New engagement page under `NOTION_MBB_ROOT_PAGE_ID` (first run only)

**Research to export:** $ARGUMENTS

---

## Step 1 — Resolve target directory

Run this bash block to resolve the path:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

BASE="/Users/maximpuda/Projects/bcg-team/research"
ARG="$ARGUMENTS"

if [ -z "$ARG" ]; then
  echo "STATUS:NO_ARG"
  echo "Available folders:"
  ls "$BASE"
elif [ -d "$ARG" ]; then
  echo "STATUS:OK"
  echo "DIR:$ARG"
elif [ -d "$BASE/$ARG" ]; then
  echo "STATUS:OK"
  echo "DIR:$BASE/$ARG"
else
  echo "STATUS:NOT_FOUND"
  echo "Looked for: $ARG and $BASE/$ARG"
  echo "Available folders:"
  ls "$BASE"
fi
```

**If STATUS is `NO_ARG` or `NOT_FOUND`:** Show the user the list of available research folders and ask which one to export. Stop.

**If STATUS is `OK`:** Extract `DIR:...` path, call it TARGET_DIR. Proceed to Step 2.

---

## Step 2 — Check root page and create per-engagement parent via MCP

Read `NOTION_MBB_ROOT_PAGE_ID` from the bash output of `.env`:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a
echo "ROOT_ID:$NOTION_MBB_ROOT_PAGE_ID"
```

**If ROOT_ID is empty:** Tell the user:
> "MBB Research Hub не настроен. Запусти `/notion-setup` для первичной настройки."
Stop.

**If ROOT_ID is set:**

Build the engagement title from the directory name. For example:
- `tsmc-30.03.2026` → "TSMC — MBB Engagement (30.03.2026)"
- `apple-15.04.2026` → "Apple — MBB Engagement (15.04.2026)"

Parse: split on first `-`, capitalize the company part, format date part in parentheses.

Create the per-engagement parent page using `notion-create-pages` MCP tool:
- parent: `{"type": "page_id", "page_id": "<ROOT_ID>"}`
- title: the formatted engagement title above
- icon: 📁

Store the returned page ID as `ENGAGEMENT_PAGE_ID`.

---

## Step 3 — Run export script

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

TARGET_DIR="<TARGET_DIR from Step 1>"
ENGAGEMENT_PAGE_ID="<ENGAGEMENT_PAGE_ID from Step 2>"

echo "Exporting: $TARGET_DIR"
echo "Notion parent: $ENGAGEMENT_PAGE_ID"
echo "---"
ls "$TARGET_DIR"
echo "---"

NOTION_PARENT_PAGE_ID="$ENGAGEMENT_PAGE_ID" \
  python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/notion-export/export_to_notion.py "$TARGET_DIR"
```

Stream all output to the user.

---

## Step 4 — Report result

After the script finishes, extract the last line containing the Notion URL and show the user:

```
✅ Export complete!

📁 Folder: <dir_name>
📄 Files: <N> exported
🔗 Notion: <URL from script output>
```

**If the script failed with a 403 error on block appending** (not page creation), that means the integration doesn't have access to the MBB Research Hub page yet.

Tell the user:
```
⚠️ Setup required (one-time):

1. Open: https://notion.so/<NOTION_MBB_ROOT_PAGE_ID without dashes>
2. Click "..." → "Connect to" → select your integration
3. Re-run: /notion-export $ARGUMENTS
```

**If any other error:** Show the full error message.
