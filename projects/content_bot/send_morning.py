#!/usr/bin/env python3
"""Одноразовый скрипт для отправки утреннего поста в digital канал."""
import sys
sys.path.insert(0, '/root/.openclaw/workspace-neuro/projects/content_bot')

# Импортируем нужные функции из bot.py
from bot import CHANNELS, CRON_TEMPLATES, format_post, send_message, add_reactions_footer

digital_channel = CHANNELS["digital"]
template = CRON_TEMPLATES["morning"]["digital"]

text_with_reactions = add_reactions_footer(template, "digital")
formatted = format_post(text_with_reactions, "digital")

print(f"Отправляю в {digital_channel['name']} (id: {digital_channel['chat_id']})")
print("=" * 40)
print(formatted[:200])
print("=" * 40)

result = send_message(digital_channel["chat_id"], formatted)
if result and result.get("ok"):
    print("✅ Утренний пост отправлен в digital канал!")
else:
    print(f"❌ Ошибка: {result}")
    sys.exit(1)
