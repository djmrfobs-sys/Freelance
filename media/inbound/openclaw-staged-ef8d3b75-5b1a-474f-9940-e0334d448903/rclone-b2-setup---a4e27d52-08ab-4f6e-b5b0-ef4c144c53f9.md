# Настройка rclone для бэкапа в Backblaze B2 (бакет: reservd)

## Шаг 1 — установить rclone (если ещё не стоит)
curl https://rclone.org/install.sh | sudo bash

## Шаг 2 — создать конфиг rclone напрямую (без интерактивного мастера)
mkdir -p ~/.config/rclone
cat > ~/.config/rclone/rclone.conf << 'EOF'
[b2]
type = b2
account = 00549fc0da1d2150000000001
key = K005zsUY3bc9IvYSqaiyle73Bpi4CiE
endpoint = s3.us-east-005.backblazeb2.com
EOF

chmod 600 ~/.config/rclone/rclone.conf

## Шаг 3 — проверить, что подключение работает
rclone lsd b2:reservd
# Должно вернуть пустой список (бакет пока пустой) без ошибок авторизации

## Шаг 4 — тестовая заливка архива вручную
rclone copy /root/backups/ b2:reservd/ --include "*.tar.gz" -v
# Проверь: rclone ls b2:reservd — должен показать залитый архив

---

# Обновление backup-neuro-zavod.sh

Замени блок REMOTE_DEST в скрипте на этот (вместо scp):

    # Отправка на Backblaze B2 через rclone
    echo "[$(date)] Копирую в Backblaze B2..."
    if rclone copy "$ARCHIVE_PATH" b2:reservd/ -v; then
      echo "[$(date)] Успешно загружено в b2:reservd/${ARCHIVE_NAME}"
    else
      echo "[$(date)] ERROR: не удалось загрузить в B2"
      exit 1
    fi

    # Ротация в самом B2 — не храним больше 30 архивов в облаке
    rclone delete --min-age 30d b2:reservd/ --include "neuro-zavod-*.tar.gz"

Полностью замени старый блок с `if [ -n "$REMOTE_DEST" ]` на этот — переменная REMOTE_DEST больше не нужна.

## После правки — тестовый прогон всего скрипта
systemctl --user start neuro-backup.service
journalctl --user -u neuro-backup.service -n 30
rclone ls b2:reservd
