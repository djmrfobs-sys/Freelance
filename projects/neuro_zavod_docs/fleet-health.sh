#!/usr/bin/env bash
# fleet-health.sh — проверка всех systemd --user юнитов нейрозавода
# Шлёт алерт в АДМИН-чат ТОЛЬКО при аномалии, не спамит "всё ок"

set -euo pipefail

# === Настройки — поправь под реальные имена юнитов ===
UNITS=(
  "openclaw-gateway.service"
  "fobs-investor-bot.service"
  "fobs-assistant-bot.service"
  "karen-bot.service"
  "clinic140.service"
  # ... добавь остальные 10 юнитов сюда по факту их реальных имён
)

# Telegram админ-чат для алертов (ОТДЕЛЬНЫЙ от пользовательских ботов!)
ADMIN_BOT_TOKEN=""   # впиши токен бота-наблюдателя
ADMIN_CHAT_ID=""     # твой личный chat_id, не пользовательский чат

FAILED_UNITS=()

for unit in "${UNITS[@]}"; do
  status=$(systemctl --user is-active "$unit" 2>/dev/null || echo "inactive")
  if [ "$status" != "active" ]; then
    FAILED_UNITS+=("$unit: $status")
  fi
done

if [ ${#FAILED_UNITS[@]} -gt 0 ]; then
  MESSAGE="⚠️ Fleet health alert ($(date '+%Y-%m-%d %H:%M')):"$'\n'
  for f in "${FAILED_UNITS[@]}"; do
    MESSAGE+=$'\n'"❌ $f"
  done

  echo "$MESSAGE"

  if [ -n "$ADMIN_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot${ADMIN_BOT_TOKEN}/sendMessage" \
      -d chat_id="${ADMIN_CHAT_ID}" \
      -d text="${MESSAGE}" > /dev/null
  fi
else
  echo "[$(date)] Все ${#UNITS[@]} юнитов активны — OK (без алерта, тихо)"
fi
