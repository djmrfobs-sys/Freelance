# ============================================================
# ПАТЧИ ДЛЯ projects/serbian_translator_bot/bot.py
# ============================================================
# Как применять: найти в bot.py функцию с тем же именем и
# заменить её целиком на версию отсюда. Порядок функций в файле
# менять не нужно — просто замена тела функции на месте.
# ============================================================


# ------------------------------------------------------------
# ПАТЧ 1: detect_lang_sr_ru
# БАГ: буквы "ц" и "ш" считались эксклюзивно русскими, хотя они
# есть и в сербской кириллице (шта, цео и т.д.) — из-за этого
# сербский текст без явных маркеров ошибочно определялся как
# русский. Исправление: убрать "ц" и "ш" из ru_only.
# Настоящие эксклюзивно русские буквы из кириллицы (которых нет
# в сербском алфавите): ъ ы э щ ё й ю я.
# ------------------------------------------------------------

    # ПРОВЕРКА 4: Русские маркеры (буквы) — ИСПРАВЛЕНО: убраны "ц","ш",
    # т.к. они есть и в сербской кириллице (шта, цео...) и раньше
    # ложно определяли сербский текст как русский.
    ru_only = ("ъ", "ы", "э", "щ", "ё", "й", "ю", "я")
    if any(ch in s for ch in ru_only):
        if chat_id:
            log_lang_detection(chat_id, source, text[:50], "ru", "ru_special_letters")
        return "ru"

    # Остальной код detect_lang_sr_ru (ПРОВЕРКА 5, ПРОВЕРКА 6 и то, что
    # шло дальше — cyr_ratio > 0.5 и default) — оставить как было,
    # он не менялся. Меняется только блок ПРОВЕРКИ 4 выше.


# ------------------------------------------------------------
# ПАТЧ 2: transcribe_groq
# БАГ: жёстко зашитый language="sr" — Whisper физически не может
# распознать русскую или английскую речь, всегда выдаёт "сербский"
# результат. Именно поэтому голосовые на русском/английском
# переводились неправильно.
# ИСПРАВЛЕНИЕ: убрать принудительный language, включить честное
# автоопределение Whisper (один проход, скорость не теряется).
# Проверку "не спутал ли Whisper сербскую речь с русской" теперь
# делает не Whisper, а detect_lang_sr_ru по тексту (см. патч 3) —
# та же надёжная логика на словах-маркерах, что уже работает для
# текстовых сообщений и OCR.
# ------------------------------------------------------------

def transcribe_groq(audio_path):
    """Whisper через Groq. Возвращает (текст, язык_whisper, ошибка).
    ИСПРАВЛЕНО: автоопределение языка Whisper (без force language="sr"),
    один проход — скорость та же, что и раньше. Реальное решение о
    языке (ru/sr/en) принимается позже в handle_voice через
    detect_lang_sr_ru по тексту транскрипции — это надёжнее, чем
    полагаться на поле language от Whisper, и одинаково хорошо
    работает для всех трёх языков."""
    data = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json"}
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


# ------------------------------------------------------------
# ПАТЧ 3: handle_voice
# БАГ: определение языка шло по полю wlang от Whisper, в котором
# НЕ БЫЛО ветки для русского вообще (только "serb"/"eng", иначе
# дефолт "sr") — русский голос физически не мог быть распознан
# как русский.
# ИСПРАВЛЕНИЕ: язык определяется через detect_lang_sr_ru по самому
# тексту транскрипции (та же проверенная функция, что и для текста
# и OCR) — теперь поддерживает ru/sr/en одинаково надёжно.
# ------------------------------------------------------------

def handle_voice(chat_id, file_id, forced_mode=None):
    send_text(chat_id, "Raspoznayu i perevozhu na russkij...")
    try:
        fi = tg("getFile", file_id=file_id)
        if not fi.get("ok"):
            send_text(chat_id, "Ne udalosy poluchit fail")
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
            send_text(chat_id, f"Ne raspoznal golos: {err or 'pusto'}")
            return

        log.info(f"voice transcribe: wlang={wlang!r} text={text!r}")

        # ИСПРАВЛЕНО: язык определяем по тексту (detect_lang_sr_ru),
        # а не по wlang от Whisper — работает для ru/sr/en.
        lang = detect_lang_sr_ru(text, chat_id=chat_id, source="voice")

        if lang != "ru":
            src_hint = "serbskogo" if lang == "sr" else "anglijskogo"
            tr = translate_to(text, "russkij", src_hint, chat_id=None, history=False)
        else:
            tr = None
        save_dialog(chat_id, "user", text)
        if tr:
            save_dialog(chat_id, "assistant", tr)
        if lang == "en":
            flag = "EN -> RU"
        elif lang == "sr":
            flag = "SR -> RU"
        else:
            flag = "RU"
        if tr:
            out = f"Raspoznano: {text}\n\n{flag}\n{tr}"
        else:
            out = f"Raspoznano (uzhe russkij): {text}\n\n{flag}\nTekst na russkom - perevod ne nuzhen."
        send_text(chat_id, out)
    except Exception as e:
        log.error(f"handle_voice err: {e}")
        send_text(chat_id, f"Oshibka obrabotki golosa: {e}")


# ------------------------------------------------------------
# ПАТЧ 4: requests_get_retry / requests_post_retry
# Не видел тела функций целиком в присланном коде (только первые
# 2 строки requests_get_retry). Ниже — безопасная реализация с
# нуля под требования пункта 3 ТЗ: быстрый повтор именно при
# обрыве соединения/таймауте, с уменьшенным ожиданием между
# попытками (а не полный дефолтный таймаут).
#
# ВАЖНО: если в реальном файле эти функции уже что-то делают
# по-другому (например, есть доп. логика, заголовки, счётчики) —
# Джарвис должен свести это с уже существующим кодом вручную,
# а не слепо затирать, если увидит расхождения.
# ------------------------------------------------------------

def requests_get_retry(url, **kwargs):
    """GET с быстрыми повторами при обрыве связи/таймауте."""
    max_retries = 3
    timeout = kwargs.pop('timeout', 10)
    last_exc = None
    for attempt in range(max_retries):
        try:
            return requests.get(url, timeout=timeout, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            log.error(f"requests_get_retry timeout/conn err (popytka {attempt+1}): {e}")
            time.sleep(0.5 * (attempt + 1))  # 0.5s, 1s, 1.5s — быстрый бэкофф
        except Exception as e:
            last_exc = e
            log.error(f"requests_get_retry err (popytka {attempt+1}): {e}")
            time.sleep(0.5 * (attempt + 1))
    raise last_exc


def requests_post_retry(url, **kwargs):
    """POST с быстрыми повторами при обрыве связи/таймауте."""
    max_retries = 3
    timeout = kwargs.pop('timeout', 10)
    last_exc = None
    for attempt in range(max_retries):
        try:
            return requests.post(url, timeout=timeout, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            log.error(f"requests_post_retry timeout/conn err (popytka {attempt+1}): {e}")
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            last_exc = e
            log.error(f"requests_post_retry err (popytka {attempt+1}): {e}")
            time.sleep(0.5 * (attempt + 1))
    raise last_exc


# ============================================================
# ЧТО ОСТАЁТСЯ СДЕЛАТЬ ОТДЕЛЬНО (не хватило кода, чтобы патчить
# безопасно — риск затереть рабочую логику вслепую):
#
# 1. handle_text (начало, до "flag = ..."), translate_to,
#    ocr_image, tts_google — не видел целиком, не трогаю.
#    Джарвис: проверьте вручную, что flag-логика в handle_text
#    (SR->RU / EN->RU / RU->SR) не пересекается по побочным
#    эффектам с изменениями выше.
#
# 2. Webhook вместо getUpdates-поллинга (пункт 2 из ТЗ) — это
#    архитектурное изменение (нужен домен + SSL-сертификат или
#    self-signed + открытый порт), сделал бы код вслепую без
#    этих деталей — риск сломать доступность бота. Сначала нужно
#    решить: есть у вас домен/сертификат для вебхука, или Джарвис
#    ставит self-signed?
#
# 3. Дублирующая строка cb = upd.get("callback_query") — в
#    присланной версии main() дубля НЕТ, значит этот пункт уже
#    неактуален (либо был в другой версии файла раньше).
#
# 4. Fallback для TTS (<1000 байт), проверка модели OCR — не видел
#    tts_google и ocr_image целиком, патчить не могу вслепую.
# ============================================================
