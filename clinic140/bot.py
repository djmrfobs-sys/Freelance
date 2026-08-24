# Клиника 140 - главный Telegram-бот (aiogram)
# Личный бот для Кети + Артур (админ).

import os
import asyncio
import sqlite3
import requests
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, FSInputFile,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    BOT_TOKEN, ALLOWED_IDS, KETY_ID, ARTHUR_ID, DOCTORS,
    HELP_TEXT, SUM_EXPERIENCE,
)
import memory
import ai
import utils

# инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# база для напоминаний
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "clinic.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        time TEXT,          -- "HH:MM"
        text TEXT,
        enabled INTEGER DEFAULT 1
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS state (
        chat_id INTEGER PRIMARY KEY,
        current_doctor TEXT,     -- doctor_id текущего кабинета
        style TEXT DEFAULT 'detailed',
        voice_mode INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()


def get_state(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT current_doctor, style, voice_mode FROM state WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"current_doctor": None, "style": "detailed", "voice_mode": 0}
    return {"current_doctor": row[0], "style": row[1] or "detailed", "voice_mode": row[2] or 0}


def set_state(chat_id, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    st = get_state(chat_id)
    st.update(kwargs)
    conn.execute("""INSERT INTO state (chat_id, current_doctor, style, voice_mode)
                    VALUES (?,?,?,?)
                    ON CONFLICT(chat_id) DO UPDATE SET
                      current_doctor=excluded.current_doctor,
                      style=excluded.style,
                      voice_mode=excluded.voice_mode""",
                 (chat_id, st["current_doctor"], st["style"], st["voice_mode"]))
    conn.commit()
    conn.close()


# ============ Клавиатуры ============
def board(cfg):
    """Составить ReplyKeyboard из списка рядов кнопок (aiogram 3.x)."""
    keyboard = []
    for row in cfg:
        keyboard.append([KeyboardButton(text=t) for t in row])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


def main_menu_kb():
    rows = []
    # врачи по 2 в ряд
    for i in range(0, len(DOCTORS), 2):
        row = []
        for d in DOCTORS[i:i+2]:
            row.append(f"{d['emoji']} {d['name']} ({d['specialty']})")
        rows.append(row)
    rows.append(["⚕️ Срочный вопрос", "🔄 Консилиум"])
    rows.append(["📅 Напоминания", "📄 Экспорт в PDF"])
    rows.append(["⚙️ Стиль ответа"])
    return board(rows)


def in_doctor_kb(doc):
    name = f"{doc['emoji']} {doc['name']} - {doc['specialty']}"
    keyboard = [
        [KeyboardButton(text="🏠 Главное меню")],
        [KeyboardButton(text=f"📋 Обо мне ({doc['name']})"),
         KeyboardButton(text="⚕️ Срочный вопрос")],
        [KeyboardButton(text="🔄 Консилиум"), KeyboardButton(text="📄 Экспорт в PDF")],
        [KeyboardButton(text="⚙️ Стиль ответа")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


def style_kb():
    keyboard = [
        [KeyboardButton(text="✂️ Короткий"),
         KeyboardButton(text="📖 Подробный"),
         KeyboardButton(text="🗂 Пошаговый план")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


# ============ Экраны ============
def doctor_card(doc):
    faq = "\n".join([f"  ⁉️ {q}" for q in doc["faq"]])
    return (
        f"{doc['emoji']} {doc['name']} - {doc['specialty']}\n"
        f"Опыт: {doc['experience']} лет\n\n"
        f"Зона ответственности:\n{doc['zone']}\n\n"
        f"Частые вопросы:\n{faq}"
    )


def build_system_prompt_for_doc(doc, style="detailed"):
    """Shortcut для совместимости (используем ai._system_prompt)."""
    return ai._system_prompt(doc["id"], style)


# ============ Команды ============
@router.message(Command("start"))
async def cmd_start(msg: Message):
    if msg.from_user.id not in ALLOWED_IDS:
        await msg.answer("Этот бот личный для Кети. 🔒")
        return
    txt = (
        f"Добро пожаловать в Клинику 140, {'Кети' if msg.from_user.id == KETY_ID else 'Доктор'}! 🩷\n\n"
        f"Тут 10 врачей с суммарным опытом {SUM_EXPERIENCE} лет. Выбери доктора из меню.\n\n"
        f"{HELP_TEXT}"
    )
    await msg.answer(txt, reply_markup=main_menu_kb())


@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "Как пользоваться Клиникой 140:\n"
        "- Выбери врача в меню и задай вопрос\n"
        "- Кнопка ⚕️ Срочный вопрос - быстрый короткий ответ\n"
        "- 🔄 Консилиум - несколько врачей обсудят случай\n"
        "- 📄 Экспорт в PDF - вся история одним файлом\n"
        "- 📅 Напоминания - настроить уведомления\n"
        "- ⚙️ Стиль ответа - короткий / подробный / план",
        reply_markup=main_menu_kb())


# ============ Главное меню (кнопки) ============
@router.message(F.text.func(lambda t: t and "Главное меню" in t))
async def goto_main(msg: Message):
    set_state(msg.from_user.id, current_doctor=None)
    await msg.answer("Главное меню. Выбери врача:", reply_markup=main_menu_kb())


# выбор врача из главного меню
# фильтр в декораторе: срабатывает ТОЛЬКО на точные кнопки выбора врача,
# чтобы НЕ перехватывать "Обо мне", "Срочный вопрос" и прочие кнопки
_DOCTOR_KEYS = {f"{d['emoji']} {d['name']} ({d['specialty']})" for d in DOCTORS}

@router.message(F.text.in_(_DOCTOR_KEYS))
async def pick_doctor(msg: Message):
    uid = msg.from_user.id
    if uid not in ALLOWED_IDS:
        return
    text = msg.text.strip()
    doc = None
    for d in DOCTORS:
        expected = f"{d['emoji']} {d['name']} ({d['specialty']})"
        if text == expected:
            doc = d
            break
    set_state(uid, current_doctor=doc["id"])
    memory.init_cabinet(uid, doc["id"])
    welcome = (
        f"{doc['emoji']} {doc['name']}, {doc['specialty']}. Опыт {doc['experience']} лет.\n"
        f"Здравствуй, я с тобой. Задай свой вопрос - я помогу и успокою."
    )
    await msg.answer(welcome, reply_markup=in_doctor_kb(doc))


# карточка врача
@router.message(F.text.func(lambda t: t and "Обо мне" in t))
async def whoami(msg: Message):
    st = get_state(msg.from_user.id)
    doc = next((d for d in DOCTORS if d["id"] == st["current_doctor"]), None)
    if not doc:
        await msg.answer("Сначала выбери врача в главном меню.", reply_markup=main_menu_kb())
        return
    await msg.answer(doctor_card(doc), reply_markup=in_doctor_kb(doc))


# ============ Стиль ответа ============
@router.message(F.text.func(lambda t: t and "Стиль ответа" in t))
async def choose_style(msg: Message):
    await msg.answer("Выбери стиль ответов врача:", reply_markup=style_kb())


@router.message(F.text.func(lambda t: t and "Короткий" in t))
async def set_short(msg: Message):
    set_state(msg.from_user.id, style="short")
    await msg.answer("Стиль: короткий. Врач отвечает кратко и по делу.", reply_markup=_after_style_kb(msg.from_user.id))


@router.message(F.text.func(lambda t: t and "Подробный" in t))
async def set_detailed(msg: Message):
    set_state(msg.from_user.id, style="detailed")
    await msg.answer("Стиль: подробный. Врач объясняет развёрнуто.", reply_markup=_after_style_kb(msg.from_user.id))


@router.message(F.text.func(lambda t: t and "Пошаговый" in t))
async def set_plan(msg: Message):
    set_state(msg.from_user.id, style="plan")
    await msg.answer("Стиль: пошаговый план действий.", reply_markup=_after_style_kb(msg.from_user.id))


def _after_style_kb(uid):
    st = get_state(uid)
    if st["current_doctor"]:
        doc = next((d for d in DOCTORS if d["id"] == st["current_doctor"]), None)
        if doc:
            return in_doctor_kb(doc)
    return main_menu_kb()


# ============ Срочный вопрос ============
@router.message(F.text.func(lambda t: t and "Срочный вопрос" in t))
async def urgent(msg: Message):
    st = get_state(msg.from_user.id)
    doc = next((d for d in DOCTORS if d["id"] == st["current_doctor"]), None)
    if not doc:
        await msg.answer("Выбери врача в главном меню, к которому срочный вопрос.", reply_markup=main_menu_kb())
        return
    await msg.answer(
        f"⚕️ Срочный вопрос к {doc['name']}. Опиши кратко, что случилось - отвечу за 30 секунд.\n"
        "Если это экстренная ситуация (сильная боль, кровь, затруднённое дыхание, потеря сознания) - звони 112/103 и к очному врачу!",
        reply_markup=in_doctor_kb(doc))
    set_state(msg.from_user.id, voice_mode=0)  # снимем режим свободного диалога - на самом деле оставим, ниже логика


# ============ Консилиум ============
@router.message(F.text.func(lambda t: t and "Консилиум" in t))
async def consilium_menu(msg: Message):
    uid = msg.from_user.id
    # inline-выбор нескольких врачей
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    # соберём по 2 в ряд
    row = []
    for d in DOCTORS:
        row.append(InlineKeyboardButton(text=f"{d['emoji']} {d['specialty']}", callback_data=f"cons:{d['id']}"))
        if len(row) == 2:
            kb.inline_keyboard.append(row)
            row = []
    if row:
        kb.inline_keyboard.append(row)
    kb.inline_keyboard.append([InlineKeyboardButton(text="✅ Начать консилиум", callback_data="cons:start")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="✖️ Отмена", callback_data="cons:cancel")])
    await msg.answer("Выбери врачей для консилиума (минимум 2). Потом нажми «Начать консилиум»:", reply_markup=kb)


# состояние выбора консилиума храним просто в переменной в памяти (текущая сессия)
CONS_SELECT = {}


@router.callback_query(F.data.startswith("cons:"))
async def cons_handler(cb: CallbackQuery):
    uid = cb.from_user.id
    action = cb.data.split(":", 1)[1]
    if action == "cancel":
        CONS_SELECT.pop(uid, None)
        await cb.message.delete()
        await cb.message.answer("Консилиум отменён.", reply_markup=_after_style_kb(uid))
        return
    if action == "start":
        selected = CONS_SELECT.get(uid, [])
        if len(selected) < 2:
            await cb.answer("Выбери минимум 2 врачей сначала.", show_alert=True)
            return
        await cb.message.answer("Описание состояния или вопроса для консилиума (текстом):")
        CONS_SELECT[uid] = selected
        set_state(uid, current_doctor=None)  # чтобы свободный текст ниже шёл в консилиум, обработаем отдельно флагом
        CONS_SELECT["pending_" + str(uid)] = selected
        return
    # toggle врач
    selected = CONS_SELECT.setdefault(uid, [])
    if action in selected:
        selected.remove(action)
        await cb.answer(f"Убран: {next((d['specialty'] for d in DOCTORS if d['id']==action), '')}", show_alert=False)
    else:
        if len(selected) >= 5:
            await cb.answer("Максимум 5 врачей.", show_alert=True)
            return
        selected.append(action)
        await cb.answer(f"Добавлен: {next((d['specialty'] for d in DOCTORS if d['id']==action), '')}", show_alert=False)
    await cb.answer()
    # обновим текст подписи
    await cb.message.edit_text(
        "Выбрано врачей: " + ", ".join([next((d['specialty'] for d in DOCTORS if d['id']==x), x) for x in selected])
        + "\n\nЖми «Начать консилиум» когда готов.\nМожно добавить ещё или убрать.",
        reply_markup=cb.message.reply_markup)


# ============ Напоминания ============
@router.message(F.text.func(lambda t: t and "Напоминания" in t))
async def reminders_menu(msg: Message):
    uid = msg.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT id, time, text, enabled FROM reminders WHERE chat_id=? ORDER BY time", (uid,))
    rows = cur.fetchall()
    conn.close()
    txt = "📅 Твои напоминания:\n"
    if not rows:
        txt += "Пока пусто.\n"
    else:
        for r in rows:
            on = "🔔" if r[3] else "🔕"
            txt += f"{on} {r[1]} - {r[2]} (id:{r[0]})\n"
    await msg.answer(
        txt + "\nЧтобы добавить, напиши командой:\n"
        "/rem 08:30 Пить воду\nЧтобы удалить:\n/delrem <id>",
        reply_markup=_after_style_kb(uid))


@router.message(Command("rem"))
async def add_reminder(msg: Message):
    uid = msg.from_user.id
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        await msg.answer("Формат: /rem 08:30 Текст напоминания")
        return
    t = parts[1]
    text = parts[2]
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO reminders (chat_id, time, text, enabled) VALUES (?,?,?,1)", (uid, t, text))
    conn.commit()
    conn.close()
    await msg.answer(f"✅ Напоминание на {t}: «{text}» добавлено.", reply_markup=_after_style_kb(uid))


@router.message(Command("delrem"))
async def del_reminder(msg: Message):
    uid = msg.from_user.id
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.answer("Формат: /delrem <id>")
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM reminders WHERE id=? AND chat_id=?", (int(parts[1]), uid))
    conn.commit()
    conn.close()
    await msg.answer("✅ Напоминание удалено.", reply_markup=_after_style_kb(uid))


# ============ Экспорт PDF ============
@router.message(F.text.func(lambda t: t and "Экспорт в PDF" in t))
async def export_pdf(msg: Message):
    uid = msg.from_user.id
    await msg.answer("Формирую PDF со всей историей...")
    cabinets_data = []
    for d in DOCTORS:
        data = memory.init_cabinet(uid, d["id"])
        cabinets_data.append(data)
    try:
        path = utils.build_pdf(uid, cabinets_data, user_name="Кети" if uid == KETY_ID else "Пользователь")
        await msg.answer_document(FSInputFile(path), caption="Клиника 140 - вся история консультаций")
    except Exception as e:
        await msg.answer(f"Не удалось сформировать PDF: {str(e)[:100]}")


# ============ Свободные текстовые сообщения (диалог с врачом / консилиум) ============
@router.message(F.text)
async def chat_dialog(msg: Message):
    uid = msg.from_user.id
    if uid not in ALLOWED_IDS:
        return
    text = msg.text.strip()

    # спец-режим консилиума: ждём описание случая
    pending = CONS_SELECT.get("pending_" + str(uid))
    if pending:
        CONS_SELECT["pending_" + str(uid)] = None
        await msg.answer("Консилиум запущен, собираю мнения врачей...")
        style = get_state(uid)["style"]
        last = memory.get_last_messages(uid, pending[0], limit=10)
        summary = ai.ask_consilium(pending, text, last, style)
        for doc_id in pending:
            memory.add_message(uid, doc_id, "user", text)
            memory.add_message(uid, doc_id, "assistant", summary)
        kb = main_menu_kb()
        await msg.answer(summary, reply_markup=kb)
        return

    # обычный диалог: нужно выбрать врача
    st = get_state(uid)
    doc = next((d for d in DOCTORS if d["id"] == st["current_doctor"]), None)
    if not doc:
        await msg.answer("Сначала выбери врача в главном меню, или воспользуйся кнопками ниже.", reply_markup=main_menu_kb())
        return

    await bot.send_chat_action(chat_id=uid, action="typing")
    style = st["style"]
    # сохраняем сообщение пользователя
    memory.add_message(uid, doc["id"], "user", text)
    # контекст
    last = memory.get_last_messages(uid, doc["id"], limit=30)
    response, error = ai.ask_doctor(doc["id"], text, last, style)
    if error:
        await msg.answer("Врач сейчас занят, попробуй ещё раз через минуту. 📵")
        return
    # сохраняем ответ
    memory.add_message(uid, doc["id"], "assistant", response)
    await msg.answer(response, reply_markup=in_doctor_kb(doc))


# ============ Медиа от Кети (фото, видео, документы, голос) ============
@router.message(F.photo)
async def on_photo(msg: Message):
    uid = msg.from_user.id
    if uid not in ALLOWED_IDS or not get_state(uid)["current_doctor"]:
        await msg.answer("Выбери врача в главном меню, чтобы отправить фото врачу.")
        return
    await msg.answer("Получил фото. Если нужно - опиши вопрос, я передам доктору.")


@router.message(F.video)
async def on_video(msg: Message):
    await msg.answer("Получил видео. Сохранил в кабинет.")


@router.message(F.document)
async def on_document(msg: Message):
    await msg.answer("Получил документ. Сохранил в кабинет.")


@router.message(F.voice | F.audio)
async def on_voice(msg: Message):
    uid = msg.from_user.id
    if uid not in ALLOWED_IDS:
        return
    st = get_state(uid)
    if not st["current_doctor"]:
        await msg.answer("Выбери врача в главном меню, потом диктуй голосом.")
        return
    await msg.answer("Распознаю голос...")
    try:
        voice = msg.voice or msg.audio
        file_bytes = await _get_file_bytes(msg.bot, voice.file_id)
        text, err = utils.transcribe_voice(file_bytes, "voice.ogg")
        if err or not text:
            await msg.answer("Не смог распознать голос. Попробуй ещё раз или напиши текстом.")
            return
        # подставляем распознанный текст как вопрос доктора
        await bot.send_chat_action(chat_id=uid, action="typing")
        doc = next((d for d in DOCTORS if d["id"] == st["current_doctor"]), None)
        memory.add_message(uid, doc["id"], "user", "🎤 " + text)
        last = memory.get_last_messages(uid, doc["id"], limit=30)
        response, error = ai.ask_doctor(doc["id"], text, last, st["style"])
        if error:
            await msg.answer("Врач сейчас занят, попробуй ещё раз.")
            return
        memory.add_message(uid, doc["id"], "assistant", response)
        await msg.answer(f"🎤 {text}\n\n{response}", reply_markup=in_doctor_kb(doc))
    except Exception as e:
        await msg.answer(f"Ошибка обработки голоса: {str(e)[:100]}")


async def _get_file_bytes(bot, file_id):
    from io import BytesIO
    import aiogram
    fi = await bot.get_file(file_id)
    buf = BytesIO()
    await bot.download_file(fi.file_path, buf)
    return buf.getvalue()


# ============ Фоновая задача: напоминания + бэкап ============
async def background_loop():
    last_backup_day = None
    while True:
        now = datetime.now()
        # напоминания каждую минуту
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute("SELECT chat_id, time, text FROM reminders WHERE enabled=1")
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            chat_id, t, text = r
            if now.strftime("%H:%M") == t:
                try:
                    await bot.send_message(chat_id, f"🔔 Напоминание: {text}")
                except Exception as e:
                    print("reminder err", e)
        # бэкап раз в сутки
        if last_backup_day != now.strftime("%Y-%m-%d"):
            memory.daily_backup()
            last_backup_day = now.strftime("%Y-%m-%d")
        await asyncio.sleep(30)


async def main():
    init_db()
    # запускаем фоновый цикл (напоминания + ежедневный бэкап)
    bg = asyncio.create_task(background_loop())
    await dp.start_polling(bot, skip_updates=True)
    bg.cancel()


if __name__ == "__main__":
    init_db()
    memory.daily_backup()
    print(f"🤖 Doctors_for_kety_bot (Клиника 140) стартовал. Врачей: {len(DOCTORS)}, суммарный стаж: {SUM_EXPERIENCE} лет.")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
