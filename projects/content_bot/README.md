# Content Poster — Telegram-бот для постов в каналы

Бот публикует посты от Артура в Telegram-каналы KISELEVY CREO.

## Команды
- `/digital текст` — пост в @kiselevy_creo_digital
- `/mantra текст` — пост в @ecstatic_dance_mantra
- `/both текст` — пост в оба канала
- `/start` — справка
- `/channels` — список каналов
- `/test` — тестовая отправка

## Фичи
- Автоматическое форматирование (короткие тире, без двойных пробелов)
- Поддержка фото с подписью
- Валидация перед отправкой

## Стек
- Python 3, requests
- Telegram Bot API (polling)
