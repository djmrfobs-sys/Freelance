"""
Demo Telegram Bot — парсинг URL и выдача результатов
Стек: Python, requests, BeautifulSoup4, SQLite, openpyxl
Без фреймворков — работает на чистом Telegram Bot API
"""

import requests
import sqlite3
import os
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import openpyxl

TOKEN = "8547512810:AAGlNvWdI_V01bWrzOr6BjTPJ6Kts4Fw584"
API_BASE = f"https://api.telegram.org/bot{TOKEN}"
DB_FILE = "data.db"
EXCEL_FILE = "result.xlsx"

# Инициализация БД
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
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


def send_message(chat_id, text, parse_mode=None):
    """Отправить сообщение в Telegram"""
    url = f"{API_BASE}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")


def send_document(chat_id, file_path, caption=""):
    """Отправить файл в Telegram"""
    url = f"{API_BASE}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, data=data, files=files, timeout=30)
    except Exception as e:
        print(f"Send doc error: {e}")


def parse_url(url: str) -> list[dict]:
    """Парсинг страницы: собирает заголовки"""
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
    except Exception as e:
        return [{"error": str(e)}]

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 3:
            results.append({"title": text[:200], "price": "—"})
            if len(results) >= 10:
                break
    return results if results else [{"title": "Контент не найден", "price": "—"}]


def save_to_excel(data: list[dict]):
    """Сохранить результаты в Excel"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Результаты"
    ws.append(["Название", "Цена"])
    for row in data:
        ws.append([row.get("title", ""), row.get("price", "")])
    wb.save(EXCEL_FILE)


def get_updates(offset=None):
    """Получить новые сообщения от Telegram"""
    url = f"{API_BASE}/getUpdates"
    data = {"timeout": 30, "offset": offset}
    try:
        resp = requests.post(url, data=data, timeout=35)
        return resp.json().get("result", [])
    except:
        return []


def handle_message(chat_id, text, user_id):
    """Обработка входящего сообщения"""
    text = text.strip()

    if text == "/start":
        send_message(chat_id,
            "👋 Привет! Я бот-парсер.\n\n"
            "Просто отправь мне ссылку на сайт, и я соберу данные.\n"
            "Команды:\n"
            "/start — это сообщение\n"
            "/history — история твоих запросов")
        return

    if text == "/history":
        cursor.execute(
            "SELECT url, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,)
        )
        rows = cursor.fetchall()
        if not rows:
            send_message(chat_id, "📭 История пуста.")
            return
        msg = "📋 Последние запросы:\n\n"
        for url, dt in rows:
            msg += f"• {url[:50]}... ({dt})\n"
        send_message(chat_id, msg)
        return

    if not text.startswith("http"):
        send_message(chat_id, "❌ Отправь ссылку (начинается с http:// или https://)")
        return

    send_message(chat_id, "🔍 Парсю данные... подожди пару секунд")

    data = parse_url(text)

    if "error" in data[0]:
        send_message(chat_id, f"❌ Ошибка: {data[0]['error']}")
        return

    # Сохраняем в БД
    now = datetime.now().isoformat()
    for item in data[:5]:
        cursor.execute(
            "INSERT INTO history (user_id, url, title, price, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, text, item.get("title", ""), item.get("price", ""), now)
        )
    conn.commit()

    # Сохраняем в Excel
    save_to_excel(data)

    # Превью
    preview = "📄 **Результаты парсинга:**\n\n"
    for i, item in enumerate(data[:5], 1):
        preview += f"{i}. {item.get('title', '—')}\n"
    if len(data) > 5:
        preview += f"\n...и ещё {len(data) - 5} позиций"

    send_message(chat_id, preview)
    send_document(chat_id, EXCEL_FILE, "✅ Готово! Файл с результатами.")


def main():
    print("🤖 Бот запущен! Ожидание сообщений...")
    last_update_id = 0

    while True:
        try:
            updates = get_updates(offset=last_update_id + 1)
            for update in updates:
                last_update_id = update.get("update_id", last_update_id)

                msg = update.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                if text:
                    print(f"[{datetime.now().isoformat()}] {user_id}: {text[:50]}")
                    handle_message(chat_id, text, user_id)

        except KeyboardInterrupt:
            print("\n⏹ Бот остановлен")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
