# -*- coding: utf-8 -*-
"""
Клиника Рядом - работа с PostgreSQL.
Единая база для ВСЕХ 7 ботов (главный + 6 врачей).
"""
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import config

DB_DSN = "host=127.0.0.1 dbname=clinic_ryadom user=clinic_ryadom password=clinic_ryadom_2026"

TODAY = datetime.date.today


CONNECT_TIMEOUT = 6   # сек, чтобы не зависать если база лежит
DB_RETRIES = 3          # попыток при временной недоступности
DB_RETRY_SLEEP = 1.0    # пауза между попытками


def get_conn():
    """Подключение с таймаутом и повторами при временном сбое базы."""
    last = None
    for attempt in range(1, DB_RETRIES + 1):
        try:
            conn = psycopg2.connect(
                DB_DSN, cursor_factory=RealDictCursor, connect_timeout=CONNECT_TIMEOUT
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            last = e
            if attempt < DB_RETRIES:
                time.sleep(DB_RETRY_SLEEP)
    raise last


# ------------------------------ users ------------------------------
def ensure_user(user_id, username, first_name):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO users (user_id, username, first_name)
               VALUES (%s,%s,%s)
               ON CONFLICT (user_id) DO UPDATE
               SET username=EXCLUDED.username, first_name=EXCLUDED.first_name""",
            (user_id, username, first_name),
        )


# ------------------------------ client card ---------------------------
def get_card(user_id):
    """Вернёт карточку клиента (dict) или None."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM client_card WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def card_completed(user_id):
    """Только если пользователь заполнил всю карточку."""
    card = get_card(user_id)
    if not card:
        return False
    return bool(card.get("completed"))


def set_card_completed(user_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE client_card SET completed=TRUE, updated_at=now() WHERE user_id=%s",
            (user_id,),
        )


def save_card_field(user_id, field, value):
    """Пишет одно поле карточки. Создаёт строку при отсутствии."""
    col = {
        "имя": "full_name",
        "возраст": "age",
        "пол": "gender",
        "хронические_заболевания": "chronics",
        "жалобы": "complaints",
    }.get(field)
    if not col:
        return
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO client_card (user_id, {col})
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET {col}=EXCLUDED.{col}, updated_at=now()""",
            (user_id, value),
        )


def card_to_prompt(user_id):
    """Формирует строку-контекст карточки для передачи врачу."""
    card = get_card(user_id)
    if not card or not card.get("completed"):
        return ""
    parts = []
    if card.get("full_name"):
        parts.append(f"Имя: {card['full_name']}")
    if card.get("age"):
        parts.append(f"Возраст: {card['age']}")
    if card.get("gender"):
        parts.append(f"Пол: {card['gender']}")
    if card.get("chronics"):
        parts.append(f"Хронические заболевания: {card['chronics']}")
    if card.get("complaints"):
        parts.append(f"Общие жалобы: {card['complaints']}")
    if not parts:
        return ""
    return "Карточка клиента: " + "; ".join(parts) + "."


# ---------------------------- consent ------------------------------
# bot_id - идентификатор проекта/бота, к которому относится согласие.
# Согласие в другом боте (клиника140, иное) НЕ покрывает этот бот.
BOT_ID = "clinic-ryadom"


def consent_done(user_id, bot_id=BOT_ID, policy_version=None):
    """Вернёт True, если пользователь согласился с политикой И дисклеймером
    И данным о здоровье ИМЕННО для bot_id. Если указана policy_version,
    согласие засчитывается только если оно получено под этой версией (re-consent)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT policy_agreed, disclaimer_agreed, health_data_agreed, policy_version
               FROM consent WHERE user_id=%s AND bot_id=%s""",
            (user_id, bot_id),
        )
        row = cur.fetchone()
    if not row:
        return False
    ok = bool(row["policy_agreed"] and row["disclaimer_agreed"] and row["health_data_agreed"])
    if policy_version and ok:
        # Текущая версия политики должна совпадать, иначе нужен re-consent
        ok = str(row["policy_version"]) == str(policy_version)
    return ok


def mark_consent(user_id, bot_id=BOT_ID, policy_version=None):
    """Фиксирует согласие И стартует триал (7 дней), если он ещё не стартовал.
    policy_version - версия текста политики, под которой получено согласие."""
    version = policy_version or config.POLICY_VERSION
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO consent (user_id, bot_id, policy_version, policy_agreed,
                                    disclaimer_agreed, health_data_agreed, consent_date, agreed_at)
               VALUES (%s, %s, %s, TRUE, TRUE, TRUE, now(), now())
               ON CONFLICT (user_id, bot_id) DO UPDATE
               SET policy_version=EXCLUDED.policy_version,
                   policy_agreed=TRUE, disclaimer_agreed=TRUE,
                   health_data_agreed=TRUE, consent_date=now(), agreed_at=now()""",
            (user_id, bot_id, version),
        )
    # Стартуем триал только если он ещё не был начат
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT trial_started_at, trial_end_at FROM consent WHERE user_id=%s AND bot_id=%s",
            (user_id, bot_id),
        )
        row = cur.fetchone()
    if row and row["trial_started_at"] is None:
        start_trial(user_id, bot_id)
    return True


def start_trial(user_id, bot_id=BOT_ID):
    """Начинает триал на TRIAL_DAYS от текущего момента."""
    import datetime
    end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=config.TRIAL_DAYS)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE consent
               SET trial_started_at=now(), trial_end_at=%s
               WHERE user_id=%s AND bot_id=%s""",
            (end, user_id, bot_id),
        )
    return True


def trial_info(user_id, bot_id=BOT_ID):
    """Вернёт (trial_active, trial_end) или (False, None) если нет триала."""
    import datetime
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT trial_started_at, trial_end_at FROM consent WHERE user_id=%s AND bot_id=%s",
            (user_id, bot_id),
        )
        row = cur.fetchone()
    if not row or not row["trial_started_at"]:
        return False, None
    end = row["trial_end_at"]
    if end and end > datetime.datetime.now(datetime.timezone.utc):
        return True, end
    return False, end


# -------------------------- subscriptions ---------------------------
def subscription_status(user_id):
    """Вернёт: 'active' | 'expired' | 'none' | 'pending'."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT status, date_end, paid FROM subscriptions WHERE user_id=%s",
            (user_id,),
        )
        row = cur.fetchone()
    if not row:
        return "none"
    if row["status"] == "pending":
        return "pending"
    if row["status"] == "active":
        if row["date_end"] and row["date_end"] < datetime.datetime.now(datetime.timezone.utc):
            return "expired"
        return "active"
    return row["status"] or "none"


def create_pending_subscription(user_id):
    """Создаёт абонемент в статусе ожидания оплаты (заглушка + реальная оплата)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO subscriptions (user_id, status, paid)
               VALUES (%s, 'pending', FALSE)
               ON CONFLICT (user_id) DO UPDATE SET status='pending', paid=FALSE""",
            (user_id,),
        )
    return True


def activate_subscription(user_id, days=30):
    """Активирует абонемент на N дней от текущего момента."""
    end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO subscriptions (user_id, status, paid, date_start, date_end)
               VALUES (%s,'active',TRUE,now(),%s)
               ON CONFLICT (user_id) DO UPDATE
               SET status='active', paid=TRUE, date_start=now(), date_end=EXCLUDED.date_end""",
            (user_id, end),
        )
    return True


# -------------------------- chat history ----------------------------
def save_message(user_id, doctor_key, role, content, photo_file=None):
    """Каждое сообщение сразу пишется в базу (история НИКОГДА не теряется)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO chat_history (user_id, doctor_key, role, content, photo_file)
               VALUES (%s,%s,%s,%s,%s)""",
            (user_id, doctor_key, role, content, photo_file),
        )


def get_history(user_id, doctor_key, limit=40):
    """Возвращает последние N сообщений диалога пользователя с врачом."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT role, content FROM chat_history
               WHERE user_id=%s AND doctor_key=%s
               ORDER BY created_at DESC LIMIT %s""",
            (user_id, doctor_key, limit),
        )
        rows = cur.fetchall()
    rows.reverse()  # хронологический порядок
    return rows


def clear_history(user_id, doctor_key):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chat_history WHERE user_id=%s AND doctor_key=%s",
            (user_id, doctor_key),
        )


# -------------------------- daily limits ----------------------------
def get_today_count(user_id, doctor_key):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT count FROM daily_limits
               WHERE user_id=%s AND doctor_key=%s AND day=%s""",
            (user_id, doctor_key, TODAY()),
        )
        row = cur.fetchone()
    return row["count"] if row else 0


def increment_today_count(user_id, doctor_key):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO daily_limits (user_id, doctor_key, day, count)
               VALUES (%s,%s,%s,1)
               ON CONFLICT (user_id, doctor_key, day)
               DO UPDATE SET count = daily_limits.count + 1""",
            (user_id, doctor_key, TODAY()),
        )


# ----------------------------- payments ------------------------------
def log_payment(user_id, amount, status="pending", provider_tx=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO payments (user_id, amount, currency, status, provider, provider_tx)
               VALUES (%s,%s,'RUB',%s,'cloudpayments',%s)""",
            (user_id, amount, status, provider_tx),
        )


# ---------------------- разовый пакет вопросов ------------------------
def buy_question_pack(user_id, questions, price):
    """Покупает разовый пакет вопросов (без подписки). Статус 'pending' пока не оплачен."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO question_packs (user_id, questions, used, price, status)
               VALUES (%s, %s, 0, %s, 'pending')""",
            (user_id, questions, price),
        )
    return True


def pack_balance(user_id):
    """Сколько вопросов осталось активными пакетами (использовать до оплаты нельзя)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(SUM(questions - used), 0) AS left
               FROM question_packs WHERE user_id=%s AND status='active'""",
            (user_id,),
        )
        row = cur.fetchone()
    return row["left"] if row else 0


def pack_pending_amount(user_id):
    """Сумма неоплаченных пакетов (для инфо при оплате)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(SUM(price),0) AS total FROM question_packs
               WHERE user_id=%s AND status='pending'""",
            (user_id,),
        )
        row = cur.fetchone()
    return row["total"] if row else 0


def confirm_pack(user_id, questions):
    """Подтверждает оплату пакета: ставит active и возвращает баланс."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE question_packs SET status='active' WHERE user_id=%s
               AND status='pending' AND id=(SELECT min(id) FROM question_packs
               WHERE user_id=%s AND status='pending')""",
            (user_id, user_id),
        )
    return True


def spend_pack_question(user_id):
    """Списывает один вопрос из активных пакетов (самый старый)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE question_packs SET used=used+1 WHERE user_id=%s AND status='active'
               AND id=(SELECT id FROM question_packs WHERE user_id=%s AND status='active'
               AND used < questions ORDER BY id LIMIT 1)""",
            (user_id, user_id),
        )
        return cur.rowcount > 0


# ---------------------- лог рассылок (анти-спам) ------------------------
def notify_logged(user_id, notify_type, day=None):
    """True, если уведомление уже отправлялось сегодня (single-fire)."""
    import datetime as _dt
    day = day or _dt.date.today()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM notify_log WHERE user_id=%s AND notify_type=%s AND day=%s",
            (user_id, notify_type, day),
        )
        return cur.fetchone() is not None


def notify_mark(user_id, notify_type, day=None):
    """Отмечает, что уведомление отправлено (для single-fire)."""
    import datetime as _dt
    day = day or _dt.date.today()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO notify_log (user_id, notify_type, day)
               VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""",
            (user_id, notify_type, day),
        )
