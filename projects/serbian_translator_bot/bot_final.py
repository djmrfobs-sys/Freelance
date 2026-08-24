#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сербско-русский бот-переводчик + голосовой ввод (Whisper) + озвучка (TTS).
- Текстовый перевод: серб<->рус (автоопределение языка)
- Голос: транскрипция Whisper (Groq) -> перевод
- /ru : рус->серб (голос: + озвучка сербским голосом)
- /sr : серб->рус
Запуск: python3 bot.py
"""

import os, io, time, re, logging, subprocess, tempfile, json, threading, datetime, sqlite3
import requests

# ------------------ Конфигурация ------------------
BASE = "/root/.openclaw/workspace-neuro"
with open(f"{BASE}/secrets/serbian_translator_bot.token") as f:
    TOKEN = f.read().strip()

GROQ_KEY = open(os.path.expanduser("~/.openclaw-neuro/.groq_key")).read().strip()
DEEPSEEK_KEY = open(os.path.expanduser("~/.openclaw-neuro/.deepseek_key")).read().strip()

API = f"https://api.telegram.org/bot{TOKEN}"
AUTHORIZED = {199790247, 5276541529}  # владелец (Артур) + супруга (Кети)

# -------- SQLite для истории диалога и логов определения языка --------
DB_PATH = os.path.join(os.path.dirname(__file__), "translator_history.db")
DB_LOCK = threading.Lock()

def init_db():
    """Инициализировать БД если её нет."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS dialog_history (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    role TEXT,
                    text TEXT,
                    ts TEXT
                )
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_id ON dialog_history(chat_id)
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS lang_detection_log (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    source TEXT,
                    input_text TEXT,
                    detected_lang TEXT,
                    confidence TEXT,
                    ts TEXT
                )
            """)
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"init_db err: {e}")

def save_dialog(chat_id, role, text):
    """Сохранить сообщение в историю диалога."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            ts = datetime.datetime.now().isoformat()
            c.execute(
                "INSERT INTO dialog_history (chat_id, role, text, ts) VALUES (?, ?, ?, ?)",
                (chat_id, role, text, ts)
            )
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"save_dialog err: {e}")

def get_dialog_history(chat_id, limit=12):
    """Получить последние N сообщений из истории диалога."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT role, text FROM dialog_history WHERE chat_id=? ORDER BY id DESC LIMIT ? ;",
                (chat_id, limit)
            )
            rows = c.fetchall()
            conn.close()
            return [{'role': r[0], 'text': r[1]} for r in reversed(rows)]
    except Exception as e:
        log.error(f"get_dialog_history err: {e}")
        return []

def log_lang_detection(chat_id, source, input_text, detected_lang, confidence=""):
    """Логировать решение определения языка (для дебага)."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            ts = datetime.datetime.now().isoformat()
            c.execute(
                "INSERT INTO lang_detection_log (chat_id, source, input_text, detected_lang, confidence, ts) VALUES (?, ?, ?, ?, ?, ?)",
                (chat_id, source, input_text[:100], detected_lang, confidence, ts)
            )
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"log_lang_detection err: {e}")

LAST_USER = {}
LAST_LOCK = threading.Lock()

def save_last_user(chat_id, text):
    with LAST_LOCK:
        LAST_USER[chat_id] = text

def get_last_user(chat_id):
    with LAST_LOCK:
        return LAST_USER.get(chat_id)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("srbot")

# -------- Retry-логика для API вызовов --------
def requests_get_retry(url, **kwargs):
    """requests.get() с retry-логикой: до 2 попыток с уменьшенным таймаутом."""
    max_retries = 2
    timeout = kwargs.get('timeout', 10)
    
    for attempt in range(max_retries):
        try:
            current_timeout = 10 if attempt > 0 else timeout
            kwargs['timeout'] = current_timeout
            return requests.get(url, **kwargs)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
            if attempt < max_retries - 1:
                log.warning(f"timeout на попытке {attempt+1}/{max_retries}, повтор с таймаутом {current_timeout}s: {url}")
                time.sleep(0.5)
                continue
            else:
                log.error(f"timeout после {max_retries} попыток: {url}")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                log.warning(f"ошибка на попытке {attempt+1}/{max_retries}, повтор: {e}")
                time.sleep(0.5)
                continue
            else:
                raise
    return None

def requests_post_retry(url, **kwargs):
    """requests.post() с retry-логикой: до 2 попыток с уменьшенным таймаутом."""
    max_retries = 2
    timeout = kwargs.get('timeout', 10)
    
    for attempt in range(max_retries):
        try:
            current_timeout = 10 if attempt > 0 else timeout
            kwargs['timeout'] = current_timeout
            return requests.post(url, **kwargs)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
            if attempt < max_retries - 1:
                log.warning(f"timeout на попытке {attempt+1}/{max_retries}, повтор с таймаутом {current_timeout}s: {url}")
                time.sleep(0.5)
                continue
            else:
                log.error(f"timeout после {max_retries} попыток: {url}")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                log.warning(f"ошибка на попытке {attempt+1}/{max_retries}, повтор: {e}")
                time.sleep(0.5)
                continue
            else:
                raise
    return None

# ------------------ Telegram helpers ------------------
def tg(method, **params):
    r = requests_post_retry(f"{API}/{method}", data=params, timeout=120)
    try:
        return r.json()
    except Exception:
        return {"ok": False}

def send_text(chat_id, text, reply_to=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    requests.post(f"{API}/sendMessage", data=data, timeout=60)

def send_text_with_button(chat_id, text, button_text, callback_data):
    """Текст + инлайн-кнопка."""
    keyboard = {"inline_keyboard": [[{"text": button_text, "callback_data": callback_data}]]}
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)}
    requests.post(f"{API}/sendMessage", data=data, timeout=60)

def send_voice(chat_id, voice_path, caption=None, reply_to=None):
    with open(voice_path, "rb") as f:
        files = {"voice": ("voice.ogg", f, "audio/ogg")}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        if reply_to:
            data["reply_to_message_id"] = reply_to
        requests.post(f"{API}/sendVoice", data=data, files=files, timeout=120)

def send_audio(chat_id, audio_path, reply_to=None):
    with open(audio_path, "rb") as f:
        files = {"audio": ("audio.ogg", f, "audio/ogg")}
        data = {"chat_id": chat_id}
        if reply_to:
            data["reply_to_message_id"] = reply_to
        requests.post(f"{API}/sendAudio", data=data, files=files, timeout=120)

# ------------------ Перевод (DeepSeek) ------------------
def transcribe_groq(audio_path):
    """Whisper через Groq."""
    data = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json", "language": "sr"}
    with open(audio_path, "rb") as f:
        r = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            data=data,
            files={"file": ("audio.ogg", f, "audio/ogg")},
            timeout=90,
        )
    if r.status_code != 200:
        return None, None, f"STT error {r.status_code}"
    d = r.json()
    text = d.get("text", "").strip()
    lang = d.get("language") or None
    return text, lang, None

def detect_lang_sr_ru(text, chat_id=None, source="text"):
    """Определение языка: сербский, русский или английский. Сербские маркеры ПЕРВЫМИ."""
    low = text.lower()
    s = set(t.lower() for t in text)
    letters = [c for c in text if c.isalpha()]
    words = {w.strip(". ,!?():;'\"-–—/").lower() for w in low.split()}

    sr_words_lat = {
        "kako", "sta", "šta", "sto", "što", "gde", "gdje", "kada", "kad", "kuda",
        "nije", "nema", "hvala", "dobro", "zdravo", "danas", "sutra", "sada", "uvek",
        "opet", "jos", "održ", "zato", "kroz", "preko", "dok", "ako", "sve",
        "oni", "ona", "mi", "vi", "nas", "vas", "se", "sam", "si", "smo", "ste", "su",
        "je", "bilo", "bio", "bila", "ovde", "tamo", "puno", "malo", "idem", "idemo",
        "dolazim", "volim", "zelim", "želim", "moram", "probam", "imate", "imam",
        "radim", "radimo", "znam", "znate", "lepo", "brzo", "polako", "recite",
        "reći", "pomoci", "pomoći", "potreban", "kupiti", "kupujem", "stize", "stiže",
        "dolazi", "zovem", "zovemo", "cemo", "ćemo", "necu", "neću", "posle", "pre",
        "vece", "veče", "dan", "jutro", "noc", "noć", "dobrodosli", "dobrodošli",
        "kako si", "kako ste", "prijatno", "izvoli", "izvolite", "moze", "može",
        "treba", "trebam", "zelim", "želim", "sta je", "shta", "shodno", "bas", "baš",
        "naravno", "svakako", "jedan", "dva", "tri", "voda", "hleb", "hrana", "kafa",
        "svuda", "samo", "jer", "ali", "pa", "li", "da", "ne", "evo", "eto",
    }
    sr_words_cyr = {
        "како", "хвала", "данас", "сутра", "добро", "здраво", "желим", "радим", "знам",
        "волим", "имам", "имате", "није", "нема", "све", "кроз", "сада", "овде", "пуно",
        "са", "је", "сам", "си", "смо", "сте", "су", "било", "био", "била",
        "добар", "веће", "дана", "добродошли", "пријатно", "молим", "изволи", "може",
        "треба", "један", "два", "три", "вода", "хлеб", "храна", "кафа", "само",
    }
    sr_spec_cyr = "љњџћђ"
    sr_lat_dia = ("š", "ž", "ć", "č", "đ", "nj", "lj", "dž")

    if words & (sr_words_lat | sr_words_cyr):
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "sr", "sr_word_match")
        return "sr"

    if s & set(sr_spec_cyr):
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "sr", "sr_special_cyrillic")
        return "sr"

    if any(m in low for m in sr_lat_dia):
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "sr", "sr_latin_diacritics")
        return "sr"

    ru_only = ("ъ", "ы", "э", "щ", "ё", "й", "ю", "я", "ц", "ш")
    if any(ch in s for ch in ru_only):
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "ru", "ru_special_letters")
        return "ru"

    ru_words = {
        "привет", "пока", "спасибо", "пожалуйста", "извините", "здравствуйте",
        "ночь", "утро", "день", "вечер", "ночью", "утром", "днём", "вечером",
        "люблю", "хочу", "могу", "надо", "нельзя", "можно", "нужно", "старший",
        "меньше", "больше", "хороший", "плохой", "красивый", "новый", "старый",
        "горячий", "холодный", "тёплый", "мягкий", "твёрдый", "русский", "родной",
    }
    if words & ru_words:
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "ru", "ru_word_match")
        return "ru"

    cyr_all = "абвгдежзийклмнопрстуфхцчшщъыьэюяљњџћђ"
    if letters:
        cyr_count = sum(1 for c in letters if c.lower() in cyr_all)
        cyr_ratio = cyr_count / len(letters)
        if cyr_ratio > 0.5:
            if chat_id:
                log_lang_detection(chat_id, source, text[:50], "ru", f"cyrillic_ratio_{cyr_ratio:.2f}")
            return "ru"

    en_words = {
        "the", "and", "is", "are", "i", "you", "to", "of", "it", "in", "that",
        "this", "with", "for", "on", "not", "my", "your", "hello", "hi", "please",
        "thank", "how", "what", "when", "where", "why", "dear", "can", "do", "have",
        "get", "need", "want", "good", "very", "really", "about", "from", "at", "by",
    }
    if words & en_words:
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "en", "en_word_match")
        return "en"

    if chat_id:
        log_lang_detection(chat_id, source, text[:50], "sr", "default_sr")
    return "sr"

def _now():
    """Текущие дата и время."""
    now = datetime.datetime.now()
    wd = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][now.weekday()]
    return now.strftime(f"%d.%m.%Y год | {wd} | %H:%M UTC")

def translate(text, source_lang, chat_id=None):
    """Перевод через DeepSeek."""
    if source_lang == "sr":
        target, src_hint = "русский", "сербского"
    elif source_lang == "en":
        target, src_hint = "русский", "английского"
    else:
        target, src_hint = "сербский", "русского"
    return translate_to(text, target, src_hint, chat_id=chat_id)

def translate_to(text, target, src_hint, chat_id=None, history=True):
    """Перевод на указанный язык."""
    system = (
        "Ты профессиональный переводчик. Сейчас реальный момент: " + _now() + ". "
        "Переведи последнее сообщение пользователя "
        f"с {src_hint} языка на {target} язык. "
        "ВАЖНО: верни ТОЛЬКО сам перевод на " + target + " языке, БЕЗ какого-либо русского текста, "
        "без пояснений, без кавычек-разметки, без заголовков. Первым же словом начинай перевод."
    )
    ctx = []
    if chat_id:
        for m in get_dialog_history(chat_id):
            role = "user" if m["role"] == "user" else "assistant"
            ctx.append({"role": role, "content": m["text"]})
    if not ctx:
        ctx.append({"role": "system", "content": system})
        ctx.append({"role": "user", "content": text})
    else:
        ctx.insert(0, {"role": "system", "content": system})
        ctx.append({"role": "user", "content": text})
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.deepseek.com", api_key=DEEPSEEK_KEY)
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=ctx,
            temperature=0.3,
            max_tokens=800,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"translate err: {e}")
        return f"[ошибка перевода: {e}]"

def tts_google(text, lang_code="sr"):
    """Озвучка через Google TTS с fallback."""
    url = "https://translate.google.com/translate_tts"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"ie": "UTF-8", "q": text[:200], "tl": lang_code, "client": "tw-ob"}
    
    for attempt in range(2):
        try:
            r = requests_get_retry(url, params=params, headers=headers, timeout=60)
            if r.status_code == 200 and len(r.content) >= 1000:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(r.content)
                    mp3 = f.name
                ogg = mp3.replace(".mp3", ".ogg")
                subprocess.run(["ffmpeg", "-y", "-i", mp3, "-filter:a", "atempo=0.85",
                                "-c:a", "libopus", "-b:a", "48k", ogg],
                               capture_output=True)
                os.unlink(mp3)
                return ogg if os.path.exists(ogg) else None
            elif attempt < 1:
                log.warning(f"tts_google: ответ маленький ({len(r.content)} байт), повтор...")
                time.sleep(1)
            else:
                log.error(f"tts_google: после 2 попыток <1000 байт")
                return None
        except Exception as e:
            log.error(f"tts_google err: {e}")
            return None
    return None

GEMINI_KEY = open(os.path.expanduser("~/.openclaw-neuro/.gemini_key")).read().strip()
GEMINI_OCR_MODEL = "gemini-3-flash-preview"

def ocr_image(image_path):
    """OCR через Gemini Vision."""
    import base64, json as _json
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        body = {
            "contents": [{"parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
                {"text": "Прочитай весь текст с этой фотографии дословно. Верни только распознанный текст, без пояснений, без перевода, без обрамления. Если текста нет — ответь одним словом: пусто"}
            ]}]
        }
        req = requests_post_retry(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_OCR_MODEL}:generateContent?key={GEMINI_KEY}",
            json=body, timeout=90)
        if req.status_code != 200:
            return None, f"OCR HTTP {req.status_code}: {req.text[:200]}"
        d = req.json()
        txt = ""
        try:
            parts_list = d["candidates"][0]["content"]["parts"]
            for p in parts_list:
                if isinstance(p, dict) and p.get("text"):
                    txt += p["text"]
        except Exception:
            txt = ""
        txt = (txt or "").strip()
        if not txt or txt.lower() == "пусто":
            return None, "Текст на фото не найден."
        return txt, None
    except Exception as e:
        return None, f"OCR ошибка: {e}"

def handle_text(chat_id, text):
    """Текстовый перевод."""
    lang = detect_lang_sr_ru(text, chat_id=chat_id, source="text")
    tr = translate(text, lang, chat_id=chat_id)
    if lang == "sr":
        flag = "🇷🇸 → 🇷🇺"
    elif lang == "en":
        flag = "🇬🇧 → 🇷🇺"
    else:
        flag = "🇷🇺 → 🇷🇸"
    save_dialog(chat_id, "user", text)
    save_dialog(chat_id, "assistant", tr)
    if lang == "ru":
        save_last_user(chat_id, text)
        send_text_with_button(chat_id, f"{flag}\n\n{tr}", "🇬🇧 Перевести на английский", "to_en")
    else:
        send_text(chat_id, f"{flag}\n\n{tr}", reply_to=None)

def handle_voice(chat_id, file_id, forced_mode=None):
    """Голосовой перевод."""
    send_text(chat_id, "🎙️ Распознаю и перевожу на русский...")
    try:
        fi = tg("getFile", file_id=file_id)
        if not fi.get("ok"):
            send_text(chat_id, "Не удалось получить файл 🙁")
            return
        path = fi["result"]["file_path"]
        data = requests_get_retry(f"https://api.telegram.org/file/bot{TOKEN}/{path}", timeout=60).content
        with tempfile.NamedTemporaryFile(suffix=".oga", delete=False) as f:
            f.write(data)
            raw = f.name
        audio = raw + ".ogg"
        subprocess.run(["ffmpeg", "-y", "-i", raw, "-c:a", "libopus", audio], capture_output=True)
        os.unlink(raw)

        text, wlang, err = transcribe_groq(audio)
        os.unlink(audio)
        if err or not text:
            send_text(chat_id, f"Не распознал голос: {err or 'пусто'} 🙁")
            return

        log.info(f"voice transcribe: wlang={wlang!r} text={text!r}")
        if wlang:
            wl = wlang.lower()
            if "serb" in wl or wl in ("sr",):
                lang = "sr"
            elif "eng" in wl or wl in ("en",):
                lang = "en"
            else:
                lang = "sr"
        else:
            lang = "sr"
        if lang != "ru":
            src_hint = "сербского" if lang == "sr" else "английского"
            tr = translate_to(text, "русский", src_hint, chat_id=None, history=False)
        else:
            tr = None
        save_dialog(chat_id, "user", text)
        if tr:
            save_dialog(chat_id, "assistant", tr)
        if lang == "en":
            flag = "🇬🇧 → 🇷🇺"
        elif lang == "sr":
            flag = "🇷🇸 → 🇷🇺"
        else:
            flag = "🇷🇺"
        if tr:
            out = f"🎙 <i>Распознано:</i> {text}\n\n{flag}\n<b>{tr}</b>"
        else:
            out = f"🎙 <i>Распознано (уже русский):</i> {text}\n\n{flag}\nТекст на русском - перевод не нужен."
        send_text(chat_id, out)
    except Exception as e:
        log.error(f"handle_voice err: {e}")
        send_text(chat_id, f"Ошибка обработки голоса: {e} 🙁")

def handle_photo(chat_id, file_id):
    """OCR + перевод фото."""
    try:
        fi = tg("getFile", file_id=file_id)
        if not fi.get("ok"):
            send_text(chat_id, "Не удалось получить фото 🙁")
            return
        path = fi["result"]["file_path"]
        data = requests_get_retry(f"https://api.telegram.org/file/bot{TOKEN}/{path}", timeout=120).content
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(data)
            img = f.name
        send_text(chat_id, "🔎 Распознаю текст на фото...")
        text, err = ocr_image(img)
        os.unlink(img)
        if err or not text:
            send_text(chat_id, f"{err or 'Не распознал текст'} 🙁")
            return
        lang = detect_lang_sr_ru(text, chat_id=chat_id, source="text")
        if lang == "ru":
            tr = text
            flag = "🖼 Русский текст (перевод не нужен)"
        elif lang == "en":
            tr = translate_to(text, "русский", "английского", chat_id=None, history=False)
            flag = "🇬🇧 → 🇷🇺"
        else:
            tr = translate_to(text, "русский", "сербского", chat_id=None, history=False)
            flag = "🇷🇸 → 🇷🇺"
        save_dialog(chat_id, "user", text)
        save_dialog(chat_id, "assistant", tr)
        out = f"🖼 <i>Распознано:</i> {text}\n\n{flag}\n<b>{tr}</b>"
        send_text(chat_id, out)
        if lang != "ru":
            ogg = tts_google(tr, "ru")
            if ogg:
                send_voice(chat_id, ogg, caption="🔊 Русский (озвучено)")
                os.unlink(ogg)
    except Exception as e:
        log.error(f"photo err: {e}")
        send_text(chat_id, f"Ошибка при обработке фото: {e}")

def get_updates(offset):
    """Забрать апдейты с retry."""
    for attempt in range(3):
        try:
            r = requests_get_retry(f"{API}/getUpdates",
                             params={"offset": offset, "timeout": 25},
                             timeout=30)
            return r.json().get("result", [])
        except Exception as e:
            log.error(f"getUpdates err (попытка {attempt+1}): {e}")
            time.sleep(1.5)
    return []

def main():
    init_db()
    log.info("Бот запущен")
    offset = 0
    while True:
        try:
            for upd in get_updates(offset):
                offset = upd["update_id"] + 1
                cb = upd.get("callback_query")
                if cb:
                    cid = cb["message"]["chat"]["id"]
                    if cid not in AUTHORIZED:
                        continue
                    if cb["data"] == "to_en":
                        requests.post(f"{API}/answerCallbackQuery",
                                      data={"callback_query_id": cb["id"], "text": "Перевожу на английский..."}, timeout=30)
                        src = get_last_user(cid) or ""
                        if not src:
                            send_text(cid, "Нет исходного текста для перевода. Напиши что-нибудь заново.")
                        else:
                            en = translate_to(src, "английский", "русского", chat_id=None, history=False)
                            send_text(cid, f"🇷🇺 → 🇬🇧\n\n{en}")
                    continue
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                if chat_id not in AUTHORIZED:
                    send_text(chat_id, "Извините, бот личный.")
                    continue
                text = msg.get("text")
                voice = msg.get("voice")
                if text and text.startswith("/"):
                    if text.startswith("/start"):
                        send_text(chat_id,
                            "🤖 <b>Переводчик</b>\n\n"
                            "📝 <b>Текст:</b> просто напиши фразу — бот сам определит язык и переведёт\n"
                            "   (сербский ⇄ русский, английский ⇄ русский)\n"
                            "🎙 <b>Голос:</b> нажми запись и говори — распознаю и переведу\n"
                            "🧠 <b>История:</b> бот помнит диалог для связности перевода\n"
                            "🗑 <b>/clear</b> — удалить всю историю разговора")
                    elif text.startswith("/clear"):
                        send_text(chat_id, "🗑 История разговора удалена из сессии.")
                    elif text.startswith("/sr"):
                        send_text(chat_id, "Режим: 🇷🇸 сербский → русский. Говори по-сербски.")
                    elif text.startswith("/ru"):
                        send_text(chat_id, "Режим: русский → 🇷🇸 сербский (+ озвучка). Говори по-русски.")
                    elif text.startswith("/en"):
                        send_text(chat_id, "Режим: 🇬🇧 английский → русский. Говори по-английски.")
                    else:
                        send_text(chat_id, "Неизвестная команда. Используй /start, /clear, /sr, /ru, /en.")
                elif text:
                    handle_text(chat_id, text)
                elif voice:
                    handle_voice(chat_id, voice["file_id"])
                elif msg.get("photo"):
                    handle_photo(chat_id, msg["photo"][-1]["file_id"])
        except Exception as e:
            log.error(f"loop err: {e}")
            time.sleep(3)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
