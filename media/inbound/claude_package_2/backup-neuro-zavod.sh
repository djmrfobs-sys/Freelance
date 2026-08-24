#!/usr/bin/env bash
set -euo pipefail

# === Настройки — поправь под свои реальные пути ===
BACKUP_ROOT="$HOME/backups/neuro-zavod"
SOURCES=(
  "$HOME/.openclaw-neuro/config.json5"      # конфиг gateway
  "$HOME/.openclaw-neuro/skills"            # все 95 скиллов
  "$HOME/projects/zavod"                    # цеха 01-07
  "$HOME/knowledge/artur"                   # копилка знаний
)
KEEP_DAYS=14          # сколько дней хранить локальные архивы
REMOTE_DEST=""        # напр. "user@backup-server:/backups/neuro/" — оставь пустым, если не настроено ещё

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="neuro-zavod-${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_ROOT}/${ARCHIVE_NAME}"

mkdir -p "$BACKUP_ROOT"

echo "[$(date)] Старт бэкапа -> ${ARCHIVE_PATH}"

# Собираем архив, пропуская несуществующие пути (не падаем, если чего-то пока нет)
EXISTING_SOURCES=()
for src in "${SOURCES[@]}"; do
  if [ -e "$src" ]; then
    EXISTING_SOURCES+=("$src")
  else
    echo "[$(date)] WARN: путь не найден, пропускаю: $src"
  fi
done

if [ ${#EXISTING_SOURCES[@]} -eq 0 ]; then
  echo "[$(date)] ERROR: ни один источник не найден, бэкап не создан"
  exit 1
fi

tar -czf "$ARCHIVE_PATH" "${EXISTING_SOURCES[@]}" 2>/dev/null || {
  echo "[$(date)] ERROR: tar завершился с ошибкой"
  exit 1
}

echo "[$(date)] Архив создан: $(du -h "$ARCHIVE_PATH" | cut -f1)"

# Ротация — удаляем локальные архивы старше KEEP_DAYS
find "$BACKUP_ROOT" -name "neuro-zavod-*.tar.gz" -mtime "+${KEEP_DAYS}" -delete
echo "[$(date)] Ротация: удалены архивы старше ${KEEP_DAYS} дней"

# Отправка на удалённое хранилище (если настроено)
if [ -n "$REMOTE_DEST" ]; then
  echo "[$(date)] Копирую на удалённое хранилище..."
  scp -q "$ARCHIVE_PATH" "$REMOTE_DEST" && echo "[$(date)] Скопировано на $REMOTE_DEST"
else
  echo "[$(date)] REMOTE_DEST не настроен — архив остаётся только локально. Это риск при падении сервера!"
fi

echo "[$(date)] Бэкап завершён успешно"
