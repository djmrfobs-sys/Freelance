#!/usr/bin/env python3
"""
Универсальный постинг в Telegram-каналы через Bot API.
Используется из cron-задач OpenClaw.

Аргументы:
  --channel digital|mantra
  --photo /path/to/photo.jpg (опционально)
  --text "текст поста"
  --text-file /path/to/text.txt (альтернатива --text)
"""

import requests
import sys
import os
import argparse
import json

TOKEN = os.environ.get("OPENCLAW_POSTER_BOT_TOKEN", "")
CHANNELS = {
    "digital": -1004292661967,
    "mantra": -1003710808648
}

def send_photo(chat_id, photo_path, caption, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(photo_path, "rb") as f:
        r = requests.post(url, 
            data={"chat_id": chat_id, "caption": caption, "parse_mode": parse_mode},
            files={"photo": f},
            timeout=30)
    return r.json()

def send_text(chat_id, text, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url,
        data={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
        timeout=10)
    return r.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True, choices=["digital", "mantra"])
    parser.add_argument("--photo", default=None)
    parser.add_argument("--text", default=None)
    parser.add_argument("--text-file", default=None)
    args = parser.parse_args()
    
    chat_id = CHANNELS[args.channel]
    
    if args.text_file:
        with open(args.text_file) as f:
            text = f.read().strip()
    else:
        text = args.text
    
    if not text:
        print("❌ Нет текста поста")
        sys.exit(1)
    
    if args.photo and os.path.exists(args.photo):
        result = send_photo(chat_id, args.photo, text)
    else:
        result = send_text(chat_id, text)
    
    if result.get("ok"):
        print(f"✅ Пост в @kiselevy_creo_{args.channel}")
    else:
        print(f"❌ Ошибка: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
