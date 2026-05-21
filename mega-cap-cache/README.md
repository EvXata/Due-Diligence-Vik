# Mega-Cap Cache

Pre-built company profiles for S&P 500 mega-caps (market cap >$100B).
Used by `bcg-researcher` to short-circuit Phase -1 data collection: instead of
running ~30 fresh WebSearches against the 10-K, transcripts, and consensus,
the researcher reads the cached profile and runs a 5-min **delta refresh**
against news from the last 30 days only.

## Schema

Each ticker has a file named `<ticker-lowercase>.md` with these mandatory
sections (the researcher will fail-soft if any are missing and fall back to
full WebSearch):

```
# <Company Name> (<TICKER>) — Mega-Cap Profile
**Refreshed:** YYYY-MM-DD
**Market Cap:** $X.XT
**Sell-Side Coverage:** N analysts | Consensus PT: $X (range $X–$Y)

## Segments (revenue + growth)
| Segment | Revenue (FY) | YoY | Operating Margin | % of Total |

## Key Competitors (with market shares)
## Recent Earnings Highlights (last 4 quarters)
## Regulatory / Litigation Posture (active matters only)
## Management (CEO/CFO with tenure and TSR vs S&P 500)
## Known Bear Arguments (short interest, analyst downgrades)
## Sources (URLs)
```

## Trigger logic

`bcg-researcher` does this on every run:
1. Lowercase + slugify the company name → `<slug>.md`
2. Check `mega-cap-cache/<slug>.md` exists
3. If yes: read cache + WebSearch for "<company> news last 30 days" + earnings news
4. If no: standard full Phase -1 (~18 min)

## Refresh cadence

Manually refreshed monthly. Each file has a `Refreshed:` line — if older than
60 days, the researcher will WARN but still use the cache (numbers >60 days
stale are flagged in the engagement log).

## Currently seeded

- `nvidia.md` — seeded 2026-05-20 for /dd nvidia engagement
