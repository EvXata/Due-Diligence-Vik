# DD Tournament Methodology

## 1. Tournament Question

Rank DD product/jobs by commercial value:

> Which diligence product should Vik DD sell next, to which buyer, using which proof artifact?

The tournament is deliberately narrow. It only scores deals where at least one of these was ordered or produced:
- `bear_case`
- `bull_case`
- `deep_audit`
- `fast_short`

## 2. Product Taxonomy

| Product | File signal | Buyer job | Best use |
|---|---|---|---|
| Bear Case Generator | `dd-red-team.md`, bear section in `dd-short.md`, breakup files | "Tell me how this deal fails before I commit." | Overpriced private rounds, token secondaries, mega-cap AI exposure |
| Bull Case Conditions | `bull-case.md` | "What must be true to still make money?" | Objection handling after a PASS/CONDITIONAL verdict |
| Deep Audit | `dd-decision-first.md` | "Give me IC-grade decision support." | $100k+ decisions, M&A, PE/VC, family-office tickets |
| DD Short Fast | `dd-short.md` without master | "Give me a pre-meeting read now." | Lead magnet, analyst workflow, fast screening |
| Acquirer Protection Package | `ma-exit-scenarios.md`, `customer-discovery.md`, `dd-risk-matrix.md` | "If I still want the deal, how do I structure protections?" | Strategic acquirer / M&A |

## 3. Scoring

Manual tournament score in `dd-deal-vector.csv` uses a 0-100 commercial-readiness rubric:

| Component | Weight | What earns points |
|---|---:|---|
| Decision pain | 25 | Large downside, live catalyst, high urgency, specific price decision |
| Product completeness | 20 | Deep audit + bear + bull + customer/M&A memos when relevant |
| Proof clarity | 20 | Verdict, confidence, fair value, deal breakers, hypothesis score all explicit |
| Buyer specificity | 15 | Clear buyer profile and use case: VC, acquirer, PM, token investor |
| Reusability | 10 | Can become template/SKU for similar deals |
| GTM wedge | 10 | Easy hook for outreach or landing page |

Penalties:
- `partial_pipeline`: cap at 20
- no `dd-decision-first`: cap at 70 unless intentionally fast-mode
- no clear buyer profile: -10
- no fair-value / price anchor: -10

## 4. Current Ranking

| Rank | Deal | Product vector | Score | Why |
|---:|---|---|---:|---|
| 1 | Cursor Series E | Bear + Deep | 95 | High-priced private AI round, high-conviction PASS, direct VC/growth buyer pain |
| 2 | dYdX token secondary | Bear + Bull + Deep | 94 | Perfect bear/bull pair: upside narrative exists but base verdict is PASS |
| 3 | T-Bank acquirer | Bear + Bull + Deep + M&A | 92 | Strong acquirer package with protections, sanctions, governance, CBS risk |
| 4 | Tinkoff secondary | Bear + Bull + Deep | 86 | Good sanctions/local-vs-western investor split; weaker source metadata than T-Bank |
| 5 | Microsoft full DD | Bear + Deep | 78 | Repeatable mega-cap public-equity product; less urgent than private/token deals |
| 6 | Microsoft prior DD | Bear + Deep | 76 | Useful but lower confidence and duplicate target |
| 7 | Bitcoin | Bear + Deep | 71 | Clear tripwires, but buyer segment is broader and less institutional |
| 8 | Microsoft fast | Bear + Fast | 65 | Good lead magnet, not IC-grade |
| 9 | NVIDIA partial | Partial | 15 | Not eligible until decision/bear layer exists |

## 5. GTM Discovery Interpretation

### Best wedge: "We kill bad deals before IC."

The strongest examples are not generic company reports. They are verdict-first artifacts where the buyer is about to overpay or needs to defend not doing a deal.

Recommended product line:

1. **Bear Case Generator** — $749-899, 24h.
   - Best for: VP/Sr Associate, PM, founder investor, crypto fund.
   - Promise: "3 ways this deal fails, fair-value gap, tripwires."

2. **Deep Audit** — $2,499-4,999, 48h.
   - Best for: Partner, GP, principal, acquirer.
   - Promise: "IC-grade PASS / CONDITIONAL / PROCEED memo."

3. **Bull/Bear Pair** — $1,499-1,999, 36h.
   - Best for: buyer who still wants the deal after a bear case.
   - Promise: "What has to be true to proceed, and what invalidates it."

4. **Acquirer Protection Package** — $4,999-9,999, 72h.
   - Best for: strategic acquirer / family office / M&A team.
   - Promise: "If you still buy, here is price, escrow, earn-out, R&W, and exit structure."

### Bad wedge: "MBB-quality DD report."

Too generic. The corpus shows the artifact wins when it is tied to a painful decision:
- "Do not enter at $50B."
- "Token upside exists but all four conditions must hit."
- "Russian acquirer can proceed only with escrow/earn-out/RPT audit."
- "Mega-cap is great; entry price is not."

## 6. How to Use in PreCompany Tournament

Map each deal row into a PreCompany product candidate:

```json
{
  "product_name": "Bear Case Generator",
  "buyer_profile": "VC / growth investor",
  "proof_artifact": "research/cursor-19.05.2026/dd-short.md",
  "decision_pain": "avoid $20B+ overpayment",
  "price_test": [749, 899, 1499],
  "conversion_hypothesis": "higher for VP/Sr Associate than Partner because it helps them prepare IC dissent",
  "success_metric": "reply rate, paid conversion, post-call quote: 'this changed the decision'"
}
```

Tournament rules:
- Do not compare all buyers together. Run separate brackets for VC/growth, public-equity PM, crypto fund, and acquirer.
- Score revenue and proof reuse separately. A low-price fast-mode product may be the best acquisition wedge even if deep audit wins revenue.
- Bull case should not be sold first unless buyer already wants to buy. Sell bear first; upsell bull conditions.

