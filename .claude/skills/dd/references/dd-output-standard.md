# DD Output Standard — Product-Grade Decision Engine
**Based on: 5 rounds of product feedback (April 2026)**
**Applies to: dd-production, dd-risk-analyst, dd-red-team, dd-hypothesis-tester, and final output structure**

---

## Context

The DD pipeline produces three output layers. Each layer is a standalone product at a different price point.
All feedback rounds converge on one core insight:

> The product does not fail on quality. It fails when quality is buried inside a report-first structure.
> Reframe: not "here is the analysis" — but "here is the decision, here is why, here is what to do."

---

## Rule 1 — Three-Layer Output Architecture (MANDATORY)

Every DD engagement must produce exactly three files:

| File | Name | Reading time | Purpose |
|------|------|-------------|---------|
| `dd-short.md` | Decision Page | 10 seconds | First screen; binary signal |
| `dd-mid.md` | Key Issues Breakdown | 5 minutes | Pre-meeting briefing; top risks with consequences |
| `dd-decision-first.md` | Full Decision Report | 45–60 min | Investment committee; deep diligence |

The full institutional report (`dd-report.md`) remains as the legal/compliance reference layer.

**Each layer must be independently useful.** A reader who only sees `dd-short.md` must have enough to act.

---

## Rule 2 — Opening Block Structure (ALL LAYERS)

Every file must open in this exact order:

### Step 1: ONE LINE BOTTOM LINE
```
Bottom line:
Do not enter at this price.
```
Or the equivalent positive: `Proceed — entry below fair value.`

### Step 2: 10-SECOND DECISION (thresholds)
```
10-second decision:

→ PASS        at $[current price]
→ CONDITIONAL at $[X–Y]
→ PROCEED     below $[Z]
```

### Step 3: EXPLICIT ENTRY WARNING (if PASS or CONDITIONAL)
```
If you are considering entry now — this is the risk you are taking:

You are choosing between:
→ potential upside: +X% (requires everything to go right, simultaneously)
→ probable downside: -Y% (requires only one of N active risks to materialize)

If you enter at this price: expected loss -Z% in the base case.
```

### Step 4: PERSONAL PAIN HOOK
```
A [X]% drawdown on a [Y]% position = -[Z]% portfolio hit.
Most investors underestimate how quickly this compounds across a cycle.
```

**Rule: The verdict and the "do not enter" signal must appear before any analysis, explanation, or data.**

---

## Rule 3 — Verdict Block (dd-short.md format)

```
Verdict:      PASS / CONDITIONAL / PROCEED
Confidence:   X% ([interpretation: high / moderate / low] conviction)
Deal Score:   X.X / 10

You are paying $[X] for a business worth ~$[Y]
Expected downside: -Z% (base case)
Worst case: -W%

This deal breaks if:
→ [trigger 1]
→ [trigger 2]
→ [trigger 3]

Biggest risk:
[One sentence. Data → decision impact. Not "there is concentration risk" but "61% revenue from 4 customers building alternatives — one procurement shift = direct revenue cliff"]

Recommended action:
→ do not enter at current price ($[X])
→ wait for $[Y–Z] range before reconsidering
→ if already invested: [specific action]

Fair value:
$[X] – $[Y] (base: $[Z])
```

**Confidence must always include interpretation:**
- `>80%`: high conviction
- `65–80%`: moderate conviction
- `<65%`: low conviction — flag uncertainty explicitly

---

## Rule 4 — "So What?" Requirement (ALL RISKS)

Every risk in every layer must end with an explicit **So what?** block.

**Forbidden format:**
```
Customer concentration: 61% of revenue from 4 companies.
```

**Required format:**
```
61% of revenue from 4 companies (Microsoft ~19%, Meta ~11%, Amazon ~6%, Google ~6%).
All four are simultaneously funding AMD, custom chips, and in-house alternatives.

So what?
→ If 1–2 customers cut orders by 30% → direct revenue loss ~12%
→ Sentiment breaks → multiple compresses from 23x to 14x
→ Combined effect: -40–55% stock price without any technology failure

This alone justifies a PASS.
```

**The chain must be:** data → mechanism → quantified consequence → verdict anchor.

---

## Rule 5 — Decision Anchors (FULL REPORT)

Every major risk section must close with a verdict anchor:

```
→ This alone justifies a PASS.
```

Or for CONDITIONAL:
```
→ This alone requires a valuation adjustment of -15–25%.
```

Anchors prevent readers from getting lost in depth. They keep the verdict visible throughout the document.
Minimum frequency: after each Critical or High risk section.

---

## Rule 6 — Loss Visualization (MANDATORY)

Risk must be expressed in **absolute dollars first**, percentage second.

**Forbidden:**
```
Downside: -31%
```

**Required:**
```
Expected loss at current entry: -$1.3T in base case
Worst case: -$2.6T
(-31% / -62% in percentage terms)
```

The dollar figure is the hook. The percentage is the context.

---

## Rule 7 — "This Deal Breaks" Block Format

Must appear in every layer. Format for MID and FULL layers:

```
This deal breaks immediately if any one of these happens:

→ [Trigger 1] — [direct consequence] + [proven precedent if exists]
→ [Trigger 2] — [direct consequence] + [proven precedent if exists]
→ [Trigger 3] — [direct consequence] + [proven precedent if exists]

All [N] are already in motion. None need to fully materialize —
the market re-prices on the signal alone.
```

The word "immediately" is intentional — it communicates irreversibility.

---

## Rule 8 — Self-Identification Table (FULL REPORT)

Must appear before the Recommended Actions section. Enables the reader to locate their own situation.

```
| Your position | What this means | Recommended action |
|--------------|----------------|-------------------|
| Considering entry now at $[X] | Expected loss -Z% in base case | Do not enter. PASS. |
| Already holding — above [X]% of portfolio | Overexposed to single-multiple collapse | Reduce to [Y]% immediately |
| Already holding — [A]–[B]% of portfolio | Within range, unhedged | Buy puts. Pre-commit exit triggers now. |
| Already holding — below [A]% | Manageable exposure | Monitor triggers only |
| Considering entry at $[Y–Z] | Within DD fair value range | CONDITIONAL. Max [X]% AUM. |
```

Follow with explicit threshold statement:
```
If your [TICKER] position is above [X]% of your portfolio, you are overexposed.
```

---

## Rule 9 — CTA Structure (TWO HOOKS MINIMUM)

Every output file must contain at minimum **two CTAs**:

### Mid-document CTA (insert after Risk Matrix or Risk Summary table):
```
We identified [N] risks in this deal.

Want this level of clarity on your next investment?
→ Run Strategic DD in 48h — [URL]
```

### End CTA (final block before footnotes):
```
If you are making a $100k+ decision:

→ This analysis pays for itself if it prevents ONE mistake.

Run this for your deal.
→ Strategic DD in 48h — [URL]
```

The end CTA should be inside a code block (visual separation).

---

## Rule 10 — Narrative Failure Scenarios (FULL REPORT)

Failure scenarios must be written as **narratives with cascading events**, not as bullet lists.

**Forbidden format:**
```
Risk: Capex digestion
- Revenue slows
- Multiple compresses
- Stock falls 30-45%
```

**Required format:**
```
### Failure Scenario: The Digestion Event (probability: 25–30%)

[Company] reports Q[N] capex guidance flat with prior year.
Analysts call it a buying opportunity. Stock falls 14%.

Three months later: [competitor's] first [infrastructure] deployment goes live.
[Competitor] reports $[X]B revenue in a single quarter.

Six months later: [Company] discloses a $[Y]B inventory impairment —
the direct consequence of $[Z]B in non-cancellable supply orders placed at peak demand.

By [date]: revenue stabilizes at ~$[X]B — at [Y]% margins.
The investor who paid $[price] is sitting on a [-%] loss.

Warning signs visible today that the market is ignoring:
- [Signal 1] (classified as "[market narrative]")
- [Signal 2] (classified as "[market narrative]")
```

Minimum: 3 failure scenarios per full report. Each with: probability, cascade narrative, warning signs the market is misframing.

---

## Rule 11 — Pre-Mortem (FULL REPORT)

Must be written as a future-dated first-person narrative, not a list.

Format: "It is [2–3 years from now]. Here is what happened."

Include:
- The triggering event (specific, not generic)
- The cascade sequence (3–5 steps)
- The moment the market re-priced
- What the early warning signs were and why they were ignored
- Closing: "The investors who read the warning signs and acted in [timeframe] avoided this entirely."

---

## Rule 12 — Reduce Jargon

**Replace with plain English:**

| Jargon | Replace with |
|--------|-------------|
| TAM | addressable market |
| CAGR | annual growth rate |
| Multiple compression | valuation re-rating (stock drops even if earnings hold) |
| CUDA moat | software ecosystem switching cost |
| Capex digestion | customers stop ordering after over-buying |

Only use the technical term when the plain-English version is in the same sentence.

---

## Rule 13 — Value Bridge Format (MANDATORY IN MID + FULL)

```
Asking price:               $[X]

What DD says it's worth:    $[Y]   (base case)

Gap:                        -$[Z]  you overpay if you enter now

Adjustments that drive the gap:
  [Risk 1]:                  -$[A]  ([one-line explanation])
  [Risk 2]:                  -$[B]  ([one-line explanation])
  ...
                             ──────
Total adjustments:          -$[Z]

DD Fair Value:
  Base case:                 $[Y]   ([X]% below asking)
  Conservative:              $[Y1]  ([X]% below asking)
  Optimistic:                $[Y2]  ([X]% below asking)
```

Follow with probability-weighted expected return:
```
Probability-weighted expected return at current entry:
  Bull ([X]%): +[A]%  →  contribution: +[B]%
  Base ([Y]%): -[C]%  →  contribution: -[D]%
  Bear ([Z]%): -[E]%  →  contribution: -[F]%
  ─────────────────────────────────────────
  Expected return:           ~-[G]%
```

---

## Rule 14 — Hypothesis Scorecard Format

Every DD must test exactly 10 hypotheses. Each one must be:
- Stated as a testable claim (not a question)
- Assigned a verdict: ✅ CONFIRMED / ⚠️ UNCERTAIN / ❌ REFUTED
- Accompanied by 1–2 sentences of evidence
- Labeled with deal impact: Critical / High / Medium / Low

**Key rule:** 3 or more REFUTED hypotheses = mandatory PASS verdict, no exceptions.
State this explicitly: `[N] refuted hypotheses = PASS. No exceptions.`

---

## Rule 15 — Language and Framing Principles

### Data → Decision Impact (always)

**Forbidden:** `Customer concentration is 61%.`

**Required:** `61% revenue from 4 customers — if 1–2 reduce orders, direct revenue cliff + multiple collapse.`

### Position, not observation

**Forbidden:** `There are risks associated with the current valuation.`

**Required:** `You are buying a multiple, not a business. That multiple collapses non-linearly the moment the narrative cracks.`

### Asymmetry, always visible

In every layer, show that downside is larger than upside in absolute terms:
```
The asymmetry: bear downside is [N]x larger than bull upside.
```

---

## Summary Checklist for dd-production Agent

Before finalizing any DD output, verify:

**dd-short.md:**
- [ ] One-line bottom line in first 3 lines
- [ ] 10-second decision block (PASS/CONDITIONAL/PROCEED with prices)
- [ ] Loss in absolute dollars + percentage
- [ ] "This deal breaks if" with 3 triggers
- [ ] Biggest risk: data → decision impact (one sentence)
- [ ] Action: specific price thresholds, not "reconsider"
- [ ] Fair value range

**dd-mid.md:**
- [ ] Bottom line + 10-second decision at top
- [ ] Entry warning + decision framing (+upside vs -downside)
- [ ] Personal pain hook (position size → portfolio impact)
- [ ] Each issue has "So what?" with quantified consequence
- [ ] "This deal breaks IMMEDIATELY if" block
- [ ] "This deal only works if" conditions block
- [ ] Value bridge
- [ ] Mid-document CTA after risk table
- [ ] Strong end CTA ("$100k+ decision" format)

**dd-decision-first.md:**
- [ ] Explicit "DO NOT ENTER" trigger before verdict block
- [ ] Full verdict with confidence interpretation
- [ ] Self-identification table
- [ ] Failure scenarios as narratives (3 minimum)
- [ ] Pre-mortem as dated first-person narrative
- [ ] 20-risk matrix with P×I scoring
- [ ] Decision anchors ("this alone justifies a PASS") after each Critical/High risk
- [ ] Value bridge with probability-weighted expected return
- [ ] Strategic forks (what must be true for each verdict threshold)
- [ ] Exit triggers pre-commitment table
- [ ] Product CTA ("We found N critical risks — run this for your deal")
- [ ] Data quality appendix with source grades

---

*Compiled: April 2026 · Based on 5 feedback rounds on NVIDIA DD output*
*Applies to all future DD engagements*
