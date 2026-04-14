---
name: analyze-call
description: >
  Analyzes a sales call transcript and extracts MEDDPICC/BANT/3 Whys signals with quotes,
  generates Opportunity Summary (Key Risks, Key Players, Key Decisions, Next Steps),
  and produces crm-update.json ready for CRM write-back.
  Use when: /analyze-call, "проанализируй звонок", "разбор звонка", "транскрипт звонка",
  "analyze transcript", "MEDDPICC extraction", "что было на звонке".
argument-hint: <company_name> [transcript_file_path]  # e.g. "Acme Corp" or "Acme Corp transcript.txt"
disable-model-invocation: true
---

# Analyze Call — Sales Transcript Intelligence

**Аргументы:** $ARGUMENTS

---

## Step 1 — Разбор аргументов и получение транскрипта

Разбери `$ARGUMENTS`:
- Первая часть = **COMPANY** (название компании с которой был звонок)
- Вторая часть (если есть) = **TRANSCRIPT_PATH** (путь к файлу транскрипта)

### Если TRANSCRIPT_PATH указан:
```bash
if [ -f "$TRANSCRIPT_PATH" ]; then
  echo "STATUS:OK"
  echo "FILE:$TRANSCRIPT_PATH"
else
  echo "STATUS:NOT_FOUND"
fi
```

Если файл не найден — сообщи пользователю и попроси указать правильный путь.

### Если TRANSCRIPT_PATH НЕ указан:
Попроси пользователя:
> "Вставь транскрипт звонка с [COMPANY] прямо в чат (или укажи путь к файлу):"

Используй вставленный текст как транскрипт.

---

## Step 2 — Определить или создать директорию

Спроси пользователя:
> "Добавить анализ к существующему engagement (укажи папку в research/) или создать новую? [папка / новая]"

### Если существующая папка:
```bash
BASE="/Users/maximpuda/Projects/bcg-team/research"
if [ -d "$BASE/$FOLDER" ]; then
  echo "OUTPUT_DIR:$BASE/$FOLDER"
else
  echo "NOT_FOUND"
  ls "$BASE"
fi
```

### Если новая:
```bash
DATE=$(date +%d.%m.%Y)
COMPANY_SLUG=$(echo "$COMPANY" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
OUTPUT_DIR="/Users/maximpuda/Projects/bcg-team/research/${COMPANY_SLUG}-call-${DATE}"
mkdir -p "$OUTPUT_DIR"
echo "OUTPUT_DIR:$OUTPUT_DIR"
```

### Если транскрипт вставлен как текст — сохрани его:
```bash
cat > "$OUTPUT_DIR/transcript.txt" << 'TRANSCRIPT_EOF'
[ВСТАВЛЕННЫЙ ТЕКСТ]
TRANSCRIPT_EOF
echo "Transcript saved: $OUTPUT_DIR/transcript.txt"
```

---

## Step 3 — Запустить bcg-call-analyzer агент

Запусти агент **bcg-call-analyzer** со следующими параметрами:

```
Компания (prospect): [COMPANY]
Транскрипт: [путь к файлу или текст]
OUTPUT_DIR: [OUTPUT_DIR из Step 2]
Output file: [OUTPUT_DIR]/call-analysis.md
```

Агент сгенерирует:
- `call-analysis.md` — MEDDPICC + BANT + 3 Whys + Opportunity Summary + Coaching
- `crm-update.json` — готово для записи в Salesforce/HubSpot

Сообщи пользователю во время работы:
```
🎙️ Анализирую звонок с [COMPANY]...
📊 Извлекаю MEDDPICC сигналы...
```

---

## Step 4 — Показать результат

После завершения агента прочитай `[OUTPUT_DIR]/call-analysis.md` и выведи:

```
✅ Анализ звонка готов: [COMPANY]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MEDDPICC SCORE
[краткая таблица из MEDDPICC Analysis — что confirmed / missing]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ KEY RISKS
[Key Risks из Opportunity Summary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 KEY PLAYERS
[Key Players из Opportunity Summary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ NEXT STEPS
[Next Steps таблица]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CRITICAL PATH
[Critical Path to Closure]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 RISK LEVEL: [Low/Medium/High]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Полный анализ: [OUTPUT_DIR]/call-analysis.md
📋 CRM Update JSON: [OUTPUT_DIR]/crm-update.json
```

---

## Step 5 — CRM Write-back (опционально)

Спроси пользователя:
> "Записать обновления в CRM? (да/нет — требует настроенного /crm-sync)"

Если **да** — запусти `/crm-sync [COMPANY] --direction push --data [OUTPUT_DIR]/crm-update.json`

---

## Step 6 — Экспорт в Notion (опционально)

Спроси пользователя:
> "Экспортировать анализ в Notion? (да/нет)"

Если **да** — запусти `/notion-export [engagement_dir_name]`
