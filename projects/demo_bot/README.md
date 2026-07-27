# Telegram Bot Parser (Demo)

Telegram-бот для парсинга сайтов с выдачей результатов в Excel.

## Возможности
- Принимает ссылку, парсит заголовки и цены
- Сохраняет историю запросов (SQLite)
- Выгружает результаты в Excel (.xlsx)
- Простая команда /history

## Установка и запуск

```bash
pip install -r requirements.txt
# Отредактируй bot.py — вставь свой токен в TOKEN
python bot.py
```

## Стек
- Python 3.11+
- aiogram 3
- BeautifulSoup4
- openpyxl
- SQLite
