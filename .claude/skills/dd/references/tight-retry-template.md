# Tight Retry Template — universal agent boilerplate

Every agent prompt in the DD pipeline should inject this block to prevent the
600s stream-watchdog kill that fires when a Sonnet/Haiku agent does many searches
and then composes a very long Write payload. The watchdog can't see streaming
inside a single Write call, so any Write that takes >600 seconds gets terminated.

Symptom of the failure mode (seen in this codebase): the agent's last message is
literally "Excellent. I now have sufficient data. Let me write the report." → 600s
pass → `<status>failed</status>` with no output file. Three different agents in the
NVIDIA run hit this on the first attempt.

## The boilerplate (copy verbatim into Agent prompts)

```
🚨 HARD CONSTRAINTS (watchdog protection):
- MAX <N> WebSearches total. After <N>, STOP searching and write.
- MAX <M> lines of output. Dense, decision-grade, no fluff. <M> is a hard ceiling.
- TARGET: complete the Write call within <T> minutes from agent start.
- If you find yourself wanting to add a 10th example or a 4th paragraph on a topic,
  STOP — you are about to trip the watchdog.
```

## Recommended caps by agent role

| Agent | Searches | Lines | Time |
|---|---|---|---|
| bcg-researcher (cache hit) | 4 | 600 | 7 min |
| bcg-researcher (no cache) | 12 | 700 | 18 min |
| bcg-market-mapper | 8 | 700 | 10 min |
| bcg-data-scientist | 10 | 500 | 12 min |
| bcg-segment-analyst (Tier-1) | 4 | 300 | 6 min |
| bcg-segment-analyst (Tier-2) | 3 | 180 | 4 min |
| bcg-domain-expert | 4 | 250 | 5 min |
| bcg-fact-checker | 4 | 250 | 5 min |
| dd-market-validator | 6 | 280 | 6 min |
| dd-hypothesis-tester (mega-cap) | 21 (3/hyp × 7) | 350 | 8 min |
| dd-hypothesis-tester (standard) | 35 (5/hyp × 7) | 450 | 12 min |
| bcg-portfolio-analyst (read-only) | 0 | 350 | 6 min |
| dd-risk-analyst (read-only) | 0 | 300 | 6 min |
| dd-red-team (read-only) | 0 | 350 | 6 min |
| dd-production-decision-first | 8 backfill only | 700 | 12 min |
| dd-production-summary | 0 | 250 | 4 min |
| dd-production (legal layer) | 0 | 600 | 6 min |
| dd-insight-booster | 0 | edit-in-place | 4 min |

## Why these specific numbers

- **Lines cap** is the primary watchdog defense. ~300 lines of decision-grade markdown
  takes ~3-4 minutes for Sonnet to compose, well under 600s.
- **Search cap** is secondary — prevents agents from spending all their time searching
  and running out of clock for the actual write.
- **Time target** is what we tell the agent to plan for. Agents respect time hints.

## Anti-patterns to forbid in agent prompts

- "Comprehensive analysis" → triggers maximalism → long write → kill
- "All 10-15 strategies" without a line cap → agents write 5-line preambles for each → 80 lines × 10 = 800 lines → kill
- "Cite at least 5 sources per claim" → padding the output → kill
- "Show your reasoning" outside a constraint → kill

## Incremental save fallback (advanced)

For agents that legitimately need long outputs (researcher, master report),
instruct them to write in **two passes**:

1. Save a skeleton/outline first via Write (300 lines)
2. Then Edit specific sections to flesh out content

This way the watchdog never sees a >600s single tool call.
