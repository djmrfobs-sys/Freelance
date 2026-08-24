# -*- coding: utf-8 -*-
"""
Клиника Рядом - ядро бота.
Обслуживает ВСЕ 7 ботов (главный + 6 врачей) через один код.
Бот выбирается по токену из аргумента:  python bot.py main
                                         python bot.py terapevt
                                         ...
"""
import sys
import os
import logging
import asyncio
import telegram
import emergency  # детерминированный слой фильтрации экстренных маркеров
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, TypeHandler,
)

import config
import db

# Модуль retention-уведомлений импортируем лениво в main(), чтобы не тянуть лишнее

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("clinic")

# --- распознавание голоса (Whisper через Groq) -----------------------
GROQ_KEY_FILE = os.path.join(os.path.expanduser("~/.openclaw-neuro"), ".groq_key")

def _groq_key():
    try:
        with open(GROQ_KEY_FILE) as f:
            return f.read().strip()
    except Exception:
        return None

async def _transcribe_voice(update: Update):
    """Скачивает голосовое и возвращает распознанный текст. None - если не вышло."""
    key = _groq_key()
    if not key:
        log.error("Ключ Groq не найден - голос не распознан")
        return None
    try:
        voice = update.effective_message.voice
        file = await voice.get_file()
        import tempfile
        import io
        import groq
        buf = io.BytesIO()
        await file.download_to_memory(buf)
        buf.seek(0)
        client = groq.Groq(api_key=key)
        res = client.audio.transcriptions.create(
            file=("voice.ogg", buf),
            model="whisper-large-v3-turbo",
            language="ru",
            response_format="text",
        )
        text = (res or "").strip()
        return text or None
    except Exception as e:
        log.error("Ошибка распознавания голоса: %s", e, exc_info=True)
        return None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ai


# ----------------------------- helpers ------------------------------
def load_token(bot_key):
    """Достаёт токен бота из секретного файла.
    Имена файлов имеют суффикс _bot: main_bot.token, terapevt_bot.token, ...
    """
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, "secrets", bot_key + "_bot.token"),
        os.path.join(base, "secrets", bot_key + ".token"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r") as f:
                return f.read().strip()
    raise FileNotFoundError(f"Токен для '{bot_key}' не найден в secrets/")


def is_owner(user_id):
    return user_id == config.OWNER_ID


# ---------------------- доступ: триал / абонемент ---------------------------
def access_info(user_id):
    """Возвращает dict с данными доступа пользователя.
    key: 'trial' | 'active' | 'expired' | 'none' | 'pack'
    pack - есть неоплаченный казначейский разовый пакет (ждёт оплаты),
    доступ к вопросам даёт только оплаченный пакет (status active).
    """
    st = db.subscription_status(user_id)
    if st == "active":
        return {"key": "active"}
    # Оплаченные разовые пакеты дают доступ к вопросам без подписки
    if db.pack_balance(user_id) > 0:
        return {"key": "pack", "pack_left": db.pack_balance(user_id)}
    trial_active, trial_end = db.trial_info(user_id)
    if trial_active:
        return {"key": "trial", "trial_end": trial_end}
    if trial_end is not None:
        return {"key": "expired"}   # триал истёк, абонемента нет
    # Если есть ещё неоплаченный пакет - показываем как отдельный статус для оплаты
    if db.pack_pending_amount(user_id) > 0:
        return {"key": "none", "pack_pending": True}
    return {"key": "none"}


def daily_limit_for(user_id, doctor_key):
    """Лимит в день для этого врача: триал 10, платный 35, пакет - без дневного лимита."""
    info = access_info(user_id)
    if info["key"] == "active":
        return config.DAILY_LIMIT_PER_DOCTOR
    if info["key"] == "pack":
        return None  # без лимита, списывается по вопросу из пакета
    return config.TRIAL_DAILY_LIMIT_PER_DOCTOR


def remaining_trial_days(user_id):
    """Сколько дней осталось в триале."""
    import datetime
    trial_active, trial_end = db.trial_info(user_id)
    if not trial_active or not trial_end:
        return None
    left = trial_end - datetime.datetime.now(datetime.timezone.utc)
    return max(1, int(left.total_seconds() // 86400) + 1)


# ---------------------- карточка клиента (квест) ---------------------------
def card_started(user_id):
    """True если пользователь уже начал заполнять карточку (хотя бы 1 поле)."""
    card = db.get_card(user_id)
    return bool(card)


def card_next_prompt(user_id):
    """Возвращает (field, prompt) следующего пустого поля карточки, либо (None,None)."""
    card = db.get_card(user_id)
    for f in config.CARD_FIELDS:
        col = {
            "имя": "full_name", "возраст": "age", "пол": "gender",
            "хронические_заболевания": "chronics", "жалобы": "complaints",
        }[f]
        val = card.get(col) if card else None
        if not val:
            return f, config.CARD_PROMPTS[f]
    return None, None


# --------------------- глобальный перехват ошибок ---------------------
# Если любой обработчик упадёт - бот отвечает вежливо, а НЕ молчит/падает.
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    try:
        log.error("Обработка сообщения упала: %s", context.error, exc_info=True)
        if update and hasattr(update, "effective_message") and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Произошла небольшая техническая заминка. "
                    "Ваше сообщение сохранено - повторите, пожалуйста, "
                    "через минуту, врач продолжит с того места, где вы остановились."
                )
            except Exception:
                pass
    except Exception:
        pass


# ---------------------------- keyboards ------------------------------
def consent_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Я ознакомился и согласен", callback_data="consent_yes")]]
    )


def policy_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📄 Политика конфиденциальности", callback_data="show_policy")]]
    )


def docs_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📄 Политика конфиденциальности", callback_data="show_policy")],
         [InlineKeyboardButton("✅ Я ознакомился и согласен", callback_data="consent_yes")]]
    )


def main_menu_kb():
    kb = []
    # Подбор врача - первый акцент (онбординг)
    kb.append([InlineKeyboardButton("🤔 Не знаю, к какому врачу - подобрать", callback_data="onboard_start")])
    # Верхняя секция: врачи как кнопки-ссылки
    for key in config.DOCTORS:
        d = config.DOCTORS[key]
        kb.append([InlineKeyboardButton(f"🩺 {d['doctor']} - {d['specialty']}", url=f"https://t.me/{d['bot'][1:]}")])
    # Кнопки информации и действий
    row1 = [InlineKeyboardButton("ℹ️ О клинике", callback_data="about"),
            InlineKeyboardButton("💰 Тарифы", callback_data="prices")]
    row2 = [InlineKeyboardButton("❓ FAQ", callback_data="faq"),
            InlineKeyboardButton("👤 Кабинет", callback_data="mylk")]
    row3 = [InlineKeyboardButton("🛡️ Политика", callback_data="show_policy"),
            InlineKeyboardButton("💳 Оплатить", callback_data="pay")]
    kb.append(row1)
    kb.append(row2)
    kb.append(row3)
    return InlineKeyboardMarkup(kb)


def pay_kb():
    # Расширенная клавиатура оплаты: месяц / год / разовый пакет
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"📅 1 месяц - {config.PRICE_LABEL}", callback_data="pay_monthly")],
         [InlineKeyboardButton(f"📆 Год - {config.PRICE_YEARLY_LABEL} ({config.PRICE_YEARLY_MONTH_LABEL}, скидка ~{config.YEARLY_SAVE_PERCENT}%)", callback_data="pay_yearly")],
         [InlineKeyboardButton(f"🎟️ Разовый пакет: {config.PACK_LABEL}", callback_data="pay_pack")],
         [InlineKeyboardButton("◀ Назад", callback_data="back_main")]]
    )


def _tariffs_text():
    """Текст раздела Тарифы с тремя вариантами и сравнением."""
    return (
        f"💰 Тарифы {config.CLINIC_NAME}\n\n"
        "Выберите удобный вариант - все дают доступ ко всем 6 врачам.\n\n"
        f"1️⃣ Помесячно\n"
        f"   {config.PRICE_LABEL}\n\n"
        f"2️⃣ Годовая (выгоднее)\n"
        f"   {config.PRICE_YEARLY_LABEL} вместо 20 280 руб\n"
        f"   {config.PRICE_YEARLY_MONTH_LABEL} - экономия ~3 080 руб (скидка ~{config.YEARLY_SAVE_PERCENT}%)\n\n"
        f"3️⃣ Разовый пакет\n"
        f"   {config.PACK_LABEL} - без подписки, для редких вопросов\n\n"
        "Что входит в любой вариант:\n"
        "✅ Доступ ко всем 6 врачам\n"
        f"✅ {config.DAILY_LIMIT_PER_DOCTOR} обращений/день/врача (по подписке)\n"
        "✅ Анализ фото (кожа, снимки, анализы)\n"
        "✅ История бесед сохраняется навсегда\n\n"
        "🎁 Новым пользователям - 7 дней бесплатно (по {config.TRIAL_DAILY_LIMIT_PER_DOCTOR} обращений/день/врача)."
    )


def _tariffs_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"📅 {config.PRICE_LABEL}", callback_data="pay_monthly")],
         [InlineKeyboardButton(f"📆 Год {config.PRICE_YEARLY_LABEL}", callback_data="pay_yearly")],
         [InlineKeyboardButton(f"🎟️ {config.PACK_LABEL}", callback_data="pay_pack")],
         [InlineKeyboardButton("◀ Назад", callback_data="back_main")]]
    )


# ------------------------------ main bot ------------------------------
async def handle_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.ensure_user(user.id, user.username, user.first_name)

    # Фирменная картинка-приветствие при старте
    try:
        with open("media/welcome.png", "rb") as img:
            await update.effective_message.reply_photo(
                photo=img, caption=config.CLINIC_NAME
            )
    except Exception:
        # если картинка недоступна - просто продолжаем без неё
        pass

    if not db.consent_done(user.id, policy_version=config.POLICY_VERSION):
        text = (
            f"Добро пожаловать в {config.CLINIC_NAME}!\n\n"
            f"{config.CLINIC_TAGLINE}\n\n"
            "❗ Важно: это ИИ-консультанты, а не настоящие врачи.\n"
            "Они дают рекомендации и не заменяют очный визит к специалисту.\n\n"
            "Если у вас острое состояние - вызывайте скорую помощь.\n\n"
            "Чтобы начать, ознакомьтесь с политикой конфиденциальности "
            "и правилами:\n"
        )
        await update.effective_message.reply_text(text, reply_markup=policy_kb())
        return

    await update.effective_message.reply_text(
        config.MAIN_WELCOME + "\n\nВыберите врача или действие:",
        reply_markup=main_menu_kb(),
    )


async def main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = update.effective_user
    data = q.data

    if data == "consent_yes":
        db.mark_consent(user.id, policy_version=config.POLICY_VERSION)
        await q.edit_message_text(
            config.MAIN_WELCOME + "\n\nВыберите врача или действие:",
            reply_markup=main_menu_kb(),
        )
    elif data == "show_policy":
        text = (
            config.DISCLAIMER_TEXT + "\n\n---\n\n" + config.PRIVACY_POLICY_TEXT
            + "\n\nПродолжая, вы подтверждаете, что ознакомились и согласны."
        )
        await q.edit_message_text(text, reply_markup=docs_kb())
    elif data == "about":
        text = (
            f"🏥 {config.CLINIC_NAME}\n{config.CLINIC_TAGLINE}\n\n"
            "Это современная цифровая клиника, где консультации ведут "
            "6 профильных специалистов:\n"
        )
        for d in config.DOCTORS.values():
            text += f"\n🩺 {d['doctor']} - {d['specialty']}"
        text += (
            "\n\nКаждый врач - отдельный бот со своей историей. "
            "Вы платите один абонемент и получаете доступ ко всем сразу.\n\n"
            "Помните: консультации носят информационный характер и не заменяют "
            "очный визит к врачу."
        )
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("◀ Назад", callback_data="back_main")]]
        ))
    elif data == "prices":
        await q.edit_message_text(_tariffs_text(), reply_markup=_tariffs_kb())
    elif data == "faq":
        text = (
            "❓ Частые вопросы\n\n"
            "🩺 Это настоящие врачи?\n"
            "Нет, это цифровые консультанты на базе ИИ. Они дают рекомендации "
            "информационного характера и не заменяют живого врача.\n\n"
            "🔢 Сколько обращений я могу сделать?\n"
            f"До {config.DAILY_LIMIT_PER_DOCTOR} к каждому врачу в день.\n\n"
            "📸 Можно присылать фото?\n"
            "Да, дерматологу (кожа) и другим врачам (анализы, снимки).\n\n"
            "💳 Как оплатить?\n"
            "Через кнопку Оплатить в главном меню.\n\n"
            "🚨 Что при серьёзной проблеме?\n"
            "Немедленно обратитесь к врачу лично или вызовите скорую.\n\n"
            "🔒 Что с моими данными?\n"
            "Они хранятся конфиденциально, не передаются третьим лицам. "
            "Подробнее - в политике."
        )
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("◀ Назад", callback_data="back_main")]]
        ))
    elif data == "pay":
        await q.edit_message_text(
            f"💳 Тарифы {config.CLINIC_NAME}\n\n"
            "Выберите вариант оплаты:",
            reply_markup=pay_kb(),
        )
    elif data in ("pay_monthly", "pay_yearly", "pay_pack"):
        # Выбор тарифа через главного бота
        if data == "pay_monthly":
            _start_purchase(q, user.id, "monthly")
        elif data == "pay_yearly":
            _start_purchase(q, user.id, "yearly")
        else:
            _start_purchase(q, user.id, "pack")
    elif data == "mylk":
        await _show_cabinet(q, user.id)
    elif data == "pay_trial":
        # Автоматическое предложение продления после триала
        st = db.subscription_status(user.id)
        if st == "active":
            await q.edit_message_text(
                "✅ Ваш абонемент активен, доступ ко всем врачам открыт.",
                reply_markup=main_menu_kb(),
            )
            return
        db.create_pending_subscription(user.id)
        await q.edit_message_text(
            "💳 Продление абонемента\n\n"
            f"Стоимость: {config.PRICE_LABEL}\n"
            "Доступ ко всем 6 врачам сразу, история сохраняется.\n\n"
            "Оплата через CloudPayments будет подключена автоматически. "
            "Пока заявка на продление создана, доступ активируется вручную.",
            reply_markup=pay_kb(),
        )
    elif data == "back_main":
        await q.edit_message_text(
            config.MAIN_WELCOME, reply_markup=main_menu_kb()
        )
    elif data == "onboard_start":
        # Онбординг: подбор врача - шаг 1: категория
        lines = [
            "🤔 Помогу подобрать врача.",
            "",
            "Что вас беспокоит?",
        ]
        kb = []
        for idx, (cat, _keys) in enumerate(config.ONBOARD_CATEGORIES):
            kb.append([InlineKeyboardButton(cat, callback_data=f"ob_cat:{idx}")])
        kb.append([InlineKeyboardButton("◀ Назад", callback_data="back_main")])
        await q.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("ob_cat:"):
        idx = int(data.split(":")[1])
        if 0 <= idx < len(config.ONBOARD_CATEGORIES):
            cat, keys = config.ONBOARD_CATEGORIES[idx]
            doctor_key = keys[0]
            doc_cfg = config.DOCTORS[doctor_key]
            # Финальное предложение: врач + переход к оплате (если не подписан)
            st = db.subscription_status(user.id)
            info = access_info(user.id)
            lines = [
                f"✅ Вам подойдёт: {doc_cfg['doctor']} ({doc_cfg['specialty']}).",
                "",
                f"\ud83d\udcdd {doc_cfg['doctor']} может ответить прямо сейчас \u2014",
            ]
            kb = [[InlineKeyboardButton("\ud83d\udc69\u200d\u2695\ufe0f Открыть кабинет", url=f"https://t.me/{doc_cfg['bot'][1:]}")]]
            if st == "active":
                lines.append("ваш абонемент активен, доступ открыт.")
            elif info["key"] == "trial":
                lines.append(f"пробный период ({config.TRIAL_LABEL}) активен.")
            else:
                lines.append(
                    "оформите тариф {config.PRICE_LABEL} или разовый пакет, "
                    "чтобы начать."
                )
                kb.append([InlineKeyboardButton("\ud83d\udcb3 Оплатить / тарифы", callback_data="pay")])
            kb.append([InlineKeyboardButton("◀ Назад", callback_data="onboard_start")])
            kb.append([InlineKeyboardButton("🏠 В меню", callback_data="back_main")])
            await q.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))


async def _start_purchase(q, user_id, plan):
    """Оформление выбранного тарифа (месяц/год/разовый пакет).
    По факту - создаёт заявку, доступ активируется вручную (демо-режим,
    потом CloudPayments)."""
    if plan == "monthly":
        price = config.PRICE_MONTHLY
        label = config.PRICE_LABEL
        detail = "Месячная подписка - доступ ко всем 6 врачам."
    elif plan == "yearly":
        price = config.PRICE_YEARLY
        label = config.PRICE_YEARLY_LABEL
        detail = (
            f"Годовая подписка - выгоднее (≈{config.PRICE_YEARLY_MONTH_LABEL}).\n"
            f"Экономия ~3 080 руб против помесячной."
        )
    else:  # pack
        price = config.PACK_PRICE
        label = config.PACK_LABEL
        detail = f"Разовый пакет: {config.PACK_QUESTIONS} вопросов без подписки."
        db.buy_question_pack(user_id, config.PACK_QUESTIONS, price)
        db.log_payment(user_id, price)
        await q.edit_message_text(
            f"\ud83c\udf9f\ufe0f {label}\n\n{detail}\n\n"
            "Заявка на разовый пакет создана. Обычно доступ активируется "
            "в течение пары минут после оплаты.\n\n"
            "(Сейчас оплата - демо-режим, доступ активируется вручную.)",
            reply_markup=main_menu_kb(),
        )
        return

    # Подписка (месяц/год) - создаём pending абонемент
    db.create_pending_subscription(user.id)
    db.log_payment(user_id, price)
    await q.edit_message_text(
        f"\ud83d\udcb3 Заявка на абонемент {label}\n\n{detail}\n\n"
        "Оплата через CloudPayments будет подключена автоматически. "
        "Пока заявка создана, доступ активируется вручную.",
        reply_markup=main_menu_kb(),
    )


async def _show_cabinet(q, user_id):
    """Личный кабинет: статус, триал, карточка, кнопка продления."""
    st = db.subscription_status(user_id)
    info = access_info(user_id)
    lines = ["\ud83d\udc64 Личный кабинет", ""]

    # Разовый пакет в приоритете показа
    pack_left = db.pack_balance(user_id)
    if pack_left > 0:
        lines.append(f"\ud83c\udf9f\ufe0f Разовый пакет: осталось {pack_left} вопроса(ов)")
        lines.append("Без дневного лимита, списывается по вопросу.")
        lines.append("")

    if st == "active":
        lines.append("\u2705 Абонемент: активен")
        lines.append("Доступ ко всем 6 врачам открыт.")
        lines.append(f"Лимит: {config.DAILY_LIMIT_PER_DOCTOR} обращений/день/врача")
    elif info["key"] == "trial":
        days = remaining_trial_days(user_id)
        lines.append(f"\ud83c\udf81 Пробный период: {config.TRIAL_LABEL}")
        lines.append(f"Осталось дней: {days}")
        lines.append(f"Лимит в триале: {config.TRIAL_DAILY_LIMIT_PER_DOCTOR} обращений/день/врача")
    elif info["key"] == "expired":
        lines.append("\u23f3 Пробный период закончился")
        lines.append("Для продолжения оформите абонемент.")
    else:
        lines.append("Абонемент: не оформлен")

    # Карточка клиента
    card = db.get_card(user_id)
    if card and card.get("completed"):
        lines.append("")
        lines.append("📋 Карточка клиента: заполнена")
    else:
        lines.append("")
        lines.append("📋 Карточка клиента: не заполнена")
        lines.append("Заполните её в любом кабинете врача перед общением.")

    kb = [[InlineKeyboardButton("💳 Оплатить / тарифы", callback_data="pay")]]
    if info["key"] == "expired":
        kb.append([InlineKeyboardButton(f"🔄 Продлить - {config.PRICE_LABEL}", callback_data="pay_monthly")])
    kb.append([InlineKeyboardButton("◀ Назад", callback_data="back_main")])
    await q.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))


# ---------------------------- doctor bot -----------------------------
def make_doctor_handler(key):
    """Создаёт обработчики для конкретного врача."""
    doc_cfg = config.DOCTORS[key]

    def _need_consent(update):
        return not db.consent_done(update.effective_user.id, policy_version=config.POLICY_VERSION)

    async def _send_consent(update):
        await update.effective_message.reply_text(
            f"Добро пожаловать! Это кабинет {doc_cfg['doctor']} "
            f"({doc_cfg['specialty']}).\n\n"
            + config.DISCLAIMER_TEXT + "\n\n---\n\n" + config.PRIVACY_POLICY_TEXT
            + "\n\nПродолжая, вы подтверждаете, что ознакомились и согласны.",
            reply_markup=consent_kb(),
        )

    async def handle_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.ensure_user(user.id, user.username, user.first_name)

        # Согласие обязательно
        if _need_consent(update):
            await _send_consent(update)
            return

        # Доступ: активный абонемент, триал ИЛИ разовый пакет
        info = access_info(user.id)
        if info["key"] not in ("active", "trial", "pack"):
            if info["key"] == "expired":
                text = (
                    f"Ваш бесплатный период ({config.TRIAL_LABEL}) закончился.\n"
                    f"Для доступа к {doc_cfg['doctor']} и всем врачам оформите абонемент "
                    f"за {config.PRICE_LABEL} в главном боте: @Clinic_ryadom_bot"
                )
            else:
                text = (
                    f"Для доступа к {doc_cfg['doctor']} нужен активный абонемент или разовый пакет.\n"
                    f"Подробнее: @Clinic_ryadom_bot"
                )
            await update.effective_message.reply_text(text)
            return

        # Карточка клиента обязательна ПЕРЕД общением
        if not db.card_completed(user.id):
            f, prompt = card_next_prompt(user.id)
            context.user_data["card_field"] = f
            await update.effective_message.reply_text(
                "Перед началом общения заполните, пожалуйста, короткую карточку. "
                "Это поможет врачу говорить с учётом ваших особенностей.\n\n" + prompt
            )
            return

        # Если у пользователя разовый пакет - лимит не применяем, списываем вопрос ниже
        is_pack = info["key"] == "pack"
        if not is_pack:
            # Лимит в день на этого врача (триал 10, платный 35)
            limit = daily_limit_for(user.id, key)
            count = db.get_today_count(user.id, key)
            if count >= limit:
                await update.effective_message.reply_text(
                    f"Лимит обращений сегодня к этому врачу исчерпан (до {limit} в день). "
                    "Возвращайтесь завтра - врач продолжит с того места, где вы остановились."
                )
                return
            # Предупреждение о лимите (single-fire через notify_log)
            remaining = limit - count
            if remaining <= config.LIMIT_WARN_REMAINING and not db.notify_logged(
                user.id, config.NOTIFY_LIMIT
            ):
                db.notify_mark(user.id, config.NOTIFY_LIMIT)
                try:
                    await update.effective_message.reply_text(
                        f"⚠️ Осталось {remaining} обращение(й) к этому врачу на сегодня. "
                        f"Завтра лимит ({limit}) обновится."
                    )
                except Exception:
                    pass

        # Сохранить сообщение пользователя сразу (история навсегда)
        text = update.effective_message.text or ""
        db.save_message(user.id, key, "user", text, None)

        # ЭКСТРЕННЫЙ ТРИГГЕР: детерминированная проверка ДО вызова LLM
        emg = emergency.check_emergency(text)
        if emg:
            emergency.log_trigger(user.id, key, emg["category"], emg["match"])
            db.save_message(user.id, key, "assistant", emg["response"])
            await update.effective_message.reply_text(emg["response"])
            return

        # Ответ врача (карточка клиента идёт контекстом)
        reply = _consult(user.id, key, doc_cfg)

        # Сохранить ответ врача; списать вопрос из пакета ИЛИ програть лимит
        db.save_message(user.id, key, "assistant", reply)
        if is_pack:
            db.spend_pack_question(user.id)
        else:
            db.increment_today_count(user.id, key)

        await update.effective_message.reply_text(reply)

    async def handle_doctor_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.ensure_user(user.id, user.username, user.first_name)

        if _need_consent(update):
            await _send_consent(update)
            return

        info = access_info(user.id)
        if info["key"] not in ("active", "trial", "pack"):
            await update.effective_message.reply_text(
                f"Для доступа к {doc_cfg['doctor']} нужен активный абонемент или разовый пакет.\n"
                f"Подробнее: @Clinic_ryadom_bot"
            )
            return

        # Карточка клиента обязательна ПЕРЕД общением
        if not db.card_completed(user.id):
            f, prompt = card_next_prompt(user.id)
            context.user_data["card_field"] = f
            await update.effective_message.reply_text(
                "Перед началом общения заполните, пожалуйста, короткую карточку.\n\n" + prompt
            )
            return

        is_pack = info["key"] == "pack"
        if not is_pack:
            limit = daily_limit_for(user.id, key)
            count = db.get_today_count(user.id, key)
            if count >= limit:
                await update.effective_message.reply_text(
                    "Лимит обращений на сегодня исчерпан. Вернитесь завтра."
                )
                return

        photos = update.effective_message.photo
        photo_id = photos[-1].file_id if photos else None
        text = update.effective_message.caption or "[фото]"

        # ЭКСТРЕННЫЙ ТРИГГЕР: проверка текста к фото до анализа/LMM
        emg = emergency.check_emergency(text)
        if emg:
            emergency.log_trigger(user.id, key, emg["category"], emg["match"])
            db.save_message(user.id, key, "user", text, photo_file=photo_id)
            db.save_message(user.id, key, "assistant", emg["response"])
            await update.effective_message.reply_text(emg["response"])
            return

        # Скачиваем фото из Telegram (бинарные данные) для vision-анализа
        photo_bytes = None
        if photo_id:
            try:
                fobj = await context.bot.get_file(photo_id)
                photo_bytes = await fobj.download_as_bytearray()
            except Exception as e:
                log.warning("Не удалось скачать фото: %s", e)

        # Сохраняем фото в историю сразу
        db.save_message(user.id, key, "user", text, photo_file=photo_id)

        # Анализ фото (Gemini Vision по бинарным данным)
        desc = ai.analyze_photo(photo_bytes, text, doc_cfg)

        hist = db.get_history(user.id, key, config.HISTORY_CONTEXT_LEN)
        hist_messages = [{"role": r["role"], "content": r["content"]} for r in hist]
        if desc:
            hist_messages.append({"role": "user", "content": f"[Пользователь прислал фото, анализ: {desc}]"})
        reply = ai.ask_doctor(doc_cfg, hist_messages)

        db.save_message(user.id, key, "assistant", reply)
        if is_pack:
            db.spend_pack_question(user.id)
        else:
            db.increment_today_count(user.id, key)

        await update.effective_message.reply_text(reply)

    async def doctor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        user = update.effective_user
        await q.answer()
        if q.data == "consent_yes":
            db.mark_consent(user.id, policy_version=config.POLICY_VERSION)  # согласие + старт триала 7 дней
            # Начинаем с карточки клиента
            f, prompt = card_next_prompt(user.id)
            context.user_data["card_field"] = f
            await q.edit_message_text(
                f"Кабинет {doc_cfg['doctor']} ({doc_cfg['specialty']}).\n\n"
                f"Ваш бесплатный период ({config.TRIAL_LABEL}) активен!\n"
                "Сначала заполните короткую карточку клиента - врач будет "
                "говорить с учётом ваших особенностей.\n\n" + prompt
            )
        elif q.data == "skip_trial":
            # Спец-кнопка (для теста/владельца) - сразу без триала
            await q.edit_message_text(
                f"Кабинет {doc_cfg['doctor']} ({doc_cfg['specialty']}).\n"
                "Заполните карточку клиента, чтобы врач знал ваши особенности.\n\n"
                + config.CARD_PROMPTS["имя"]
            )
            context.user_data["card_field"] = "имя"

    async def handle_doctor_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.ensure_user(user.id, user.username, user.first_name)

        if _need_consent(update):
            await _send_consent(update)
            return

        # Сообщение о распознавании - быстро, чтобы юзер не думал, что бросили
        try:
            await update.effective_message.reply_text("Распознаю ваше голосовое...")
        except Exception:
            pass

        text = await _transcribe_voice(update)
        if not text:
            await update.effective_message.reply_text(
                f"Я {doc_cfg['doctor']} ({doc_cfg['specialty']}). "
                "Не смог распознать ваше голосовое. Попробуйте повторить, "
                "говорите чуть медленнее, или напишите текстом/фото - и мы продолжим."
            )
            return

        # Подставляем распознанный текст в сообщение и идём обычным потоком врача
        update.effective_message.text = text
        await handle_doctor(update, context)

    # Обработчик-заглушка для всего остального: стикер, документ,
    # видео и т.д. Не даём боту упасть и объясняем, что ждём.
    async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.ensure_user(user.id, user.username, user.first_name)

        if _need_consent(update):
            await _send_consent(update)
            return

        info = access_info(user.id)
        if info["key"] not in ("active", "trial"):
            await update.effective_message.reply_text(
                f"Для доступа к {doc_cfg['doctor']} нужен активный абонемент или триал.\n"
                f"Подробнее: @Clinic_ryadom_bot"
            )
            return

        # Карточка клиента
        if not db.card_completed(user.id):
            f, prompt = card_next_prompt(user.id)
            context.user_data["card_field"] = f
            await update.effective_message.reply_text(
                "Перед общением с врачом заполните карточку клиента.\n\n" + prompt
            )
            return

        await update.effective_message.reply_text(
            f"Я {doc_cfg['doctor']} ({doc_cfg['specialty']}). "
            "Лучше всего я отвечу на текстовое сообщение или фото. "
            "Напишите словами, что вас беспокоит, - и мы продолжим разговор."
        )

    # Карточка клиента: обработчик текстовых ответов на вопросы карточки
    async def handle_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.ensure_user(user.id, user.username, user.first_name)
        field = context.user_data.get("card_field")
        if not field:
            # Вне квеста карточки - просто переходим к обычному потоку
            await handle_doctor(update, context)
            return
        text = (update.effective_message.text or "").strip()
        if not text:
            await update.effective_message.reply_text("Пожалуйста, напишите ответ текстом.")
            return
        db.save_card_field(user.id, field, text)
        # следующий вопрос
        f, prompt = card_next_prompt(user.id)
        if f:
            context.user_data["card_field"] = f
            await update.effective_message.reply_text(prompt)
        else:
            db.set_card_completed(user.id)
            context.user_data["card_field"] = None
            card_text = db.card_to_prompt(user.id)
            await update.effective_message.reply_text(
                "Спасибо! Ваша карточка сохранена. Врач будет учитывать её при общении.\n\n"
                + (card_text or "") + "\n\n"
                f"Кабинет {doc_cfg['doctor']} готов. Расскажите, что вас беспокоит."
            )

    return handle_doctor, handle_doctor_photo, doctor_callback, handle_other, handle_card, handle_doctor_voice


def _consult(user_id, key, doc_cfg):
    """Сборка ответа врача из истории + карточка клиента как контекст."""
    hist = db.get_history(user_id, key, config.HISTORY_CONTEXT_LEN)
    hist_messages = [{"role": r["role"], "content": r["content"]} for r in hist]
    card_prompt = db.card_to_prompt(user_id)
    if card_prompt:
        # Карточка клиента идёт в начало контекста как системная информация о пациенте
        hist_messages.insert(0, {"role": "system", "content": card_prompt})
    return ai.ask_doctor(doc_cfg, hist_messages)


# ----------------------------- main entry ----------------------------
def main():
    tool = sys.argv[1] if len(sys.argv) > 1 else "main"
    token = load_token(tool)
    key = None if tool == "main" else tool

    app = ApplicationBuilder().token(token).build()
    app.add_error_handler(error_handler)

    if key is None:
        app.add_handler(CommandHandler("start", handle_main))
        app.add_handler(CallbackQueryHandler(main_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main))
        # Всё не-текстовое в главном боте - аккуратно в меню
        async def main_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            db.ensure_user(user.id, user.username, user.first_name)
            if not db.consent_done(user.id, policy_version=config.POLICY_VERSION):
                await handle_main(update, context)
                return
            await update.effective_message.reply_text(
                "Используйте кнопки меню или напишите слово - помогу. "
                "Кнопки-ссылки на врачей ниже.",
                reply_markup=main_menu_kb(),
            )
        app.add_handler(TypeHandler(Update, main_other))
    else:
        h_text, h_photo, h_cb, h_other, h_card, h_voice = make_doctor_handler(key)
        app.add_handler(CommandHandler("start", h_text))
        app.add_handler(CallbackQueryHandler(h_cb))
        # Карточка клиента: перехватывает текст, если идёт заполнение (по флагу в user_data)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_card))
        app.add_handler(MessageHandler(filters.PHOTO, h_photo))
        # Голосовые: распознаём через Whisper и передаём врачу как текст
        app.add_handler(MessageHandler(filters.VOICE, h_voice))
        # всё остальное (стикер, документ, видео) - вежливая заглушка
        app.add_handler(MessageHandler(~filters.TEXT & ~filters.PHOTO & ~filters.VOICE, h_other))

    if key is None:
        # Фоновый поток retention-уведомлений (только в главном боте)
        try:
            import notify
            import threading
            threading.Thread(
                target=notify.run_forever,
                args=(token,),
                daemon=True,
                name="notify-cron",
            ).start()
            log.info("Фоновый поток рассылок запущен")
        except Exception as e:
            log.error("Не удалось запустить рассылки: %s", e)

    log.info("Бот запущен: %s", tool)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
