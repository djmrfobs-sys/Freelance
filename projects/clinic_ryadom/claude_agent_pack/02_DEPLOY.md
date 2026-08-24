# КЛИНИКА РЯДОМ - КАК ЗАПУЩЕНО (DEPLOY)

## Сервер
- Ubuntu, сервер: 4 ядра, 8 ГБ RAM, 2 ТБ диск.
- Временная зона: Etc/UTC (в коде даты берутся в UTC).

## База данных
- PostgreSQL, база: `clinic_ryadom`
- Пользователь/пароль: `clinic_ryadom` / `clinic_ryadom_2026`
- Подключение: `host=127.0.0.1 dbname=clinic_ryadom user=clinic_ryadom password=clinic_ryadom_2026`
- DSN зашит в `db.py` (DB_DSN).

## Таблицы в БД (реальная проверка, 12.08.2026)
Реально в базе 8 таблиц:
- admins
- chat_history
- client_card  [ЕСТЬ в БД, но НЕ описан в schema.sql - создаётся отдельной миграцией]
- consent
- daily_limits
- payments
- subscriptions
- users

Таблица client_card (реальная структура):
```
user_id    bigint PK (FK -> users, ON DELETE CASCADE)
full_name  text
age        text
gender     text
chronics   text
complaints text
completed  boolean default false
updated_at timestamptz default now()
```

ВАЖНО: чтобы восстановить БД с нуля из schema.sql, надо ДОБАВИТЬ CREATE TABLE IF NOT EXISTS client_card в schema.sql. Сейчас схема неполная.

## Запуск ботов (systemd)
7 сервисов (все active):
- clinic-ryadom-main.service  → python bot.py main  (@Clinic_ryadom_bot)
- clinic-ryadom-terapevt.service → python bot.py terapevt
- clinic-ryadom-psiholog.service → python bot.py psiholog
- clinic-ryadom-kardiolog.service → python bot.py kardiolog
- clinic-ryadom-gastro.service  → python bot.py gastro
- clinic-ryadom-nevrolog.service → python bot.py nevrolog
- clinic-ryadom-dermatolog.service → python bot.py dermatolog

Перезапуск одного: `systemctl restart clinic-ryadom-terapevt.service`
Проверка: `systemctl is-active clinic-ryadom-terapevt.service`

## Токены
- Лежат в `secrets/*.token` (по одному файлу на бота, права 600).
- main_bot.token, terapevt_bot.token, psiholog_bot.token, kardiolog_bot.token, gastro_bot.token, nevrolog_bot.token, dermatolog_bot.token
- Токены - секреты, НЕ выкладывать наружу.

## API-ключи нейросетей (вне папки клиники, общие для сервера)
- DeepSeek: `~/.openclaw-neuro/.deepseek_key`
- Gemini Vision: `~/.openclaw-neuro/.gemini_key`
- Groq (Whisper для голоса): `~/.openclaw-neuro/.groq_key`

## Python-стек
- python-telegram-bot (боты)
- psycopg2 (PostgreSQL)
- groq (распознавание голоса) - добавлено 12.08.2026
- Через urllib напрямую (DeepSeek, Gemini) - без SDK для этих нейросетей

## Команда для проверки синтаксиса
```
cd /root/.openclaw/workspace-neuro/projects/clinic_ryadom
python3 -c "import ast; ast.parse(open('bot.py').read()); print('OK')"
```
