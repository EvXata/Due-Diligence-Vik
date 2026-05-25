# Анализ: BCG Strategy Framework (2001) + pipeline-master-2026-05-19-f4.json
## → Рекомендации по усовершенствованию Strategy и DD pipeline в Due-Diligence-Vik

**Дата:** 22 мая 2026
**Источники:**
- BCG Strategy Framework (June 2001, 95 страниц) — каноническая методология BCG
- `BCG-team/pipeline-history/pipeline-master-2026-05-19-f4.json` (111 промптов, 10 фаз)
- Текущий `Due-Diligence-Vik/.claude/agents/` (~20 агентов, после T-Bank patches)

---

## Часть 1. Что показывает BCG Framework (2001)

### Каноническая последовательность 5 линз
```
Description → Advantage → Future → Options → Selection
   (понять источники преимущества)        (оценить стратегии)
```

**Четыре strategic pillars** (взаимосвязанные):
1. **Competitive Advantage** — затраты vs user value, sources + drivers
2. **Business Segmentation** — сегмент валиден если конкурент может в нём прибыльно жить без соседних
3. **Customer Needs** — unmet needs движут market growth и определяют тип advantage
4. **Segment Growth** — high growth ≠ value (growth trap)

### Strategy Pattern 2×2 (главная decision-логика BCG)
```
                  Is BU winning?
                Yes              No
        ┌─────────────────┬─────────────────┐
Stable  │ Fortify, grow   │ Improve returns │
(low    │ segment, expand │ no invest;      │
growth) │ adjacent, cash  │ shrink; divest; │
        │                 │ focus/diff      │
        ├─────────────────┼─────────────────┤
High    │ Invest aggress, │ Differ/focus to │
growth  │ acquire, expand │ gain share OR   │
        │ adjacent, max   │ sell space at   │
        │ option value    │ premium         │
        ├─────────────────┼─────────────────┤
New     │ Create options, │ Divest at prem  │
game    │ acquire/partner,│ to winners OR   │
        │ protect via     │ partner to win  │
        │ segment/focus   │ new game        │
        └─────────────────┴─────────────────┘
```

### Sources of sustainability (только 3 категории!)
1. **Unique resources** — может владеть только один (патенты, уникальное местоположение)
2. **Scarce resources / critical mass** — прохибитивно дорого реплицировать
   - Scale → cost → share → scale (virtuous circle)
   - Experience curve
   - Network effects
3. **Capabilities-based** — embedded в complex organisation, конкурент не понимает, не может купить, не успевает построить

### Три типа capabilities
- **Knowledge** (customer understanding, creativity, knowledge management) → drive user value
- **Process** (speed, operational excellence, organisational excellence, risk mgmt) → drive cost
- **Nimbleness** (responsiveness, adaptability, transformational ability) → drive any in new game

### Selection lens — три типа risk
1. **Competitor behaviour** (proactive + reactive; what would "killer competitor" look like)
2. **Exogenous risk** (growth, macro, factor costs, discontinuity timing)
3. **Implementation risk** (capabilities audit, Ready/Willing/Able, beliefs audit, **DICE** Duration/Integrity/Commitment/Effort)

### Viability viz two questions
- **Constraints:** corporate, financial, regulatory, time, market reaction
- **Feasibility:** culture/organisation fit, worst-case resources, consistency with past positioning

### Strategy Patterns — generated from creativity (Appendix 2)
- Rethink market | Look for anomalies | Find analogies | Look for compromises
- Apply new forces (alliances, technology, mindset shifts)
- Deconstruct business

---

## Часть 2. Что показывает pipeline-master-2026-05-19-f4.json

**Объём: 111 промптов, 10 фаз, 8 gates, 3 archetypes, 13 banned strings.**

### Структура (vs текущая Due-Diligence-Vik)

| Phase | Pipeline-master | Due-Diligence-Vik | Δ Промптов | Главные missing pieces |
|-------|----------------|-------------------|-----------|----------------------|
| **-2 Onboarding** | 4 промпта (O1-O4) | ❌ нет | +4 | Public extract, two-stage intake, feedback loop |
| **-1 Foundation** | 5 (BP1, F1, F2, F4, W1) | 1 (researcher) | +4 | Burning problem diagnosis, client context (NDA), syndicated data, first-run wow preview |
| **0 Mapping** | 7 (M1, M3-M8) | 2 (market-mapper, data-scientist) | +5 | Multi-axis segmentation, profit pool analysis, stress test, retailer category roles, initial hypotheses |
| **0.5 Quick Wins** | 4 (Q1-Q4) | ❌ нет | +4 | Value-at-stake → candidates → prioritized → activation pack |
| **1 Analysis** | 23 (A1-A27, 18 per-segment) | 1 segment-analyst × N + 1 domain-expert + 1 fact-checker | +20 | Per-segment: hypothesis log, customer needs, JTBD (B2B/seller/retailer), cohort, velocity/shelf turn, private label threat, SKU portfolio, intra-segment selection. Cross: brand equity, supply chain leverage |
| **2 Synthesis** | 8 (S1-S10) | 1 (portfolio-analyst) | +7 | Stakeholder alignment, sensitivity+pre-mortem, cross-segment dynamics, capital allocation shift, exit readiness, legal blocker audit |
| **2.5 Activation** | 24 (X1-X19, GTM stack of 9) | 1 (gtm-analyst) | +23 | Capability gaps, operating model, corp dev, pricing/RGM, marketing mix, innovation pipeline, aftermarket, ESG, data/AI readiness, tax, litigation, GTM (ICP/offer/channels/pipeline/ads/direct/organic/PLG/marketplace), retail GTM overlay, channel governance, carve-out, trust/safety |
| **3 Communication** | 27 (C1-C13, по главам) | 1 (production → final-report) | +26 | 8-chapter final report, risk register, KPI tree, governance, weekly/monthly/quarterly plans, balance sheet, segment presentations, strategy presentations, board pack, investor narrative, one-pager |
| **4 Format** | 1 (C14) | implicit (PDF skill) | 0 | Format conversion as explicit phase |
| **Post Methodology** | 8 (C5.0, C5.3, C16-C22) | 1 (methodologist) | +7 | Self-critique, cross-engagement compare, NPS, value realization tracker, weekly value sync, refresh trigger, daily standup, daily metrics pulse |

**Δ Total: ~95 промптов недостаёт.** Это не означает что Due-Diligence-Vik в 5× хуже — у нас более крупнозернистые агенты (один агент делает работу 3-5 промптов master pipeline). Но granularity master pipeline даёт несколько критических преимуществ.

### Архитектурные особенности master pipeline (которых у нас нет)

1. **`pipeline_spec_version`** — версионирование самого pipeline (1.2)
2. **`consolidated_output_file: RAWSTRAT.md`** — append-only единый файл всех outputs с separator-блоками `## [<prompt_id>] [<ISO8601_timestamp>] [<segment_slug_if_any>]`
3. **`archetypes`** — таксономия engagement'а:
   - **industry** (12 типов: B2B-HW/SW/SVC, B2C-RTL/DTC, B2B2C, MARKET, FIN, HCP, HCY, IND, ENRG)
   - **ownership** (7 типов: PUBLIC, PE, VC, FAM, FOUNDER, STATE, COOP)
   - **growth_motion** (7 типов: PLG, SALES, OUTBOUND, MKTPL, RETAIL, CHANNEL, COMMUNITY)
4. **`gates`** — 8 блокирующих гейтов с явными checks (e.g., G0_after_onboarding требует 10+ competitors в public-extract, confidence tags, two-stage intake)
5. **`banned_strings`** — список запрещённых строк (анти-копипаст из прошлых engagements: Megapack, Starlink, Optimus, BESS, ServiceNow, etc.)
6. **`dependency_graph`** — explicit DAG (111 nodes)
7. **`per_segment` флаг** — некоторые промпты автоматически копируются под каждый сегмент (🔁)
8. **`webSearch` флаг** — explicit declaration (🔍) — позволяет batch-ить промпты без поиска отдельно от поисковых

---

## Часть 3. Где Due-Diligence-Vik отстаёт от обоих источников

### А. Strategy production — что у нас слабее BCG Framework 2001

| BCG Framework требует | У нас сейчас | Gap |
|----------------------|-------------|-----|
| **Cost vs User value game classification** (Шаг 2 Advantage lens) | Не делается явно | Стратегии генерируются без знания "это cost game или user-value game" → размытость рекомендаций |
| **Sources + Drivers + Capabilities 3-уровневая декомпозиция** | Только sources иногда | Стратегии не привязаны к sustainability mechanism (unique/scarce/capabilities) |
| **Strategy Pattern 2×2** (winning × stable/high-growth/new-game) | Implicit, не используется явно | Архетипы стратегий "Defend/Pivot/Scale/Focus/Innovate" — это не та таксономия что у BCG (Fortify/Grow segment/Expand/Cash/Invest/Acquire/Create options/Differentiate/Divest/Partner) |
| **Game theory + Growth-Growth matrix для competitor behaviour** (Selection lens) | Нет | Stress-сценарии не проигрывают "killer competitor" formally |
| **Beliefs audit, Ready/Willing/Able, DICE для implementation risk** | DICE упоминается в шаблоне portfolio, но не считается формально | Implementation risk остаётся качественным |
| **Capability typology: knowledge/process/nimbleness** | Нет | Капабилити обсуждаются amorphно |
| **Creativity questionnaire** (Appendix 2 — anomalies, analogies, compromises, new forces, deconstruction) | Нет | Стратегии generated механистически из benchmarks |
| **Industry lifecycle, Strategic Fit Cycle, Environment matrix** (Volume/Stalemate/Specialised/Fragmented) | Нет | Сегмент не классифицируется в Porter-style environment |

### Б. Strategy production — что у нас слабее master pipeline

1. **Нет Onboarding фазы**
   - Master: O1 public extract (10+ competitors + 24-mo events, confidence tags) → O2 confirmation form (≤6 questions, async) → O2 intake call agenda (≤8 questions, 60 min sync) → O3 ingest answers (NDA flag) → O4 intake feedback form
   - У нас: пользователь сразу пишет "/dd Tinkoff Bank" — context минимальный

2. **Нет BP1 burning problem diagnosis**
   - Master: explicit prompt "what is the CEO losing sleep over" + проверка 4 dependencies
   - У нас: hypotheses formed by Partner brief заранее без проверки что это правда главная боль

3. **Нет F4 syndicated data ingest**
   - Master: explicit raw-data/syndicated/* нормализация (Nielsen, IDC, Gartner)
   - У нас: только WebSearch + WebFetch (без syndicated, без paid databases)

4. **Нет W1 first-run wow preview** — pre-engagement teaser (free deliverable)

5. **Mapping слишком thin**
   - Master: M1 overview + M3 multi-axis segmentation + M4 profit pool analysis + M5 stress test + M6 retailer category roles + M7 initial hypotheses + M8 retailer review prep
   - У нас: 1 market-mapper делает всё в одном промпте — pool analysis отсутствует, retailer/channel category не различается

6. **Нет Phase 0.5 Quick Wins**
   - Master: 4 промпта — value-at-stake (top-line opportunity), candidates list, prioritized list, activation pack (включая plan/owners/KPI)
   - У нас: quick wins не существует как отдельный deliverable — клиент получает только большую стратегию

7. **Per-segment analysis — у нас 1 промпт где у master 18**
   - Master per-segment: description, advantage, advantage tools, customer needs, future, growth, SaaS growth, marketplace growth, cohort revenue, velocity/shelf turn, private label threat, B2B journey, seller JTBD, retailer JTBD, hypothesis log, options, SKU portfolio, intra-segment selection, distillation
   - У нас per-segment: 1 segment-analyst делает Description + Advantage + Future + 10-15 strategies + Distillation
   - **Это самый большой gap.** Один наш промпт = 18 master'овских

8. **Нет A18 hypothesis log per segment**
   - Каждый сегмент имеет running JSON-лог hypotheses, который updateется по мере analysis
   - У нас hypotheses глобальные (10 H-D1...H-S1), не per-segment

9. **Нет cross-segment analyses (A24-A26)**
   - Brand equity diagnostic, supply chain leverage audit, cross-segment strategies — отдельные deliverables
   - У нас всё это implicit в portfolio.md

10. **Synthesis (Phase 2) — у нас 1 промпт где у master 8**
    - Master: selection lens, stakeholder alignment (NDA-read), sensitivity + pre-mortem, portfolio matrix, cross-segment dynamics (synergies + cannibalization), capital allocation shift, exit readiness (QoE + IPO-readiness), legal blocker audit
    - У нас: portfolio-analyst делает всё в одном
    - **Stakeholder alignment, exit readiness, legal blocker audit отсутствуют полностью**

11. **Phase 2.5 Activation — у нас 1 промпт где у master 24**
    - Это самый функциональный gap. Master имеет:
    - **Capability gaps assessment** — explicit gap-to-strategy mapping
    - **Operating model blueprint** — talent location, structure
    - **Corp dev plan** — explicit M&A target list
    - **Pricing/RGM diagnostic** — packaging economics, RGM (revenue growth management)
    - **Marketing mix audit** — MMM, trade promo
    - **Innovation pipeline audit** — innovation ROI, time-to-market
    - **Aftermarket strategy** — customer success
    - **ESG strategy**
    - **Data/AI readiness**
    - **Tax structure implications**
    - **Litigation/regulatory risk register**
    - **GTM stack (9 sub-prompts):** ICP+DMU, offer stack, channels, pipeline model, ads, direct sales, organic, PLG playbook, marketplace GTM
    - **Retail GTM overlay** — trade marketing, shopper marketing
    - **Channel governance audit**
    - **Carve-out playbook**
    - **Trust/safety ops playbook**
    - У нас: gtm-analyst (только GTM core) + creative-strategist (только creatives)
    - **Operating model, capability gaps, corp dev, pricing, ESG, data/AI, tax, litigation, carve-out, trust/safety — нет вовсе**

12. **Communication (Phase 3) — у нас 1 промпт где у master 27**
    - Master: final-report разделён на 8 chapters (C1.1-8) → KPI tree → governance blueprint → weekly/monthly/quarterly plans → balance sheet implications → segment-level presentations (C7.1-4 per segment) → strategy-level presentations (C8.1-3 per strategy) → portfolio presentation → executive summary presentation → one-pager → investor narrative (VC pitch + IPO narrative) → board pack
    - У нас: bcg-production делает один файл `final-report.md`
    - **Investor narrative, board pack, weekly/monthly/quarterly plans отсутствуют**

13. **Methodology layer — у нас 1 промпт где у master 8**
    - Master: C16 self-critique, C17 cross-engagement compare, C19 NPS, **C20 value realization tracker** (period-based), C21 weekly value sync, C22 strategy refresh trigger (signals → trigger.json), C5.0 daily standup, C5.3 daily metrics pulse
    - **Value realization tracking** — это ongoing post-delivery measurement KPI realization. У нас полностью отсутствует.
    - **Refresh trigger** — automatic detection that strategy needs review.

### В. DD production — что у нас слабее обоих источников

Strategy DD — это узкая вертикаль (применение Strategy + adversarial layer). Master pipeline сам не DD-focused — но Strategy DD должен **переиспользовать всё это качество** + добавить DD-специфику.

| DD-критичное | BCG Framework говорит | Master pipeline даёт | У нас есть |
|--------------|----------------------|---------------------|-----------|
| Pre-mortem | "что произошло через 3 года когда сделка failed?" — Selection lens | S3_sensitivity_analysis → pre-mortem.md | dd-decision-first.md имеет narrative pre-mortem ✅ |
| Exit readiness | Не покрыто | S9_exit_readiness_assessment (QoE + IPO readiness) | Только в --investor-profile (ma-exit-scenarios) — не в base DD ⚠️ |
| Legal blocker audit | Не покрыто | S10_legal_blocker_audit | ❌ нет |
| Litigation risk register | Не покрыто | X14_litigation_regulatory_risk_register | ⚠️ часть dd-risk-matrix, но не register-формат |
| Capability gap assessment | Capabilities audit (Adv lens) | X1_capability_gap_assessment | ❌ нет |
| Carve-out playbook | Не покрыто | X18_carve_out_playbook | ❌ нет (критично для PE deals) |
| Operating model | Не покрыто | X2_operating_model_blueprint | ❌ нет |
| Corp dev plan | Не покрыто | X5_corp_dev_plan | ❌ нет (критично для bolt-on roll-ups) |
| QoE (Quality of Earnings) | Не покрыто | S9 включает QoE | ❌ нет |
| Stakeholder alignment | Не покрыто | S2_stakeholder_alignment_check (NDA-read) | ❌ нет (критично для board approval) |
| 100-day plan | Implementation | C5.1_monthly_roadmap, X1 capability gaps | ⚠️ есть в dd-decision-first но без detail |

---

## Часть 4. Рекомендации по усовершенствованию

Разделены на 3 уровня по cost-benefit. Все рекомендации specific и actionable.

### Уровень 1: Quick wins (≤1 неделя работы, high ROI)

#### 1.1 Добавить cost-vs-user-value game classification в bcg-segment-analyst

**Текущая проблема:** Стратегии generated без явной классификации (это cost-driven или differentiation-driven segment). Бенчмарки используются нерефлексивно.

**Изменение:** в Step 2 (Advantage Lens) добавить блокирующий sub-step:
```
Cost-vs-User-Value Game Classification (BLOCKING):
1. Price premium analysis — есть ли variance в реализации цен?
2. Supply curve — overlap competitors на cost level?
3. Verdict: cost game / user value game / both
4. ALL strategies должны быть consistent с verdict
```

**Expected gain:** стратегии становятся coherent (если segment — cost game, не предлагаем premium positioning).

#### 1.2 Добавить Sources/Drivers/Capabilities 3-уровневую декомпозицию

**Текущая проблема:** Стратегии говорят "moat = data" но не объясняют какой capability создаёт этот moat и какой driver обеспечивает sustainability.

**Изменение:** в bcg-segment-analyst Advantage Lens — обязательная таблица:
```
| Source | Driver (unique resource / scarce resource / capability) | Capability type (knowledge/process/nimbleness) | Sustainability years |
```

**Expected gain:** stress-test "is this moat real" получает quantitative answer.

#### 1.3 Заменить наши archetypes (Defend/Pivot/Scale/Focus/Innovate) на каноническую BCG taxonomy

**Текущая проблема:** Strategy archetypes — это наша outdoor taxonomy. BCG framework использует другую (Fortify, Grow segment, Expand adjacent, Cash, Invest, Acquire, Create options, Differentiate/focus, Divest, Partner) с явной привязкой к Pattern 2×2.

**Изменение:** в bcg-segment-analyst → требовать что каждая strategy маркирована **двумя** taxonomies:
- Наш archetype (для familiarity)
- BCG pattern (Fortify/Cash/Differentiate/etc.) с явным "winning × game-type" reasoning

**Expected gain:** стратегии становятся trace-back to BCG framework — повышается perceived methodological rigor.

#### 1.4 Добавить S10 legal blocker audit в DD pipeline

**Изменение:** новый агент `dd-legal-blocker-auditor` (Phase DD-2.5, parallel с dd-risk-analyst):
- License/permit transferability check
- Change-of-control clauses в material contracts
- Regulatory approval requirements (antitrust, sector-specific)
- Pending litigation что блокирует closing
- IP encumbrances

**Output:** `dd-legal-blockers.md`

**Expected gain:** закрывает hidden deal-breakers до production stage. T-Bank engagement не имел этого — мы могли упустить FAS approval requirement для Точка M&A.

#### 1.5 Добавить S2 stakeholder alignment check

**Изменение:** новый агент `dd-stakeholder-alignment` (Phase DD-2, parallel):
- Map all material stakeholders (board, key execs, major shareholders, lenders, regulators, key customers, unions)
- Per stakeholder: position on the deal (support / neutral / oppose), influence, leverage
- Identify hostage situations и opportunity для negotiation

**Output:** `dd-stakeholder-alignment.md`

**Expected gain:** для M&A/PE deals — критично понимать кто может заблокировать.

---

### Уровень 2: Medium investment (≤1 месяц, ощутимое улучшение качества)

#### 2.1 Реструктурировать Phase 1 в multi-prompt per-segment

**Текущее:** 1 `bcg-segment-analyst` промпт делает Desc+Adv+Future+Strategies+Distillation.

**Предлагаемое:** разбить на под-агенты per-segment:
- `segment-description` (1 промпт)
- `segment-advantage` (1 промпт, + cost/UV gate, + sources/drivers/capabilities)
- `segment-future` (1 промпт, + 4 forecasts)
- `segment-customer-needs-jtbd` (1 промпт — новое, NotYet covered)
- `segment-hypothesis-log` (1 промпт — JSON running log)
- `segment-options-generation` (1 промпт — generates 15-20 strategies)
- `segment-intra-segment-selection` (1 промпт — выбирает top 3-5)
- `segment-distillation` (1 промпт — summary)

**Trade-off:** wall-clock увеличится (с 15 мин → 30-40 мин для Phase 1) **НО** quality по depth каждого аспекта вырастет drастически. Можно сделать optional flag `--deep-segment` для DD engagements, default остаётся single-agent для quick BCG runs.

#### 2.2 Добавить Phase 0.5 Quick Wins

**Новые агенты:**
- `quick-wins-value-at-stake` (Q1) — top-line opportunity quantification
- `quick-wins-candidate-list` (Q2) — 10-20 specific actions
- `quick-wins-prioritization` (Q3) — RICE / impact-effort matrix
- `quick-wins-activation-pack` (Q4) — owner, KPI, 30-day plan per win

**Trigger:** автоматически после Phase 1 (BCG mode) или опционально через `/bcg-team --quick-wins`.

**Expected gain:** клиент получает actionable 30-day wins ДО того как полный strategic report готов — это меняет perceived value engagement'а (instant credibility).

#### 2.3 Реструктурировать Phase 2.5 Activation — добавить минимум 5 missing modules

Приоритет (по DD-релевантности):
1. **`bcg-operating-model-architect`** (X2) — talent location, structure, span of control. Критично для post-close 100-day planning.
2. **`bcg-pricing-rgm-analyst`** (X6) — pricing strategy, RGM, packaging economics. Огромный value driver, у нас полностью отсутствует.
3. **`bcg-capability-gap-assessor`** (X1) — explicit gap-to-strategy mapping. Закрывает "что нам нужно построить чтобы стратегия работала".
4. **`bcg-corp-dev-planner`** (X5) — для PE deals роль M&A target list критична (bolt-on roll-up thesis).
5. **`bcg-carve-out-architect`** (X18) — для divestiture/carve-out DD scenarios. Без этого мы не покрываем целый класс PE deals.

Optional: ESG, data/AI readiness, tax — добавить когда есть запрос.

#### 2.4 Разбить bcg-production на 8 chapter-агентов + 4 cross-cutting

**Текущее:** monolithic `final-report.md` (~500-700 строк) — Haiku агент рискует hit context limits при больших engagements (Phase 1 уже видели streamup at 7+ segments в Microsoft DD).

**Новое:**
- 8 `production-chapter-N` агентов (по 1 на главу final report) — parallel
- 4 cross-cutting агента: investor-narrative, board-pack, executive-summary, one-pager

**Expected gain:**
- Parallelism → wall-clock сокращается с ~5 мин до ~2-3 мин
- Каждый chapter получает focused attention (lower hallucination)
- Investor narrative + board pack — новые deliverables, расширяют рынок

#### 2.5 Внедрить master-anchors.json в Phase 2 (не только DD-3a)

**Текущее:** master-anchors.json создаётся только dd-production-decision-first.

**Предлагаемое:** каждая critical-decision phase производит свой anchors.json:
- `portfolio-anchors.json` после Phase 2 (recommendation, top strategies IDs, MBB matrix coordinates)
- `dd-anchors.json` после DD-3a (всё что сейчас в master-anchors)

**Expected gain:** downstream агенты читают small JSON вместо большого markdown → fewer hallucinations, faster.

#### 2.6 Добавить consolidated RAWSTRAT.md — append-only лог всех outputs

**Текущее:** outputs разбросаны по 25+ файлам в OUTPUT_DIR.

**Предлагаемое:** в каждом агенте — финальная инструкция:
```
After Write to your designated output file, append the same content to [OUTPUT_DIR]/RAWSTRAT.md with header:
## [<agent_id>] [<ISO8601_timestamp>] [<segment_slug_if_any>]
<full content>
---
```

**Expected gain:**
- Один файл для audit trail (compliance / re-run reasoning)
- Можно diff'ать между engagements
- Облегчает methodologist'у full-pass review

---

### Уровень 3: Strategic upgrades (≤3 месяца, structural improvements)

#### 3.1 Внедрить archetype-driven prompt tuning

**Идея master pipeline:** classifyengagement по 3 осям до старта:
- **Industry** (12 вариантов: B2B-HW/SW/SVC, B2C-RTL/DTC, B2B2C, MARKET, FIN, HCP, HCY, IND, ENRG)
- **Ownership** (PUBLIC/PE/VC/FAM/FOUNDER/STATE/COOP)
- **Growth motion** (PLG/SALES/OUTBOUND/MKTPL/RETAIL/CHANNEL/COMMUNITY)

**Реализация:**
- Новый Phase -2 prompt `O0_archetype_classifier` — classifies before pipeline starts
- Agents читают archetype tags и активируют industry-specific gates (e.g., `IND-FIN` triggers revenue-TAM gate в bcg-data-scientist; `OWN-PE` triggers carve-out playbook автоматически)
- T-Bank engagement: `IND-FIN, OWN-PE+STATE-influence, GM-RETAIL` → автоматически revenue-TAM gate + carve-out option + retail-overlay GTM

**Expected gain:** prompts становятся **adaptive** к context'у. T-Bank balance-aggregate TAM bug не повторится — gate fire-ит автоматически на `IND-FIN`.

#### 3.2 Внедрить explicit gates с blocking checks

**Текущее:** мы только что добавили несколько inline gates (T-Bank patches). Они scattered по агентам.

**Предлагаемое:** centralised `gates.json` в `.claude/skills/bcg-team/references/`:
```json
{
  "G0_after_onboarding": {"blocking": true, "checks": ["company-brief.md exists", "10+ competitors", "confidence tags per claim", "глоссарий метрик section"]},
  "G1_after_mapping": {"blocking": true, "checks": ["3-7 segments identified", "Tier-1/Tier-2 classified", "profit pools mapped", "stress test passed"]},
  "G2_after_segment_analysis": {"blocking": true, "checks": ["100% segment coverage in validation-report", "cost-vs-UV game classified", "sources/drivers/capabilities table per segment"]},
  ...
}
```

**Runner:** small bash script `check_gate.sh` который читает `gates.json`, чекает условия, возвращает PASS/FAIL.

**Expected gain:** quality bugs catch до того как propagate downstream.

#### 3.3 Внедрить banned_strings registry

**Текущее:** нет защиты от копипаста между engagements (один из риск-факторов когда agents используют "templates").

**Предлагаемое:** `banned_strings.json` per engagement (gitignored) + auto-check:
```bash
# В конце каждой фазы:
for file in $(ls *.md); do
  for str in $(cat banned_strings.json | jq -r '.[]'); do
    grep -l "$str" $file && echo "❌ Banned string '$str' in $file"
  done
done
```

Banned strings auto-populate из: предыдущих engagements в research/ (любая company name которая встречается там), known template phrases ("вставьте ...", "TODO", "...").

**Expected gain:** ловит copy-paste contamination что особенно вредно в DD (кросс-engagement leakage).

#### 3.4 Внедрить value realization tracker (C20)

**Идея master pipeline:** после delivery строится tracker который measures KPI realization период за периодом.

**Реализация:**
- Новый агент `bcg-value-realization-tracker` (Sonnet)
- Triggered manually (или scheduled) post-delivery: `/bcg-track <engagement_dir> --period 2026-Q3`
- Reads original strategy KPI tree (C3) → fetches current public data → computes variance
- Output: `value-tracker-2026-Q3.md` с verdict (on track / behind / ahead / pivot needed)

**Connection с DD:** для DD client что invested, можно автоматически tracking thesis validation. Если NIM falls below trigger в dd-decision-first exit table → fires alert.

**Expected gain:** transforms one-off engagement в ongoing relationship → higher client LTV.

#### 3.5 Внедрить refresh trigger (C22)

**Идея:** strategy/DD должна automatically detect когда она obsolete.

**Реализация:**
- `bcg-refresh-trigger` агент (Haiku, fast)
- Cron-scheduled: ежемесячно проверяет каждый archive engagement
- Reads master-anchors + exit-trigger table → fetches current public data → если any trigger fired, generates `refresh-signals.md` для клиента
- Outputs `refresh-trigger.json` — machine-readable signal

**Expected gain:** transforms static deliverable в live asset. Особенно для DD — exit triggers ARE the value (если автоматически fire'ить — клиент видит ROI каждый месяц).

#### 3.6 Внедрить creativity questionnaire в Options Lens

**Из BCG Framework Appendix 2:**
- Rethink the market (что если customers совсем другие?)
- Look for anomalies (что в данных не fit'ит pattern?)
- Find analogies (какие industries прошли через подобный transition?)
- Look for compromises (какие customer compromises мы можем сломать?)
- Apply new forces (какие alliances / technologies могут перепрограммировать game?)
- Deconstruct the business (какие parts of value chain могут существовать independently?)

**Реализация:** в `bcg-segment-analyst` (или в новом `segment-options-generation`) — обязательный sub-step "Creativity check" перед финальным списком стратегий:
- Для каждой из 6 categories — explicit 1-paragraph attempt
- Если attempt дал new strategy → tag её `[creativity-derived]`

**Expected gain:** стратегии становятся менее formulaic. Мы видели в T-Bank engagement что стратегии иногда повторяют стандартные templates (Defend X, Pivot Y) без real creativity.

#### 3.7 Внедрить game theory + competitive scenario tree в Selection lens

**Из BCG Framework:** explicit game theory matrix + growth-growth analysis + "killer competitor" hypothetical.

**Реализация:** новый агент `bcg-competitive-scenario-tree` (или встроить в dd-red-team для DD):
- Identify top-3 competitors
- For each: list 3 likely moves (proactive) + 3 reactive moves
- Game theory matrix: our 3 strategies × their 3 responses → 9 payoffs
- Identify Nash equilibria
- "Killer competitor" hypothesis — что было бы если конкурент с unlimited capital + zero regulatory friction?

**Output:** `competitive-scenario-tree.md`

**Expected gain:** stress-testing strategies против strategic moves конкурентов — на T-Bank engagement мы упустили competitive analysis "что если Сбер запустит price war на cards"?

---

## Часть 5. Конкретные приоритеты для immediate roadmap

### Quarter 1 (Q3 2026 — июль-сентябрь): "Catch up to canonical BCG"
1. **Уровень 1.1** Cost-vs-UV game classification gate в bcg-segment-analyst (≤1 день)
2. **Уровень 1.2** Sources/Drivers/Capabilities decomposition в bcg-segment-analyst (≤1 день)
3. **Уровень 1.4** dd-legal-blocker-auditor agent (≤2 дня)
4. **Уровень 1.5** dd-stakeholder-alignment agent (≤2 дня)
5. **Уровень 2.5** master-anchors.json для Phase 2 (≤1 день)
6. **Уровень 2.6** RAWSTRAT.md consolidated output (≤1 день — добавить в base agent template)

**Effort:** ~1-2 недели разработки. **Impact:** DD reports получают legal/stakeholder coverage; стратегии становятся methodologically rigorous; debug audit trail работает.

### Quarter 2 (Q4 2026): "Granularity boost"
1. **Уровень 2.1** Per-segment multi-prompt split (`--deep-segment` flag) (≤1 неделя)
2. **Уровень 2.2** Phase 0.5 Quick Wins (4 новых агента) (≤1 неделя)
3. **Уровень 2.3** 5 Activation modules (operating model, pricing/RGM, capability gaps, corp dev, carve-out) (≤2 недели)
4. **Уровень 2.4** Phase 3 split в 8 chapters + 4 cross-cutting (≤1 неделя)

**Effort:** ~5-6 недель. **Impact:** depth analysis ↑↑, investor/board deliverables появляются, PE-deal coverage становится complete.

### Quarter 3 (Q1 2027): "Adaptive + ongoing"
1. **Уровень 3.1** Archetype-driven prompt tuning (industry/ownership/growth motion) (≤2 недели)
2. **Уровень 3.2** Centralised gates.json + check_gate.sh runner (≤1 неделя)
3. **Уровень 3.3** banned_strings registry + auto-check (≤3 дня)
4. **Уровень 3.4** Value realization tracker (≤1 неделя)
5. **Уровень 3.5** Refresh trigger (≤1 неделя)

**Effort:** ~5-6 недель. **Impact:** pipeline становится adaptive, prevents recurrence of past bugs, transforms one-off engagement → ongoing client relationship.

### Long-tail (Q2 2027+): "Methodological purity"
1. **Уровень 3.6** Creativity questionnaire (≤3 дня)
2. **Уровень 3.7** Game theory + scenario tree (≤1 неделя)
3. Strategy Pattern 2×2 taxonomy adoption (изменить strategy archetypes labels везде — labour-intensive, ≤2 недели)

---

## Часть 6. Что НЕ копировать из master pipeline

Не всё в pipeline-master-2026-05-19-f4.json подходит для Due-Diligence-Vik:

1. **Retailer-specific промпты** (M6, M8, A11, A16 velocity/shelf turn, X16 retail GTM overlay) — узкая retail/CPG specifika. Полезно если делаем DD на retail компанию, но не universal. → Реализовать как **archetype-conditional** (только если `IND-B2C-RTL`).
2. **Marketplace-specific** (A13.2 marketplace growth, X15.9 marketplace GTM) — узкая marketplace specifika. → Archetype-conditional на `IND-MARKET`.
3. **SaaS-specific** (A13.1 SaaS growth decomposition) — узкая SaaS metric. → Archetype-conditional на `IND-B2B-SW`.
4. **PLG playbook** (X15.8) — узкое для PLG companies. → Archetype-conditional на `GM-PLG`.
5. **27 промптов Phase 3 Communication** — overkill для $500/48hr DD. Investors готовы платить за основной отчёт + executive summary + one-pager. Board pack + investor narrative — optional add-on.
6. **Daily standup + daily metrics pulse** (C5.0, C5.3) — это ongoing engagement model. У нас сейчас one-off model. Включать только когда переходим на subscription pricing.

---

## Часть 7. DD-специфические улучшения (НЕ из master pipeline)

Master pipeline — это Strategy production, не DD. Поэтому есть DD-критичные вещи которые **ни в одном из источников нет** и которые надо добавить:

1. **`dd-management-quality-assessor`** — DD должен оценить менеджмент команды (track record, integrity, capability to execute thesis). Сейчас implicit. Чек: years in role, prior exits, governance red flags.

2. **`dd-financial-quality-of-earnings`** — explicit QoE — какая часть earnings recurring vs one-time. Особенно для PE deals критично. Master pipeline имеет S9 но cursory; нужен deeper.

3. **`dd-debt-capacity-modeler`** — для leveraged deals — какой leverage capacity при текущих cash flows + base/bear case. Сейчас implicit.

4. **`dd-deal-structuring-optimizer`** — earn-out structure, escrow size, R&W insurance, MAC clauses — auto-generate optimal deal structure based on risk matrix.

5. **`dd-comparable-transactions`** — explicit comp transaction analysis (recent M&A в industry с multiples).

6. **`dd-thesis-attribution-tracker`** (post-close) — после deal closed, отслеживает какая часть IRR пришла от каждого assumption deal thesis. Closes feedback loop "была ли наша DD reasoning right?"

---

## Резюме

**Ключевые insights:**

1. Текущий pipeline Due-Diligence-Vik сильно **более крупнозернистый** чем master (1 наш агент ≈ 5 master prompts). Это даёт скорость, но **жертвует depth**.
2. Самый большой gap — **Phase 2.5 Activation** (нас 1, у master 24). Это значит у нас нет operating model, pricing, capability gaps, corp dev, carve-out — критичные DD deliverables.
3. Второй большой gap — **Phase 3 Communication** (нас 1, у master 27). Нет board pack, investor narrative, weekly/monthly/quarterly plans.
4. BCG Framework 2001 показывает что нам **не хватает явной cost-vs-UV classification, sources/drivers/capabilities decomposition, и Strategy Pattern 2×2**. Это foundational и должно быть в каждом segment analysis.
5. Pipeline-master показывает что нам **не хватает onboarding, quick wins, value realization tracker, refresh trigger** — это то что трансформирует one-off deliverable в ongoing client relationship.

**Главные DD-specific upgrades:**
- Legal blocker audit + stakeholder alignment + QoE + debt capacity + deal structuring + thesis attribution tracker = full institutional DD coverage.

**Priority sequence:**
- **Q1 (≤2 недели):** 6 quick wins из Уровня 1 + 2 из Уровня 2.5/2.6 = methodological discipline catch-up.
- **Q2 (5-6 недель):** depth boost — per-segment split, Phase 0.5 quick wins, 5 activation modules, Phase 3 split.
- **Q3 (5-6 недель):** adaptive — archetype tuning, gates, banned strings, value realization, refresh trigger.

После Q3 — наш pipeline будет **superset** master pipeline (Strategy + DD + ongoing) с methodological purity BCG Framework 2001.
