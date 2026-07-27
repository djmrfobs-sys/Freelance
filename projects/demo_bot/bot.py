"""
Demo Telegram Bot — парсинг URL и выдача результатов
Стек: aiogram 3, BeautifulSoup4, SQLite, openpyxl
"""

import asyncio
import sqlite3
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import requests
from bs4 import BeautifulSoup
import openpyxl

TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# DB init
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT,
        title TEXT,
        price TEXT,
        created_at TEXT
    )
""")
conn.commit()


def parse_url(url: str) -> list[dict]:
    """Простой парсер: собирает заголовки и цены со страницы"""
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
    except Exception as e:
        return [{"error": str(e)}]

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 3:
            results.append({"title": text[:200], "price": "—"})
            if len(results) >= 10:
                break
    return results if results else [{"title": "Контент не найден", "price": "—"}]


def save_to_excel(data: list[dict], filename: str = "result.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Результаты"
    ws.append(["Название", "Цена"])
    for row in data:
        ws.append([row.get("title", ""), row.get("price", "")])
    wb.save(filename)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я бот-парсер.\n\n"
        "Просто отправь мне ссылку на сайт, и я соберу данные.\n"
        "Команды:\n"
        "/start — это сообщение\n"
        "/history — история твоих запросов"
    )


@dp.message(Command("history"))
async def history(message: Message):
    cursor.execute(
        "SELECT url, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 5",
        (message.from_user.id,)
    )
    rows = cursor.fetchall()
    if not rows:
        await message.answer("История пуста.")
        return
    text = "📋 Последние запросы:\n\n"
    for url, dt in rows:
        text += f"• {url[:50]}... ({dt})\n"
    await message.answer(text)


@dp.message()
async def handle_url(message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("Пожалуйста, отправь ссылку (начинается с http:// или https://)")
        return

    await message.answer("🔍 Парсю данные... подожди пару секунд")

    data = parse_url(url)

    if "error" in data[0]:
        await message.answer(f"❌ Ошибка при парсинге: {data[0]['error']}")
        return

    # Save to DB
    now = datetime.now().isoformat()
    for item in data[:5]:
        cursor.execute(
            "INSERT INTO history (user_id, url, title, price, created_at) VALUES (?, ?, ?, ?, ?)",
            (message.from_user.id, url, item.get("title", ""), item.get("price", ""), now)
        )
    conn.commit()

    # Save to Excel
    save_to_excel(data)

    # Send preview
    preview = "📄 **Результаты парсинга:**\n\n"
    for i, item in enumerate(data[:5], 1):
        preview += f"{i}. {item.get('title', '—')}\n"
    if len(data) > 5:
        preview += f"\n...и ещё {len(data) - 5} позиций"
    preview += "\n\n📎 Файл Excel прикреплён ниже"

    await message.answer(preview)

    # Send Excel file
    excel_file = FSInputFile("result.xlsx")
    await message.answer_document(excel_file, caption="✅ Готово!")


async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
