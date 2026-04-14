---
name: crm-sync
description: >
  Syncs CRM data for a client engagement via Merge.dev (supports HubSpot, Salesforce, Pipedrive, 50+ CRMs).
  Pull: fetches accounts, contacts, opportunities into the research directory.
  Push: writes MEDDPICC/Next Actions from crm-update.json back to CRM.
  Use when: /crm-sync, "синхронизировать CRM", "подключить CRM", "загрузить данные из CRM",
  "записать в CRM", "pull CRM", "push to CRM", "connect client CRM".
argument-hint: <company_or_engagement_dir> [--direction pull|push]
disable-model-invocation: true
---

# CRM Sync via Merge.dev — Pull & Push

**Аргументы:** $ARGUMENTS

---

## Step 1 — Разбор аргументов

Разбери `$ARGUMENTS`:
- `ENGAGEMENT` — название компании или папки в research/
- `--direction pull|push` — направление (по умолчанию: pull)

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

---

## Step 3 — Проверка конфигурации

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a
echo "MERGE_API_KEY:${MERGE_API_KEY:+SET}"
```

Если `MERGE_API_KEY` не установлен:
```
⚠️ Merge.dev не настроен.

1. Зарегистрируйся на https://merge.dev (есть free tier)
2. Добавь в .env:
   MERGE_API_KEY=your_api_key

После настройки повтори /crm-sync.
```
Стоп.

Проверь, есть ли уже account_token для этого клиента:
```bash
cat "$ENGAGEMENT_DIR/crm-config.json" 2>/dev/null || echo "NO_CONFIG"
```

Если `crm-config.json` существует и содержит `account_token` — перейти к Step 4/5.

Если конфига нет — выполнить Step 3.1 (onboarding нового клиента).

---

## Step 3.1 — Merge Link Onboarding (новый клиент)

Спроси у пользователя:
> "Email и название компании клиента? (нужно для Merge Link)"

Затем создай link token:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

CLIENT_EMAIL="[введённый email]"
CLIENT_ORG="[введённое название]"
CLIENT_ID="$(echo '$ENGAGEMENT' | tr '[:upper:]' '[:lower:]' | tr ' ' '_')"

curl -s -X POST "https://api.merge.dev/api/integrations/create-link-token" \
  -H "Authorization: Bearer $MERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"end_user_email_address\": \"$CLIENT_EMAIL\",
    \"end_user_organization_name\": \"$CLIENT_ORG\",
    \"end_user_origin_id\": \"$CLIENT_ID\",
    \"categories\": [\"crm\"]
  }"
```

Показать пользователю:
```
🔗 Ссылка для подключения CRM клиента:
https://link.merge.dev/[link_token]

Отправьте эту ссылку клиенту. Клиент:
1. Открывает ссылку
2. Выбирает свою CRM (HubSpot / Salesforce / Pipedrive / др.)
3. Авторизуется через OAuth

После подключения клиента:
— Зайди в Merge Dashboard → Linked Accounts
— Скопируй Account Token для этого клиента
— Введи его здесь: /crm-sync [engagement] --account-token at_xxx
```

Стоп. Ждём account_token от пользователя.

---

## Step 3.2 — Сохранить account_token

Когда пользователь предоставил account_token:

Сохранить в `[ENGAGEMENT_DIR]/crm-config.json`:
```json
{
  "provider": "merge.dev",
  "account_token": "[account_token]",
  "client": "[ENGAGEMENT]",
  "connected_at": "[YYYY-MM-DD]"
}
```

Перейти к Step 4 или 5.

---

## Step 4 — Pull: загрузить данные из CRM

Если direction = pull:

```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

ACCOUNT_TOKEN=$(python3 -c "import json; d=json.load(open('$ENGAGEMENT_DIR/crm-config.json')); print(d['account_token'])")

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/crm-sync/fetch_crm.py \
  --dir "$ENGAGEMENT_DIR" \
  --account-token "$ACCOUNT_TOKEN"
```

Показать пользователю прогресс из stdout скрипта.

После успешного pull:
```
✅ CRM данные загружены: [ENGAGEMENT_DIR]/crm-data/

📊 Загружено:
  Contacts:      [N]
  Accounts:      [N]
  Opportunities: [N]
  Notes:         [N]

Данные готовы для использования агентами в пайплайне.
```

---

## Step 5 — Push: записать данные в CRM

Если direction = push:

Найди crm-update.json:
```bash
DATA_FILE="$ENGAGEMENT_DIR/crm-update.json"
if [ ! -f "$DATA_FILE" ]; then
  echo "NOT_FOUND"
  find "$ENGAGEMENT_DIR" -name "crm-update.json" | head -3
fi
```

Если файл не найден:
> "crm-update.json не найден. Сначала запусти `/analyze-call` для генерации файла."
Стоп.

Если файл найден:
```bash
set -a; source /Users/maximpuda/Projects/bcg-team/.env; set +a

ACCOUNT_TOKEN=$(python3 -c "import json; d=json.load(open('$ENGAGEMENT_DIR/crm-config.json')); print(d['account_token'])")

python3 /Users/maximpuda/Projects/bcg-team/.claude/skills/crm-sync/write_crm.py \
  --data "$DATA_FILE" \
  --account-token "$ACCOUNT_TOKEN"
```

После успешного push:
```
✅ CRM обновлён!

📝 Записано:
  MEDDPICC поля: обновлены
  Next Step: обновлён
  Call note: добавлена
```
