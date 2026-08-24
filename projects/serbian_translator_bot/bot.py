#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Профессиональный бот-переводчик v5.0 PRO — KISELEVY CREO

Что умеет:
- Полная матрица перевода 3x3: SR <-> RU <-> EN (все 6 направлений)
- Текст + голос (Groq Whisper, умная детекция языка) + фото/OCR (Gemini Vision)
- Озвучка перевода (Google TTS) — не блокирует ответ
- Кэш переводов (повторные фразы — мгновенно)
- Inline-кнопки: быстрый пере-перевод того же текста на любой язык
- Rate-limit (дневной лимит бесплатного тарифа, предохранитель от минуса)
- Статистика для админа /stats
- Мультиюзер (OPEN_MODE) — готов к комьюнити Олега (33к человек)

Направления: SR->RU | RU->SR | SR->EN | EN->SR | RU->EN | EN->RU
"""

import os, io, time, re, logging, subprocess, tempfile, json, hashlib
import threading, datetime, sqlite3, urllib.parse, base64
import requests

# ======================== КОНФИГУРАЦИЯ ========================

BASE = "/root/.openclaw/workspace-neuro"

with open(f"{BASE}/secrets/serbian_translator_bot.token") as f:
    TOKEN = f.read().strip()

GROQ_KEY = open(os.path.expanduser("~/.openclaw-neuro/.groq_key")).read().strip()
DEEPSEEK_KEY = open(os.path.expanduser("~/.openclaw-neuro/.deepseek_key")).read().strip()

_gemini_paths = [
    os.path.expanduser("~/.openclaw-neuro/.gemini_key"),
    f"{BASE}/secrets/gemini_key",
    f"{BASE}/secrets/.gemini_key",
]
GEMINI_KEY = ""
for _gp in _gemini_paths:
    if os.path.exists(_gp):
        GEMINI_KEY = open(_gp).read().strip()
        break

API = f"https://api.telegram.org/bot{TOKEN}"

# Кто может пользоваться. OPEN_MODE=True — бот открыт для всех (комьюнити Олега).
OPEN_MODE = False
AUTHORIZED = {199790247, 5276541529}   # Артур + Кети (личный режим)
ADMIN_IDS = {199790247}                # Артур — админ, видит /stats

# Лимиты бесплатного тарифа (предохранитель от минуса по API-расходам)
DAILY_LIMIT = 15          # переводов в день на одного бесплатника (текст+голос+фото суммарно)
ADMIN_UNLIMITED = True    # админ без лимита

# ГЛОБАЛЬНЫЙ СТОП-КРАН: при превышении месячного бюджета бесплатники отключаются
MONTHLY_BUDGET_USD = 50.0       # бюджет на API в месяц (стоп-кран)
COST_PER_REQUEST_USD = 0.0002   # консервативная оценка себестоимости 1 запроса (смесь текст/голос/фото)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("srbot")

# ======================== ЯЗЫКОВАЯ МАТРИЦА ========================

LANG_INFO = {
    "sr": {"name": "сербского", "tgt": "сербский", "flag": "🇷🇸"},
    "ru": {"name": "русского", "tgt": "русский", "flag": "🇷🇺"},
    "en": {"name": "английского", "tgt": "английский", "flag": "🇬🇧"},
}

# Куда переводим по умолчанию при автодетекте
DEFAULT_TARGET = {"sr": "ru", "ru": "sr", "en": "ru"}

ALL_LANGS = ("sr", "ru", "en")


# ======================== SQLite ========================

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translator_history.db")
DB_LOCK = threading.Lock()


def init_db():
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS dialog_history (
                    id INTEGER PRIMARY KEY, chat_id INTEGER, role TEXT, text TEXT, ts TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON dialog_history(chat_id)")
            c.execute("""
                CREATE TABLE IF NOT EXISTS lang_detection_log (
                    id INTEGER PRIMARY KEY, chat_id INTEGER, source TEXT,
                    whisper_result TEXT, text_sample TEXT, final_lang TEXT, reason TEXT, ts TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS translation_cache (
                    id INTEGER PRIMARY KEY, src_hash TEXT, src_text TEXT,
                    src_lang TEXT, tgt_lang TEXT, translated TEXT, ts TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON translation_cache(src_hash, src_lang, tgt_lang)")
            c.execute("""
                CREATE TABLE IF NOT EXISTS usage_daily (
                    chat_id INTEGER, date TEXT, cnt INTEGER,
                    PRIMARY KEY (chat_id, date)
                )
            """)
            # Миграция: если старая таблица lang_detection_log без колонки whisper_result
            try:
                c.execute("SELECT whisper_result FROM lang_detection_log LIMIT 1")
            except Exception:
                c.execute("ALTER TABLE lang_detection_log ADD COLUMN whisper_result TEXT")
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"init_db err: {e}")


def save_dialog(chat_id, role, text):
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            ts = datetime.datetime.now().isoformat()
            conn.execute("INSERT INTO dialog_history (chat_id, role, text, ts) VALUES (?, ?, ?, ?)", (chat_id, role, text, ts))
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"save_dialog err: {e}")


def get_dialog_history(chat_id, limit=12):
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT role, text FROM dialog_history WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit))
            rows = c.fetchall()
            conn.close()
            return [{"role": r[0], "text": r[1]} for r in reversed(rows)]
    except Exception as e:
        log.error(f"get_dialog_history err: {e}")
        return []


def clear_dialog_history(chat_id):
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM dialog_history WHERE chat_id=?", (chat_id,))
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"clear_dialog_history err: {e}")


def cache_get(text, src_lang, tgt_lang):
    try:
        h = hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT translated FROM translation_cache WHERE src_hash=? AND src_lang=? AND tgt_lang=?", (h, src_lang, tgt_lang))
            row = c.fetchone()
            conn.close()
            if row:
                log.info(f"cache HIT: {text[:40]!r}")
                return row[0]
        return None
    except Exception as e:
        log.error(f"cache_get err: {e}")
        return None


def cache_set(text, src_lang, tgt_lang, translated):
    try:
        h = hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            ts = datetime.datetime.now().isoformat()
            conn.execute(
                "INSERT OR REPLACE INTO translation_cache (src_hash, src_text, src_lang, tgt_lang, translated, ts) VALUES (?, ?, ?, ?, ?, ?)",
                (h, text[:200], src_lang, tgt_lang, translated, ts),
            )
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"cache_set err: {e}")


def log_lang_detection(chat_id, source, whisper_result, text_sample, final_lang, reason):
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            ts = datetime.datetime.now().isoformat()
            conn.execute(
                "INSERT INTO lang_detection_log (chat_id, source, whisper_result, text_sample, final_lang, reason, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (chat_id, source, whisper_result, text_sample[:100], final_lang, reason, ts),
            )
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"log_lang_detection err: {e}")


# ======================== RATE LIMIT (дневной лимит) ========================

def check_and_count(chat_id):
    """Возвращает (allowed, used, limit, reason). Админ без лимита."""
    if ADMIN_UNLIMITED and chat_id in ADMIN_IDS:
        return True, 0, DAILY_LIMIT, None

    # Глобальный стоп-кран: если месячный бюджет превышен, бесплатники отключаются
    total_req, cost_usd = monthly_cost_and_usage()
    if cost_usd >= MONTHLY_BUDGET_USD:
        return False, 0, DAILY_LIMIT, "budget"

    today = datetime.date.today().isoformat()
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT cnt FROM usage_daily WHERE chat_id=? AND date=?", (chat_id, today))
            row = c.fetchone()
            used = row[0] if row else 0
            if used >= DAILY_LIMIT:
                conn.close()
                return False, used, DAILY_LIMIT, "daily"
            c.execute(
                "INSERT INTO usage_daily (chat_id, date, cnt) VALUES (?, ?, 1) ON CONFLICT(chat_id, date) DO UPDATE SET cnt = cnt + 1",
                (chat_id, today),
            )
            conn.commit()
            conn.close()
            return True, used + 1, DAILY_LIMIT, None
    except Exception as e:
        log.error(f"check_and_count err: {e}")
        return True, 0, DAILY_LIMIT, None


def monthly_cost_and_usage():
    """Суммарные переводы и оценка стоимости за текущий месяц (для стоп-крана)."""
    try:
        month = datetime.date.today().strftime("%Y-%m")
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COALESCE(SUM(cnt),0) FROM usage_daily WHERE date LIKE ?", (month + "%",))
            total = c.fetchone()[0]
            conn.close()
            cost_usd = total * COST_PER_REQUEST_USD
            return total, cost_usd
    except Exception as e:
        log.error(f"monthly_cost err: {e}")
        return 0, 0.0


def stats():
    today = datetime.date.today().isoformat()
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(DISTINCT chat_id) FROM dialog_history")
            users = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM dialog_history WHERE role='assistant'")
            translations = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM translation_cache")
            cache_entries = c.fetchone()[0]
            c.execute("SELECT COUNT(*), COALESCE(SUM(cnt),0) FROM usage_daily WHERE date=?", (today,))
            rows = c.fetchone()
            conn.close()
            return {
                "users": users,
                "translations": translations,
                "cache_entries": cache_entries,
                "today_users": rows[0] or 0,
                "today_translations": rows[1] or 0,
            }
    except Exception as e:
        log.error(f"stats err: {e}")
        return {}


# ======================== Последний текст + режим ========================

LAST_USER = {}
LAST_LOCK = threading.Lock()
MODE = {}
MODE_LOCK = threading.Lock()


def set_mode(chat_id, mode):
    with MODE_LOCK:
        MODE[chat_id] = mode


def get_mode(chat_id):
    with MODE_LOCK:
        return MODE.get(chat_id)


def save_last_user(chat_id, text):
    with LAST_LOCK:
        LAST_USER[chat_id] = text
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("CREATE TABLE IF NOT EXISTS last_user (chat_id INTEGER PRIMARY KEY, text TEXT)")
            conn.execute("INSERT OR REPLACE INTO last_user (chat_id, text) VALUES (?, ?)", (chat_id, text))
            conn.commit()
            conn.close()
    except Exception as e:
        log.error(f"save_last_user db err: {e}")


def get_last_user(chat_id):
    with LAST_LOCK:
        v = LAST_USER.get(chat_id)
        if v:
            return v
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT text FROM last_user WHERE chat_id=?", (chat_id,))
            row = c.fetchone()
            conn.close()
            if row:
                return row[0]
    except Exception as e:
        log.error(f"get_last_user db err: {e}")
    return None


# ======================== HTTP-ретраи ========================

def requests_get_retry(url, **kwargs):
    max_retries = 3
    timeout = kwargs.pop("timeout", 10)
    last_exc = None
    for attempt in range(max_retries):
        try:
            return requests.get(url, timeout=timeout, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            log.warning(f"GET retry {attempt+1}/{max_retries}: {e}")
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            last_exc = e
            log.error(f"GET err {attempt+1}: {e}")
            time.sleep(0.5 * (attempt + 1))
    raise last_exc


def requests_post_retry(url, **kwargs):
    max_retries = 3
    timeout = kwargs.pop("timeout", 10)
    last_exc = None
    for attempt in range(max_retries):
        try:
            return requests.post(url, timeout=timeout, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            log.warning(f"POST retry {attempt+1}/{max_retries}: {e}")
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            last_exc = e
            log.error(f"POST err {attempt+1}: {e}")
            time.sleep(0.5 * (attempt + 1))
    raise last_exc


# ======================== Telegram helpers ========================

def tg(method, **params):
    try:
        r = requests_post_retry(f"{API}/{method}", data=params, timeout=120)
        return r.json()
    except Exception:
        return {"ok": False}


def send_text(chat_id, text, reply_to=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        r = requests_post_retry(f"{API}/sendMessage", data=data, timeout=20)
        if not r.json().get("ok"):
            log.error(f"send_text fail: {r.text[:200]}")
    except Exception as e:
        log.error(f"send_text err: {e}")


def send_text_with_buttons(chat_id, text, buttons):
    """buttons: список списков dict {text, callback_data}."""
    keyboard = {"inline_keyboard": buttons}
    data = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps(keyboard)}
    try:
        r = requests_post_retry(f"{API}/sendMessage", data=data, timeout=20)
        if not r.json().get("ok"):
            log.error(f"send_text_with_buttons fail: {r.text[:200]}")
    except Exception as e:
        log.error(f"send_text_with_buttons err: {e}")


def send_voice(chat_id, voice_path, caption=None, reply_to=None):
    try:
        with open(voice_path, "rb") as f:
            files = {"voice": ("voice.ogg", f, "audio/ogg")}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            if reply_to:
                data["reply_to_message_id"] = reply_to
            requests_post_retry(f"{API}/sendVoice", data=data, files=files, timeout=120)
    except Exception as e:
        log.error(f"send_voice err: {e}")


# ======================== ОПРЕДЕЛЕНИЕ ЯЗЫКА (УМНОЕ) ========================

def detect_lang_sr_ru(text, chat_id=None, source="text"):
    low = text.lower()
    chars = set(low)
    letters = [c for c in text if c.isalpha()]
    words = {w.strip(".,!?():;'\"-–—/").lower() for w in low.split()}

    sr_words_lat = {
        "kako", "sta", "šta", "sto", "što", "gde", "gdje", "kada", "kad", "kuda",
        "nije", "nema", "hvala", "dobro", "zdravo", "danas", "sutra", "sada", "uvek",
        "opet", "jos", "još", "zato", "kroz", "preko", "dok", "ako", "sve",
        "oni", "ona", "mi", "vi", "nas", "vas", "se", "sam", "si", "smo", "ste", "su",
        "je", "bilo", "bio", "bila", "ovde", "tamo", "puno", "malo", "idem", "idemo",
        "dolazim", "volim", "zelim", "želim", "moram", "probam", "imate", "imam",
        "radim", "radimo", "znam", "znate", "lepo", "brzo", "polako", "recite",
        "pomoci", "pomoći", "potreban", "kupiti", "kupujem", "stize", "stiže",
        "dolazi", "zovem", "zovemo", "cemo", "ćemo", "necu", "neću", "posle", "pre",
        "vece", "veče", "dan", "jutro", "noc", "noć", "dobrodosli", "dobrodošli",
        "prijatno", "izvoli", "izvolite", "moze", "može", "treba", "trebam", "shta",
        "bas", "baš", "naravno", "svakako", "jedan", "dva", "tri", "voda", "hleb",
        "hrana", "kafa", "svuda", "samo", "jer", "ali", "pa", "li", "da", "ne",
        "evo", "eto", "molim", "hocu", "hoću", "razumem", "razumijem", "vidim",
        "cujem", "čujem", "govorim", "pricam", "pričam", "pitam", "odgovor", "odgovaram",
        "račun", "novi", "novog", "novom",
    }

    sr_words_cyr = {
        "хвала", "здраво", "добродошли", "пријатно", "изволи", "изволите", "молим",
        "добар", "дан", "јутро", "вече", "ноћ", "добар дан", "добро јутро", "добро вече",
        "лаку ноћ", "драго ми је", "хвала лепо", "данас", "сутра", "сада", "прекосутра",
        "синоћ", "ујутру", "увече", "није", "нема", "све", "кроз", "овде", "тамо", "пуно",
        "са", "је", "јесте", "које", "која", "који", "шта", "када", "кад", "јер", "само",
        "ово", "то", "оно", "зашто", "како", "колико", "чиме", "си", "смо", "сте", "су",
        "био", "желим", "желиш", "жели", "желимо", "радим", "знам", "волим", "имам", "имате",
        "идем", "идеш", "иде", "идемо", "долазим", "морам", "мораш", "покушавам", "разумем",
        "чујем", "причам", "причаш", "питам", "зовеш", "зове", "звао", "звала", "дођи",
        "дођите", "дошао", "дошла", "хоћу", "хоћеш", "хоће", "треба", "требам", "платим",
        "купим", "купујем", "тражим", "гледам", "слушам", "чекам", "помажем", "свиђа",
        "седим", "стојим", "живим", "вратим", "враћам", "храна", "кафа", "шоља", "тањир",
        "пиће", "јело", "човек", "дете", "деца", "кућа", "земља", "рачун", "новац", "пекара",
        "продавница", "пијаца", "апотека", "лекар", "болница", "школа", "музеј", "воз",
        "аутобус", "станица", "карта", "презиме", "име", "боја", "окус", "топло", "хладно",
        "вруће", "лепо", "дивно", "супер", "један", "четири", "пет", "шест", "седам", "осам",
        "девет", "десет", "како си", "како сте", "молим вас", "добро сам", "шта радиш",
        "шта радите", "колико кошта", "како се зовеш", "како се зовете", "код куће",
        "на послу", "у школи", "у граду", "зато", "опет", "још", "близу", "далеко", "полако",
        "брзо", "свакако", "наравно", "можда", "вероватно", "стварно", "баш", "већ", "увек",
        "понекад", "често", "ретко", "занимљиво", "занимљив", "радознао", "радознала",
    }

    sr_spec_cyr = set("љњџћђј")
    sr_lat_dia = ("š", "ž", "ć", "č", "đ", "nj", "lj", "dž")

    ru_exclusive = set("ъыэёщйюя")
    ru_words = {
        "привет", "пока", "спасибо", "пожалуйста", "извините", "здравствуйте",
        "ночь", "утро", "день", "вечер", "ночью", "утром", "днём", "вечером",
        "люблю", "хочу", "могу", "надо", "нельзя", "можно", "нужно",
        "меньше", "больше", "хороший", "плохой", "красивый", "новый", "старый",
        "горячий", "холодный", "тёплый", "русский", "родной", "сегодня",
        "завтра", "вчера", "сейчас", "потом", "здесь", "там", "тут",
        "почему", "зачем", "откуда", "куда", "когда", "сколько",
        "переведи", "переведите", "перевод", "скажи", "скажите",
    }

    if chars & sr_spec_cyr:
        reason = "sr_special_cyrillic: љњџћђј"
        log.info(f"detect: {reason}")
        if chat_id:
            log_lang_detection(chat_id, source, "?", text[:50], "sr", reason)
        return "sr"

    if chars & ru_exclusive:
        reason = "ru_exclusive: ъыэёщйюя"
        log.info(f"detect: {reason}")
        if chat_id:
            log_lang_detection(chat_id, source, "?", text[:50], "ru", reason)
        return "ru"

    sr_word_hits = words & (sr_words_lat | sr_words_cyr)
    if sr_word_hits:
        reason = f"sr_words: {','.join(list(sr_word_hits)[:3])}"
        log.info(f"detect: {reason}")
        if chat_id:
            log_lang_detection(chat_id, source, "?", text[:50], "sr", reason)
        return "sr"

    ru_word_hits = words & ru_words
    if ru_word_hits:
        reason = f"ru_words: {','.join(list(ru_word_hits)[:3])}"
        log.info(f"detect: {reason}")
        if chat_id:
            log_lang_detection(chat_id, source, "?", text[:50], "ru", reason)
        return "ru"

    if any(m in low for m in sr_lat_dia):
        reason = "sr_latin_diacritics: š,ž,ć,č,đ"
        log.info(f"detect: {reason}")
        if chat_id:
            log_lang_detection(chat_id, source, "?", text[:50], "sr", reason)
        return "sr"

    cyr_all = set("абвгдежзиклмнопрстуфхцчшщъыьэюяјљњџћђ")
    if letters:
        cyr_count = sum(1 for c in letters if c.lower() in cyr_all)
        cyr_ratio = cyr_count / len(letters)
        lat_count = sum(1 for c in letters if c.lower() in "abcdefghijklmnopqrstuvwxyz")
        lat_ratio = lat_count / len(letters)

        if lat_ratio > 0.5:
            reason = f"latin_dominant: {lat_ratio:.2f}"
            log.info(f"detect: {reason}")
            if chat_id:
                log_lang_detection(chat_id, source, "?", text[:50], "en", reason)
            return "en"

        if cyr_ratio > 0.5:
            reason = f"cyr_ratio={cyr_ratio:.2f}_default_ru"
            log.info(f"detect: {reason}")
            if chat_id:
                log_lang_detection(chat_id, source, "?", text[:50], "ru", reason)
            return "ru"

    reason = "fallback_sr"
    log.info(f"detect: {reason}")
    if chat_id:
        log_lang_detection(chat_id, source, "?", text[:50], "sr", reason)
    return "sr"


# ======================== WHISPER (Groq) ========================

def transcribe_groq(audio_path, chat_id=None):
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}

    log.info("Whisper: Pass1 (auto-detect)")
    data1 = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json"}
    with open(audio_path, "rb") as f:
        r1 = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers, data=data1,
            files={"file": ("audio.ogg", f, "audio/ogg")}, timeout=90,
        )
    if r1.status_code != 200:
        return None, None, f"STT error {r1.status_code}"

    d1 = r1.json()
    text1 = d1.get("text", "").strip()
    wlang1 = (d1.get("language") or "").lower()
    log.info(f"Whisper Pass1: lang={wlang1!r} text={text1[:80]!r}")

    if "eng" in wlang1 or wlang1 == "en":
        log.info(f"Whisper: detected ENGLISH")
        if chat_id:
            log_lang_detection(chat_id, "voice", wlang1, text1[:50], "en", "whisper_english")
        return text1, "en", None

    detected_lang = detect_lang_sr_ru(text1, chat_id=None, source="whisper_analysis")

    if "russ" in wlang1 or wlang1 == "ru":
        ru_word_markers = {
            "привет", "пока", "спасибо", "пожалуйста", "извините", "здравствуйте",
            "хочу", "надо", "нельзя", "можно", "нужно", "почему", "зачем", "откуда",
            "сколько", "сегодня", "завтра", "вчера", "сейчас", "потом", "здесь",
            "переведи", "переведите", "перевод", "скажи", "подскажи", "подскажите",
            "ладно", "хорошо", "давай", "ничего", "ещё", "уже", "тоже", "только",
            "конечно", "наверное", "кажется", "кстати", "вообще", "поэтому", "понял",
            "поняла", "понятно", "ребята", "ребёнок", "деньги", "работа", "работаю",
            "делаю", "пойдём", "пойду", "пошли", "будет", "будем", "будешь", "который",
            "которая", "которые", "чтобы", "потому", "слушай", "смотри", "знаешь",
            "думаю", "считаю", "верно", "добрый", "день", "тебя", "зовут", "меня",
            "мне", "есть", "быть", "очень", "просто", "самый", "самая", "такой",
            "такая", "этот", "эта",
        }
        auto_words = {w.strip(".,!?():;'\"-–—/").lower() for w in text1.split()}
        has_ru_words = bool(auto_words & ru_word_markers)
        log.info(f"Whisper: russian? ru_word_markers={has_ru_words} detected={detected_lang}")

        if has_ru_words:
            if chat_id:
                log_lang_detection(chat_id, "voice", wlang1, text1[:50], "ru", "ru_word_markers_found")
            return text1, "ru", None

        log.info(f"Whisper: 'russian' but NO ru word markers -> Pass2 с language='sr'")

        data2 = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json", "language": "sr"}
        with open(audio_path, "rb") as f:
            r2 = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers, data=data2,
                files={"file": ("audio.ogg", f, "audio/ogg")}, timeout=90,
            )
        if r2.status_code != 200:
            if chat_id:
                log_lang_detection(chat_id, "voice", wlang1, text1[:50], "sr", "pass2_failed_use_pass1")
            return text1, "sr", None

        d2 = r2.json()
        text2 = d2.get("text", "").strip()
        log.info(f"Whisper Pass2 (sr): text={text2[:80]!r}")

        detected_lang2 = detect_lang_sr_ru(text2, chat_id=None, source="whisper_pass2_analysis")
        log.info(f"Whisper Pass2 analysis: {detected_lang2}")

        if detected_lang2 in ("sr", "en"):
            if chat_id:
                log_lang_detection(chat_id, "voice", f"{wlang1}+sr", text2[:50], detected_lang2, "pass2_confirmed")
            return text2, detected_lang2, None
        else:
            if chat_id:
                log_lang_detection(chat_id, "voice", f"{wlang1}+sr", text1[:50], "sr", "pass2_ru_still_use_sr")
            return text1, "sr", None

    if detected_lang != wlang1 and "eng" not in wlang1:
        if chat_id:
            log_lang_detection(chat_id, "voice", wlang1, text1[:50], detected_lang, "whisper_non_ru_use_detect")
        return text1, detected_lang, None

    log.info(f"Whisper: Pass1 OK, lang={detected_lang}")
    if chat_id:
        log_lang_detection(chat_id, "voice", wlang1, text1[:50], detected_lang, "pass1_ok")
    return text1, detected_lang, None


# ======================== ПЕРЕВОД (DeepSeek) — полная матрица ========================

def translate(text, src, tgt, chat_id=None):
    """Перевод в любом из 6 направлений. src==tgt -> возврат как есть."""
    if src == tgt:
        return text

    cached = cache_get(text, src, tgt)
    if cached:
        return cached

    src_name = LANG_INFO[src]["name"]
    tgt_name = LANG_INFO[tgt]["tgt"]

    system_prompt = (
        f"Ты профессиональный переводчик сербского, русского и английского языков. "
        f"Переведи следующий текст с {src_name} на {tgt_name}. "
        f"Верни ТОЛЬКО перевод: без пояснений, без кавычек, без комментариев и без лишнего текста. "
        f"Сохрани смысл, стиль и тон оригинала. "
        f"Переводи естественно, как носитель языка, без буквальности."
    )

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]

    try:
        r = requests_post_retry(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.3, "max_tokens": 2000},
            timeout=20,
        )
        if r.status_code != 200:
            log.error(f"DeepSeek err {r.status_code}: {r.text[:200]}")
            return f"[Ошибка: {r.status_code}]"
        data = r.json()
        result = data["choices"][0]["message"]["content"].strip()

        if not result.startswith("["):
            cache_set(text, src, tgt, result)
        return result
    except Exception as e:
        log.error(f"translate err: {e}")
        return f"[Ошибка: {e}]"


# ======================== TTS (Google Translate) ========================

def tts_google(text, lang="sr"):
    try:
        tts_text = text[:500]
        encoded = urllib.parse.quote(tts_text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl={lang}&client=tw-ob"
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200 or len(r.content) < 1000:
            log.warning(f"TTS: bad response (status={r.status_code}, size={len(r.content)})")
            return None

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(r.content)
            mp3 = f.name

        ogg = mp3 + ".ogg"
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", mp3, "-filter:a", "atempo=0.85", "-c:a", "libopus", ogg],
            capture_output=True, timeout=30,
        )
        os.unlink(mp3)

        if result.returncode != 0:
            log.error(f"TTS ffmpeg err: {result.stderr[:200]}")
            return None
        return ogg
    except Exception as e:
        log.error(f"tts_google err: {e}")
        return None


def tts_async(chat_id, text, lang):
    def _worker():
        try:
            ogg = tts_google(text, lang)
            if ogg:
                send_voice(chat_id, ogg)
                os.unlink(ogg)
        except Exception as e:
            log.error(f"tts_async err: {e}")
    threading.Thread(target=_worker, daemon=True).start()


# ======================== OCR (Gemini Vision) ========================

def ocr_image(image_path):
    if not GEMINI_KEY:
        return None, "Gemini API key not found"
    try:
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash-preview-05-20"]

        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_data}},
                            {"text": "Распознай весь текст на изображении. Верни ТОЛЬКО распознанный текст без пояснений."},
                        ]
                    }]
                }
                r = requests.post(url, json=payload, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if text:
                        log.info(f"OCR ok (model={model})")
                        return text, None
                else:
                    log.warning(f"OCR model {model} err {r.status_code}")
                    continue
            except Exception as e:
                log.warning(f"OCR model {model} exception: {e}")
                continue
        return None, "All Gemini models unavailable"
    except Exception as e:
        return None, f"OCR err: {e}"


# ======================== ЯДРО: перевод + кнопки ========================

def flip_buttons(src):
    """Кнопки для пере-перевода того же текста на все языки, кроме исходного."""
    others = [l for l in ALL_LANGS if l != src]
    return [[{"text": f"{LANG_INFO[l]['flag']} {LANG_INFO[l]['tgt']}", "callback_data": f"flip:{l}"} for l in others]]


def is_allowed(chat_id):
    return OPEN_MODE or chat_id in AUTHORIZED


def do_translate(chat_id, text, src, prefix=""):
    """Переводит text из src в DEFAULT_TARGET[src], возвращает (ответ, tgt, ok)."""
    tgt = DEFAULT_TARGET[src]
    tr = translate(text, src, tgt, chat_id=chat_id)

    save_dialog(chat_id, "user", text)
    save_dialog(chat_id, "assistant", tr)
    save_last_user(chat_id, text)

    flag_src = LANG_INFO[src]["flag"]
    flag_tgt = LANG_INFO[tgt]["flag"]
    head = f"{flag_src} → {flag_tgt}"
    if prefix:
        head = f"{prefix}\n{flag_src} → {flag_tgt}"

    out = f"{head}\n\n{tr}"
    send_text_with_buttons(chat_id, out, flip_buttons(src))

    # Озвучка перевода на целевом языке
    tts_async(chat_id, tr, tgt)
    return tr, tgt


# ======================== ОБРАБОТЧИКИ ========================

def handle_text(chat_id, text):
    mode = get_mode(chat_id)
    if mode:
        src = mode
    else:
        src = detect_lang_sr_ru(text, chat_id=chat_id, source="text")
    log.info(f"handle_text: src={src} text={text[:50]!r}")
    do_translate(chat_id, text, src)


def handle_voice(chat_id, file_id):
    send_text(chat_id, "🎙 Распознаю...")
    try:
        fi = tg("getFile", file_id=file_id)
        if not fi.get("ok"):
            send_text(chat_id, "Не удалось получить файл.")
            return
        path = fi["result"]["file_path"]
        data = requests_get_retry(f"https://api.telegram.org/file/bot{TOKEN}/{path}", timeout=60).content
        with tempfile.NamedTemporaryFile(suffix=".oga", delete=False) as f:
            f.write(data)
            raw = f.name

        audio = raw + ".ogg"
        subprocess.run(["ffmpeg", "-y", "-i", raw, "-c:a", "libopus", audio], capture_output=True, timeout=30)
        os.unlink(raw)

        text, lang, err = transcribe_groq(audio, chat_id=chat_id)
        os.unlink(audio)
        if err or not text:
            send_text(chat_id, f"Не распознал: {err or 'пусто'}")
            return

        mode = get_mode(chat_id)
        src = mode or lang
        log.info(f"voice: src={src} text={text!r}")
        do_translate(chat_id, text, src, prefix=f"🎙 {text}")
    except Exception as e:
        log.error(f"handle_voice err: {e}")
        send_text(chat_id, f"Ошибка: {e}")


def handle_photo(chat_id, file_id):
    try:
        fi = tg("getFile", file_id=file_id)
        if not fi.get("ok"):
            send_text(chat_id, "Не удалось получить фото.")
            return
        path = fi["result"]["file_path"]
        data = requests_get_retry(f"https://api.telegram.org/file/bot{TOKEN}/{path}", timeout=120).content
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(data)
            img = f.name

        send_text(chat_id, "📷 Распознаю текст...")
        text, err = ocr_image(img)
        os.unlink(img)

        if err or not text:
            send_text(chat_id, f"{err or 'Не распознал'}")
            return

        mode = get_mode(chat_id)
        src = mode or detect_lang_sr_ru(text, chat_id=chat_id, source="photo")
        log.info(f"photo: src={src} text={text!r}")
        do_translate(chat_id, text, src, prefix=f"📷 {text}")
    except Exception as e:
        log.error(f"handle_photo err: {e}")
        send_text(chat_id, f"Ошибка при обработке фото: {e}")


def handle_flip(chat_id, tgt):
    """Пере-перевод последнего текста на выбранный язык."""
    src_text = get_last_user(chat_id)
    if not src_text:
        send_text(chat_id, "Нет исходного текста. Отправь фразу снова.")
        return

    src = detect_lang_sr_ru(src_text, chat_id=None, source="flip")
    if src == tgt:
        tr = src_text
    else:
        tr = translate(src_text, src, tgt, chat_id=chat_id)

    save_dialog(chat_id, "assistant", tr)

    flag_src = LANG_INFO[src]["flag"]
    flag_tgt = LANG_INFO[tgt]["flag"]
    out = f"{flag_src} → {flag_tgt}\n\n{tr}"
    send_text_with_buttons(chat_id, out, flip_buttons(src))

    if src != tgt:
        tts_async(chat_id, tr, tgt)


def send_start(chat_id):
    kb = [
        [{"text": "🇷🇸 Сербский → 🇷🇺 Русский", "callback_data": "mode:sr"}],
        [{"text": "🇷🇺 Русский → 🇷🇸 Сербский", "callback_data": "mode:ru"}],
        [{"text": "🇬🇧 Английский → 🇷🇺 Русский", "callback_data": "mode:en"}],
        [{"text": "🔄 Автодетект", "callback_data": "mode:auto"}],
    ]
    send_text_with_buttons(
        chat_id,
        "🇷🇸🇷🇺🇬🇧 Профессиональный переводчик\n\n"
        "📝 Текст — просто напиши фразу\n"
        "🎙 Голос — отправь голосовое (распознаю и переведу)\n"
        "📷 Фото — отправь фото с текстом (распознаю и переведу)\n\n"
        "Направления: SR↔RU, SR↔EN, RU↔EN\n\n"
        "Выбери режим или просто пиши — язык определю сам.",
        kb,
    )


# ======================== POLLING ========================

def get_updates(offset):
    for attempt in range(3):
        try:
            r = requests_get_retry(f"{API}/getUpdates", params={"offset": offset, "timeout": 25}, timeout=30)
            return r.json().get("result", [])
        except Exception as e:
            log.error(f"getUpdates err (popytka {attempt+1}): {e}")
            time.sleep(1.5)
    return []


def main():
    init_db()
    log.info("Bot zapuschen (v5.0 PRO — polnaya matrica 3x3)")
    offset = 0

    while True:
        try:
            for upd in get_updates(offset):
                offset = upd["update_id"] + 1

                cb = upd.get("callback_query")
                if cb:
                    cid = cb["message"]["chat"]["id"]
                    if not is_allowed(cid):
                        continue
                    data = cb["data"]
                    requests_post_retry(
                        f"{API}/answerCallbackQuery",
                        data={"callback_query_id": cb["id"]},
                        timeout=8,
                    )
                    if data.startswith("flip:"):
                        tgt = data.split(":", 1)[1]
                        if tgt in ALL_LANGS:
                            handle_flip(cid, tgt)
                    elif data.startswith("mode:"):
                        m = data.split(":", 1)[1]
                        if m == "auto":
                            set_mode(cid, None)
                            send_text(cid, "✅ Режим: автодетект языка")
                        elif m in ALL_LANGS:
                            set_mode(cid, m)
                            nm = LANG_INFO[m]["tgt"]
                            send_text(cid, f"✅ Режим: {nm} → перевод")
                    continue

                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                if not is_allowed(chat_id):
                    send_text(chat_id, "Бот личный.")
                    continue

                text = msg.get("text")
                voice = msg.get("voice")

                if text and text.startswith("/"):
                    cmd = text.lower().split()[0]
                    if cmd == "/start":
                        send_start(chat_id)
                    elif cmd == "/sr":
                        set_mode(chat_id, "sr")
                        send_text(chat_id, "✅ Режим: сербский → русский")
                    elif cmd == "/ru":
                        set_mode(chat_id, "ru")
                        send_text(chat_id, "✅ Режим: русский → сербский")
                    elif cmd == "/en":
                        set_mode(chat_id, "en")
                        send_text(chat_id, "✅ Режим: английский → русский")
                    elif cmd == "/auto":
                        set_mode(chat_id, None)
                        send_text(chat_id, "✅ Режим: автодетект")
                    elif cmd == "/clear":
                        clear_dialog_history(chat_id)
                        send_text(chat_id, "✅ История очищена.")
                    elif cmd == "/stats" and chat_id in ADMIN_IDS:
                        s = stats()
                        total_req, cost_usd = monthly_cost_and_usage()
                        send_text(
                            chat_id,
                            f"📊 Статистика\n\n"
                            f"Пользователей всего: {s.get('users', 0)}\n"
                            f"Переводов всего: {s.get('translations', 0)}\n"
                            f"Записей в кэше: {s.get('cache_entries', 0)}\n\n"
                            f"Сегодня:\n"
                            f"Активных: {s.get('today_users', 0)}\n"
                            f"Переводов: {s.get('today_translations', 0)}\n\n"
                            f"💰 Месяц:\n"
                            f"Запросов: {total_req}\n"
                            f"Оценка расхода: ${cost_usd:.2f} / ${MONTHLY_BUDGET_USD:.0f} бюджет\n\n"
                            f"Дневной лимит: {DAILY_LIMIT}\n"
                            f"OPEN_MODE: {'да' if OPEN_MODE else 'нет'}",
                        )
                    continue

                # Rate limit перед обработкой (кроме команд)
                allowed, used, limit, reason = check_and_count(chat_id)
                if not allowed:
                    if reason == "budget":
                        send_text(chat_id, "⚠️ Сервис временно на техобслуживании. Загляни позже.")
                    else:
                        send_text(chat_id, f"⏳ Дневной лимит исчерпан ({limit} переводов). Попробуй завтра.")
                    continue

                if text:
                    handle_text(chat_id, text)
                elif voice:
                    handle_voice(chat_id, voice["file_id"])
                elif msg.get("photo"):
                    handle_photo(chat_id, msg["photo"][-1]["file_id"])

        except Exception as e:
            log.error(f"loop err: {e}")
            time.sleep(3)

        time.sleep(0.3)


if __name__ == "__main__":
    main()
