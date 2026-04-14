---
name: call-prep
description: >
  Prepares a complete pre-call intelligence brief for a prospect company.
  Researches the company from public sources, builds a Value Pyramid mapping
  their objectives to our solution, identifies key decision-makers (DMU),
  and generates a Contact Brief with Current Situation, Critical Info, Talk Track.
  Use when: /call-prep, "подготовиться к звонку", "пре-колл бриф", "prepare for call", "research prospect".
argument-hint: <company_name> [our_product_description]  # e.g. "Acme Corp" or "Acme Corp — AI sales platform"
disable-model-invocation: true
---

# Call Prep — Pre-call Intelligence Brief

**Аргументы:** $ARGUMENTS

---

## Step 1 — Разбор аргументов

Разбери `$ARGUMENTS`:
- Первая часть (до `—` или до конца если `—` нет) = **COMPANY** (название prospect-компании)
- Вторая часть после `—` = **OUR_PRODUCT** (описание нашего продукта/сервиса)

Если OUR_PRODUCT не указан — используй дефолт:
> "MBB-team: AI-powered strategic consulting and GTM intelligence platform"

Примеры парсинга:
- `"Acme Corp"` → COMPANY="Acme Corp", OUR_PRODUCT=default
- `"Acme Corp — AI-native CRM replacement"` → COMPANY="Acme Corp", OUR_PRODUCT="AI-native CRM replacement"
- `"Lazy Dynamics — outbound GTM automation"` → COMPANY="Lazy Dynamics", OUR_PRODUCT="outbound GTM automation"

---

## Step 2 — Создать директорию

```bash
DATE=$(date +%d.%m.%Y)
COMPANY_SLUG=$(echo "$COMPANY" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
OUTPUT_DIR="/Users/maximpuda/Projects/bcg-team/research/${COMPANY_SLUG}-callprep-${DATE}"
mkdir -p "$OUTPUT_DIR"
echo "OUTPUT_DIR:$OUTPUT_DIR"
```

Сохрани OUTPUT_DIR из вывода.

Сообщи пользователю:
```
🔍 Запускаю pre-call исследование: [COMPANY]
📁 Директория: research/[slug]-callprep-[date]/
```

---

## Step 3 — Запустить bcg-account-intel агент

Запусти агент **bcg-account-intel** со следующими параметрами:

```
Компания (prospect): [COMPANY]
Наш продукт/сервис: [OUR_PRODUCT]
OUTPUT_DIR: [OUTPUT_DIR из Step 2]
Output file: [OUTPUT_DIR]/account-brief.md
```

Агент выполнит полное исследование компании и сгенерирует:
- `account-brief.md` — Contact Brief + Value Pyramid + Key Players + Talk Track

---

## Step 4 — Показать результат

После завершения агента:

1. Прочитай `[OUTPUT_DIR]/account-brief.md`
2. Выведи пользователю в следующем формате:

```
✅ Pre-call brief готов: [COMPANY]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CONTACT SNAPSHOT
[Contact Snapshot из account-brief.md]

📊 ICP MATCH: [X%]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔺 VALUE HYPOTHESIS
[Value Hypothesis из account-brief.md]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ COMPELLING EVENTS
[Why Now из account-brief.md]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 KEY PLAYERS
[Key Players таблица]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ NEXT ACTIONS
[Next Actions checklist]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Полный бриф: research/[slug]-callprep-[date]/account-brief.md
```

---

## Step 5 — Опциональный экспорт в Notion

Спроси пользователя:
> "Экспортировать бриф в Notion? (да/нет)"

Если **да** — запусти `/notion-export [slug]-callprep-[date]`

Если **нет** — завершить.
