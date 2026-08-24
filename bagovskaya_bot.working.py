# -*- coding: utf-8 -*-
"""
Бот-нейропродавец для домика в станице Баговской (Авито).

Отвечает строго по базе знаний, ничего не выдумывает.
Ведёт живой диалог: расспрашивает о человеке и делится информацией о домике,
участке, соседях, магазинах, ПВЗ, школе.
Собирает лид: имя, о себе, дата просмотра/заселения, контакт.
Шлёт лид в группу заказчика + дублирует владельцу в личку с кнопкой.
Напоминает владельцу каждые 15 минут, пока лид не закрыт (/done или кнопка).
"""
import logging
import re
import time
import asyncio
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("bagovskaya_bot")

# ===== КОНФИГИ =====
BOT_TOKEN = "8769879618:AAEKQRLCsjmtq5h5_UJDN9SpzcNqiU7ZpF8"
LEAD_CHAT_ID = -5203432409  # группа «Баговская Авито Бот»
OWNER_CHAT_ID = 199790247   # личка Артура
OWNER_USERNAME = "KISELEVY_CREO"
REMINDER_INTERVAL = 900     # 15 минут = 900 секунд

# ===== СОСТОЯНИЯ ОПРОСА =====
S_ASK_NAME = "name"
S_ASK_QUEST = "quest"
S_ASK_ABOUT = "about"
S_ASK_CHECKIN = "checkin"
S_ASK_CONTACT = "contact"
S_DONE = "done"

# ===== БАЗА ЗНАНИЙ (строго, ничего не выдумываем) =====
BASE = {
    "price": "17500 рублей в месяц",
    "deposit": "залоговая сумма 17500 рублей, она возвращается при съезде",
    "term": "сдаём на длительный срок, от 11 месяцев",
    "capacity": "дом рассчитан на 2 человек, плюс можно с питомцем (котам и собакам рады)",
    "communal": "коммуналка оплачивается отдельно: свет по счётчику (сколько намотали, столько и платите), вывоз мусора 150 рублей, интернет 800 рублей",
    "heating": "зимой отапливается конвекционными электрорадиаторами, они едят мало электроэнергии, дом тёплый",
    "water": "горячая и холодная вода идёт со скважины, установлен новый водонагреватель на 30 литров, есть душевая",
    "wifi": "проведён интернет Wi-Fi, 200 мбит/с - хватает и на работу, и на кино",
    "toilet": "туалет расположен во дворе, отдельный, аккуратный",
    "furniture": "внутри кухонный гарнитур, холодильник, микроволновая печь, комод, кровать, есть вся необходимая мебель для комфортной жизни",
    "bedroom": "в доме есть спальная зона с кроватью, место для отдыха",
    "style": "свежий ремонт, всё сделано в бохо-стиле, абсолютно новые шторы, фасад дома расписан - это настоящий арт-объект",
    "plot": "участок 25 соток. На участке есть костровая зона и мангальная зона рядом с большой пушистой елью - в любое время года под ёлкой комфортно и есть тенёк. С одной стороны от дома нет соседей - там поле и небольшой прудик, дальше ручей. Сзади, в конце участка, начинается лес и течёт ручей",
    "secure": "на участке установлено видеонаблюдение для вашей безопасности",
    "fence": "забора нет - ни сзади (там сразу лес), ни с одной стороны, ни спереди по фасаду. Мы специально его не ставили, чтобы всегда наслаждаться красивыми видами поля и леса",
    "grass": "траву косить вам не нужно, она всегда идеально ровная - всё поддерживается в порядке",
    "animals": "котам и собакам рады. Рядом - природа, поле и лес, есть где гулять. На участке днём пасутся кони и барашки, это очень красиво",
    "neighbors": "дом стоит на тихой улице, суеты почти нет. Соседи есть только с одной стороны, а через дорогу - дружелюбные соседи. С другой стороны поля и тишина",
    "outdoor": "перед входом навес с подсветкой, там столик и два хороших кресла. Площадка, большая пушистая ель и сам домик подсвечены специальными светильниками - они включаются автоматически вечером и выключаются утром. Вечером очень уютно сидеть и смотреть на закат над полем",
    "location": "станица Баговская",
    "status": "дом сейчас свободен, и в нём после ремонта ещё никто не жил - вы будете первыми",
    "photos": "больше фото можно отправить, напишите что именно хотите посмотреть - домик, участок или окружение",
    "about": "мы с женой купили домик несколько лет назад, сделали в нём свежий ремонт в бохо-стиле. Хотим сдавать его в хорошие руки, тем, кто оценит тишину, природу и уют",
    # ===== НОВОЕ: ОКРУЖЕНИЕ =====
    "neighbor_detail": "Соседи живут только с одной стороны дома. По другую сторону соседей нет - там поле и небольшой прудик, дальше течёт ручей. Через дорогу живут дружелюбные соседи. Улица очень тихая и спокойная, суеты почти нет",
    "plot_area": "общая площадь участка 25 соток - просторно, есть где погулять и отдохнуть",
    "nature": "сзади домика, в конце участка, начинается лес и течёт ручей. С одной стороны поле и прудик. Это место для тихой спокойной жизни на природе",
    "shops": "недалеко от домика есть три продуктовых магазина, где можно купить всё необходимое. Работают до 22:00",
    "pvz": "рядом с домиком есть несколько пунктов выдачи заказов Wildberries и Ozon - заказывать товары удобно",
    "school": "в станице есть школа и детский сад - подходит для семей с детьми",
    "quiet": "на улице очень мало суеты, очень тихо и спокойно - это идеальное место, чтобы отдохнуть от города и пожить размеренно",
    "sights": "в станице очень много достопримечательностей для отдыха: есть дольмены (их около тридцати), недалеко горная река и прекрасные виды. Буквально в 100 метрах от домика смотровая площадка, откуда видно крупным планом горы и Чёртовы ворота - очень красиво",
    "mountains": "вокруг деревни везде расположены горы и холмы. Очень красивое место, где тишина, уют и спокойствие",
}

# ===== СОСТОЯНИЯ ДИАЛОГА (кастомные данные на пользователя) =====
surveys = {}

# Открытые лиды (ждут подтверждения владельца): {lid: {name, about, checkin, contact, last}}
open_leads = {}
lead_counter = 0


def kb(buttons):
    """Клавиатура с кнопками."""
    return ReplyKeyboardMarkup([[KeyboardButton(b) for b in buttons]], resize_keyboard=True)


def done_kb():
    """Инлайн-кнопка для закрытия всех лидов одним нажатием."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Готово - обработал", callback_data="close_leads")]])


def send_lead(context, data):
    """Отправляет лид в группу и владельцу в личку, регистрирует для напоминаний."""
    global lead_counter
    name = data.get("name") or "-"
    about = data.get("about") or "-"
    checkin = data.get("checkin") or "-"
    contact = data.get("contact") or "-"
    text = (
        "НОВЫЙ ЛИД - домик в Баговской\n"
        "--------------------------------\n"
        f"Имя: {name}\n"
        f"О себе: {about}\n"
        f"Желаемая дата просмотра и заселения: {checkin}\n"
        f"Контакт: {contact}\n"
        "--------------------------------\n"
        "Связаться с человеком можно по контакту или в ответ здесь."
    )
    try:
        context.bot.send_message(chat_id=LEAD_CHAT_ID, text=text)
        logger.info("Лид отправлен в группу %s", LEAD_CHAT_ID)
    except Exception as e:
        logger.error("Не удалось отправить лид в группу: %s", e)

    try:
        context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=(
                "НОВЫЙ ЛИД\n"
                f"Имя: {name}\n"
                f"О себе: {about}\n"
                f"Просмотр/заселение: {checkin}\n"
                f"Контакт: {contact}\n\n"
                "Обработайте заявку и нажмите кнопку, чтобы остановить напоминания."
            ),
            reply_markup=done_kb(),
        )
        logger.info("Уведомление о лиде отправлено владельцу %s", OWNER_CHAT_ID)
    except Exception as e:
        logger.error("Не удалось отправить уведомление владельцу: %s", e)

    lead_counter += 1
    lid = f"L{lead_counter}-{int(time.time())}"
    open_leads[lid] = {"name": name, "about": about, "checkin": checkin, "contact": contact, "last": time.time()}
    logger.info("Лид %s открыт для напоминаний", lid)


def reminder_loop():
    """Фоновый поток: каждые 15 минут напоминает владельцу о необработанных лидах."""
    async def check():
        app = Application.builder().token(BOT_TOKEN).build()
        await app.initialize()
        try:
            while True:
                now = time.time()
                for lid, rec in list(open_leads.items()):
                    if now - rec["last"] >= REMINDER_INTERVAL:
                        try:
                            await app.bot.send_message(
                                chat_id=OWNER_CHAT_ID,
                                text=(
                                    f"Напоминание: ещё не обработан лид - {rec['name']}, "
                                    f"просмотр {rec['checkin']}, контакт {rec['contact']}.\n"
                                    "Нажмите кнопку, когда обработаете."
                                ),
                                reply_markup=done_kb(),
                            )
                            open_leads[lid]["last"] = time.time()
                            logger.info("Напоминание по лиду %s", lid)
                        except Exception as e:
                            logger.error("Ошибка напоминания: %s", e)
                await asyncio.sleep(REMINDER_INTERVAL)
        finally:
            await app.shutdown()

    asyncio.run(check())


def start_reminders():
    Thread(target=reminder_loop, daemon=True).start()
    logger.info("Фоновый поток напоминаний запущен (интервал %s сек)", REMINDER_INTERVAL)


# ===== ПОИСК ОТВЕТА ПО БАЗЕ =====
def agrep(text):
    """Возвращает ответ из базы по ключевым словам (ключи = англ., как в BASE)."""
    t = text.lower()
    pairs = {
        "capacity": ["человек", "сколько нас", "вмести", "вмеща", "можем жив", "семь"],
        "price": ["цен", "стоим", "стоит", "сколько", "плат", "аренд", "руб"],
        "deposit": ["залог", "депозит"],
        "term": ["длител", "месяц", "срок", "надолго", "долго"],
        "communal": ["коммунал", "свет", "электрич", "оплат", "счётчик", "мусор", "интернет сколь"],
        "heating": ["отопл", "радиатор", "тепло", "зим", "холодно"],
        "water": ["вода", "душ", "горяч"],
        "wifi": ["wi", "интернет", "вайфай"],
        "toilet": ["туалет", "сорт"],
        "furniture": ["мебел", "что внутри", "кухн", "холодильник", "плита", "телевизор", "диван", "кровать"],
        "bedroom": ["спальн", "кровать", "спать"],
        "style": ["ремонт", "бохо", "штор", "фасад", "арт"],
        "outdoor": ["шезлонг", "подсветк", "вечер", "навес перед"],
        "plot_area": ["площадь участка", "сколько соток", "25 сот", "размер участка"],
        "plot": ["костров", "мангал", "ель", "ёлка", "костр", "шашлык"],
        "fence": ["забор", "огражд"],
        "secure": ["видеонаблюд", "камер", "безопасн", "сигнализа"],
        "grass": ["трава", "косить", "газон"],
        "animals": ["животн", "кот", "собак", "питом", "кони", "бараш"],
        "neighbor_detail": ["сколько соседей", "соседи живут", "соседи рядом", "кто рядом", "суета"],
        "neighbors": ["сосед", "за стеной"],
        "nature": ["лес", "ручей", "пруд", "поле", "природа", "речка"],
        "quiet": ["тихо", "спокойно", "шум"],
        "sights": ["дольмен", "достопримечат", "смотровая", "чёртовы ворот", "чертовы ворот", "экскурс", "куда можно сходить", "что посмотреть", "отдых"],
        "mountains": ["горы", "холм", "гора", "виды", "вид на"],
        "shops": ["магазин", "продукт", "купить", "пвз", "пункт выдач", "вайлдберриз", "озон", "wildberries", "wb", "заказ"],
        "pvz": ["пвз", "пункт выдач"],
        "school": ["школ", "садик", "детский сад", "ребён", "дети"],
        "location": ["где", "район", "местопол", "адрес", "далеко", "город", "море"],
        "status": ["свобод", "заехать", "можно жить", "пуст"],
        "photos": ["фото", "фотограф", "больше", "покажи"],
        "about": ["домик", "дом", "расскаж", "жильё", "квартир", "про дом"],
    }
    # Специфичные вопросы проверяем раньше общего цикла
    if "сколько соседей" in t or "соседи живут" in t or "соседи рядом" in t:
        return BASE["neighbor_detail"]
    if "сколько соток" in t or "размер участка" in t or "площадь участка" in t:
        return BASE["plot_area"]
    if "пвз" in t or "пункт выдач" in t:
        return BASE["pvz"]
    if "достопримечат" in t or "дольмен" in t or "смотровая" in t or "чёртовы" in t or "чертовы" in t or "экскурс" in t or "что посмотреть" in t:
        return BASE["sights"]
    if "горы" in t or "гора " in t or "холм" in t or "виды" in t or "вид на" in t:
        return BASE["mountains"]
    if "светильник" in t or "подсветка" in t or "подсветк" in t or "освещени" in t or "вечером свет" in t:
        return BASE["outdoor"]
    for key, words in pairs.items():
        for w in words:
            if w in t:
                return BASE[key]
    return None


# Реакции на слова клиента в процессе общения (добавляют жизни)
def react(text):
    """Возвращает живую реплику-реакцию на слова клиента, либо None."""
    t = text.lower()
    if "собак" in t or "кот" in t or "питом" in t:
        return "Отлично, что вы с питомцем! 🐾 Собакам и котам у нас рады, рядом поле и лес - есть где погулять."
    if "тишин" in t or "спокойн" in t or "уединен" in t or "тихо" in t:
        return "Тогда вам точно понравится: у нас очень тихая улица, суеты почти нет. С одной стороны дома вообще нет соседей - только поле и прудик, дальше ручей. Идеально для спокойной жизни."
    if "семь" in t or "дет" in t or "ребен" in t or "ребён" in t:
        return "Для семьи это хороший вариант: рядом три продуктовых магазина, в станице есть школа и садик."
    if "природ" in t or "лес" in t or "ручей" in t:
        return "Природа тут просто сказочная: сзади дома лес и ручей, с одной стороны поле и прудик. Вечером под навесом с подсветкой - очень красиво."
    if "работ" in t or "удален" in t or "в интернет" in t:
        return "Для удалённой работы отлично: интернет Wi-Fi 200 мбит/с, стабильный. И тихо - можно спокойно сосредоточиться."
    return None


# ===== ОБРАБОТЧИКИ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text if update.message and update.message.text else ""
    surveys[uid] = {"state": S_ASK_NAME, "name": None, "about": None, "checkin": None, "contact": None}
    if "просмотр" in text.lower() or "подходит" in text.lower():
        await update.message.reply_text(
            "Конечно! 😊 Расскажите, как вас зовут, чтобы я передал хозяину, кто интересуется домиком?"
        )
        return
    await update.message.reply_text(
        "Добрый день! 😊 Спасибо за интерес к нашему домику в станице Баговской.\n\n"
        "Коротко: это уютный домик на 25 сотках у самого леса и ручья, свежий ремонт в бохо-стиле, "
        "тихая спокойная улица. Сдаём на длительный срок, от 11 месяцев.\n\n"
        "Отвечу на все ваши вопросы по домику, участку и окружению, а в конце договоримся о просмотре.\n\n"
        "С чего начнём - как вас зовут?"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    surveys.pop(uid, None)
    await update.message.reply_text("Хорошо, если что - напишите, я всегда на связи. 👋")


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Закрывает все открытые лиды - напоминания прекращаются."""
    if update.effective_user.id != OWNER_CHAT_ID:
        await update.message.reply_text("Эта команда только для владельца.")
        return
    if not open_leads:
        await update.message.reply_text("Необработанных лидов нет. Напоминать нечего. 🎉")
        return
    open_leads.clear()
    await update.message.reply_text("Готово! Все лиды отмечены как обработанные, напоминания прекращены.")
    logger.info("Владелец закрыл все лиды")


async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопки 'Готово - обработал'."""
    query = update.callback_query
    if query.from_user.id != OWNER_CHAT_ID:
        await query.answer("Эта кнопка только для владельца.")
        return
    await query.answer()
    if not open_leads:
        await query.edit_message_text("Необработанных лидов нет. Напоминать нечего. 🎉")
        return
    open_leads.clear()
    await query.edit_message_text("✅ Готово! Все лиды отмечены как обработанные, напоминания прекращены.")
    logger.info("Владелец закрыл все лиды кнопкой")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_CHAT_ID:
        return
    if not open_leads:
        await update.message.reply_text("Необработанных лидов нет.")
    else:
        names = ", ".join(r["name"] for r in open_leads.values())
        await update.message.reply_text(f"Открытых лидов: {len(open_leads)}. Имена: {names}. Когда обработаете - нажмите кнопку или напишите /done.")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = update.effective_user
    text = update.message.text if update.message and update.message.text else ""

    # Игнорируем сообщения из групп
    if update.effective_chat.type != "private":
        return

    st = surveys.get(uid)

    # Нет активного опроса - просто отвечаем на вопросы по базе, и мягко заводим опрос
    if st is None or st["state"] == S_DONE:
        answer = agrep(text)
        if answer:
            await update.message.reply_text(answer)
            if st is None or st["state"] == S_DONE:
                surveys[uid] = {"state": S_ASK_NAME, "name": None, "about": None, "checkin": None, "contact": None}
                await update.message.reply_text(
                    "Если домик подходит - расскажите, как вас зовут, и обсудим просмотр. 😊"
                )
            return
        # Не распознали - предлагаем начать
        surveys[uid] = {"state": S_ASK_NAME, "name": None, "about": None, "checkin": None, "contact": None}
        await update.message.reply_text(
            "Здравствуйте! 😊 Посмотрим домик в Баговской? Это уютный домик на природе, "
            "у леса и ручья, тихая улица. Отвечу на вопросы по домику, участку, соседям, "
            "магазинам - спрашивайте что угодно. Как вас зовут?"
        )
        return

    state = st["state"]

    # Если во время опроса человек задаёт вопрос про домик - отвечаем и возвращаемся к опросу
    if state in (S_ASK_ABOUT, S_ASK_CHECKIN, S_ASK_CONTACT):
        answer = agrep(text)
        if answer and len(text.split()) < 7:
            # Вопрос про дом (короткий вопрос), отвечаем и предлагаем продолжить опрос
            await update.message.reply_text(answer)
            if state == S_ASK_ABOUT:
                await update.message.reply_text("Расскажите немного о себе и планах, чтобы я всё передал хозяину. 😊")
            elif state == S_ASK_CHECKIN:
                await update.message.reply_text("Так когда вам было бы удобно приехать на просмотр?")
            else:
                await update.message.reply_text("Как с вами удобно связаться хозяину?")
            return

    # State machine для сбора лида (живой, расспрашивающий)
    if state == S_ASK_NAME:
        st["name"] = text.strip()
        st["state"] = S_ASK_QUEST
        await update.message.reply_text(
            f"Очень приятно, {st['name']}! 😊\n\n"
            f"Расскажу немного о нашем домике: это уютный домик на 25 сотках у самого леса и ручья, "
            f"свежий ремонт в бохо-стиле, тихая спокойная улица. На участке костровая и мангальная зона "
            f"у пушистой ели, есть видеонаблюдение. Рядом три продуктовых магазина, пункты выдачи "
            f"Wildberries и Ozon, а в станице - школа и садик. Вокруг горы и холмы."
        )
        await update.message.reply_text(
            "Какие у вас ещё остались вопросы? Можете задать их сейчас, я с радостью отвечу: "
            "про домик, участок, соседей, магазины или достопримечательности. 😊"
        )
    elif state == S_ASK_QUEST:
        # Пользователь может задать вопрос про домик - отвечаем
        answer = agrep(text)
        if answer and len(text.split()) < 9:
            # Это похоже на вопрос про дом - отвечаем и снова спрашиваем
            await update.message.reply_text(answer)
            await update.message.reply_text(
                "Ещё какие-нибудь вопросы есть? Или можем уже продолжить - расскажите немного о себе: "
                "кто будет жить, чем занимаетесь, что вас привело к нам? 😊"
            )
            return
        # Человек не задал вопрос (вопросов нет / всё ясно / просто ответил) - идём дальше
        st["state"] = S_ASK_ABOUT
        st["about"] = None  # очистим, т.к. это не ответ о себе, а реплика
        await update.message.reply_text(
            "Отлично! Чтобы я передал хозяину всё верно, расскажите немного о себе:\n"
            "- кто будет жить (один, вдвоём, с детьми или питомцами)?\n"
            "- чем занимаетесь, есть ли удалённая работа?\n"
            "- что вас привело к нам - ищете тишину, природу или работу на удалёнке?"
        )
    elif state == S_ASK_ABOUT:
        react_msg = react(text)
        if react_msg:
            await update.message.reply_text(react_msg)
        st["about"] = text.strip()
        st["state"] = S_ASK_CHECKIN
        # Живо продолжаем - реагируем на ответ и ведём дальше
        if react_msg:
            await update.message.reply_text(
                "Круто, что мы нашли общий язык! 😊 Когда вам было бы удобно приехать на просмотр? "
                "И ориентировочно когда планируете заселиться?"
            )
        else:
            await update.message.reply_text(
                "Спасибо, это очень помогает! 😊\n\n"
                "Кстати, если есть вопросы по домику, участку или окружению (соседи, магазины, ПВЗ) - "
                "смело спрашивайте, я всё расскажу.\n\n"
                "А пока: когда вам было бы удобно приехать на просмотр и ориентировочно когда планируете заселиться?"
            )
    elif state == S_ASK_CHECKIN:
        st["checkin"] = text.strip()
        st["state"] = S_ASK_CONTACT
        await update.message.reply_text(
            "Отлично, записал! 😊 И последний шаг: как с вами удобно связаться хозяину? "
            "Оставьте номер телефона или @username в Telegram.",
            reply_markup=kb([f"Мой номер: {user.phone}" if getattr(user, 'phone', None) else "Оставить контакт вручную"]),
        )
    elif state == S_ASK_CONTACT:
        st["contact"] = text.strip()
        st["state"] = S_DONE
        await update.message.reply_text(
            "Спасибо большое! 😊 Я передал вашу заявку хозяину, он свяжется с вами в ближайшее время, "
            "чтобы договориться о просмотре.\n\n"
            "Если есть вопросы по домику или участку - пишите, всегда рады помочь! 🏡\n\n"
            "Кстати, вдруг ещё не спрашивали: рядом три продуктовых магазина (работают до 22:00), "
            "есть пункты выдачи Wildberries и Ozon, в станице школа и садик. Спрашивайте что угодно!"
        )
        send_lead(context, st)
        surveys[uid]["state"] = S_DONE


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(close_callback, pattern="close_leads"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    logger.info("Бот запущен. Токен OK. Группа лидов: %s, владелец: %s", LEAD_CHAT_ID, OWNER_CHAT_ID)
    start_reminders()
    app.run_polling()


if __name__ == "__main__":
    main()
