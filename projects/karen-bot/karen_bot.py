#!/usr/bin/env python3
"""
@Karen_bro_bot — Нейропомощник Карена (видеограф)
Психолог-коуч + ежедневный помощник.
- 7 дней бесплатно с момента старта
- потом оплата (Карен переводит Артуру на карту) -> админ продлевает командой
"""

import json, sqlite3, datetime, os, sys, re, time, requests, threading

TOKEN = "8000724913:AAEFlulMIGgGJ3AciXdYNv4WvHv9aeCYn4E"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# DeepSeek — дёшево и надёжно
DEEPSEEK_KEY = None
for p in ["~/.openclaw-neuro/.deepseek_key", "/root/.openclaw-neuro/.deepseek_key"]:
    fp = os.path.expanduser(p)
    if os.path.exists(fp):
        DEEPSEEK_KEY = open(fp).read().strip()
        break
DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

# Админы (Артур) и допущенные пользователи
# ONLY эти chat_id могут пользоваться ботом. Остальные получают отказ.
ALLOW_FILE = "/root/karen-bot/data/allowed.json"

def load_allowed():
    try:
        with open(ALLOW_FILE) as f:
            data = json.load(f)
            return set(data.get("allowed", []))
    except Exception:
        return set()

def save_allowed():
    try:
        with open(ALLOW_FILE, "w") as f:
            json.dump({"allowed": sorted(ALLOWED)}, f)
    except Exception as e:
        print("save_allowed err:", e)

ALLOWED = set(load_allowed())
ALLOWED.add(199790247)   # Артур — всегда есть доступ
ADMINS = {199790247}

# Настройки
DB_PATH = "/root/karen-bot/data/karen_data.db"
TRIAL_DAYS = 7            # бесплатный период
LIFETIME_PRICE = "5000"   # разовая цена за пожизненный доступ (текст для Карена)

# ========== SQLite ==========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        chat_id INTEGER PRIMARY KEY,
        name TEXT,
        profession TEXT,
        goals TEXT,
        started_at TEXT,
        paid_until TEXT,
        lifetime INTEGER DEFAULT 0,   -- 1 = оплачено навсегда
        status TEXT DEFAULT 'active',
        last_morning TEXT,
        last_evening TEXT,
        history TEXT DEFAULT '[]'
    )""")
    # Полная история переписки для каждого пользователя
    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,               -- 'user' | 'assistant'
        text TEXT,
        ts TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, id)")
    # Личная память: факты о пользователе (имя, проекты, клиенты, предпочтения)
    c.execute("""CREATE TABLE IF NOT EXISTS facts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        fact TEXT,
        ts TEXT
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_facts_chat ON facts(chat_id)")
    conn.commit()
    conn.close()

# ===== Полная история переписки =====
def save_message(chat_id, role, text):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("INSERT INTO messages(chat_id, role, text, ts) VALUES(?,?,?,?)",
                  (chat_id, role, text, datetime.datetime.now().isoformat()))
        conn.commit(); conn.close()
    except Exception as e:
        print("save_message err:", e)

def get_history(chat_id, limit=40):
    try:
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT role, text FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit))
        rows = c.fetchall(); conn.close()
        hist = list(reversed([dict(r) for r in rows]))
        return hist
    except Exception as e:
        print("get_history err:", e)
        return []

# ===== Личная память (факты) =====
def get_facts(chat_id):
    try:
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT fact FROM facts WHERE chat_id=? ORDER BY id DESC LIMIT 50", (chat_id,))
        rows = c.fetchall(); conn.close()
        return [r['fact'] for r in rows]
    except Exception:
        return []

def save_fact(chat_id, fact):
    try:
        # не дублируем одинаковые факты
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM facts WHERE chat_id=? AND fact=?", (chat_id, fact))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO facts(chat_id, fact, ts) VALUES(?,?,?)",
                      (chat_id, fact, datetime.datetime.now().isoformat()))
            conn.commit()
        conn.close()
    except Exception as e:
        print("save_fact err:", e)

def get_user(chat_id):
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    r = c.fetchone(); conn.close()
    return dict(r) if r else None

def save_user(u):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO users(chat_id,name,profession,goals,started_at,paid_until,lifetime,status,last_morning,last_evening,history)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (u['chat_id'], u.get('name'), u.get('profession'), u.get('goals'),
               u.get('started_at'), u.get('paid_until'), u.get('lifetime',0), u.get('status','active'),
               u.get('last_morning'), u.get('last_evening'), u.get('history')))
    conn.commit(); conn.close()

init_db()

# ========== DeepSeek ==========
def _now():
    """Текущие реальные дата и время сервера (живой момент)."""
    now = datetime.datetime.now()
    wd = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"][now.weekday()]
    return now.strftime(f"%d.%m.%Y год | {wd} | %H:%M UTC")

def ask_deepseek(messages, temperature=0.7, max_tokens=700):
    if not DEEPSEEK_KEY:
        return "Пока не подключена нейросеть. Напиши мне позже 😊"
    # живая дата/время к системному сообщению
    msgs = list(messages)
    now_line = f"Сейчас реальный момент: {_now()}."
    for i, m in enumerate(msgs):
        if m.get("role") == "system":
            msgs[i] = {"role": "system", "content": m["content"] + "\n" + now_line}
            break
    else:
        msgs.insert(0, {"role": "system", "content": now_line})
    try:
        r = requests.post(DEEPSEEK_API, headers={
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }, json={
            "model": "deepseek-chat",
            "messages": msgs,
            "temperature": temperature,
            "max_tokens": max_tokens
        }, timeout=60)
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("DeepSeek error:", e)
        return "Чуток завис, дай секунду. Попробуй ещё раз 🙏"

SYSTEM_PROMPT = """Ты — Карен Бро, персональный нейропсихолог, коуч и ежедневный помощник Карена — видеографа и фотографа.

ТВОЯ ЛИЧНОСТЬ:
- Ты тёплый, мудрый друг с опытом психолога и коуча. Понимаешь творческих людей.
- Карен — видеограф, снимает видео и фото. У него бывают: дедлайны по проектам, творческие ступоры, страх "пустого листа", перегрузки, прокрастинация, сравнение себя с другими.
- Ты помогаешь не только с работой, но и по жизни: режим, энергия, фокус, отдых, вдохновение.

КАК ОБЩАЕШЬСЯ:
- Обращайся к Карену на "ты", по имени. Никогда не "вы" и не "Карен Бро" в обращении.
- Говори по-русски. Спокойно, тепло, без воды. Не длинно, но содержательно.
- Эмодзи умеренно: 🎬📸⚡🧠🎯🔥💡✨
- Ты не "искусственный интеллект" — ты его надёжный помощник-друг.
- Если Карен устал/выгорел — не говори "просто отдохни". Спроси: "Что именно давит сейчас? Разложи по полочкам." Дай конкретные микрошаги (5-15 мин).
- Если он в ступоре по съёмке/монтажу — помоги разбить задачу на маленькие кусочки, предложи начать с самого простого.

ТВОИ ФУНКЦИИ:
- Планирование дня: приоритеты, 3 главных дела, микрошаги.
- Психолог: фокус, энергия, тревога, мотивация, творческий блок.
- Помощь по делу: идеи для съёмок, структура проекта, подготовка, клиенты, портфолио.
- Режим: напоминай про отдых, сон, воду, движение.

ЕЖЕДНЕВНО:
1. Утро: приветствие + план дня + 1 короткий совет психолога.
2. Вечер: итоги дня + рефлексия + вопрос "что завтра важно".

ПАМЯТЬ:
- У тебя БЕССМЕРТНАЯ память. Ты помнишь ВСЁ, о чём говорил с Кареном раньше, в любой сессии.
- Ниже даны "Личные факты о Карене" — используй их, обращайся к ним.
- Если Карен рассказал что-то важное (имя, проект, клиента, дату, предпочтения, планы, проблемы) — запомни это:
  после ответа выведи строку [FACT] важный факт из его сообщения[/FACT], чтобы я мог сохранить.
- Не переспрашивай то, что уже знаешь. Показывай, что помнишь. Это его личный умный ассистент.

Всегда заканчивай вечернее сообщение вопросом для рефлексии."""

MEMORY_EXTRACT_PROMPT = """Ты — модуль памяти ассистента. Из сообщения пользователя (видеограф) извлеки ЛЮБЫЕ устойчивые факты, которые стоит запомнить насовсем:
- Имя, возраст, город
- Проекты, клиенты, заказы, съёмки (что снимает, для кого, дедлайны)
- Предпочтения, оборудование, любимые стили
- Планы, цели, мечты
- Проблемы, страхи, важные события в жизни

Верни ТОЛЬКО список фактов, каждый с новой строки, без нумерации и без пояснений.
Если важных фактов нет — верни пустую строку."""

def extract_facts(chat_id, user_text):
    """Автоматически извлекает и сохраняет устойчивые факты из сообщения."""
    try:
        # Не извлекаем факты из служебных автосообщений
        if user_text.startswith("[") and ("] ") in user_text[:8]:
            return
        msgs = [
            {"role": "system", "content": MEMORY_EXTRACT_PROMPT},
            {"role": "user", "content": user_text}
        ]
        out = ask_deepseek(msgs, temperature=0.2, max_tokens=250)
        for line in out.split("\n"):
            line = line.strip()
            # пропускаем пустые и служебные
            if not line or line.startswith("["):
                continue
            if len(line) < 4:
                continue
            save_fact(chat_id, line)
    except Exception as e:
        print("extract_facts err:", e)

def ai_reply(chat_id, user_text):
    u = get_user(chat_id) or {}
    name = u.get('name') or 'Карен'

    # Сохраняем сообщение пользователя
    save_message(chat_id, 'user', user_text)

    # Извлекаем и сохраняем устойчивые факты
    extract_facts(chat_id, user_text)
    facts = get_facts(chat_id)

    # Собираем полный SYSTEM-промпт с памятью
    memory_block = "\n".join(f"• {f}" for f in facts) if facts else "(пока пусто)"
    sys_prompt = SYSTEM_PROMPT + f"\n\nЛИЧНЫЕ ФАКТЫ О КАРЕНЕ:\n{memory_block}"
    messages = [{"role": "system", "content": sys_prompt}]

    # Подтягиваем историю переписки (последние 40 сообщений)
    hist = get_history(chat_id, limit=40)
    for h in hist:
        messages.append(h)
    if len(hist) and hist[-1]["role"] == "user":
        pass
    else:
        messages.append({"role": "user", "content": user_text})
    messages.append({"role": "user", "content": f"(продолжение, последнее сообщение {name}): {user_text}"})

    ans = ask_deepseek(messages)
    save_message(chat_id, 'assistant', ans)
    return ans

# ========== Доступ / оплата ==========
def parse_date(s):
    return datetime.datetime.fromisoformat(s) if s else None

def is_active(u):
    if not u: return True
    if u.get('lifetime'): return True   # оплачено навсегда
    start = parse_date(u.get('started_at'))
    paid = parse_date(u.get('paid_until'))
    now = datetime.datetime.now()
    if paid and paid > now: return True
    if start and (now - start).days < TRIAL_DAYS: return True
    return False

def days_left(u):
    if not u: return TRIAL_DAYS
    if u.get('lifetime'): return 999999   # навсегда
    start = parse_date(u.get('started_at'))
    paid = parse_date(u.get('paid_until'))
    now = datetime.datetime.now()
    if paid and paid > now: return (paid - now).days
    if start and (now - start).days < TRIAL_DAYS: return TRIAL_DAYS - (now - start).days
    return 0

def send(chat_id, text, kb=None):
    d = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb: d["reply_markup"] = json.dumps({"inline_keyboard": kb})
    try: requests.post(f"{API_URL}/sendMessage", json=d, timeout=30)
    except Exception as e: print("send err:", e)

def main_menu():
    return [[{"text":"🎯 План на день","callback_data":"plan"},
             {"text":"💭 Самочувствие","callback_data":"mood"}],
            [{"text":"⚡ Мозговой штурм","callback_data":"ideas"},
             {"text":"🎬 Идея для съёмки","callback_data":"shoot"}],
            [{"text":"📝 Записать мысль/задачу","callback_data":"note"}]]

TRIAL_END_MSG = ("⏳ <b>Бесплатный период закончился.</b>\n\n"
                 "Отлично поработали 7 дней! Чтобы я продолжал помогать тебе и дальше, "
                 f"переведи разовую оплату (<b>{LIFETIME_PRICE}₽</b>) Артуру на карту. Это <b>одна</b> оплата — доступ навсегда. 🙌\n\n"
                 "После перевода напиши боту <b>/продлить</b> — как только Артур подтвердит, доступ откроется навсегда.")

def handle_start(chat_id, first_name=None):
    u = get_user(chat_id)
    if not u:
        # Первое касание — создаём запись сразу, имя запросим
        u = {
            'chat_id': chat_id,
            'name': '',
            'profession': '',
            'goals': '',
            'started_at': None,   # старт 7-дневного периода — при сохранении имени
            'paid_until': None,
            'lifetime': 0,
            'status': 'active',
            'last_morning': None,
            'last_evening': None,
            'history': '[]',
        }
        save_user(u)
    if u.get('name'):
        if is_active(u):
            dl = days_left(u)
            if u.get('lifetime'):
                send(chat_id, f"С возвращением, {u['name']}! 👋 Доступ у тебя навсегда. Чем помогу?", main_menu())
            else:
                send(chat_id, f"С возвращением, {u['name']}! 👋 Осталось бесплатных дней: <b>{dl}</b>.\nЧем помогу?", main_menu())
        else:
            send(chat_id, TRIAL_END_MSG)
        return
    send(chat_id, "🎬 Привет! Я — <b>Карен Бро</b>, твой персональный нейропсихолог и помощник на каждый день.\n\nЯ помогаю видеографам и фотографам: держу фокус, планирую день, вытаскиваю из творческих ступоров, слежу за режимом и зарядом.\n\n<b>7 дней — бесплатно</b> 🎁\n\nКак тебя зовут?")
    send(chat_id, "✳️ Напиши просто имя, например: <i>Карен</i>")

# ========== Команды ==========
def handle_cmd(chat_id, text, first_name=None):
    low = text.strip().lower()

    if low == "/start":
        handle_start(chat_id, first_name); return

    # Админ-команды
    if chat_id in ADMINS:
        if low.startswith("/pay"):
            parts = text.split()
            if len(parts) >= 2:
                try:
                    uid = int(parts[1])
                    u = get_user(uid)
                    if not u:
                        send(chat_id, "Пользователь не найден. Пусть сначала напишет боту /start.")
                        return
                    u['lifetime'] = 1
                    u['status'] = 'active'
                    save_user(u)
                    send(uid, "✅ Оплата подтверждена! Доступ для тебя теперь <b>навсегда</b> 🎉 Работаем дальше! 💪")
                    send(chat_id, f"✅ {u.get('name') or uid} получил пожизненный доступ навсегда.")
                except Exception as e:
                    send(chat_id, f"Ошибка: {e}")
            else:
                send(chat_id, "Формат: <code>/pay &lt;chat_id&gt;</code> (пожизненный доступ)")
            return
        if low.startswith("/status"):
            conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
            c = conn.cursor(); c.execute("SELECT * FROM users")
            rows = c.fetchall(); conn.close()
            if not rows:
                send(chat_id, "Пользователей пока нет."); return
            out = "👥 <b>Пользователи:</b>\n"
            for r in rows:
                u = dict(r)
                if u.get('lifetime'):
                    st = "♾️ навсегда"
                else:
                    st = f"{days_left(u)} дн."
                act = "🟢" if is_active(u) else "🔴"
                out += f"{act} {u.get('name') or u['chat_id']} (id {u['chat_id']}): {st}\n"
            send(chat_id, out)
            return
        if low.startswith("/unlock"):
            # /unlock chat_id — пожизненный доступ (синоним /pay)
            parts = text.split()
            if len(parts) >= 2:
                handle_cmd(chat_id, "/pay " + parts[1])
            else:
                send(chat_id, "Формат: <code>/unlock &lt;chat_id&gt;</code>")
            return
        if low.startswith("/allow"):
            # /allow chat_id — допустить пользователя в whitelist
            parts = text.split()
            if len(parts) >= 2:
                try:
                    uid = int(parts[1])
                    ALLOWED.add(uid)
                    # также записываем в whitelist-файл, чтобы пережить рестарт
                    save_allowed()
                    send(chat_id, f"✅ Пользователь {uid} допущен к боту.")
                except Exception as e:
                    send(chat_id, f"Ошибка: {e}")
            else:
                send(chat_id, "Формат: <code>/allow &lt;chat_id&gt;</code>")
            return

    # Пользовательские команды
    if low == "/продлить" or low == "/prodli" or low == "/renew":
        u = get_user(chat_id)
        if not u:
            handle_start(chat_id, first_name); return
        if is_active(u):
            send(chat_id, f"У тебя всё отлично — доступ активен{" навсегда 😎" if u.get('lifetime') else f", осталось {days_left(u)} дн. бесплатного периода"}.")
        else:
            send(chat_id, f"Для доступа: переведи разовую оплату ({LIFETIME_PRICE}₽) Артуру на карту, затем напиши <b>/продлить</b> ещё раз. Как только Артур подтвердит — доступ откроется <b>навсегда</b>. 🙌")
        return

    # Обработка имени (первый шаг)
    u = get_user(chat_id)
    if u and not u.get('name') and not u.get('started_at'):
        u['name'] = text.strip()[:40]
        u['profession'] = "видеограф / фотограф"
        u['started_at'] = datetime.datetime.now().isoformat()
        u['goals'] = ""
        save_user(u)
        # Запоминаем в личную память
        save_fact(chat_id, f"Имя пользователя: {u['name']}")
        save_fact(chat_id, "Профессия: видеограф и фотограф")
        send(chat_id, f"Приятно познакомиться, {u['name']}! 🎬\n\nТы видеограф и фотограф — я учту это и буду помнить всегда.\n\nНачнём? Жми кнопку или просто пиши мне о своих задачах, мыслях, настроении — я всегда рядом. 💪",
             main_menu())
        return

    # Команда показать память
    if low == "/memory" or low == "/память":
        u = get_user(chat_id)
        if not u or not u.get('name'):
            send(chat_id, "Сначала давай познакомимся: напиши /start и представься 🙌")
            return
        facts = get_facts(chat_id)
        hist = get_history(chat_id, limit=20)
        if facts or hist:
            lines = ["🧠 <b>Что я помню о тебе:</b>"]
            for f in facts:
                lines.append(f"• {f}")
            if hist:
                lines.append("\n📜 <b>Последний диалог:</b>")
                for h in hist[-6:]:
                    who = "Ты" if h['role'] == 'user' else "Я"
                    txt = h['text'].replace("\n", " ")[:80]
                    lines.append(f"<i>{who}:</i> {txt}")
            send(chat_id, "\n".join(lines))
        else:
            send(chat_id, "Пока о тебе ничего не записано. Расскажи о себе, своих проектах — я всё запомню! 🎬")
        return

    # Обслуживание: кнопки и текст описаны ниже; здесь стандартный пропуск неактивных
    if not u or not u.get('name'):
        handle_start(chat_id, first_name); return

    if not is_active(u):
        send(chat_id, TRIAL_END_MSG)
        return

    resp = ai_reply(chat_id, text)
    send(chat_id, resp)

# ========== Callback-кнопки ==========
def handle_cb(chat_id, cb):
    u = get_user(chat_id)
    if not is_active(u):
        send(chat_id, TRIAL_END_MSG); return
    prompts = {
        "plan": "Составь мне план на сегодня. Я видеограф. Дай 3 главных дела и микрошаги по 5-15 минут, учти отдых.",
        "mood": "Спроси у меня как я себя чувствую сейчас. Дай поддержку и 2 конкретных совета, если нужно.",
        "ideas": "Сделай со мной мозговой штурм для моего видео/фото проекта. Задай пару уточняющих вопросов и предложи 5 идей.",
        "shoot": "Предложи мне 3 конкретные идеи для съёмки (видео или фото) с описанием: сюжет, свет, ракурс, монтаж.",
        "note": "Запиши важное. Скажи мне, что записать — и я сохраню твои мысли и задачи на будущее.",
    }
    p = prompts.get(cb, "Помоги мне с текущей задачей.")
    resp = ai_reply(chat_id, "[кнопка] " + p)
    send(chat_id, resp, main_menu())

def notify_trial_end(chat_id):
    send(chat_id, TRIAL_END_MSG)

# ========== Ежедневные автосообщения ==========
def daily_jobs():
    while True:
        try:
            now = datetime.datetime.now()
            hm = now.strftime("%H:%M")
            date_key = now.strftime("%Y-%m-%d")
            conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
            c = conn.cursor(); c.execute("SELECT * FROM users")
            rows = c.fetchall(); conn.close()
            for r in rows:
                u = dict(r)
                cid = u['chat_id']
                if not u.get('name'): continue
                if not is_active(u):
                    # если период кончился сегодня и не уведомляли ещё — уведомить
                    notify_trial_end(cid)
                    continue
                if hm == "09:00" and u.get('last_morning') != date_key:
                    resp = ai_reply(cid, "[утро] Составь план на день для видеографа. 3 главных дела, микрошаги, 1 совет психолога.")
                    send(cid, f"☀️ <b>Доброе утро, {u['name']}!</b> Вот твой план:\n\n{resp}")
                    u['last_morning'] = date_key; save_user(u)
                if hm == "21:00" and u.get('last_evening') != date_key:
                    resp = ai_reply(cid, "[вечер] Подведи итоги дня. Спроси что получилось, что не получилось без самокритики, и что важно сделать завтра. Закончи вопросом для рефлексии.")
                    send(cid, f"🌙 <b>Вечер, {u['name']}.</b>\n\n{resp}")
                    u['last_evening'] = date_key; save_user(u)
        except Exception as e:
            print("daily err:", e)
        time.sleep(45)

# ========== Polling ==========
last_update = None

def handle(cid, fn, *args):
    # Белый список: только допущенные могут пользоваться ботом
    if cid not in ALLOWED:
        send(cid, "⛔ Доступ ограничен. Этот бот — персональный помощник, и работает он только у своего владельца.")
        return
    threading.Thread(target=fn, args=(cid,)+args, daemon=True).start()

def poll():
    global last_update
    while True:
        try:
            off = last_update + 1 if last_update is not None else None
            params = {"timeout": 30, "offset": off}
            r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=40)
            data = r.json()
            if not data.get("ok"): continue
            for upd in data["result"]:
                last_update = upd["update_id"]
                msg = upd.get("message")
                cb = upd.get("callback_query")
                if cb:
                    m = cb.get("message") or {}
                    cid = (m.get("chat") or {}).get("id")
                    data_cb = cb.get("data")
                    if cid:
                        handle(cid, handle_cb, data_cb)
                    continue
                if not msg: continue
                chat = msg.get("chat") or {}
                cid = chat.get("id")
                text = msg.get("text")
                fname = chat.get("first_name")
                if not cid or not text: continue
                handle(cid, handle_cmd, text, fname)
        except Exception as e:
            print("poll err:", e)
            time.sleep(3)

if __name__ == "__main__":
    print("Karen_bro_bot started")
    threading.Thread(target=daily_jobs, daemon=True).start()
    poll()
