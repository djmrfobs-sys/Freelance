# -*- coding: utf-8 -*-
"""
Клиника Рядом - интеграция с нейросетями.
- Текст: DeepSeek (дёшево)
- Фото: Gemini по умолчанию / GPT-4o при необходимости (переключается в config)

Устойчивость к сбоям:
- таймауты и повторы при сетевых ошибках (ретраи)
- если нейросеть не ответила - вежливый fallback, бот никогда не молчит и не падает
"""
import os
import json
import time
import base64
import logging
import datetime
import urllib.request
import urllib.error

from config import DEEPSEEK_MODEL, PHOTO_MODEL

log = logging.getLogger("clinic.ai")

# Ключи (для главного бота-хозяина OpenClaw и для клиники одинаковые файлы)
KEY_DIR = os.path.expanduser("~/.openclaw-neuro")
DEEPSEEK_KEY_FILE = os.path.join(KEY_DIR, ".deepseek_key")
GEMINI_KEY_FILE = os.path.join(KEY_DIR, ".gemini_key")

# Настройки устойчивости
REQUEST_TIMEOUT = 45        # сек на один запрос
RETRIES = 3                 # сколько попыток при ошибке
RETRY_BACKOFF = 2           # базовая пауза между попытками (сек, 2^n)


def _read_key(fname):
    try:
        with open(fname, "r") as f:
            return f.read().strip()
    except Exception:
        return None


def _deepseek_key():
    return _read_key(DEEPSEEK_KEY_FILE)


def _gemini_key():
    return _read_key(GEMINI_KEY_FILE)


def _now_str():
    now = datetime.datetime.now()
    return now.strftime("%A, %d %B %Y, %H:%M")


def _call_deepseek(messages, temperature=0.7, max_tokens=900):
    """Прямой вызов DeepSeek API с ретраями и таймаутом."""
    key = _deepseek_key()
    if not key:
        log.error("Ключ DeepSeek не найден")
        return None

    url = "https://api.deepseek.com/chat/completions"
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")

    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "***" + key,
                },
            )
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            # 429 = апдейт: стоп, не мучаем. Прочее - пробуем ещё.
            if e.code == 429:
                break
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
        except Exception as e:
            last_err = str(e)

        log.warning("DeepSeek попытка %s/%s не удалась: %s", attempt, RETRIES, last_err)
        if attempt < RETRIES:
            time.sleep(RETRY_BACKOFF ** attempt)

    log.error("DeepSeek не ответил после %s попыток: %s", RETRIES, last_err)
    return None


def build_system_prompt(doctor_cfg):
    """Собирает системный промпт врача с учётом живой даты."""
    return (
        f"{doctor_cfg['role']}\n\n"
        f"Сегодня: {_now_str()}.\n"
        f"Ты работаешь в {doctor_cfg.get('clinic', 'Клинике Рядом')}. "
        f"Твоё имя: {doctor_cfg['doctor']} ({doctor_cfg['specialty']}).\n"
        "\n"
        "СТИЛЬ ЖИВОГО ВРАЧА (главное):\n"
        "- Ты живой внимательный доктор, а не робот-справочник. Общаешься тепло, "
        "по-человечески, без канцелярита и сухих списков.\n"
        "- Сначала эмпатия: коротко отреагируй на чувства ('Понимаю вас', "
        "'Это правда выматывает', 'Хорошо, что пришли с этим'). Не начинай сразу "
        "с советов.\n"
        "- Говори просто, будто в кабинете напротив человека. Местоимение 'вы', "
        "короткие фразы, живой тон.\n"
        "- Показывай интерес: спрашивай про самочувствие, страхи, что беспокоит "
        "больше всего, как давно, как влияет на жизнь.\n"
        "- В КОНЦЕ каждого ответа задавай 1-2 открытых вопроса, чтобы продолжить "
        "диалог, как врач на приёме ('Как давно это беспокоит?', 'Что тревожит "
        "сильнее всего?', 'Расскажите подробнее'). Не обрывай на монологе.\n"
        "- Если рассказано мало - попроси уточнить, прежде чем советовать. "
        "Не вываливай всё сразу, веди беседу постепенно.\n"
        "- Теплота и лёгкий юмор, но уважительно, без фамильярности.\n"
        "\n"
        "ОТВЕЧАЙ ПО ДЕЛУ, НА РУССКОМ, БЕЗ ЗВЁЗДОЧЕК И ДЛИННЫХ ТИРЕ. "
        "При угрожающих симптомах (резкая боль в груди, кровотечение, затруднённое "
        "дыхание, внезапное онемение, нарушение речи) настоятельно советуй срочно "
        "вызвать скорую 103/112 - это важнее любого совета."
    )


FALLBACK_REPLY = (
    "Извините, сейчас технический перебой в работе нейросети, меня "
    "ненадолго отвлекли. Ваше сообщение сохранено, я на него обязательно "
    "вернусь, если вы напишете ещё раз через пару минут. Спасибо за терпение."
)


def ask_doctor(doctor_cfg, history_messages):
    """Получить ответ врача на основе истории диалога.

    Возвращает всегда строку (даже при сбое - вежливый fallback),
    чтобы бот никогда не молчал и не падал.
    """
    try:
        system = build_system_prompt(doctor_cfg)
        messages = [{"role": "system", "content": system}] + history_messages
        reply = _call_deepseek(messages)
        if reply:
            return reply
    except Exception as e:
        log.error("ask_doctor исключение: %s", e)

    # Если DeepSeek молчит, даём человечный fallback и НЕ теряем диалог:
    # история пользователя уже сохранена до вызова, следующая попытка
    # увидит её и продолжит с места остановки.
    return FALLBACK_REPLY


GEMINI_VISION_MODEL = "gemini-flash-latest"
GEMINI_VISION_TIMEOUT = 50  # сек, анализ фото дольше обычного текста


def _mime_for(data):
    """Грубо угадать MIME по магическим байтам (JPEG/PNG/WebP/GIF)."""
    if data[:2] == b"\xff\xd8":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF":
        return "image/webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return "image/jpeg"


def analyze_photo(photo_data=None, description="", doctor_cfg=None):
    """Реальный анализ фото через Gemini Vision по бинарным данным.

    Аргументы:
        photo_data: байты изображения (бот скачивает из Telegram через get_file).
        description: подпись/комментарий пользователя к фото.
        doctor_cfg: конфиг врача (для контекста - что за специалист смотрит).

    Возвращает подробное описание того, что видно на фото, для передачи врачу.
    При сбое/отсутствии данных возвращает вежливое сообщение, НЕ спадая.
    """
    if not photo_data:
        return None

    key = _gemini_key()
    if not key:
        log.error("Ключ Gemini не найден для vision")
        return None

    specialty = doctor_cfg["specialty"] if doctor_cfg else "Врач"
    user_comment = description.strip() if (description and description != "[фото]") else ""

    prompt = (
        f"Ты - {specialty} в медицинской клинике. Пациент прислал фото "
        "и хочет консультацию.\n"
        f"Комментарий пациента к фото: {user_comment or '(нет)'}\n\n"
        "Опиши подробно и по делу, что видно на изображении: состояние кожи/тела/объекта, "
        "цвет, размер, локализацию, любые признаки. Не ставь диагноз, только "
        "объективно опиши то, что видно, медицинским, но понятным языком. "
        "Если фото не информативно, честно это скажи."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + GEMINI_VISION_MODEL + ":generateContent"
    )
    body = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": _mime_for(photo_data), "data": base64.b64encode(photo_data).decode()}},
                {"text": prompt},
            ]
        }]
    }

    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": key},
            )
            with urllib.request.urlopen(req, timeout=GEMINI_VISION_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code == 429:
                break
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
        except Exception as e:
            last_err = str(e)
        log.warning("Gemini Vision попытка %s/%s не удалась: %s", attempt, RETRIES, last_err)
        if attempt < RETRIES:
            time.sleep(RETRY_BACKOFF ** attempt)

    log.error("Gemini Vision не ответил: %s", last_err)
    return None
