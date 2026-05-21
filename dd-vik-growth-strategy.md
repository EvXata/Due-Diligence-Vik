# DD-Vik — Organic Growth Strategy → 50K Users + Product Rework

**Date:** 2026-05-19
**Goal:** 50,000 целевых пользователей органическим путём (без paid acquisition)
**Inputs:**
- ICPs из [`icp-detailed-profiles.md`](../OLD-BCG-team/research/cursor-18.05.2026/icp-detailed-profiles.md) (6 ICP × 3 timeframes)
- Current product: [`README.md`](README.md), [`CLAUDE.md`](CLAUDE.md), [`DD-Vik-template/`](DD-Vik-template/)

---

## 1. Product Audit — Current State (May 2026)

| Аспект | Что есть | Что отсутствует для 50K users |
|---|---|---|
| **Distribution** | CLI tool (`/dd <company>`); Notion export | Нет self-serve web UI; нет publicly-indexed страниц |
| **Pricing** | $500 / 48h flat | Нет free tier; нет recurring subscription |
| **Output** | 3-layer (10s/5min/45min) markdown + Notion | Output = files; нет shareable links с tracking |
| **User model** | 1 user → 1 deal → 1 report | Нет team / multi-user / org-level |
| **Acquisition loop** | Manual outreach / cold email | 0 referral / 0 viral / 0 SEO / 0 invite-mechanic |
| **Retention** | Per-deal transaction | 0 recurring use; report = consumable, не tool |
| **WOW моменты** | "$500 vs $250K MBB" + PASS verdict | Скрыт за 48h ожиданием; нет instant gratification на landing |

### Главная архитектурная проблема для роста

> Продукт сегодня = **transaction** (купил → получил → ушёл). Для 50K users нужен **engine** (вошёл → залип → пригласил → вернулся).

---

## 2. ICP Cross-Reference — Что Product Не Закрывает

Из 6 ICP в [`icp-detailed-profiles.md`](../OLD-BCG-team/research/cursor-18.05.2026/icp-detailed-profiles.md):

| ICP | Текущее покрытие DD-Vik | Что упущено |
|---|---|---|
| **1 Capital Allocators** (Series E / LP / hedge) | ✅ Core product подходит; $500 — anchor entry | ❌ Нет continuous coverage; нет watchlist; нет IC-share; нет team-workspace |
| **2 Strategic Rivals** | ⚠️ Можно использовать но privacy = риск | ❌ Нет private/anonymous purchase; нет multi-rival compare mode |
| **3 F500 Buyers** | ⚠️ Generic, не CISO-ready | ❌ Нет ELA cover memo; нет risk-register paste; нет team license |
| **4 Advisors** | ⚠️ Slide-export через PDF; нет re-license rights | ❌ Нет white-label; нет attribution rights; нет mandate-pitch tiers |
| **5 Media / Analysts** | ❌ Не покрыт | ❌ Нет free citation-grade exec summary; нет public archive |
| **6 Talent / Employees** | ❌ Не покрыт | ❌ Нет $200 candidate-brief tier; нет equity-wallet; нет B2C consumer funnel |

**Вывод:** Продукт сейчас обслуживает 1 из 6 ICP (Capital Allocators core), частично 2-3 ещё. Для 50K — нужно открывать ICP-5 и ICP-6 (volume players) и виральные механики через ICP-4 (advisors multipliers).

---

## 3. Три Варианта Роста до 50K Органически

### Каждый вариант комбинирует все 5 механик
*Quality WOW · Referral · Contact-book unlock · Internal forwarding · TeamSync*

---

### Variant A — "DD Search Engine" (SEO + Instant WOW)

**Ядро:** Превратить DD-Vik в **публичный поиск по компаниям** с моментальным результатом.

| Механика | Реализация |
|---|---|
| **Quality WOW** | На landing — поле "Введите тикер / название компании" → 30-сек генерация **dd-short.md** (10-line verdict) **БЕЗ регистрации**. Первое касание = WOW. |
| **Referral** | Под результатом: "Хотите видеть `dd-mid.md` (5-min)?" → требует email + 1 invite |
| **Contact-book unlock** | Для `dd-decision-first.md` (full IC report) → "Загрузите 3 контакта в формате CSV / LinkedIn export — мы пригласим их посмотреть свой первый DD" |
| **Internal forwarding** | Каждый DD имеет shareable public URL + OG image для LinkedIn/X с verdict-headline и watermark "powered by DD-Vik" |
| **TeamSync** | Если 2+ users с одинаковым корпоративным email domain — auto-join shared workspace; видят deals друг друга |

**ICP coverage:** ICP-1 (через WOW), ICP-5 Media (free citation), ICP-6 Talent (free DD на own company / portfolio)

**Уникальный механизм:** **Public archive = compounding SEO**
- Каждый paid full-DD имеет опцию "опубликовать через 90 дней после deal close"
- Long-tail Google traffic: `"NVIDIA due diligence 2026"`, `"Cursor investment thesis"`, `"is Snowflake worth $40B"`
- Каждая страница = lead-magnet для нового user

**Math до 50K:**
| Источник | 12-мес. target | Коэффициент |
|---|---|---|
| Organic search (long-tail) | 20K | 50–100 reports × 200–500 impressions/mo × 6 mo |
| LinkedIn / X виральность OG-shares | 15K | 500 paid DDs × 30 social shares × 1% CTR |
| Invite-to-unlock | 10K | 20K registrations × 1 invite avg × 50% accept |
| Direct (PR / Stratechery citations) | 5K | 5–10 citations × 500 visits each |
| **Total** | **50K** | — |

**Best for:** Если хотим broad-reach awareness + позиционирование "DD = consumer category"

**Слабые места:**
- Зависимость от SEO compounding (12+ мес. до пика)
- Public publishing = риск для paying customers (NDA conflict)
- Low engagement per user (one-and-done)

---

### Variant B — "DD Wallet / Portfolio Dashboard" (Recurring Engagement)

**Ядро:** DD-Vik = **личный портфельный кокпит**, где tickers = живые тикеты с автообновлением.

| Механика | Реализация |
|---|---|
| **Quality WOW** | После регистрации: "Загрузите ваш portfolio (CSV / Robinhood export / Carta link)" → **5 секунд** → instant heatmap "Ваш portfolio: 14/100 stress-tested. 3 holdings в Critical risk" |
| **Referral** | "Пригласите коллегу из своего фонда — оба получите 1 free deep DD/мес." Текущий user тратит credit вместе с invitee — win-win |
| **Contact-book unlock** | "Подключите LinkedIn / Google Contacts — мы найдём ваших знакомых, кто работает в портфельных компаниях, и предложим им own portfolio scan" → каждый match = 1 unlocked DD для пригласившего |
| **Internal forwarding** | На каждом deep DD — кнопка "Send to my IC" + "Send to my CFO" с branded read-tracking |
| **TeamSync** | Family-office / fund-team mode: shared portfolio dashboard, role-based access (Partner / Analyst / IC); auto-join по email domain |

**ICP coverage:** ICP-1 Capital Allocators (core), ICP-6 Talent (employee equity wallet), ICP-3 F500 (treasury/M&A teams)

**Уникальный механизм:** **Quarterly auto-refresh on material events**
- Watchlist tickers получают auto-refreshed DD при triggers: earnings miss, M&A announcement, exec departure, regulatory event
- User получает email "DD на NVIDIA обновлён — verdict изменился с CONDITIONAL на PASS — 5 событий с last update"
- Built-in re-engagement loop

**Math до 50K:**
| Источник | 12-мес. target | Коэффициент |
|---|---|---|
| Direct registrations (LinkedIn / X / podcast halo) | 10K | Founder-led content marketing |
| Invite-a-colleague (k = 0.8) | 15K | 10K × 1.5 invites × 100% accept |
| Contact-book matches (LinkedIn export) | 12K | 10K × 50% sync × 30 contacts × 8% match |
| Family-office / fund TeamSync (3-5 per fund) | 8K | 1.5K seed funds × 5 team members avg |
| Wallet-watch SEO ("track NVIDIA in your portfolio") | 5K | Long-tail wallet/portfolio search |
| **Total** | **50K** | — |

**Best for:** Если хотим high-LTV recurring revenue + deep engagement (avg session 15+ мин.)

**Слабые места:**
- Дольше до monetization (recurring builds slowly)
- Требует integration работы (Carta / Robinhood / Notion / Google)
- Private-company tickets harder (нет market data feed)

---

### Variant C — "DealRoom Co-DD" (Team-Collab + Multiplayer)

**Ядро:** DD-Vik = **Notion для due diligence**, где deals collaboratively analyzed командой.

| Механика | Реализация |
|---|---|
| **Quality WOW** | Pre-onboarding: "Запустите DD на companу — мы спросим 3 ваших коллег оценить top-5 рисков по 5-point scale → AI синтезирует team consensus vs disagreement зон" → **collaborative WOW** на первом deal |
| **Referral** | "Free DD за каждые 3 коллег, которых добавили в workspace" + "Add your IC chair → unlock IC-grade template" |
| **Contact-book unlock** | "Загрузите ваш cap-table / IC roster CSV → invite all → auto-assign roles (Partner / Analyst / Risk Officer)" — 1 upload = 5-15 new users |
| **Internal forwarding** | Каждый DD = deal-room link с email-tracking: "Иван открыл, Маша оставила comment, Сергей оценил Risk-3 как Critical" → forwards = visible leads |
| **TeamSync** | Workspace = first-class concept; email-domain auto-join; role hierarchy (Owner / Partner / Analyst / Observer); deal-archive shared |

**ICP coverage:** ICP-1 (fund team), ICP-3 (F500 procurement+CISO+CFO consensus), ICP-4 (advisor team + client invite)

**Уникальный механизм:** **Invite-to-vote turns recipients into users**
- "Иван прислал тебе DD на Cursor — оцени 5 рисков и добавь comment (30 сек)"
- Recipient = autosignup user, can launch own DD by next click
- В отличие от read-only PDF — viewer = becomes user

**Math до 50K:**
| Источник | 12-мес. target | Коэффициент |
|---|---|---|
| Workspace-of-5 from PE/VC funds | 15K | 1.5K paid teams (firms) × 10 seats avg (incl. invitees) |
| F500 procurement + CISO + CFO trios | 10K | 1K F500 deals × 10 stakeholder invites |
| Advisor-client white-label (ICP-4) | 12K | 200 advisor firms × 60 client touchpoints |
| Deal-link forwards (organic) | 8K | 5K active DDs × 5 forwards × 30% signup |
| Direct (PR + founder + ICP-5 citations) | 5K | — |
| **Total** | **50K** | — |

**Best for:** Если хотим highest viral coefficient (k = 2-4) + highest revenue capture (team-tier $7.5K)

**Слабые места:**
- Narrower TAM (только люди в team-context)
- Sales motion долже (требует team-onboarding)
- Workspace product complexity (permissions / roles / audit logs)

---

### Сравнительная Матрица — Three Variants

| Параметр | A — Search Engine | B — Wallet | C — DealRoom |
|---|---|---|---|
| **Primary ICP** | 5 Media, 6 Talent | 1 Capital, 6 Talent | 1 Capital, 3 F500, 4 Advisors |
| **Viral coefficient k** | 1.3–1.8 | 1.5–2.5 | **2.0–4.0** |
| **Time-to-50K** | 12 мес. | 14–18 мес. | 9–12 мес. |
| **LTV per user** | $5–50 | $200–2K | **$500–7.5K** |
| **Engagement (avg session)** | 1–3 мин. | 10–15 мин. | **15–30 мин.** |
| **Conversion to paid** | 0.5–2% | 5–10% | **10–20%** |
| **Implementation effort** | Medium | High | High |
| **NDA / privacy риск** | High (public archive) | Low (private wallets) | Low (private rooms) |
| **Revenue @ 50K users** | $500K–$1M ARR | $2–5M ARR | **$5–15M ARR** |

### Рекомендация — Sequenced Hybrid

> **Запускать C → A → B в последовательности.** C даёт highest k + revenue early; A после года compounding SEO; B как retention layer для paying customers.

---

## 4. 10 Самых Ценных Изменений Продукта

Приоритезация по формуле: **(Sales conversion × Acquisition viral × ICP coverage) / Implementation effort**

### P1 — Foundation (Week 1-4)

#### #1. Live WOW Search на landing — instant DD-short без регистрации
**Что:** Поле ввода компании → 30 сек → 10-line verdict (PASS/CONDITIONAL/PROCEED + fair value gap + 3 deal-breakers)
**Почему:** Сейчас новый user не видит ценность 48 часов. С Live Search — видит за 30 сек.
**Какие ICP:** Все (ICP-1, 3, 5, 6 — anyone who lands)
**Impact:** Visitor → email conversion 5% → 25%. Acquisition top-of-funnel × 10.
**Effort:** 2 недели. Reuse `dd-production-summary` agent в streaming mode.

#### #2. Public Shareable Links с Watermark + OG Image
**Что:** Каждый DD = public URL `dd.io/cursor-19may2026` с branded OG-preview для LinkedIn / X / email
**Почему:** Replace file-only output. Forwarding = built-in. Tracking = built-in.
**Какие ICP:** ICP-4 (advisor share с client), ICP-5 (media citation), ICP-1 (IC-share)
**Impact:** Каждый paid DD = 5-30 organic impressions через social sharing.
**Effort:** 1 неделя. Static-site generation из markdown + Vercel deploy per report.

#### #3. Invite-to-Unlock — Full DD требует 3 invite OR contact-book upload
**Что:** Free user видит `dd-short`. Чтобы unlock `dd-mid` — email. Чтобы unlock `dd-decision-first` — либо $500, либо invite 3 colleagues OR upload LinkedIn export
**Почему:** Превращает каждого user в acquisition channel
**Какие ICP:** ICP-1 (FOMO on IC), ICP-3 (board memo), ICP-6 (tender decision)
**Impact:** k coefficient: 1.0 → 1.6 (60% активируют unlock-mechanic)
**Effort:** 1 неделя. CSV parser + invite email queue.

### P1 — Team & Forwarding (Week 4-8)

#### #4. Team Workspace Auto-Join по Email Domain
**Что:** Когда @goldmansachs.com user logs in — automatic detect, прикрепить к существующему GS workspace, видит team's recent DDs
**Почему:** Reduce friction from "Should I share this with Иван?" to "Иван уже в workspace, shared by default"
**Какие ICP:** ICP-1 (fund teams), ICP-3 (F500 CISO+CFO+procurement), ICP-4 (firm-wide license)
**Impact:** Avg seats per workspace 1 → 6. TeamSync mechanic = built-in.
**Effort:** 2 недели. Domain detection + role-default assignment.

#### #5. IC-Share Button с Read Tracking
**Что:** В каждом `dd-decision-first.md` — кнопка "Send to my IC" → opens dialog with email list, branded preview, tracking ("Иван открыл 12 мая в 14:32")
**Почему:** Internal forwarding mechanic. Каждый share = potential new user + retention signal.
**Какие ICP:** ICP-1 (IC submission), ICP-3 (board memo), ICP-4 (client share)
**Impact:** Avg 3-5 internal forwards per DD; 30% recipient signup rate.
**Effort:** 1 неделя. Email + read-receipt + lightweight CRM.

#### #6. Reverse Stress-Test Mode ("Что убъёт этот deal?")
**Что:** На странице DD — interactive query: "What if capex slows 30%?", "What if Anthropic raises API 25%?", "What if SpaceX option not exercised?" → live updated value bridge
**Почему:** Превращает static report в interactive tool — drives engagement + return visits
**Какие ICP:** ICP-1 (IC questions live), ICP-3 (CISO scenarios)
**Impact:** Avg session 3 мин → 15 мин. Return-visit rate +40%.
**Effort:** 3 недели. Scenario engine + cached parameter variations.

### P2 — Retention & Multipliers (Week 8-16)

#### #7. Watchlist Subscription — Auto-Refresh on Material Events
**Что:** User помечает companies → email alerts when DD verdict changes (earnings miss / M&A / exec exit / regulatory event); auto-refresh DD-short
**Почему:** Преобразует one-off transactions в recurring use (Variant B core)
**Какие ICP:** ICP-1 (quarterly mark refresh need — future state), ICP-3 (vendor monitoring), ICP-6 (employee equity tracking)
**Impact:** MAU/DAU ratio 5% → 25%. Subscription-tier monetization unlocked.
**Effort:** 4 недели. Event feed + scheduled re-runs + alert system.

#### #8. Side-by-Side Compare Mode
**Что:** "Compare Cursor DD vs Cohere DD" → 2-column view (verdicts, fair values, risk matrices side by side)
**Почему:** Drives time-on-site + shareability ("Cursor floor $32B vs Cohere $14B — which is mispriced?")
**Какие ICP:** ICP-1 (sector positioning), ICP-2 (competitive intel), ICP-5 (media angle)
**Impact:** Average DDs viewed per session 1 → 3.5; share rate +60%.
**Effort:** 2 недели. UI + data alignment layer.

#### #9. White-Label DD для Advisors (ICP-4 viral mechanic)
**Что:** Advisor uploads logo → DD rendered with advisor branding + "Powered by DD-Vik" footer; advisor shares c clients с own attribution
**Почему:** ICP-4 = highest multiplier (1 advisor = 5-20 client touchpoints). Solves "не могу использовать в client deck" barrier из ICP profile.
**Какие ICP:** ICP-4 (core unlock), spreads to ICP-1+3 через advisor's clients
**Impact:** Каждый whitelabel-active advisor = 10-30 new users (clients invited to view branded DD)
**Effort:** 2 недели. Logo + brand-color overrides + PDF render с co-branding.

#### #10. Public DD Archive (SEO Long-Tail)
**Что:** Опция "Make this DD public 90 days after deal close" — каждая публичная страница indexed by Google; topic clustering ("AI coding DDs", "Q1 2026 PE DDs")
**Почему:** Self-sustaining organic acquisition. SEO compounds non-linearly с volume.
**Какие ICP:** ICP-5 (citations), ICP-6 (newcomers exploring), ICP-1 (sector benchmarking)
**Impact:** Year-1: 5-10K organic monthly visitors. Year-2: 50K+ (compound).
**Effort:** 3 недели. CMS layer + sitemap + structured data + indexing strategy.

---

## 5. Sequenced 90-Day Implementation Plan

| Phase | Weeks | Changes | Outcomes |
|---|---|---|---|
| **Phase 0 — Front Door** | 1–4 | #1 Live WOW Search · #2 Public Links · #3 Invite-Unlock | Visitor → user conversion 25%; viral k = 1.4 |
| **Phase 1 — Team Layer** | 5–8 | #4 Team Workspace · #5 IC-Share · #6 Reverse Stress-Test | Engagement 15+ мин; team-share rate 60% |
| **Phase 2 — Retention + Multipliers** | 9–12 | #7 Watchlist · #8 Compare · #9 White-Label · #10 SEO Archive | MAU/DAU 25%; ICP-4 viral channel active; SEO compounding starts |

### KPI Targets by Phase End

| Метрика | After Phase 0 | After Phase 1 | After Phase 2 |
|---|---|---|---|
| Signups (cumulative) | 2K | 8K | 25K |
| Trajectory to 50K | T+12 mo | T+10 mo | **T+9 mo** |
| Viral coefficient | 1.4 | 1.8 | 2.3 |
| MAU/DAU | 8% | 15% | 25% |
| Paid conversion | 1% | 3% | 6% |
| ARR run-rate | $50K | $400K | $2M+ |

---

## 6. Cross-Reference — Changes × ICPs

| ICP | Top Change | Mechanic Unlocked |
|---|---|---|
| **1 Capital Allocators** | #6 Reverse Stress-Test, #7 Watchlist | Continuous coverage (matches future-state need) |
| **2 Strategic Rivals** | #8 Compare Mode | Multi-rival positioning (privacy still concern) |
| **3 F500 Buyers** | #4 Team Workspace, #5 IC-Share | CISO+CFO+procurement trio; cover memo workflow |
| **4 Advisors** | #9 White-Label | Mandate-win material + attribution rights solved |
| **5 Media / Analysts** | #2 Public Links, #10 SEO Archive | Citation-grade exec summary + OG-shareable |
| **6 Talent / Employees** | #1 Live WOW, #3 Invite-Unlock | $200 self-serve B2C funnel + viral entry |

---

## 7. Open Questions для Решения

1. **NDA conflict on public archive** — paying ICP-1 clients могут возразить против публикации даже через 90 дней. Тест на 5 первых customers до запуска #10.
2. **Pricing tier для team workspace** — $500 still per-deal? Или переход на $99/seat/mo recurring? Recommend: дуальная модель — pay-per-deal entry + subscription для team-tier.
3. **Authorship / byline policy** — Public DDs as anonymous "DD-Vik team" or Evgeny-named? Named principal +30% conversion на ICP-1/4 hypothesis (per ICP profiles), но conflict-risk при ICP-2 sales.
4. **B2C tier ICP-6 risk** — может cannibalize ICP-1 pricing? Recommend: разные products (Wallet ≠ DD Concierge); $19/mo wallet ≠ $500 deep DD.
5. **Founder bandwidth** — 10 changes за 12 недель требует engineering team. Если solo — приоритезация P1 #1/#2/#3 first, P2 опционально.

---

## 8. Связанные Файлы

- [`icp-detailed-profiles.md`](../OLD-BCG-team/research/cursor-18.05.2026/icp-detailed-profiles.md) — input source (6 ICP × 3 timeframes)
- [`README.md`](README.md) — current product surface
- [`CLAUDE.md`](CLAUDE.md) — current architecture
- [`DD-Vik-template/`](DD-Vik-template/) — output format reference
