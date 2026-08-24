#!/bin/bash
# safe-edit-openclaw-config.sh
# Безопасное редактирование /root/.openclaw-neuro/openclaw.json:
# 1) бэкапит текущий файл перед правкой
# 2) открывает его в nano
# 3) после сохранения проверяет валидность JSON
# 4) если JSON битый — предлагает откатить на бэкап
# 5) если всё ок — перезапускает openclaw-gateway.service

set -e

CONFIG="/root/.openclaw-neuro/openclaw.json"
BACKUP_DIR="/root/.openclaw-neuro/config-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/openclaw.json.$TIMESTAMP.bak"

mkdir -p "$BACKUP_DIR"

if [ ! -f "$CONFIG" ]; then
  echo "Ошибка: $CONFIG не найден."
  exit 1
fi

cp "$CONFIG" "$BACKUP_FILE"
echo "Бэкап сохранён: $BACKUP_FILE"

# Открыть в редакторе (nano по умолчанию)
${EDITOR:-nano} "$CONFIG"

# Проверить валидность JSON
if python3 -m json.tool "$CONFIG" > /dev/null 2>&1; then
  echo "JSON валиден."
else
  echo "ОШИБКА: JSON невалиден после правки!"
  echo "Детали:"
  python3 -m json.tool "$CONFIG" 2>&1 | tail -5
  read -p "Откатить на бэкап $BACKUP_FILE ? [Y/n]: " ans
  ans=${ans:-Y}
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    cp "$BACKUP_FILE" "$CONFIG"
    echo "Откачено на бэкап. Изменения отменены."
    exit 1
  else
    echo "Оставлен невалидный конфиг — сервис не запустится, пока не исправите вручную."
    exit 1
  fi
fi

# Дополнительная проверка через openclaw doctor (если доступен)
if command -v openclaw >/dev/null 2>&1; then
  echo "Запускаю openclaw doctor --fix для дополнительной проверки..."
  openclaw --profile neuro doctor --fix || true
fi

echo "Перезапускаю openclaw-gateway.service..."
systemctl --user restart openclaw-gateway.service
sleep 2
systemctl --user status openclaw-gateway.service --no-pager -l | head -10

echo ""
echo "Готово. Старые бэкапы лежат в $BACKUP_DIR (можно чистить вручную по мере накопления)."
