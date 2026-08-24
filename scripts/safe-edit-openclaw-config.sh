#!/bin/bash
# safe-edit-openclaw-config.sh (усиленная версия, 2026-08-14)
# Безопасное редактирование /root/.openclaw-neuro/openclaw.json:
#  1) бэкапит текущий файл перед правкой (с автоочисткой старых бэкапов)
#  2) открывает конфиг в редакторе ИЛИ принимает переданный путь/файл
#  3) проверяет валидность JSON (синтаксис)
#  4) проверяет ключевую структуру конфига (обязательные поля)
#  5) если что-то не так — предлагает откатить на бэкап
#  6) если всё ок — перезапускает openclaw-gateway.service и реально проверяет здоровье
#
# Использование:
#   ./safe-edit-openclaw-config.sh                    # открыть в $EDITOR (vim/nano/...)
#   ./safe-edit-openclaw-config.sh <путь-к-новому-json>  # проверить и применить готовый файл
#   ./safe-edit-openclaw-config.sh --check            # только проверить текущий конфиг
#   ./safe-edit-openclaw-config.sh --rollback <бэкап> # откатиться на конкретный бэкап

set -u

CONFIG="/root/.openclaw-neuro/openclaw.json"
BACKUP_DIR="/root/.openclaw-neuro/config-backups"
MAX_BACKUPS=20            # храним не больше 20 последних бэкапов
PROFILE="neuro"           # профиль openclaw
SERVICE="openclaw-gateway.service"

mkdir -p "$BACKUP_DIR"

log()  { echo "[safe-edit] $*"; }
err()  { echo "[safe-edit] ОШИБКА: $*" >&2; }

# --- Проверка структуры конфига (ключевые поля, которые обязаны существовать) ---
check_structure() {
  python3 - "$CONFIG" <<'PY'
import json, sys
p = sys.argv[1]
try:
    d = json.load(open(p, encoding="utf-8"))
except Exception as e:
    print(f"НЕВАЛИДНЫЙ JSON: {e}")
    sys.exit(1)

problems = []

# обязательные корневые секции
for key in ("agents", "channels", "models"):
    if key not in d:
        problems.append(f"нет секции '{key}'")

# агенты: должен быть список и хотя бы один
ag = d.get("agents", {})
lst = ag.get("list", [])
if not isinstance(lst, list) or not lst:
    problems.append("agents.list пуст или не список")
else:
    ids = [a.get("id") for a in lst if isinstance(a, dict)]
    if "main" not in ids:
        problems.append("в agents.list нет агента 'main' (нужен минимум один главный)")

# telegram-аккаунты
ch = d.get("channels", {})
accs = ch.get("telegram", {}).get("accounts", {})
if not isinstance(accs, dict) or not accs:
    problems.append("channels.telegram.accounts пуст")

# проверка, что id агентов не дублируются
if isinstance(lst, list):
    if len(ids) != len(set(ids)):
        problems.append("дублируются id агентов в agents.list")

if problems:
    print("ПРОБЛЕМЫ СТРУКТУРЫ:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(2)
else:
    print("Структура конфига корректна. Обязательные поля на месте.")
    sys.exit(0)
PY
}

# --- Проверка валидности JSON ---
check_json() {
  python3 -m json.tool "$CONFIG" > /dev/null 2>&1
}

# --- Очистка старых бэкапов ---
cleanup_backups() {
  # удаляем самые старые, оставляя MAX_BACKUPS последних
  ls -1t "$BACKUP_DIR"/openclaw.json.*.bak 2>/dev/null | tail -n +$((MAX_BACKUPS+1)) | while read -r old; do
    rm -f "$old" && log "удалён старый бэкап: $old"
  done
}

# --- Перезапуск и реальная проверка здоровья сервиса ---
restart_and_check() {
  local tries=0
  log "Перезапускаю $SERVICE ..."
  systemctl --user restart "$SERVICE"
  # ждём до 30 сек, пока сервис не станет active
  while [ $tries -lt 10 ]; do
    sleep 3
    if systemctl --user is-active --quiet "$SERVICE"; then
      log "Сервис активен."
      # дополнительно проверим, что gateway отвечает (если есть CLI)
      if command -v openclaw >/dev/null 2>&1; then
        local d=""
        d=$(openclaw --profile "$PROFILE" gateway status 2>&1 | head -5)
        if echo "$d" | grep -qiE "running|active|ok"; then
          log "Gateway отвечает: OK"
        else
          log "ВНИМАНИЕ: gateway статус выглядит необычно:"
          echo "$d"
        fi
      fi
      return 0
    fi
    tries=$((tries+1))
    log "Сервис ещё поднимается... ($((tries*3)) сек)"
  done
  err "Сервис не поднялся за 30 сек. Смотри systemctl --user status $SERVICE"
  return 1
}

# --- Логика ---
ACTION="${1:-}"
case "$ACTION" in
  --check)
    log "Только проверка текущего конфига..."
    check_json || { err "JSON невалиден"; exit 1; }
    check_structure
    exit $?
    ;;
  --rollback)
    TARGET="${2:-}"
    if [ -z "$TARGET" ] || [ ! -f "$TARGET" ]; then
      err "Укажи существующий файл бэкапа: $0 --rollback <файл>"
      exit 1
    fi
    cp "$TARGET" "$CONFIG"
    log "Откачено на: $TARGET"
    restart_and_check || exit 1
    exit 0
    ;;
esac

# если передан файл-замена — применяем его
if [ -n "$ACTION" ] && [ -f "$ACTION" ]; then
  log "Применяю файл: $ACTION"
  cp "$ACTION" "$CONFIG"
  NEW_FILE=1
else
  NEW_FILE=0
fi

# 1) бэкап
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/openclaw.json.$TIMESTAMP.bak"
cp "$CONFIG" "$BACKUP_FILE"
log "Бэкап сохранён: $BACKUP_FILE"

# если не применяли файл-замену — то NO_NANO не интерактивный по умолчанию для SSH/exec
if [ "$NEW_FILE" = "0" ]; then
  # поддержка не-интерактивного редактирования: открываем в $EDITOR если есть tty
  if [ -t 0 ]; then
    log "Открываю редактор. Сохрани и выйди, когда закончишь."
    ${EDITOR:-nano} "$CONFIG"
  else
    err "Нет интерактивного терминала. Передай файл-замену: $0 <путь-к-json>"
    log "Ничего не менял. Бэкап остался: $BACKUP_FILE"
    exit 1
  fi
fi

# 2) проверка JSON-синтаксиса
if ! check_json; then
  err "JSON невалиден после правки!"
  python3 -m json.tool "$CONFIG" 2>&1 | tail -8
  read -r -p "Откатить на бэкап $BACKUP_FILE ? [Y/n]: " ans
  ans=${ans:-Y}
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    cp "$BACKUP_FILE" "$CONFIG"
    log "Откачено. Изменения отменены."
    exit 1
  else
    err "Оставлен невалидный конфиг. Сервис не запустится, пока не исправишь."
    exit 1
  fi
fi
log "Синтаксис JSON: валиден."

# 3) проверка структуры
if ! output=$(check_structure); then
  echo "$output"
  read -r -p "Откатить на бэкап $BACKUP_FILE ? [Y/n]: " ans
  ans=${ans:-Y}
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    cp "$BACKUP_FILE" "$CONFIG"
    log "Откачено. Изменения отменены."
    exit 1
  else
    err "Оставлен конфиг с проблемами структуры. Рискуешь, что сервис не поднимется."
  fi
else
  echo "$output"
fi

# 4) очистка старых бэкапов
cleanup_backups

# 5) перезапуск с проверкой
restart_and_check || exit 1

log "Готово. Актуальный конфиг: $CONFIG"
log "Бэкапы: $BACKUP_DIR (храним последние $MAX_BACKUPS)"
