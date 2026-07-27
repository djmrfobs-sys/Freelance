#!/usr/bin/env python3
"""
@Nigt_help_bot — бот для публикации постов в Telegram-каналы KISELEVY CREO
Принимает текст + фото от Артура, отправляет в каналы с соблюдением правил
"""

import requests
import json
import datetime
import os
import sys
import time
import re

TOKEN = "8547512810:AAGlNvWdI_V01bWrzOr6BjTPJ6Kts4Fw584"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Каналы
CHANNELS = {
    "digital": {
        "chat_id": -1004292661967,
        "name": "@kiselevy_creo_digital",
        "desc": "AI, автоматизация, вайбкодинг"
    },
    "mantra": {
        "chat_id": -1003710808648,
        "name": "@ecstatic_dance_mantra",
        "desc": "мантры, экстатик дэнс, духовность"
    }
}

# ID Артура
ARTHUR_ID = 199790247

# ========== Правила форматирования ==========

def format_post(text, channel="digital"):
    """Форматирует пост под правила канала"""
    # Убираем лишние пробелы в начале/конце строк
    text = text.strip()
    
    # Длинное тире → короткое
    text = text.replace("—", "–").replace("―", "–")
    
    # Двойные пробелы → одиночные
    text = re.sub(r'  +', ' ', text)
    
    # Пустые строки больше одной → одна
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text


def validate_post(text):
    """Проверяет пост на соответствие правилам"""
    errors = []
    
    if not text or len(text.strip()) < 10:
        errors.append("Пост слишком короткий (< 10 символов)")
    
    # Проверка на длинное тире
    if "—" in text or "―" in text:
        errors.append("Найдено длинное тире (—), заменил на короткое (–)")
    
    # Проверка на двойные пробелы
    if re.search(r'  ', text):
        errors.append("Найдены двойные пробелы")
    
    return errors


# ========== Telegram API ==========

def send_message(chat_id, text, parse_mode="Markdown"):
    """Отправить текстовое сообщение"""
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Send error: {e}")
        return None


def send_photo(chat_id, photo_path, caption="", parse_mode="Markdown"):
    """Отправить фото с подписью"""
    url = f"{API_URL}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": parse_mode}
            r = requests.post(url, data=data, files=files, timeout=30)
            return r.json()
    except Exception as e:
        print(f"Send photo error: {e}")
        return None


def send_chat_action(chat_id, action="typing"):
    try:
        requests.post(f"{API_URL}/sendChatAction", json={"chat_id": chat_id, "action": action}, timeout=5)
    except:
        pass


def get_updates(offset=None):
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []


def download_photo(file_id):
    """Скачать фото из Telegram"""
    r = requests.get(f"{API_URL}/getFile", params={"file_id": file_id}, timeout=10)
    result = r.json()
    file_path = result.get("result", {}).get("file_path", "")
    if not file_path:
        return None
    
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None
    
    ext = file_path.split(".")[-1] if "." in file_path else "jpg"
    tmp = f"/tmp/post_photo_{int(time.time())}.{ext}"
    with open(tmp, "wb") as f:
        f.write(r.content)
    return tmp


# ========== Обработка команд ==========

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    user_id = msg.get("from", {}).get("id")
    
    # Только Артур может постить
    if user_id != ARTHUR_ID:
        if text:
            send_message(chat_id, "⛔ Этот бот только для Артура.")
        return
    
    # Команды
    if text == "/start":
        send_message(chat_id,
            "📝 *Content Poster*\n\n"
            "Я принимаю твои посты и отправляю в каналы.\n\n"
            "📌 *Команды:*\n"
            "/digital текст — пост в @kiselevy_creo_digital\n"
            "/mantra текст — пост в @ecstatic_dance_mantra\n"
            "/both текст — пост в оба канала\n"
            "Также можно просто отправить текст, и я спрошу куда.\n\n"
            "📸 Если хочешь с фото: отправь фото с подписью.\n"
            "   Команда в подписи укажет канал.\n\n"
            "⚠️ Правила постов соблюдаются автоматически:\n"
            "– короткие тире\n"
            "– монохромные эмодзи\n"
            "– без ошибок")
        return
    
    if text == "/channels":
        info = "📡 *Доступные каналы:*\n\n"
        for key, ch in CHANNELS.items():
            info += f"• {ch['name']} — {ch['desc']}\n"
            info += f"  Команда: `/{key} текст поста`\n\n"
        send_message(chat_id, info)
        return
    
    if text == "/test":
        # Тестовая отправка в оба канала
        test_msg = "🧪 *Тест бота*\n\nЕсли ты это видишь — бот работает! – KISELEVY CREO"
        for key, ch in CHANNELS.items():
            r = send_message(ch["chat_id"], test_msg)
            status = "✅" if r and r.get("ok") else "❌"
            print(f"Test to {ch['name']}: {status}")
        send_message(chat_id, "✅ Тест отправлен в оба канала. Проверь.")
        return
    
    # Обработка фото
    if "photo" in msg:
        handle_photo(msg)
        return
    
    if not text:
        return
    
    # Определяем канал и текст из команды
    channel_keys = []
    if text.startswith("/digital"):
        post_text = text[9:].strip()
        channel_keys = ["digital"]
    elif text.startswith("/mantra"):
        post_text = text[8:].strip()
        channel_keys = ["mantra"]
    elif text.startswith("/both"):
        post_text = text[6:].strip()
        channel_keys = ["digital", "mantra"]
    else:
        # Без команды — спрашиваем куда
        # Сохраняем сообщение и отвечаем
        post_text = text
        ask_destination(chat_id, text)
        return
    
    if not post_text:
        send_message(chat_id, "❌ Напиши текст после команды. Пример:\n`/digital Привет, мир!`")
        return
    
    publish_post(chat_id, post_text, channel_keys)


def handle_photo(msg):
    """Обработка фото с подписью"""
    chat_id = msg.get("chat", {}).get("id")
    caption = msg.get("caption", "").strip()
    
    if not caption:
        send_message(chat_id, "📸 Фото без текста. Напиши подпись к фото с указанием канала:\n`/digital текст` или `/mantra текст`")
        return
    
    # Скачиваем фото
    photos = msg["photo"]
    best = photos[-1]
    file_id = best["file_id"]
    file_path = download_photo(file_id)
    
    if not file_path:
        send_message(chat_id, "❌ Не смог скачать фото.")
        return
    
    # Определяем канал и текст из подписи
    channel_keys = []
    if caption.startswith("/digital"):
        post_text = caption[9:].strip()
        channel_keys = ["digital"]
    elif caption.startswith("/mantra"):
        post_text = caption[8:].strip()
        channel_keys = ["mantra"]
    elif caption.startswith("/both"):
        post_text = caption[6:].strip()
        channel_keys = ["digital", "mantra"]
    else:
        post_text = caption
        channel_keys = ["digital", "mantra"]  # по умолчанию в оба
    
    if not post_text:
        send_message(chat_id, "❌ Напиши текст к фото.")
        try:
            os.unlink(file_path)
        except:
            pass
        return
    
    # Отправляем
    success_count = 0
    for key in channel_keys:
        ch = CHANNELS[key]
        formatted = format_post(post_text, key)
        r = send_photo(ch["chat_id"], file_path, formatted)
        if r and r.get("ok"):
            success_count += 1
            print(f"✅ Фото отправлено в {ch['name']}")
        else:
            print(f"❌ Ошибка отправки в {ch['name']}: {r}")
    
    # Отвечаем Артуру
    if success_count == len(channel_keys):
        names = " + ".join([CHANNELS[k]["name"] for k in channel_keys])
        send_message(chat_id, f"✅ *Пост с фото отправлен в {names}*")
    elif success_count > 0:
        send_message(chat_id, f"⚠️ Частично отправлено ({success_count}/{len(channel_keys)})")
    else:
        send_message(chat_id, "❌ Не удалось отправить пост. Ошибка на сервере.")
    
    # Удаляем временный файл
    try:
        os.unlink(file_path)
    except:
        pass


def ask_destination(chat_id, text):
    """Если текст без команды — спрашиваем куда отправить"""
    # Показываем, что текст получен, но нужна команда
    send_message(chat_id,
        "✏️ *Текст получен.*\n\n"
        "Куда отправить?\n"
        f"`/digital` — {CHANNELS['digital']['name']}\n"
        f"`/mantra` — {CHANNELS['mantra']['name']}\n"
        f"`/both` — в оба\n\n"
        "Просто отправь команду, и я опубликую:\n"
        f"`/digital {text[:50]}...`")


def publish_post(chat_id, text, channel_keys, photo_path=None):
    """Опубликовать пост в указанные каналы"""
    
    # Форматируем
    for key in channel_keys:
        formatted = format_post(text, key)
        
        # Проверяем
        errors = validate_post(formatted)
        warn = ""
        if errors:
            warn = "\n⚠️ " + "\n".join(errors)
        
        # Отправляем
        if photo_path:
            r = send_photo(CHANNELS[key]["chat_id"], photo_path, formatted)
        else:
            r = send_message(CHANNELS[key]["chat_id"], formatted)
        
        status = "✅" if r and r.get("ok") else "❌"
        print(f"{status} {CHANNELS[key]['name']}: {formatted[:50]}...")
    
    # Ответ Артуру
    names = " + ".join([CHANNELS[k]["name"] for k in channel_keys])
    send_message(chat_id, f"✅ *Пост опубликован в {names}*{warn}" if warn else f"✅ *Пост опубликован в {names}*")


# ========== Главный цикл ==========

def main():
    STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_state.json")
    LAST_UPDATE_ID = None
    
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
                LAST_UPDATE_ID = state.get("last_update_id")
        except:
            pass
    
    print(f"🤖 Content Poster (Nigt_help_bot) запущен — {datetime.datetime.now()}")
    
    # Тестовое сообщение Артуру
    send_message(ARTHUR_ID,
        "📝 *Content Poster перезапущен!*\n\n"
        "Теперь я умею:\n"
        "• `/digital текст` — пост в @kiselevy_creo_digital\n"
        "• `/mantra текст` — пост в @ecstatic_dance_mantra\n"
        "• `/both текст` — в оба канала\n"
        "• Фото с подписью — тоже работает\n\n"
        "Напиши /test — проверю связь с каналами.")
    
    while True:
        try:
            updates = get_updates(offset=LAST_UPDATE_ID)
            for update in updates:
                if "message" in update:
                    try:
                        handle_message(update["message"])
                    except Exception as e:
                        print(f"❌ Handle error: {e}")
                if update.get("update_id", 0) >= (LAST_UPDATE_ID or 0):
                    LAST_UPDATE_ID = update["update_id"] + 1
            
            if LAST_UPDATE_ID:
                with open(STATE_FILE, "w") as f:
                    json.dump({"last_update_id": LAST_UPDATE_ID}, f)
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("⏹ Остановлен.")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
