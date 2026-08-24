#!/usr/bin/env bash
# token-usage-log.sh — простой лог расхода по каждому собранному проекту
# Вызывать вручную (или из конвейера) в конце Этапа 5 (релиз) с параметрами

set -euo pipefail

LOG_FILE="$HOME/backups/token-usage.csv"
PROJECT_NAME="${1:?Использование: token-usage-log.sh <имя_проекта> <входные_токены> <выходные_токены> <модель>}"
INPUT_TOKENS="${2:?нужны входные токены}"
OUTPUT_TOKENS="${3:?нужны выходные токены}"
MODEL="${4:?нужна модель}"

# Создать файл с заголовком, если его ещё нет
if [ ! -f "$LOG_FILE" ]; then
  echo "date,project,model,input_tokens,output_tokens" > "$LOG_FILE"
fi

echo "$(date -Iseconds),${PROJECT_NAME},${MODEL},${INPUT_TOKENS},${OUTPUT_TOKENS}" >> "$LOG_FILE"

echo "Записано: $PROJECT_NAME ($MODEL) — in:$INPUT_TOKENS out:$OUTPUT_TOKENS"

# Еженедельная сводка (запускать отдельно, например по воскресеньям)
weekly_summary() {
  echo "=== Сводка за последние 7 дней ==="
  awk -F, -v cutoff="$(date -d '7 days ago' -Iseconds)" '
    NR>1 && $1 >= cutoff {
      in_sum[$3] += $4; out_sum[$3] += $5; count[$3]++
    }
    END {
      for (m in in_sum) printf "%s: %d проектов, in=%d out=%d\n", m, count[m], in_sum[m], out_sum[m]
    }
  ' "$LOG_FILE"
}

# Раскомментируй, чтобы сразу увидеть сводку после записи:
# weekly_summary
