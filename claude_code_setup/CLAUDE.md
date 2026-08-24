# CLAUDE.md — KISELEVY CREO Project Agent

## 1. Project overview

KISELEVY CREO — digital agency (Артур + Кети). Основные направления:
- Telegram-каналы (@kiselevy_creo_digital, @ecstatic_dance_mantra)
- AI-продукты: боты, автоматизация, вайбкодинг
- Instagram-аккаунты (парсинг, анализ, стратегии)
- Lovable-проекты (веб-приложения на Supabase)

## 2. Stack

- **Frontend:** Lovable.dev (React/Vite), иногда Next.js
- **Backend:** Supabase (PostgreSQL, Edge Functions, Auth, Storage)
- **Hosting:** Supabase, Lovable preview, GitHub Pages
- **CI/CD:** GitHub Actions
- **Python:** Парсинг (Apify), обработка данных
- **Telegram bots:** python-telegram-bot / aiogram, python-telegram-bot
- **OS:** macOS (рабочая станция)

## 3. Project locations

Root workspace: ~/Desktop/Project/

Active subfolders:
- Мои проекты/ — основные проекты
- МАНТРЫ 2026/ — контент для @ecstatic_dance_mantra
- ANGAR/ — возможно склад/инвентарь
- АФФЕРМАЦИИ/ — контент-материалы
- Баговская/ — проект Bagovskaya Boho (Lovable)

## 4. Conventions

- Telegram-посты: короткие тире (–), только векторные/монохромные эмодзи, без ошибок, без лишних символов
- Посты от Артура — от 1-го лица ("я Артур"), от Кети — от 1-го лица ("я Кети"), вместе — "мы"
- Код: комментарии на русском или английском, переменные — camelCase
- Git: коммиты на русском, описывают ЧТО сделано
- .env файлы — никогда не коммитить
- Перед изменением файлов — спрашивать подтверждение

## 5. DO NOT TOUCH (без подтверждения)

- .env, .env.local, *.key
- node_modules/, venv/, __pycache__/
- Существующие базы данных (только чтение через SQL)
- production-конфиги (supabase/config.toml, docker-compose.yml)
- Чужие скриншоты и медиа-файлы

## 6. Agent mode instructions

Когда я (агент) работаю в этом проекте:
1. Всегда читаю этот файл первым делом
2. Перед любыми изменениями сообщаю план и жду подтверждения
3. После выполнения задачи — краткий отчёт: что сделано, что не получилось
4. Если не уверен — спрашиваю, не гадаю
5. Пишу код, который можно запустить "из коробки"
