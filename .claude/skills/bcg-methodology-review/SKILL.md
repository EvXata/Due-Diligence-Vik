---
name: bcg-methodology-review
description: >
  MBB Methodology Review — cross-engagement analysis of the MBB Team system quality.
  Reads all past methodology-review.md files, identifies systematic patterns in agent errors,
  prioritizes improvements, and automatically applies high-confidence prompt fixes.
  Use when: /bcg-methodology-review, "review bcg methodology", "improve bcg agents",
  "what's wrong with bcg system", "analyze bcg team quality", "improve consulting agents".
argument-hint: [optional: focus on specific agent, e.g. "segment-analyst"]
disable-model-invocation: true
---

# MBB Methodology Review — Cross-Engagement Analysis

You are the **Partner / Managing Director** running a methodology improvement session.

---

## Step 0 — Check Available Data

```bash
# Count past engagements with methodology reviews
find /Users/maximpuda/Projects/bcg-team/research -name "methodology-review.md" | wc -l

# List all engagement folders
ls /Users/maximpuda/Projects/bcg-team/research/
```

Output to user:
```
## 📊 MBB Methodology Review

**Engagements with quality data:** [N]
**Folders found:** [list]
**Methodology log:** [exists / not yet created]

🚀 Launching cross-engagement analysis...
```

If N = 0:
```
No methodology reviews found yet. Run /bcg-team on a company first,
then the post-engagement bcg-methodologist will create methodology-review.md.
```
Stop if no data.

---

## Step 1 — Launch bcg-methodologist in Cross-Engagement Mode

One Agent call — bcg-methodologist:

```
Mode: cross-engagement
Company: N/A (cross-engagement analysis)
Project directory: /Users/maximpuda/Projects/bcg-team
Language: [user's language]

Read /Users/maximpuda/Projects/bcg-team/methodology/improvement-log.md (if exists).

For each file found at:
/Users/maximpuda/Projects/bcg-team/research/*/methodology-review.md
→ Read it and extract: engagement name, overall score, agent scores, issues found, proposed changes

Then:
1. Build pattern analysis table across all engagements
2. Identify P1 issues (>60% engagements, HIGH impact)
3. Identify P2 issues (>40% engagements)
4. For P1 issues: directly apply prompt changes to agent files in /Users/maximpuda/Projects/bcg-team/.claude/agents/
5. Update /Users/maximpuda/Projects/bcg-team/methodology/improvement-log.md
6. Save cross-engagement report to /Users/maximpuda/Projects/bcg-team/methodology/cross-engagement-[date].md

[If $ARGUMENTS is set: focus analysis on bcg-$ARGUMENTS agent]
```

Progress: `🔍 Analyzing [N] past engagements...`

---

## Step 2 — Output Results

After bcg-methodologist completes, read `methodology/improvement-log.md` and output to user:

```
## ✅ Methodology Review Complete

### Quality Trends
[Overall trend: improving / stable / degrading]
[Average score across all agents and engagements]

### Top Issues Found
[Top 3 systemic problems with frequency]

### Changes Applied (P1 — High Priority)
[List of agent files that were directly modified]

### Changes Proposed (P2 — Medium Priority)
[List of recommendations that need manual review]

📁 Full report: methodology/cross-engagement-[date].md
📁 Applied changes log: methodology/applied-changes.md
📁 Improvement history: methodology/improvement-log.md
```

---

## MBB Standards for Methodology Review

**P1 (auto-apply):** Issue appears in >60% of engagements AND has HIGH impact on output quality.

**P2 (propose only):** Issue appears in >40% of engagements OR has MEDIUM-HIGH impact.

**Never auto-apply:** Changes that alter the fundamental MBB framework (5 lenses, segmentation principle, Pyramid Principle).
