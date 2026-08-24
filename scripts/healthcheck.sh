#!/bin/bash
# Сторож-диагност: проверяет ботов + gateway + сервер, чинит упавшее, шлёт алерт Артуру.
# Работает НАПРЯМУЮ через cron и не зависит от gateway — переживёт даже его падение.

CHAT_ID="199790247"
LOG="/root/.openclaw/workspace-neuro/logs/healthcheck.log"
mkdir -p "$(dirname "$LOG")"

# токен для алертов (тот же, что у постеров)
source /root/.openclaw/workspace-neuro/.bots_env.sh 2>/dev/null
TOKEN="$OPENCLAW_POSTER_BOT_TOKEN"

# список сервисов: боты + gateway
SERVICES="fobs_investor_bot fobs_assistant_bot serbian-translator-bot megamind-bot karen-bot content-bot maksim-bot clinic-ryadom-main clinic-ryadom-dermatolog clinic-ryadom-gastro clinic-ryadom-kardiolog clinic-ryadom-nevrolog clinic-ryadom-psiholog clinic-ryadom-terapevt clinic140 site-projects-bot openclaw-gateway-helper openclaw-gateway-rodion"

ALERTS=""

# 1. проверка сервисов
for svc in $SERVICES; do
  state=$(systemctl is-active "$svc" 2>/dev/null)
  if [ "$state" != "active" ]; then
    systemctl restart "$svc" 2>/dev/null
    sleep 1
    newstate=$(systemctl is-active "$svc" 2>/dev/null)
    if [ "$newstate" = "active" ]; then
      ALERTS="$ALERTS
✅ $svc: был '$state' → перезапустил, теперь active"
    else
      ALERTS="$ALERTS
🔴 $svc: был '$state', перезапуск не помог (теперь '$newstate')"
    fi
  fi
done

# 2. диск и память
DISK=$(df -h / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
[ "${DISK:-0}" -gt 90 ] 2>/dev/null && ALERTS="$ALERTS
🟥 Диск заполнен на ${DISK}%"

MEM=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
[ "${MEM:-0}" -gt 95 ] 2>/dev/null && ALERTS="$ALERTS
🟥 Память занята на ${MEM}%"

# 3. отправить алерт, если есть проблемы
if [ -n "$ALERTS" ] && [ -n "$TOKEN" ]; then
  MSG="🔧 Сторож-диагност $(date '+%d.%m %H:%M'):${ALERTS}"
  curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d chat_id="$CHAT_ID" -d text="$MSG" > /dev/null 2>&1
fi

echo "$(date '+%F %T') check done. alerts: $([ -n "$ALERTS" ] && echo yes || echo no)" >> "$LOG"
