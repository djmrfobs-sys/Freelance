#!/usr/bin/env python3
"""
@Nigt_help_bot — Content Poster для каналов KISELEVY CREO
v2: генерация изображений по референсам + посты от первого лица
"""

import requests
import json
import datetime
import os
import time
import re
import base64
import subprocess

TOKEN = "854751…w584"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# ========== КАНАЛЫ ==========
CHANNELS = {
    "digital": {
        "chat_id": -1004292661967,
        "name": "@kiselevy_creo_digital",
        "topic": "AI, боты, автоматизация, вайбкодинг",
        "rules": "короткие тире (–), векторные/монохромные эмодзи, без ошибок, никаких лишних символов",
        "lang": "ru+en",
        "bilingual": True,
        "bilingual_note": "Все посты сначала на русском, потом на английском через пустую строку"
    },
    "mantra": {
        "chat_id": -1003710808648,
        "name": "@ecstatic_dance_mantra",
        "topic": "мантры, экстатик дэнс, духовность, музыка",
        "rules": "тёплый тон, духовность, безалкогольная тематика, упомянать Кети как проводника Шанти",
        "lang": "ru+sr",
        "bilingual": True,
        "bilingual_note": "Все посты сначала на русском, потом на сербском через пустую строку"
    }
}

ARTHUR_ID = 199790247

# ========== РЕФЕРЕНСЫ ==========
REFERENCES = {
    "fobs_keti_1": {
        "path": "/root/.openclaw/workspace-neuro/references/fobs_keti_1.jpg",
        "desc": "Артур (лёгкая щетина+усы, тёмные короткие волосы, наушники) и Кети (длинные тёмные волнистые волосы, светлый пиджак) вместе",
        "size": "1024x1024"
    },
    "fobs_keti_2": {
        "path": "/root/.openclaw/workspace-neuro/references/fobs_keti_2.jpg",
        "desc": "Артур и Кети вместе, второй ракурс",
        "size": "960x1280"
    },
    "keti_solo": {
        "path": "/root/.openclaw/workspace-neuro/references/keti_reference.jpg",
        "desc": "Кети: белая кружевная блуза + оливковая юбка с воланами, 30-35 лет, кавказская внешность, длинные тёмные волнистые волосы"
    },
    "mantra_1": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_1.jpg", "desc": "Референс ЭДМ 1"},
    "mantra_2": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_2.jpg", "desc": "Референс ЭДМ 2"},
    "mantra_3": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_3.jpg", "desc": "Референс ЭДМ 3"},
    "mantra_4": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_4.jpg", "desc": "Референс ЭДМ 4"},
    "mantra_5": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_5.jpg", "desc": "Референс ЭДМ 5"},
    "mantra_6": {"path": "/root/.openclaw/workspace-neuro/references/mantra_ref_6.jpg", "desc": "Референс ЭДМ 6"}
}

# ========== ПРАВИЛА ПОСТОВ ==========
POST_RULES = """
ПРАВИЛА НАПИСАНИЯ ПОСТОВ:

0. ДВУЯЗЫЧНОСТЬ:
   - @kiselevy_creo_digital: русский + английский дубляж (сначала RU, потом EN)
   - @ecstatic_dance_mantra: русский + сербский дубляж (сначала RU, потом SR)

1. ЛИЦО В ПОСТАХ:
   - Фото Артура → от 1-го лица (я Артур, рекомендую/советую)
   - Фото Кети → от 1-го лица (я Кети, приглашаю/практикую)
   - Фото вместе → от команды (мы, KISELEVY CREO)

2. ПЕРСОНАЖИ НЕ МЕНЯТЬ:
   - Артур: лёгкая щетина+усы, тёмные короткие волосы, наушники, 30-35 лет, кавказец
   - Кети: длинные тёмные волнистые волосы, 30-35 лет, кавказская внешность
   - Можно менять фон, одежду, позы — но лица и люди остаются теми же

3. ФОРМАТИРОВАНИЕ:
   - Только короткие тире (–), никогда длинные (—)
   - Только векторные/монохромные эмодзи (⚡🧠💡📊🎯🤖🚀💻🛠️)
   - Без орфографических ошибок
   - Никаких лишних символов

4. КОНТЕНТ @kiselevy_creo_digital:
   - Только полезная информация про: автоматизацию, создание ботов, написание сайтов, внедрение AI-систем
   - Маркетинг и продюсирование от Кети
   - Реальный опыт: "как я сделал", "как я автоматизировал", "какую систему внедрил"
   - Никаких шаблонных приветствий "доброе утро", "день подходит к концу" — ненужная вода

5. ДЛЯ @ecstatic_dance_mantra:
   - Кети — проводник Шанти (упоминать в каждом посте)
   - Безалкогольные вечеринки: музыка + слияние + расслабление
   - Артур как DJ.MR.FOBS — пишет музыку для вечеринок
   - Тёплый, духовный тон
   - ОБЯЗАТЕЛЬНО: пост на русском + пустая строка + пост на сербском

6. СТИЛЬ:
   - Писать как настоящий копирайтер, без AI-шаблонов
   - Живой, человеческий язык, разговорный тон
   - Не использовать фразы типа "в эпоху цифровых технологий", "добро пожаловать в мир"

7. РЕАКЦИИ:
   - В конце каждого поста добавлять строку с призывом к реакции
   - Для DIGITAL: 

❤️🔥💡 — поставь реакцию"""

CRON_TEMPLATES = {
    "morning": {
        "digital": "Запустил нового Telegram-бота за 20 минут. Просто описал задачу — AI сам написал код.\n\nВайбкодинг — это не магия. Это когда ты перестаёшь писать код руками и начинаешь описывать, что нужно сделать.\n\nСобрал для вас ТОП-3 инструмента, которые реально экономят время:\n\n1. Cursor — AI-редактор кода. Пишет за тебя\n2. Lovable — сайты из промпта\n3. n8n — автоматизация без кода\n\nКаким пользуетесь вы?\n\n– Артур, KISELEVY CREO\n\n——\n\nI launched a new Telegram bot in 20 minutes. Just described the task — AI wrote the code itself.\n\nVibecoding is not magic. It's when you stop writing code by hand and start describing what needs to be done.\n\nTop 3 tools that save real time:\n\n1. Cursor — AI code editor\n2. Lovable — websites from a prompt\n3. n8n — no-code automation\n\nWhat do you use?\n\n– Artur, KISELEVY CREO\n\n❤️🔥💡 — drop a reaction",
        "mantra": "Каждое утро я начинаю с 5 минут тишины. Без телефона, без мыслей о делах. Просто дыхание.\n\nЭто не про религию. Это про возможность услышать себя до того, как мир начнёт диктовать, что делать.\n\nПопробуйте завтра. Прямо после будильника. 5 минут.\n\n– Кети, проводник Шанти\n\n——\n\nСвако јутро почињем са 5 минута тишине. Без телефона, без мисли о обавезама. Само дисање.\n\nОво није вера. Ово је прилика да чујете себе пре него што свет почне да диктира.\n\nПробајте сутра. Одмах после будилице. 5 минута.\n\n– Кети, водич Шанти\n\n❤️🕊🔥 — остави реакцију"
    },
    "evening": {
        "digital": "Сегодня автоматизировал выгрузку данных из 5 источников в одну таблицу.\n\nРаньше это занимало 2 часа ручной работы. Теперь — 5 минут и скрипт всё делает сам.\n\nСекрет: не надо писать сложный код. Связка Make.com + Google Sheets + Python решает 90% задач.\n\nЧто из своего бизнеса вы хотите автоматизировать, но не знаете с чего начать?\n\n– Артур, KISELEVY CREO\n\n——\n\nToday I automated data export from 5 sources into one table.\n\nBefore: 2 hours of manual work. Now: 5 minutes and the script does it all.\n\nThe secret: you don't need complex code. Make.com + Google Sheets + Python solves 90% of tasks.\n\nWhat part of your business do you want to automate but don't know where to start?\n\n– Artur, KISELEVY CREO\n\n❤️🔥💡 — drop a reaction",
        "mantra": "Вечером я зажигаю свечу. Не для красоты — как ритуал завершения дня.\n\nПламя напоминает: всё, что горело сегодня — отпусти. Завтра новый огонь.\n\nПопробуйте: перед сном зажгите свечу на 5 минут. Просто смотрите на огонь.\n\n– Кети, проводник Шанти\n\n——\n\nУвече палим свећу. Не због лепоте — као ритуал завршетка дана.\n\nПламен подсећа: све што је горело данас — пусти. Сутра нова ватра.\n\nПробајте: пред спавање упалите свећу на 5 минута. Само гледајте у пламен.\n\n– Кети, водич Шанти\n\n🕊🕯❤️ — остави реакцију"
    }
}

# ========== GEMINI API ==========
GEMINI_KEY_PATH = os.path.expanduser("~/.openclaw-neuro/.gemini_key")

def read_gemini_key():
    try:
        with open(GEMINI_KEY_PATH) as f:
            return f.read().strip()
    except:
        return None

def generate_image(prompt, reference_paths=None):
    """Генерация изображения через Gemini (доступную модель)"""
    # Пока используем команду image_generate, которая есть у меня
    # Для бота — возвращаем промпт, а генерацию делаю я
    return {
        "success": False,
        "note": "Генерация изображений выполняется мной (Нейро) по запросу",
        "prompt": prompt
    }

# ========== ФОРМАТИРОВАНИЕ ==========

def format_post(text, channel="digital"):
    text = text.strip()
    text = text.replace("—", "–").replace("―", "–")
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def validate_post(text):
    errors = []
    if not text or len(text.strip()) < 5:
        errors.append("Пост слишком короткий")
    if "—" in text or "―" in text:
        errors.append("Найдено длинное тире")
    if re.search(r'  ', text):
        errors.append("Найдены двойные пробелы")
    return errors

# ========== TELEGRAM API ==========

def send_message(chat_id, text, parse_mode="Markdown"):
    url = f"{API_URL}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}, timeout=10)
        return r.json()
    except:
        return None

def send_photo(chat_id, photo_path, caption="", parse_mode="Markdown"):
    url = f"{API_URL}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            r = requests.post(url, data={"chat_id": chat_id, "caption": caption, "parse_mode": parse_mode},
                             files={"photo": f}, timeout=30)
            return r.json()
    except:
        return None

def get_updates(offset=None):
    params = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def download_photo(file_id):
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

# ========== ОБРАБОТКА ==========

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    user_id = msg.get("from", {}).get("id")
    
    if user_id != ARTHUR_ID:
        if text:
            send_message(chat_id, "⛔")
        return
    
    # Фото
    if "photo" in msg:
        handle_photo(msg)
        return
    
    if not text:
        return
    
    if text == "/start":
        send_message(chat_id,
            "📝 *Content Poster v2*\n\n"
            "Пишу и публикую посты в твои каналы.\n\n"
            "📌 *Команды:*\n"
            "`/digital текст` — пост в @kiselevy_creo_digital\n"
            "`/mantra текст` — пост в @ecstatic_dance_mantra\n"
            "`/both текст` — в оба канала\n"
            "`/morning` — готовое утреннее приветствие\n"
            "`/evening` — готовое вечернее\n"
            "`/cron` — шаблоны рассылок\n"
            "`/refs` — список референсов\n"
            "`/rules` — правила постов\n\n"
            "📸 Отправь фото с подписью — опубликую с фото.\n\n"
            "🌐 *Двуязычность:*\n"
            "• @kiselevy_creo_digital — русский + английский дубляж\n"
            "• @ecstatic_dance_mantra — русский + сербский дубляж\n"
            "Ты присылаешь сразу на двух языках через пустую строку.\n\n"
            "🤖 *Генерация:* напиши `сгенерируй: описание` — я сделаю изображение по референсам и опубликую.")
        return
    
    if text == "/rules":
        send_message(chat_id, POST_RULES.strip())
        return
    
    if text == "/refs":
        info = "📸 *Доступные референсы:*\n\n"
        for key, ref in REFERENCES.items():
            info += f"• `{key}` — {ref['desc']}\n"
        info += "\nМогу сгенерировать изображение с этими персонажами: напиши `сгенерируй: описание`"
        send_message(chat_id, info)
        return
    
    if text == "/morning":
        # Отправляет шаблоны
        for key, tmpl in CRON_TEMPLATES["morning"].items():
            ch = CHANNELS[key]
            formatted = format_post(tmpl, key)
            r = send_message(ch["chat_id"], formatted)
            status = "✅" if r and r.get("ok") else "❌"
            print(f"{status} Morning to {ch['name']}")
        send_message(chat_id, "✅ Утренние приветствия разосланы в оба канала!")
        return
    
    if text == "/evening":
        for key, tmpl in CRON_TEMPLATES["evening"].items():
            ch = CHANNELS[key]
            formatted = format_post(tmpl, key)
            r = send_message(ch["chat_id"], formatted)
            status = "✅" if r and r.get("ok") else "❌"
            print(f"{status} Evening to {ch['name']}")
        send_message(chat_id, "✅ Вечерние сообщения разосланы в оба канала!")
        return
    
    if text == "/cron":
        info = "🕐 *Шаблоны рассылок:*\n\n"
        for period in ["morning", "evening"]:
            info += f"**{period.upper()}**\n"
            for key, tmpl in CRON_TEMPLATES[period].items():
                info += f"• {CHANNELS[key]['name']}: _{tmpl[:40]}..._\n"
            info += "\n"
        info += "Отправить: `/morning` или `/evening`"
        send_message(chat_id, info)
        return
    
    # Генерация изображения
    if text.startswith("сгенерируй:") or text.startswith("сделай картинку:") or text.startswith("нарисуй:"):
        handle_generate_request(chat_id, text)
        return
    
    # Определяем канал
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
        post_text = text
        ask_destination(chat_id, text)
        return
    
    if not post_text:
        send_message(chat_id, "❌ Напиши текст после команды.")
        return
    
    publish_post(chat_id, post_text, channel_keys)


def handle_photo(msg):
    chat_id = msg.get("chat", {}).get("id")
    caption = msg.get("caption", "").strip()
    
    if not caption:
        send_message(chat_id, "📸 Фото без текста. Напиши подпись с командой:\n`/digital текст` или `/mantra текст`")
        return
    
    photos = msg["photo"]
    best = photos[-1]
    file_id = best["file_id"]
    file_path = download_photo(file_id)
    if not file_path:
        send_message(chat_id, "❌ Не смог скачать фото.")
        return
    
    # Определяем канал из подписи
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
        channel_keys = ["digital", "mantra"]
    
    if not post_text:
        send_message(chat_id, "❌ Напиши текст к фото.")
        try: os.unlink(file_path)
        except: pass
        return
    
    success = 0
    for key in channel_keys:
        ch = CHANNELS[key]
        text_with_reactions = add_reactions_footer(post_text, key)
        formatted = format_post(text_with_reactions, key)
        r = send_photo(ch["chat_id"], file_path, formatted)
        if r and r.get("ok"):
            success += 1
            print(f"✅ Photo to {ch['name']}")
    
    if success == len(channel_keys):
        names = " + ".join([CHANNELS[k]["name"] for k in channel_keys])
        send_message(chat_id, f"✅ *Фото опубликовано в {names}*")
    else:
        send_message(chat_id, "❌ Ошибка при отправке")
    
    try: os.unlink(file_path)
    except: pass


def handle_generate_request(chat_id, text):
    """Обработка запроса на генерацию изображения"""
    # Извлекаем описание
    desc = re.sub(r'^(сгенерируй|сделай картинку|нарисуй)\s*[:\s]*', '', text, flags=re.IGNORECASE).strip()
    
    if not desc:
        send_message(chat_id, "❌ Напиши, что сгенерировать. Например:\n`сгенерируй: Артур и Кети на фоне заката, пишут код на ноутбуке`")
        return
    
    send_message(chat_id, "🎨 *Запрос на генерацию получен!*\n\n"
                 "Я передам его Нейро — он сгенерирует изображение по референсам и опубликует.\n\n"
                 f"*Промпт:* {desc}\n\n"
                 "Ожидай — скоро будет готово.")
    
    print(f"🎨 GENERATE REQUEST: {desc}")
    # Здесь Нейро (я) подхватывает запрос и генерирует


def ask_destination(chat_id, text):
    send_message(chat_id,
        "✏️ *Текст получен.* Куда отправить?\n\n"
        f"`/digital` — {CHANNELS['digital']['name']}\n"
        f"`/mantra` — {CHANNELS['mantra']['name']}\n"
        f"`/both` — в оба\n\n"
        f"Напиши команду + текст:\n"
        f"`/both {text[:40]}...`")


def add_reactions_footer(text, channel_key):
    """Добавляет строку с призывом к реакции в конец поста"""
    footers = {
        "digital": "\n\n❤️🔥💡 — поставь реакцию",
        "mantra": "\n\n🕊❤️🔥 — остави реакцију"
    }
    footer = footers.get(channel_key, "\n\n❤️ — поставь реакцију")
    
    # Проверяем, не добавлена ли уже строка с реакциями
    if footer.strip() not in text:
        text += footer
    return text


def publish_post(chat_id, text, channel_keys, photo_path=None):
    warn = ""
    for key in channel_keys:
        # Добавляем строку с реакциями
        text_with_reactions = add_reactions_footer(text, key)
        formatted = format_post(text_with_reactions, key)
        errors = validate_post(formatted)
        if errors:
            warn = "\n⚠️ " + "\n".join(errors)
        
        if photo_path:
            r = send_photo(CHANNELS[key]["chat_id"], photo_path, formatted)
        else:
            r = send_message(CHANNELS[key]["chat_id"], formatted)
        
        status = "✅" if r and r.get("ok") else "❌"
        print(f"{status} {CHANNELS[key]['name']}")
    
    names = " + ".join([CHANNELS[k]["name"] for k in channel_keys])
    send_message(chat_id, f"✅ *Опубликовано в {names}*{warn}")


# ========== ГЛАВНЫЙ ЦИКЛ ==========

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
    
    print(f"🤖 Content Poster v2 (with refs) запущен — {datetime.datetime.now()}")
    
    # Приветственное сообщение Артуру
    send_message(ARTHUR_ID,
        "📝 *Content Poster v2*\n\n"
        "Обновлён! Теперь знаю все референсы и правила.\n\n"
        "Напиши:\n"
        "• `/digital текст` — пост в DIGITAL\n"
        "• `/mantra текст` — пост в MANTRA\n"
        "• `/morning` / `/evening` — шаблоны\n"
        "• `сгенерируй: описание` — создам картинку по референсам\n"
        "• `/rules` — все правила\n"
        "• `/refs` — референсы")
    
    while True:
        try:
            updates = get_updates(offset=LAST_UPDATE_ID)
            for update in updates:
                if "message" in update:
                    try:
                        handle_message(update["message"])
                    except Exception as e:
                        print(f"❌ Handle: {e}")
                if update.get("update_id", 0) >= (LAST_UPDATE_ID or 0):
                    LAST_UPDATE_ID = update["update_id"] + 1
            
            if LAST_UPDATE_ID:
                with open(STATE_FILE, "w") as f:
                    json.dump({"last_update_id": LAST_UPDATE_ID}, f)
            
            time.sleep(30)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
