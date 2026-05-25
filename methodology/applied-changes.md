# MBB Team — Applied Prompt Changes Log
*Изменения, внесённые непосредственно в файлы агентов по результатам cross-engagement анализа*

---

## 2026-03-28 — Applied: Innovate Archetype Blocking Gate

**Agent:** bcg-segment-analyst.md
**Change:** Добавлен блок "ОБЯЗАТЕЛЬНЫЙ КОНТРОЛЬ КАЧЕСТВА СТРАТЕГИЙ" с тремя blocking gates перед шагом сохранения файла:

1. **Archetype Completeness Gate** — обязательная таблица по всем 5 архетипам (D/P/S/F/I) с количеством стратегий; минимальные счётчики по MBB-позиции (Star/QM: 10-15 стратегий; Cash Cow: 8-12; Dog: 6-10); при несоответствии — добавить стратегии перед сохранением

2. **Innovate Archetype Gate** — точное определение (создаёт новую категорию/бизнес-модель, которой ранее не существовало); позитивные примеры (Arm architecture licensing, Spotify podcast exclusivity, MCP protocol ownership, Stripe Connect marketplace revenue share); негативные примеры (снижение цены — НЕ Innovate; улучшение features — НЕ Innovate; M&A в существующей категории — НЕ Innovate); обязательный INNOVATE GAP statement если 2 квалифицирующих стратегии найти невозможно (объяснение причин, а не просто пропуск)

3. **Financial Parameters Validation Gate** — проверка источников (❌-маркированные данные не могут появляться в финансовых параметрах как конкретные значения); revenue ceiling check (если implied market share >30% — пересчитать); fleet math check (для стратегий с unit economics: Revenue Check = units × revenue/unit × periods; расхождение >30% требует объяснения)

**Rationale:** 15/15 engagements с отсутствующим Innovate архетипом несмотря на 14 предложений изменить промпт; Baidu engagement подтвердил возможность полного coverage когда мотивация высока; blocking gate с Gap Statement как safety valve устраняет проблему без принудительного генерирования слабых стратегий
**Expected improvement:** Innovate присутствует в >80% сегментов начиная со следующего engagement'а; ❌-данные в финансовых параметрах сокращаются до нуля

---

## 2026-03-28 — Applied: Section Header Standard with Blocking Self-Check

**Agent:** bcg-production.md
**Change:** Заменена одиночная инструкция заголовков на детальный стандарт "СТАНДАРТ ЗАГОЛОВКОВ РАЗДЕЛОВ — СТРОГО ОБЯЗАТЕЛЕН":

- **Тест для каждого заголовка:** "Этот заголовок отвечает на вопрос 'Что это значит для решения?' или только объявляет тему раздела? Если только объявляет — перепиши."
- **Запрещённые (topic-style) заголовки** с конкретными примерами: "Анализ сегментов", "Конкурентный ландшафт", "Гипотезы", "GTM Playbook", "Анализ рисков", "Стратегические варианты", "Портфельный синтез", "Синергии", "Распределение ресурсов"
- **Требуемые (conclusion-style) заголовки** с калиброванными примерами: "Два сегмента несут всю компанию — без инвестиций в оба она теряет лидерство за 18 месяцев", "Все 10 гипотез подтверждают: ставка на Enterprise Platform должна быть сделана в 2026 году"
- **Обязательный шаблон для сегментных заголовков:** "[Сегмент]: [единственный самый важный стратегический вывод для компании в этом сегменте]" с примерами
- **Примеры конвертации sub-header:** "Ключевое преимущество" → "Closed-loop атрибуция структурно недостижима ни для одного конкурента"
- **Блокирующая самопроверка:** прочитай только заголовки (без текста разделов) — если читатель понимает общую рекомендацию, главный вывод по каждому сегменту и ключевой риск — стандарт соблюдён; если чтение заголовков малоинформативно — перепиши перед сохранением

**Rationale:** 13/15 engagements с topic-style заголовками несмотря на 12 предложений изменить промпт; сильные примеры в Amazon ("The AI Infrastructure Window Is Open Now, Not Forever") и Intel ("Kodak trap") доказывают, что агент способен писать conclusion-style headers — проблема в непоследовательном применении под давлением длины; blocking self-check устраняет проблему
**Expected improvement:** Соответствие conclusion-style headers во всех секциях финального отчёта начиная со следующего engagement'а

---

## 2026-03-28 — Applied: TAM Source Hierarchy + WAU/MAU Discipline + Corporate Event Protocol

**Agent:** bcg-market-mapper.md
**Change:** Добавлены три обязательных дисциплинарных секции:

1. **TAM Scope Gate:** TAM должен соответствовать определению сегмента, а не более широкой рыночной категории; если TAM более чем в 3 раза превышает суммарную раскрытую выручку топ-5 игроков — скорее всего, используется более широкое определение; обязательное явное указание определения TAM

2. **Иерархия источников Tier 1/2/3:** Tier 1 (Goldman Sachs, Morgan Stanley, IDC, Gartner, Canalys, SEMI) — предпочтительный; Tier 2 (Forrester, Counterpoint, Grand View Research, Mordor Intelligence) — приемлемый при кросс-проверке; Tier 3 (MarkSpark, Verified Market Research, Business Research Insights и аналогичные агрегаторы) — только как контекст bull case; если Tier 3 оценка более чем в 3x превышает Tier 1 — маркировать как "агрессивный bull case", Tier 1 использовать как primary

3. **Дисциплина WAU/MAU:** при цитировании метрик пользователей всегда явно указывать тип метрики с источником и датой; не усреднять и не смешивать WAU с MAU; разрыв может достигать 2-4x

4. **Корпоративный event протокол:** для любых корпоративных событий, произошедших менее 6 месяцев назад или неверифицированных из двух независимых первичных источников — помечать [НЕ ВЕРИФИЦИРОВАНО — требуется поиск]; M&A завершение — только после проверки SEC filings или пресс-релизов компании

5. **Актуальность выручки конкурентов:** для каждого конкурента в конкурентных таблицах искать фактические квартальные результаты Q4/FY2025 до использования аналитических прогнозов

**Rationale:** WAU/MAU conflation в 4/15 engagements (всегда в market-mapper); unverified M&A claims в 7/15 engagements; TAM scope inflation в 11/15 engagements; competitor revenue currency failures в 6/15 engagements; все четыре класса ошибок originate в этом агенте
**Expected improvement:** WAU/MAU conflation устраняется; unverified M&A claims устраняются; TAM source quality улучшается; competitor revenue currency failures снижаются на 70%+

---

## 2026-04-09 — Applied: Question Mark Strategy Minimum + Structural Template

**Agent:** bcg-segment-analyst.md
**Source:** Alphabet engagement methodology review — Issue #2 (4-engagement pattern confirmed)
**Change:** Добавлен явный минимум для Question Mark сегментов (8 стратегий) с обязательным структурным шаблоном:

- Шаблон: 2×D, 2×S, 1×P, 1×F, 1×I, 1×exit strategy (IPO/JV/дивестиция)
- Явное предупреждение: "Question Mark с 2–4 стратегиями — это НЕ полный анализ"
- Объяснение пространства стратегических опций для Question Mark: платформенная лицензия, B2B white-label, govt concession, IPO/spin-out, стратегические партнёрства с OEM
- Шаблон обязателен для предотвращения low-effort coverage в нарождающихся сегментах

**Rationale:** В Alphabet engagement SPD и Waymo (оба Question Mark) произвели 4 и 2 стратегии соответственно vs. минимума 8; в Samsung engagement 5/6 сегментов ниже минимума; Question Mark исторически не имел явного минимума в промпте несмотря на формально заявленный диапазон 10–15; структурный шаблон даёт конкретные scaffolding для нарождающихся сегментов где агент дефолтно производит low-effort coverage
**Expected improvement:** Question Mark стратегии достигают минимума 8 начиная со следующего engagement'а

---

## 2026-04-09 — Applied: Innovate Substance Gate (Self-Check Before Labeling)

**Agent:** bcg-segment-analyst.md
**Source:** Alphabet engagement methodology review — Issue #1 (4-engagement confirmed pattern: Apple, Samsung, Amkor, Alphabet — все с отсутствующим или слабым Innovate)
**Change:** Усилен существующий Innovate Gate добавлением явной самопроверки перед присвоением ярлыка I:

- Чёткое определение: "бизнес-модель, продуктовая категория или источник выручки, который в настоящее время не существует для данной компании в данном сегменте"
- Два явных проверочных вопроса: "Существует ли эта бизнес-модель уже у компании?" / "Существует ли она у любого конкурента?"
- Если ответ "да" на любой — перекласифицировать и производить Gap Statement
- Добавлен блок "Допустимые паттерны Innovate": новая модель ценообразования, новый класс покупателей, новая позиция в value chain, новая регуляторная категория

**Rationale:** Существующий blocking gate оказался недостаточным — агент проходил архетипную проверку генерируя фейковые I стратегии (Defend/Scale под ярлыком I); substance gate с явными проверочными вопросами создаёт механизм self-correction прямо в точке присвоения ярлыка
**Expected improvement:** Доля genuine Innovate стратегий (или честных Gap Statement'ов) повышается; исчезают стратегии Scale/Defend переименованные в Innovate

---

## 2026-04-09 — Applied: Cross-Company Benchmark Temporal Parity Gate

**Agent:** bcg-data-scientist.md
**Source:** Alphabet engagement methodology review — Issue #3 (first confirmed occurrence; same root mechanism as Apple temporal scope gate)
**Change:** Добавлен явный блокирующий gate "TEMPORAL PARITY GATE" перед таблицей бенчмарков (Analysis 4):

1. Проверка через company-brief.md — какой финансовый год использован для таргет-компании
2. Для каждого peer — искать `[competitor] FY2025 annual results` до использования FY2024
3. Если FY2025 peer недоступен — указывать фактический год в метке колонки
4. Обязательный footnote при сравнении разных fiscal years: "⚠️ [Competitor]: FY2024 data — FY2025 not yet reported"
5. Обязательная колонка "Fiscal Year" в таблице бенчмарков

**Rationale:** В Alphabet engagement ROIC (41.1%), margin (35.6%), revenue growth (+15%) сравнивались с Microsoft/Meta/Apple FY2024 данными несмотря на наличие FY2025 данных в company-brief.md; систематически завышает относительное улучшение таргет-компании; тот же root mechanism что Apple engagement (quarterly vs. annual), теперь применён к cross-company оси
**Expected improvement:** Все peer-метрики используют тот же fiscal year что таргет-компания или явно помечены; temporal mismatch исчезает из benchmarking таблиц

---

## 2026-04-09 — Applied: Part V Incremental Content Enforcement (Strengthened)

**Agent:** bcg-production.md
**Source:** Alphabet engagement methodology review — Issue #4 (5-й consecutive engagement с этим паттерном, declining severity)
**Change:** Добавлена блокирующая самопроверка "САМОПРОВЕРКА ЧАСТИ V" перед содержимым Part V:

- Явный проверочный вопрос для каждого абзаца: "Описывает ЧТО представляет собой стратегия (её содержание) OR объясняет ПОЧЕМУ выбрана / ЧТО является критичным допущением / ЧТО первым в исполнении?"
- Инструкция: если абзац описывает содержание — удалить или перенести в Часть II
- Явный список того, что Part V содержит ИСКЛЮЧИТЕЛЬНО: (a) логика выбора с trade-offs, (b) критичное допущение + сигнал провала, (c) корреляция рисков портфеля, (d) последовательность исполнения 30/90/180 дней с владельцами и KPI
- Триггер-фраза: "Если абзац начинается 'Эта стратегия предполагает...' / 'Суть подхода...' — это дублирование Части II. Удали."

**Rationale:** Samsung Change 3 (первая версия правила) снизила severity с 800→600→400 слов дублирования, но не устранила паттерн; strengthened self-check с конкретным триггером-фразой и инструкцией "удали или перенеси" (а не просто "не дублируй") закрывает оставшийся gap
**Expected improvement:** Part V дублирование Part II снижается до нуля; Part V содержит исключительно selection logic, assumptions, risk correlation, execution sequence


---

## 2026-05-22 — T-Bank DD post-mortem — 7 Applied Changes

**Source:** T-Bank (Т-Технологии, MOEX: T) DD engagement methodology review + post-mortem
**Engagement type:** Full Strategic DD (BCG foundation + DD phases + investor profile memos)
**Wall-clock:** 1h 31min total
**Bugs caught:** 7 (1 critical, 5 medium, 1 noted)

### Change 1: dd-production.md — Pre-flight directory verification
**Trigger:** BUG #1 — false-negative on first attempt (claimed directory missing while 12+ files existed; was actually a parallel-with-master ordering issue)
**Change:** Added Step 0 (MANDATORY) requiring `Bash ls` directory check + `Read` master-anchors.json/dd-decision-first.md verification BEFORE claiming any missing-file state. Differentiates "directory missing" (engagement folder not created) from "expected file not yet produced" (parallel ordering issue).
**Tools added:** Bash (was: Read, Write only)
**Expected gain:** ~5 min wall-clock per DD engagement (eliminates retry-after-false-negative)

### Change 2: bcg-data-scientist.md — Financial-company TAM gate
**Trigger:** BUG #3 — TAM 113 трлн ₽ for T-Bank was balance aggregate, not revenue addressable (~14× overstatement)
**Change:** Added BLOCKING gate before market sizing — if industry ∈ {banking, insurance, asset-mgmt, brokerage, specialty finance}, TAM MUST be revenue-based, not asset/AUM/balance. Includes conversion formula (balance × NIM/fee rate), sanity checks (SOM > SAM = error), and forbidden-output patterns.
**Expected gain:** Prevents ~30 min false-optimism in portfolio.md for financial-company engagements; closes first-known-case in corpus

### Change 3: bcg-portfolio-analyst.md — Validation caveat propagation
**Trigger:** BUG #4 — Rosbank synergies (⚠️ in validation-report) used as top-3 strategic support without inline caveat
**Change:** Added Step 1.5 BLOCKING — explicit read of validation-report.md, extraction of all ⚠️ flags, mandatory inline caveat after any claim used in top-line recommendation. Auto-downgrade confidence rule if 3+ ⚠️ claims in final verdict. Optional Caveat Register section.
**Expected gain:** Eliminates strategic signal pollution in portfolio.md from contested data; downstream DD agents see properly tagged claims

### Change 4: bcg-fact-checker.md — Coverage enumeration gate
**Trigger:** BUG #5 — segment-retail-unsecured (40-43% revenue, largest segment) silently skipped; agent logged "(не полностью прочитан)" but no coverage failure flagged
**Change:** Added Step 0 BLOCKING — Coverage Manifest table at start of validation-report listing every segment-*.md with Read status. 100% coverage required. Large-file handling: split via offset+limit if >100 KB.
**Expected gain:** Eliminates silent coverage gaps; downstream agents get full validation signal

### Change 5: bcg-researcher.md — Metrics glossary requirement
**Trigger:** BUG #6 — multiple metric methodology conflicts (NII % as 37/40/43/55, AUM as 1.4 vs 5.3 trln, customers as 54M nominal vs 34M MAU vs 4.2M active)
**Change:** company-brief.md MUST begin with `## Глоссарий метрик` table defining all denominators (revenue/net revenue/group revenue, NII, fee income, AUM methodology, customer activity definition) BEFORE any financial data. Downstream agents must cite glossary when using ambiguous metrics.
**Expected gain:** Eliminates cross-file denominator drift; portfolio-analyst can no longer accidentally compare apples to oranges

### Change 6: bcg-methodologist.md — Improvement-log append fallback
**Trigger:** BUG #7 — improvement-log.md >25K tokens → could not Read+Write entire file → T-Bank entry saved to separate temp file
**Change:** Trinary fallback strategy — Bash wc -c check first, branch on size: (a) missing → Write, (b) <20KB → Read+Write, (c) ≥20KB → Bash heredoc append (`cat <<'EOF' >> file`). Atomic, no context-window issues.
**Tools added:** Bash (was: WebSearch, Read, Write)
**Expected gain:** improvement-log append never fails again as corpus grows; tested live on T-Bank append (67.5 KB → 76.6 KB)

### Change 7: bcg-market-mapper.md — Corporate event date freshness
**Trigger:** BUG #2 — Точка M&A shareholder vote date cited as "5 июня 2026" (actual: 18 сентября 2026, rescheduled)
**Change:** For ANY future corporate event date (vote, M&A close, IPO, regulatory filing) — MANDATORY WebSearch freshness check (≤30 days). If verified reschedule found, cite both old/new with sources. If not verified in 30 days, use quarter/month only (no specific calendar date).
**Expected gain:** Prevents stale-date contamination of downstream files (portfolio, DD, risk-matrix all received the wrong Точка date in T-Bank DD before fact-checker caught it)

### Changes NOT applied (out of scope this iteration)

- **OPT #1: DD-3c → Notion sequencing in `/dd` skill** — explicitly excluded by user ("кроме ноушен")
- **OPT #8: Notion export better error messages** — explicitly excluded
- **OPT #9: Phase 1 Tier-2 batching** — additive optimization, not bug-fix; defer to next iteration
- **OPT #10: engagement.log auto-updater agent** — new agent, broader scope; defer

### Test status
- All 7 prompt edits applied via Edit tool
- Bash tools added to dd-production + bcg-methodologist
- T-Bank entry appended to improvement-log.md via the new heredoc fallback (verified: 67.5 KB → 76.6 KB)
- temp file improvement-log-tbank-append.md cleaned up
- 8/8 post-mortem tasks closed

---

## 2026-05-25 — Applied: TAM-Ceiling Resolution Protocol (v9.1 P4)

**Agent:** bcg-segment-analyst.md
**Source:** Pipeline v9.1.0 release (cumulative on v9.0.0); 3-engagement confirmed pattern (Micron AEBU, Amkor Automotive, GFS A&D)
**Change:** Шаг B (Revenue Impact Ceiling Check) полностью переписан с soft ≤30/50% sanity check на BLOCKING resolution protocol:

- Триггер: implied_share > 50% И не-доминирующий участник ИЛИ implied_share > 80% для любого
- Три способа resolve: (a) revise to credible share с named precedent · (b) expand TAM с named Tier-1/2 source · (c) labeled target_not_independently_constrained с явным precondition assumption
- Запрещено flag-and-pass — resolution MUST произойти внутри стратегии до сохранения файла
- Обязательная output table per strategy с колонкой resolution_status (= ceiling_check required field в pipeline91.json)
- Legacy ≤30% sanity check сохранён как Шаг B.1 (one-line обоснование без блокировки)

**Rationale:** 3-engagement pattern (Micron/Amkor/GFS) с TAM-ceiling breach passed unresolved через fact-checker и portfolio в final report только с footnote caveat; existing sanity check (>30% → recheck, >50% → "impossible") был too soft — давал агенту разрешение оставить ⚠️ flag вместо реального resolve. v9.1 P4 заменяет soft check на BLOCKING gate с тремя named resolution paths.

**Companion:** spec patched в methodology/pipeline91.json под `4_STRATEGY_FINANCIAL.content` + `required_fields_per_stage.4_STRATEGY_FINANCIAL.ceiling_check`
**Expected improvement:** Zero TAM-ceiling breaches passed to portfolio.md / final-report.md без resolved status начиная со следующего engagement'а

---

## 2026-05-25 — Applied: TAM Provenance Classification (v9.1 P3 — runtime)

**Agent:** bcg-market-mapper.md
**Source:** Pipeline v9.1.0 release (P3 runtime alignment) — pre-existing Tier 1/2/3 hierarchy lacked explicit `self_derived` category
**Change:** Дополнен блок "Иерархия источников для TAM" новой v9.1 P3 секцией "TAM Provenance Classification (BLOCKING)":

- Обязательная классификация tam_provenance ∈ {tier1_sourced, tier2_sourced, self_derived} per segment
- Когда self_derived → warning `⚠️ TAM — NO INDEPENDENT SOURCE` должен быть в САМОМ ВЕРХУ TAM-блока (не в footnote, не в appendix), с указанием методики и явной propagation note
- output schema additions: `tam_provenance`, `tam_warning_at_top: bool`
- V1 validator AUTO-REJECTS если self_derived TAM без top-level warning

**Rationale:** Pre-existing Tier 1/2/3 иерархия покрывала случай "источник существует но низкого качества", но не покрывала случай "я сам собрал TAM из bottom-up или triangulation" — это самый опасный класс, потому что отсутствие источника часто маскируется красиво форматированным числом. v9.1 P3 закрывает этот gap явным provenance flag + top-of-block warning.

**Companion:** spec already patched in methodology/pipeline91.json (1S0_segmenter.tam_provenance, 1B_industry_economics.tam_warning_at_top, 6F_market_map_data warning preservation)
**Expected improvement:** Zero self-derived TAMs presented as if independently sourced; downstream revenue targets always inherit explicit uncertainty flag

---

## 2026-05-25 — T-Bank v9.1 acceptance-test bug fixes (4 bugs)

**Source:** T-Bank DD engagement 25.05.2026 (v9.1 acceptance test) post-mortem
**Engagement type:** Full Strategic DD, completed locally in 64 min (target ≤90 min)
**Bugs surfaced and fixed:** 4 (1 HIGH path-config, 1 MEDIUM Notion parser, 2 MEDIUM agent-rule gaps)

### Bug 1: Stale Due-Diligence-Vik hardcoded paths (HIGH)
**Files patched:** 5 (30 path refs total)
- `.claude/skills/dd/SKILL.md` (14 refs)
- `.claude/skills/dd-short/SKILL.md` (8 refs)
- `.claude/skills/dd-short-batch/SKILL.md` (5 refs)
- `.claude/settings.local.json` (15 refs)
- `.claude/agents/bcg-researcher.md` (1 ref)
- `methodology/improvement-log.md` (1 ref)
**Change:** Replaced both legacy variants `/Users/cofounder/Documents/Projects/Due-Diligence-Vik/` AND `/Users/maximpuda/Projects/Due-Diligence-Vik/` with current `/Users/cofounder/Documents/Projects/DD MarketStrat/`.
**Rationale:** Project was renamed; legacy paths broke phase-gate.sh invocations and Notion-export script paths in 3 skills. Caused manual workarounds during T-Bank test run.

### Bug 2: Notion engagement-title parser (MEDIUM)
**File:** `.claude/skills/notion-export/export_to_notion.py`
**Locations:** 2 (parse_engagement_metadata + main block)
**Change:** Replaced `dir_name.split("-", 1)` first-hyphen split with date-pattern regex `r"-(\d{1,2}\.\d{1,2}\.\d{4})$"` that anchors on trailing DD.MM.YYYY and pulls company from the prefix. Multi-hyphen company slugs now resolve correctly.
**Verified cases (9):** dydx, microsoft (+fast), tsmc, t-bank, jp-morgan, t-bank (+fast), alphabet, globalfoundries, general-electric — all parse correctly. Bug case `t-bank-25.05.2026` → "T-Bank — MBB Engagement (25.05.2026)" (was: "T — MBB Engagement (bank-25.05.2026)").
**Rationale:** T-Bank engagement created Notion page with corrupted title; would corrupt every future multi-hyphen company (t-mobile, jp-morgan, general-electric, etc.).

### Bug 3: bcg-researcher rescheduled-from rule (MEDIUM)
**File:** `.claude/agents/bcg-researcher.md`
**Change:** Added "Rescheduled Event Dates — MANDATORY DUAL-CITATION" section. When prompt contains hard-constraint correction of form "stated [A], VERIFIED ACTUAL = [B] (rescheduled)" — agent MUST cite BOTH dates with explicit tags, NOT consolidate to single date or vague phrasing.
**T-Bank evidence:** Despite explicit hard-constraint correction `Точка vote: stated 5.06.2026, actual = 18.09.2026 (rescheduled)`, agent used "Sep 2026" generically. Audit trail lost; downstream stress-signal (the fact of rescheduling) dropped.
**Required format documented with verbatim T-Bank example.**

### Bug 4: bcg-market-mapper Change 7 dual-date tightening (MEDIUM)
**File:** `.claude/agents/bcg-market-mapper.md`
**Change:** Extended existing "СТАТУС КОРПОРАТИВНЫХ СОБЫТИЙ" protocol with "Перенесённые даты — DUAL CITATION" subsection. Explicit prohibitions: do NOT use rescheduled-to-only, do NOT use original-only, do NOT smooth to "Q4/осень/Sep". List of event classes where this matters (M&A votes, IPO, regulatory filings, earnings releases).
**T-Bank evidence:** Market-mapper DID get this right in T-Bank run (cited both 5.06.2026 + 18.09.2026) — the rule existed implicitly. Tightening makes it explicit so future agents don't regress when the implicit signal is absent.

### Test status
All 4 fixes applied. No regressions detected (re-ran parser unit tests with 9 cases). Spec-side v9.1 patches unchanged (sha256 204dfd45… preserved). Next engagement will exercise Bug 3 fix in the wild — verification deferred to that run.
