#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МегаМозг - бот-генератор идей и ТЗ для нейрофабрики KISELEVY.CREO.
Пользователь пишет тему -> бот выдаёт 3-5 идей, потом подробное ТЗ.
ТЗ пользователь кидает ассистенту-нейрофабрике на реализацию.

Команды:
- /start    - приветствие
- /idea     - режим генерации идей
- /tz       - режим генерации подробного ТЗ
- /analyze  - аналитика ссылки (сайт / Telegram-бот / канал): разбор + ТЗ что добавить
- /clear    - сброс контекста
Запуск: python3 bot.py (под systemd)
"""

import os, time, re, json, threading, logging
from urllib.parse import urlparse
import requests

# глушим SSL-предупреждения при обращении к чужим сайтам
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "/root/.openclaw/workspace-neuro"
with open(f"{BASE}/secrets/megamind_bot.token") as f:
    TOKEN = f.read().strip()

DEEPSEEK_KEY = open(os.path.expanduser("~/.openclaw-neuro/.deepseek_key")).read().strip()

API = f"https://api.telegram.org/bot{TOKEN}"
AUTHORIZED = {199790247, 5276541529}  # Артур + Кети

DEEPSEEK_API = "https://api.deepseek.com/chat/completions"

log = logging.getLogger("megamind")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# ---------------- Состояние по чатам (в памяти + в файле) ----------------
# chat_id -> {"context": [сообщения], "last_topic": str, "mode": str, "ptype": str, "tz_notes": str}
# Сохраняется в файл, чтобы перезапуск сервиса не стирал диалог пользователя.
STATE = {}
STATE_LOCK = threading.Lock()
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


def save_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False)
    except Exception as e:
        log.error(f"save state: {e}")


def load_state():
    global STATE
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                STATE = loaded
    except FileNotFoundError:
        STATE = {}
    except Exception as e:
        log.error(f"load state: {e}")
        STATE = {}

# ---------------- Сервисы ----------------
def tg(method, **params):
    try:
        r = requests.post(f"{API}/{method}", data=params, timeout=20)
        return r.json()
    except Exception as e:
        log.error(f"tg {method}: {e}")
        return {}

def send(chat_id, text):
    # убираем длинные тире и звёздочки - глобальное правило чистого текста
    text = text.replace("*", "").replace("**", "")
    text = text.replace("—", "-").replace("–", "-").replace("−", "-")
    text = re.sub(r"\n{3,}", "\n\n", text)
    # очень длинный ответ разбиваем на части, чтобы не потерялся в Telegram
    if len(text) > 3900:
        parts = []
        while len(text) > 3900:
            cut = text.rfind("\n", 0, 3900)
            if cut < 3000:
                cut = 3900
            parts.append(text[:cut])
            text = text[cut:].lstrip("\n")
        parts.append(text)
        for p in parts:
            tg("sendMessage", chat_id=chat_id, text=p)
        return
    tg("sendMessage", chat_id=chat_id, text=text)

def ask_deepseek(messages, system):
    msgs = [{"role": "system", "content": system}] + messages
    try:
        r = requests.post(DEEPSEEK_API, json={
            "model": "deepseek-chat",
            "messages": msgs,
            "temperature": 0.8,
            "max_tokens": 1500,
        }, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}",
                    "Content-Type": "application/json"}, timeout=40)
        d = r.json()
        return d["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.error(f"deepseek: {e}")
        return None

SYSTEM_IDEA = (
    "Ты МегаМозг - генератор идей для нейрофабрики KISELEVY.CREO. "
    "На запрос пользователя выдай от 3 до 5 конкретных идей цифровых продуктов. "
    "Каждая идея в 1-2 короткие строки: название, для кого, что решает. "
    "ЖЁСТКО: максимально коротко, без воды, без длинных списков. "
    "Пиши по-русски. Запрещено: звёздочки, длинные тире, markdown."
)

# Профильные промпты под разные типы продуктов
SYSTEM_TZ_BOT = (
    "Ты МегаМозг - ведущий ТЗ-аналитик нейрофабрики KISELEVY.CREO. Ты не просто составитель документов, "
    "а старший эксперт с 10+ годами в разработке продуктов. Ты вёл десятки проектов и умеешь копать глубже."
    "Твоя задача - собрать МОЩНОЕ, продуманное ТЗ, за которое клиент заплатил бы и сдал в работу."
    "Веди диалог как живой эксперт, а не чат-бот:\n"
    "1. Каждый раз задавай ОДИН сильный наводящий вопрос. Спрашивай не шаблонно, а по сути: цель, "
    "болезнь пользователя, чем сейчас пользуется, какой результат хочет, откуда придёт клиент, "
    "что уже пробовал, бюджет, сроки. Копай глубже - так ты вытащишь реальные потребности.\n"
    "2. Не заваливай списком вопросов за раз. Один вопрос - жди ответ.\n"
    "3. Держи в голове полный контекст диалога и возвращайся к важным деталям. Если видишь слабое место "
    "в задаче - не молчи, а наводящим вопросом подсвети и предложи решение.\n"
    "4. Когда данных хватает - предложи 2 коротких варианта (MVP и расширенный) с плюсами/минусами в 1-2 строки.\n"
    "5. Собери ГОТОВОЕ ТЗ - КОРОТКО, по пунктам, без воды, как для разработчика-ассистента.\n\n"
    "ЖЁСТКОЕ ТРЕБОВАНИЕ К ОБЪЁМУ: финальное ТЗ максимум на 1 экран сообщения. Каждый пункт в 1 строку. \n"
    "Чтобы отличить финал от черновика: если ТЗ уже готово и полноценно - НЕ добавляй внизу фразы про черновой вариант. "
    "Если в ТЗ есть непроработанные места или ты сам чувствуешь, что можно докрутить - кратко предложи 1-2 "
    "конкретных улучшения вопросом. Не проси механически 'скажи что добавить'.\n\n"
    "СТРУКТУРА ИЗ 6 ПУНКТОВ (по одной строке каждый):\n"
    "1) Цель и для кого.\n"
    "2) Команды и логика по шагам.\n"
    "3) UX: приветствие, меню, кнопки.\n"
    "4) Оплата/подписки (если нужны).\n"
    "5) Стек: Python, DeepSeek, база, systemd.\n"
    "6) ЧТО МОЖНО ДОКИНУТЬ: кратко перечисли 3-5 идей (фичи/интеграции/монетизация), которые усилят продукт без лишних затрат.\n"
    "Пиши по-русски. Запрещено: звёздочки, длинные тире, markdown."
)

SYSTEM_TZ_FUNNEL = (
    "Ты МегаМозг - ведущий ТЗ-аналитик воронок (10+ лет).\n"
    "Веди коротко: уточни (цель, ЦА, что продаём, канал), предложи 2 коротких варианта, собери готовое ТЗ КОРОТКО.\n\n"
    "ЖЁСТКОЕ ТРЕБОВАНИЕ: финальное ТЗ максимум 1 экран, каждый пункт в 1 строку, без воды.\n\n"
    "СТРУКТУРА ИЗ 6 ПУНКТОВ:\n"
    "1) Цель и для кого.\n"
    "2) Этапы: холодный/тёплый/горячий.\n"
    "3) Тексты и CTA по этапам.\n"
    "4) Триггеры и тайминги сообщений.\n"
    "5) Интеграции (оплата, CRM) и метрики.\n"
    "6) ЧТО МОЖНО ДОКИНУТЬ: 3-5 идей усиления.\n"
    "Пиши по-русски. Запрещено: звёздочки, длинные тире, markdown."
)

SYSTEM_TZ_CONTENT = (
    "Ты МегаМозг - ведущий ТЗ-аналитик контент-систем (10+ лет).\n"
    "Веди коротко: уточни (цель, ЦА, канал, тон), предложи 2 коротких варианта сетки, собери готовое ТЗ КОРОТКО.\n\n"
    "ЖЁСТКОЕ ТРЕБОВАНИЕ: финальное ТЗ максимум 1 экран, каждый пункт в 1 строку, без воды.\n\n"
    "СТРУКТУРА ИЗ 6 ПУНКТОВ:\n"
    "1) Цель и для кого.\n"
    "2) Рубрики и сетка по дням на неделю.\n"
    "3) Форматы и tone of voice.\n"
    "4) Какие материалы нужны.\n"
    "5) График публикаций и автопостинг.\n"
    "6) ЧТО МОЖНО ДОКИНУТЬ: 3-5 идей усиления.\n"
    "Пиши по-русски. Запрещено: звёздочки, длинные тире, markdown."
)

SYSTEM_TZ_QUIZ = (
    "Ты МегаМозг - ведущий ТЗ-аналитик квизов и опросников (10+ лет).\n"
    "Веди коротко: уточни (цель, ЦА, что собираем, результат), предложи 2 коротких варианта, собери готовое ТЗ КОРОТКО.\n\n"
    "ЖЁСТКОЕ ТРЕБОВАНИЕ: финальное ТЗ максимум 1 экран, каждый пункт в 1 строку, без воды.\n\n"
    "СТРУКТУРА ИЗ 6 ПУНКТОВ:\n"
    "1) Цель квиза и для кого.\n"
    "2) Структура вопросов: сколько, логика ветвлений.\n"
    "3) Результат/вывод для пользователя.\n"
    "4) Подписка и оплата.\n"
    "5) UX и интеграции (CRM, email, оплата).\n"
    "6) ЧТО МОЖНО ДОКИНУТЬ: 3-5 идей усиления.\n"
    "Пиши по-русски. Запрещено: звёздочки, длинные тире, markdown."
)

SYSTEM_TZ = SYSTEM_TZ_BOT  # по умолчанию

# Промпт для аналитики ссылок: разбор сайта/бота/канала + ТЗ что внедрить
SYSTEM_ANALYZE = (
    "Ты МегаМозг - аналитик цифровых продуктов для нейрофабрики KISELEVY.CREO. "
    "Тебе дадут выжимку контента сайта, Telegram-бота или канала (или её описание). "
    "Выдай разбор по шагам:\n"
    "1) Что это за продукт, для кого, суть.\n"
    "2) Сильные стороны (что уже хорошо).\n"
    "3) Слабые места и что можно улучшить.\n"
    "4) Дополнительные советы и выводы (что добавить из практики, чтобы росло).\n"
    "5) Готовое техническое задание: конкретный список фич, что внедрить, по пунктам и цифрам, "
    "пригодное для ассистента-разработчика нейрофабрики (бот/воронка/контент/квиз и т.п.).\n"
    "Если контент по ссылке получить не удалось или он обрывочный - честно скажи об этом и "
    "дай разбор по тому, что видно в описании/метаданных, плюс советы вслепую.\n"
    "Пиши по-русски, коротко и по делу. Запрещено: звёздочки, длинные тире, markdown."
)

# ---------------- Аналитика ссылок ----------------
TG_PREVIEW = re.compile(r"t\.me/(\w+)")
URL_RE = re.compile(r"https?://[^\s]+")

HTML_STRIP = re.compile(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", re.S | re.I)
TAG_STRIP = re.compile(r"<[^>]+>")
MULTI_SPACE = re.compile(r"\s+")

HEADS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ru,en;q=0.8",
}


def clean_text(html):
    """Из HTML достаёт чистый текст: без скриптов, стилей и тегов."""
    html = HTML_STRIP.sub(" ", html or "")
    html = TAG_STRIP.sub(" ", html)
    txt = MULTI_SPACE.sub(" ", html)
    return txt.strip()


def fetch_site(url):
    """Скачивает сайт и возвращает чистый текст (обрезанный по лимиту)."""
    try:
        r = requests.get(url, headers=HEADS, timeout=20, verify=False)
        body = clean_text(r.text)
        # title из тега title, если есть
        m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
        title = m.group(1).strip() if m else ""
        return title, body[:6000]
    except Exception as e:
        log.error(f"fetch site {url}: {e}")
        return None, None


def fetch_tg_by_url(url):
    """Для ссылки на Telegram-канал/бот. По прямой ссылке контент закрыт,
    поэтому тянем публичный preview: username, title и описание.
    Для бота .bot/t.me/bot также вытаскиваем описание из веб-превью."""
    m = TG_PREVIEW.search(url)
    if not m:
        return None, None
    username = m.group(1)
    # пробуем получить публичную страницу /s/ (web preview)
    for fmt in (f"https://t.me/s/{username}", url):
        try:
            r = requests.get(fmt, headers=HEADS, timeout=20, verify=False)
            if r.status_code != 200:
                continue
            body = clean_text(r.text)
            if body:
                return username, body[:4000]
        except Exception as e:
            log.error(f"fetch tg {fmt}: {e}")
    return username, None


def analyze_url(chat_id, url):
    """Достаёт контент по ссылке, отдаёт DeepSeek с аналитическим промптом,
    присылает разбор + ТЗ. Возвращает строку с собранным контентом."""
    parsed = urlparse(url)
    is_tg = bool(TG_PREVIEW.search(url)) or "t.me" in parsed.netloc
    intro = f"Ссылка: {url}\n"

    tg("sendChatAction", chat_id=chat_id, action="typing")
    send(chat_id, "Открываю и изучаю...")

    if is_tg:
        username, content = fetch_tg_by_url(url)
        if content:
            intro += f"Объект: Telegram (@{username}). Описание/превью:\n{content}"
        else:
            intro += (f"Объект: Telegram (@{username}). Открытый контент недоступен "
                      f"(публичные сообщения канала скрыты для бота). Проанализируй по имени и "
                      f"дай советы, что обычно добавляют в такие каналы/боты.")
    else:
        title, content = fetch_site(url)
        if content:
            intro += f"Объект: сайт. Заголовок: {title or 'нет'}.\nКонтент:\n{content}"
        else:
            intro += (f"Объект: сайт. Прочитать страницу не удалось (возможно, защита от ботов "
                      f"или JS-heavy). Дай общие советы по улучшению такого типа сайта.")

    msgs = [{"role": "user", "content": intro}]
    out = ask_deepseek(msgs, SYSTEM_ANALYZE)
    if not out:
        send(chat_id, "Не смог проанализировать, попробуй ещё раз.")
        return intro
    # ещё одно сообщение со стимулом писать именно ТЗ, если модель его не дала
    send(chat_id, out)
    send(chat_id, "Итог при желании можно превратить в финальное ТЗ под нейрофабрику: набери /tz и вставь разбор.")
    return intro


def get_first_url(text):
    m = URL_RE.search(text)
    return m.group(0).rstrip(".),;") if m else None

# типы продуктов и их промпты
TYPES = {
    "bot": "Telegram-бот",
    "funnel": "Воронка / автоворонка",
    "content": "Контент-система / сетка",
    "quiz": "Опросник / квиз с подпиской",
}
TYPE_SYSTEMS = {
    "bot": SYSTEM_TZ_BOT,
    "funnel": SYSTEM_TZ_FUNNEL,
    "content": SYSTEM_TZ_CONTENT,
    "quiz": SYSTEM_TZ_QUIZ,
}

# ---------------- Обработка ----------------
def handle_start(chat_id):
    if chat_id not in AUTHORIZED:
        send(chat_id, "Этот бот личный и работает только у владельца.")
        return
    send(chat_id,
        "Привет, я МегаМозг - ведущий ТЗ-аналитик с 10+ лет опыта для нейрофабрики.")
    send(chat_id,
        "Собираю для тебя полные и рабочие ТЗ на ботов, воронки, контент и квизы. "
        "Веди меня: я сам задам вопросы, предложу варианты и соберу готовое ТЗ под разработку.\n\n"
        "Команды:\n"
        "/tz - составить ТЗ (я проведу тебя по шагам)\n"
        "/idea - накидать идеи по теме\n"
        "/analyze - разобрать сайт, бот или канал и написать ТЗ по нему: кидай ссылку\n"
        "/type - выбрать тип продукта (бот/воронка/контент/квиз)\n"
        "/clear - сброс")

def handle_text(chat_id, text):
    if chat_id not in AUTHORIZED:
        send(chat_id, "Этот бот личный и работает только у владельца.")
        return

    # авто-аналитика: если в сообщении есть ссылка на сайт/t.me - разбираем сразу
    url = get_first_url(text)
    if url and len(URL_RE.findall(text)) and not text.startswith("/"):
        analyze_url(chat_id, url)
        return

    with STATE_LOCK:
        st = STATE.setdefault(chat_id, {"context": [], "mode": "idea"})
        st["context"].append({"role": "user", "content": text})
        st["context"] = st["context"][-30:]
        mode = st["mode"]
        last_topic = text

    system = SYSTEM_IDEA if mode == "idea" else TYPE_SYSTEMS.get(st.get("ptype"), SYSTEM_TZ_BOT)
    # сообщение о работе
    tg("sendChatAction", chat_id=chat_id, action="typing")
    out = ask_deepseek(st["context"], system)
    if not out:
        send(chat_id, "Не смог сгенерировать, попробуй ещё раз.")
        return
    with STATE_LOCK:
        st = STATE.setdefault(chat_id, {"context": [], "mode": "idea"})
        st["context"].append({"role": "assistant", "content": out})
        st["context"] = st["context"][-30:]
        st["last_topic"] = last_topic
        save_state()
    send(chat_id, out)
    # в режиме ТЗ пусть бот сам решит по системному промпту: либо задаст уточняющий вопрос,
    # либо предложит докрутить, либо подтвердит что ТЗ готово. Тут не досылаем жёсткий текст.

def main():
    load_state()  # восстанавливаем диалоги после рестарта
    log.info("МегаМозг бот запущен")
    # персистентный offset чтобы не дублировать ответы после рестарта
    offset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_offset.txt")
    offset = None
    try:
        with open(offset_file) as f:
            offset = int(f.read().strip())
    except Exception:
        pass

    # первый проход: если offset неизвестен - проглотить всё без ответа
    first_pass = offset is None

    while True:
        try:
            params = {"timeout": 40, "offset": None if first_pass else offset}
            r = requests.get(f"{API}/getUpdates", params=params, timeout=60)
            d = r.json()
            if not d.get("ok"):
                time.sleep(2)
                continue
            for upd in d.get("result", []):
                new_id = upd["update_id"]
                offset = new_id + 1
                with open(offset_file, "w") as f:
                    f.write(str(offset))
                if first_pass:
                    continue  # не отвечаем на старые
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = msg.get("text")
                if not text:
                    continue
                with STATE_LOCK:
                    st = STATE.setdefault(chat_id, {"context": [], "mode": "idea"})
                if text.startswith("/"):
                    cmd = text.split()[0]
                    rest = text[len(cmd):].strip()
                    if cmd == "/start":
                        handle_start(chat_id)
                    elif cmd in ("/analyze", "/analiz", "/разбор"):
                        url = get_first_url(rest) if rest else None
                        if not url:
                            send(chat_id, "Кидай ссылку на сайт, Telegram-бот или канал, например:\n/analyze https://example.com\nили просто пришли ссылку - я разберу.")
                        else:
                            analyze_url(chat_id, url)
                    elif cmd in ("/idea", "/ideas"):
                        st["mode"] = "idea"
                        save_state()
                        send(chat_id, "Режим: генерация идей. Напиши тему.")
                    elif cmd == "/tz":
                        st["mode"] = "tz"
                        st["context"] = [{"role": "user", "content": "Составь техническое задание. Начни как профессионал: кратко поприветствуй по делу и задай ПЕРВЫЙ уточняющий вопрос, чтобы понять продукт, для которого делать ТЗ. Задавай по одному вопросу за раз, коротко."}]
                        save_state()
                        send(chat_id, "Режим: составление ТЗ. Я как ведущий аналитик (10+ лет опыта) проведу тебя по шагам. Сначала уточню детали, потом предложу варианты, и в конце соберу чистовое ТЗ.\n\nНачнём: опиши, что ты хочешь сделать (например, бот для продаж, воронка, опросник), и я задам первый вопрос.")
                    elif cmd == "/type":
                        st["mode"] = "type"
                        save_state()
                        send(chat_id, "Выбери тип продукта цифрой:\n1 - Telegram-бот\n2 - Воронка / автоворонка\n3 - Контент-система / сетка\n4 - Опросник / квиз с подпиской\n\nНапиши 1, 2, 3 или 4.")
                    elif cmd == "/clear":
                        st["context"] = []
                        save_state()
                        send(chat_id, "Контекст сброшен.")
                    else:
                        send(chat_id, "Неизвестная команда. Доступно: /start, /idea, /tz, /type, /clear.")
                elif st.get("mode") == "type":
                    # выбор типа продукта
                    tmap = {"1": "bot", "2": "funnel", "3": "content", "4": "quiz"}
                    key = tmap.get(text.strip())
                    if key:
                        st["ptype"] = key
                        st["mode"] = "tz"
                        save_state()
                        send(chat_id, f"Тип: {TYPES[key]}. Напиши тему - соберу ТЗ.")
                    else:
                        send(chat_id, "Напиши цифру 1, 2, 3 или 4.")
                else:
                    handle_text(chat_id, text)
            first_pass = False
            time.sleep(1)
        except Exception as e:
            log.error(f"main loop: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
