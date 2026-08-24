# RESTORE.md - Восстановление нейрозавода на новом сервере

Цель: если Hetzner-дроплет умрёт (физически / диск / переустановка) - развернуть всё заново
по этому документу. Бэкап-архив: `/root/backups/neuro-zavod/neuro-zavod-*.tar.gz` (~137M).

## Сырая сводка того, что должно быть восстановлено (проверено 13.08.2026)

- OpenClaw 2026.7.1-2 (0790d9f)
- workspace: /root/.openclaw/workspace-neuro
- конфиг gateway: /root/.openclaw-neuro/openclaw.json
- ключи: /root/.openclaw-neuro/.deepseek_key, .groq_key (а также .gemini_key, .apify_key НЕ в бэкапе - перевыпустить!)
- 15 ботов на systemd (полный список ниже)
- secrets ботов: /root/.openclaw/workspace-neuro/secrets/*.token
- бэкап нейрозавода: скрипт + systemd-таймер neuro-backup.timer (ежедневно 06:00)

## ВАЖНО: что НЕ попадает в бэкап (проверено!)

Эти данные живут вне архива - их надо восстановить/создать руками или клиентами:
- .bot_token Telegram самого OpenClaw (в openclaw.json, поле botToken - там есть)
- .gemini_key, .apify_key (если нужны - перевыпустить в консолях Google/Apify)
- доступы к Lovable/Supabase/хостингам (вне сервера)
- любые файлы в /tmp

## Полный список 15 ботов (systemd-сервисы, 39 активных юнитов суммарно)

| Бот | WorkingDirectory | Как запустить |
|---|---|---|
| fobs_investor_bot | /root/workspace/fobs_projects/investor | systemctl start fobs_investor_bot |
| fobs_assistant_bot | /root/workspace | systemctl start fobs_assistant_bot |
| serbian-translator-bot | /root/.openclaw/workspace-neuro/projects/serbian_translator_bot | systemctl start serbian-translator-bot |
| megamind-bot | /root/.openclaw/workspace-neuro/projects/megamind_bot | systemctl start megamind-bot |
| karen-bot | /root/karen-bot | systemctl start karen-bot |
| content-bot | /root/.openclaw/workspace-neuro/projects/content_bot | systemctl start content-bot |
| maksim-bot | /root/.openclaw/workspace-neuro/projects/zavod/07_maksim_bot | systemctl start maksim-bot |
| clinic140 | /root/workspace/clinic140 | systemctl start clinic140 |
| clinic-ryadom-main/dermatolog/gastro/kardiolog/nevrolog/psiholog/terapevt | /root/.openclaw/workspace-neuro/projects/clinic_ryadom | systemctl start clinic-ryadom-* |

## ПОШАГОВАЯ ПРОЦЕДУРА ВОССТАНОВЛЕНИЯ

### Шаг 1. Поднять свежий сервер (Hetzner / любой Linux)
- Ubuntu 22.04/24.04, минимум 2GB RAM, ~20GB диск. Включить IPv4+IPv6.

### Шаг 2. Установить OpenClaw той же версии
```
npm install -g openclaw@2026.7.1-2
# или: openclaw (актуальная) если совместимо; но версия должна совпадать с архивом
```

### Шаг 3. Датация бэкапа
Если архив НА СЕРВЕРЕ - сначала спасти его (scp на новую машину):
```
scp root@<старый-ip>:/root/backups/neuro-zavod/neuro-zavod-*.tar.gz ./
```
Если архив во ВНЕШНЕМ хранилище (Backblaze B2 / второй VPS / Google Drive) - скачать оттуда.

### Шаг 4. Распаковать архив в корень
```
tar -xzf neuro-zavod-*.tar.gz -C /
```
Архив хранит пути вида `root/.openclaw/...` - распакуется в нужные места.

### Шаг 5. Восстановить ключи/токены (чего нет в архиве)
- .gemini_key, .apify_key - перевыпустить (см. список «что не в бэкапе»)
- если токены ботов не подхватились - проверить /root/.openclaw/workspace-neuro/secrets/*.token

### Шаг 6. Поднять systemd-сервисы
```
# перечитать unit-файлы
systemctl daemon-reload
# по очереди каждый бот (см. таблицу выше)
systemctl start <имя-бота>
systemctl enable <имя-бота>   # автозапуск при ребуте
```

### Шаг 7. Поднять gateway OpenClaw
```
openclaw gateway start   # или через systemd: systemctl --user start openclaw-gateway
openclaw status          # проверить, что запущен и отвечает
```

### Шаг 8. Проверка после восстановления
```
systemctl list-units --type=service | grep -E "fobs|clinic|karen|maksim|megamind|content|translat"   # все active
ls /root/backups/neuro-zavod/          # бэкап на месте
openclaw status                        # gateway ОК
```

## РЕЦЕПТ ПРОВЕРКИ БЭКАПА (периодически)
Раз в 1-2 месяца - реальный тест: распаковать архив на чистом тестовом дроплете,
убедиться что все коды и токены на месте, потом удалить тестовую машину.

## Финальные советы
- НЕ хранить только локально: архив должен выгружаться ВОВНЕ (Backblaze B2 / второй VPS / Google Drive).
  Сейчас (13.08.2026) REMOTE_DEST в backup-neuro-zavod.sh ПУСТ - это критичная дыра, закрыть первым делом.
- Секреты не коммитить в git. Все токены - только secrets/ + .openclaw-neuro/.

---
Дата создания: 13.08.2026. Ревизия: 1.
