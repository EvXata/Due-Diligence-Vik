---
name: send-outreach
description: >
  Generates personalized outreach messages for Tier 1 contacts and sends them via email.
  Runs bcg-message-writer to create drafts, shows them for approval, then sends via Resend.
  Use when: /send-outreach, "разослать сообщения", "outreach рассылка", "написать контактам",
  "send emails to contacts", "подготовить рассылку", "отправить письма".
argument-hint: <engagement_dir> [--channel email|linkedin|both] [--tier 1|2|all] [--dry-run]
disable-model-invocation: true
---

# Send Outreach — Personalized Message Generation & Sending

**Аргументы:** $ARGUMENTS

---

## Step 1 — Разбор аргументов

Разбери `$ARGUMENTS`:
- `ENGAGEMENT` — название компании или папки в research/
- `--channel email|linkedin|both` — канал (по умолчанию: email)
- `--tier 1|2|all` — какой tier контактов (по умолчанию: 1)
- `--goal gtm-outreach|sell-report` — цель рассылки (по умолчанию: gtm-outreach)
- `--dry-run` — сгенерировать без отправки

---

## Step 2 — Resolve engagement directory

```bash
BASE="/Users/maximpuda/Projects/bcg-team/research"

if [ -d "$BASE/$ENGAGEMENT" ]; then
  echo "DIR:$BASE/$ENGAGEMENT"
elif [ -d "$ENGAGEMENT" ]; then
  echo "DIR:$ENGAGEMENT"
else
  MATCH=$(ls "$BASE" | grep -i "$ENGAGEMENT" | head -1)
  if [ -n "$MATCH" ]; then
    echo "DIR:$BASE/$MATCH"
  else
    echo "NOT_FOUND"
    ls "$BASE"
  fi
fi
```

Если NOT_FOUND — показать список, попросить уточнить. Стоп.

Проверь что в директории есть `contact-universe.md`:
```bash
ls "$ENGAGEMENT_DIR" | grep -E "contact-universe|account-brief"
```

Если `contact-universe.md` не найден — сообщи:
> "contact-universe.md не найден. Сначала запусти `/bcg-team` или `/call-prep` для генерации контактов."
Стоп.

---

## Step 3 — Проверка email конфигурации

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a
echo "RESEND_KEY:${RESEND_API_KEY:+SET}"
echo "FROM_EMAIL:${FROM_EMAIL:-NOT_SET}"
echo "FROM_NAME:${FROM_NAME:-NOT_SET}"
echo "CALENDLY_URL:${CALENDLY_URL:-NOT_SET}"
```

Если ключ не установлен и не `--dry-run`:
```
⚠️ Resend не настроен.

Добавь в .env:
  RESEND_API_KEY=re_xxx
  FROM_EMAIL=you@company.com
  FROM_NAME=Your Name

После настройки повтори /send-outreach.
```
Стоп.

---

## Step 4 — Запустить bcg-message-writer

Сообщи пользователю:
```
✍️ Генерирую персонализированные сообщения...
📂 Engagement: [ENGAGEMENT_DIR]
📧 Канал: [channel] | Tier: [tier]
```

Запусти агент **bcg-message-writer** со следующими параметрами:

```
Компания: [название из директории]
OUTPUT_DIR: [ENGAGEMENT_DIR]
Канал: [channel из аргументов]
Tier: [tier из аргументов]
GOAL: [goal из аргументов, по умолчанию: gtm-outreach]
CALENDLY_URL: [CALENDLY_URL из .env]
Output files:
  - [ENGAGEMENT_DIR]/outreach-drafts.md
  - [ENGAGEMENT_DIR]/outreach-drafts.json
```

---

## Step 5 — Показать драфты для review

После завершения агента прочитай `outreach-drafts.md` и выведи сводку:

```
✅ Сообщения готовы!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ДРАФТЫ ДЛЯ ОТПРАВКИ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Таблица: # | Компания | Контакт | DMU | Email | Subject]

Полные тексты: [ENGAGEMENT_DIR]/outreach-drafts.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Покажи первые 2 письма полностью для проверки качества.

---

## Step 6 — Запрос подтверждения

Если НЕ `--dry-run`:

Спроси пользователя:
```
Отправить сообщения?

  [all]     — отправить все [N] контактам
  [1,3,5]   — отправить только выбранным (укажи номера)
  [no]      — не отправлять, сохранить только драфты
  [preview] — показать все письма полностью
```

Если `preview` — прочитай и выведи `outreach-drafts.md` полностью.

Если `no` — завершить:
```
✅ Драфты сохранены: [ENGAGEMENT_DIR]/outreach-drafts.md
Для отправки позже запусти:
python3 .claude/skills/send-outreach/send_outreach.py --data [path] --approve all
```

---

## Step 7 — Отправка

Если пользователь подтвердил (all или номера):

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/send-outreach/send_outreach.py \
  --data "$ENGAGEMENT_DIR/outreach-drafts.json" \
  --approve "$APPROVE_ARG" \
  --from-email "$FROM_EMAIL" \
  --from-name "$FROM_NAME"
```

Показать пользователю весь stdout скрипта.

---

## Step 8 — Результат

После отправки:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Рассылка завершена!

📤 Отправлено: [N] из [total]
📋 Лог: [ENGAGEMENT_DIR]/outreach-log.json
📄 Статусы: [ENGAGEMENT_DIR]/outreach-drafts.json

Follow-up через 3 дня:
  /send-outreach [engagement] --follow-up 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 9 — Экспорт в Notion (опционально)

Спроси:
> "Добавить лог рассылки в Notion? (да/нет)"

Если да — запусти `/notion-export [engagement_dir_name]`
